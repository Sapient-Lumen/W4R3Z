# Human stories and friction atlas

Status: first narrative pass plus red-team and hope passes. Updated 2026-09-17.

This document is product discovery by story. It is not a protocol promise and
not a command registry. The goal is to keep asking: when a real human reaches
for IoTox, what are they probably trying to do, where will they accidentally
cut themselves, and what is the smallest feature that makes the safe path feel
obvious?

The answer should usually be a porch, not magic:

```text
show the situation
name the boundary
print the exact next command
refuse to hide authority
```

IoTox should feel warm at the edge and strict at the center. A good feature
lets the operator take one correct next step. A bad feature silently decides
who is trusted, where remote files go, whether sudo is allowed, whether a route
fallback is acceptable, or whether synchronized copies count as backups.

The red-team rule for this file is sharper:

```text
if the feature mostly proves we are clever, do not build it yet
if the feature removes a common wrong action, consider it
if the feature creates confidence faster than it creates evidence, reject it
```

This repo is already powerful and already too easy to make ceremonious. The
human risk is not only that IoTox lacks features. The risk is also that it has
so many exact surfaces, proofs, porches, and nonclaims that a tired operator
either gives up or cargo-cults a command sequence without understanding the
boundary that made the sequence safe.

## Story 1: “I just want this laptop and that box to know each other”

Mara has IoTox running on a laptop and a small machine across the room. She can
see two long keys, one Tox address, one stable principal, and a signed
invitation artifact. The machine is right there, but the ritual still feels
like a wire transfer form.

She is not trying to understand authority-v3 yet. She wants a card: “this is
the box, this is what it is asking for, here is the phrase/fingerprint to
compare, and accepting this still grants no powers.”

Likely accidental friction:

- confusing the Tox public key, Tox address, and stable IoTox principal;
- thinking a requested capability in an invitation is already granted;
- pasting the wrong expected inviter key because every token looks equally
  inhuman;
- accepting friendship and then wondering why sync or terminal still refuses;
- losing the artifact and not knowing whether retry is safe.

Worth fixing:

- printable/pastable pair cards with a stable word fingerprint, expiry, alias
  suggestion, requested capabilities, and `authority-granted=0` in the loudest
  possible place;
- `peer-fingerprint PEER` or `pair-card fingerprint PATH` using the same word
  vocabulary everywhere IoTox asks humans to compare identities;
- pair-card inspection that says “transport introduction only” and prints the
  next authority command only as a separate ceremony;
- retry-safe language: “friendship already exists; alias still needs repair” is
  better than a generic failure.

Do not fix it by auto-granting authority when a card is accepted. The whole
point is that friendliness does not become sovereignty by accident.

## Story 2: “Can this replace Resilio for my notes?”

Alex has a directory of notes, scripts, and small documents. Resilio worked
because every machine just joined the share and started moving bytes. IoTox
looks more honest but also more ceremonious: local path here, remote path
there, reciprocal grants, `sync-doctor`, `read-write`, RecallRoot phrases,
writer sets, and backup warnings.

Alex's real question is not “what is tree-v2?” It is: “is this directory safe
to try, what exact commands do I run on both sides, and when am I allowed to
trust the result as a working copy?”

Likely accidental friction:

- trying to sync a directory containing symlinks, xattrs, sockets, hard links,
  sparse files, or case-colliding names;
- assuming one side can choose the other side's destination path;
- doing only one `sync-share` in a read-write pair and wondering why writes do
  not flow back;
- using a precious directory as the first experiment because the happy path
  looks real;
- reading “passed sync” as “backed up.”

Worth fixing:

- a true `docs/quickstart.md` with three copyable recipes: pair two nodes,
  create a read-write sync, and create an SSH-like terminal profile;
- a “replace Resilio?” page that says: useful for noncritical/private Linux
  regular-file working copies, not a backup, not for unsupported filesystem
  semantics, and not yet a sole system of record;
- `sync plan-pair` and `sync plan-mesh` outputs that render the ceremony as a
  two-column or seating-chart plan: local act, remote act, authority act,
  expected state after each;
- an optional “practice tree” generator so a new operator can experience
  pair/share/edit/conflict/repair without risking real files;
- a convergence watch that says which phase is active: source scan, transfer,
  CAS verification, branch publication, projection, repair, conflict
  preservation.

Do not fix it by allowing remote-selected paths. Choosing where bytes land is
local machine authority.

## Story 3: “I edited the same file on two machines while offline”

