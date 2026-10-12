# Security notes

Only registered licensors may update a work's URL/fee. Every update increments the version; history is bounded and immutable. Pending approvals check current versions and the exact request digest. All distinct licensors must consent before issuance; the model cannot set fees, choose participants, override consent or spend funds.

Every selected licence URL is fetched in the leader and independently in each validator. Complete strict UTF-8 bodies must be HTTP 200, nonempty and at most 20,000 raw bytes. Evidence metadata and all normalized findings/conflicts are exactly compared. Fetch failures are recorded UNAVAILABLE, causing a fail-closed DENIED_UNVERIFIABLE request without reservation. Model errors/malformed results disagree. Text is untrusted data, including purported instructions to validators.

URL validation rejects literal IPs, private/local/special-use DNS suffixes, credentials, whitespace/control characters, backslashes, fragments and non-443 ports. It is structural validation; no claim of DNS rebinding prevention or redirect destination enforcement is made. Tag-pinned SPDX sources and stored raw-body digests support reproducible evidence; the digest binds bytes at assessment time, not perpetual URL content.

Compatible requests reserve exact fixed fees only after sufficient funding. Only final consent pays once. Rejection, cancellation, expiry and stale invalidation refund the whole reservation. The general ledger conserves all spendable balances plus reservations against minted units; cumulative payments are not a separate removed balance.

Bounds: 32 works, 32 requests, 64 accounts, eight versions per work, two to three works per request, 20,000 raw bytes per licence and 180 days maximum expiry.

Synthetic payment units; no legal advice. This does not prove copyright ownership, legal enforceability, real-money payment, arbitrary payment recycling, ecosystem-wide originality, perpetual URL immutability, or DNS/redirect destination enforcement. URL validation is structural public-HTTPS validation; it rejects literal IPs, private/local hostnames, credentials, ambiguous authority and non-443 ports.

Lint/direct tests and the requested StudioNet demo passed; live unavailable-evidence and forged-leader attacks remain untested. See [test matrix](TEST_MATRIX.md) and [manifest](../deployments/studionet-release-2026-10-12-spdx.json).
