# Submission draft

Repository PUBLIC; existing submission pending review. No Portal edits or visibility changes were performed for this release. The user will update the submission.

## Portal note (781 characters)

License Bundle Clearinghouse has GenLayer validators fetch the real, tag-pinned SPDX licence text, judge the precise requested use and conflicts between selected terms, and compare raw-body SHA-256 digests and availability. Consent binds the exact fetched bytes, versions, use and fixed fees. Only a compatible, funded bundle with every licensor's approval issues an expiring permission and credits fees. The StudioNet demo issued a CC-BY-4.0 advertising bundle and blocked CC-BY-NC-4.0 commercial use, missing consent and stale-version approval. Deployed source matches the local deployment commit byte-for-byte; origin/main is checked for the identical contract blob after the final push. Synthetic payment units; no legal advice, copyright ownership or real-money payment proof.

## Evidence

- [Explorer contract: 0x3C2C00d43de74399cEf2c74051675050C91ad366](https://explorer-studio.genlayer.com/address/0x3C2C00d43de74399cEf2c74051675050C91ad366)
- [Pinned deployed contract file, commit 26d8a0f16de14543c602d80c8253139b49bf6929](https://github.com/JWattjr/license-bundle-clearinghouse/blob/26d8a0f16de14543c602d80c8253139b49bf6929/contracts/license_bundle_clearinghouse.py)
- [Fetched-SPDX release manifest](https://github.com/JWattjr/license-bundle-clearinghouse/blob/main/deployments/studionet-release-2026-10-12-spdx.json)
- [SPDX v3.25.0 CC-BY-4.0 text](https://raw.githubusercontent.com/spdx/license-list-data/v3.25.0/text/CC-BY-4.0.txt)
- [SPDX v3.25.0 CC-BY-NC-4.0 text](https://raw.githubusercontent.com/spdx/license-list-data/v3.25.0/text/CC-BY-NC-4.0.txt)
- [Compatible issuance](https://explorer-studio.genlayer.com/tx/0x5ec8ac483b483a087323d0c2b5383239cbbb12bc1f6e3749a5f54b1d04f7f002) — FINALIZED; leader SUCCESS. ISSUED after both approvals; fixed credits 30/20.
- [NC commercial-use block](https://explorer-studio.genlayer.com/tx/0x73df5dcd4a810c6f96b17a25a85e02e75f2bb4e2db72aa89b413fe7cd298b41d) — FINALIZED; leader SUCCESS. NC work NOT_PERMITTED, DENIED_INCOMPATIBLE, no reservation or permission.
- [Missing-consent block](https://explorer-studio.genlayer.com/tx/0x0778a52cd76a643a89edfa4eae42d704e91d0dd14be004653feecb1918aa0afa) — FINALIZED; leader SUCCESS. One approval, AWAITING_CONSENT, no permission; later cancelled and refunded.
- [Stale-version approval block](https://explorer-studio.genlayer.com/tx/0xe3caccd4fc9cb56791160128a04efc38da93237ae0e041c98fe086c07dcb2b99) — FINALIZED; leader ERROR with [STALE] rollback. No approval or permission; later invalidated and refunded.

The fetched-SPDX release is [0x3C2C00d43de74399cEf2c74051675050C91ad366](https://explorer-studio.genlayer.com/address/0x3C2C00d43de74399cEf2c74051675050C91ad366), deployed from local commit `26d8a0f16de14543c602d80c8253139b49bf6929` before any push. The deployed source equals that commit's Git blob byte-for-byte. All 16 transactions finalized: 15 leader SUCCESS executions and one expected stale-approval ERROR/rollback. ACCEPTED observations, FINALIZED status, and execution outcomes are separate manifest fields. Every demo step has a latest-final read-back. All four compatibility assessments stored hashes equal to the independently curl-verified SPDX bodies: CC-BY-4.0 17,023 bytes and CC-BY-NC-4.0 17,649 bytes.

The incompatible and missing-consent blocks are successful writes that prevent permission; only the stale approval rolls back. Missing/stale reservations were refunded after the blocked states were read back.

The funded requester budget remained nonnegative and satisfied `deposited = requester available + reserved + paid` after every step; final `300 = 250 + 0 + 50`. Licensor credits were 30 and 20 and were not reused. The general ledger separately conserves `minted = all spendable balances + reserved`; cumulative fees paid are turnover, so adding them to all spendable balances would double-count credits.

Does not prove: real-money payment or ownership; units are synthetic and judgments are not legal advice.

The prior participant-text release `0x48E3539Ef83ed5459B13bB6D3778b003CBfd3a32` is historical. The original dispatch-failed `0x907c4540Bb4f59aBAA5b91c9Fd8000bb2Ba87472` is failed and excluded from evidence.