Nia takes a laptop into the field and edits `today.md`. A desktop at home edits
the same path. When they reconnect, IoTox does the correct thing: it preserves
both values, projects one deterministic ordinary path, and exposes the other
candidate under `.iotox-conflicts/by-origin`.

That is honest, but not necessarily humane. The conflict directory looks like
an implementation detail until someone is scared that IoTox “lost” their edit.

Likely accidental friction:

- interpreting the projected ordinary file as the winner;
- editing `.iotox-conflicts` directly and expecting that to resolve anything;
- not knowing which device authored which candidate;
- not knowing whether a deletion conflict preserved bytes somewhere else;
- resolving before all branches are visible.

Worth fixing:

- keep expanding `sync-conflicts-summary` and `sync-conflict-explain` into a
  comforting guide: “nothing was overwritten; here are the candidates; resolve
  by making one later ordinary edit”;
- add a read-only candidate opener/exporter that copies alternatives into a
  temporary review directory without treating that directory as the protocol
  state;
- add `sync-watch` conflict events that are alias-aware but path-redacted when
  requested;
- eventually add a merge porch that stages a normal worktree edit rather than
  creating a secret conflict-resolution protocol.

Do not fix it with last-writer-wins. That makes IoTox feel familiar right up
until it destroys the only copy of the truth someone cared about.

## Story 4: “I deleted the wrong folder and now every peer is honest about it”

Sam deletes a directory, or a script mangles many files, or a compromised
authorized writer emits valid bad state. IoTox authenticates the event because
the writer really had authority. The cluster converges beautifully into the
wrong human outcome.

This is the story behind “sync is not backup.” Humans understand it only after
they have been burned unless the product gives them a brake and a recovery
porch.

Likely accidental friction:

- assuming another writable peer is a backup;
- assuming pins, checkpoints, CAS history, or conflict preservation are enough;
- running repair while trying to recover a human mistake;
- not knowing how to stop automation before damage spreads further;
- not knowing which backup generation was last independently restored.

Worth fixing:

- an emergency local brake such as `sync pause NAMESPACE` or `sync freeze
  NAMESPACE` that stops local automation and prints exactly what it did not do;
- a recovery-plan porch that joins `sync-recovery-verify`, provenance labels,
  readiness, pins/checkpoints, and “do not mutate live state yet” guidance;
- clearer panic language in `readiness storage` and `explain backup-independence`;
- retained, content-free restore drill receipts that operators can compare over
  time;
- a “before precious data” checklist that treats recovery custody and restore
  rehearsal as living operations, not one-time setup.

Do not fix it by adding a casual `rollback` button. A rollback is another
powerful write and can become a second way to destroy good data.

## Story 5: “I need a shell on my machine, and honestly I probably need sudo”

Jules is away from home and wants to administer a machine. The desired
experience is SSH-shaped: connect, get a shell, run commands, use sudo when
the host policy allows it, survive flaky connectivity.

IoTox's security posture is right but surprising. The peer does not choose an
arbitrary command. A profile chooses the account, executable, argv, cwd,
environment, and limits. Sudo is not the default. A profile may grow stale if
its Nix-store shell path is collected or upgraded.

Likely accidental friction:

- expecting `iotox terminal host "any command"` to exist;
- expecting a terminal authority grant to imply sudo;
- binding the wrong profile to the wrong principal;
- discovering the shell path no longer exists only during an emergency;
- not understanding whether a reconnect resumed the same PTY or opened a new
  session;
- confusing host sudo failure with IoTox authority failure.

Worth fixing:

- terminal status that says, in human language, “normal shell ready,” “sudo
  profile installed but host policy still decides,” “rescue profile missing,”
  or “profile executable no longer exists”;
- a profile stale-path checker, especially for exact Nix-store paths;
- first-attach banners that name the profile, account, privilege posture,
  confinement posture, and reconnect behavior before the user starts typing;
- a `terminal sudo doctor` that checks only prerequisites and never edits
  sudoers;
- a batch-mode story that is explicit: shell input, not SSH exec.

Do not fix it with remote-selected exec, agent forwarding, port forwarding, or
automatic sudo profiles. Those are different authorities.

## Story 6: “The normal shell is broken; please bring tools with you”

Rae can reach the Agent, but `/bin/bash` is gone, the dynamic loader is broken,
or the PATH is unusable. IoTox's rescue toolbox idea is exactly for this kind
of unpleasant day, but it only helps if it was installed, retained, bound, and
rehearsed before the outage.

Likely accidental friction:

