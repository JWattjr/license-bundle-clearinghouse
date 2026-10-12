import json
import hashlib
import re
from pathlib import Path

import pytest


SDK = "v0.6.0-rc5"
NOW = "2030-01-01T12:00:00Z"
CONSENT_DEADLINE = "2030-01-05T00:00:00Z"
PERMISSION_EXPIRY = "2030-01-30T00:00:00Z"
WORK_IDS = ["artwork", "dataset"]
BY_URL = "https://raw.githubusercontent.com/spdx/license-list-data/v3.25.0/text/CC-BY-4.0.txt"
NC_URL = "https://raw.githubusercontent.com/spdx/license-list-data/v3.25.0/text/CC-BY-NC-4.0.txt"
BY_BODY = (Path(__file__).parent / "fixtures/CC-BY-4.0.txt").read_bytes()
NC_BODY = (Path(__file__).parent / "fixtures/CC-BY-NC-4.0.txt").read_bytes()


def mock_sources(direct_vm, body=BY_BODY, status=200):
    direct_vm.mock_web(re.escape(BY_URL), {"response": {"status": status, "headers": {}, "body": body}})
    direct_vm.mock_web(re.escape(NC_URL), {"response": {"status": 200, "headers": {}, "body": NC_BODY}})


def llm(value) -> str:
    """The direct mock decodes once; the v0.6 SDK then parses JSON text."""
    return json.dumps(json.dumps(value))


def deploy(direct_vm, direct_deploy, direct_owner):
    direct_vm.sender = direct_owner
    direct_vm.warp(NOW)
    return direct_deploy("contracts/license_bundle_clearinghouse.py", sdk_version=SDK)


def register_two(contract, direct_vm, direct_alice, direct_bob):
    with direct_vm.prank(direct_alice):
        contract.register_license(
            "artwork", "Water station design", BY_URL, 30,
        )
    with direct_vm.prank(direct_bob):
        contract.register_license(
            "dataset", "Regional conductivity dataset", BY_URL, 20,
        )


def compatible_result(findings=None, conflict_pairs=None):
    if findings is None:
        findings = ["PERMITTED", "PERMITTED"]
    if conflict_pairs is None:
        conflict_pairs = []
    return {
        "license_decisions": [
            {"work_id": "artwork", "version": 1, "finding": findings[0]},
            {"work_id": "dataset", "version": 1, "finding": findings[1]},
        ],
        "conflict_pairs": conflict_pairs,
    }


def request_bundle(contract, direct_vm, requester, request_id="clinic-report", result=None):
    if result is None:
        result = compatible_result()
    mock_sources(direct_vm)
    direct_vm.mock_llm(r"LICENSE BUNDLE COMPATIBILITY", llm(result))
    with direct_vm.prank(requester):
        return contract.request_bundle(
            request_id,
            json.dumps(WORK_IDS),
            "Create and distribute a paid advertising campaign using both works with attribution, licence links, modification notices and no additional restrictions.",
            CONSENT_DEADLINE,
            PERMISSION_EXPIRY,
        )


def fund_requester(contract, direct_vm, requester, amount=100):
    with direct_vm.prank(requester):
        contract.deposit_demo_units(amount)


def test_compatible_bundle_requires_every_licensor_and_distributes_fixed_fees(
    direct_vm, direct_deploy, direct_owner, direct_alice, direct_bob
):
    contract = deploy(direct_vm, direct_deploy, direct_owner)
    register_two(contract, direct_vm, direct_alice, direct_bob)
    fund_requester(contract, direct_vm, direct_owner)
    request = request_bundle(contract, direct_vm, direct_owner)
    assert request["status"] == "AWAITING_CONSENT"
    assert request["fee_units"] == 50
    assert contract.get_balance(direct_owner) == 50
    assert contract.get_accounting() == {
        "minted_units": 100, "available_units": 50, "reserved_units": 50,
        "fees_paid_units": 0, "conserved": True,
    }
    assert direct_vm.run_validator()

    direct_vm.clear_mocks()
    with direct_vm.prank(direct_alice):
        first = contract.approve_bundle_request("clinic-report", request["request_digest"])
    assert first["status"] == "AWAITING_CONSENT"
    assert contract.get_request("clinic-report")["approvals"] == ["0x" + direct_alice.hex()]

    with direct_vm.prank(direct_bob):
        issued = contract.approve_bundle_request("clinic-report", request["request_digest"])
    assert issued["status"] == "ISSUED"
    assert issued["paid_units"] == 50
    permission = contract.get_permission("clinic-report")
    assert permission["permission_status"] == "ACTIVE"
    assert permission["requested_use"].startswith("Create and distribute")
    assert [row["work_id"] for row in permission["licenses"]] == WORK_IDS
    assert [row["version"] for row in permission["licenses"]] == [1, 1]
    assert contract.get_balance(direct_alice) == 30
    assert contract.get_balance(direct_bob) == 20
    assert contract.get_accounting() == {
        "minted_units": 100, "available_units": 100, "reserved_units": 0,
        "fees_paid_units": 50, "conserved": True,
    }

    with direct_vm.prank(direct_alice):
        updated = contract.update_license_terms(
            "artwork", 1,
            NC_URL, 35,
        )
    assert updated["version"] == 2
    permission_after_update = contract.get_permission("clinic-report")
    assert permission_after_update["licenses"][0]["version"] == 1
    assert permission_after_update["licenses"][0]["terms_url"] == BY_URL
    assert contract.get_license("artwork")["version"] == 2
    assert contract.get_license_version("artwork", 1)["fee_units"] == 30


