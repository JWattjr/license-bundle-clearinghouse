# StudioNet client compatibility record

Date: 2026-09-28 (Africa/Lagos). Contract runner: py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6.

## Diagnosis

The first deployed address, 0x907c4540Bb4f59aBAA5b91c9Fd8000bb2Ba87472, came from source commit eb01427c82e148aa3b50147f99724b88062622d0 with an exact on-chain Git blob match. The registration call sent with the portfolio .venv genlayer-py 0.19.0rc2 finalized with leader ERROR, contract_error, exit_code 1. The recorded resolver error was: ValueError in resolve_method: call to private method Contract.__handle_undefined_method__; call to private method Contract.__receive__. The saved view readback recorded GenLayerError: gen_call failed (code=-32000): execution failed for each of the six exposed views.

The successful semantic-barter write harness imports genlayer_py.create_client, not GenLayerJS or the GenLayer CLI. Its JSON release record says genlayer-py 0.19.0rc2, but the script hard-codes that field. The script imports TransactionStatus; the current portfolio .venv 0.19 package does not export it, while the available global Python runtime is genlayer-py 0.18.0 and does export it. The historical invocation did not save its executable/version, so attribution of that specific barter run to 0.18.0 is a strong runtime inference rather than a persisted per-process stamp.

A get_accounting() retry on the old address using genlayer-py 0.18.0 succeeded and returned {"available_units":0,"conserved":true,"fees_paid_units":0,"minted_units":0,"reserved_units":0}. The same 0.18.0 client then finalized a diagnostic bundle flow on that address: compatible permission issued after both licensors consented, 50 synthetic units credited as 30/20, conflicting commercial use classified INCOMPATIBLE, and the attempted approval rolled back. Nine transactions finalized in that diagnostic flow (7 leader SUCCESS, 2 expected rollback). This confirms the 0.19-to-0.18 client/runner dispatch mismatch. The old address is still a failed deployment and is not release evidence.

## Direct tests

From ROOT\.venv, the project direct suite passed 11 tests in 1.07s. tests/test_bundle.py exercises register_license and get_accounting. The test environment used genlayer-test 0.30.0rc2 with genlayer-py 0.19.0rc2; that test package declares genlayer-py>=0.19.0rc2, so it cannot be resolved together with the live-client pin. The checked-in requirements.txt is the direct-test stack. Use requirements-runtime.txt in a separate environment for StudioNet calls.

## Final release

The ordered diagnosis was conclusive at step 2: `get_accounting()` failed through the portfolio `.19.0rc2` path but succeeded against the same deployed address with `genlayer-py==0.18.0`; `.18.0` also successfully dispatched `register_license` and completed the diagnostic bundle flow. The exact `.19` registration error and saved view error are recorded above. The historical semantic-barter process did not stamp its executable/version, so its `.18.0` attribution remains an inference; the license-bundle retry and final release do stamp `.18.0`.

The final release from commit `e9bc336c1eaff364683431a494c8f13a4528c147` is at `0x52B06c3284CE66Bb5085790dc043AfC6B232963c`. Its deployment finalized with leader SUCCESS and its on-chain blob matches Git. The nine recorded demo transactions finalized (seven SUCCESS and two expected rollbacks), and the compatible / blocked-conflict readbacks passed. See [the release manifest](../deployments/studionet-release-2026-09-28-client-fix.json). The old `0x907c...7472` address remains a failed deployment and diagnostic-only.

The release helper initially omitted its `ADDRESS` global assignment, then hit an SDK metadata error after an initial registration was submitted. The registration is visible in latest-final state but its hash was not captured; the manifest records it as a separate non-evidence side effect, and the planned demo used new IDs. These helper errors are separate from the contract's `.19`/`.18` compatibility diagnosis.

## Use

Use `genlayer-py==0.18.0` from `requirements-runtime.txt` for StudioNet calls with the pinned runner. Keep the direct-test stack in `requirements.txt`: `genlayer-test==0.30.0rc2` requires `genlayer-py>=0.19.0rc2`, so the direct-test and live-runtime pins cannot be resolved together in one environment. The old address and its diagnostic rerun are not release evidence.
## Conclusive selector diagnosis (2026-10-12)

Both licence-bundle and semantic-barter define one class, subclass `gl.Contract`, use public view/write decorators, have `__init__(self)`, and otherwise contain imports, constants, and helper definitions at module level. The runner dependency is `py-lib-genlayer-std:11rhn002yfajawsz7fai6mykznbxkxs6l91iskj5cm82c92qhy3v`: `Contract.__init_subclass__` registers the single class in `__known_contract__`. Its `_genlayer_runner.py` resolver reads `ctx.cd.get("method", "")`; the venv client constructs `{ "": method }`. Thus all calls select the empty receive/fallback route and encounter private base methods. Constructor dispatch checks `is_init` first, explaining successful deployment. Address parameter types are unrelated.

The pinned venv direct runner successfully called `get_accounting()` and `register_license()`. Ordinary direct proxies bypass remote method selection, so that success alone did not test the fault. The new regression extracts and executes the actual cached runner resolver: the original envelope raises the recorded fallback error, and the adapted envelope dispatches a view and registration. Diagnosis stopped here; no throwaway deployment was needed. The scoped adapter changes only the selector key and restores the SDK after use; it refuses other chains, runners, and client versions. Historical `.18.0` evidence remains valid, but this release uses the requested portfolio venv throughout.