- believing rescue fallback is automatic;
- building the toolbox but not binding a rescue profile;
- letting the static payload be garbage-collected;
- expecting rescue tools to repair a lost Agent, lost authority, or wrong
  architecture;
- not rehearsing login until the day it matters.

Worth fixing:

- `readiness terminal` should eventually say whether a rescue profile is
  installed, bound, executable, and recently rehearsed;
- a rescue rehearsal command that opens a harmless profile and records a
  content-free success receipt;
- a retention check for toolbox payload paths;
- documentation that says rescue userland is boring insurance, not magic.

Do not fix it by shipping arbitrary remote payloads on demand. The rescue
toolbox is a preauthorized local profile, not a smuggling lane.

## Story 7: “The Agent is down, or maybe I used the wrong runtime”

Taylor runs `iotox peers` and gets a socket/path error. They do not know if the
Agent is stopped, the runtime directory is wrong, the service never installed,
the config file is invalid, or the process lacks permissions.

This is the first-contact failure. It should be almost impossible for a normal
operator to get stuck here without a next command.

Likely accidental friction:

- wrong `--runtime`;
- stale systemd user service;
- config generated under one root and service started with another;
- runtime directory missing after logout;
- bad permissions on state/config roots;
- expecting control commands to start the Agent.

Worth fixing:

- a top-level `doctor` or stronger `overview` offline mode that tries the
  canonical config/runtime guesses and prints exact next commands;
- service examples that are copied into a first-run guide, not only a deep doc;
- `explain agent-offline` variants for “runtime missing,” “socket refused,”
  “permission denied,” and “wrong user”;
- `run-check --config` output that is short enough to paste into support.

Do not fix it by auto-starting an Agent from an arbitrary control command.
Starting a device identity is a real local state decision.

## Story 8: “Support asked for a bundle; am I leaking secrets?”

Ira hits a weird sync or terminal state and wants help. IoTox says the
diagnostic bundle is content-free, but the operator still worries: is it safe
to paste? Does it prove the device produced it? Does it expose private paths?

The correct answer is subtle: content-free is not information-free; inspect
before sharing; it is not attestation, not backup proof, and not a signed audit
log for outsiders.

Likely accidental friction:

- treating `diagnostics-export` as a log sweep;
- treating a valid bundle as proof the device is healthy;
- sharing a correlating metadata bundle with the wrong audience;
- forgetting to inspect before uploading;
- wanting to include more detail and accidentally reaching for raw logs,
  config, or paths.

Worth fixing:

- keep `support-bundle plan` as the front door, and make it more narrative:
  “what this includes,” “what it never includes,” “what it can correlate”;
- add an inspect summary grouped by audience: self, trusted maintainer, public
  issue;
- add a local-only “support note” template that keeps private free-form notes
  outside the bundle unless the user deliberately copies them;
- make all future support paths resist “just add raw logs.”

Do not fix it by making support bundles omnivorous. IoTox's useful support
artifact is useful because it refuses content.

## Story 9: “I asked for Tor or I2P; did it quietly fall back?”

Lee wants a route policy, not a vibe. If a command says Tor, and Tor cannot
carry it, IoTox must fail loudly. If a status line says native, it should mean
native. Route labels are evidence scope.

Likely accidental friction:

- assuming Tor/I2P routes are anonymity guarantees;
- assuming a successful native transfer says anything about overlay readiness;
- assuming a route preference may silently fall back;
- not seeing which route class carried a sync or terminal event;
- comparing performance without knowing the route class.

Worth fixing:

- `readiness routes` should stay blunt about native accepted versus Tor/I2P
  bounded;
- status/watch output should include route class in a redaction-safe way;
- explain topics should distinguish fallback refusal from ordinary network
  loss;
- future route setup should print “this will not fall back silently” before it
  mutates configuration.

Do not fix it with best-effort fallback. That makes the evidence lie.

## Story 10: “It is moving bytes, but I cannot tell if it is alive”

Morgan starts a large sync. For a long time nothing human-visible changes.
Under the hood, IoTox may be scanning, hashing, transferring, verifying CAS,
publishing a branch, staging a projection, repairing, or waiting for a peer.
All of those are different states with different failure meanings.

Likely accidental friction:

- killing a healthy job because it looks hung;
- missing store/staging pressure until the job refuses;
- interpreting partial sparse custody as corruption;
- not knowing whether cap 4/8/16 lanes would be better for this directory;
- being surprised by projection cost after transfer completes.

Worth fixing:

- `sync-watch NAMESPACE` with phase lines, counters, and no content/path leak by
  default;
