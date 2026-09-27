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

The recorded direct-mode run passed 11 tests. GenVM lint passed 3 checks, SDK validation reported 15 methods (6 views and 9 writes), and schema extraction succeeded. No deployment was run.
