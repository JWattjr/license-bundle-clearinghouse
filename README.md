# License Bundle Clearinghouse

`LicenseBundleClearinghouse` judges the real licence text fetched from public HTTPS evidence for a precisely requested use. Participants register a URL and fixed fee, not licence text. A bundle selects two or three works. A compatible assessment reserves the total fixed fee and requires every distinct licensor's consent before issuing an expiring permission and crediting each licensor.

Licensor consent covers the commercial deal, while GenLayer validators judge whether the licence terms actually permit the requested use and whether the selected terms conflict.

## Verified fetched-SPDX release

The fetched-SPDX release is [0x3C2C00d43de74399cEf2c74051675050C91ad366](https://explorer-studio.genlayer.com/address/0x3C2C00d43de74399cEf2c74051675050C91ad366), deployed from local commit `26d8a0f16de14543c602d80c8253139b49bf6929` before any push. The deployed source equals that commit's Git blob byte-for-byte. All 16 transactions finalized: 15 leader SUCCESS executions and one expected stale-approval ERROR/rollback. ACCEPTED observations, FINALIZED status, and execution outcomes are separate manifest fields. Every demo step has a latest-final read-back. All four compatibility assessments stored hashes equal to the independently curl-verified SPDX bodies: CC-BY-4.0 17,023 bytes and CC-BY-NC-4.0 17,649 bytes.

The commercial use is: Use both selected photographs in a paid advertising campaign for a for-profit business, including reproducing, adapting and commercially distributing them. Credit each creator, link to each licence, and mark all modifications. Claim no endorsement and impose no DRM, exclusivity or additional restrictions on recipients exercising the licensed rights.

- [Compatible issuance](https://explorer-studio.genlayer.com/tx/0x5ec8ac483b483a087323d0c2b5383239cbbb12bc1f6e3749a5f54b1d04f7f002) — FINALIZED; leader SUCCESS. ISSUED after both approvals; fixed credits 30/20.
- [NC commercial-use block](https://explorer-studio.genlayer.com/tx/0x73df5dcd4a810c6f96b17a25a85e02e75f2bb4e2db72aa89b413fe7cd298b41d) — FINALIZED; leader SUCCESS. NC work NOT_PERMITTED, DENIED_INCOMPATIBLE, no reservation or permission.
- [Missing-consent block](https://explorer-studio.genlayer.com/tx/0x0778a52cd76a643a89edfa4eae42d704e91d0dd14be004653feecb1918aa0afa) — FINALIZED; leader SUCCESS. One approval, AWAITING_CONSENT, no permission; later cancelled and refunded.
- [Stale-version approval block](https://explorer-studio.genlayer.com/tx/0xe3caccd4fc9cb56791160128a04efc38da93237ae0e041c98fe086c07dcb2b99) — FINALIZED; leader ERROR with [STALE] rollback. No approval or permission; later invalidated and refunded.

See [release manifest](deployments/studionet-release-2026-10-12-spdx.json), [Portal note and complete evidence list](SUBMISSION_DRAFT.md), [test matrix](docs/TEST_MATRIX.md) and [distinctiveness review](docs/DISTINCTIVENESS.md). The repository is PUBLIC and its existing submission is pending review; this release did not touch the Portal or visibility.

The previous `studionet-release-2026-10-12.json` records historical participant-typed terms and is superseded for fetched-evidence claims. The original `0x907c...7472` deployment remains failed, not evidence.

## Evidence and consent binding

Each leader and validator fetches every selected URL using `gl.nondet.web.get`. A licence is AVAILABLE only for HTTP 200 with a nonempty complete strict UTF-8 body of at most 20,000 raw bytes. Nothing is truncated or whitespace-normalized before hashing. Invalid UTF-8, HTTP failure, missing/empty body, fetch failure or oversize body yields UNAVAILABLE. Any unavailable licence makes the entire request DENIED_UNVERIFIABLE with no reservation or permission, without asking the model to invent missing terms.

The stored compatibility record contains each work ID, version, URL, availability, raw-body SHA-256 digest and raw byte length. Validators independently re-fetch and judge, then exactly compare those fields, every permission finding, conflict pair and frozen snapshot digest. A malformed result or validator error cannot agree merely because the leader also failed. The request digest that licensors approve includes the complete compatibility record, so consent is bound to the fetched licence bytes as assessed. Fetching is done at assessment time; approval does not assert that a mutable URL still serves the same bytes later. Use pinned evidence URLs.

Licence text, URLs, work names and requested use are untrusted prompt data. The model judges only use permission and conflicts; deterministic code owns versions, fees, funding, parties, consent, dates and refunds. NOT_PERMITTED or conflicting terms produce DENIED_INCOMPATIBLE; uncertainty produces DENIED_UNCERTAIN. Neither reserves funds.

## API and lifecycle

`register_license(work_id, work_name, terms_url, fee_units)` registers version 1. `update_license_terms(work_id, expected_version, terms_url, fee_units)` requires the licensor and matching version, then advances the version and immutable history entry. A URL change therefore stales every pending request selecting the previous version; previously issued permissions keep their original version, evidence digests, scope and expiry.

The requester deposits synthetic demo units and calls `request_bundle(request_id, work_ids_json, requested_use, consent_deadline_iso, permission_expiry_iso)`. After compatibility and reservation, each required licensor calls `approve_bundle_request(request_id, expected_request_digest)`. All approvals issue and pay once. Rejection, requester cancellation, deadline expiry or stale invalidation refunds the one reservation.

Views are `get_license`, `get_license_version`, `get_request`, `get_permission`, `get_balance` and `get_accounting`. Other writes are `deposit_demo_units`, `reject_bundle_request`, `cancel_bundle_request`, `expire_bundle_request` and `invalidate_stale_request`. See [ABI](contracts/abi.json) and [demo sequence](examples/demo_sequence.md). No constructor arguments are required.

Bounds: 32 works, 32 requests, 64 accounts, eight versions per work, three works per bundle, 20,000 raw bytes per fetched licence and 180 days maximum permission duration.

## Runner, dispatch and checks

Runner remains `py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6`. The portfolio venv client `genlayer-py==0.19.0rc2` emits an empty-string method selector, while this runner expects `method`; the scoped `studionet_compat.pinned_runner_calldata` adapter fixes dispatch on StudioNet only. See [dispatch diagnosis](docs/CLIENT_COMPATIBILITY.md). The runner resolver regression reproduces the fallback error and verifies adapted view/write dispatch.

```powershell
& '..\.venv\Scripts\genvm-lint.exe' check contracts/license_bundle_clearinghouse.py --json
& '..\.venv\Scripts\python.exe' -m pytest -q
```

Lint passed (three AST checks and SDK validation), and 33 pytest cases passed. Direct tests mock fetches and model output; the manifest supplies separate live evidence. `studionet_spdx_release.py` is the completed one-shot live procedure and refuses to overwrite its manifest. All commits were local before deployment; one final push follows the three gate checks. `origin/main` is checked for the identical deployed contract blob, while the later evidence commit may be its tip.

## Accounting and limits of evidence

The funded requester budget remained nonnegative and satisfied `deposited = requester available + reserved + paid` after every step; final `300 = 250 + 0 + 50`. Licensor credits were 30 and 20 and were not reused. The general ledger separately conserves `minted = all spendable balances + reserved`; cumulative fees paid are turnover, so adding them to all spendable balances would double-count credits.

Synthetic payment units; no legal advice. This does not prove copyright ownership, legal enforceability, real-money payment, arbitrary payment recycling, ecosystem-wide originality, perpetual URL immutability, or DNS/redirect destination enforcement. URL validation is structural public-HTTPS validation; it rejects literal IPs, private/local hostnames, credentials, ambiguous authority and non-443 ports.