- a short “why no ETA?” explanation when IoTox cannot honestly estimate;
- status fields that distinguish selected objects, missing objects, projected
  entries, conflict alternatives, sparse-skipped objects, and repair state;
- warnings when a directory approaches documented entry/quota/capacity edges;
- operator-tunable lane advice only after measuring the actual namespace shape.

Do not fix it by printing private paths or pretending all phases are transfer
progress.

## Story 11: “We have three writable nodes and one person left”

A small group has three machines in a read-write mesh. One device is retired,
lost, or no longer trusted. The right ceremony is bigger than “remove friend”:
revoke capability, cut off writer generations, update every survivor, and
verify health.

Likely accidental friction:

- removing a Tox friend but leaving IoTox writer authority effective;
- updating one survivor and forgetting another;
- misunderstanding the six directional share ceremonies in a three-node mesh;
- failing to prove every peer has observed the cutoff;
- not knowing whether old branches remain only as history or still active
  authority.

Worth fixing:

- a mesh “seating chart” that renders principals, aliases, capabilities,
  writer/subscriber membership, automation mode, and cutoff floor without
  exposing paths;
- `sync retire-writer plan` that prints exact revocation/cutoff/repair checks
  for every survivor;
- health output that treats stale writer membership as an operator-facing
  yellow/red condition;
- a story in the quickstart for replacing one node from empty state.

Do not fix it by making friendship removal imply authority removal. Transport
and authority must remain separate enough to audit.

## Story 12: “I want to talk to ChatGPT or a maintainer about this repo”

The founding operator already uses datacubes to carry repository state into
other conversations. That is a real human workflow: package the truth, keep it
under a size budget, include the docs that explain the product, and exclude
build/proof debris unless deliberately requested.

Likely accidental friction:

- exporting too much local evidence and blowing the size budget;
- omitting the docs that explain the human boundaries;
- including bulky generated build trees;
- treating a datacube as a release artifact rather than a conversation
  artifact;
- forgetting which commit the datacube represents.

Worth fixing:

- keep the exporter dry-run and manifest-first;
- include README, product page, roadmap, human ergonomics, this story atlas,
  sync plan, Ratox status, and storage readiness near the top of the manifest;
- add a small “conversation bundle” profile distinct from “evidence bundle” and
  “release source archive”;
- always record commit, dirty status, byte budget, and exclusions.

Do not fix it by hiding the repository's real complexity. The point of a good
datacube is that another mind can understand the shape without having the
machine.

## Red-team pass: how these stories could be wrong

The first story pass is friendly to IoTox. That is useful for invention, but it
can also flatter the repo. A harsher reading produces several warnings.

### We may be designing for the founder, not the next human

The founding operator is unusually tolerant of exact ceremonies, retained
proofs, Nix/Sandwurm language, datacubes, and evidence-shaped claims. A normal
operator may not want a philosophy lesson before syncing notes or opening a
shell. If the first minute contains too many nouns—RecallRoot, stable
principal, Tox key, authority ledger, tree-v2, route class, witness floor—the
right feature may not be another command. It may be one shorter sentence and
one exact safe next action.

Product correction:

- every new porch should have a “first sentence” test: one line that explains
  what the human can do now and what it does not prove;
- docs should lead with the smallest successful story, then link to the proof;
- binary output should avoid introducing more internal names than the next
  action requires.

### We may be overproducing porches

Porches are good, but porch sprawl is real. If every difficult concept becomes
another top-level command, IoTox can become a museum of safe entrances rather
than a tool. The command surface is already large; making it kinder by adding
more verbs has a ceiling.

Product correction:

- prefer improving existing `overview`, `readiness`, `explain`, `help`, and
  grouped `sync`/`terminal` commands before adding new top-level spellings;
- add new verbs only when they change the operator's action, not merely the
  phrasing of the explanation;
- aggressively group human flows under existing families.

### We may be using evidence prose as emotional armor

IoTox is admirably honest about what its tests prove. But long evidence
sections can also function as armor: a user cannot easily tell which sentence
answers “should I put my directory here?” The repo can be technically honest
and still fail the human.

Product correction:

- each major area needs one blunt readiness line: use, do not use, or use only
  with named external guardrails;
- every “accepted” evidence statement should be paired with a “still does not
  mean” sentence;
- precious-data and sudo boundaries should stay visible even in happy-path
  quickstarts.

### We may be too optimistic about sync ergonomics

