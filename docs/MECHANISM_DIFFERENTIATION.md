# Mechanism differentiation

## Nearest comparison

The nearest local comparison is Material Terms Change Guard, which detects changes to terms in an existing relationship. This project composes permission across several licensors for one requested use, gathers each licensor's consent to a versioned request, reserves the combined fixed fees, and issues a scoped permission record after all approvals.

## New state transition

The central transition is `registered license versions → compatible scoped bundle → combined fee reservation → consent by every unique licensor → immutable permission issuance and per-work payment`. Each approval binds to the exact request digest. A current-term update invalidates pending requests that included the old version; it leaves already issued permission snapshots unchanged.

The model only interprets term compatibility and use fit. Deterministic code owns the selected work list, version snapshot, fee sum, consent set, deadlines, refunds, and payment distribution.

## Limits

This is permission composition among registered participants. It does not prove copyright ownership, enforce a license in court, or move real assets. Model judgments can misread legal language. Local comparison does not establish ecosystem-wide originality or Portal outcomes.
