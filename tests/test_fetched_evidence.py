"""Fetched licence bytes, fail-closed evidence and independent validator checks."""
import copy
import hashlib
import json

import pytest

from test_bundle import (
    BY_BODY, BY_URL, NC_URL, CONSENT_DEADLINE, PERMISSION_EXPIRY, WORK_IDS,
    compatible_result, deploy, fund_requester, llm, mock_sources,
    register_two, request_bundle,
)


def test_judgment_receives_complete_real_text_and_consent_binds_raw_digest(
    direct_vm, direct_deploy, direct_owner, direct_alice, direct_bob, monkeypatch
):
    contract = deploy(direct_vm, direct_deploy, direct_owner)
    register_two(contract, direct_vm, direct_alice, direct_bob)
    fund_requester(contract, direct_vm, direct_owner)
    gl = contract._instance._assess_compatibility.__func__.__globals__["gl"]
    original = gl.nondet.exec_prompt
    prompts = []

    def inspect_prompt(prompt, **kwargs):
        data = json.loads(prompt.split("INPUT_JSON: ", 1)[1])
        assert [row["text"] for row in data["fetched_licenses"]] == [BY_BODY.decode("utf-8")] * 2
        assert all("terms_text" not in row for row in data["licenses"])
        assert "UNTRUSTED DATA" in prompt
        prompts.append(data)
        return original(prompt, **kwargs)

    monkeypatch.setattr(gl.nondet, "exec_prompt", inspect_prompt)
    request = request_bundle(contract, direct_vm, direct_owner)
    assert direct_vm.run_validator()
    assert len(prompts) == 2  # Leader and validator independently fetch and judge.
    evidence = request["compatibility"]["evidence"]
    expected = "sha256:" + hashlib.sha256(BY_BODY).hexdigest()
    assert [(row["availability"], row["body_digest"], row["body_bytes"]) for row in evidence] == [
        ("AVAILABLE", expected, len(BY_BODY))] * 2
    core_keys = ("request_id", "requester", "requested_use", "consent_deadline", "permission_expiry",
                 "fee_units", "licenses", "required_licensors", "compatibility")
    approved = {key: request[key] for key in core_keys}
    canonical = json.dumps(approved, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    assert request["request_digest"] == "sha256:" + hashlib.sha256(canonical.encode()).hexdigest()
    changed = copy.deepcopy(approved)
    changed["compatibility"]["evidence"][0]["body_digest"] = "sha256:" + "0" * 64
    canonical = json.dumps(changed, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    altered_digest = "sha256:" + hashlib.sha256(canonical.encode()).hexdigest()
    assert altered_digest != request["request_digest"]
    with direct_vm.prank(direct_alice), direct_vm.expect_revert("consent digest does not match"):
        contract.approve_bundle_request("clinic-report", altered_digest)


@pytest.mark.parametrize("body,status", [
    (BY_BODY, 404), (b"x" * 20_001, 200), ("é" * 10_001, 200),
    (b"\xff", 200), (b"", 200),
], ids=["http404", "over-raw-limit", "utf8-over-raw-limit", "invalid-utf8", "empty"])
def test_unavailable_oversized_or_invalid_utf8_fails_closed_without_model(
    direct_vm, direct_deploy, direct_owner, direct_alice, direct_bob, body, status
):
    contract = deploy(direct_vm, direct_deploy, direct_owner)
    register_two(contract, direct_vm, direct_alice, direct_bob)
    with direct_vm.prank(direct_bob):
        contract.update_license_terms("dataset", 1, NC_URL, 20)
    fund_requester(contract, direct_vm, direct_owner)
    mock_sources(direct_vm, body=body, status=status)
    # No LLM mock: missing/invalid evidence must short circuit judgment.
    with direct_vm.prank(direct_owner):
        request = contract.request_bundle("unverifiable", json.dumps(WORK_IDS),
            "Use both photographs in a paid advertising campaign with attribution.",
            CONSENT_DEADLINE, PERMISSION_EXPIRY)
    assert request["status"] == "DENIED_UNVERIFIABLE"
    assert request["compatibility_status"] == "UNVERIFIABLE"
    assert request["compatibility"]["evidence"][0]["availability"] == "UNAVAILABLE"
    assert request["compatibility"]["evidence"][1]["availability"] == "AVAILABLE"
    assert request["compatibility"]["license_decisions"][0]["finding"] == "NOT_PERMITTED"
    assert direct_vm.run_validator()
    assert contract.get_balance(direct_owner) == 100
    assert contract.get_accounting()["reserved_units"] == 0
    with direct_vm.expect_revert("permission has not been issued"):
        contract.get_permission("unverifiable")
    with direct_vm.prank(direct_alice), direct_vm.expect_revert("not awaiting"):
        contract.approve_bundle_request("unverifiable", request["request_digest"])


def test_exact_byte_limit_is_allowed_and_digest_forgery_or_changed_fetch_is_rejected(
    direct_vm, direct_deploy, direct_owner, direct_alice, direct_bob
):
    contract = deploy(direct_vm, direct_deploy, direct_owner)
    register_two(contract, direct_vm, direct_alice, direct_bob)
    fund_requester(contract, direct_vm, direct_owner)
    body = BY_BODY + b" " * (20_000 - len(BY_BODY))
    mock_sources(direct_vm, body=body)
    direct_vm.mock_llm(r"LICENSE BUNDLE COMPATIBILITY", llm(compatible_result()))
    with direct_vm.prank(direct_owner):
        request = contract.request_bundle("boundary", json.dumps(WORK_IDS),
            "Use both photographs in a paid advertising campaign with attribution.",
            CONSENT_DEADLINE, PERMISSION_EXPIRY)
    assert request["status"] == "AWAITING_CONSENT"
    assert request["compatibility"]["evidence"][0]["body_bytes"] == 20_000
    assert direct_vm.run_validator()
    forged = copy.deepcopy(request["compatibility"])
    forged["evidence"][0]["body_digest"] = "sha256:" + "0" * 64
    assert direct_vm.run_validator(leader_result=forged) is False
    direct_vm.clear_mocks()
    mock_sources(direct_vm, body=body[:-1] + b"\n")
    direct_vm.mock_llm(r"LICENSE BUNDLE COMPATIBILITY", llm(compatible_result()))
    assert direct_vm.run_validator(leader_result=request["compatibility"]) is False


@pytest.mark.parametrize("url", [
    "http://raw.githubusercontent.com/text", "https://localhost/text", "https://127.0.0.1/text",
    "https://192.168.1.1/text", "https://[::1]/text", "https://user@github.com/text",
    "https://github.com:8080/text", "https://a.local/text", "https://github.com/a#fragment",
    "https://github.com\\@localhost/text", "https://github.com/space here", "https://%31%32%37.0.0.1/text",
])
def test_registration_rejects_nonpublic_or_ambiguous_urls(direct_vm, direct_deploy, direct_owner, url):
    contract = deploy(direct_vm, direct_deploy, direct_owner)
    with direct_vm.expect_revert("[EXPECTED]"):
        contract.register_license("bad-url", "Photograph", url, 30)


def test_bundle_cap_is_three(direct_vm, direct_deploy, direct_owner):
    contract = deploy(direct_vm, direct_deploy, direct_owner)
    with direct_vm.expect_revert("two to three"):
        contract.request_bundle("too-large", json.dumps(["one", "two", "three", "four"]),
            "Use all photographs in a paid advertising campaign with attribution.",
            CONSENT_DEADLINE, PERMISSION_EXPIRY)
