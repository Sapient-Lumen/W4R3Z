# ntpq replay fixtures — rev0130

These fixtures are sanitized `ntpq -c rv` and `ntpq -pn` captures used by the ntpq replay adapter and the cross-adapter equivalence harness. Numeric `rootdelay`, `rootdisp`, `offset`, and `clk_wander` values are parsed into seconds/ppm before conservative TimeSync evaluation.

rev0129 introduced the ntpq adapter. rev0130 adds equivalent-state ntpq fixtures paired with chrony fixtures to prove the shared NTP bound and P1 decision path do not diverge across adapters.
