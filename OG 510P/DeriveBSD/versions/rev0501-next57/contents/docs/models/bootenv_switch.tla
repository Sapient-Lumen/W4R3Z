---- MODULE BootenvSwitch ----
EXTENDS Naturals, Sequences

(*
A tiny *finite* model of DeriveBSD boot-environment switching.

This is intentionally small: it's here to demonstrate the workflow, not to be
a complete spec of ZFS, loaders, or health checking.

State summary:
- active: the currently confirmed generation (0 or 1)
- staged: the target generation chosen for the next boot (0 or 1)
- mode:   "stable" | "trying" | "confirmed" | "rolledback"
- tries:  remaining attempts before rollback

*)
CONSTANTS MaxTries

VARIABLES active, staged, mode, tries

Init ==
  /\ active \in {0,1}
  /\ staged = active
  /\ mode = "stable"
  /\ tries = 0

Switch(to) ==
  /\ to \in {0,1}
  /\ to # active
  /\ staged' = to
  /\ mode' = "trying"
  /\ tries' = MaxTries
  /\ active' = active

BootAttempt ==
  /\ mode = "trying"
  /\ staged' = staged
  /\ active' = active
  /\ IF tries > 0 THEN tries' = tries - 1 ELSE tries' = 0
  /\ mode' = mode

AssessHealthy ==
  /\ mode = "trying"
  /\ active' = staged
  /\ staged' = staged
  /\ tries' = 0
  /\ mode' = "confirmed"

Rollback ==
  /\ mode = "trying"
  /\ tries = 0
  /\ active' = active
  /\ staged' = active
  /\ mode' = "rolledback"
  /\ tries' = 0

Next ==
  \/ \E to \in {0,1} : Switch(to)
  \/ BootAttempt
  \/ AssessHealthy
  \/ Rollback

TypeOK ==
  /\ active \in {0,1}
  /\ staged \in {0,1}
  /\ mode \in {"stable","trying","confirmed","rolledback"}
  /\ tries \in 0..MaxTries

(*
Safety: we never "confirm" without making staged == active.
*)
ConfirmedImpliesActive ==
  mode = "confirmed" => active = staged

Spec == Init /\ [][Next]_<<active,staged,mode,tries>>

THEOREM Spec => []TypeOK
====
