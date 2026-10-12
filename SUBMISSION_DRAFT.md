# Submission draft

Status: live evidence verified; repository PRIVATE; Portal not used. Make the repo public before submitting.

## Portal note (804 characters)

License Bundle Clearinghouse judges each licence against a precisely requested use and checks the selected terms for conflicts. A compatible bundle reserves fixed fees, requires every licensor to consent to the exact version-bound request digest, then issues an expiring permission and credits the fees. Consent covers the commercial deal; GenLayer validators determine whether the terms actually permit the use and whether they conflict. The StudioNet demo issued a CC-BY-style commercial bundle and blocked a CC-BY-NC-style commercial use, missing consent, and stale-version approval. Source matches the pushed Git blob byte-for-byte. Three withheld siblings share the judgment/consent/funding mechanism and are not submitted. Synthetic payment units; no legal advice, real payment, or ownership proof.

## Evidence

Release `0x48E3539Ef83ed5459B13bB6D3778b003CBfd3a32`, source commit `d3d01f1c94dacc45cbdd607cdd2be28ecd6563c4`; exact deployed Git-blob byte match.

- [Compatible issuance: both licensors consented, 30/20 units paid](https://explorer-studio.genlayer.com/tx/0x55600cc1881e1c7e00f7b997445af3181438ff321052ab884164e198375e9005) — FINALIZED, leader SUCCESS; request `compatible` is ISSUED with active permission.
- [Expected failure: noncommercial term against commercial use](https://explorer-studio.genlayer.com/tx/0x9af35ba2dadcb02866d26b8559b3986fde15b97b3b4c333653b9f2d91af6ab77) — FINALIZED, leader SUCCESS; stored DENIED_INCOMPATIBLE, NC licence NOT_PERMITTED, conflict pair nc-photo/water-data, zero reservation, no permission.
- [Expected failure: one licensor consent missing](https://explorer-studio.genlayer.com/tx/0x751b0d7af0f7a275065e7d9db2250dd2f8ded7cbc47de2dd813ea27881f04cf1) — FINALIZED, leader SUCCESS; stored AWAITING_CONSENT with only Alice, and `get_permission` failed. This is a successful partial-consent transaction demonstrating blocked issuance, not a reverted write.
- [Expected failure: approval after terms version update](https://explorer-studio.genlayer.com/tx/0x56c9febfcdedbbd668579df3eb7a4b5f0493af3ea245b39bf9446d91f3a01c3c) — FINALIZED, leader ERROR, rollback containing [STALE]; no approval/permission, then reservation refunded.

All 16 transactions including deployment finalized; 15 leader SUCCESS, 1 expected stale-version rollback. The incompatible and missing-consent failures are successful state transitions that deny permission; only stale approval is a reverted write. Full state readbacks and receipts: [release manifest](deployments/studionet-release-2026-10-12.json).

Final demo budget: 300 deposited = 250 requester available + 0 reserved + 50 paid, nonnegative. Recipient balances remain separately spendable credits; this partition is verified without recycling them.

Does not prove: real payments or copyright ownership; units are synthetic and judgments are not legal advice.

The original `0x907c4540Bb4f59aBAA5b91c9Fd8000bb2Ba87472` deployment is failed and excluded. Three withheld siblings share the mechanism and are not submitted. No visibility change or Portal submission was performed.

Explorer page access returned HTTP 403 to automated verification; transaction contents and finality were verified through StudioNet RPC and saved receipts.
