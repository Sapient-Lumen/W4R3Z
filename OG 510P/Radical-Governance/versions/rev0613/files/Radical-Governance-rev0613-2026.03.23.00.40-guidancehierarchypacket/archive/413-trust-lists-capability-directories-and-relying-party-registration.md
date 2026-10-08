# 413 — Trust lists, capability directories, and relying-party registration

## One-line thesis

Shared public digital ecosystems need a **public trust layer**: clear registration, machine-readable trust lists, and capability directories that show who is allowed to do what under which status.

## Why this matters

Interoperability fails not only because messages do not parse, but because participants cannot reliably answer:

- who this counterparty is,
- whether it is authorised,
- what role it is allowed to play,
- whether its status is current, suspended, or revoked,
- which public register or trust anchor makes that claim legible.

Without this layer, ecosystems drift into bilateral exception handling, spreadsheet trust, and manual whitelisting. That is not federation. It is hidden fragility.

## Design rule

When public systems depend on multiple issuers, verifiers, providers, or relying parties, the ecosystem should publish a trust and capability directory that records at minimum:

- participant identity,
- role,
- jurisdiction,
- registration status,
- certification or qualification status,
- scope of allowed use,
- revocation or suspension state,
- machine-readable access path.

## Pattern pack

### 1. Register participants before they exercise power

If an organisation will:

- request sensitive proofs,
- issue attestations,
- verify credentials,
- sign or seal public outputs,
- operate critical shared components,

then its registration should be legible before live use, not reconstructed after the fact.

### 2. Distinguish identity, role, and capability

A capable directory separates:

- who the participant is,
- what role it holds,
- what actions that role permits,
- under what conditions those permissions expire.

That prevents every trust question from collapsing into a vague binary of “known” or “unknown.”

### 3. Publish status changes as governance events

The directory should visibly record when a participant is:

- newly onboarded,
- limited in scope,
- suspended,
- revoked,
- superseded,
- restored after remediation.

Silent trust changes are dangerous when the ecosystem expects automated reliance.

### 4. Make the trust layer machine-readable

Trust directories should support automated processing with:

- signed lists,
- structured records,
- stable identifiers,
- change timestamps,
- public discovery endpoints.

Manual lookup alone does not scale for cross-border or high-volume systems.

### 5. Tie capability to minimum data rights

Where relying parties or service providers register, the directory should also express what they are allowed to request or rely on. This limits:

- over-collection,
- function creep,
- unauthorised re-use,
- ambiguous delegation.

Trust without bounded capability becomes an extraction channel.

### 6. Keep public and oversight views aligned

Some details may require restricted access, but the public view should still reveal enough to answer:

- is this participant real,
- is it authorised,
- what role does it hold,
- where can concerns be raised.

If the public cannot tell whether a relying party is legitimate, trust has been privatised.

### 7. Build revocation into the normal flow

Revocation and suspension should propagate operationally, not linger as stale registry entries. Ecosystems should test:

- status refresh,
- expiry handling,
- failure behavior,
- user-facing warnings,
- restoration after remediation.

## Guardrails

- Do not confuse a marketing roster with a trust directory.
- Registration should be proportionate, but consequential roles deserve strong onboarding and visibility.
- Capability statements should be specific enough to constrain overreach.
- Machine-readability should not erase human-readable explanations.
- The trust layer should support appeal and correction when entries are wrong.

## Failure modes

- **spreadsheet trust**: participant status is tracked informally and drifts.
- **role blur**: entities are known, but their actual permitted actions are unclear.
- **revocation lag**: a participant is suspended in policy but still trusted in practice.
- **directory theater**: a list exists, but cannot be consumed automatically.
- **overbroad reliance**: registration becomes a blank cheque to demand or verify more than allowed.

## Practical tests

A shared trust layer passes when it can answer yes to all of the following:

1. Can a participant’s legitimacy and role be checked from a public or auditable source of truth?
2. Are capability boundaries visible rather than implied?
3. Are suspension and revocation events propagated quickly enough to matter operationally?
4. Is the directory available in both human-readable and machine-readable forms?
5. Can users and oversight bodies discover whether a relying party is acting within registered scope?

## Compression rule for the archive

When a shared public ecosystem says “trust us,” ask:

**Where is the machine-readable public record of who is authorised to do what, and what happens when that status changes?**

If the answer is vague, the trust layer is still improvised.
