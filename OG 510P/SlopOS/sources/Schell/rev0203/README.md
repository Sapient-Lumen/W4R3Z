# Schell living archive

**North star:** see [`docs/00-meta/charter.md`](docs/00-meta/charter.md).

Revision notes: [`CHANGELOG.md`](CHANGELOG.md).

Schell is a **living archive** for designing a tightly integrated **shell + terminal** in **Rust** for **SlopOS**: explicit about authority, careful about side effects, durable across sessions, and disciplined enough to serve both interactive humans and automation.


This revision keeps the archive in **research mode** while making four bounded advances:

- it deepens the companion evaluation around SlopOS exact reviewed basis and explicit interpreter/startup-hook boundaries, plus ViewFS neighboring-state separation, Harbor label honesty, Ward revalidation pressure, Steward adaptation posture, Helm miss-ledger discipline, and Foundry actor/path caveat discipline so file-loading comfort never quietly becomes hidden shell truth,
- it converts current outside pressure from Bash, zsh, fish, PowerShell, and Nushell source / autoload / dot-source / module / overlay docs into a smaller synthesis centered on **source witnesses, import cards, and scope-mutation humility** rather than freezing one final module syntax, startup-file constitution, or compatibility importer too early,
- it adds `docs/80-terminal/source-witnesses-import-cards-and-scope-mutation-humility.md` so Schell can keep executed file, sourced file, autoloaded function, imported module/overlay, current-scope environment mutation, and exact reviewed basis visibly separate,
- and it refreshes the repo ledgers so the datacube remains hygienic and citable.
## How to navigate

1. Start-here briefing: [`START_HERE.md`](START_HERE.md)
2. Current source/import seam: [`docs/80-terminal/source-witnesses-import-cards-and-scope-mutation-humility.md`](docs/80-terminal/source-witnesses-import-cards-and-scope-mutation-humility.md)
3. Research synthesis, pass CC: [`docs/00-meta/research-synthesis-2026-03-24-pass-cc.md`](docs/00-meta/research-synthesis-2026-03-24-pass-cc.md)
4. SlopOS evaluation, pass CC: [`docs/00-meta/slopos-datacube-evaluation-pass-cc.md`](docs/00-meta/slopos-datacube-evaluation-pass-cc.md)
5. Current option/strictness seam: [`docs/80-terminal/option-witnesses-strictness-scopes-and-startup-mode-humility.md`](docs/80-terminal/option-witnesses-strictness-scopes-and-startup-mode-humility.md)
6. Research synthesis, pass CXCIX: [`docs/00-meta/research-synthesis-2026-03-24-pass-cxcix.md`](docs/00-meta/research-synthesis-2026-03-24-pass-cxcix.md)
7. SlopOS evaluation, pass CXCIX: [`docs/00-meta/slopos-datacube-evaluation-pass-cxcix.md`](docs/00-meta/slopos-datacube-evaluation-pass-cxcix.md)
8. Current substitution seam: [`docs/80-terminal/substitution-witnesses-capture-residue-and-helper-sidecar-humility.md`](docs/80-terminal/substitution-witnesses-capture-residue-and-helper-sidecar-humility.md)
9. Research synthesis, pass CXCVIII: [`docs/00-meta/research-synthesis-2026-03-24-pass-cxcviii.md`](docs/00-meta/research-synthesis-2026-03-24-pass-cxcviii.md)
10. SlopOS evaluation, pass CXCVIII: [`docs/00-meta/slopos-datacube-evaluation-pass-cxcviii.md`](docs/00-meta/slopos-datacube-evaluation-pass-cxcviii.md)
11. Current redirection seam: [`docs/80-terminal/redirection-witnesses-heredoc-cards-and-fd-lease-humility.md`](docs/80-terminal/redirection-witnesses-heredoc-cards-and-fd-lease-humility.md)
12. Repo hygiene + process: [`docs/00-meta/repo-hygiene-and-rust-process.md`](docs/00-meta/repo-hygiene-and-rust-process.md)
## Design stance


Schell is **not** just a nicer command prompt and **not** merely a terminal wrapper around a shell.
The working thesis is that a modern SlopOS operator surface should co-design shell and terminal together while still keeping their layers explicit, while also refusing the old habit of importing ambient startup/session magic by default:

