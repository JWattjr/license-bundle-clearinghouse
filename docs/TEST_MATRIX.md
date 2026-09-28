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

The direct-mode suite passed 11 tests in ROOT `.venv` (1.07s) using `genlayer-test==0.30.0rc2` and `genlayer-py==0.19.0rc2`; this is the test stack, separate from the `.18.0` StudioNet runtime because the test package requires `genlayer-py>=0.19.0rc2`. GenVM lint passed 3 checks, SDK validation reported 15 methods (6 views and 9 writes), and schema extraction succeeded; those checks were not rerun for this release.

The 2026-09-28 live release at `0x52B06c3284CE66Bb5085790dc043AfC6B232963c` finalized with leader SUCCESS and an exact source-blob match. Its nine recorded demo transactions finalized (7 leader SUCCESS; 2 expected rollback). All six public view methods were read back, including an unavailable permission before all consent and a denied conflicting request. Final accounting was 100 minted, 100 available, 0 reserved, and 50 fees paid. One earlier helper-submitted `artwork` registration has no captured hash after a harness metadata error; its latest-final state is disclosed separately and excluded from release evidence. Full receipts and readbacks are in [the final release manifest](../deployments/studionet-release-2026-09-28-client-fix.json). The original `0x907c...7472` deployment remains failed and non-evidence.
