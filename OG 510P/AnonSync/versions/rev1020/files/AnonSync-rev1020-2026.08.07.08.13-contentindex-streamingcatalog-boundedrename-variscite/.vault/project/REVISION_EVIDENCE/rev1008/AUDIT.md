# Rev1008 audit

Rev1008 removes the remaining authenticated-peer-turn dependency from source-side
content-defined manifest preparation. One request discovers the exact digest-named
payload and pays the first bounded 32 MiB pulse; the retained single-threaded peer
service can then reopen and re-prove that payload and advance later pulses without
a connected requester. Source preparation and receiver terminal verification share
one fairness gate, yield after each pulse, and alternate when both lanes are pending.

The adjacent audit centralized the borrowed source-projection lookup followed by the
historical access audit, corrected stale lexical ownership assumptions, and bound the
shipping process oracle and status generation 26. The focused source-local scheduler
audit passed 35/35 and the complete structural authority audit passed 602/602.
