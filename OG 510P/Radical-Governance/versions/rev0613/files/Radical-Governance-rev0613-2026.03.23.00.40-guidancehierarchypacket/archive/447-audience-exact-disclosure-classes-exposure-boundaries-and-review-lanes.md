# 447 — Audience-exact disclosure classes, exposure boundaries, and review lanes

## One-line thesis

Governance artifacts for consequential public AI should carry exact audience and exposure labels so public, affected-person, operator, reviewer, regulator, supplier, and privileged-admin lanes cannot be silently mixed or widened.

## Why this matters

Public AI governance increasingly depends on many compact artifacts: registry entries, public system cards, operator runbooks, appeal packets, peer-review materials, supplier disclosures, regulator submissions, audit logs, and privileged-access records. The problem is not only whether each artifact exists. The deeper problem is whether the archive can still tell **who each artifact is actually for** and **how far it is allowed to travel**.

Without explicit audience and exposure boundaries, systems drift into contradiction. A record describes itself as internal review material but is copied into a public-facing surface. A public transparency page borrows privileged or case-specific language that should never have been exposed. A support packet intended only for an affected person is widened into a generic operator export. A supplier-facing evidence bundle silently becomes the only documentation the public ever gets. The archive should reject this blur. Governance evidence should be typed by audience with the same discipline used for jurisdiction, scope, and privileged access.

## Pattern pack

### 1. Give every governance artifact an explicit audience class

For each consequential artifact, record an intended audience class such as:

- **public**,
- **affected person / case-bound recipient**,
- **frontline operator**,
- **internal reviewer or auditor**,
- **regulator, court, or ombuds**,
- **supplier or external assessor**,
- **privileged administrator or incident responder**.

The point is not to create endless taxonomy. The point is to stop pretending that every governance artifact is either simply “public” or simply “internal.”

### 2. Pair audience with an exposure boundary

Audience labels should be matched by an exposure boundary such as:

- openly published,
- case-bound release,
- role-restricted internal access,
- legally controlled disclosure,
- supplier-limited exchange,
- or privileged-log access only.

A record should not be able to describe itself as narrowly targeted while still carrying a broad exposure posture that contradicts the lane.

### 3. Keep lane-specific fields exact to their lane

Fields that imply one audience boundary should not appear casually in another. For example:

- a case-recipient delivery note should not drift into a general public page,
- a regulator-only confidentiality field should not appear in a public card,
- a privileged-investigation note should not become routine operator guidance,
- and supplier-specific remediation language should not substitute for the institution’s own public explanation.

Typed fields should stay evidence-bearing, not degrade into generic comment slots.

### 4. Use paired artifacts when the same subject needs both public and restricted versions

Sometimes the right answer is not one universal record but a linked set such as:

- a public system card plus a reviewer dossier,
- a public notice plus a case-specific appeal packet,
- a public incident entry plus a restricted forensic log,
- or a public supplier register plus a contract- or security-restricted annex.

When paired artifacts exist, they should point to each other clearly while keeping the audience boundary explicit.

### 5. Make audience widening a governed change, not a casual export

If an artifact is moved from one lane to a broader one — for example from operator-only to public summary, or from case-bound packet to wider oversight bundle — that widening should be treated as a governed change with:

- a named owner,
- a lawful basis or policy reason,
- a redaction or minimization review where needed,
- and an updated label showing the new audience and scope.

Silent widening is itself a governance event.

### 6. Default sensitive logs and packets to the narrowest workable audience

Case packets, audit logs, privileged-session records, and investigation artifacts should default to the narrowest lane that still supports review, remedy, and lawful oversight. Broad visibility should be justified, not assumed.

This matters because consequential public AI often generates mixed evidence that combines public-interest accountability with personal, operational, or security-sensitive detail.

### 7. Show the current lane at the interface and export point

The audience boundary should not live only in metadata. Interfaces and exports should visibly indicate what lane a user is in, what class of artifact they are viewing or generating, and whether the output is:

- safe for public publication,
- restricted to the case recipient,
- internal review material,
- or privileged/investigative evidence.

That reduces accidental lane crossing at exactly the moments when copying, forwarding, or publication become easiest.

## Guardrails

- Do not collapse all governance artifacts into a vague “internal” bucket.
- Keep audience labels paired with exposure boundaries, not audience claims alone.
- Do not let lane-specific fields become generic explanatory prose in other lanes.
- Treat audience widening as a governed change requiring justification and review.
- Default mixed-sensitivity logs and packets to the narrowest workable lane.

## Failure modes

- **lane contradiction**: an artifact claims a narrow audience but is exposed far more broadly.
- **public-by-copy**: internal or case-bound material becomes public through informal reuse rather than explicit review.
- **typed-field laundering**: evidence-bearing audience fields degrade into generic notes and lose their boundary meaning.
- **single-record fantasy**: one artifact is forced to serve public, operator, reviewer, and supplier audiences badly at once.
- **invisible widening**: a broader disclosure happens without ownership, basis, or updated labeling.

## Practical tests

An audience-exact regime passes when it can answer yes to all of the following:

1. Does every consequential governance artifact have an explicit audience class?
2. Is each audience class matched to a coherent exposure boundary?
3. Are lane-specific fields prevented from drifting into contradictory lanes?
4. When the same subject needs multiple surfaces, are public and restricted artifacts linked without being collapsed together?
5. Would any widening of audience or exposure trigger named review, lawful basis, and updated labels?

## Compression rule for the archive

When a governance artifact cannot say **who it is for and how far it may travel**, the archive is still running on **blurred disclosure lanes**.