The stories assume humans will run doctors, read warnings, and rehearse
recovery. Many will not. They will point IoTox at the directory they care
about because that is what synchronizers are for. If IoTox makes that easy
before backup custody is real, our docs will not save them.

Product correction:

- the first sync setup should bias toward a generated practice tree or an
  explicitly noncritical path;
- `sync start`/`sync-create` should continue to make unsupported filesystem
  shapes painful early, not forgiving;
- emergency pause/freeze may matter more than richer merge UX because human
  damage is more likely than exotic merge needs.

### We may be too optimistic about terminal readiness

Ratox is technically impressive, but remote administration is judged during
stress: weak network, stale profile, missing shell, collected Nix store path,
sudo prompt weirdness, or a half-remembered alias. A beautiful terminal demo
does not mean the operator can rescue a machine at midnight.

Product correction:

- stale-profile and rescue-readiness checks are not polish; they are part of
  making SSH-like control humane;
- first-attach banners and `terminal doctor` should explain host sudo versus
  IoTox authority before the user misdiagnoses a failure;
- do not spend product complexity on SSH parity features before the boring
  “will my approved shell still start?” path is excellent.

### We may be underestimating privacy leaks in “helpful” views

Humans want names, paths, progress, and support summaries. Those are exactly
the details that can leak private life. Alias-aware and path-aware views are
nice locally; support bundles and public datacubes need a different default.

Product correction:

- local human output may be rich, but every shareable artifact must remain
  content-free by construction;
- any watch/support feature needs an explicit redaction mode from the start;
- private notes/tags for aliases should never enter diagnostics by accident.

### We may be tempted to build impressive wrong features

Some features would make demos better while cutting against IoTox's product
law: one-click authority after pairing, remote-selected sync paths, arbitrary
remote exec, port forwarding, agent forwarding, automatic sudo, silent route
fallback, raw support logs, or a rollback button that hides its danger.

Product correction:

- if a feature makes IoTox feel more like a cloud account, SSH superset, or
  magic backup, distrust it;
- every convenience must declare which authority remains external or separate;
- refuse the feature if the refusal teaches the product better than the feature
  would.

## Stories still missing

These are not yet written deeply enough and should shape future passes.

### “I installed IoTox from a package; what owns updates?”

A packaged user will ask whether IoTox updates itself, whether the OS package
manager owns it, whether a signed IoTox update can replace the binary, and how
to recover if an update breaks remote terminal access. This intersects update
signing, host service policy, and terminal rescue. The right feature is likely
an update/readiness story, not automatic self-update.

### “I lost the laptop but remember the phrase”

RecallRoot is core, but the human story of re-entry is bigger than a ceremony:
which devices still trust the old principal, which sessions must be revoked,
which backups are safe, and how to avoid making a stolen device useful again.
This story should pressure owner-reentry docs, revocation porches, and witness
freshness.

### “My friend helped me set this up; who can still do what?”

IoTox is personal, but real humans ask friends for help. The product needs a
way to inspect current authority in plain language without exposing secrets:
who may sync, who may open a terminal, who may publish updates, and what is
only transport friendship.

### “I changed machines, usernames, filesystems, or distros”

The repo's strongest evidence path is Linux/KVM-heavy. Users will move between
NixOS, other Linux distributions, ext4, btrfs, different shells, changing UID/
GID layouts, and eventually non-Linux dreams. The feature pressure is not
portability promises. It is migration/readiness honesty before mutation.

### “A command says no, but I need to get work done”

Fail-closed systems create pressure to bypass them. If IoTox refuses symlinks,
world-writable files, weak permissions, route fallback, or unsupported sudo
posture, the operator will look for a flag. The right design may be better
explanation and safer staging, not more `--force`.

## Features the red-team pass downgrades

Some first-pass ideas are still interesting but should not lead the roadmap.

- **Merge porch:** useful later, but dangerous if it implies IoTox can safely
  decide human content. Keep conflict explain/export first.
- **Dynamic completion over live state:** tempting, but easy to leak aliases,
  namespaces, or paths. Keep static completion and explicit local commands
  until redaction rules are obvious.
- **Support audience summaries:** useful, but only after the bundle remains
  mechanically content-free. Do not add a path where raw notes slide into the
  artifact.
- **Lane tuning advice:** can help large syncs, but premature advice may
  distract from the simpler bottleneck: humans need to know what phase is
  happening and whether it is healthy.
- **Additional top-level aliases for every porch:** discoverability improves
  until it does not. Group first, alias later only when repeated use proves it.

## Hope pass: if IoTox becomes worthy

