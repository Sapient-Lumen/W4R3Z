# ADR-0341: Removable-media local fallback post-detach credential envelope stays launcher-fixed and non-elevating

- Status: accepted
- Date: 2026-05-18
- Deciders: archive maintainers
- Consulted: `docs/49-capsicum-casper-hardening.md`, `docs/181-workload-identity-and-secretless-deploys.md`, `docs/235-process-contracts-and-service-ownership.md`, `docs/294-oblivious-sandboxing-launchers.md`, `docs/746-removable-media-local-fallback-post-detach-later-tool-code-enters-capability-mode-before-mainline-and-stays-there.md`, `docs/751-removable-media-local-fallback-post-detach-runtime-dependency-closure-stays-launcher-pinned-and-loader-path-free.md`, `spec/preopen.map.schema.json`

## Context

ADR-0337 through ADR-0340 made the post-detach removable-media later worker closed-world at the descriptor, launch-context, executable, and runtime-dependency layers. That still leaves one kernel authority seam: the worker's credential envelope.

A process that inherits root, broad supplementary groups, saved-id regain, login-class privilege, or setuid/setgid execution affordances can turn a narrow descriptor set into a wider host effect. Capability mode removes path lookup authority, but it is not a substitute for making the worker's effective credential envelope explicit, unprivileged, and non-elevating before tool mainline code runs.

The first removable-media local fallback therefore needs a receipt-visible worker credential envelope, not just a receipt-visible executable and runtime closure.

## Decision

For the first host-local removable-media fallback lane, post-detach later workers now use `launcher-fixed-unprivileged-credential-envelope-no-supplementary-groups` and `no-setuid-setgid-saved-id-or-ambient-privilege-regain`.

1. **The worker credential envelope is launcher-fixed before handoff.**
   - The launcher selects the worker user/group from reviewed policy before spawning or dropping into the later worker.
   - The canonical first-lane example uses `derive-rm-worker:derive-rm-worker` as the reviewed worker principal/group labels.
   - The worker does not inherit the launcher's root, operator, login-session, or device-domain credential identity.

2. **Supplementary groups stay empty in the first lane.**
   - The later worker records `no-supplementary-groups`.
   - Parent login/session groups, device administration groups, storage/operator groups, and wheel-like groups do not cross into the post-detach worker.
   - If a future compatibility lane needs a richer group vector, it must declare that vector and receipt it as authority.

3. **Privilege regain is unavailable.**
   - The later worker records `no-setuid-setgid-saved-id-or-ambient-privilege-regain`.
   - Setuid/setgid binaries, saved-ID regain, privilege-preserving exec tricks, ambient caps, login-class privilege, and similar host affordances stay out of the first lane.
   - The executable and runtime closure are already pinned; this decision says the credential context in which they run is pinned too.

4. **Receipts expose the credential envelope rather than trusting launcher folklore.**
   - Plans and receipts carry `post_detach_credential_posture`, worker user/group labels, `post_detach_supplementary_groups_posture`, and `post_detach_privilege_regain_posture`.
   - The attach grant carries `post_detach_credential_receipt_posture = receipt-records-worker-credential-envelope` and `post_detach_credential_envelope_required = true`.
   - The preopen map carries the same posture as launcher-owned execution metadata.

## Consequences

- A later worker cannot accidentally keep root, wheel/operator groups, or saved-ID regain while the archive claims a narrow first lane.
- Support can answer which principal/group envelope processed the preserved subject from the receipt stack.
- Static tools, store-managed dynamic closures, and launcher-owned wrappers remain practical; they simply run under the reviewed unprivileged worker identity.
- Tools that require privileged helper work remain possible only through a later explicit broker/helper contract that declares and receipts that privileged authority outside the first lane.

## Alternatives considered

- **Rely on capability mode alone.** Rejected because credential-derived authority and privilege-regain paths are a separate execution fact from path namespace confinement.
- **Let the disposable jail's default user stand in for the contract.** Rejected because receipts should not depend on implementation-local launch folklore.
- **Permit inherited supplementary groups because the descriptor set is closed.** Rejected for the first lane because group membership affects kernel authorization, filesystem/object checks, helper behavior, and future extension seams.
- **Require a numeric UID/GID in the portable contract.** Rejected for now; the first lane records reviewed principal/group labels while leaving host-local numeric realization to the launcher receipt/broker implementation.

## Follow-up

- Update the canonical removable-media local-ingest examples so they record the post-detach credential envelope.
- Add a drift check that fails if the first lane slides back to root/wheel/operator inheritance, supplementary groups, setuid/setgid or saved-ID regain, or unrecorded credential identity.

## Links

- boundary doc: `docs/752-removable-media-local-fallback-post-detach-credential-envelope-stays-launcher-fixed-and-non-elevating.md`
- previous cut: `adrs/ADR-0340-removable-media-local-fallback-post-detach-runtime-dependency-closure-stays-launcher-pinned-and-loader-path-free.md`
