# Fetched-SPDX demo sequence

1. Alice and Bob register different photographs with the public, tag-pinned [CC-BY-4.0 URL](https://raw.githubusercontent.com/spdx/license-list-data/v3.25.0/text/CC-BY-4.0.txt) and fixed fees of 30 and 20 units. Alice also registers a [CC-BY-NC-4.0 photograph](https://raw.githubusercontent.com/spdx/license-list-data/v3.25.0/text/CC-BY-NC-4.0.txt). No participant-typed licence text is accepted.
2. A requester deposits 300 synthetic units and requests both BY works for a paid advertising campaign with attribution, licence links, modification notices and no extra restrictions.
3. Validators independently fetch the complete bodies and compare availability, byte lengths, SHA-256 digests and judgments. A compatible request reserves 50 units and binds this evidence into the consent digest.
4. Alice's approval leaves the request awaiting Bob. Bob's approval issues the expiring permission and credits 30/20 units.
5. Commercial use of the NC work is NOT_PERMITTED and does not reserve funds or issue permission. Another BY request with only Alice's consent does not issue permission; cancellation refunds it.
6. A new BY request is assessed at version 1. Alice updates its work URL to the NC URL, producing version 2. Approval of the old request rolls back as stale; invalidation refunds it. The earlier issued permission retains BY version 1 and its evidence digest.

Every step was read back at latest-final state. Final requester budget: `300 = 250 + 0 + 50`. See [manifest](../deployments/studionet-release-2026-10-12-spdx.json). Tests use mocks; live receipts are separate evidence. Units are synthetic; no legal advice.
