# Submission draft — not ready

**Status: NOT READY.** A StudioNet deployment finalized, but the first contract method call failed before registration. The repository remains private and the contract has not been submitted to the Portal.

## Project

`LicenseBundleClearinghouse` composes permission from two to five versioned licenses for one requested use. It reserves fixed demo fees, requires every distinct licensor to approve the same request digest, then records an expiring permission and credits each licensor.

## Evidence and limits

The attempted terms and uses were synthetic participant-submitted text; the contract does not fetch external sources. Demo units are internal ledger entries, not real funds or custody.

**The live run proves:** the committed source deployed and its on-chain Git blob matched the pre-deploy commit.

**The live run does not prove:** public methods execute, validators assess a bundle, or any permission or payout can complete.

See [`deployments/studionet-release-2026-09-28.json`](deployments/studionet-release-2026-09-28.json) for transaction receipts, attempted public-view readback, run types, and the separate readiness gates.