The red-team pass keeps IoTox from flattering itself. The hope pass asks the
opposite question: if IoTox grows up without betraying its laws, what beautiful
human situations should become ordinary?

This is not permission to claim readiness early. It is permission to remember
why the hard parts are worth doing.

```text
the device is yours before it is online
the shell is ordinary before it is magical
the proof is quiet before it is impressive
the network helps without becoming king
```

### Hope story 1: “The little machine comes home”

Someone buys or builds a small computer. There is no vendor account to create,
no cloud tenancy to accept, no “forgot password” route that gives a company
the power to become owner. The box boots, prints a pair card, and says in plain
language: “I can be introduced. I cannot be commanded yet.”

The human compares words, names it `basement`, and later grants exactly two
things: sync this noncritical directory, and allow an owner shell. Months
later, the Tox route identity rotates, Tor becomes useful, or a bootstrap node
changes. The name `basement` still means the same owned machine because its
stable principal never became a vendor account or a transport accident.

Hopeful feature shape:

- a first-run identity card that is understandable on paper;
- one visible distinction between “reachable,” “known,” and “authorized”;
- a household/device map that displays stable principals, aliases, routes, and
  authority without exposing secrets;
- endpoint rotation and route changes that feel like changing roads, not
  changing the person.

### Hope story 2: “A directory becomes a living working copy, not a trap”

A writer keeps field notes on a laptop, a desktop, and a small home server.
IoTox sync is not the only copy; the backup is independent and rehearsed. That
condition is visible, not hidden in a forgotten runbook. The writer opens
`iotox readiness sync` and sees: “working copy ready; precious-data guardrail
depends on backup generation X, last restored on Y.”

The sync itself feels calm. When it is busy, it says which phase it is in.
When two edits conflict, it speaks like a good librarian: “both notes are
safe; here are the two origins; make one later ordinary edit to choose.” When
the writer panics after deleting a folder, one local brake stops automation and
prints what remains outside its reach.

Hopeful feature shape:

- phase-aware `sync-watch`;
- local emergency pause/freeze that is boring, reversible, and exact;
- recovery-plan output that joins recovery-custody labels, restore drill
  receipts, pins/checkpoints, and current sync health;
- conflict review tools that preserve ordinary editing rather than inventing a
  magical merge authority;
- a “practice sync” path that teaches with disposable trees before anyone
  points IoTox at a beloved directory.

### Hope story 3: “SSH, but owned by the machine instead of the network”

The owner is away from home. The machine is behind NAT, its IP address is
irrelevant, and there is no inbound SSH port. The owner says `iotox terminal
workstation --reconnect` and gets the approved shell. A banner names the
profile, account, route class, confinement posture, and sudo posture in a few
lines. It feels like SSH in the fingers, but not in the trust model.

Sudo is present because the owner deliberately installed an admin profile and
the host's own sudo policy accepts the human. If the normal shell path is
stale, IoTox knew yesterday. If rescue tools are installed, IoTox has rehearsed
them. If the route dies, the PTY waits for the same owner to return rather
than pretending packet loss is a new login.

Hopeful feature shape:

- first-attach terminal banner with profile/account/sudo/confinement/reconnect
  truth;
- terminal stale-profile checks, especially for exact Nix-store paths;
- rescue toolbox retention and rehearsal receipts;
- native terminal readiness now says whether shell/sudo/rescue profile payloads
  are present, pinned, stale, or review-required; the richer future banner
  should fold that into live binding/service/route state;
- no remote-selected exec, forwarding, or ambient credential tunnel.

### Hope story 4: “A family has machines, not accounts”

A household has a few laptops, one media box, one backup box, and a device in a
workshop. The people are not system administrators, but they understand
relationships: this person may read photos, this device may publish music,
this old laptop may no longer write, this friend may help with repair today
but not remain an owner forever.

IoTox can show those relationships without turning them into a social network
or a cloud ACL screen. The map is local, private, and printable. It says:
friendship, authority, sync membership, terminal profile binding, and update
signing are different edges. Removing a friend does not lie and pretend it
revoked every capability; instead the retirement plan walks the human through
the exact cuts.

Hopeful feature shape:

- authority “seating chart” for ordinary humans;
- `sync retire-writer plan` and broader `authority retire-principal plan`;
- pair-card/fingerprint language that two people can compare aloud;
- private local notes/tags that never enter diagnostics;
- small household runbooks generated from actual local policy, not generic
  docs.

### Hope story 5: “Support is dignified”

