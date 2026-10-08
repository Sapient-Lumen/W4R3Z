# Refutation packet checklist (TTR) — Minimal publishable shape

**Track:** A (Deployable core)

Use this when a high-impact false claim is circulating. The goal is *verification*, not persuasion.
Prefer **pointers + digests** over long prose. See `docs/240`.

## 1) Signed public object exists (TTR‑1)
- [ ] A new **PublicNotice** exists (signed; digest-first; includes epistemic tags + `next_update_at` when uncertain) (`docs/186`, `docs/218–219`)
- [ ] Notice links to prior notice(s) / correction chain (`docs/220`)
- [ ] Notice is discoverable via `.well-known` / directory / feed pointers (`docs/200–205`)
- [ ] Mirrors have the same digest (spot-check at least 2 independent paths)

## 2) Offline-verifiable packet exists (TTR‑2)
- [ ] Evidence packet manifest exists and is signed (`observer-kit/`, `docs/92`, `docs/177`)
- [ ] Packet includes the PublicNotice object(s) and any referenced payloads
- [ ] Packet includes required anti-suppression attachments:
  - [ ] `gossip_summary`
  - [ ] `transparency_receipt`
- [ ] Packet is mirrorable as bytes (static URLs / directory listing; not app-only)

## 3) Independent verification surfaces
- [ ] At least one independent party publishes a PacketVerificationReport (or equivalent replayable verifier output) (`docs/188`)
- [ ] If institutional trust is contested: a witness cosigns or publishes a dissent item that cites the notice digest (`docs/135`)


## 3b) Distribution path (so verification reaches the public)
- [ ] Status/rumor-control surface links to the verdict notice digest and packet digest (`195`).
- [ ] Status update links to at least one independent PacketVerificationReport digest (`193`).
- [ ] Status surface links to the current verifier capacity roster digest (`241`) so the audience can find more verifier outputs.
- [ ] A low-bandwidth digest card exists for high‑reach channels and points back to the status surface (`206`).

## 4) Keep the refutation honest
- [ ] If unknown: say “unknown” and commit to a next update time (don’t fill the vacuum with guesses)
- [ ] If key compromise is possible: publish the key-compromise boundary object and point to the new keyset (`docs/239`)
