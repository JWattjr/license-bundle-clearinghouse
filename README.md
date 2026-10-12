# License Bundle Clearinghouse

`LicenseBundleClearinghouse` composes permission from two to five registered licenses for one precisely scoped use. Each named licensor registers a versioned terms record and fixed fee. A requester deposits internal demo units, proposes a use with consent and permission expiry dates, and receives a compatibility assessment against the exact selected versions.

Incompatible or uncertain requests are recorded without reserving funds. A compatible request reserves the sum of its fixed fees. Every distinct licensor must approve the same request digest, which includes the requested use and each selected terms version. Once all licensors consent, the contract issues a permission snapshot and credits each fixed fee to its licensor. A later terms update makes a pending request stale; it does not rewrite an already issued permission.

## Toolchain and verified release

The runner remains `py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6`. The portfolio venv uses `genlayer-py==0.19.0rc2`; its empty-string method key is incompatible with this runner's `method` key. `studionet_compat.py` changes only that selector inside a context restricted to StudioNet, this runner, and this client version. The regression executes the actual pinned runner resolver and reproduces the old fallback error before verifying corrected view/write dispatch. See [the diagnosis](docs/CLIENT_COMPATIBILITY.md).

The 2026-10-12 release is `0x48E3539Ef83ed5459B13bB6D3778b003CBfd3a32`, deployed from pushed commit `d3d01f1c94dacc45cbdd607cdd2be28ecd6563c4`. Deployment and all 15 demo writes reached FINALIZED; 15 executions were leader SUCCESS and 1 was the labeled expected stale-version rollback. ACCEPTED observations and FINALIZED status are recorded separately from execution results. The deployed source equals the Git blob byte-for-byte. The compatible commercial CC-BY-style bundle issued after both licensors approved and credited fixed fees of 30 and 20. Commercial use of the CC-BY-NC-style work was denied with a NOT_PERMITTED finding and a recorded conflict pair against the other selected work, one missing consent prevented permission, and consent after a version update rolled back as stale. Every step has a latest-final read-back; pending missing/stale requests were refunded after evidence was captured.

See [the current release manifest](deployments/studionet-release-2026-10-12.json) and [the evidence list and Portal draft](SUBMISSION_DRAFT.md). The original `0x907c4540Bb4f59aBAA5b91c9Fd8000bb2Ba87472` deployment remains failed and is not evidence; same-address diagnostic reads are excluded. The earlier 2026-09-28 release remains historical evidence. The repo is PRIVATE, and nothing has been submitted to the Portal.

From this repository, use the requested portfolio venv:

```powershell
& '..\.venv\Scripts\genvm-lint.exe' check contracts/license_bundle_clearinghouse.py --json
& '..\.venv\Scripts\python.exe' -m pytest
```

Lint passed and all 13 tests passed. Direct tests mock model responses and do not prove live consensus. `studionet_release.py` documents the completed live procedure and refuses to overwrite an existing manifest; do not rerun it to create duplicate evidence. The historical `requirements-runtime.txt` `.18.0` pin remains an alternative client; this release uses the requested venv and scoped adapter.

## Lifecycle

1. A licensor registers a unique work ID, work name, terms text, and fixed positive fee. Terms versions are immutable history entries; only the licensor may advance the current version and fee.
2. A requester mints demo balance into their ledger account and proposes two to five work IDs, an exact use description, a consent deadline, and permission expiry. The selected terms, owners, fees, scope, and dates are frozen into the compatibility snapshot.
3. GenLayer evaluates whether the use fits each license and whether selected licenses conflict with one another. Validators independently assess the same on-chain snapshot. A conflict, restriction, uncertainty, malformed response, or disagreement cannot start consent or reserve funds.
4. For a compatible bundle, the exact total fee moves into a request reservation. Each distinct licensor approves the exact request digest. A licensor may reject; the requester may cancel; anyone may expire after the consent deadline. These paths refund the reservation.
5. If any selected license version changes before all approvals, approval fails as stale. Anyone may invalidate the pending request and return its funds. Once all licensors consent, the contract credits each work's frozen fee to its licensor and stores the exact issued permission snapshot.
6. Issued permissions keep their original terms and scope through the frozen permission expiry. A subsequent terms change affects future requests and pending requests only; it does not silently modify or revoke earlier permission records.

## API

Writes are `deposit_demo_units`, `register_license`, `update_license_terms`, `request_bundle`, `approve_bundle_request`, `reject_bundle_request`, `cancel_bundle_request`, `expire_bundle_request`, and `invalidate_stale_request`. Views are `get_license`, `get_license_version`, `get_request`, `get_permission`, `get_balance`, and `get_accounting`. The generated ABI is [contracts/abi.json](contracts/abi.json).

There are no constructor arguments; see [examples/constructor.json](examples/constructor.json). The full consent/payment example is [examples/demo_sequence.md](examples/demo_sequence.md).

## Bounds and failure behavior

The registry supports 32 works, 32 bundle requests, 64 participant accounts, at most 8 versions per work, and bundles of up to 5 works. Text, fee amounts, IDs, and permission duration are bounded. All fees are fixed by the selected license versions and distributed deterministically from one reserved amount. The accounting invariant is `available demo balances + pending reservations = total demo units minted`.

Demo units are internal ledger entries, not real funds. Registration does not prove copyright ownership or legal authority. Compatibility is a model judgment over licensor-provided text, not legal advice or proof that a license is enforceable. See [mechanism differentiation](docs/MECHANISM_DIFFERENTIATION.md), [test matrix](docs/TEST_MATRIX.md), [security notes](docs/SECURITY_NOTES.md), and the [submission draft](SUBMISSION_DRAFT.md).

## Why GenLayer

Validators must interpret published license restrictions together with the requested use and the other selected terms; licensor approvals authorize the exact request but do not independently establish cross-license compatibility, which deterministic code cannot infer from natural language.

## Venv dispatch fix (2026-10-12)

The pinned runner reads the `method` calldata key, while the portfolio venv client (`genlayer-py==0.19.0rc2`) emits the empty-string key; use the scoped adapter in `studionet_compat.py` for this runner on StudioNet. The regression executes the pinned runner resolver with both envelopes, then dispatches `get_accounting` and `register_license`. The contract source and runner are unchanged.

Licensor consent covers the commercial deal, while GenLayer validators judge whether the licence terms actually permit the requested use and whether the selected terms conflict.

## Release budget accounting

The demo checks `deposited = requester available + reserved + paid` after every step, with no negative values. Final partition: `300 = 250 + 0 + 50`. Licensor balances were 30 and 20. The contract's general ledger instead conserves `minted = all spendable balances + reserved`; licensor payments are credits within that ledger, and `fees_paid_units` is cumulative turnover. Adding cumulative paid to all spendable balances would double-count payment. The demo does not reuse licensor credits, so its requester-budget partition is valid; it does not prove that deposited equals available plus reserved plus cumulative turnover under arbitrary recycling.
