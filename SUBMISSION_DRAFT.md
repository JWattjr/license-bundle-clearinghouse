# Submission draft — ready with caveats

**Status: READY WITH CAVEATS.** The final StudioNet release is deployed and the planned live demo completed. The repository remains private and has not been submitted to the Portal.

## Project

`LicenseBundleClearinghouse` composes permission from two to five versioned licenses for one requested use. It reserves fixed synthetic demo fees, requires each distinct licensor to approve the exact request digest, then records an expiring permission and credits each licensor.

## Live evidence

The release deployment at `0x52B06c3284CE66Bb5085790dc043AfC6B232963c` came from source commit `e9bc336c1eaff364683431a494c8f13a4528c147`. Deployment transaction `0xeaaa99ceebafef2085971b6d6e6ab6176e5107ebd19eb0c870682785c0ced1da` finalized with leader SUCCESS, and the deployed source Git blob matched the committed source.

The planned demo recorded nine finalized transactions: seven leader SUCCESS and two labeled expected rollbacks. A compatible two-license bundle issued only after both licensors consented and credited 30 and 20 synthetic units. The unconsented request had no permission; the conflicting commercial request was classified `INCOMPATIBLE`, reserved no units, and could not receive approval. Final accounting was 100 minted, 100 available, 0 reserved, 50 fees paid, conserved. All six public view methods were read back.

One earlier helper attempt on the release address submitted a separate `artwork` registration before a harness metadata error prevented the transaction hash from being saved. A later latest-final view confirms that license exists. It is explicitly recorded as an untracked, non-evidence side effect; the release demo used fresh IDs and a separate set of signers. The first deployment at `0x907c4540Bb4f59aBAA5b91c9Fd8000bb2Ba87472` remains marked failed and is not evidence.

The run used `genlayer-py==0.18.0` with the pinned runner. The direct suite passed 11 tests in ROOT `.venv` using the separate test stack. `genlayer-test==0.30.0rc2` requires `genlayer-py>=0.19.0rc2`, so those test dependencies cannot be installed together with the `.18.0` StudioNet runtime pin.

## Scope and limits

The terms and uses are synthetic participant-provided text. Demo units are internal ledger entries, not real funds, custody, tokens, or external payments. The demonstration does not establish copyright ownership, legal authority, or enforceability. Compatibility is a model judgment, not legal advice.

See [the final release manifest](deployments/studionet-release-2026-09-28-client-fix.json), [the original failed deployment record](deployments/studionet-release-2026-09-28.json), and [the client compatibility record](docs/CLIENT_COMPATIBILITY.md) for complete transaction receipts, readbacks, dependency constraints, and diagnosis.
