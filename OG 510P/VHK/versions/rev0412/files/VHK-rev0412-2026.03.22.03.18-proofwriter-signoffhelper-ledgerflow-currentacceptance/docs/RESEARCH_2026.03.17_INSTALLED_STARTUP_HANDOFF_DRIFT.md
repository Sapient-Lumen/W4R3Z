# Research notes: installed startup handoff drift

Linux startup ownership is not just a present-tense question. Systemd unit-file
state and XDG autostart state can both change between runs, and the resulting
operator question is often historical: was this lane always duplicate-owned, or
did it just drift there?

This revision adds a bounded local history so VHK can preserve that distinction
without pretending it has a fleet-wide monitoring plane.