def test_conflicting_terms_block_issuance_before_reserving_user_funds(
    direct_vm, direct_deploy, direct_owner, direct_alice, direct_bob
):
    contract = deploy(direct_vm, direct_deploy, direct_owner)
    register_two(contract, direct_vm, direct_alice, direct_bob)
    fund_requester(contract, direct_vm, direct_owner)
    result = compatible_result(conflict_pairs=[["artwork", "dataset"]])
    request = request_bundle(contract, direct_vm, direct_owner, result=result)
    assert request["status"] == "DENIED_INCOMPATIBLE"
    assert request["compatibility_status"] == "INCOMPATIBLE"
    assert request["compatibility"]["conflict_pairs"] == [["artwork", "dataset"]]
    assert contract.get_balance(direct_owner) == 100
    assert contract.get_accounting()["reserved_units"] == 0
    with direct_vm.expect_revert("permission has not been issued"):
        contract.get_permission("clinic-report")


@pytest.mark.parametrize(
    "findings, expected_status",
    [
        (["NOT_PERMITTED", "PERMITTED"], "DENIED_INCOMPATIBLE"),
        (["PERMITTED", "UNCERTAIN"], "DENIED_UNCERTAIN"),
    ],
)
def test_restricted_or_uncertain_license_never_enters_consent_or_payment(
    direct_vm, direct_deploy, direct_owner, direct_alice, direct_bob, findings, expected_status
):
    contract = deploy(direct_vm, direct_deploy, direct_owner)
    register_two(contract, direct_vm, direct_alice, direct_bob)
    fund_requester(contract, direct_vm, direct_owner)
    request = request_bundle(
        contract, direct_vm, direct_owner, result=compatible_result(findings=findings)
    )
    assert request["status"] == expected_status
    assert contract.get_balance(direct_owner) == 100
    assert contract.get_accounting()["reserved_units"] == 0


def test_each_consent_binds_to_the_exact_request_and_only_named_licensors_may_approve(
    direct_vm, direct_deploy, direct_owner, direct_alice, direct_bob, direct_charlie
):
    contract = deploy(direct_vm, direct_deploy, direct_owner)
    register_two(contract, direct_vm, direct_alice, direct_bob)
    fund_requester(contract, direct_vm, direct_owner)
    request = request_bundle(contract, direct_vm, direct_owner)
    with direct_vm.prank(direct_charlie):
        with direct_vm.expect_revert("only a licensor in this bundle"):
            contract.approve_bundle_request("clinic-report", request["request_digest"])
    with direct_vm.prank(direct_alice):
        with direct_vm.expect_revert("consent digest does not match"):
            contract.approve_bundle_request("clinic-report", "sha256:" + "0" * 64)
        contract.approve_bundle_request("clinic-report", request["request_digest"])
        with direct_vm.expect_revert("already consented"):
            contract.approve_bundle_request("clinic-report", request["request_digest"])
    assert contract.get_accounting()["reserved_units"] == 50


def test_rejection_cancellation_and_expiry_return_the_reserved_budget(
    direct_vm, direct_deploy, direct_owner, direct_alice, direct_bob
):
    contract = deploy(direct_vm, direct_deploy, direct_owner)
    register_two(contract, direct_vm, direct_alice, direct_bob)
    fund_requester(contract, direct_vm, direct_owner)
    first = request_bundle(contract, direct_vm, direct_owner, "rejected")
    with direct_vm.prank(direct_bob):
        rejected = contract.reject_bundle_request("rejected")
    assert rejected["status"] == "REJECTED_REFUNDED"
    assert contract.get_balance(direct_owner) == 100

    direct_vm.clear_mocks()
    second = request_bundle(contract, direct_vm, direct_owner, "cancelled")
    with direct_vm.prank(direct_owner):
        cancelled = contract.cancel_bundle_request("cancelled")
    assert cancelled["refunded_units"] == 50
    assert contract.get_balance(direct_owner) == 100

    direct_vm.clear_mocks()
    request_bundle(contract, direct_vm, direct_owner, "expired")
    direct_vm.warp(CONSENT_DEADLINE)
    with direct_vm.expect_revert("consent deadline has not passed"):
        contract.expire_bundle_request("expired")
    direct_vm.warp("2030-01-05T00:00:01Z")
    expired = contract.expire_bundle_request("expired")
    assert expired["status"] == "EXPIRED_REFUNDED"
    assert contract.get_balance(direct_owner) == 100
    assert contract.get_accounting()["conserved"] is True


