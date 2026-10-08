# Official voter-information storage-availability surface checklist

Use this checklist when an election office relies on **browser cookies, Web Storage, IndexedDB, Cache API state, or embedded cross-site cookie/state continuity** to keep a public answer/help route usable.

## Scope and dependency review

- [ ] Record which public routes depend on first-party browser persistence, embedded third-party state, or both.
- [ ] Distinguish this surface from request-context variance, login posture, constrained containers, and local-saved-vs-office-acknowledged truthfulness.
- [ ] Keep critical read-only answer/help routes explicit instead of assuming every first-contact path may depend on durable client-side state.

## Private-browsing and storage-denial review

- [ ] Review what happens when the route is opened in private/incognito browsing where local persistence may be temporary.
- [ ] Review whether storage reads and writes fail cleanly when persistence is denied or cleared.
- [ ] Do not let blocked or unavailable storage collapse the route into a blank shell, silent reset loop, or misleading remembered state.

## No-storage fallback review

- [ ] Keep a bounded no-storage / privacy-hardened first-contact lane for critical answer/help routes.
- [ ] Make default selections or recovery cues visible enough that the voter can reconstruct context after reset.
- [ ] Do not imply that locally remembered context is itself office-controlled or durable across browser modes.

## Embedded third-party state review

- [ ] Review whether any official embed depends on third-party cookies or unpartitioned state that browsers may block by default.
- [ ] Keep a credential-free fallback, explicit permission step, or first-party recovery lane when embedded shared state is unavailable.
- [ ] Do not treat an infinite spinner, empty shell, or “disable browser protections” message as an acceptable first-contact outcome for a public election-information route.

## Evidence and minimization review

- [ ] Preserve a small public digest of reviewed storage-dependent route classes, fallback classes, and last review time.
- [ ] Do not preserve individualized browser-storage dumps, full cookie jars, or invasive per-user private-browsing telemetry merely to prove the posture was reviewed.
