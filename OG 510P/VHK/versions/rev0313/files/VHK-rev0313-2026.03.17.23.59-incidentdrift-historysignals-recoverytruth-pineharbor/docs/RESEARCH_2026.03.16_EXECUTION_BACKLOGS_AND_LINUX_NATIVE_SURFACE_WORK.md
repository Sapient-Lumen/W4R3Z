# Research notes — execution backlogs and Linux-native surface work

This pass focused on a product gap that shows up repeatedly in Linux automation
projects: teams can usually describe the architecture before they can stage the
real shipping work.

## Current ecosystem lesson

### 1) Linux automation stacks tend to be assembled, not monolithic

Current tools still split responsibilities sharply:

- text expansion/package tools own always-on snippets and app scoping
- remappers own low-latency key semantics and interception boundaries
- desktop/compositor surfaces own parts of trigger registration
- richer runners own procedural sequencing, prompts, and diagnostics

That means a believable Linux-native planner should not stop at “lane X looks
right.” It should also make the next queued work explicit.

### 2) A lot of real Linux work is review work, not only generation work

The ecosystem keeps showing that some surfaces are not “generate once and done”:

- portal/global-shortcut stories are session/backend-shaped
- helper/input-capture stories require host/service review
- app-aware remapping often needs compositor/app-id confirmation
- launcher/menu integration is desktop-visible and packaging-sensitive

Implication for VHK: a good backlog has to model review and unblock tasks, not
only “generate config” tasks.

### 3) Claim discipline belongs in the same queue as export work

Linux-native product drift often happens when review/claim work is separated
from implementation work. A team generates configs, sees something running on
one box, and then accidentally speaks as if the whole desktop matrix is solved.

Implication for VHK: promotion gates should appear in the same queue as export
surfaces so the project cannot forget the “what is safe to promise?” work.

## Product idea carried into the repo

VHK now has a clearer ladder:

1. classify macro ownership
2. derive project export surfaces
3. mark readiness
4. derive promotion/claim gates
5. queue the remaining work as a **promotion backlog**

That makes the planner feel less like an essay and more like a Linux-native
studio/workbench.