- the shell owns reviewed action truth,
- the semantic transport carries boundaries and references,
- the terminal renders humane local UX,
- side effects stay legible before they happen,
- session lineage turns history into evidence,
- and transcript truth survives outside the fancy renderer.
- compact authority summaries should remain descriptive, not magical.
- strong actions should keep authorship and exact reviewed basis visible before execution.
- restored continuity should stay visibly restored until live truth is reacquired.
- attention hints should remain hints rather than completion proof or hidden authority.
- outside-world ingress should arrive as explicit packets rather than ambient text that silently inherits execution authority.
- visible selection should become an explicit packet family rather than a blur of highlight, hover, and accidental live-target promotion.
- rich pane trees should stay local view structure rather than silently becoming a portable PTY/session authority plane.
- rich output browsing should preserve explicit channel, provenance, and merge truth rather than pretending one renderer-local scrollback view is the universal transcript.
- visible-object actions should route through explicit intent packets and route witnesses instead of collapsing into generic smart-click helper behavior.
- progress, waiting-input, cancellation, draining cleanup, and completion should stay shell-owned exact state rather than spinner or prompt-return folklore.
- cwd, env/profile, activation, and namespace/view posture should become explicit execution-ground witnesses rather than prompt-hook magic, banner glow, or startup-session residue.
- environment layers should stay source-bearing and timing-bearing so inherited state, startup scripts, terminal injection, repo activation, overlays, and command-local overrides never collapse into one flattering ambient env story.
- outcome claims should stay source-bearing and aggregation-bearing so one prompt color, one `$?`, one chain-success boolean, or one imported completion badge never collapses exit, signal, stop, wait, and pipeline-member truth into one flattering result story.
- remote convenience should not blur peer identity, attach/resume posture, or borrowed-local authority; fresh connect, attach, resume, restore, and predictive local echo should stay visibly distinct.
- repair suggestions and exact handoff bundles should stay source-labeled and proposal-only until a new explicit review path is taken.
- visible objects should become typed object cards with explicit inspect, reveal, open, safe-open, insert, and attach ladders rather than one flattering click-to-do-whatever surface.
- transcript export and replay should stay exact, selective, redaction-visible, and clearly weaker than live authority or fresh review on current basis.
- repo-local smartness should arrive as visible accelerator packs with local trust leases, changed-basis reauthorization, and a separately named hook lane rather than ambient folder-open shell authorship.
- assistant conversation, plan mode, insert/review/run choices, and any stronger trusted-auto lanes should stay visibly distinct so AI help never becomes a second hidden shell.
- visible links should become explicit hyperlink witnesses before hover, preview, extraction, or history makes stronger claims than the shell actually knows.
- inline media and richer preview should hang off exact object/output witnesses, keep text-safe transcript stubs, and treat restored preview residue as historical rather than current truth.
- detector-driven affordances should hang off explicit detector witnesses with visible source/confidence posture and bounded action rails so regexes, quick fixes, and restored matches stay proposal-only until fresh review.
- ambient titles, badges, titlebar pills, status strips, and taskbar/dock progress should project exact shell-owned chrome witnesses with visible freshness and claim-strength posture rather than quietly becoming a second truth system.
- secret-bearing work should prefer refs, handles, and narrow materialization over literal reveal, and every history/transcript/clipboard/remote-peer sink should stay visibly distinct so masking never pretends plaintext residue does not matter.
- secure-input posture should stay visibly lease-shaped, scope-bearing, and release-aware so local keywatcher suppression never impersonates shell semantic certainty about what prompt or field is being answered.
- foreground tty claim, shell-tracked background work, detached continuity, and promoted supervised continuation should stay visibly distinct so prompt return and `&` folklore never masquerade as durable completion truth.
- interrupt, suspend, hangup severance, shell tracking drop, ignore-hangup folklore, detach, and durable promotion should stay visibly distinct so stop comfort never masquerades as one universal cancel/keep-running contract.
- failed-command recovery should preserve exact resolver truth and keep correction, install, docs lookup, and rerun as separately named offers so “helpful” repair never becomes stealth execution authority.
- shared observation, annotation, writable co-drive, browser join, service share, and evidence export should stay separately named collaboration seams so a helpful pairing surface never becomes ambient host authority on the guest or on the host.
- terminal/session capability posture should stay explicit so shell-known truth, local luxuries, adapted enhancement, and degraded fallback never collapse into terminal-brand folklore.
- terminal/session luxury should ship with explicit vetoes against hidden reparsing, spoofable metadata, heuristic open/execute jumps, and ambient input promotion so delight does not silently choose the architecture.
- provenance-first luxury should be the default import posture: semantic zones, suggestion engines, repo-local accelerators, recording surfaces, and typed routes should all declare source, exact object, claim strength, and the stronger act still kept separate.
- remembered, saved, restored, and provisional shell state should stay separately named so history hits, launch kits, resurrected rooms, and latency masks never impersonate current live footing.
- every continuity-facing object should advertise the strongest honest next verb it still supports so attach/reconnect/restore/rerun/relaunch/insert/inspect/start-clean stay distinct.
- typed pattern token, expansion family, current match set, no-match policy, literal override posture, and exact reviewed basis should stay separately named so brace rewrites, tilde rewrites, globs, and provider-side wildcard matching never quietly become hidden reviewed spend.
- typed recall token, cited source event, word/modifier selection, realized expanded line, re-edit posture, source locality, and exact reviewed basis should stay separately named so bang-history, argument reuse, prefix recall, and shared-history search never quietly become hidden reviewed spend.
- typed substitution token, helper footing, capture form, split/trim residue, sidecar lifetime, and exact reviewed basis should stay separately named so command substitution, process substitution, temp-file sidecars, scalar/array capture, and current-scope helper execution never quietly become hidden reviewed spend.
