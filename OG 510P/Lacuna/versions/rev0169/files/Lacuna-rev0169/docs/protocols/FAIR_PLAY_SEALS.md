# Fair-play precommitment seals

## Purpose

Lacuna keeps hidden state plastic until consequences require commitment. That flexibility is useful, but without a counterweight it can also let a host manufacture hindsight: choose a culprit after seeing the investigation, reinterpret every clue, and then claim the answer was fixed all along.

A **fair-play seal** lets the campaign host commit to one exact hidden JSON value before later play, publish only a salted digest, and reveal the opening in a later transaction. A verifier can then check that the revealed bytes describe the value committed under that cube and seal identity.

This is deliberately narrower than “prove the mystery was fair.” It proves **continuity of one opening**. It does not prove truth, quality, uniqueness, clue sufficiency, authorship, or a real-world creation time.

## Keep three ideas separate

Lacuna has three adjacent but non-interchangeable mechanisms:

1. An assignment **commitment level** governs whether an authored candidate-world assignment may be revised inside the kernel.
2. An **anchor** records an assertion whose contradiction is no longer acceptable in current canon.
3. A **fair-play seal** cryptographically binds an external opening to an earlier digest.

A hard assignment is not cryptographic proof. A valid seal is not automatically a claim, assertion, assignment, or anchor. Revealing a payload does not silently make it world truth. The host must perform any semantic transition separately and under the ordinary epistemic rules.

That separation is essential. A seal may commit to a design decision, candidate set, clue policy, random seed, alternate ending, or continuity promise without asserting that the sealed object is already true in the world.

## Threat model

The protocol is useful against accidental drift and against a host that might otherwise rewrite one retained campaign history after the commitment was published.

It is not, by itself, sufficient against a hostile host that can:

- replace the cube and verifier together;
- show different players different forked cubes;
- create many candidate seals and reveal only the convenient one;
- falsely describe when or why a receipt was created;
- keep the only copy of the pre-reveal receipt;
- expose or destroy the secret opening outside Lacuna.

For stronger non-equivocation, a player or independent verifier must retain the initial receipt or externally anchor its `receipt_sha256` before the reveal. A public transparency log, signed witness, timestamping service, shared message, or independently archived file can provide that outside evidence. Lacuna does not bundle one.

## Commitment construction

The current scheme identifier is:

```text
lacuna.salted-sha256-json.v1
```

The digest is:

```text
SHA-256(UTF-8(canonical_json({
  "domain": "lacuna.fair-play-seal.v1",
  "scheme": "lacuna.salted-sha256-json.v1",
  "cube_id": CUBE_ID,
  "seal_id": SEAL_ID,
  "nonce": NONCE_HEX,
  "payload": PAYLOAD
})))
```

The nonce is 32 cryptographically random bytes encoded as 64 lowercase hexadecimal characters. Binding both `cube_id` and `seal_id` prevents an opening prepared for one identity from being replayed as another seal or transplanted into another cube.

### Portable JSON profile

The payload may contain:

- `null`;
- booleans;
- strings containing Unicode scalar values (unpaired UTF-16 surrogate code points are refused);
- integers in the exactly interoperable range `[-(2^53-1), 2^53-1]`;
- arrays;
- objects with string keys.

Floating-point numbers are refused. Exact decimals should be strings. Payloads are bounded by depth, item count, and canonical UTF-8 size.

Lacuna’s `canonical_json` sorts object keys, emits no insignificant whitespace, preserves Unicode code points without normalization, and emits UTF-8. This is a deliberately small project profile. **Rev0151 does not claim RFC 8785/JCS conformance.** In particular, its number and string serialization contract is the Python profile described by the executable and tests. Cross-language implementations must reproduce that exact profile or use Lacuna to prepare and verify openings.

The no-normalization rule means visually similar Unicode strings can be different openings. Unpaired surrogate code points are refused before canonicalization so malformed Python strings cannot escape the structured validation boundary. That is intentional byte custody, not linguistic equivalence.

## Lifecycle

A seal has one origin and exactly one terminal path:

```text
prepared outside cube -> sealed -> revealed
                              \-> voided
```

### 1. Prepare the secret opening outside the cube

Create a JSON payload file, for example:

```json
{
  "culprit": "Ada",
  "method": "glass key",
  "motive": "prevent the archive sale"
}
```

Prepare an opening:

```bash
./lacuna seal prepare ./stories culprit.json \
  --seal-id seal.case-culprit > seal.case-culprit.opening.json
```

This reads the cube identity, generates a fresh nonce, computes the digest, and prints a `lacuna.seal-opening.v1` document. It does **not** mutate the cube.

The opening contains the payload and nonce. Keep it secret and outside the campaign directory until reveal. Loss of the opening makes the digest practically unopenable. Disclosure of the opening discloses the payload.

### 2. Publish only the digest and metadata

```bash
./lacuna seal create ./stories seal.case-culprit.opening.json \
  --label "Authored culprit" \
  --purpose mystery \
  --visibility public > seal.case-culprit.creation.json
```

The immutable event records:

- seal ID and scheme;
- commitment digest;
- label and purpose;
- visibility and audience;
- optional provenance source ID.

It does not record the nonce or payload. The creation response includes a receipt. Retain that receipt separately or at least retain/anchor its `receipt_sha256`.

