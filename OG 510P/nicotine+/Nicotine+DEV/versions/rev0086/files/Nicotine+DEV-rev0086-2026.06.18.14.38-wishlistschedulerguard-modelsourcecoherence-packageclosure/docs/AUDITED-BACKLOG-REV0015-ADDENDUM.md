# Audited backlog addendum — rev0015

## U-164 / F-CONN-FRAME-01

**Status:** verified audited-backlog hardening; not strict-promoted.

Partial fixed-width F-connection frames are consumed and lost instead of retained until complete. The stronger rev0015 witness also shows resynchronization into different token/offset values when remaining bytes are combined with later suffix bytes. This deserves a regression test and small accumulator guard, but not a front-lane report yet.

## U-188

**Status:** duplicate/alias of U-164. No further independent work planned.

## Next queue target

**ADDR-CONNECT-01 / U-145 + U-171**: server-supplied peer addresses can induce outbound connection attempts to arbitrary non-peer/internal addresses. Audit U-40 and U-205 as aliases/support rows, not separate reports.
