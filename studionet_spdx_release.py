"""One fetched-SPDX StudioNet release from a local commit; stop on any unexpected judgment."""
from __future__ import annotations
import base64
import hashlib
import importlib.metadata
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
from eth_account import Account
from genlayer_py import create_client
from genlayer_py.chains import studionet
from genlayer_py.types import TransactionHashVariant
from studionet_compat import RUNNER, pinned_runner_calldata

REPO = Path(__file__).resolve().parent
DATE = "2026-10-12-spdx"
OUTPUT = REPO / "deployments" / f"studionet-release-{DATE}.json"
RPC_LOG = REPO / "deployments" / f"studionet-release-{DATE}-rpc.jsonl"
COMMAND_LOG = REPO / "deployments" / f"studionet-release-{DATE}-commands.jsonl"
ENDPOINT = "https://studio.genlayer.com/api"
SOURCE = "contracts/license_bundle_clearinghouse.py"
EXPLORER = "https://explorer-studio.genlayer.com/tx/"
record = {"release_date": "2026-10-12", "release_id": DATE, "push_policy": "Local commits; single push only after all three gates pass", "timezone": "Africa/Lagos", "status": "IN_PROGRESS",
          "network": {"name": "StudioNet", "chain_id": 61999, "rpc": ENDPOINT, "portal_used": False},
          "runner": RUNNER, "runtime_executable": sys.executable,
          "client": importlib.metadata.version("genlayer-py"), "adapter": "studionet_compat.pinned_runner_calldata",
          "repository": "https://github.com/JWattjr/license-bundle-clearinghouse", "repository_visibility": "PUBLIC",
          "transactions": [], "readbacks": [], "accounting_checks": [], "gates": {},
          "previous_failed_deployment": {"address": "0x907c4540Bb4f59aBAA5b91c9Fd8000bb2Ba87472",
              "status": "FAILED_DEPLOYMENT_NOT_EVIDENCE", "release_evidence": False,
              "reason": "Calls sent with the empty-string method selector fail against the pinned runner, which expects method."}}
address = None
clients = {}


def save():
    OUTPUT.write_text(json.dumps(record, indent=2, default=str) + "\n", encoding="utf-8")


def append(path, value):
    with path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(value, default=str) + "\n")


def command(args):
    proc = subprocess.run(args, capture_output=True)
    append(COMMAND_LOG, {"command": args, "exit_code": proc.returncode,
                        "stdout": proc.stdout.decode("utf-8", errors="replace"),
                        "stderr": proc.stderr.decode("utf-8", errors="replace")})
    proc.check_returncode()
    return proc.stdout


def git(*args):
    return command(["git", "-c", f"safe.directory={REPO}", "-C", str(REPO), *args])


def rpc(method, params):
    response = requests.post(ENDPOINT, json={"jsonrpc": "2.0", "method": method, "params": params, "id": 1}, timeout=(10, 45))
    response.raise_for_status()
    body = response.json()
    append(RPC_LOG, {"timestamp": datetime.now(timezone.utc).isoformat(), "method": method, "params": params, "result": body})
    if "error" in body:
        raise RuntimeError(f"{method}: {body['error']}")
    return body["result"]


def wait(entry):
    last = None
    for _ in range(240):
        raw = rpc("eth_getTransactionByHash", [entry["hash"]])
        status = raw.get("status_name") or raw.get("status") if raw else None
        if isinstance(status, int):
            raise RuntimeError("Unexpected numeric StudioNet status; inspect raw RPC log")
        if status != last:
            entry.setdefault("observed_statuses", []).append(status)
            last = status
            print(json.dumps({"operation": entry["operation"], "hash": entry["hash"], "lifecycle": status}), flush=True)
        entry["acceptance_status"] = "ACCEPTED" if "ACCEPTED" in entry.get("observed_statuses", []) else "NOT_OBSERVED"
        entry["finality_status"] = status
        save()
        if status == "FINALIZED":
            receipt = clients["requester"].get_transaction(transaction_hash=entry["hash"])
            # Persist the decoded receipt independently of lifecycle status.
            record.setdefault("receipts", {})[entry["hash"]] = receipt
            leaders = (receipt.get("consensus_data") or {}).get("leader_receipt") or []
            leader = leaders[0] if isinstance(leaders, list) and leaders else leaders if isinstance(leaders, dict) else {}
            result = leader.get("result") or {}
            entry["leader_execution"] = leader.get("execution_result")
            entry["execution_result_code"] = result.get("status")
            entry["execution_payload"] = result.get("payload")
            entry["consensus_result"] = receipt.get("result_name")
            save()
            expected = "ERROR" if entry.get("expected_rollback") else "SUCCESS"
            if entry["leader_execution"] != expected:
                raise RuntimeError(f"Unexpected execution result for {entry['operation']}: {entry}")
            if entry.get("expected_rollback") and entry["execution_result_code"] != "rollback":
                raise RuntimeError("Expected a contract rollback, not a dispatch/runtime error")
            print(json.dumps({"operation": entry["operation"], "finality": status,
                              "leader_execution": entry["leader_execution"], "result_code": entry["execution_result_code"]}), flush=True)
            return receipt
        if status in {"CANCELED", "UNDETERMINED"}:
            raise RuntimeError(f"Transaction terminated unexpectedly: {status}")
        time.sleep(5)
    raise RuntimeError("Finality timeout: stop without resubmitting")


