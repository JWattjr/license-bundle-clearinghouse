# Test matrix

Run `python -m pytest` from the repository root. Direct-mode tests mock model responses and do not establish live consensus or network finality.

| Invariant or behavior | Test |
|---|---|
| Compatible bundle reserves the exact fee, waits for every licensor, distributes fees, and keeps issued version 1 after a later update | `test_compatible_bundle_requires_every_licensor_and_distributes_fixed_fees` |
| Pairwise conflict prevents issuance and leaves user balance untouched | `test_conflicting_terms_block_issuance_before_reserving_user_funds` |
| Individually restricted or uncertain license cannot start consent or payment | `test_restricted_or_uncertain_license_never_enters_consent_or_payment` (2 parameter cases) |
| Only selected licensors can approve; consent is bound to the exact digest and cannot be replayed | `test_each_consent_binds_to_the_exact_request_and_only_named_licensors_may_approve` |
| Licensor rejection, requester cancellation, and post-deadline expiry return the reservation | `test_rejection_cancellation_and_expiry_return_the_reserved_budget` |
| Updating a selected version blocks stale consent and enables one permissionless refund | `test_version_change_stales_pending_request_and_refunds_once_without_changing_old_permission` |
| Malformed leader fields revert; direct validator rejects a conflicting leader result | `test_malformed_model_output_reverts_then_validator_rejects_disagreement` |
| Insufficient balance fails before compatibility judgment | `test_insufficient_balance_fails_before_compatibility_judgment` |
| Per-work version history stops at its fixed cap | `test_license_version_history_has_a_fixed_cap` |
| Every model-returned judgment field is validated and compared or bound to frozen input | `test_every_returned_judgment_field_is_compared_or_snapshot_bound` |

| Pinned runner rejects empty selector, then resolves no-arg view and registration through scoped adapter | `test_legacy_runner_dispatches_view_and_registration` |
| Adapter refuses other chains/runners and preserves constructor/args/kwargs envelopes | `test_compatibility_is_scoped_and_preserves_arguments` |

2026-10-12 verification: 13 pytest cases passed in the requested portfolio venv. GenVM lint check passed 3 AST checks and SDK validation of 15 methods (6 views, 9 writes). The newer-runner notice is informational; the requested runner pin is unchanged.

The 2026-10-12 release is `0x48E3539Ef83ed5459B13bB6D3778b003CBfd3a32`, deployed from pushed commit `d3d01f1c94dacc45cbdd607cdd2be28ecd6563c4`. Deployment and all 15 demo writes reached FINALIZED; 15 executions were leader SUCCESS and 1 was the labeled expected stale-version rollback. ACCEPTED observations and FINALIZED status are recorded separately from execution results. The deployed source equals the Git blob byte-for-byte. The compatible commercial CC-BY-style bundle issued after both licensors approved and credited fixed fees of 30 and 20. Commercial use of the CC-BY-NC-style work was denied with a NOT_PERMITTED finding and a recorded conflict pair against the other selected work, one missing consent prevented permission, and consent after a version update rolled back as stale. Every step has a latest-final read-back; pending missing/stale requests were refunded after evidence was captured.

- [Compatible issuance: both licensors consented, 30/20 units paid](https://explorer-studio.genlayer.com/tx/0x55600cc1881e1c7e00f7b997445af3181438ff321052ab884164e198375e9005) — FINALIZED, leader SUCCESS; request `compatible` is ISSUED with active permission.
- [Expected failure: noncommercial term against commercial use](https://explorer-studio.genlayer.com/tx/0x9af35ba2dadcb02866d26b8559b3986fde15b97b3b4c333653b9f2d91af6ab77) — FINALIZED, leader SUCCESS; stored DENIED_INCOMPATIBLE, zero reservation, no permission.
- [Expected failure: one licensor consent missing](https://explorer-studio.genlayer.com/tx/0x751b0d7af0f7a275065e7d9db2250dd2f8ded7cbc47de2dd813ea27881f04cf1) — FINALIZED, leader SUCCESS; stored AWAITING_CONSENT with only Alice, and `get_permission` failed. This is a successful partial-consent transaction demonstrating blocked issuance, not a reverted write.
- [Expected failure: approval after terms version update](https://explorer-studio.genlayer.com/tx/0x56c9febfcdedbbd668579df3eb7a4b5f0493af3ea245b39bf9446d91f3a01c3c) — FINALIZED, leader ERROR, rollback containing [STALE]; no approval/permission, then reservation refunded.

Budget checks passed after each step; final deposited = available + reserved + paid is 300 = 250 + 0 + 50. This partition excludes recipient fee credits from requester availability; the general ledger separately conserves minted = all spendable balances + reserved.

Complete receipts, readbacks, status observations, and accounting checks: [release manifest](../deployments/studionet-release-2026-10-12.json). The failed `0x907c...7472` deployment and diagnostic reads are excluded from release evidence.
