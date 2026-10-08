# Court admissibility worksheet (bundle-local, jurisdiction-bound)

**Track:** Shared (cross-cutting)


> Goal: make an `EvidenceBundleManifest` usable in a real proceeding without requiring the reader to be a cryptographer.
> Keep this to **1–2 pages**. Attach as `notes/admissibility.md` in the bundle.

## 1) Case + jurisdiction
- **Jurisdiction / venue:**
- **Proceeding type:** (certification challenge / recount dispute / injunction / administrative hearing / other)
- **Filing party / proponent:**
- **Opposing party:**
- **Date of preparation:**

## 2) What claim this bundle supports (bounded)
- **Claim ID / short name:**
- **Claim card included:** (yes/no) — reference: `claim.md` digest from `manifest.json`

## 3) Authentication (why the court should believe these bytes)
- **Bundle digest:** (sha256 / other)  
- **Manifest signature:** (key id / signer / how key is controlled)
- **Publication method (if public):** (PublicNotice id + digest / mirror urls / other)
- **Custodian declaration:** who can swear to how this bundle was assembled?

## 4) Chain of custody (bytes)
List each hop:
- **Source → capture:** (who, when, tools, controls)
- **Capture → packaging:** (who, when, controls)
- **Packaging → filing:** (who, when, controls)

## 5) Tool provenance (verifier)
- **Verifier name + version:**
- **Verifier binary hash:**
- **Build identity / reproducibility note:** (reproducible build? independent rebuild? where to obtain identical build)
- **Policy profile digest (if used):**
- **Test vectors referenced:** (if any)

## 5a) Crypto primer + expert lane (if needed)
- **Crypto primer attached (1 page):** (yes/no)  
  If yes, where: (bundle path / exhibit label)
- **Expert declaration required by this venue:** (yes/no/unknown)  
  If yes, expert name + qualifications + what they attest (bounded).


## 6) Explainability (what was checked)
In plain language (3–8 bullets):
- What objects were verified?
- What signatures/hashes were checked?
- What would cause verification to fail?
- What the verification result does *not* prove (explicit boundary).

## 7) Exhibits map (human ↔ machine)
For each human-readable exhibit, map it to a digest:
- Exhibit name → `manifest.json` object path → digest

## 8) Open questions / disputes (if any)
- What is contested or uncertain?
- What further evidence would resolve it?
