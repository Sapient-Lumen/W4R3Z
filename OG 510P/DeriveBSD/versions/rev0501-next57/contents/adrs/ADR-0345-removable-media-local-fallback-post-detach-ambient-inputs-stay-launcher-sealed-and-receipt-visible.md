# ADR-0345: Removable-media local fallback post-detach ambient inputs stay launcher-sealed and receipt-visible

- Status: accepted
- Date: 2026-05-18
- Deciders: archive maintainers
- Consulted: `docs/227-time-discipline-and-trustworthy-timestamps-as-evidence.md`, `docs/294-oblivious-sandboxing-launchers.md`, `docs/755-removable-media-local-fallback-post-detach-peer-interaction-stays-launcher-isolated-and-ambient-ipc-free.md`, `spec/preopen.map.schema.json`

## Context

ADR-0337 through ADR-0344 made the post-detach removable-media later worker closed-world across descriptors, launch context, executable identity, runtime dependency closure, credentials, lifecycle, resources, and peer interaction. A remaining host-local seam is ambient observation and nondeterminism: a worker can still read wall-clock time, timezone state, host entropy, random devices, hostname, kernel/sysctl facts, locale catalogs, or machine identity and let those observations influence derivative bytes without them appearing in the receipt.

For the first removable-media local fallback, post-detach later work is supposed to be a one-shot computation over one preserved subject and one declared derivative sink. Ambient host inputs would make replay and review weaker even if peer control, resources, and descriptors were correct.

## Decision

For the first host-local removable-media fallback lane, post-detach later workers now use `launcher-sealed-ambient-input-envelope-no-worker-clock-random-or-host-identity`, `receipt-records-ambient-input-envelope-and-launcher-owned-timestamps`, `worker-wall-clock-and-timezone-not-derivative-authority`, `no-worker-randomness-or-host-entropy-as-derivative-input`, and `hostname-kernel-sysctl-locale-and-machine-identity-not-derivative-authority`.

1. **The launcher owns the ambient-input envelope.**
   - The worker is launched so ordinary derivative bytes depend on the preserved subject, reviewed argv/environment/cwd, pinned executable/runtime closure, and reviewed descriptors rather than host-observation defaults.
   - Backend details may include syscall filtering, deterministic shims, sealed virtual files, empty locale/timezone views, deterministic seeds, or equivalent mechanisms. The portable contract is the receipt-visible ambient-input posture.

2. **Time is receipt evidence, not worker input authority.**
   - The worker records `worker-wall-clock-and-timezone-not-derivative-authority`.
   - Launcher timestamps, timeout observations, and receipt creation times remain launcher/broker evidence.
   - Worker-read wall-clock, local timezone, calendar locale, or clock drift do not shape ordinary derivative bytes in the first lane.

3. **Randomness and host entropy stay out.**
   - The worker records `no-worker-randomness-or-host-entropy-as-derivative-input`.
   - Random devices, host entropy, per-run seeds, randomized output ordering, and temporary-name nondeterminism are absent unless a future wrapper/broker contract admits and receipts them.

4. **Host identity is not derivative input authority.**
   - The worker records `hostname-kernel-sysctl-locale-and-machine-identity-not-derivative-authority`.
   - Hostname, domain name, kernel release, sysctl inventory, machine-id state, locale catalogs, timezone files, CPU model, or host package metadata are not ordinary derivative inputs.

## Consequences

- The first lane no longer assumes that a pinned runtime closure is enough for replayable derivative evidence.
- Receipts can distinguish deterministic launcher-sealed execution from a run that depended on wall-clock, randomness, host identity, sysctl, locale, or timezone behavior.
- Compatibility tools that need timestamps, random seeds, host feature detection, or locale-aware formatting need a future explicit contract rather than hidden ambient inputs.
- The post-detach worker remains boring: one preserved subject, one declared derivative sink, one launcher-owned evidence path, no unrecorded host-observation authority.

## Alternatives considered

- **Treat clock/random/host identity as harmless metadata.** Rejected because metadata can change derivative bytes, leak host state, or make replay non-deterministic.
- **Rely on an empty environment.** Rejected because clock, random, uname/sysctl, locale, and timezone inputs can be reached without inherited environment variables.
- **Require every tool to be perfectly deterministic internally.** Rejected as too vague; the archive needs a receipt-visible launcher contract for admitted ambient inputs.
- **Permit time and randomness in the ordinary lane.** Rejected because support/compatibility lanes can be explicit later, while the first lane should stay reviewably boring.

## Follow-up

- Update the canonical removable-media local-ingest examples so they record ambient-input, clock, randomness, and host-identity posture.
- Add a drift check that fails if the first lane slides back to worker wall-clock/timezone authority, host entropy/randomness, hostname/kernel/sysctl/locale/machine identity, or receipt-invisible ambient inputs.

## Links

- boundary doc: `docs/756-removable-media-local-fallback-post-detach-ambient-inputs-stay-launcher-sealed-and-receipt-visible.md`
- previous cut: `adrs/ADR-0344-removable-media-local-fallback-post-detach-peer-interaction-stays-launcher-isolated-and-ambient-ipc-free.md`
