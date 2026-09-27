# Submission draft — not deployed or submitted

**Status: local draft only. This contract is undeployed and has not been submitted to the GenLayer Portal.**

## Project

`LicenseBundleClearinghouse` composes use permission from two to five registered, versioned license terms for one precisely scoped request. Selected licensors approve the same request digest, which includes their license versions, fixed fees, requested use, and permission expiry.

## Distinguishing mechanism

GenLayer evaluates compatibility across the requested use and terms bundle. A compatible bundle reserves the sum of fixed per-work fees; permission issues and payment credits occur only after every distinct licensor consents. A term update stales pending requests and does not mutate already issued permission snapshots.

## Local verification recorded

- GenVM lint: passed 3 checks.
- Contract validation: 15 methods (6 views, 9 writes).
- ABI schema extraction: succeeded to `contracts/abi.json`.
- Direct-mode tests: 10 passed, covering bundle conflicts and restrictions, exact licensor consent, fee distribution, rejection/cancel/expiry refunds, version invalidation, malformed/disagreeing output, and bounds.
- Deployment, live consensus receipts, Portal review, and real payment or ownership verification: not performed.

## Limitations

Registration does not prove copyright ownership, and model compatibility is not legal advice. Demo units are internal ledger entries. The pinned runner's availability on a target chain remains unverified. This draft makes no ecosystem originality or Portal-score claim.
