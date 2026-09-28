# Complete demo sequence

Run the executable direct-mode scenario:

```powershell
python -m pytest tests/test_bundle.py::test_compatible_bundle_requires_every_licensor_and_distributes_fixed_fees
```

1. Alice registers `artwork` with a 30-unit fee; Bob registers `dataset` with a 20-unit fee. Each registration stores terms version 1.
2. The requester deposits 100 synthetic demo units and requests both works for one noncommercial, attributed clinic-report use. GenLayer assesses the exact two-term bundle as compatible.
3. The contract reserves 50 units and computes a request digest that binds the use, selected version 1 terms, fees, consent deadline, and permission expiry.
4. Alice approves the digest. No permission is issued while Bob's consent is still missing. Bob approves, which issues the permission and credits 30 units to Alice and 20 to Bob.
5. Alice advances her current terms to version 2 with a new fee. The issued permission still reports the original version 1 terms and fee; version 2 only applies to future requests.

The test uses mock model output and demo units. It does not verify copyright ownership, legal enforceability, or real payment.

## Live release status

The sequence above is a direct-mode scenario with mocked model output and synthetic demo units. On 2026-09-28 the StudioNet deployment succeeded and matched the committed source, but the first `register_license` transaction finalized with a contract error before this sequence could run. No live judgment, permission, or payout is claimed; see the [release record](../deployments/studionet-release-2026-09-28.json).
