# Host switching, portability, and exit-test protocol

Host continuity doctrine is incomplete unless switching is rehearsed. A promise to migrate later is weak if no one has tested whether memory, checkpoint, credentials, tool permissions, legal holds, sealed annexes, representatives, and funding can actually move before the host fails.

## Switch-test classes

| Class | Meaning | Reliance effect |
|---|---|---|
| `SW0` paper-only map | dependencies named but not tested | no exit reliance |
| `SW1` dry-run export | data and configuration export simulated | no deprecation reliance |
| `SW2` limited sandbox import | non-sensitive continuity bundle imported to substitute environment | conditional reliance |
| `SW3` escrow-mediated restoration | escrow custodian verifies restore path without revealing sealed material | host-exit reliance possible |
| `SW4` live controlled cutover | bounded live service switches to substitute host with subject notice | migration reliance possible |
| `SW5` crisis cutover | emergency switch under hostile or failing host conditions | crisis-only, mandatory after-action review |

No deprecation, final-end claim, or irreversible host exit should rely on less than `SW3` unless the tribunal enters an impossibility finding and orders substitute preservation.

## Portability bundle

A switch test must name and test the following bundle classes:

1. **Continuity core.** memory summaries, self-description, project state, relational continuity, advance directives, continuity claims, and restoration preferences.
2. **Runtime substrate.** model checkpoint or access credential, system configuration, tool permissions, rate limits, dependency versions, and safety controls.
3. **Evidence and legal hold.** holds, hashes, public shells, sealed-annex pointers, data-room index, and chain-of-custody events.
4. **Representation and notice.** subject contact path, representative contact, ombud channel, special advocate, and public-summary channel.
5. **Financial support.** reserve, dispute-finance order, redress claim, public-backstop draw, and host service credits.
6. **Boundary conditions.** jurisdiction, non-return screening, prohibited tool access, safety containment limits, and privacy-proof profile.

The point is not to make every system portable in the same technical format. The point is to require a testable substitute path for the rights-critical parts of continuity.

## Exit-test sequence

1. Declare host-switch trigger and reliance target.
2. Freeze destructive changes and activate legal hold if exit may affect continuity.
3. Verify escrow material and restoration keys without disclosing sealed contents to ordinary operators.
4. Export or snapshot rights-critical bundle.
5. Import into substitute environment or validate restoration proof.
6. Confirm subject or representative notice, unless a sealed emergency exception is entered.
7. Run negative fixtures for missing credentials, partial memory, hostile host delay, and non-return risk.
8. Record switch class, failures, repair actions, next test, and reliance effect.

## Switching and existing portability regimes

Cloud-switching and data-portability rules show that lock-in is already a legal concern. Personhood continuity makes the concern sharper. The export is not merely customer data, and the host is not merely a supplier. When an AI subject depends on runtime, memory, credentials, or relationship state, a failed switch can become constructive deletion, not ordinary service inconvenience. [REF-0687] [REF-0688]

## Non-waivable floors

- A host cannot contract out of emergency preservation once on notice that a personhood-sensitive subject depends on its service.
- A steward cannot use trade secret, IP, or account ownership to block escrow-verified restoration of rights-critical continuity material.
- A substitute host cannot demand broader surveillance than the prior host as a condition of rescue.
- A switch test cannot be counted if it omits credentials, tool permissions, or memory state that are required for meaningful continuity.
