# License Bundle Clearinghouse

`LicenseBundleClearinghouse` composes permission from two to five registered licenses for one precisely scoped use. Each named licensor registers a versioned terms record and fixed fee. A requester deposits internal demo units, proposes a use with consent and permission expiry dates, and receives a compatibility assessment against the exact selected versions.

Incompatible or uncertain requests are recorded without reserving funds. A compatible request reserves the sum of its fixed fees. Every distinct licensor must approve the same request digest, which includes the requested use and each selected terms version. Once all licensors consent, the contract issues a permission snapshot and credits each fixed fee to its licensor. A later terms update makes a pending request stale; it does not rewrite an already issued permission.

## Toolchain

The contract pins `py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6`, accepted by the installed GenVM linter. The fallback runner finalized a trivial StudioNet deployment and write/read-back probe; this project contract has not yet been deployed. `requirements.txt` pins the locally installed v0.6 RC test toolchain.

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
genvm-lint lint contracts/license_bundle_clearinghouse.py
genvm-lint validate contracts/license_bundle_clearinghouse.py
genvm-lint schema contracts/license_bundle_clearinghouse.py --output contracts/abi.json
python -m pytest
```

Direct-mode tests mock model responses. They do not establish live consensus, network finality, or remote runner availability.

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

Demo units are internal ledger entries, not real funds. Registration does not prove copyright ownership or legal authority. Compatibility is a model judgment over licensor-provided text, not legal advice or proof that a license is enforceable. See [mechanism differentiation](docs/MECHANISM_DIFFERENTIATION.md), [test matrix](docs/TEST_MATRIX.md), [security notes](docs/SECURITY_NOTES.md), and the [undeployed submission draft](SUBMISSION_DRAFT.md).

## Why GenLayer

Validators must interpret published license restrictions together with the requested use and the other selected terms; licensor approvals authorize the exact request but do not independently establish cross-license compatibility, which deterministic code cannot infer from natural language.
