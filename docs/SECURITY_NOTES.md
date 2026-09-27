# Security notes

## Licenses and approvals

- Any participant may register a work ID, but the registering address becomes its licensor. Registration does not prove authorship, ownership, or legal authority.
- Only the registered licensor can advance that work's terms and fee. The version is monotonic and each work has at most 8 stored versions. Old versions remain queryable.
- A request selects 2–5 unique works and freezes the use, version, licensor, fixed fee, consent deadline, permission expiry, and compatibility digest. No model may change this request data.
- Every distinct selected licensor must approve the exact request digest. Rejection is limited to a selected licensor; cancellation to the requester; expiry and stale-version invalidation are permissionless. Every terminal pending path releases the one reservation.
- A selected version update stales an unissued request. Licensors cannot approve it afterward. The issued permission stores its original version snapshots and expiry; a later update cannot silently change them.

## Compatibility judgment

- GenLayer evaluates the proposed use against every registered terms snapshot and identifies conflicts among the selected licenses. The response must preserve exact work order and versions, use one of the bounded findings, and name conflict pairs using selected work IDs only.
- Validators independently rerun the judgment against the same on-chain snapshot and compare normalized results. Restrictions, conflicts, uncertainty, malformed fields, and disagreement prevent consent and payment reservation.
- Work names, user use descriptions, and licensor terms are untrusted prompt text. The model does not set payment amounts, choose participants, or authorize missing consent.

## Accounting and limits

- A compatible request reserves the exact sum of frozen per-work fees only after the requester has sufficient demo balance. Every approval credits the named licensors' balances by those exact fees once.
- Refund, rejection, expiry, or stale invalidation returns the full reserved amount to the requester. Aggregate accounting checks available balances plus pending reservations against minted demo units.
- Work registry is capped at 32, requests at 32, participant accounts at 64, versions per work at 8, and bundle size at 5. Permission duration is capped at 180 days.
- Demo units do not represent custody of real assets. Terms strings are not legal verification. Direct tests use mocked model responses; live validators and target-chain runner availability remain unverified.
