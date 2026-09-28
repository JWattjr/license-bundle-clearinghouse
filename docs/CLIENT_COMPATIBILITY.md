# StudioNet client compatibility record

Date: 2026-09-28 (Africa/Lagos). Contract runner: py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6.

## Diagnosis

The first deployed address, 0x907c4540Bb4f59aBAA5b91c9Fd8000bb2Ba87472, came from source commit eb01427c82e148aa3b50147f99724b88062622d0 with an exact on-chain Git blob match. The registration call sent with the portfolio .venv genlayer-py 0.19.0rc2 finalized with leader ERROR, contract_error, exit_code 1. The recorded resolver error was: ValueError in resolve_method: call to private method Contract.__handle_undefined_method__; call to private method Contract.__receive__. The saved view readback recorded GenLayerError: gen_call failed (code=-32000): execution failed for each of the six exposed views.

The successful semantic-barter write harness imports genlayer_py.create_client, not GenLayerJS or the GenLayer CLI. Its JSON release record says genlayer-py 0.19.0rc2, but the script hard-codes that field. The script imports TransactionStatus; the current portfolio .venv 0.19 package does not export it, while the available global Python runtime is genlayer-py 0.18.0 and does export it. The historical invocation did not save its executable/version, so attribution of that specific barter run to 0.18.0 is a strong runtime inference rather than a persisted per-process stamp.

A get_accounting() retry on the old address using genlayer-py 0.18.0 succeeded and returned {"available_units":0,"conserved":true,"fees_paid_units":0,"minted_units":0,"reserved_units":0}. The same 0.18.0 client then finalized a diagnostic bundle flow on that address: compatible permission issued after both licensors consented, 50 synthetic units credited as 30/20, conflicting commercial use classified INCOMPATIBLE, and the attempted approval rolled back. Nine transactions finalized in that diagnostic flow (7 leader SUCCESS, 2 expected rollback). This confirms the 0.19-to-0.18 client/runner dispatch mismatch. The old address is still a failed deployment and is not release evidence.

## Direct tests

From ROOT\.venv, the project direct suite passed 11 tests in 1.07s. tests/test_bundle.py exercises register_license and get_accounting. The test environment used genlayer-test 0.30.0rc2 with genlayer-py 0.19.0rc2; that test package declares genlayer-py>=0.19.0rc2, so it cannot be resolved together with the live-client pin. The checked-in requirements.txt is the direct-test stack. Use requirements-runtime.txt in a separate environment for StudioNet calls.

## Use

Use genlayer-py 0.18.0 for StudioNet calls with the pinned runner. The full release still requires a fresh deployment from the client-fix source commit, an exact source-blob check, finalized deployment with leader SUCCESS, and the planned demo. Do not count the original address or its diagnostic rerun as release evidence.