A restricted seal requires one or more audience agents:

```bash
./lacuna seal create ./stories opening.json \
  --visibility restricted --audience player
```

Perspective views receive only seals visible to that agent. They never receive the privileged provenance source linkage.

### 3. Inspect or export the receipt

```bash
./lacuna seal list ./stories
./lacuna seal receipt ./stories seal.case-culprit > seal.case-culprit.receipt.json
```

The receipt contains two deliberately different views:

- `receipt_core`: immutable origin metadata suitable for external anchoring;
- `seal`: current lifecycle state for convenience.

`receipt_sha256` is the SHA-256 digest of canonical `receipt_core`. It remains stable when the seal is later revealed or voided. `current_head`, `seal.status`, and terminal details may change; they are not part of the anchored core.

The origin event envelope includes the event hash, previous hash, sequence, recorded time, and the change-set head after commitment. The recorded time is local ledger metadata, not a trusted external timestamp.

### 4. Verify without mutating

```bash
./lacuna seal verify ./stories seal.case-culprit.opening.json
```

Verification checks:

- opening schema and exact field set;
- cube identity;
- seal identity;
- scheme;
- opening self-consistency;
- match against the recorded commitment digest;
- after reveal, equality with the recorded opening.

It exits successfully only on a passing verification report.

### 5. Reveal in a later transaction

```bash
./lacuna seal reveal ./stories seal.case-culprit.opening.json \
  --reason "The players reached the authored resolution."
```

A reveal must match the recorded digest. It stores the payload, nonce, reason, and reveal sequence in an immutable event-backed projection.

The seal must already have a committed origin change-set. Creating and revealing it in the same atomic change-set is refused. This phase boundary prevents a vacuous “commitment” assembled only at reveal time. It does not require a minimum number of scenes or elapsed seconds; a host can still reveal in the next transaction, so the retained receipt and campaign protocol remain important.

### 6. Void without revealing

```bash
./lacuna seal void ./stories seal.case-culprit \
  --reason "The campaign ended before this branch was played."
```

Void is terminal and keeps the opening secret. A void receipt proves only that the recorded seal was explicitly retired, not what it contained.

## Host-only custody boundary

The three lifecycle operations are intentionally absent from ordinary `lacuna.turn-proposal.v2` write grants:

- `seal_precommitment`;
- `reveal_precommitment`;
- `void_precommitment`.

A director model may see a seal that its context authorizes, reason about its status, and narrate around it. It may not become the secret custodian or operate the seal lifecycle through the ordinary model turn entrance.

The host or a dedicated administrative process must prepare, create, reveal, or void seals through the CLI or direct Python API. This protects against a prompt-injected player asking the narrator to reveal an opening and against an overhelpful model committing a convenient answer during the same turn it invents it.

This is least authority, not a claim that the host itself is trustworthy.

## Event and projection guarantees

The verifier checks that:

- every seal projection originates from an exact `precommitment.sealed` event;
- metadata, digest, visibility, audience, and sequence match the event payload;
- reveal and void states are mutually exclusive and complete;
- the terminal event occurs in a different change-set from the origin;
- a reveal recomputes to the original digest;
- the projected opening matches its immutable reveal event;
- every seal event has a corresponding projection;
- deterministic rebuild reproduces the projection from events.

Projection tampering is therefore detectable under the normal Lacuna threat model, and `lacuna rebuild` can restore a valid projection without changing the event-ledger head.

## What to seal

Good seal payloads are small, explicit, and independently interpretable. Examples:

```json
{"culprit_id":"character.ada"}
```

```json
{
  "culprit_id":"character.ada",
  "method_claim_id":"clm_...",
  "motive_claim_id":"clm_...",
  "solution_version":1
}
```

```json
{
  "allowed_resolutions":["ending.mercy","ending.exile"],
  "selection_seed":"2026-campaign-seed-17"
}
```

Use stable IDs where the surrounding campaign already defines them. Include a version field when future tooling may interpret the payload structurally. Do not place the entire private campaign database into one opening merely because the size limit permits it.

## What not to infer

A passing seal verification does not establish:

- that the culprit was logically deducible;
- that clues were shown before the reveal;
- that no clue was rewritten;
- that the sealed answer is coherent with the event ledger;
- that the host did not prepare many alternatives;
- that the host authored the answer;
- that the `recorded_at` value is externally accurate;
- that the player possessed the receipt at the claimed time;
- that the answer is aesthetically satisfying;
- that the payload became canon.

Those require other records, tests, witnesses, or design rules. A future fair-play layer could seal a clue graph, candidate set, generation policy, random seed, or Merkle root over multiple independently revealable statements. Rev0151 intentionally implements the smallest auditable primitive first.

## Design consequence for adaptive fiction

Gwern-style retcon planning asks the engine to delay commitments so the story can adapt. Fair-play seals add the complementary rule:

> Keep interpretation plastic, but let the author prove that selected hidden facts were not chosen after observing the player.

The useful system is neither a rigid simulation nor unlimited retrospective explanation. It is a ledger in which some unknowns remain probabilistic, some meanings remain revisable, some physical facts become anchored through consequence, and selected mystery premises can be externally precommitted without exposing them.