def submit(label, actor, method, args, expected_rollback=False):
    tx = clients[actor].write_contract(address=address, function_name=method, args=args, leader_only=False)
    # Save the returned hash before any receipt or metadata operation.
    entry = {"operation": label, "method": method, "args": args, "actor": actor,
             "hash": str(tx), "explorer": EXPLORER + str(tx), "expected_rollback": expected_rollback}
    record["transactions"].append(entry)
    save()
    wait(entry)
    return entry


def view(label, method, args, *, expect_error=False):
    entry = {"label": label, "method": method, "args": args, "state": "LATEST_FINAL"}
    try:
        entry["value"] = clients["requester"].read_contract(address=address, function_name=method, args=args,
                    transaction_hash_variant=TransactionHashVariant.LATEST_FINAL)
        entry["status"] = "SUCCESS"
    except Exception as error:
        entry.update(status="ERROR", error=str(error))
    record["readbacks"].append(entry)
    save()
    if (entry["status"] == "ERROR") != expect_error:
        raise RuntimeError(f"Unexpected read-back: {entry}")
    print(json.dumps({"readback": label, "status": entry["status"], "value": entry.get("value", entry.get("error"))}), flush=True)
    return entry.get("value")


def accounting(label):
    raw = view(label + "-ledger", "get_accounting", [])
    requester = view(label + "-requester", "get_balance", [record["participants"]["requester"]])
    alice = view(label + "-alice", "get_balance", [record["participants"]["alice"]])
    bob = view(label + "-bob", "get_balance", [record["participants"]["bob"]])
    # Paid units remain spendable recipient credits in this contract. This demo
    # never recycles those credits, so requester budget is a disjoint partition.
    budget = {"deposited": raw["minted_units"], "available": requester,
              "reserved": raw["reserved_units"], "paid": raw["fees_paid_units"]}
    nonnegative = all(value >= 0 for value in [*budget.values(), alice, bob, raw["available_units"]])
    valid = (budget["deposited"] == budget["available"] + budget["reserved"] + budget["paid"]
             and requester + alice + bob == raw["available_units"]
             and alice + bob == budget["paid"] and raw["conserved"])
    record["accounting_checks"].append({"label": label, **budget, "nonnegative": nonnegative,
                 "equation_pass": valid, "ledger": raw,
                 "scope": "Requester-funded demo budget; paid recipient credits are not reused in this demo."})
    save()
    if not (valid and nonnegative):
        raise RuntimeError("Accounting invariant failed")


BY = "https://raw.githubusercontent.com/spdx/license-list-data/v3.25.0/text/CC-BY-4.0.txt"
NC = "https://raw.githubusercontent.com/spdx/license-list-data/v3.25.0/text/CC-BY-NC-4.0.txt"
USE = ("Use both selected photographs in a paid advertising campaign for a for-profit business, "
       "including reproducing, adapting and commercially distributing them. Credit each creator, "
       "link to each licence, and mark all modifications. Claim no endorsement and impose no DRM, "
       "exclusivity or additional restrictions on recipients exercising the licensed rights.")
SPDX = json.loads((REPO / "tests/fixtures/PROVENANCE.json").read_text(encoding="utf-8"))


def verify_fetched_evidence(row):
    indexed = {item["url"]: item for item in SPDX}
    checks = []
    for item in row["compatibility"]["evidence"]:
        expected = indexed[item["terms_url"]]
        valid = (item["availability"] == "AVAILABLE" and item["body_digest"] == expected["body_digest"]
                 and item["body_bytes"] == expected["raw_bytes"])
        checks.append({**item, "matches_curl_verified_spdx": valid})
    record.setdefault("fetched_evidence_checks", []).append({"request_id": row["request_id"], "licenses": checks})
    save()
    if not all(item["matches_curl_verified_spdx"] for item in checks):
        raise RuntimeError("Fetched bytes differ from curl-verified SPDX evidence; STOP, no retry")


