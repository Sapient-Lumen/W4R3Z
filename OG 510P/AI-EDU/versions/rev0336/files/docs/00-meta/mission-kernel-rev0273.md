# Mission kernel rev0273

## Active mission

The mission remains to make AI in education accountable to learning, human
agency, access, safety, workload reality, and honest public claims. The archive
should reward field progress that survives the owner-packet path, not local
paperwork that merely looks like evidence.

## Rev0273 field kernel

Rev0273 burns down the returned-CSV provenance gap. A plausible local CSV is no
longer enough to enter the owner-reply intake bundle. The router and intake tool
must now tie any returned CSV to an active scratch `SENT_AWAITING_REPLY` or
`REASK_AWAITING_REPLY` contact-status clock. That contact clock remains local
non-evidence, but it prevents a free-floating CSV from masquerading as a reply to
the bounded owner request.

The current kernel is:

1. prepare the bounded eight-row packet;
2. send or adapt it outside the archive;
3. record a minimal send log with no contact details or owner answers and a
   bounded response clock;
4. record `SENT_AWAITING_REPLY` from that send log;
5. if a CSV returns, run `owner-field-next` from the same scratch root so the
   emitted `owner-reply-intake` command carries `SOURCE_CONTACT_STATUS=...`;
6. otherwise send one bounded re-ask, or record matching-clock
   `NO_OWNER_PACKET` once the re-ask clock passes;
7. never turn any local routing artifact into `SRC2+` evidence.

## What must not change

No public claim can be made from packet prep, send-now brief, field-texture memo,
send log, contact status, field-next docket, intake bundle, workbench seed, or
smoke output. `FT-0181` remains live until a real owner-reviewed packet is
received, staged, accepted, reviewed, and closed through the downstream evidence
path.

## What should change next

The next substantive move is still external: send or adapt the bounded packet. If
a CSV returns, it should be intaken only through the source-contact-status gate.
If nothing viable returns, the archive should reach a dated `NO_OWNER_PACKET`
rather than stretching clocks, widening the ask, or adding another doctrine
surface.
