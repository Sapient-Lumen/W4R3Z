# rev0018 C++ coverage probe

The C++ transition bridge should be ported according to measured traffic, not intuition. rev0018 adds:

```text
src/muc5/cpp_coverage.py
scripts/run_rev0018_cpp_coverage_probe.py
```

The probe runs public-agent games and counts two things:

```text
chosen-action support:
  Did the action actually selected by the public agent have C++ transition support?

legal-action support:
  Did every legal action in the menu have C++ transition support?
```

This distinction matters. A policy may avoid unsupported actions by habit, but a future learned agent could choose them. The long-haul C++ core needs legal-menu-wide coverage, not only chosen-path coverage.

rev0018 smoke results:

```text
games:                      48
decisions:                  13,598
chosen_supported:           13,598
chosen_unsupported:         0
chosen_support_rate:        1.0000
legal_actions_seen:         29,038
legal_actions_supported:    29,038
legal_action_support_rate:  1.0000
```

This happened only after adding C++ support for Jace +2 and Jace Brainstorm activation. Before that, the coverage probe immediately pointed at `ACTIVATE_JACE(mode=zero)` as the dominant unsupported chosen transition. That is exactly what this probe is for.

## Remaining caution

Coverage of sampled public-agent traffic is not a proof. It is a priority signal. The next C++ work should still be driven by directed edge cases and replayable traces.