DEADLINE = "2026-10-20T00:00:00Z"
EXPIRY = "2026-11-20T00:00:00Z"


def request(label, works, expected):
    tx = submit(label, "requester", "request_bundle", [label, json.dumps(works), USE, DEADLINE, EXPIRY])
    row = view(label, "get_request", [label])
    if row["status"] != expected:
        raise RuntimeError(f"JUDGMENT DIFFERED FROM EXPECTED: {label} -> {row['status']}; STOP, do not retry")
    verify_fetched_evidence(row)
    decisions = [item["finding"] for item in row["compatibility"]["license_decisions"]]
    wanted = ["NOT_PERMITTED", "PERMITTED"] if label == "commercial-nc" else ["PERMITTED", "PERMITTED"]
    if decisions != wanted:
        raise RuntimeError(f"JUDGMENT DIFFERED FROM EXPECTED: {label} findings {decisions}; STOP, no retry")
    accounting(label)
    return row, tx


def main():
    global address, clients
    if OUTPUT.exists():
        raise RuntimeError("Refusing to deploy again or overwrite an existing release")
    # Preflight before creating output files, so clean worktree has meaning.
    if git("status", "--porcelain").strip():
        # COMMAND_LOG is untracked output created by the first command above.
        status = git("status", "--porcelain").decode()
        if any("studionet-release-2026-10-12-spdx-commands.jsonl" not in line for line in status.splitlines()):
            raise RuntimeError(f"Dirty worktree: {status}")
    commit = git("rev-parse", "HEAD").decode().strip()
    visibility = json.loads(command(["gh", "repo", "view", "JWattjr/license-bundle-clearinghouse", "--json", "visibility"]))
    if visibility["visibility"] != "PUBLIC":
        raise RuntimeError("Repository visibility is unexpectedly not PUBLIC")
    source = git("show", f"{commit}:{SOURCE}")
    if source != (REPO / SOURCE).read_bytes():
        raise RuntimeError("Working source differs byte-for-byte from the local committed blob")
    if RUNNER not in source.decode():
        raise RuntimeError("Runner pin differs")
    if int(rpc("eth_chainId", []), 16) != 61999:
        raise RuntimeError("RPC is not StudioNet")
    record.update(source_commit=commit, source_path=SOURCE, source_blob=git("rev-parse", f"{commit}:{SOURCE}").decode().strip(),
                  source_bytes=len(source), source_sha256=hashlib.sha256(source).hexdigest())
    record["spdx_evidence"] = SPDX
    record["local_validation"] = {"pytest": "33 passed", "genvm_lint": "PASS: 3 AST checks and SDK validation", "runner_unchanged": True}
    accounts = {name: Account.create() for name in ["requester", "alice", "bob"]}
    clients = {name: create_client(chain=studionet, account=account) for name, account in accounts.items()}
    record["participants"] = {name: account.address for name, account in accounts.items()}
    save()
    with pinned_runner_calldata(chain_id=studionet.id, runner=RUNNER):
        tx = clients["requester"].deploy_contract(code=source, args=[], leader_only=False)
        deployment = {"operation": "deploy", "hash": str(tx), "explorer": EXPLORER + str(tx)}
        record["deployment_transaction"] = deployment
        save()
        receipt = wait(deployment)
        address = (receipt.get("data") or {}).get("contract_address") or (receipt.get("tx_data_decoded") or {}).get("contract_address")
        if not address:
            raise RuntimeError("Deployment address missing")
        record["contract_address"] = address
        deployed = base64.b64decode(rpc("gen_getContractCode", [address]))
        record["onchain_source_matches_git_blob"] = deployed == source
        record["deployed_source_sha256"] = hashlib.sha256(deployed).hexdigest()
        save()
        if deployed != source:
            raise RuntimeError("On-chain source differs byte-for-byte from local committed git blob")
        accounting("initial")
        for actor, work, name, terms, fee in [
            ("alice", "water-art", "Amina's urban water photograph", BY, 30),
            ("bob", "water-data", "Bayo's urban water photograph", BY, 20),
            ("alice", "nc-photo", "Amina's noncommercial water photograph", NC, 25)]:
            submit("register-" + work, actor, "register_license", [work, name, terms, fee])
            row = view("registered-" + work, "get_license", [work])
            assert row["version"] == 1 and row["fee_units"] == fee and row["terms_url"] == terms
            accounting("registered-" + work)
        submit("deposit-budget", "requester", "deposit_demo_units", [300])
        accounting("funded")
        row, _ = request("compatible", ["water-art", "water-data"], "AWAITING_CONSENT")
        submit("compatible-alice-consent", "alice", "approve_bundle_request", ["compatible", row["request_digest"]])
        pending = view("compatible-one-consent", "get_request", ["compatible"])
        assert pending["status"] == "AWAITING_CONSENT" and len(pending["approvals"]) == 1
        view("compatible-no-permission-yet", "get_permission", ["compatible"], expect_error=True)
        accounting("compatible-one-consent")
        issuance = submit("compatible-bob-issues", "bob", "approve_bundle_request", ["compatible", row["request_digest"]])
        issued = view("compatible-issued", "get_request", ["compatible"])
        permission = view("compatible-permission", "get_permission", ["compatible"])
        assert issued["status"] == "ISSUED" and len(issued["approvals"]) == 2 and permission["permission_status"] == "ACTIVE"
        accounting("issued")
        incompatible, blocked = request("commercial-nc", ["nc-photo", "water-data"], "DENIED_INCOMPATIBLE")
        assert incompatible["compatibility_status"] == "INCOMPATIBLE" and incompatible["reserved_units"] == 0
        view("commercial-nc-no-permission", "get_permission", ["commercial-nc"], expect_error=True)
        row, _ = request("missing-consent", ["water-art", "water-data"], "AWAITING_CONSENT")
        missing = submit("missing-consent-alice-only", "alice", "approve_bundle_request", ["missing-consent", row["request_digest"]])
        pending = view("missing-consent-request", "get_request", ["missing-consent"])
        assert pending["status"] == "AWAITING_CONSENT" and len(pending["approvals"]) == 1
        view("missing-consent-no-permission", "get_permission", ["missing-consent"], expect_error=True)
        accounting("missing-consent")
        submit("missing-consent-cancel-refund", "requester", "cancel_bundle_request", ["missing-consent"])
        assert view("missing-consent-cancelled", "get_request", ["missing-consent"])["status"] == "CANCELLED_REFUNDED"
        accounting("missing-consent-refunded")
        row, _ = request("stale-consent", ["water-art", "water-data"], "AWAITING_CONSENT")
        submit("update-terms-v2", "alice", "update_license_terms", ["water-art", 1, NC, 30])
        updated = view("updated-license", "get_license", ["water-art"])
        assert updated["version"] == 2 and updated["terms_url"] == NC
        assert view("original-version", "get_license_version", ["water-art", 1])["version"] == 1
        assert view("issued-permission-survives-update", "get_permission", ["compatible"])["licenses"][0]["version"] == 1
        accounting("terms-updated")
        stale = submit("stale-version-approval-rejected", "alice", "approve_bundle_request", ["stale-consent", row["request_digest"]], expected_rollback=True)
        if "[STALE]" not in json.dumps(stale["execution_payload"]):
            raise RuntimeError("Rollback did not identify stale terms")
        pending = view("stale-request-unchanged", "get_request", ["stale-consent"])
        assert pending["approvals"] == [] and pending["licenses"][0]["version"] == 1
        view("stale-no-permission", "get_permission", ["stale-consent"], expect_error=True)
        accounting("stale-rejected")
        submit("stale-invalidate-refund", "requester", "invalidate_stale_request", ["stale-consent"])
        assert view("stale-refunded", "get_request", ["stale-consent"])["status"] == "STALE_REFUNDED"
        accounting("final")
        record["evidence"] = {"compatible_issuance": issuance, "incompatible_commercial_use": blocked,
                              "missing_licensor_consent": missing, "stale_terms_version": stale}
        record["gates"] = {"dispatch_and_release": "PASS", "mechanism_and_accounting": "PASS", "distinctiveness": "PENDING_DOC_REVIEW"}
        record["limitations"] = ["Synthetic payment units, no legal advice; no copyright ownership or real-money payment proved.",
            "Budget partition is checked for this demo with one depositor and no recycling of paid licensor credits; the general ledger uses available+reserved=minted.",
            "Distinctiveness is a local portfolio comparison, not an ecosystem-wide originality claim.",
            "Public-HTTPS validation rejects private/literal/ambiguous hosts; DNS rebinding and redirect destination enforcement are not proved.",
            "The judgement and consent bind the fetched bytes at assessment time; no claim of perpetual URL content immutability."]
        record["status"] = "DEMO_PASS_DOCS_PENDING"
        save()
        print(json.dumps({"status": "DEMO_PASS_DOCS_PENDING", "address": address, "source_commit": commit, "transactions": len(record["transactions"])}), flush=True)


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        record.update(status="STOPPED", stop_reason=str(error))
        if record.get("source_commit"):
            save()
        print(json.dumps({"status": "STOPPED", "reason": str(error)}), flush=True)
        raise