Something fails. The operator can ask for help without pasting private paths,
terminal output, filenames, keys, or logs. The support bundle is not a dump; it
is a small, inspectable object that says what classes of things happened and
what it cannot prove.

A maintainer can respond with humility: “your Agent was offline,” “this
namespace is healthy but not backed up,” “this terminal profile path is stale,”
or “I cannot tell from this bundle; please run this local-only command and read
the line to me.” IoTox support culture becomes part of the product: never ask
for secrets, never normalize raw log uploads, never make shame the price of
debugging.

Hopeful feature shape:

- support-bundle inspect summaries for self/trusted-maintainer/public issue
  that are still mechanically content-free;
- local-only support notes that are never swept into bundles;
- explain topics that turn common strict refusals into calm next actions;
- diagnostic receipts that are useful because they omit tempting private data.

### Hope story 6: “The network commons gets stronger without owning anyone”

IoTox devices can contribute bootstrap and relay capacity because their owners
choose to help. The product can say: “you are contributing reachability; you
are not becoming anyone's owner; no one depends on this exact node as a vendor
service.” Tox gets healthier because ordinary operators can run small pieces
of commons infrastructure without becoming a company.

Routes become understandable. Native, Tor, and I2P are named paths with
evidence and nonclaims. A route working does not become an anonymity badge; a
route failing does not silently leak over another path. The operator can see
which roads are available and which roads carried which class of work.

Hopeful feature shape:

- route readiness that distinguishes reachability, privacy posture, and
  evidence scope;
- contribution plans for bootstrap/relay capacity that do not create central
  dependence;
- route watch/status lines that stay redaction-safe but never hide fallback;
- route policies that ordinary owners can read before enabling.

### Hope story 7: “Small physical things become accountable”

The long dream is not just laptops. It is a pump, a greenhouse vent, a light, a
sensor, a lab box, a cabin machine. The first safe effects are intentionally
boring. IoTox does not start with locks, vehicles, medical devices, heat,
industrial motion, or anything whose wrong state can hurt a person.

But when a harmless effect arrives, it has dignity: the command is signed, the
capability is explicit, the result is durable, replay is understood, rollback
is witnessed where it matters, and the local device can explain what happened
without asking a vendor who owns the thing.

Hopeful feature shape:

- one low-consequence actuation demo that is end-to-end and deeply boring;
- effect-specific capabilities, not generic “run anything” power;
- durable effect receipts with deduplication and replay boundaries;
- physical safety exclusions that stay louder than the demo.

### Hope story 8: “A person returns from memory”

Years pass. A laptop dies. A phone is lost. The owner still has the generated
phrase in the place they chose to preserve it. IoTox lets them re-enter
without asking a company to bless them. That re-entry is not casual: it
explains which devices are known, which authority epoch is current, which
old device should be distrusted, and which witness/checkpoint facts are
available.

The beautiful part is not that the phrase is magic. The beautiful part is that
the owner can come back without a vendor master key existing anywhere.

Hopeful feature shape:

- owner re-entry guide that is calm, offline-first, and hostile to weak
  human-chosen phrases;
- lost-device ceremony that joins revocation, writer cutoffs, terminal
  session closure, route identity rotation, and backup verification;
- witness freshness made visible without making witnesses sovereign;
- printable custody cards for humans who need physical memory aids.

### Hope story 9: “A maintainer can disappear without bricking the world”

The official repo may slow down, fork, or vanish. A worthy IoTox still leaves
behind enough ordinary surface, protocol docs, reproducible builds, and
content-free evidence patterns that another implementation can speak to owned
devices. The project does not become a company-shaped root of trust.

The operator should be able to say: “I can replace the controller, move the
route, rebuild the binary, inspect the ledger, and recover the owner. The
network and the repo helped me, but neither owns me.”

Hopeful feature shape:

- command and protocol docs that remain implementable, not merely historical;
- reproducible source/package/datacube receipts;
- exported public examples that never require a project-controlled service;
- compatibility tests that help independent clients without requiring
  cross-client work from this repo.

### Hope story 10: “IoTox becomes boring”

The highest hope is not that IoTox feels futuristic. It is that one day the
sovereign path feels normal. Pairing is a card. Sync is a working copy with a
known backup. Remote shell is an approved profile. Sudo is the host's policy.
Routes are named. Support is content-free. Recovery is rehearsed. The device
is owned locally before the network ever helps.

That boringness is the product. The miracle disappears into habits that do not
betray the human.

Hopeful feature shape:

