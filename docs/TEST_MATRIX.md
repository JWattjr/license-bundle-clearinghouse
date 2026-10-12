# Test matrix

Requested venv verification: GenVM lint PASS (three AST checks; SDK validation of 15 methods), pytest 33 passed. Direct tests mock network/model responses and exercise the pinned direct runner; they do not establish live finality.

| Coverage | Test |
|---|---|
| Complete real SPDX body reaches leader and validator prompts; raw digest and consent binding | `test_judgment_receives_complete_real_text_and_consent_binds_raw_digest` |
| HTTP failure, oversized raw body, multibyte raw-byte overflow, invalid UTF-8 and empty body fail closed; every selected URL fetched | `test_unavailable_oversized_or_invalid_utf8_fails_closed_without_model` (5 cases) |
| Exact 20,000-byte boundary accepted; forged digest and different validator-fetched bytes rejected | `test_exact_byte_limit_is_allowed_and_digest_forgery_or_changed_fetch_is_rejected` |
| Private, literal, credential-bearing, ambiguous or non-HTTPS URL rejected | `test_registration_rejects_nonpublic_or_ambiguous_urls` (12 cases) |
| Bundle cap three | `test_bundle_cap_is_three` |
| Every licensor required; fixed fees reserved and credited once; original permission survives URL update | `test_compatible_bundle_requires_every_licensor_and_distributes_fixed_fees` |
| Pairwise conflict, NOT_PERMITTED and UNCERTAIN prevent reservation/issuance | Existing conflict/restricted tests (3 cases) |
| Role checks, exact-digest consent and duplicate approval rejection | Existing exact-consent test |
| Rejection, cancellation, expiry and stale invalidation refund | Existing refund/stale tests |
| URL change advances version; old consent rejected; bounded immutable history | Existing version-change/history tests |
| Malformed model fields and forged finding rejected | Existing malformed/disagreement test |
| Insufficient funding prevents any judgment | Existing insufficient-balance test |
| Exact evidence/result field comparison and snapshot binding | `test_every_returned_judgment_field_is_compared_or_snapshot_bound` |
| Actual legacy runner dispatch and adapter guards | `test_legacy_runner_dispatches_view_and_registration`, `test_compatibility_is_scoped_and_preserves_arguments` |

## StudioNet evidence

The fetched-SPDX release is [0x3C2C00d43de74399cEf2c74051675050C91ad366](https://explorer-studio.genlayer.com/address/0x3C2C00d43de74399cEf2c74051675050C91ad366), deployed from local commit `26d8a0f16de14543c602d80c8253139b49bf6929` before any push. The deployed source equals that commit's Git blob byte-for-byte. All 16 transactions finalized: 15 leader SUCCESS executions and one expected stale-approval ERROR/rollback. ACCEPTED observations, FINALIZED status, and execution outcomes are separate manifest fields. Every demo step has a latest-final read-back. All four compatibility assessments stored hashes equal to the independently curl-verified SPDX bodies: CC-BY-4.0 17,023 bytes and CC-BY-NC-4.0 17,649 bytes.

- [Compatible issuance](https://explorer-studio.genlayer.com/tx/0x5ec8ac483b483a087323d0c2b5383239cbbb12bc1f6e3749a5f54b1d04f7f002) — FINALIZED; leader SUCCESS. ISSUED after both approvals; fixed credits 30/20.
- [NC commercial-use block](https://explorer-studio.genlayer.com/tx/0x73df5dcd4a810c6f96b17a25a85e02e75f2bb4e2db72aa89b413fe7cd298b41d) — FINALIZED; leader SUCCESS. NC work NOT_PERMITTED, DENIED_INCOMPATIBLE, no reservation or permission.
- [Missing-consent block](https://explorer-studio.genlayer.com/tx/0x0778a52cd76a643a89edfa4eae42d704e91d0dd14be004653feecb1918aa0afa) — FINALIZED; leader SUCCESS. One approval, AWAITING_CONSENT, no permission; later cancelled and refunded.
- [Stale-version approval block](https://explorer-studio.genlayer.com/tx/0xe3caccd4fc9cb56791160128a04efc38da93237ae0e041c98fe086c07dcb2b99) — FINALIZED; leader ERROR with [STALE] rollback. No approval or permission; later invalidated and refunded.

The funded requester budget remained nonnegative and satisfied `deposited = requester available + reserved + paid` after every step; final `300 = 250 + 0 + 50`. Licensor credits were 30 and 20 and were not reused. The general ledger separately conserves `minted = all spendable balances + reserved`; cumulative fees paid are turnover, so adding them to all spendable balances would double-count credits.

Unavailable evidence and forged-digest paths are direct-test evidence; they were not submitted as additional live transactions. The four requested live scenarios were run once, with no repeated judgment attempts. Complete receipts, readbacks and accounting checks are in [the manifest](../deployments/studionet-release-2026-10-12-spdx.json).