def test_version_change_stales_pending_request_and_refunds_once_without_changing_old_permission(
    direct_vm, direct_deploy, direct_owner, direct_alice, direct_bob
):
    contract = deploy(direct_vm, direct_deploy, direct_owner)
    register_two(contract, direct_vm, direct_alice, direct_bob)
    fund_requester(contract, direct_vm, direct_owner)
    request = request_bundle(contract, direct_vm, direct_owner, "pending-stale")
    with direct_vm.prank(direct_alice):
        contract.update_license_terms(
            "artwork", 1,
            NC_URL, 35,
        )
    with direct_vm.prank(direct_bob):
        with direct_vm.expect_revert("terms changed"):
            contract.approve_bundle_request("pending-stale", request["request_digest"])
    stale = contract.invalidate_stale_request("pending-stale")
    assert stale["status"] == "STALE_REFUNDED"
    assert contract.get_balance(direct_owner) == 100
    assert contract.get_accounting()["reserved_units"] == 0
    assert contract.get_accounting()["conserved"] is True


def test_malformed_model_output_reverts_then_validator_rejects_disagreement(
    direct_vm, direct_deploy, direct_owner, direct_alice, direct_bob
):
    contract = deploy(direct_vm, direct_deploy, direct_owner)
    register_two(contract, direct_vm, direct_alice, direct_bob)
    fund_requester(contract, direct_vm, direct_owner)
    malformed = compatible_result()
    malformed["leader_comment"] = "untrusted extra field"
    mock_sources(direct_vm)
    direct_vm.mock_llm(r"LICENSE BUNDLE COMPATIBILITY", llm(malformed))
    with direct_vm.prank(direct_owner):
        with direct_vm.expect_revert("unknown or missing fields"):
            contract.request_bundle("malformed", json.dumps(WORK_IDS),
                                    "Create an attributed clinic report from both works for public health use.",
                                    CONSENT_DEADLINE, PERMISSION_EXPIRY)
    assert contract.get_accounting()["reserved_units"] == 0
    assert contract.get_balance(direct_owner) == 100

    direct_vm.clear_mocks()
    request = request_bundle(contract, direct_vm, direct_owner, "valid-after-malformed")
    assert direct_vm.run_validator()
    forged = json.loads(json.dumps(request["compatibility"]))
    forged["license_decisions"][0]["finding"] = "NOT_PERMITTED"
    assert direct_vm.run_validator(leader_result=forged) is False
    assert contract.get_balance(direct_owner) == 50
    assert contract.get_accounting()["conserved"] is True


def test_insufficient_balance_fails_before_compatibility_judgment(
    direct_vm, direct_deploy, direct_owner, direct_alice, direct_bob
):
    contract = deploy(direct_vm, direct_deploy, direct_owner)
    register_two(contract, direct_vm, direct_alice, direct_bob)
    with direct_vm.expect_revert("insufficient available demo units"):
        contract.request_bundle("unfunded", json.dumps(WORK_IDS),
                                "Create an attributed clinic report from both works for public health use.",
                                CONSENT_DEADLINE, PERMISSION_EXPIRY)
    assert contract.get_accounting() == {
        "minted_units": 0, "available_units": 0, "reserved_units": 0,
        "fees_paid_units": 0, "conserved": True,
    }


def test_license_version_history_has_a_fixed_cap(
    direct_vm, direct_deploy, direct_owner, direct_alice, direct_bob
):
    contract = deploy(direct_vm, direct_deploy, direct_owner)
    register_two(contract, direct_vm, direct_alice, direct_bob)
    with direct_vm.prank(direct_alice):
        for version in range(1, 8):
            updated = contract.update_license_terms(
                "artwork", version,
                NC_URL if version % 2 else BY_URL,
                30 + version,
            )
        assert updated["version"] == 8
        with direct_vm.expect_revert("version history is full"):
            contract.update_license_terms(
                "artwork", 8,
                BY_URL, 40,
            )
    assert contract.get_license_version("artwork", 1)["version"] == 1
    assert contract.get_license("artwork")["version"] == 8
