# Resilio typed bootstrap artifact overloading and intake-route ambiguity evaluation

## Why this pass exists

The archive already has strong doctrine for manual claim, browser handoff, identity join, encrypted custody, and existing-bytes review.
What still remained under-explained was the earlier seam:

> before any of those deeper flows even begin, how clearly does the product tell the operator what kind of authority-bearing artifact they just received?

Current official Resilio docs still show a genuinely useful product.
They also still show that materially different powers can arrive through very similar `copy key`, `enter a key`, `enter key or link`, browser-open, and manual-intake rituals.

That is a good reason to adapt rather than clone.

## What current Resilio still gets right

### 1) It offers several practical intake lanes

Current official docs still support:

- one-identity linking by `M-key`
- ordinary subject claim by link/key/QR
- encrypted-custody creation by encrypted key and manual connection
- browser-open convenience when a link can hand off to the local app
- manual fallback when direct handoff is unavailable

That flexibility is useful.

### 2) It still distinguishes several real authority families

Current docs still make clear that these are not all the same thing:

- an **identity-link artifact** can join a seat into one linked-device family so all folders become available across that cohort
- a **subject-claim artifact** can connect one shared folder with permissions and optional approval behavior
- an **encrypted-custody artifact** can create a ciphertext-only node with stricter posture and capability ceilings

Those are real semantic differences, not naming trivia.

### 3) It still candidly admits some surface mismatch

Current docs still say link-click/browser-open flows can be convenient, but also still say WebUI cannot consume clicked links directly and instead needs manual `Enter a key or link`.
That candor is helpful.

## Where the current page shape still fails

### 1) Similar intake surfaces still front very different powers

Current docs still describe:

- `Enter a key` for identity linking
- `Enter key or link` for ordinary shared-folder claim
- `Manual connection` with encrypted key for ciphertext custody
- browser landing pages that may simply open the app and then continue elsewhere

A careful user can learn the difference.
But the product still asks the operator to infer too much from article memory and surrounding flow.

### 2) Carrier clothing and artifact family still sit too close together

A QR code, pasted text, browser wrapper, or copied string may be only delivery clothing.
The real question is whether the underlying object is:

- identity-link authority
- subject-claim authority
- encrypted-custody authority
- malformed or unsupported material

Current docs still leave too much of that determination to article context instead of one typed product-owned intake verdict.

### 3) The consequence of a mistaken route is not small

If the operator treats the artifact as the wrong family, the consequences are not cosmetic:

- identity join can replace a local certificate world and import another one
- ordinary subject claim can create one subject bind with approval and permission consequences
- encrypted-custody setup can deliberately create a ciphertext-only seat with no ordinary plaintext capability

That means the earlier type/route verdict deserves stronger product ownership than a generic text-entry box.

### 4) Downstream truth is often only learned after route selection

Current docs still spread route consequences across later pages:

- identity-join takeover and whole-family availability live in linked-device docs
- ordinary folder claim and approval consequences live in sharing docs
- encrypted-custody posture, strict target rules, and recovery burden live in encrypted-folder docs
- browser and surface mismatch live in link-structure and WebUI docs

So the ordinary operator still has to answer two questions in the wrong order:

1. **what artifact family is this really?**
2. **what happens if I continue on this route?**

A better product answers both before any live join/claim/custody commit.

## What AnonSync should do instead

AnonSync should preserve the flexibility and replace the route ambiguity with four ordinary product-owned pages:

1. **Artifact family router**
   - classify the imported material before commitment
   - separate carrier from authority family
   - show parse confidence and admissible routes

2. **Typed artifact card**
   - show scope, world, ceiling, and target consequences
   - explain what the artifact can and cannot do

3. **Intake route review**
   - compare join vs claim vs encrypted-custody consequences
   - allow safe route switch with explicit semantic change

4. **Typed intake receipt**
   - preserve what was parsed, which route was taken, and which deeper review page followed
   - support handoff, rereview, and support without exporting secrets

## Sharper non-clone line

So the tighter conclusion for this pass is:

> Resilio is worth borrowing for the breadth of its bootstrap lanes. It is not worth cloning the way materially different authority families still arrive through similar manual/key/link surfaces, while the operator often has to remember from help articles whether this string joins an identity family, claims one subject, or creates ciphertext-only custody.

## New replacement pages added in this revision

- `497` Artifact family router
- `498` Typed artifact card
- `499` Intake route review
- `500` Typed intake receipt
