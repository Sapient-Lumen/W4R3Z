# REV0129 to REV0130 migration map

## For evaluator implementers

- Keep chrony and ntpq parsing adapter-specific.
- Use `tools/ntp_bound.py` for conservative NTP-family interval arithmetic instead of reimplementing root-delay/root-dispersion/age calculations.
- Treat `tools/adapter_equivalence.py` as a regression gate whenever adding or changing an NTP-family adapter.

## For fixture authors

- Add paired adapter fixtures when claiming that two management surfaces describe the same state.
- Do not compare adapter-local diagnostics as core equivalence. Compare interval, timescale, freshness/actionability boundaries, regime, source posture, applicability, and profile decision.

## For consumers

- No TimeState field was added.
- rev0130 states remain compatible with rev0129 consumers that accept local-assessed-state schema output.
- The new generated example is an additional positive fixture, not a new message type.