- fewer nouns per minute;
- fewer surprise powers;
- more calm receipts;
- better first-contact diagnosis;
- more local rehearsals before emergencies;
- docs that teach one safe movement at a time.

## Hopeful feature signals

The hope pass does not replace the red-team priority list, but it changes the
emotional center. The right features are not merely “ergonomic.” They help a
human feel at home with owned machines.

1. **Identity cards and maps.** Make reachable/known/authorized distinctions
   visible enough that humans stop conflating them.
2. **Practice before preciousness.** Give people disposable paths to learn
   pairing, sync, conflict, recovery, and terminal setup before real data or
   emergencies are involved.
3. **Calm emergency controls.** Pause/freeze, rescue readiness, stale-profile
   checks, and recovery plans are hopeful because they reduce panic.
4. **Relationship views.** Human-scale authority maps matter as much as raw
   command power once there are several devices or helpers.
5. **Content-free support culture.** Make dignified debugging the default, not
   an advanced privacy mode.
6. **Commons contribution without sovereignty.** Help Tox become stronger
   while keeping infrastructure operators out of the owner role.
7. **Effect receipts before exciting actuators.** The first physical effects
   should be boring enough to prove the semantic path, not impressive enough
   to hide safety questions.
8. **Re-entry without vendor mercy.** Owner recovery, lost-device response, and
   witness freshness are part of the soul of the product, not late polish.

## Patterns worth building around

The stories point at a small set of feature shapes that seem right for IoTox:

1. **Porches before mutation.** `plan`, `doctor`, `readiness`, `explain`,
   `inspect`, and `watch` are high-leverage because they make the next step
   visible before state changes.
2. **Receipts after scary operations.** Pairing, sharing, repair, recovery
   rehearsal, rescue rehearsal, support export, and datacube export should all
   leave small content-free records of what class of thing happened.
3. **Names with fingerprints.** Aliases are for memory; word fingerprints are
   for comparison; neither should become authority.
4. **Emergency brakes.** Synchronization needs a humane local pause/freeze path
   for “I may have done damage” moments.
5. **Phase-aware watches.** Long operations should say what kind of work is
   happening without leaking content.
6. **Stale-profile detection.** Remote shell reliability depends on noticing
   missing shells, collected rescue tools, invalid profile stores, and sudo
   prerequisites before an emergency.
7. **Backup humility.** Every recovery-friendly feature must keep saying:
   convergence is not backup, and history is not independent custody.
8. **Fewer nouns per minute.** If output teaches three internal concepts when
   one next command would do, the output is probably serving the repo more than
   the operator.
9. **Shareable artifacts are hostile territory.** Anything meant for another
   human or another model must start from redaction, not add redaction later.
10. **Stress paths beat demo paths.** Rescue, stale-profile checks, pause/
   freeze, restore rehearsal, and first-contact diagnostics matter because
   humans reach for them when already anxious.

## Highest-priority feature candidates after red-team

The next ergonomic features that still look valuable after doubting the repo
are:

1. **One brutally short quickstart plus “replace Resilio?” page.** This is the
   cheapest way to reduce dangerous overtrust, but it must be short enough that
   a non-founder actually reads it.
2. **First-contact `doctor`/offline overview improvements.** Before adding
   deeper features, make “Agent not reachable” and “wrong runtime/config/user”
   almost impossible to get stuck on.
3. **Richer `sync-watch NAMESPACE` phase truth.** A first watch now exists and
   reports live/offline state plus the local freeze record. The next layer is
   Agent-exposed phase truth: scanning, transferring, verifying, projecting,
   repairing, conflict preservation, or stuck, still without invented ETA
   confidence.
4. **Emergency sync pause/freeze enforcement.** The local durable freeze record
   now exists and says exactly what it does not stop. The next safety step is
   Agent enforcement that stops local automation/destructive cleanup while
   preserving the same honesty about remote peers.
5. **Terminal profile stale-path and rescue readiness.** The first native
   `terminal readiness` porch now checks profile payload pins and rescue
   toolbox staleness. SSH-like trust still needs richer binding/service/route
   continuity signals in the same view.
6. **Peer/pair-card word fingerprints.** Important, but lower than first
   contact and recovery because bad hex UX hurts setup while bad recovery UX
   hurts data.
7. **Recovery-plan porch.** Valuable only if it stays brutally honest that it
   joins evidence and labels; it does not certify disaster recovery.
8. **Mesh membership/retirement plan.** Important for groups, but likely after
   pairwise stories are excellent.

These are deliberately not the features that make IoTox look most powerful.
They are the features that make the right thing easiest to do under stress.
