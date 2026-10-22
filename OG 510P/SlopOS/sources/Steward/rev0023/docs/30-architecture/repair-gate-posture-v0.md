# Repair-gate posture v0

Purpose: define a **small crash-loop quieting / repair-gate seam** so Steward can stop pretending that every repeated failure should trigger endless automatic restart.

## Posture
1. **Repeated failure belongs to policy history, not to one exit code alone**
   - One concrete runtime cycle may end with a crash, timeout, or requested stop.
   - A repair gate is about the *pattern* of recent cycles and restart attempts, not about overloading one cycle-end cause with too much meaning.
2. **Backoff and repair gates should stay explicit and visible**
   - Steward should be able to surface states such as cooling down, restart delayed, or repair required instead of silently sleeping and trying again forever.
   - Status views, receipts, and shell affordances should prefer explicit explanation over “it just is not coming back yet.”
3. **Quieting is healthier than endless restart optimism**
   - Historical systems repeatedly rediscover that blind fast respawn can waste resources, hide root cause, and amplify damage.
   - Steward should keep some narrow notion of “enough automatic retries for now” even if the exact thresholds remain implementation policy at first.
4. **Cooling down is not the same as repaired**
   - A temporary backoff window and a repair-required gate answer different questions.
   - “Try again later automatically” is different from “wait for operator/policy/runtime change before trying again.”
5. **Clear/repair should be explicit, not ambient**
   - If a component is repair-gated, leaving that state should happen through an explicit Steward action, a manifest/config revision, or another narrow policy signal.
   - Steward should resist folklore where random restarts, reboots, or stray manual pokes implicitly erase fault history.
6. **Repair gates should preserve explanatory context**
   - The user should be able to see the recent cycle witnesses, compact end causes, cooldown/quieting history, and the reason the gate was entered.
   - A good repair gate is partly an evidence object, not just a stop bit.
7. **Portable semantics should stay smaller than a universal retry language**
   - Phase 1 likely needs only a compact distinction such as active, cooling-down, and repair-required, plus optional native detail underneath.
   - The full restart-budget grammar can stay more open until real use-cases converge.
8. **Healthy runs may earn a reset, but the rule should stay honest**
   - Historical systems often reset backoff after a sufficiently successful run.
   - Steward may do likewise, but the UI should not imply the system forgot history magically; it should simply say the recent-failure window no longer applies.
9. **Shell/terminal UX should make repair gates actionable, not mysterious**
   - When a command frame or status chip points at a repair-gated component, likely good affordances are explain, open recent cycles, attach failure bundle, or request explicit repair/clear.
   - Rerun-heavy affordances should require stronger confirmation when the system is telling the user it is in a repeated-failure state.

## Phase-1 non-goals
- freezing a universal restart-budget DSL with every threshold, curve, and exception knob up front;
- promising that every implementation has identical backoff timing or identical repair heuristics;
- conflating crash-loop quieting with liveness, readiness, or one-cycle termination cause;
- hiding repair gates behind silent retries or host-specific folklore.

## Adjacent docs
- `supervision-posture-v0.md`
- `readiness-posture-v0.md`
- `status-channel-posture-v0.md`
- `runtime-cycle-witness-posture-v0.md`
- `termination-cause-posture-v0.md`
- `context-handoff-posture-v0.md`
- `non-decisions-v0.md`

## References
- REF-ERLANG-OTP-SUPERVISOR
- REF-LAUNCHD-SOCKETS
- REF-SYSTEMD-SERVICE
- REF-SYSTEMD-UNIT
- REF-K8S-POD-LIFECYCLE
- REF-SMF-MAINTENANCE
- REF-GNU-SHEPHERD-MANUAL
