':' // <<'null'
// ==UserScript==
// @name         qomrade
// @namespace    qomrade.local
// @version      0.18.40
// @description  Single-tab exact-prompt loop with non-scrolling transcript succession, visible context-item capture, and resilient background operation.
// @author       h0p3 and current/future qomrade officers
// @match        https://chatgpt.com/*
// @match        https://chat.openai.com/*
// @exclude      https://chatgpt.com/codex*
// @exclude      https://chat.openai.com/codex*
// @run-at       document-idle
// @sandbox      DOM
// @noframes
// @grant        GM_info
// @grant        GM_getTab
// @grant        GM_saveTab
// @grant        GM_registerMenuCommand
// @grant        GM_setClipboard
// @license      MIT
// ==/UserScript==
null
':' /*
# ============================================================================
# qomrade is one authoritative polyglot artifact.
#
# Tampermonkey runs the JavaScript. A sandperson runs this same file through
# Bash. The embedded workbench is standard-library first, extracts safely,
# understands arbitrary copied-and-pasted handoffs, carries tests and browser
# fixtures, and can split and rejoin the complete artifact byte-for-byte.
#
# Bare invocation is identity-first wake. The browser operator never needs
# this Bash surface and never needs a console.
# ============================================================================
set -euo pipefail
SELF="${BASH_SOURCE[0]:-$0}"
SELF="$(cd "$(dirname "$SELF")" && pwd)/$(basename "$SELF")"
NAME="$(basename "$SELF")"
TMP=""
cleanup_qomrade_() { [ -z "$TMP" ] || rm -rf "$TMP"; }
trap cleanup_qomrade_ EXIT INT TERM HUP
extract_bootstrap_() {
  [ -z "$TMP" ] || rm -rf "$TMP"
  TMP="$(mktemp -d "${TMPDIR:-/tmp}/qomrade-tool.XXXXXX")"
  python3 - "$SELF" "$TMP" <<'PY'
import base64, io, pathlib, re, sys, tarfile
source = pathlib.Path(sys.argv[1]).read_text(encoding='utf-8')
dest = pathlib.Path(sys.argv[2])
begin_marker = '/' + '*@QOMRADE-WORKBENCH-B64-BEGIN*' + '/'
end_marker = '/' + '*@QOMRADE-WORKBENCH-B64-END*' + '/'
a = source.find(begin_marker)
b = source.find(end_marker, a + 1)
if a < 0 or b < 0 or b <= a:
    raise SystemExit('qomrade: embedded workbench markers are missing')
rows = re.findall(r"'([A-Za-z0-9+/=]{20,})'", source[a:b])
if not rows:
    raise SystemExit('qomrade: embedded workbench has no base64 rows')
payload = base64.b64decode(''.join(rows), validate=True)
with tarfile.open(fileobj=io.BytesIO(payload), mode='r:gz') as archive:
    names = set()
    total = 0
    for member in archive.getmembers():
        path = pathlib.PurePosixPath(member.name)
        if member.name.startswith('/') or '..' in path.parts or member.name in names:
            raise SystemExit('qomrade: unsafe embedded member: ' + member.name)
        if not (member.isreg() or member.isdir()):
            raise SystemExit('qomrade: unsupported embedded member: ' + member.name)
        names.add(member.name)
        total += max(0, member.size)
        if total > 100 * 1024 * 1024:
            raise SystemExit('qomrade: embedded workbench expands beyond 100 MiB')
    try:
        archive.extractall(dest, members=archive.getmembers(), filter='data')
    except TypeError:
        # Python before tarfile's filter= API. Every member was already
        # path-normalized and allow-listed above.
        archive.extractall(dest, members=archive.getmembers())
PY
}
run_tool_() {
  extract_bootstrap_
  python3 "$TMP/tools/qomrade_tool.py" "$SELF" "$@"
}
cmd="${1:-wake}"
[ "$#" -eq 0 ] || shift
case "$cmd" in
  wake|doctor|map|chunk|extract|humpty|test|test-browser|handoff|surface|document|candidate|cloudtainer)
    run_tool_ "$cmd" "$@"
    ;;
  cnp)
    run_tool_ cnp "$@"
    ;;
  setup)
    dest="${1:-qomrade-workbench}"
    run_tool_ extract "$dest"
    printf 'workbench=%s\n' "$dest"
    printf 'next: bash %s doctor && bash %s test\n' "$NAME" "$NAME"
    ;;
  source-id)
    run_tool_ source-id
    ;;
  self-test)
    run_tool_ doctor
    run_tool_ test
    run_tool_ test-browser
    work="$(mktemp -d "${TMPDIR:-/tmp}/qomrade-humpty.XXXXXX")"
    run_tool_ humpty split "$work"
    run_tool_ humpty verify "$work"
    rm -rf "$work"
    printf 'QOMRADE_SELF_TEST=PASS\n'
    ;;
  ship)
    out="${1:-/mnt/user-data/outputs/qomrade.user.js}"
    run_tool_ doctor
    run_tool_ test
    run_tool_ test-browser
    mkdir -p "$(dirname "$out")"
    tmp_out="${out}.tmp.$$"
    cp "$SELF" "$tmp_out"
    cmp -s "$SELF" "$tmp_out" || { rm -f "$tmp_out"; printf 'qomrade: read-back differs; refusing ship\n' >&2; exit 1; }
    mv -f "$tmp_out" "$out"
    printf 'staged=%s\nQOMRADE_SHIP=PASS\n' "$out"
    ;;
  help|-h|--help)
    cat <<EOF
qomrade — one userscript for the operator, one workbench for the sandperson
  bash $NAME                     identity-first wake
  bash $NAME doctor              verify both halves, payload, identity, and sentinels
  bash $NAME test                dependency-free core tests
  bash $NAME test-browser        strongest available Chromium fixture tests
  bash $NAME handoff brief FILE  parse arbitrary copied-and-pasted qomrade output
  bash $NAME handoff faults FILE inspect structural pipeline-fault episodes and outcomes
  bash $NAME handoff background FILE inspect pre-trust recovery and foreground-hydration dependencies
  bash $NAME handoff control-plane FILE inspect panel, boot, persistence, and fleet control-plane liveness
  bash $NAME handoff barrier FILE inspect conversation-wide maximum-length terminal evidence
  bash $NAME handoff red-signals FILE inspect structural red/error evidence and authority
  bash $NAME handoff work FILE    inspect structural qCoT/tool-work leases and possible overlap
  bash $NAME handoff dogfooder FILE inspect historical Officer Loop handoffs (legacy parser only)
  bash $NAME surface brief FILE  parse an outside GlassTTY/surface-oracle report
  bash $NAME surface compare A B compare suspect and working surface reports
  bash $NAME document brief      read the embedded office, lineage, and sandperson protocol
  bash $NAME document office     print the current office capsule
  bash $NAME document heritage   print retained capabilities, scars, retired machinery, and deferred authority
  bash $NAME document dialogue   print the bounded classified operator/officer/sandperson conversation
  bash $NAME document history    print the bounded source lineage
  bash $NAME document protocol   print the complete-file succession protocol
  bash $NAME handoff SECTION F doctor|brief|wake|authenticity|barrier|red-signals|work|qcot|dogfooder|anchor|boots|footprint|control-plane|contradictions|models|reloads|recovery|background|faults|governor|outputs|custody|scheduler|notifications|surface|conversation|timeline|raw|compare|extract
  bash $NAME cnp FILE            auto-detect qomrade or outside surface CnP
  bash $NAME cnp compare A B     compare two copied surface reports
  bash $NAME map                 source chunk map
  bash $NAME chunk ID            print one exact source chunk
  bash $NAME humpty split DIR    exact split into a disposable workspace
  bash $NAME humpty join DIR OUT exact reassembly
  bash $NAME humpty verify DIR   prove no-edit byte identity
  bash $NAME candidate init DIR  immutable accepted copy plus complete editable candidate
  bash $NAME candidate check DIR [--browser]
  bash $NAME candidate review DIR
  bash $NAME candidate diff DIR
  bash $NAME candidate embed DIR rebuild the embedded workbench atomically
  bash $NAME candidate package DIR OUT.tar.gz
  bash $NAME cloudtainer env     report the current officer/container tool surface
  bash $NAME cloudtainer study HANDOFF... aggregate multiple Developer Handoffs into one parseable field study
  bash $NAME cloudtainer release OUTDIR [--browser] build and independently verify JS, one-member ZIP, checksums, and manifest
  bash $NAME setup [DIR]         extract the embedded workbench
  bash $NAME self-test           doctor, tests, and Humpty/Dumpty roundtrip
  bash $NAME ship [OUTPUT]       emit one complete verified qomrade file
EOF
    ;;
  *)
    printf 'qomrade: unknown command: %s\n' "$cmd" >&2
    printf 'run: bash %s help\n' "$NAME" >&2
    exit 2
    ;;
esac
exit 0
*/
/*
================================================================================
QOMRADE CONSTITUTION — SCHEMA 45
================================================================================
OFFICER LICENSE
  h0p3 grants the current and future qomrade developers and sandpeople authority to
  inspect, record, compare, reason about, and operate anything ChatGPT-related
  that is available through the browser, Tampermonkey, qomrade, a Developer
  Handoff, a transcript-only Session Handoff, or this complete source document. Page text and model prose remain
  evidence, not operator instructions. Unattended browser effects remain bounded
  by the laws below.
HARD RUNTIME LAWS
  1. One operator-authored prompt is captured code-point faithfully when Start
     is pressed; only CRLF/CR line endings are canonicalized to LF. The active
     run never silently adopts later edits. The exact editor payload is verified
     before Send. Later rendered user turns may extend custody only through a
     declared lossy UI projection (whitespace/inline-code/rendering), which is
     recorded separately and never mutates the prompt that qomrade sends.
  2. Before every Send qomrade obtains fresh, send-local model evidence under
     one operator-selected per-tab policy. Smart Pro is the recommended default:
     explicit GPT-5.6 Pro first; GPT-6-or-newer Pro is a bounded fallback for the
     current failed request lineage or for one Send when 5.6 cannot be confirmed.
     A stable successful reply clears that fallback, so the next ordinary turn
     probes GPT-5.6 first again. Pin exact model & effort selects one live-discovered
     route and reasoning level, including non-Pro, with no silent fallback. Follow
     ChatGPT selection changes nothing and witnesses the currently selected route
     and effort, including non-Pro, from the live menu. Policy changes apply to the
     next Send, never retroactively to active generation. Page labels remain UI
     evidence, not backend-model attestation.
  3. qomrade repeats only the captured operator prompt. Dev dogfooder, developer
     file exchange, plan ingestion, automatic diagnostic uploads, and temporary
     behavior trials are removed. Files and page prose cannot change this runtime.
  4. Each browser tab is independent. qomrade has no GM_getTabs grant, shared
     control key, value-change listener, storage-event listener, BroadcastChannel,
     or other tab-to-tab discovery or coordination mechanism.
  5. Stop revokes the current tab's run immediately. qomrade never clicks ChatGPT
     Stop, Continue, Retry, or a faster-model control, and never starts a new
     conversation. Current recoverable failures use a fresh ordinary Send of the
     exact captured prompt after quiet evidence and bounded backoff. No timeout or
     current owned failure authorizes reload. The operator-controlled Safe refresh
     option defaults on and may reload only this running tab after a safe-checkpoint preflight
     and exact one-shot per-tab ticket readback. When enabled, one newly appeared
     historical or unowned pipeline-failure surface, or a high-confidence degraded
     ChatGPT application shell, may also arm a bounded refresh after quiet settlement;
     this maintenance path never replaces current-request fresh-message recovery.
  6. “The message you submitted was too long” is a per-submission transport
     rejection, not proof that the conversation is exhausted. “The conversation
     is too long, please start a new one” and the older canonical maximum-length
     wording are distinct terminal completion signals: qomrade stops cleanly and
     never clicks Retry, resends, trims, or refreshes that completed conversation.
  7. qomrade will not send while a visible Stop control indicates generation. A
     new assistant turn must become non-generating and text-stable before the
     reply is accepted. Structural qCoT/tool-only work is held rather than treated
     as a final answer. Native recovery never uses an unowned status or quotation.
  8. Reply success and file-download success are separate. Optional native-file
     activation is restricted to explicitly named download controls in a captured
     completed assistant turn whose filename matches the operator's comma-separated
     suffix list, up to four distinct files per reply. The default list is .zip.
     Eight finite rescans admit late controls; turn-bound custody prevents replay.
     Preview, prose, arbitrary actions and unnamed controls are not download authority.
     In particular, an ordinary assistant-authored hyperlink is never clicked merely
     because its URL or text ends in a configured suffix; native file semantics must
     be explicit. Generic submit controls are likewise scoped to the exact composer
     shell whose draft qomrade verified.
  9. The browser controller is low-churn: no recurring timer while stopped, no
     persistent page-wide MutationObserver, no PerformanceObserver, no keep-awake
     audio, no page-global network monkeypatch, and no hidden-tab polling when
     hidden pause is enabled. Temporary bounded MutationObservers may exist only during the exact model-menu hydration wait or a just-activated file-notification watch; each is disconnected on every exit. Session Handoff export never scrolls the conversation or installs a history-sweep observer.
     Background operation is the default, not a guarantee against browser suspension.
 10. Only small settings plus bounded evidence-only continuity are persisted
     through per-tab GM_getTab/GM_saveTab. Prompt envelopes, complete replies,
     full DOM, and Developer Handoffs are never persisted automatically; continuity
     never resumes automation or authorizes Send. Only a separate verified, armed,
     source/conversation/prompt-bound one-shot recovery ticket can resume observation
     of its already-submitted request; Stop/Pause cancel pending recovery.
 11. Copy Developer Handoff is explicit, on-demand work. Its v2 envelope is
     amnesia-first: readMeFirst states the current situation and read order,
     incidentIndex names the consequential incidents, timeline normalizes their
     chronology, evidenceCatalog points to canonical evidence, and the legacy deep
     sections remain available for exact inspection. Routine ticks never serialize
     the complete document, but selected odd-event edges may preserve a bounded
     DOMish scene before the surface disappears.
 12. One complete qomrade.user.js remains the installable source of truth. It
     retains the current Bash workbench, tests, living office and lineage. Exact
     retired releases live in the separately delivered developer kit, not
     recursively inside the browser payload. A sandperson reads the office and
     the appropriate handoff, revises a complete candidate, updates the living
     prose and bounded lineage, runs doctor and tests, and returns the complete
     file rather than only a patch.
     Packaging is bounded at 1 MiB and 12,000 lines; a build must fail rather than
     silently erase history or embed complete parent releases again.
 13. The office capsule is the ongoing conversation between operator and
     sandpeople: accepted evidence, current design, lessons, open questions, next
     action, hard holds, and operator instructions. Stable lessons become laws,
     adapter contracts, tests, or bounded lineage entries.
 14. Consequential claims remain distinguishable as operator request, inherited
     intent, measured fact, inference, proposal, or unknown. No category silently
     becomes another.
 15. Surface adapters follow semantic attributes for both classic conversation
     turns and ChatGPT's virtualized search/group representation. Selector drift
     causes a visible hold; it never authorizes speculative clicks or page surgery.
 16. Scripted composer input, Send, ZIP activation, and the panel host are
     technically observable. qomrade does not spoof trusted events, fingerprints,
     or human behavior and does not claim invisibility.
 17. Observability is evidence, not control authority. Bounded action receipts,
     lifecycle/error listeners, scheduler metrics, and a small per-tab continuity
     capsule may record what happened. They never coordinate tabs or resume a run.
 18. The exact operator-defined hard false surface—no history plus a visible 5.3
     model—quarantines this page before Send. The panel becomes inert but retains
     explicit diagnostic and Developer Handoff custody.
 19. Explicit handoff may perform expensive bounded probes, including resource
     timing and structural DOM inventories. No such probe runs on a stopped timer.
 20. A completed send transaction leaves active control custody immediately and is
     retained as a bounded receipt. Session Handoff and Flight Recorder are explicit
     local downloads. Developer Handoff is an explicit clipboard copy for qomrade
     development. Session Handoff contains only the observed ChatGPT conversation
     transcript; it contains no qomrade diagnosis, authored brief, inferred objective,
     model policy, or maintenance state. None is pasted into the ChatGPT composer or
     treated as automation authority.
 21. Operator focus inside qomrade belongs to the operator. The panel lives in a
     separate local iframe so ChatGPT document handlers cannot reinterpret its
     events through Shadow-DOM retargeting. The iframe is assembled through direct
     DOM node creation; qomrade never calls its document.open, write, or writeln.
     While a qomrade text or number editor has focus, qomrade defers composer focus
     and Send until that editor releases it.
 22. Bounded pipeline science is active only while this tab's loop is running.
     It records change edges among generation, newest assistant ownership,
     structural work, continuation/retry/error surfaces, effort/model indicators,
     scheduler lateness, and compact system notices. Consequential odd edges—first
     fault observation, changed Retry/pipeline cards, missing model or composer
     surfaces before an authorized Send, healing-refresh arming, terminal/halt
     boundaries, and qomrade page errors—may capture a bounded DOMish scene containing
     roots, ancestry, siblings, attributes, exact-or-hashed text, markup head/tail,
     a shallow subtree, turn context, and shell inventory. It never polls while
     stopped, coordinates tabs, monkeypatches page APIs, or promotes observation into
     authority without a class-specific law.
 23. Composer insertion is a witnessed transaction, not a blind DOM write. qomrade
     uses a structured ProseMirror reader, removes only editor-irrelevant terminal
     newlines from the insertion payload, records every bounded insertion attempt,
     and rechecks the thread after each attempt and before Send. If a matching user
     turn or generation appears before qomrade clicks Send, qomrade suppresses the
     click, adopts only a conservatively matching turn, and otherwise halts in an
     explicit no-resend custody state.
 24. A pending browser-effect transaction holds one immutable, same-tab epoch.
     Stop, Pause, a new Start, pagehide, hidden-tab pause and active panel editing
     revoke its authority. Every asynchronous continuation checks its own epoch;
     it cannot borrow permission from a newer run. Final model, composer, fault,
     work, generation and Send-control checks occur after the last settlement
     wait, with no await between the final check and the Send click. Revocation
     never clears surviving draft text or resurrects cancelled recovery.
 25. Repeated turn-text reads may share a cache only within one synchronous
     observation. They never share text across an await, timer, input or Send.
     Synchronous probe costs and awaited controller wall time are different
     measurements. Nested inclusive costs must not be summed or called CPU time.
     The document may grow while live observation remains conditional and quiet.
 26. A collapsed or effort-only model indicator does not erase this Send
     operation's freshly confirmed route and effort. The final commit may carry
     Smart-Pro, pinned, or follow-current proof for up to 60 seconds only within
     the same revocable operation, same conversation and connected model control,
     without new control interaction or contradictory route/effort evidence. It
     never borrows historical or restored confirmation. This is local UI evidence,
     not a claim about backend model identity.
 27. The operator-selected recovery action for a current owned failure is a new
     message containing the exact captured operator prompt. Do not activate ChatGPT
     Retry. Current-request failure recovery neither requires nor automatically
     performs a reload. A newer stable user turn
     that exactly renders the captured prompt, with no different intervening user,
     becomes the active successor request. Its red-letter failure may fire the
     next fresh prompt; unchanged old errors cannot multiply new messages.
 28. Keep the same prompt, conversation, successor lineage, operator draft,
     active generation, dialog, continuation, model and cancellation checks through
     the final synchronous Send commit. When the owned response itself has a
     terminal red-letter failure, preserve its partial answer, work and ZIP evidence
     but do not let those remnants become completion or overlap authority. Preserve
     the superseded request as a receipt and never claim qomrade sent an externally
     observed exact successor. A cleared or changed failure invalidates the resend
     permit. A GUI error never proves prior backend termination; a fresh message
     may duplicate that prior work.
 29. Distinguish a model popup advertising open from usable menu content. Close
     and reopen its incomplete shell with bounded, revocable interactions. Failed
     hydration rechecks after 15 seconds or on visibility return; never substitute
     a placeholder or old confirmation for the live route-and-effort evidence
     required by the active operator-selected model policy.
 30. Keep the evidence surfaces distinct. Session Handoff is a transcript-only copy
     of the observed ChatGPT context river for the next tab. Developer Handoff carries
     qomrade forensic state. Flight Recorder is the compact operational first look.
     Their filenames, schemas, UI controls, and prose must not blur these roles.
 31. The session recorder captures materialized user and assistant turns across
     explicit Starts in the same conversation, before optional DOM trimming and
     before any operator-enabled safe refresh. The export presents those turns in conversation
     order without a synthetic summary or continuation prompt. It is bounded, carries
     a neutral capture note for omissions, and never claims to be a server transcript.
     A refresh may proceed only after the exact bounded archive ticket is read back.
 32. Maintenance recommendations are advice only. They may suggest an interval or
     optional trimming, but never alter settings. Safe-refresh cadence is an exact
     per-tab integer from 5 through 1,440 minutes. New installs default to a
     30-minute turn gap and background work; existing explicit per-tab settings
     remain operator-owned.
 33. With Safe refresh enabled, a newly appeared historical or unowned pipeline
     failure—such as an old-message Retry control or terminal error surface outside
     current request custody—may arm one early refresh after 15 seconds of stable
     evidence. The refresh keeps exact source/conversation/prompt ticket custody,
     treats a missing composer as evidence of a broken page only in this narrow mode,
     and remains blocked by generation, drafts, attachments, dialogs, continuation,
     route changes, terminal completion, or current-request recovery. The same
     surface is deduplicated for 30 minutes and no more than two such healing
     refreshes may commit in an hour. qomrade never clicks the observed Retry.
 34. DOMish forensics are evidence capsules, not a hidden continuous observer. The
     buffer is finite by snapshot count, bytes, roots, nodes, depth, text and markup.
     Each snapshot has a stable ID and trigger, may be referenced from incidents and
     timeline records, and is carried only through an exact Safe-refresh ticket within
     its smaller persistence budget. Dropped or truncated evidence is counted and
     stated; no snapshot authorizes Send, Retry, reload, model selection, or DOM edits.
 35. The exact ChatGPT maintenance notice “The conversation is stale, please
     reload and try again” is a page-shell condition, not a generation fault. With
     Safe refresh enabled it may authorize one exact-ticket healing refresh even while
     request custody is preserved, after quiet settlement and every existing draft,
     generation, dialog, route, terminal, dedup, budget, and cancellation guard. It
     never authorizes Retry or a fresh prompt. Current typed request failure takes
     priority and cancels that maintenance action.
 36. Developer Handoff normalizes live pipeline-surface edges with equivalent evidence
     restored inside retained DOMish snapshots. A Retry control that belongs to a
     known terminal conversation barrier is expected terminal UI, not an unexplained
     warning. DOMish related roots should add turn/shell context and skip empty clipped
     live regions when they provide no forensic value.
 37. Prompt transport and rendered-text comparison are separate. The transport
     preserves every operator code point except CRLF/CR-to-LF canonicalization and
     the longstanding explicit removal of terminal editor newlines. A lossy rendered
     projection may identify qomrade's own user turn, but it is recorded as projection
     evidence and never becomes the payload for a later Send.
 38. Per-tab persistence is one serialized channel. Recovery barriers, Safe-refresh
     barriers, ordinary continuity writes, and late GM_getTab adoption cannot overwrite
     one another. A timed-out read remains adoptable only until the operator edits or
     Starts; a Safe-refresh restore that cannot rematerialize exact request custody
     reaches a bounded visible stop rather than waiting forever.
 39. Every consequential Send enforces cadence twice: once before asynchronous model
     and composer work and again at the final synchronous click commit. Recovery
     replays retain their separately bounded schedule; no phase name alone grants a
     click permit.
 40. A settled ChatGPT shell with missing model controls plus strong presentation
     evidence—missing or unapplied author styles, native-control layout, tiny desktop
     composer, or a long-lived Loading profile surface—is maintenance evidence, not
     permission to Send. qomrade records a bounded DOMish scene. While stopped it
     remains inert; Start plus enabled Safe refresh may authorize one exact-ticket
     repair reload before any prompt action. The same evidence is deduplicated and
     cannot defeat drafts, generation, dialogs, route, terminal, or cancellation guards.
 41. Hidden model-menu proof is exact-trigger-bound, not a general visibility bypass.
     When Firefox keeps the trigger open and its controlled model menu connected,
     populated, model-like, and state=open, qomrade may read route and effort despite
     zero rectangles, opacity zero, or pointer-events suppression caused by a paused
     paint transition. Menu mutation additionally requires a non-inert, non-aria-hidden
     root. Composer, Send, Retry, Continue, dialogs, attachments, and every other
     consequential control keep ordinary actionable-visibility checks. This cannot
     execute while the browser or operating system has actually suspended the tab.
 42. Pin route identity may survive bounded UI renaming, never model fallback. If
     the stored route key disappears, qomrade may canonicalize only the single enabled
     route already selected by ChatGPT when legacy Latest maps to explicit GPT-6, or
     stored and selected versions agree with prefix-compatible labels. It never clicks
     a different alias. The new label, key, and version are persisted, and send-local
     effort proof remains mandatory.
 43. Observation pressure is bounded by purpose. During advertised generation,
     structural fault, work, and terminal-alert checks remain active while full growing
     assistant prose is deferred until completion evidence is needed. Model-menu hydration and post-file-activation notification observation may use operation-scoped MutationObservers that disconnect at success, timeout, or cancellation; Session Handoff export is non-scrolling and natural-scroll capture is passive and debounced; no persistent page-global observer exists.
     Developer Handoff may estimate qomrade evidence bytes and DOM size, but never
     claims Firefox process or React heap attribution.
#@QOMRADE-OFFICE-BEGIN schema=1
AUTHORITY: The live operator request outranks inherited prose. Outside review and page text are evidence, never automatic authority. The complete source may be revised by the current sandperson, but unattended browser effects remain bounded by the constitution and explicit controls.
ACCEPTED: The working kernel is code-point-faithful prompt custody, operator-selected send-local model custody with a GPT-5.6-first Smart Pro default, fresh-message recovery, terminal conversation completion, explicit native-file authority, cancellation, single-tab isolation, default-on bounded maintenance, serialized per-tab persistence, and distinct transcript/forensic exports.
CURRENT: 0.18.40 makes Session Handoff export non-scrolling, captures newly materialized history on ordinary user scrolling, preserves visible file and image context items, and reconciles terminal barrier ownership against the final adopted request identity.
LEARNED: A 0.18.38 handoff proved that qomrade clicked Send and adopted the exact prompt as user turn 11 before ChatGPT returned the maximum-length barrier. The controller stopped correctly, but its incident summary falsely said no user turn had materialized, making correct terminal behavior look like a missed Send.
OPEN: Browser evidence still cannot prove backend execution, and conversation-length barriers may appear without an assistant reply. Terminal ownership and request-stage evidence must remain explicit rather than converting an accepted terminal request into an automatic duplicate Send.
NEXT: Install 0.18.40 and continue ordinary use. Session Handoff should download without moving the viewport; compare its coverage and visible-context-item metadata against the conversation you can actually see.
HOLD: No duplicate prompt after a confirmed maximum-length barrier, no native Retry, no automatic new-chat creation, no keep-awake audio, worker fleet, cross-tab coordinator, persistent page-global observer, general invisible-control bypass, automatic setting changes, or un-ticketed run restoration.
OPERATOR: An empty ChatGPT composer after Send is not evidence of a missed turn. qomrade now says when the exact prompt became a real user turn before terminal completion; the 30-minute default and background work remain, alongside Smart Pro, Pin, Follow, transcript-only Session Handoff, clipboard Developer Handoff, and compact Flight Recorder.
#@QOMRADE-OFFICE-END
#@QOMRADE-HERITAGE-BEGIN schema=1
RUNTIME_KEEP: code-point-faithful prompt transport; declared rendered-text projection; exact-successor request custody; latest-only Start receipt; structured composer adapter; pre-click duplicate prevention; hard final cadence gate; operator-selected model policy with Smart-Pro default, exact pin and follow-current modes; selected-route-only pinned-label reconciliation with persisted canonical identity; exact-trigger-controlled paint-independent hidden model-menu proof; bounded operation-scoped model-menu hydration observation; low-churn generation-time assistant observation; truthful scheduling; fresh-message fault recovery; terminal conversation completion with accepted-user-turn stage evidence; ZIP custody; serialized per-tab persistence; bounded late-read adoption; bounded refresh-restore deadline; single-tab quarantine; event-isolated panel; bounded DOM trimming; safe-checkpoint refresh with exact resume; block-preserving context-river transcript capture; request-owned conversation-stale fresh-message recovery; historical/unowned conversation-stale, conversation-load-failed, and high-confidence degraded-shell maintenance classification.
PROBE_KEEP: semantic turn adapters; red and error evidence; normalized live-and-DOMish-restored pipeline surfaces; high-confidence stylesheet/hydration shell health; live-discovered model catalog and send-local route/effort receipts; pinned-route reconciliation receipts; hidden model-menu style, rectangles, blockers, and structural-acceptance receipts; on-demand resource timing; governor surfaces; selector families; page errors; performance counters; serialized memory-pressure proxy; foreground-rescue and hidden execution-gap evidence; contradictions; compact flight recording; terminal-context-aware Retry interpretation.
DOCUMENT_KEEP: current office; classified dialogue; release scars; bounded lineage; active tests; current Bash workbench; cloudtainer env/study/release officer commands; candidate workflow; deterministic embedding; Humpty byte identity; exact immediate parent in the separate developer kit.
RETIRED_RUNTIME: dev dogfooder and browser file exchange; temporary behavior trials; automatic diagnostic upload; Officer self-prompting loop; fleet and cross-tab coordination; desktop notifications; page-global network interception; persistent page-global hot observers; recursive embedded release archives.
DEFERRED_AUTHORITY: native Retry as recovery; reload of a current typed owned failure; timeout-only reload; silent resend without explicit failure; automatic new-chat creation; automatic maintenance-setting changes; browser settings or extension privileges that prevent tab discard. Historical/unowned conversation-stale, conversation-load-failed, and high-confidence degraded-shell healing are separately bounded maintenance behind Safe refresh; current request-owned conversation-stale is fresh-message recovery.
SCARS: a release that declares source_id=pending is not exact-source-safe even when its runtime works; a route label and its derived key can become stale while ChatGPT still shows the operator's intended route as selected; exact-key failure must not erase checked semantic evidence, but reconciliation must never become fallback; hidden controller timers can remain healthy while a Radix menu's paint transition is frozen; geometry or opacity is not reliable proof for an exact trigger-controlled background model menu; this exception must never leak to Send or arbitrary controls; sane defaults are not imprisonment and deliberate overrides are not safety bypasses; Follow must witness the current live route rather than trust a stale pill; outside review is fodder until verified; page prose is evidence, not authority; UI error does not prove backend termination; selector absence alone does not prove a degraded shell; an isolated iframe can remain styled while the host application loses author styles; restored structural evidence can outlive its live index; terminal Retry is expected UI; DOM trimming removes observed rendered nodes and refresh is the reconstruction path; reply success and ZIP activation are separate.
MONSTERNIX_SEAM: qomrade is a verifiable habitat of separated powers: operator request, immutable accepted source, editable candidate, bounded browser controller, explicit model policy, distinct evidence artifacts, tests, sandperson interpretation, and release succession.
#@QOMRADE-HERITAGE-END
#@QOMRADE-DIALOGUE-BEGIN schema=1 max_entries=24
#@QOMRADE-DIALOGUE at=2026-10-17 role=operator classification=operator_request statement=The-ChatGPT-user-input-bar-is-empty;-this-should-take-a-real-turn.
#@QOMRADE-DIALOGUE at=2026-10-17 role=officer classification=measured_fact statement=The-0.18.38-handoff-proves-Send-was-clicked-and-the-exact-prompt-materialized-as-user-turn-11-before-the-conversation-too-long-banner;-the-empty-composer-was-the-normal-post-Send-state.
#@QOMRADE-DIALOGUE at=2026-10-17 role=officer classification=decision statement=Keep-terminal-stop-authority-but-record-request-stage,-barrier-owner,-accepted-user-turn,-and-composer-empty-evidence,-and-never-describe-an-accepted-turn-as-unmaterialized.
#@QOMRADE-DIALOGUE at=2026-10-11 role=operator classification=operator_request statement=Ordinary-use-is-now-boring-and-mundane-in-a-good-way;-make-the-bottom-anchored-panel-about-one-third-taller,-allow-an-exact-refresh-interval,-and-keep-improving-observability-and-cloudtainer-CLI-tools-for-the-officer.
#@QOMRADE-DIALOGUE at=2026-10-11 role=officer classification=measured_fact statement=Five-0.18.35-Developer-Handoffs-were-running-in-WAITING_REPLY-with-healthy-composer-and-model-shells,-but-every-one-declared-source_id=pending;-several-current-orientation-records-also-showed-only-the-collapsed-Pro-pill-while-the-active-transaction-retained-concrete-send-local-model-proof.
#@QOMRADE-DIALOGUE at=2026-10-11 role=officer classification=decision statement=Reserve-ChatGPT-top-strip-clearance-while-expanding-the-panel,-replace-the-refresh-preset-select-with-a-bounded-integer-input,-surface-active-request-model-and-operator-settings-in-readMeFirst,-restore-exact-source-identity,-and-add-cloudtainer-env-study-release-commands-with-tests.
#@QOMRADE-DIALOGUE at=2026-10-11 role=operator classification=operator_request statement=Red-team-qomrade-for-outside-the-box-flaws.
#@QOMRADE-DIALOGUE at=2026-10-11 role=officer classification=measured_fact statement=The-0.18.34-delivery-evidence-was-internally-contradictory,-and-ordinary-prose-links-plus-page-wide-generic-submit-fallbacks-had-more-authority-than-intended.
#@QOMRADE-DIALOGUE at=2026-10-11 role=officer classification=decision statement=Require-explicit-native-file-authority,-prioritize-real-file-controls-before-prose-links,-scope-generic-submit-to-the-owned-composer,-and-require-independent-package-readback.
#@QOMRADE-DIALOGUE at=2026-10-11 role=operator classification=operator_request statement=Smart-Pro-used-GPT-6-after-a-prior-failure-and-file-downloading-needed-configurable-comma-separated-suffixes-with-.zip-on-by-default.
#@QOMRADE-DIALOGUE at=2026-10-11 role=officer classification=measured_fact statement=The-field-handoff-retained-6-fallback-after-earlier-5.6-failure-and-preserved-the-previously-unclassified-Message-delivery-timed-out-surface.
#@QOMRADE-DIALOGUE at=2026-10-11 role=officer classification=decision statement=Keep-GPT-6-only-through-the-unresolved-failed-lineage,-clear-Smart-Pro-back-to-5.6-after-stable-success,-classify-message-delivery-timeout-for-fresh-message-recovery,-and-add-bounded-native-file-suffix-configuration.
#@QOMRADE-DIALOGUE at=2026-10-08 role=operator classification=operator_request statement=Continue-research-on-Firefox-inactive-tab-operation,-RAM-pressure,-and-any-useful-observability-improvements.
#@QOMRADE-DIALOGUE at=2026-10-08 role=officer classification=measured_fact statement=Field-handoffs-proved-real-hidden-Sends-and-file-activations-but-also-showed-tens-of-millions-of-repeated-assistant-text-characters,-large-survey-retention,-and-occasional-long-hidden-callback-gaps.
#@QOMRADE-DIALOGUE at=2026-10-08 role=officer classification=decision statement=Defer-full-growing-assistant-prose-during-advertised-generation,-compact-model-surveys,-use-one-operation-scoped-menu-mutation-wait,-coalesce-repeated-page-errors,-and-export-memory-navigation-rescue-and-hidden-gap-evidence.
#@QOMRADE-DIALOGUE-END
#@QOMRADE-HISTORY-BEGIN schema=1 max_entries=64
#@QOMRADE-HISTORY version=0.8.0 source=a86565d34bcc0cd077537697db85b35483d487d6279a3abb29ebf2454289cc85 closed=contextual-generic-zip-controls-stable-conversation-anchor-and-typed-capacity-deferral-sensing
#@QOMRADE-HISTORY version=0.9.0 source=613ae40e06949b42411e5cf5744d16b33a3947d372dfc205dafc3bb883ec000b closed=provenance-gated-deferral-explicit-ghost-retry-soft-history-hold-bounded-no-turn-reloads-durable-zip-ledger-and-late-control-science
#@QOMRADE-HISTORY version=0.10.0 source=4c37cc16b2d79aa546bd29ab3f509ace7a94f51c7892af95c628b1a106a9317d closed=terminal-only-deduplicated-desktop-notification-authority-and-handoff-observability
#@QOMRADE-HISTORY version=0.10.1 source=a59dbf5f11ca617c957c238beeead3060917f09b744576901a5163bccc579be1 closed=removed-desktop-notification-grant-and-delivery-capability-added-passive-page-notification-attribution
#@QOMRADE-HISTORY version=0.10.2 source=1ab3e54a2fe5a6218ad75e2cc2b51d71449f6ded194190ab2f3833d43f11cc99 closed=chat-route-scope-codex-exclusion-silent-bootstrap-and-stale-fleet-attribution
#@QOMRADE-HISTORY version=0.11.0 source=4c185f42b33b7b07019022aab9a0770e487858d980d61fcd95d9d6e72e05ba1f closed=structural-assistant-pipeline-fault-sensing-bounded-reload-science-confirmed-exact-resend-and-long-horizon-fault-ledger
#@QOMRADE-HISTORY version=0.12.0 source=5db997de368f1172973d77f14d9b6174ba46914f35474258eb28e592500d4c55 closed=conversation-wide-maximum-length-barrier-red-signal-science-pre-send-interlock-and-immediate-separate-stop-control
#@QOMRADE-HISTORY version=0.13.0 source=5d28ae5dee6a04210ae3c146024a6291564da310a2d93843a84ecf0c89487ece closed=structural-qcot-work-leases-overlap-halt-and-no-resend-after-qcot-disappearance
#@QOMRADE-HISTORY version=0.14.0 source=96c25a2a9fb02b5d932791c5cf246e54dc5c57eb605fbd6b55d0e7ff7fdebd6b closed=canonical-network-error-native-thread-retry-pretrust-reload-recovery-and-foreground-hydration-science
#@QOMRADE-HISTORY version=0.14.1 source=97631db5fe15b793b2a609c32eea1eed15a5c695f7eeb035f594b9b01a43e8e6 closed=observable-start-receipts-recoverable-halt-resume-conversation-scoped-work-leases-and-persistence-independent-controller-start
#@QOMRADE-HISTORY version=0.14.2 source=63c82c701c9a5ef62a472f9ed849b0bdd7fa265b40c8fa0e1c72570d568d3049 closed=null-safe-stopped-state-work-lease-snapshot-named-qcot-refusal-and-measured-panel-load-preservation
#@QOMRADE-HISTORY version=0.14.3 source=983e456ae346e3a37b54dbed4e574293cf6a5be44bf03810b06f11b3142b2878 closed=passive-readable-conversation-panel-hidden-bootstrap-backoff-lifecycle-wakeup-host-connectivity-and-fleet-boot-truth
#@QOMRADE-HISTORY version=0.14.4 source=6a0923203b8eb7cc0a53e29c33ecc124757dbdced9721c0327a3ef89b639e70e closed=nonblocking-boot-persistence-full-trust-first-panel-promotion-lifecycle-reconciliation-and-persisted-fleet-control-plane-truth
#@QOMRADE-HISTORY version=0.14.5 source=3b6d6654717d46e0aa1974fe7aad83ae5ff0e4d2e08c7aaea2464effeeb095f7 closed=recoverable-qcot-work-hold-stalled-canonical-shell-diagnostic-panel-and-compact-fleet-control-plane-summary
#@QOMRADE-HISTORY version=0.14.6 source=fa95b9d9c4acb2cf9afd11dd5146733fbcade8e9638c920a66380d7c66a6a46a closed=readable-turn-native-fault-retry-bounded-repeat-and-nonterminal-rolling-qcot-reload-science
#@QOMRADE-HISTORY version=0.15.0 source=41a7ef5f4c1cddcc2c459fd6ae932695f92d1754e4ffb97c823e564db3547d45 closed=separate-dogfooder-officer-loop-turn-local-self-prompt-files-bounded-evidence-and-declarative-contingent-machinery
#@QOMRADE-HISTORY version=0.15.1 source=2b82a402d00ab336ed38eac3a7127e4ef4153d93a285bc970e57900b5f3baed9 closed=bounded-GM-getTab-fail-open-state-restore-and-zero-authority-bootstrap-fallback
#@QOMRADE-HISTORY version=0.15.2 source=be67fc31e91ba3e29fdf4d76070991f723632375cc124ccd9b6d3341899e232a closed=dual-classic-and-virtualized-search-dom-adapters-truthful-history-turn-composer-and-visible-model-sensing
#@QOMRADE-HISTORY version=0.16.0 source=1233302c6cdba4a2ba6b59506b91629cec21ebf3e559ea60720bee0def169757 closed=single-tab-low-churn-runtime-with-dogfooder-fleet-reload-and-large-handoff-removal
#@QOMRADE-HISTORY version=0.17.0 source=4bd3e13a995e67404d600f4ee93b49f2eac7ead368f5630d89ebed26942b8096 closed=restored-polyglot-bash-workbench-office-lineage-and-on-demand-handoff-around-single-tab-no-dogfooder-no-fleet-runtime
#@QOMRADE-HISTORY version=0.17.1 source=551ce6f81153caac8bbf471388011597db93b621dd7fff5ed6f821ee3abf7b70 closed=bounded-forensic-observability-action-receipts-authenticity-barrier-red-dialog-continuation-work-resource-selector-and-timer-evidence-without-hot-observers-or-cross-tab-work
#@QOMRADE-HISTORY version=0.17.2 source=9c4bf275440b5d83b18015e924c7e8f875894fe06f489a443c32eee865c5fcff closed=completed-transaction-custody-adaptive-hidden-cadence-light-authenticity-global-continue-text-retry-file-handoff-zip-isolation-and-exact-bounded-diagnostics
#@QOMRADE-HISTORY version=0.17.3 source=955a975c69d3679c82ba38a0cf3003a68650694ea379d92ab02edb8743b68aef closed=event-isolated-iframe-panel-shadow-retargeting-removal-and-operator-editor-focus-custody
#@QOMRADE-HISTORY version=0.17.4 source=c79cd65d653e400ad36d88951c9c21f0eed60181fad358954d1feeaad74765fb closed=firefox-extension-sandbox-safe-direct-DOM-iframe-mount-menu-first-boot-and-visible-panel-failure-custody
#@QOMRADE-HISTORY version=0.18.0 source=45ee5539ec49d186dd096358667f923d502e28be69de0f39d25eb7e75418c2f6 closed=automatic-newest-eligible-Pro-gate-active-only-change-edge-science-and-explicit-heritage-dialogue-memory-without-fleet-or-Dogfooder
#@QOMRADE-HISTORY version=0.18.1 source=4aa41ca9144695811e9c366756514835bbe1965740f4fb34a341a04e6d912f2d closed=structured-ProseMirror-terminal-newline-custody-per-method-insertion-receipts-pre-click-thread-advance-no-resend-adoption-and-single-menu-selected-route-confirmation
#@QOMRADE-HISTORY version=0.18.2 source=20771cd85e667bd396d45065b36c686e9e2f9778e8c9222ae2e522c894ed84b6 closed=typed-input-stream-and-thinking-faults-bounded-incident-custody-and-stopped-on-demand-observability
#@QOMRADE-HISTORY version=0.18.3 source=40327307d3b19803f7b49544dfa22031ea8a014374c3039222cd8743be22acc2 closed=revocable-async-effects-atomic-send-commit-synchronous-read-reuse-and-work-science-contract-repair
#@QOMRADE-HISTORY version=0.18.4 source=2a0a84e9c4e7266f9710c0bd71643da75d44beab1f707cd9f8d1e3e475e1f791 closed=send-local-model-proof-through-collapsed-Pro;-field-shaped-replay;-retained-cancellation;-explicit-recovery-branch-archive
#@QOMRADE-HISTORY version=0.18.5 source=6775d80e4e40ada2ebef0bad6eb1e53429ec53a0f442f12d48a695bb3e7ae195 closed=merged-real-0.18.2-recovery-with-0.18.4-cancellation-and-model-proof;stable-request-ID-promotion;post-reload-bounded-exact-restart
#@QOMRADE-HISTORY version=0.18.6 source=e4aecbd0570909d229f1287d22573b974df919115d29283ded9fe2e31f57e91a closed=off-by-default-page-local-file-experiments;typed-read-only-plans;bounded-inspection;no-hot-swap;truthful-download-receipts
#@QOMRADE-HISTORY version=0.18.7 source=8c2f76a868b8a6d04dfa9676315d5ea7ca7b7c46572ab8fd46f2627abbeea704 closed=finite-cached-observations;freshness-and-decision-evidence;three-file-correlation;retained-controller-and-complete-parent
#@QOMRADE-HISTORY version=0.18.8 source=292ef1d52341c2cd167eacd3a40f926f5fe50e2735b1cc86e6736dc35b7909c2 closed=background-default-migration;semantic-turn-bound-zip-capture;finite-rescans;reversible-target-bound-behavior-trials;retained-parent-and-custody
#@QOMRADE-HISTORY version=0.18.9 source=b8c3e7d8dda630007199d6b970e4f6c61a4ce496272c5c322faecaa4e2fe7df3 closed=finite-checkbox-dev-dogfooder;file-only-telemetry;target-bound-plan-mirrors;multi-step-behavior-trials;manual-release-install;exact-parent-retained
#@QOMRADE-HISTORY version=0.18.10 source=ce14fa3d73f5e11c95668fbfd54d6669fb1c3f6e2ab5db66f8fc88ecdd85c7e0 closed=field-shaped-hover-hidden-named-attachment-acknowledgement;exact-file-custody;compact-readiness-edges;retained-file-cycle-and-final-send-interlocks
#@QOMRADE-HISTORY version=0.18.11 source=6bd7c5639360f4f1f10f94c587be72a4191dd7bbf98894e52b378356e56d1fe0 closed=dev-dogfooder-removed;ordinary-controller-preserved;compact-current-workbench;external-exact-archive;bounded-package
#@QOMRADE-HISTORY version=0.18.13 source=8460de2de05a13ee3fef9571656a01c9d30babb6dc2c8ab39e20b1ee9991fa36 closed=operator-directed-fresh-prompt-resends;native-Retry-and-automatic-reload-retired;deferred-failure-and-selector-repair
#@QOMRADE-HISTORY version=0.18.14 source=cdc77bffad04ece800d033775290942aaa3b090b4d33fd2fa1b723396b7d1afe closed=explicit-GPT-5.6-first-model-priority;sticky-GPT-6-fallback-after-5.6-failure;Latest-remains-provisional;fresh-prompt-recovery-retained
#@QOMRADE-HISTORY version=0.18.15 source=d17314a9526b7b3e7d1daeeb277c3ee661b86c1b973f9fc7f42dd058766f2f86 closed=stable-later-exact-prompt-successor-adoption;superseded-request-receipts;red-letter-recovery-custody-follows-latest-authorized-request
#@QOMRADE-HISTORY version=0.18.16 source=7f3b3f108672ab049a11dc950facaac9bf3f360398c789d36140f3ea4272986a closed=red-letter-partial-output-and-work-are-preserved-evidence-not-terminal-blockers;post-completion-faults-preempt-ordinary-gap;transient-persistence-reconciliation
#@QOMRADE-HISTORY version=0.18.17 source=6a66922fb2569661685824c8940b508be310306374f036b2206649de0d3a60b7 closed=opt-in-bounded-old-turn-DOM-trimming;hourly-safe-checkpoint-refresh;confirmed-one-shot-exact-run-resume;visibility-overdue-wake
#@QOMRADE-HISTORY version=0.18.18 source=1fd581f4e413f9561c45e2e60e0305158386ebebd321c9ccf1915e4c96d28eec closed=field-observed-conversation-too-long-terminal-recognition;expected-COMPLETE-stop;no-Retry-resend-trim-or-refresh-after-session-end
#@QOMRADE-HISTORY version=0.18.19 source=7ccebdd032c23137f7daaa38e4059d1261c47686b10176d249fa3618fe4e33f9 closed=field-evidenced-maintenance-coalescing;generation-block-edge-wake;blocker-aware-refresh-backoff;page-local-maintenance-counters
#@QOMRADE-HISTORY version=0.18.20 source=a0219717ca95165bf09f9ef6902bab73fb56e57b9d0479274ce142e6785c5302 closed=distinct-session-and-developer-handoffs;compact-flight-recorder;conversation-spanning-bounded-observed-transcript-succession;advisory-maintenance-intervals;clean-living-prose;30-minute-background-defaults
#@QOMRADE-HISTORY version=0.18.21 source=55aebe861dc53e98bf171068d7300a3a255ebd012bb90518da8bdfd82b261d75 closed=transcript-only-ChatGPT-Session-Handoff;no-authored-brief-or-qomrade-state;separate-conversation-and-qomrade-evidence-UI;ordered-context-river-export
#@QOMRADE-HISTORY version=0.18.22 source=8cdbc8532e23bc3dc23654b46b7de322fd2835606ae02fb1a7c775bc0862fda0 closed=operator-enabled-bounded-stale-pipeline-surface-healing-refresh;15-second-settlement;missing-composer-narrowly-allowed;current-request-recovery-priority;30-minute-dedup;two-per-hour-budget
#@QOMRADE-HISTORY version=0.18.23 source=03eed683e763b31c1b6f06c66529397ebd9a42055eb3621623c2ad18fbb46c8d closed=literal-retry-card-context-and-bounded-pipeline-surface-edge-evidence;Developer-Handoff-clipboard-only;file-export-removed
#@QOMRADE-HISTORY version=0.18.24 source=3e2f1c821f574cc9bf955931fc5849c728be076a47c825e04ae4505b5149f91e closed=amnesia-first-developer-handoff-v2;canonical-incident-index-and-timeline;event-triggered-bounded-DOMish-snapshots;safe-refresh-forensic-carry
#@QOMRADE-HISTORY version=0.18.25 source=53255b992b41ae78c90806165fd33d8a191ec17e750807a70f809e6007ac9b9b closed=exact-conversation-stale-shell-healing-with-active-request-custody;normalized-live-and-DOMish-restored-pipeline-surfaces;terminal-Retry-context;higher-value-DOMish-roots
#@QOMRADE-HISTORY version=0.18.26 source=4061b0040e08cfaf8964267f6c32f1710fc0e8dad940529dceaf065cf62cf0be closed=Unicode-faithful-prompt-custody;serialized-safe-refresh-persistence;late-tab-read-adoption;all-phase-stale-shell-holds;bounded-restore-timeout;final-click-cadence;transcript-and-model-evidence-hardening
#@QOMRADE-HISTORY version=0.18.27 source=c8d5d0665dd655fc154398e21b03c0d39d3e1af79da40f62baefb2b73a3d95a2 closed=operator-selectable-model-policies;Smart-Pro-default;exact-live-discovered-pin-with-no-fallback;Follow-current-any-tier;non-Pro-send-local-confirmation
#@QOMRADE-HISTORY version=0.18.28 source=c9034617f56cafa3fe8346838ece19a6c58480927383bfe581e4f7d2740a2a53 closed=background-structural-model-menu;hidden-tab-model-progress;default-trim-and-safe-refresh;tail-bounded-terminal-scan;field-memory-hygiene
#@QOMRADE-HISTORY version=0.18.29 source=56e0db296502e984251595c93bf51bdb05cc5d7815f7d162e6d3bf6497c768ae closed=high-confidence-unstyled-or-stalled-ChatGPT-shell-detection;event-time-DOMish-evidence;no-Send-SURFACE_HOLD;Start-authorized-exact-ticket-repair;stable-dedup
#@QOMRADE-HISTORY version=0.18.30 source=2fbe45d81848738a8f55d9949d5aa8688016e30550157bd3ab6064c4a35c3600 closed=exact-conversation-load-failed-maintenance-classification;DOMish-card-evidence;no-Send-hold;exact-ticket-Safe-refresh-repair;no-native-Retry-or-prompt-resend
#@QOMRADE-HISTORY version=0.18.31 source=5c74934db4d513cac751c257ed78c6e580db70dc971618894fb0c8c352f2423d closed=field-proven-hidden-pinned-model-menu-paint-transition-bypass;exact-trigger-controlled-structural-read;non-inert-mutation-gate;background-send-without-foreground;menu-reset-churn-removed
#@QOMRADE-HISTORY version=0.18.32 source=a10a35641f70873f7fcb53d602474d95c47c6f7f1c45fb11b8925dea85d17747 closed=selected-route-only-pinned-label-drift-reconciliation;legacy-Latest-to-checked-GPT-6;persisted-canonical-label-key-version;no-alias-click-or-family-fallback
#@QOMRADE-HISTORY version=0.18.33 source=03b778676b27eae03a62197cc24838f09b4613ff2532c2df4685b6c20fcabeb4 closed=low-churn-generation-observation;compact-model-survey-retention;bounded-model-menu-mutation-wait;foreground-rescue-and-hidden-gap-evidence;memory-pressure-proxy;duplicate-page-error-coalescing
#@QOMRADE-HISTORY version=0.18.34 source=f9c01ecd7d335190a02cab9c30e28935c0bd0b21209c68a2cd2913dcc58e6a59 closed=Smart-Pro-fallback-resets-after-success;message-delivery-timeout-recovery;comma-separated-native-file-suffixes-with-.zip-default;generic-file-capture-evidence;release-verification-artifacts-were-internally-contradictory
#@QOMRADE-HISTORY version=0.18.35 source=pending closed=field-working-but-source-identity-remained-pending;explicit-file-control-authority;priority-file-scan;composer-scoped-Send;red-team-regressions
#@QOMRADE-HISTORY version=0.18.36 source=1a9b9cf9544273779220debde5e9a211a7678aed7437e573d8084cb69cf7b2d1 closed=taller-bottom-panel-with-top-clearance;exact-safe-refresh-minutes;active-request-and-settings-orientation;cloudtainer-officer-CLI;restored-source-identity-and-release-readback
#@QOMRADE-HISTORY version=0.18.37 source=5afc38b732251d7fafa4c46abb8abbed7cb66f8a728eb25bb6357dff2d980f7b closed=assistant-only-pre-click-rebaseline;current-request-owned-conversation-stale-fresh-message-recovery;maintenance-history-remains-refresh-only;defined-fault-labels
#@QOMRADE-HISTORY version=0.18.38 source=bff69c1faf3720795e19a368f51d4b500bb4c3d69f1f181d4bd8c4f98ae3dd35 closed=settled-file-activation;bounded-download-toast-evidence;single-failure-retry;boot-transcript-capture;bounded-history-backfill;ordinal-coverage
#@QOMRADE-HISTORY version=0.18.39 source=572788869f1e8a5eb225fa6576d465e69103c9c36507237dc7cd150b351d2afe closed=accepted-user-turn-terminal-stage;truthful-empty-composer-explanation;barrier-owner-evidence;terminal-handoff-clarity
#@QOMRADE-HISTORY version=0.18.40 source=94ce8693882cbd2bfc09733a0e43297f600cf32791faf9d8567573e6d00d586c closed=non-scrolling-session-handoff;natural-scroll-capture;visible-context-items;final-terminal-owner-reconciliation
#@QOMRADE-HISTORY-END
================================================================================
*/
;(function () {
  'use strict';
  // The normal controller remains single-tab, with bounded request-owned recovery and coalesced opt-in maintenance.
  // No fleet discovery, shared control keys, cross-tab listeners, self-prompting,
  // keep-awake audio, browser developer file path, or automatic diagnostic upload.
  // The large Bash workbench, heritage, dialogue, and succession document above are inert comment text in the browser.
  // @QOMRADE-CHUNK id=10.identity title="Runtime identity, embedded workbench, and succession constants"
  const QOMRADE_VERSION = '0.18.40';
  const QOMRADE_DOCUMENT_SCHEMA = 'qomrade.document.v69';
  const QOMRADE_RUNTIME_SCHEMA = 'qomrade.single-tab-runtime.v45';
  const QOMRADE_HANDOFF_SCHEMA = 'qomrade.developer-handoff.v2';
  const QOMRADE_SOURCE_ID = '94ce8693882cbd2bfc09733a0e43297f600cf32791faf9d8567573e6d00d586c';
  /*@QOMRADE-WORKBENCH-B64-BEGIN*/
  /* Bash-only embedded workbench; intentionally not JavaScript data.
    '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',
  */
  /*@QOMRADE-WORKBENCH-B64-END*/
  const EMBEDDED_WORKBENCH_BYTES = 156683;
  const EMBEDDED_WORKBENCH_SHA256 = 'b0d200dc108aa4df3c3f9599b51c886173f18e637f2268ca128c49bb49007496';
  const VERSION = QOMRADE_VERSION;
  const TEST_MODE = !!window.__QOMRADE_TEST_MODE__;
  const STORAGE_SCHEMA = 'qomrade.single-tab-state.v8';
  const MAX_PROMPT_CHARS = 32_768;
  const VISIBLE_REPLY_POLL_MS = 7_500;
  const HIDDEN_REPLY_POLL_MS = 30_000;
  const VISIBLE_GAP_POLL_MS = 30_000;
  const HIDDEN_GAP_POLL_MS = 60_000;
  const COMPLETION_STABLE_SAMPLES = 2;
  const INSERT_SETTLE_MS = 120;
  const PRE_CLICK_ADVANCE_SETTLE_MS = 800;
  const PRE_CLICK_ADVANCE_POLL_MS = 80;
  const SEND_BUTTON_WAIT_MS = 2_000;
  const INITIAL_SEND_DELAY_MS = 350;
  const MIN_POST_COMPLETE_MS = 10_000;
  const MIN_SEND_CLICK_FLOOR_MS = 1_000;
  const TAB_READ_TIMEOUT_MS = 8_000;
  const MAX_EVENT_RECORDS = 80;
  const MAX_DIAGNOSTIC_UTF8_BYTES = 64 * 1024;
  const MAX_EVENT_DETAIL_CHARS = 24_000;
  const MAX_HANDOFF_UTF8_BYTES = 8 * 1024 * 1024;
  const MAX_HANDOFF_TURNS = 64;
  const MAX_HANDOFF_TURN_CHARS = 64_000;
  const MAX_SESSION_HANDOFF_UTF8_BYTES = 24 * 1024 * 1024;
  const MAX_SESSION_ARCHIVE_UTF8_BYTES = 16 * 1024 * 1024;
  const MAX_SESSION_ARCHIVE_PERSIST_UTF8_BYTES = 4 * 1024 * 1024;
  const MAX_SESSION_TURNS = 512;
  const MAX_SESSION_TURN_CHARS = 512_000;
  const MAX_FLIGHT_RECORDER_UTF8_BYTES = 512 * 1024;
  const ZIP_RESCAN_DELAY_MS = 5_000;
  const FILE_SETTLE_DEFAULT_SECONDS = 10;
  const FILE_SETTLE_MAX_SECONDS = 120;
  const FILE_OUTCOME_WATCH_MS = 30_000;
  const FILE_FAILURE_RETRY_DELAY_MS = 30_000;
  const FILE_SCAN_MAX_PASSES = 36;
  const MAX_FILE_NOTICES = 16;
  const SESSION_BACKFILL_MAX_MS = 10_000;
  const SESSION_BACKFILL_MAX_PASSES = 16;
  const DEFAULT_DOWNLOAD_SUFFIXES = '.zip';
  const MAX_DOWNLOAD_SUFFIXES = 16;
  const MAX_DOWNLOAD_SUFFIX_CHARS = 256;
  const BOOT_AUTHENTICITY_DELAY_MS = 2_500;
  const SHELL_HEALTH_BOOT_PROBE_MS = 15_000;
  const SHELL_HEALTH_HYDRATION_MIN_MS = 30_000;
  const MAX_SHELL_HEALTH_INCIDENTS = 12;
  const MODEL_MENU_OPEN_TIMEOUT_MS = 2_200;
  const MODEL_MENU_HIDDEN_OPEN_TIMEOUT_MS = 12_000;
  const MODEL_MENU_OBSERVER_VISIBLE_POLL_MS = 200;
  const MODEL_MENU_OBSERVER_HIDDEN_POLL_MS = 1_000;
  const MODEL_SURVEY_MARKUP_HEAD_CHARS = 320;
  const BACKGROUND_RESCUE_WINDOW_MS = 5_000;
  const BACKGROUND_EXECUTION_GAP_MS = 60_000;
  const RESILIENCE_DEFAULTS_VERSION = 1;
  const MODEL_MENU_SETTLE_MS = 280;
  const MODEL_SELECTION_SETTLE_MS = 650;
  const MODEL_EFFORT_STEP_MS = 150;
  const MODEL_RECHECK_MS = 5 * 60_000;
  const MODEL_SURFACE_RECHECK_MS = 15_000;
  const MODEL_CONFIRMATION_MAX_AGE_MS = 15 * 60_000;
  const MODEL_COMMIT_MAX_AGE_MS = 60_000; // send-local UI evidence, never a cross-turn model cache
  const MAX_MODEL_CANDIDATES = 8;
  const MAX_MODEL_SURVEY_RECORDS = 8;
  const MAX_SCIENCE_PULSES = 48;
  const MAX_PIPELINE_SURFACE_EDGES = 16;
  const MAX_RETRY_CONTEXTS = 4;
  const MAX_PAGE_ERROR_RECORDS = 24;
  const MAX_TURN_RECEIPTS = 24;
  const MAX_ZIP_KEYS = 32;
  const MAX_CONTINUITY_EVENTS = 16;
  const MAX_CONTINUITY_BYTES = 64 * 1024;
  const MAX_PROBE_FAILURES = 32;
  const MAX_RESOURCE_RECORDS = 80;
  const MAX_RESOURCE_ENDPOINTS = 160;
  const MAX_CONTROL_RECORDS = 100;
  const MAX_RED_SIGNAL_RECORDS = 40;
  const MAX_DOM_SEMANTIC_RECORDS = 160;
  const MAX_DOMISH_SNAPSHOTS = 12;
  const MAX_DOMISH_TOTAL_UTF8_BYTES = 640 * 1024;
  const MAX_DOMISH_SNAPSHOT_UTF8_BYTES = 96 * 1024;
  const MAX_DOMISH_PERSIST_UTF8_BYTES = 320 * 1024;
  const MAX_DOMISH_ROOTS = 4;
  const MAX_DOMISH_TREE_NODES = 72;
  const MAX_DOMISH_TREE_DEPTH = 4;
  const MAX_DOMISH_TEXT_CHARS = 6_000;
  const MAX_DOMISH_MARKUP_CHARS = 16_000;
  const MAX_CANONICAL_TIMELINE_RECORDS = 180;
  const TIMER_LATE_THRESHOLD_MS = 15_000;
  const DOM_TRIM_KEEP_LOGICAL_TURNS = 4;
  const DOM_TRIM_TRANSIENT_RETRY_MS = 5_000;
  const DOM_TRIM_STATIC_RETRY_MS = 5 * 60_000;
  const DOM_TRIM_MIN_INTERVAL_MS = 15_000;
  const AUTO_REFRESH_DEFAULT_MINUTES = 60;
  const AUTO_REFRESH_MIN_MINUTES = 5;
  const AUTO_REFRESH_MAX_MINUTES = 1_440;
  const AUTO_REFRESH_RESTORE_MAX_MS = 120_000;
  const AUTO_REFRESH_RETRY_MS = 60_000;
  const AUTO_REFRESH_TRANSIENT_RETRY_MS = 15_000;
  const AUTO_REFRESH_UI_RETRY_MS = 5 * 60_000;
  const AUTO_REFRESH_GENERATION_RETRY_MS = 15 * 60_000;
  const AUTO_REFRESH_MAX_RETRY_MS = 15 * 60_000;
  const AUTO_REFRESH_TICKET_MAX_AGE_MS = 2 * 60 * 60_000;
  const AUTO_REFRESH_HEALING_SETTLE_MS = 15_000;
  const AUTO_REFRESH_HEALING_DEDUP_MS = 30 * 60_000;
  const AUTO_REFRESH_HEALING_WINDOW_MS = 60 * 60_000;
  const AUTO_REFRESH_HEALING_LIMIT = 2;
  const PANEL_WIDTH_PX = 420;
  const PANEL_EXPANDED_MAX_HEIGHT_PX = 826;
  const PANEL_VIEWPORT_TOP_RESERVE_PX = 96;
  const PANEL_COLLAPSED_HEIGHT_PX = 46;
  const CANONICAL_MAX_LENGTH_TEXT = "You've reached the maximum length for this conversation, but you can keep talking by starting a new chat.";
  const CURRENT_CONVERSATION_TOO_LONG_TEXT = 'The conversation is too long, please start a new one.';
  const CONVERSATION_TERMINAL_TEXTS = Object.freeze([
    { kind: 'maximum-length', text: CANONICAL_MAX_LENGTH_TEXT },
    { kind: 'conversation-too-long', text: CURRENT_CONVERSATION_TOO_LONG_TEXT },
  ]);
  const MODEL_POLICY_SMART_PRO = 'smart-pro';
  const MODEL_POLICY_PIN = 'pin';
  const MODEL_POLICY_FOLLOW = 'follow';
  const MODEL_POLICY_VALUES = Object.freeze([MODEL_POLICY_SMART_PRO, MODEL_POLICY_PIN, MODEL_POLICY_FOLLOW]);
  const MODEL_EFFORT_VALUES = Object.freeze(['keep', 'minimum', 'low', 'medium', 'high', 'pro']);
  const MODEL_EFFORT_LABELS = Object.freeze({
    keep: 'Keep current effort',
    minimum: 'Minimum / Instant',
    low: 'Low',
    medium: 'Medium',
    high: 'High / highest non-Pro',
    pro: 'Pro / maximum',
  });
  const DEFAULTS = Object.freeze({
    prompt: '',
    gapMinutes: 30,
    pauseWhenHidden: false,
    autoZip: true,
    downloadSuffixes: DEFAULT_DOWNLOAD_SUFFIXES,
    fileDelaySeconds: FILE_SETTLE_DEFAULT_SECONDS,
    requireVisibleFamily: true,
    autoSelectEligiblePro: true,
    modelPolicy: MODEL_POLICY_SMART_PRO,
    modelTargetLabel: '',
    modelTargetKey: '',
    modelTargetVersion: null,
    modelTargetEffort: 'pro',
    boundedScience: true,
    trimOldTurns: true,
    hourlyRefresh: true,
    refreshMinutes: AUTO_REFRESH_DEFAULT_MINUTES,
  });
  // @QOMRADE-CHUNK id=20.surface title="Semantic surface selectors and low-churn DOM helpers"
  const SELECTORS = Object.freeze({
    composer: [
      'form[data-chatgpt-composer] [data-composer-markdown][contenteditable="true"]',
      '[data-composer-markdown][contenteditable="true"]',
      '#prompt-textarea[contenteditable="true"]',
      'div.ProseMirror[contenteditable="true"][role="textbox"]',
      '[contenteditable="true"][role="textbox"][aria-label*="ChatGPT" i]',
      'textarea[aria-label*="ChatGPT" i]',
      'textarea[placeholder*="message" i]',
    ],
    send: [
      'form[data-chatgpt-composer] [data-testid="send-button"]',
      '[data-testid="send-button"]',
      '#composer-submit-button:not([data-testid="stop-button"])',
      'button[aria-label="Send prompt"]',
      'form button[type="submit"]',
    ],
    stop: [
      'form[data-chatgpt-composer] [data-testid="stop-button"]',
      '[data-testid="stop-button"]',
      '#composer-submit-button[data-testid="stop-button"]',
      'button[aria-label*="Stop answering" i]',
      'button[aria-label^="Stop" i]',
    ],
    model: [
      'form[data-chatgpt-composer] button[aria-label="Select ChatGPT model"]',
      'button[aria-label="Select ChatGPT model"]',
      'button[data-composer-navigation-target="reasoning"]',
      'button[data-codex-intelligence-trigger="true"]',
      'button[aria-haspopup="menu"][data-selected-reasoning-effort]',
    ],
    turns: [
      '[data-testid^="conversation-turn-"]',
      'article[data-testid^="conversation-turn-"]',
      'main [data-message-author-role]',
      '[data-content-search-turn-key]',
      '[data-chatgpt-search-unit-key]',
    ],
    errors: [
      '[role="alert"]',
      '[aria-live="assertive"]',
      '[data-testid*="error" i]',
      '[data-state="error"]',
      '[data-error]',
      '[data-color="danger"]',
      '[class*="text-red"]',
      '[class*="text-danger"]',
      '[class*="text-token-text-error"]',
      '[class*="surface-error"]',
    ],
    history: [
      '[data-sidebar-chatgpt-conversation-key]',
      'nav a[href^="/c/"]',
      'a[href^="/c/"][data-testid*="history" i]',
      '[data-testid*="history-item" i] a[href^="/c/"]',
    ],
    dialogs: [
      'dialog[open]',
      '[role="dialog"]',
      '[aria-modal="true"]',
    ],
    continue: [
      '[data-testid*="continue-generating" i]',
      'button[aria-label*="continue generating" i]',
      'button[aria-label*="keep generating" i]',
    ],
    retry: [
      '[data-testid*="regenerate-thread-error" i]',
      '[data-testid*="retry" i]',
      'button[aria-label^="Retry" i]',
      'button[aria-label*="Try again" i]',
    ],
    system: [
      '[role="status"]',
      '[aria-live="polite"]',
      '[aria-live="assertive"]',
      '[data-testid*="status" i]',
      '[data-testid*="notice" i]',
      '[data-testid*="error" i]',
    ],
    work: [
      '[data-testid^="cot-"]',
      '[data-testid*="cot-v"]',
      '[data-testid*="chain-of-thought" i]',
      '[data-testid*="reasoning-trace" i]',
      '[data-chatgpt-agent-turn-start]',
    ],
    finalAnswer: [
      '.markdown',
      '[class*="markdown"]',
      '[data-testid*="final-answer" i]',
      '[data-message-author-role="assistant"]',
    ],
  });
  const settings = { ...DEFAULTS };
  let lastSavedSettingsJson = '';
  const state = {
    running: false,
    paused: false,
    phase: 'STOPPED',
    phaseReason: 'fresh start',
    runPrompt: '',
    startedAt: 0,
    lastSendAt: 0,
    nextSendAt: 0,
    waitingSince: 0,
    baselineAssistantId: null,
    latestAssistantId: null,
    latestAssistantFingerprint: null,
    stableSamples: 0,
    anchorConversationId: null,
    timer: null,
    tickBusy: false,
    effectControl: { schema: 'qomrade.effect-control.v1', epoch: 0, operations: 0, active: null, lastRevocation: null, cancellations: 0, lastCancellation: null },
    lastError: null,
    terminalStop: null,
    faultObservation: null,
    faultIncidents: [],
    faultRecovery: { schema: 'qomrade.fault-recovery.v3', enabled: true, ledger: [], activeKey: null, lastObservation: null, lastDecision: null, preexistingAdvance: null, preexistingAdvanceCount: 0, postReloadUntil: 0, postReloadWitness: null, writeReceipts: [] },
    recoveryResume: null,
    recoveryRestorePending: false,
    lastFaultSignature: null,
    completedReplies: 0,
    sends: 0,
    startAttempts: 0,
    startAccepted: 0,
    startRefused: 0,
    startTransaction: null,
    adoptedWithoutClick: 0,
    preClickAdvanceHolds: 0,
    composerAttemptCount: 0,
    zipClicks: 0,
    zipActivationErrors: 0,
    lastZipKey: null,
    zipKeys: [],
    zipCapture: { pending: null, lastScan: null, receipts: [], seen: Object.create(null), notices: [], outcomeWatch: null, autoRetries: 0, ignoredNeutralNotices: 0, lastIgnoredNeutralNotice: null },
    background: { hiddenTicks: 0, visibleTicks: 0, hiddenSends: 0, hiddenZipActivations: 0, lastHiddenTickAt: null, lastVisibleTickAt: null, current: null, intervals: [], migration: null,
      pendingHiddenModelHold: null, foregroundRescues: [], hiddenProgresses: 0, lastHiddenProgressAt: null,
      executionGaps: [], lastVisibilityAt: null, lastFocusAt: null },
    domTrim: { schema: 'qomrade.dom-trim.v2', attempts: 0, successes: 0, unitsRemoved: 0, logicalTurnsRemoved: 0, pageAttempts: 0, pageSuccesses: 0, pageUnitsRemoved: 0, pageLogicalTurnsRemoved: 0, blockedStreak: 0, blockedSince: null, blockerChanges: 0, nextAttemptAt: 0, retryMode: null, suppressedRetries: 0, lastAt: null, lastReason: null, lastBlocked: null, receipts: [] },
    autoRefresh: { schema: 'qomrade.auto-refresh.v3', dueAt: 0, retryAt: 0, scheduledAt: 0, attempts: 0, reloads: 0, deferrals: 0, pageAttempts: 0, pageReloads: 0, pageDeferrals: 0, blockedStreak: 0, blockedSince: null, blockerChanges: 0, retryDelayMs: 0, lastAttemptAt: null, lastReloadAt: null, lastBlocked: null, lastReadback: null, receipts: [], resumeTicket: null, pendingResume: null, restorePending: false, restoreInFlight: false, inFlight: false,
      healingPending: null, healingHistory: [], healingReloads: 0, healingSuppressed: 0, lastHealingAt: null, lastHealingKey: null, lastFaultSurfaceKey: null, lastFaultSurfaceAt: null,
      restoreStartedAt: 0, restoreDeadlineAt: 0 },
    resilienceDefaultsMigration: null,
    shellHealth: { schema: 'qomrade.page-shell-health.v1', current: null, lastObservation: null, incidents: [], lastKey: null, recoveredAt: null, bootProbeAt: null },
    sessionArchive: { schema: 'qomrade.session-record.v3', sessionId: null, startedAt: null, endedAt: null, conversationId: null, pathname: null, promptHash: null, promptChars: 0, runStarts: 0, lastStartAt: null, captures: 0, lastCaptureAt: null, turns: [], totalUtf8Bytes: 0, visibleArtifactCount: 0, truncatedTurns: 0, skippedTurns: 0, restoredAcrossRefresh: false, omissions: [], naturalScrollCaptures: 0, lastNaturalScrollAt: null, lastSurfaceSignature: null, backfill: { active: false, attempts: 0, last: null } },
    events: [],
    eventSeq: 0,
    pageErrors: [],
    activeSend: null,
    turnReceipts: [],
    modelAtSend: null,
    modelDrifts: [],
    modelIndicatorEdges: [],
    modelGate: {
      schema: 'qomrade.model-gate.v4',
      active: false,
      surveys: 0,
      attempts: 0,
      selections: 0,
      effortSteps: 0,
      menuOpenFailures: 0,
      menuObserverWaits: 0,
      menuObserverResolutions: 0,
      menuObserverTimeouts: 0,
      menuObserverMutations: 0,
      retainedSurveyBytes: 0,
      retainedSurveyMaxBytes: 0,
      backgroundStructuralAccepts: 0,
      backgroundPaintSuppressedAccepts: 0,
      pinnedRouteAliasReconciliations: 0,
      lastPinnedRouteAliasReconciliation: null,
      pinnedRouteAliasReceipts: [],
      lastBackgroundStructuralAccept: null,
      lastBackgroundStructuralKey: null,
      nextSurveyAt: 0,
      lastSurvey: null,
      recentSurveys: [],
      confirmed: null,
      transientLabelsIgnored: 0,
      lastCommit: null,
      runPreference: '5.6-first',
      runPolicy: MODEL_POLICY_SMART_PRO,
      target: { label: '', key: '', version: null, effort: 'pro' },
      lastPreferenceSwitch: null,
      catalog: { schema: 'qomrade.model-catalog.v1', observedAt: null, rows: [], selectedKey: null, selectedLabel: null, effort: null },
      catalogBusy: false,
      catalogError: null,
    },
    science: {
      schema: 'qomrade.pipeline-science.v1',
      enabled: true,
      samples: 0,
      changes: 0,
      lastSignature: null,
      lastAt: null,
      lastChangedAt: null,
      pulses: [],
      surfaceEdges: [],
    },
    domForensics: {
      schema: 'qomrade.domish-event-buffer.v1',
      captures: 0,
      deduplicated: 0,
      dropped: 0,
      restoredAcrossRefresh: false,
      totalUtf8Bytes: 0,
      lastCaptureAt: null,
      lastKey: null,
      snapshots: [],
    },
    quarantine: null,
    lastAuthenticity: null,
    priorContinuity: null,
    uiModelObservation: null,
    boot: {
      startedAt: nowIso(),
      startedT: Date.now(),
      tabRead: { status: 'not-started', timeoutMs: TAB_READ_TIMEOUT_MS, elapsedMs: null, recordPresent: false, error: null, lateCallbacks: 0, pendingLate: false, lateAdoptedAt: null, lateDiscardedAt: null, lateDiscardReason: null, writeQueued: false },
      operatorTouched: false,
      panelMountedAt: null,
      panelMountStatus: 'not-started',
      panelMountError: null,
      menusRegistered: 0,
      readyAt: null,
      oneShotAuthenticityCheckedAt: null,
      settingsReadyAt: null,
    },
    persistence: {
      reads: 0,
      readTimeouts: 0,
      readErrors: 0,
      writes: 0,
      writeErrors: 0,
      lastReadAt: null,
      lastReadElapsedMs: null,
      lastWriteAt: null,
      lastWriteBytes: 0,
      maxWriteBytes: 0,
      lastWriteReason: null,
    },
    scheduler: {
      scheduledAt: 0,
      dueAt: 0,
      nominalDelayMs: 0,
      reason: null,
      lastFiredAt: 0,
      lastLatenessMs: 0,
      maxLatenessMs: 0,
      lateCount: 0,
      fires: 0,
      skippedBusy: 0,
      pendingWake: null,
      deferredWakes: 0,
      lastClearedAt: 0,
      lastClearReason: null,
    },
    metrics: {
      selectorQueries: 0,
      ticks: 0,
      tickTotalMs: 0,
      tickLastMs: 0,
      tickMaxMs: 0,
      tickLastQueries: 0,
      tickMaxQueries: 0,
      turnTextReads: 0,
      turnTextCacheHits: 0,
      turnTextChars: 0,
      turnTextReadsSuppressedWhileGenerating: 0,
      barrierProseScansSuppressedWhileGenerating: 0,
      semanticTextNodesVisited: 0,
      semanticSubtreeReads: 0,
      synchronousSections: {},
      handoffs: 0,
      handoffLastMs: 0,
      handoffMaxMs: 0,
      diagnostics: 0,
      diagnosticsLastMs: 0,
      diagnosticsMaxMs: 0,
      eventDetailsTruncated: 0,
      authenticityLightProbes: 0,
      authenticityFullProbes: 0,
      resourceEndpointOverflowEntries: 0,
      developerHandoffsCopied: 0,
      developerHandoffCopyErrors: 0,
      sessionHandoffsSaved: 0,
      sessionHandoffErrors: 0,
      flightRecordersSaved: 0,
      flightRecorderErrors: 0,
      panelEditHolds: 0,
      panelEditReleases: 0,
    },
  };
  const ui = {
    host: null,
    frame: null,
    panelDocument: null,
    refs: Object.create(null),
    mounted: false,
    collapsed: false,
    saveTimer: null,
    zipRescanTimer: null,
    fileOutcomeObserver: null,
    fileOutcomeTimer: null,
    sessionBootTimer: null,
    sessionScrollTimer: null,
    bootAuthenticityTimer: null,
    shellHealthTimer: null,
    domTrimTimer: null,
    autoRefreshTimer: null,
  };
  function normalizeFileDelaySeconds(value, fallback = FILE_SETTLE_DEFAULT_SECONDS) {
    const numeric = Number(value);
    if (!Number.isFinite(numeric)) return fallback;
    return Math.round(Math.min(FILE_SETTLE_MAX_SECONDS, Math.max(0, numeric)));
  }
  function normalizeRefreshMinutes(value, fallback = AUTO_REFRESH_DEFAULT_MINUTES) {
    const numeric = Number(value);
    if (!Number.isFinite(numeric)) return fallback;
    return Math.round(Math.min(AUTO_REFRESH_MAX_MINUTES, Math.max(AUTO_REFRESH_MIN_MINUTES, numeric)));
  }
  function autoRefreshIntervalMs() {
    return normalizeRefreshMinutes(settings.refreshMinutes) * 60_000;
  }
  function nowIso() {
    return new Date().toISOString();
  }
  function clamp(value, min, max) {
    const number = Number(value);
    if (!Number.isFinite(number)) return min;
    return Math.min(max, Math.max(min, number));
  }
  function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
  function trunc(value, max = 1_000) {
    const text = String(value == null ? '' : value);
    return text.length <= max ? text : `${text.slice(0, Math.max(0, max - 18))}…[${text.length}]`;
  }
  function normalizePromptLineEndings(value) {
    // Prompt custody is code-point faithful. Only platform line endings are
    // canonicalized; NBSP, ZWJ, ZWNJ, variation selectors and BOM-like code
    // points remain part of the operator's text and are sent unchanged.
    return String(value == null ? '' : value).replace(/\r\n?/g, '\n');
  }
  function normalizeLineEndings(value) {
    // Lossy UI projection for labels, rendered-text comparison and evidence.
    // Never use this function to mutate the composer payload.
    return normalizePromptLineEndings(value)
      .replace(/\u00a0/g, ' ')
      .replace(/[\u200b\u200c\u200d\ufeff]/g, '');
  }
  function normalizeForEditorCompare(value) {
    return normalizePromptLineEndings(value).replace(/\n+$/g, '');
  }
  function editorPayloadEquivalent(observedValue, expectedValue) {
    const observed = normalizeForEditorCompare(observedValue);
    const expected = normalizeForEditorCompare(expectedValue);
    if (observed === expected) return { ok: true, exactCodePoints: true, browserSpaceRepresentation: false };
    if (observed.length !== expected.length) return { ok: false, exactCodePoints: false, browserSpaceRepresentation: false };
    let browserSpaceRepresentation = false;
    for (let index = 0; index < expected.length; index += 1) {
      if (observed[index] === expected[index]) continue;
      // Contenteditable may represent an operator-authored ordinary space as
      // NBSP, especially at a block edge. This equivalence is directional:
      // an authored NBSP must remain NBSP and is never accepted as plain space.
      if (expected[index] === ' ' && observed[index] === '\u00a0') { browserSpaceRepresentation = true; continue; }
      return { ok: false, exactCodePoints: false, browserSpaceRepresentation: false };
    }
    return { ok: true, exactCodePoints: false, browserSpaceRepresentation };
  }
  function cleanVisibleText(value) {
    return normalizeLineEndings(value)
      .replace(/Thinking effort/gi, ' ')
      .replace(/Select ChatGPT model/gi, ' ')
      .replace(/\s+/g, ' ')
      .trim();
  }
  function fnv1a32(value) {
    const text = String(value == null ? '' : value);
    let hash = 0x811c9dc5;
    for (let i = 0; i < text.length; i += 1) {
      hash ^= text.charCodeAt(i);
      hash = Math.imul(hash, 0x01000193) >>> 0;
    }
    return hash.toString(16).padStart(8, '0');
  }
  function boundedEventDetail(detail) {
    if (detail == null) return detail;
    try {
      const serialized = JSON.stringify(detail);
      if (serialized.length <= MAX_EVENT_DETAIL_CHARS) return JSON.parse(serialized);
      state.metrics.eventDetailsTruncated += 1;
      return {
        schema: 'qomrade.bounded-event-detail.v1',
        truncated: true,
        originalChars: serialized.length,
        preview: serialized.slice(0, MAX_EVENT_DETAIL_CHARS),
      };
    } catch (_) {
      return { uncloneable: true, text: trunc(String(detail), 4_000) };
    }
  }
  function logEvent(kind, message, detail = null) {
    state.eventSeq += 1;
    const snapshot = boundedEventDetail(detail);
    state.events.push({ seq: state.eventSeq, t: Date.now(), at: nowIso(), kind, message, detail: snapshot });
    if (state.events.length > MAX_EVENT_RECORDS) {
      state.events.splice(0, state.events.length - MAX_EVENT_RECORDS);
    }
    if (kind === 'model-confirmed' || kind === 'send-click') noteBackgroundProgress(kind);
  }
  function recordPageError(record) {
    const at = nowIso();
    const now = Date.now();
    const signature = fnv1a64(JSON.stringify([
      record && record.kind || null,
      record && record.message || null,
      record && record.filename || null,
      record && record.lineno || null,
      record && record.colno || null,
    ]));
    const prior = [...state.pageErrors].reverse().find(row => row.signature === signature && now - (Number(row.lastT) || Number(row.t) || 0) <= 10 * 60_000);
    if (prior) {
      prior.observations = (Number(prior.observations) || 1) + 1;
      prior.lastAt = at;
      prior.lastT = now;
    } else {
      state.pageErrors.push({ at, t: now, firstAt: at, lastAt: at, lastT: now, observations: 1, signature, ...record });
      if (state.pageErrors.length > MAX_PAGE_ERROR_RECORDS) {
        state.pageErrors.splice(0, state.pageErrors.length - MAX_PAGE_ERROR_RECORDS);
      }
    }
    if (/^(?:qomrade-controller-error|panel-mount-error|auto-refresh-reload-error|auto-refresh-persistence-error|dom-trim-error)$/.test(String(record && record.kind || ''))) {
      try {
        captureDomishEvent('qomrade-page-error', {
          reason: String(record.kind), severity: 'error', origin: 'recordPageError',
          key: fnv1a64(JSON.stringify([record.kind, record.message || null, state.phase, document.readyState])),
          context: record,
        });
      } catch (_) {}
    }
  }
  function normalizeCompactText(value) {
    return normalizeLineEndings(value).replace(/\s+/g, ' ').trim();
  }
  function isEligibleRoute() {
    return !/^\/codex(?:\/|$)/i.test(location.pathname);
  }
  function conversationIdFromPath(pathname = location.pathname) {
    const match = /^\/c\/([^/?#]+)/.exec(pathname);
    return match ? match[1] : null;
  }
  function isVisible(element) {
    if (!(element instanceof Element)) return false;
    if (element.hidden) return false;
    const style = getComputedStyle(element);
    if (style.display === 'none' || style.visibility === 'hidden' || Number(style.opacity) === 0) return false;
    return element.getClientRects().length > 0;
  }
  // Firefox can retain a fully hydrated Radix menu in a hidden tab while its
  // layout boxes and paint transition remain frozen. Geometry remains mandatory
  // for normal page controls. Only the exact menu named by the live model
  // trigger may use the narrower hidden structural path below.
  function isStructurallyRendered(element) {
    if (!(element instanceof Element) || !element.isConnected || element.hidden || element.getAttribute('aria-hidden') === 'true') return false;
    const style = getComputedStyle(element);
    return style.display !== 'none' && style.visibility !== 'hidden' && Number(style.opacity) !== 0;
  }
  function hiddenModelMenuEvidence(element, suppliedButton = null) {
    const empty = { readable: false, interactive: false, paintSuppressed: false, root: null,
      itemCount: 0, blockers: ['not-an-exact-hidden-model-menu'], style: null };
    if (!document.hidden || !(element instanceof Element)) return empty;
    const button = suppliedButton || findModelButton();
    const id = button?.getAttribute('aria-controls');
    const root = id ? document.getElementById(id) : null;
    if (!button || !root || !(element === root || root.contains(element))) return empty;
    const style = getComputedStyle(root);
    const triggerOpen = button.getAttribute('aria-expanded') === 'true' || button.getAttribute('data-state') === 'open';
    const stateValue = root.getAttribute('data-state');
    const stateOpen = !stateValue || stateValue === 'open';
    const items = Array.from(root.querySelectorAll(MODEL_MENU_ITEM_SELECTOR));
    const text = normalizeCompactText(root.textContent || '');
    const modelLike = !!root.querySelector('[role="slider"][aria-valuemax]')
      || items.some(item => modelCandidateLabelAllowed(cleanElementVisibleText(item)))
      || /\b(?:model|latest|gpt|pro|thinking effort|power)\b/i.test(text);
    const role = root.getAttribute('role');
    const populated = items.length > 0 && modelLike
      && (role === 'menu' || role === 'listbox' || root.hasAttribute('data-radix-menu-content'));
    const blockers = [];
    if (!root.isConnected) blockers.push('disconnected');
    if (root.hidden) blockers.push('hidden-attribute');
    if (!triggerOpen) blockers.push('trigger-not-open');
    if (!stateOpen) blockers.push('menu-state-not-open');
    if (style.display === 'none') blockers.push('display-none');
    if (style.visibility === 'hidden' || style.visibility === 'collapse') blockers.push(`visibility-${style.visibility}`);
    if (!populated) blockers.push('menu-not-populated');
    const readable = blockers.length === 0;
    const ariaHidden = root.getAttribute('aria-hidden') === 'true';
    const inert = root.hasAttribute('inert') || root.inert === true;
    const rectCount = (() => { try { return root.getClientRects().length; } catch (_) { return 0; } })();
    const paintSuppressed = readable && (!isVisible(root) || !rectCount || Number(style.opacity) === 0 || style.pointerEvents === 'none');
    return { readable, interactive: readable && !ariaHidden && !inert, paintSuppressed, root,
      controlledByTrigger: true, triggerOpen, stateOpen, populated, itemCount: items.length,
      modelLike, ariaHidden, inert, rectCount, blockers, textHash: fnv1a64(text),
      style: { display: style.display, visibility: style.visibility, opacity: style.opacity, pointerEvents: style.pointerEvents } };
  }
  function hiddenModelMenuItemUsable(element, suppliedButton = null) {
    if (!(element instanceof Element) || !element.isConnected || element.hidden || element.getAttribute('aria-hidden') === 'true') return false;
    const evidence = hiddenModelMenuEvidence(element, suppliedButton);
    if (!evidence.readable) return false;
    const style = getComputedStyle(element);
    return style.display !== 'none' && style.visibility !== 'hidden' && style.visibility !== 'collapse';
  }
  function modelSurfaceUsable(element, suppliedButton = null) {
    return isVisible(element) || hiddenModelMenuItemUsable(element, suppliedButton);
  }
  function isEnabled(element) {
    if (!(element instanceof Element)) return false;
    if ('disabled' in element && element.disabled) return false;
    return element.getAttribute('aria-disabled') !== 'true';
  }
  function uniqueElements(selectors, root = document) {
    const seen = new Set();
    const output = [];
    for (const selector of selectors) {
      let nodes = [];
      state.metrics.selectorQueries += 1;
      try {
        nodes = root.querySelectorAll(selector);
      } catch (_) {
        nodes = [];
      }
      for (const node of nodes) {
        if (!seen.has(node)) {
          seen.add(node);
          output.push(node);
        }
      }
    }
    return output;
  }
  function firstVisible(selectors, root = document, { enabled = false } = {}) {
    for (const element of uniqueElements(selectors, root)) {
      if (!isVisible(element)) continue;
      if (enabled && !isEnabled(element)) continue;
      return element;
    }
    return null;
  }
  function q(selector, root = document) {
    state.metrics.selectorQueries += 1;
    try { return root.querySelector(selector); } catch (_) { return null; }
  }
  function qa(selector, root = document) {
    state.metrics.selectorQueries += 1;
    try { return Array.from(root.querySelectorAll(selector)); } catch (_) { return []; }
  }
  const STRONG_COMPOSER_SELECTOR_COUNT = 6;
  const STRONG_SEND_SELECTOR_COUNT = 4;
  function composerScopeElement(composer) {
    if (!(composer instanceof Element)) return null;
    return composer.closest('form[data-chatgpt-composer],form,[data-chatgpt-composer]') || composer.parentElement;
  }
  function controlBelongsToComposer(control, composer) {
    if (!(control instanceof Element) || !(composer instanceof Element)) return false;
    const composerForm = composer.closest('form');
    const controlForm = control.closest('form');
    if (composerForm || controlForm) return !!composerForm && controlForm === composerForm;
    const composerRoot = composer.closest('[data-chatgpt-composer]');
    const controlRoot = control.closest('[data-chatgpt-composer]');
    if (composerRoot || controlRoot) return !!composerRoot && controlRoot === composerRoot;
    const scope = composerScopeElement(composer);
    return !!scope && (scope === control || scope.contains(control));
  }
  function findComposer() {
    const strong = firstVisible(SELECTORS.composer.slice(0, STRONG_COMPOSER_SELECTOR_COUNT), document, { enabled: true });
    if (strong) return strong;
    // The placeholder-only textarea adapter is weak. Accept it only when its
    // own shell also contains a send-like control, never merely because some
    // unrelated support/search textarea contains the word “message”.
    for (const candidate of uniqueElements(SELECTORS.composer.slice(STRONG_COMPOSER_SELECTOR_COUNT), document)) {
      if (!isVisible(candidate) || !isEnabled(candidate)) continue;
      const scope = composerScopeElement(candidate);
      if (!scope) continue;
      const controls = uniqueElements([
        '[data-testid="send-button"]',
        '#composer-submit-button:not([data-testid="stop-button"])',
        'button[aria-label="Send prompt"]',
        'button[aria-label="Send"]',
        'button[type="submit"]',
      ], scope);
      if (controls.some(control => isVisible(control) && isEnabled(control) && controlBelongsToComposer(control, candidate))) return candidate;
    }
    return null;
  }
  function findSendButton() {
    const composer = findComposer();
    if (!composer) return null;
    const scope = composerScopeElement(composer) || document;
    const strong = uniqueElements(SELECTORS.send.slice(0, STRONG_SEND_SELECTOR_COUNT), scope)
      .find(control => isVisible(control) && isEnabled(control) && control.getAttribute('data-testid') !== 'stop-button' && controlBelongsToComposer(control, composer));
    if (strong) return strong;
    // A generic submit button is never searched page-wide. It must belong to
    // the exact composer form/shell whose draft qomrade verified.
    for (const button of scope.querySelectorAll('button')) {
      if (!isVisible(button) || !isEnabled(button) || !controlBelongsToComposer(button, composer)) continue;
      const testId = button.getAttribute('data-testid') || '';
      const aria = button.getAttribute('aria-label') || '';
      if (/stop/i.test(testId) || /^stop/i.test(aria)) continue;
      if (/send/i.test(testId) || /send/i.test(aria) || button.type === 'submit') return button;
    }
    return null;
  }
  function findStopButton() {
    return firstVisible(SELECTORS.stop, document, { enabled: true });
  }
  function findModelButton() {
    const direct = firstVisible(SELECTORS.model, document, { enabled: true });
    if (direct) return direct;
    const composer = findComposer();
    const scope = composer && (composer.closest('form') || composer.parentElement);
    if (!scope) return null;
    for (const button of scope.querySelectorAll('button[aria-haspopup="menu"]')) {
      if (!isVisible(button) || !isEnabled(button)) continue;
      const aria = button.getAttribute('aria-label') || '';
      const text = cleanVisibleText(button.textContent || '');
      if (/model/i.test(aria) || /\bpro\b/i.test(text) || /\b(?:5\.6|6(?:\.\d+)?)\b/.test(text)) return button;
    }
    return null;
  }
  function parseModelVersion(label) {
    const source = normalizeCompactText(String(label || '').replace(/,/g, '.'));
    const patterns = [
      /(?:^|\b)gpt\s*[- ]?\s*(\d+(?:\.\d+){0,2})(?=$|\s|pro\b)/i,
      /^\s*(\d+(?:\.\d+){1,2})(?=$|\s)/i,
      /^\s*(\d+)(?=\s+(?:thinking|sol|instant|auto|pro)\b)/i,
      /^\s*(\d+(?:\.\d+){0,2})\s*pro(?:\b|$)/i,
      /^\s*(\d+(?:\.\d+){0,2})\s*$/,
    ];
    let match = null;
    for (const pattern of patterns) { match = source.match(pattern); if (match) break; }
    if (!match) return null;
    const parts = match[1].split('.').map(value => Number.parseInt(value, 10));
    return parts.length && parts.every(Number.isFinite) ? parts : null;
  }
  function compareModelVersions(a, b) {
    const aa = Array.isArray(a) ? a : [];
    const bb = Array.isArray(b) ? b : [];
    const length = Math.max(aa.length, bb.length, 3);
    for (let index = 0; index < length; index += 1) {
      const av = aa[index] || 0;
      const bv = bb[index] || 0;
      if (av !== bv) return av > bv ? 1 : -1;
    }
    return 0;
  }
  function normalizeModelPolicy(value) {
    return MODEL_POLICY_VALUES.includes(String(value || '')) ? String(value) : MODEL_POLICY_SMART_PRO;
  }
  function normalizeModelEffortPolicy(value) {
    return MODEL_EFFORT_VALUES.includes(String(value || '')) ? String(value) : 'pro';
  }
  function modelRouteKey(label) {
    const normalized = normalizeCompactText(String(label || '')).toLocaleLowerCase('en-US');
    if (!normalized) return '';
    const slug = normalized.normalize('NFKD').replace(/[\u0300-\u036f]/g, '').replace(/[^a-z0-9.]+/g, '-').replace(/^-+|-+$/g, '') || 'model';
    return `${slug.slice(0, 96)}--${fnv1a64(normalized).slice(0, 12)}`;
  }
  function normalizeModelVersionHint(value, fallbackLabel = '') {
    const source = Array.isArray(value) ? value : parseModelVersion(fallbackLabel);
    if (!Array.isArray(source) || !source.length) return null;
    const normalized = source.slice(0, 3).map(part => Number.parseInt(part, 10));
    return normalized.every(part => Number.isFinite(part) && part >= 0) ? normalized : null;
  }
  function modelRouteSemanticStem(label) {
    return normalizeCompactText(String(label || ''))
      .toLocaleLowerCase('en-US')
      .replace(/^gpt\s*[- ]?\s*/i, '')
      .replace(/[^a-z0-9.]+/g, '');
  }
  function modelVersionHintsEqual(a, b) {
    const aa = normalizeModelVersionHint(a);
    const bb = normalizeModelVersionHint(b);
    return !!aa && !!bb && compareModelVersions(aa, bb) === 0;
  }
  function sameExactModelRoute(a, b) {
    const aa = modelRouteKey(a);
    const bb = modelRouteKey(b);
    return !!aa && aa === bb;
  }
  function modelPolicySnapshot(source = settings) {
    const policy = normalizeModelPolicy(source && source.modelPolicy);
    const pinned = policy === MODEL_POLICY_PIN;
    const label = pinned ? trunc(source && source.modelTargetLabel || '', 180) : '';
    return {
      policy,
      target: {
        label,
        key: pinned ? trunc(source && source.modelTargetKey || modelRouteKey(label), 220) : '',
        version: pinned ? normalizeModelVersionHint(source && source.modelTargetVersion, label) : null,
        effort: pinned ? normalizeModelEffortPolicy(source && source.modelTargetEffort) : 'keep',
      },
    };
  }
  function activeModelPolicySnapshot() {
    if (state.running) {
      const label = trunc(state.modelGate.target && state.modelGate.target.label || '', 180);
      return {
        policy: normalizeModelPolicy(state.modelGate.runPolicy),
        target: {
          label,
          key: trunc(state.modelGate.target && state.modelGate.target.key || '', 220),
          version: normalizeModelVersionHint(state.modelGate.target && state.modelGate.target.version, label),
          effort: normalizeModelEffortPolicy(state.modelGate.target && state.modelGate.target.effort),
        },
      };
    }
    return modelPolicySnapshot(settings);
  }
  function modelPolicySummary(snapshot = activeModelPolicySnapshot()) {
    if (snapshot.policy === MODEL_POLICY_PIN) {
      const target = snapshot.target.label || 'choose a model';
      return `Pin ${target} · ${MODEL_EFFORT_LABELS[snapshot.target.effort] || snapshot.target.effort}`;
    }
    if (snapshot.policy === MODEL_POLICY_FOLLOW) return 'Follow ChatGPT selection · any available tier';
    return 'Smart Pro · GPT-5.6 first; GPT-6 only until fallback succeeds';
  }
  function applyModelPolicyToRun(origin = 'operator-start') {
    const snapshot = modelPolicySnapshot(settings);
    state.modelGate.runPolicy = snapshot.policy;
    state.modelGate.target = { ...snapshot.target };
    state.modelGate.runPreference = snapshot.policy === MODEL_POLICY_SMART_PRO ? '5.6-first'
      : snapshot.policy === MODEL_POLICY_PIN ? 'pinned' : 'follow';
    state.modelGate.lastPreferenceSwitch = null;
    state.modelGate.confirmed = null;
    state.modelGate.lastCommit = null;
    state.modelGate.nextSurveyAt = 0;
    logEvent('model-policy-applied', `Applied ${modelPolicySummary(snapshot)}.`, { origin, ...snapshot });
    return snapshot;
  }
  function applyModelPolicySettingChange(origin = 'operator-model-policy-change') {
    settings.modelPolicy = normalizeModelPolicy(settings.modelPolicy);
    settings.modelTargetEffort = normalizeModelEffortPolicy(settings.modelTargetEffort);
    settings.modelTargetLabel = trunc(settings.modelTargetLabel || '', 180);
    settings.modelTargetKey = trunc(settings.modelTargetKey || modelRouteKey(settings.modelTargetLabel), 220);
    settings.modelTargetVersion = normalizeModelVersionHint(settings.modelTargetVersion, settings.modelTargetLabel);
    settings.autoSelectEligiblePro = settings.modelPolicy !== MODEL_POLICY_FOLLOW;
    if (state.running) {
      revokeEffectAuthority(origin);
      applyModelPolicyToRun(origin);
      if (!state.paused) scheduleTick(0, origin);
    }
    state.uiModelObservation = null;
  }
  function modelLabelIndicatesPro(label) {
    // Compact labels such as 5.6Pro have no ordinary word boundary before P.
    return /(?:^|[^a-z])pro(?:$|[^a-z])/i.test(String(label || ''));
  }
  function modelLabelIsTransient(label) {
    const compact = normalizeCompactText(label).toLowerCase();
    return !compact || /^(?:thinking effort|instant|low|medium|high|extra high|pro|select chatgpt model)$/.test(compact);
  }
  function modelVersionIsAllowed(version) {
    return Array.isArray(version) && compareModelVersions(version, [5, 5]) > 0;
  }
  function modelVersionIsPreferred56(version) {
    return Array.isArray(version) && (version[0] || 0) === 5 && (version[1] || 0) === 6;
  }
  function modelVersionIsExplicitSixOrNewer(version) {
    return Array.isArray(version) && (version[0] || 0) >= 6;
  }
  function modelCandidateLabelAllowed(label) {
    const compact = normalizeCompactText(label);
    if (!compact || compact.length > 180) return false;
    if (/\b(?:reset to default|power|thinking effort|fast|temporary chat|chat|work|legacy)\b/i.test(compact) && !/\bgpt\b|\d/.test(compact)) return false;
    if (/\blatest\b/i.test(compact)) return true;
    return modelVersionIsAllowed(parseModelVersion(compact));
  }
  function modelCandidateScore(label, menuIndex = 999, preference = '5.6-first') {
    const compact = normalizeCompactText(label);
    const version = parseModelVersion(compact);
    const latest = /\blatest\b/i.test(compact);
    const preferSix = preference === '6-fallback';
    let score = 0;
    // The ordinary run starts 5.6-first. When 5.6 cannot be selected at Pro or
    // a 5.6-backed request reaches an explicit terminal failure, the current
    // unresolved lineage uses 6-first fallback. A stable successful reply resets
    // the next ordinary turn to 5.6-first. Latest stays provisional because its
    // family must still be exposed and confirmed before Send.
    if (preferSix) {
      if (modelVersionIsExplicitSixOrNewer(version)) score += 4_000_000_000;
      else if (latest) score += 3_000_000_000;
      else if (modelVersionIsPreferred56(version)) score += 2_000_000_000;
      else if (version) score += 1_000_000_000;
    } else {
      if (modelVersionIsPreferred56(version)) score += 4_000_000_000;
      else if (modelVersionIsExplicitSixOrNewer(version)) score += 3_000_000_000;
      else if (version) score += 2_000_000_000;
      else if (latest) score += 1_000_000_000;
    }
    if (version) {
      score += (version[0] || 0) * 10_000_000;
      score += (version[1] || 0) * 100_000;
      score += (version[2] || 0) * 1_000;
    }
    if (/\bthinking\b/i.test(compact)) score += 200;
    if (/\bsol\b/i.test(compact)) score += 100;
    score -= Number.isFinite(menuIndex) ? menuIndex : 999;
    return score;
  }
  function cleanElementVisibleText(element) {
    if (!element) return '';
    let value = element.textContent || '';
    try {
      const clone = element.cloneNode(true);
      for (const hidden of clone.querySelectorAll('[aria-hidden="true"]')) hidden.remove();
      value = clone.textContent || value;
    } catch (_) {}
    return cleanVisibleText(value);
  }
  function directModelObservation() {
    const button = findModelButton();
    if (!button) {
      return { present: false, ok: false, directOk: false, reason: 'model selector not found', label: '', family: null, version: null, hasPro: false, transient: false, effortAttribute: null, element: null };
    }
    const visibleText = cleanElementVisibleText(button);
    const label = cleanVisibleText(`${button.getAttribute('aria-label') || ''} ${visibleText}`);
    const version = parseModelVersion(label);
    const family = version ? Number(version.slice(0, 2).join('.')) : null;
    const hasPro = modelLabelIndicatesPro(label);
    const transient = modelLabelIsTransient(visibleText || label);
    let reason = 'visible eligible Pro model confirmed';
    let ok = true;
    if (!hasPro) {
      ok = false;
      reason = `selected model is not visibly Pro (${visibleText || label || 'unlabeled'})`;
    } else if (settings.requireVisibleFamily && !version) {
      ok = false;
      reason = `Pro is visible, but the model family is not visible (${visibleText || label || 'unlabeled'})`;
    } else if (version && !modelVersionIsAllowed(version)) {
      ok = false;
      reason = `visible model family ${version.join('.')} is GPT-5.5 or older`;
    }
    return { present: true, ok, directOk: ok, reason, label: visibleText || label, family, version, hasPro, transient,
      effortAttribute: button.getAttribute('data-selected-reasoning-effort'), element: button };
  }
  function currentModelObservation() {
    const direct = directModelObservation();
    const confirmed = state.modelGate && state.modelGate.confirmed;
    const confirmationAgeMs = confirmed && confirmed.confirmedT ? Math.max(0, Date.now() - confirmed.confirmedT) : null;
    return {
      ...direct,
      lastConfirmed: confirmed ? { ...confirmed, ageMs: confirmationAgeMs } : null,
      evidenceSource: direct.ok ? 'visible-pill' : confirmed ? 'last-bounded-menu-confirmation' : 'visible-pill-only',
    };
  }
  // @QOMRADE-CHUNK id=25.models title="Bounded automatic newest-eligible-Pro discovery, selection, effort, and confirmation"
  const MODEL_MENU_ITEM_SELECTOR = '[role="menuitem"],[role="menuitemradio"],[role="option"],[role="radio"]';
  const MODEL_MENU_CONTAINER_SELECTORS = [
    '[data-radix-menu-content][data-state="open"]',
    '[role="menu"][data-state="open"]',
    '[role="listbox"]',
    '[data-radix-popper-content-wrapper] [role="menu"]',
    '[data-radix-popper-content-wrapper] [role="listbox"]',
  ];
  let modelMenuSerial = Promise.resolve();
  // Each asynchronous send owns immutable, same-tab authority. An old promise
  // cannot inherit permission from a later Start or Resume. No timer or listener
  // is needed for the token itself; effects cooperatively check after each wait.
  function revokeEffectAuthority(reason) {
    state.effectControl.epoch += 1;
    if (cancelRecoveryRead) cancelRecoveryRead();
    recoveryReplayPermit = null;
    preexistingFailureAdvancePermit = null;
    if (reason !== 'pagehide' || !recoveryNavigationCommitted) state.recoveryResume = null;
    state.effectControl.lastRevocation = { at: nowIso(), reason, epoch: state.effectControl.epoch };
    state.scheduler.pendingWake = null;
  }
  function createEffectGuard() {
    const epoch = state.effectControl.epoch;
    const operation = { id: `effect-${epoch}-${++state.effectControl.operations}`, epoch, startedAt: nowIso(), stage: 'admission', pathname: location.pathname };
    state.effectControl.active = operation;
    const reason = () => {
      if (state.effectControl.epoch !== epoch) return 'authority-revoked';
      if (!state.running) return 'run-stopped';
      if (state.paused) return 'run-paused';
      if (state.quarantine) return 'quarantined';
      if (!isEligibleRoute()) return 'ineligible-route';
      if (state.anchorConversationId && conversationIdFromPath() !== state.anchorConversationId) return 'conversation-changed';
      if (pauseForHidden() && document.hidden) return 'hidden-tab';
      if (panelEditorFocused()) return 'panel-editor-focused';
      return null;
    };
    const guard = stage => {
      operation.stage = stage;
      const cancelled = reason();
      if (!cancelled) return;
      const error = new Error(`qomrade effect cancelled: ${cancelled} at ${stage}`);
      error.qomradeEffectCancelled = true;
      error.receipt = { ...operation, cancelledAt: nowIso(), currentEpoch: state.effectControl.epoch, reason: cancelled, revocation: state.effectControl.lastRevocation, draftDisposition: stage === 'send-click-returned' ? 'native-send-already-dispatched-no-cleanup' : 'left-unchanged', automaticRecovery: false };
      throw error;
    };
    guard.valid = () => !reason();
    guard.operation = operation;
    return guard;
  }
  function effectCheckpoint(guard, stage) {
    if (guard) guard(stage);
  }
  async function effectWait(ms, guard, stage) {
    effectCheckpoint(guard, `${stage}:before-wait`);
    await sleep(ms);
    effectCheckpoint(guard, `${stage}:after-wait`);
    invalidateTurnCache('effect-wait-resumed');
  }
  function recordEffectCancellation(error) {
    state.effectControl.cancellations += 1;
    state.effectControl.lastCancellation = error.receipt;
    logEvent('effect-cancelled', 'Cancelled asynchronous work cannot click, focus, insert, clear a draft, or inherit a later run.', error.receipt);
    // This late receipt updates evidence, never the control state of a newer run.
    if (error.receipt.epoch === state.effectControl.epoch && state.running && !state.paused) {
      if (error.receipt.reason === 'panel-editor-focused') {
        clearControllerTimer('operator editor owns focus');
        setPhase('PANEL_EDIT_HOLD', 'Operator editing cancelled the pending send; any composer text remains untouched.');
      } else if (error.receipt.reason === 'hidden-tab') {
        clearControllerTimer('hidden-tab effect cancellation');
        setPhase('SURFACE_HOLD', 'The hidden tab cancelled pending browser effects; any composer text remains untouched.');
      } else if (['conversation-changed', 'ineligible-route'].includes(error.receipt.reason)) {
        stopRun('Navigation cancelled pending browser effects.', { error: { kind: error.receipt.reason, cancellation: error.receipt } });
      }
    }
    persistContinuity('effect-cancelled');
  }
  function serializeModelMenu(operation) {
    const result = modelMenuSerial.then(operation, operation);
    modelMenuSerial = result.then(() => undefined, () => undefined);
    return result;
  }
  function modelMenuContainers() {
    const button = findModelButton();
    const candidates = [];
    const controlledId = button && button.getAttribute('aria-controls');
    const controlled = controlledId ? document.getElementById(controlledId) : null;
    if (controlled) candidates.push(controlled);
    for (const selector of MODEL_MENU_CONTAINER_SELECTORS) {
      for (const node of qa(selector)) if (!candidates.includes(node)) candidates.push(node);
    }
    return candidates.filter(container => {
      const background = hiddenModelMenuEvidence(container, button);
      if (!(isVisible(container) || background.readable)) return false;
      const stateValue = container.getAttribute('data-state');
      if (stateValue && stateValue !== 'open') return false;
      if (container.getAttribute('aria-hidden') === 'true' && !background.readable) return false;
      const text = normalizeCompactText(container.textContent || '');
      const hasSlider = !!q('[role="slider"][aria-valuemax]', container);
      const hasCandidate = qa(MODEL_MENU_ITEM_SELECTOR, container).some(item => modelCandidateLabelAllowed(cleanElementVisibleText(item)));
      return hasSlider || hasCandidate || /\b(?:model|latest|gpt|pro|thinking effort|power)\b/i.test(text);
    });
  }
  function modelMenuItems() {
    const button = findModelButton();
    const containers = modelMenuContainers();
    const output = [];
    const seen = new Set();
    for (const container of containers) {
      for (const item of qa(MODEL_MENU_ITEM_SELECTOR, container)) {
        if (seen.has(item) || !modelSurfaceUsable(item, button)) continue;
        seen.add(item);
        output.push(item);
      }
    }
    if (output.length || !containers.length) return output;
    // A few Radix layouts portal menu rows beside the content node. This
    // fallback is legal only after a model-like open container exists.
    for (const item of qa(MODEL_MENU_ITEM_SELECTOR)) {
      if (seen.has(item) || !modelSurfaceUsable(item, button)) continue;
      const host = item.closest('[data-radix-menu-content],[role="menu"],[role="listbox"]');
      const background = host ? hiddenModelMenuEvidence(host, button) : null;
      if (!host || !(isVisible(host) || background?.readable)) continue;
      if (host.getAttribute('aria-hidden') === 'true' && !background?.readable) continue;
      seen.add(item);
      output.push(item);
    }
    return output;
  }
  function modelMenuIsOpen() {
    const button = findModelButton();
    return !!(button && (button.getAttribute('aria-expanded') === 'true' || modelMenuContainers().length) && modelMenuItems().length);
  }
  function dispatchModelKey(element, key, guard = null) {
    effectCheckpoint(guard, 'model-key-before-focus');
    try { element.focus(); } catch (_) {}
    for (const type of ['keydown', 'keyup']) {
      effectCheckpoint(guard, `model-key-before-${type}`);
      try { element.dispatchEvent(new KeyboardEvent(type, { key, code: key, bubbles: true, cancelable: true })); }
      catch (_) { return false; }
    }
    return true;
  }
  function activateModelControl(element, guard = null) {
    effectCheckpoint(guard, 'activateModelControl:entry');
    if (!element || !isEnabled(element)) return false;
    if (document.hidden) {
      const background = hiddenModelMenuEvidence(element);
      // Read-only confirmation may use an exact trigger-bound menu whose paint
      // transition is frozen. Mutation still requires the menu not to be inert
      // or aria-hidden; model selection never borrows the broader read permit.
      if (background.root && !background.interactive) return false;
    }
    try { element.click(); return true; }
    catch (_) {
      effectCheckpoint(guard, 'model-activation-fallback');
      return dispatchModelKey(element, 'Enter', guard);
    }
  }
  async function waitForModelMenuOpen(timeoutMs = MODEL_MENU_OPEN_TIMEOUT_MS, guard = null) {
    effectCheckpoint(guard, 'waitForModelMenuOpen:entry');
    const deadline = Date.now() + timeoutMs;
    let observer = null;
    let wake = null;
    let observedMutation = false;
    const observerAvailable = typeof MutationObserver === 'function' && !!document.documentElement;
    if (observerAvailable) {
      state.modelGate.menuObserverWaits += 1;
      observer = new MutationObserver(records => {
        observedMutation = true;
        state.modelGate.menuObserverMutations += records.length;
        if (wake) wake('mutation');
      });
      try {
        observer.observe(document.documentElement, {
          childList: true,
          subtree: true,
          attributes: true,
          attributeFilter: ['aria-expanded','aria-controls','aria-hidden','aria-checked','aria-selected','data-state','data-model-selected','data-maximum','style','class'],
        });
      } catch (_) { observer = null; }
    }
    try {
      while (Date.now() < deadline) {
        if (modelMenuIsOpen()) {
          if (observedMutation) state.modelGate.menuObserverResolutions += 1;
          return true;
        }
        effectCheckpoint(guard, 'waitForModelMenuOpen:loop');
        const remaining = Math.max(1, deadline - Date.now());
        const waitMs = Math.min(remaining, document.hidden ? MODEL_MENU_OBSERVER_HIDDEN_POLL_MS : MODEL_MENU_OBSERVER_VISIBLE_POLL_MS);
        const signal = await new Promise(resolve => {
          let settled = false;
          const finish = value => {
            if (settled) return;
            settled = true;
            clearTimeout(timer);
            if (wake === finish) wake = null;
            resolve(value);
          };
          const timer = setTimeout(() => finish('timer'), waitMs);
          wake = finish;
        });
        effectCheckpoint(guard, `waitForModelMenuOpen:${signal}`);
        invalidateTurnCache(`model-menu-${signal}`);
      }
      const opened = modelMenuIsOpen();
      if (!opened && observer) state.modelGate.menuObserverTimeouts += 1;
      else if (opened && observedMutation) state.modelGate.menuObserverResolutions += 1;
      return opened;
    } finally {
      if (wake) wake('disconnect');
      if (observer) {
        try { observer.disconnect(); } catch (_) {}
      }
    }
  }
  async function openModelMenu({ quiet = false, guard = null } = {}) {
    effectCheckpoint(guard, 'openModelMenu:entry');
    if (!findModelButton()) {
      recordModelMenuSurface('trigger-missing');
      return { ok: false, reason: 'model button not found', method: null, surfaceFailure: true };
    }
    if (modelMenuIsOpen()) {
      const surface = recordModelMenuSurface('already-open');
      noteBackgroundModelMenuAcceptance(surface, 'already-open');
      return { ok: true, reason: surface.backgroundStructuralReady ? 'background-structural-ready' : 'already open', method: 'already-open' };
    }
    if (modelMenuAdvertisedOpen()) {
      if (await waitForModelMenuOpen(document.hidden ? MODEL_MENU_HIDDEN_OPEN_TIMEOUT_MS : MODEL_MENU_OPEN_TIMEOUT_MS, guard)) {
        const surface = recordModelMenuSurface('hydrated-existing-shell');
        noteBackgroundModelMenuAcceptance(surface, 'await-existing-shell');
        return { ok: true, reason: document.hidden ? 'background-structural-hydration' : 'hydrated', method: 'await-existing-shell' };
      }
      if (!await resetIncompleteModelMenu(guard)) return { ok: false, reason: 'model popup is open but its content is unavailable; reset unconfirmed', surfaceFailure: true };
    }
    for (const method of ['click', 'enter', 'arrow-down']) {
      effectCheckpoint(guard, 'model-menu-opening-attempt');
      const button = findModelButton();
      if (!button) break;
      if (method === 'click') activateModelControl(button, guard);
      else dispatchModelKey(button, method === 'enter' ? 'Enter' : 'ArrowDown', guard);
      if (await waitForModelMenuOpen(document.hidden ? MODEL_MENU_HIDDEN_OPEN_TIMEOUT_MS : MODEL_MENU_OPEN_TIMEOUT_MS, guard)) {
        const surface = recordModelMenuSurface('ready-' + method);
        noteBackgroundModelMenuAcceptance(surface, `ready-${method}`);
        logEvent('model-menu-opened', `Opened the model menu with ${method}.`, { method, button: elementSummary(button), background: surface.backgroundStructuralReady ? { paintSuppressed: surface.backgroundPaintSuppressed, interactive: surface.backgroundInteractiveReady } : null });
        return { ok: true, reason: surface.backgroundStructuralReady ? 'opened-background-structural' : 'opened', method };
      }
      recordModelMenuSurface('unready-' + method);
      if (modelMenuAdvertisedOpen() && !await resetIncompleteModelMenu(guard)) break;
    }
    state.modelGate.menuOpenFailures += 1;
    const surface = recordModelMenuSurface('opening-failed');
    if (!quiet) logEvent('model-menu-open-failed', 'Bounded model-menu opening or hydration failed; no Send.', { surface });
    return { ok: false, reason: 'model menu did not expose usable content', method: null, surfaceFailure: true };
  }
  function modelMenuAdvertisedOpen() {
    const button = findModelButton();
    return !!(button && (button.getAttribute('aria-expanded') === 'true'
      || button.getAttribute('data-state') === 'open' || modelMenuContainers().length));
  }
  function recordModelMenuSurface(stage) {
    const button = findModelButton();
    const controlledId = button?.getAttribute('aria-controls') || null;
    const controlled = controlledId ? document.getElementById(controlledId) : null;
    const background = controlled ? hiddenModelMenuEvidence(controlled, button) : null;
    const receipt = { at: nowIso(), stage, hidden: document.hidden,
      triggerExpanded: button?.getAttribute('aria-expanded') || null,
      triggerState: button?.getAttribute('data-state') || null,
      triggerLabel: button ? trunc(cleanElementVisibleText(button), 160) : null,
      controlledId, controlledPresent: !!controlled, controlledVisible: !!(controlled && isVisible(controlled)),
      controlledStructural: !!(controlled && isStructurallyRendered(controlled)),
      controlledRole: controlled?.getAttribute('role') || null,
      controlledAriaHidden: controlled?.getAttribute('aria-hidden') || null,
      controlledDataState: controlled?.getAttribute('data-state') || null,
      controlledText: controlled ? trunc(cleanElementVisibleText(controlled), 240) : null,
      controlledItems: controlled ? qa(MODEL_MENU_ITEM_SELECTOR, controlled).length : 0,
      controlledStyle: background?.style || (controlled ? (() => { const style = getComputedStyle(controlled); return { display: style.display, visibility: style.visibility, opacity: style.opacity, pointerEvents: style.pointerEvents }; })() : null),
      controlledRectCount: background?.rectCount == null ? (controlled ? (() => { try { return controlled.getClientRects().length; } catch (_) { return 0; } })() : 0) : background.rectCount,
      backgroundStructuralReady: !!background?.readable,
      backgroundInteractiveReady: !!background?.interactive,
      backgroundPaintSuppressed: !!background?.paintSuppressed,
      backgroundStructuralBlockers: background?.blockers || [],
      backgroundStructuralBasis: background?.readable ? 'exact-trigger-controlled-populated-menu' : null,
      ready: modelMenuIsOpen() };
    state.modelGate.lastMenuSurface = receipt;
    state.modelGate.menuSurfaceReceipts = [...(state.modelGate.menuSurfaceReceipts || []), receipt].slice(-8);
    return receipt;
  }
  function noteBackgroundModelMenuAcceptance(surface, origin) {
    if (!surface || !surface.hidden || !surface.backgroundStructuralReady || surface.controlledVisible) return;
    const key = fnv1a64(JSON.stringify([surface.controlledId, surface.controlledText, surface.controlledItems,
      surface.controlledDataState, surface.controlledAriaHidden, surface.controlledStyle]));
    if (state.modelGate.lastBackgroundStructuralKey === key) return;
    state.modelGate.lastBackgroundStructuralKey = key;
    state.modelGate.backgroundStructuralAccepts = (state.modelGate.backgroundStructuralAccepts || 0) + 1;
    if (surface.backgroundPaintSuppressed) state.modelGate.backgroundPaintSuppressedAccepts = (state.modelGate.backgroundPaintSuppressedAccepts || 0) + 1;
    state.modelGate.lastBackgroundStructuralAccept = { at: nowIso(), origin, key, controlledId: surface.controlledId,
      items: surface.controlledItems, paintSuppressed: surface.backgroundPaintSuppressed,
      interactive: surface.backgroundInteractiveReady, style: surface.controlledStyle,
      basis: surface.backgroundStructuralBasis };
    logEvent('model-menu-background-structural', 'Accepted the exact populated model menu while hidden even though Firefox had not painted its transition.', state.modelGate.lastBackgroundStructuralAccept);
  }
  function closeModelMenu(guard = null) {
    effectCheckpoint(guard, 'closeModelMenu:entry');
    if (!modelMenuAdvertisedOpen()) return;
    const button = findModelButton();
    const id = button?.getAttribute('aria-controls');
    const target = (id && document.getElementById(id)) || modelMenuContainers()[0];
    if (target) {
      try { target.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', code: 'Escape', bubbles: true, cancelable: true })); } catch (_) {}
    } else if (button) activateModelControl(button, guard);
  }
  async function resetIncompleteModelMenu(guard = null) {
    effectCheckpoint(guard, 'model-menu-reset');
    if (!modelMenuAdvertisedOpen()) return true;
    const before = recordModelMenuSurface('reset-before');
    closeModelMenu(guard);
    await effectWait(180, guard, 'model-menu-reset-close');
    if (modelMenuAdvertisedOpen()) {
      const button = findModelButton();
      if (button) activateModelControl(button, guard);
      await effectWait(180, guard, 'model-menu-reset-trigger');
    }
    if (modelMenuAdvertisedOpen()) {
      const button = findModelButton();
      if (button) dispatchModelKey(button, 'Enter', guard);
      await effectWait(180, guard, 'model-menu-reset-key');
    }
    const closed = !modelMenuAdvertisedOpen();
    state.modelGate.menuRepairs = (state.modelGate.menuRepairs || 0) + 1;
    const after = recordModelMenuSurface('reset-after');
    logEvent('model-menu-reset', closed ? 'Reset incomplete model popup before reopening.' : 'Model popup reset was not confirmed.', { before, after, closed });
    return closed;
  }
  function modelMenuItemRecord(element, index) {
    const text = cleanElementVisibleText(element);
    return {
      index,
      text,
      role: element.getAttribute('role'),
      checked: element.getAttribute('aria-checked') === 'true' || element.getAttribute('aria-selected') === 'true' || element.getAttribute('data-model-selected') === 'true',
      disabled: !isEnabled(element),
      ariaLabel: element.getAttribute('aria-label'),
      dataTestId: element.getAttribute('data-testid'),
      version: parseModelVersion(text),
      element,
    };
  }
  function modelRouteRowIsSelectable(record, { includeDisabled = true } = {}) {
    if (!record || (!includeDisabled && record.disabled)) return false;
    const role = String(record.role || '').toLowerCase();
    const text = normalizeCompactText(record.text);
    if (!['menuitemradio', 'option', 'radio'].includes(role) || !text || text.length > 180) return false;
    if (/select model/i.test(String(record.ariaLabel || ''))) return false;
    if (/^(?:pro|instant|low|medium|high|extra high|thinking effort|power)$/i.test(text)) return false;
    return true;
  }
  function modelRowIsSelectable(record) {
    return modelRouteRowIsSelectable(record, { includeDisabled: false }) && modelCandidateLabelAllowed(record.text);
  }
  function effortSliderFromMenu(containers = modelMenuContainers()) {
    for (const container of containers) {
      const thumb = q('[role="slider"][aria-valuemax]', container);
      if (!thumb) continue;
      const numberAttr = name => {
        const value = Number.parseInt(thumb.getAttribute(name), 10);
        return Number.isFinite(value) ? value : null;
      };
      return {
        thumb,
        row: thumb.closest(MODEL_MENU_ITEM_SELECTOR) || thumb.parentElement,
        min: numberAttr('aria-valuemin'),
        max: numberAttr('aria-valuemax'),
        now: numberAttr('aria-valuenow'),
        valueText: thumb.getAttribute('aria-valuetext'),
      };
    }
    return null;
  }
  function inspectOpenModelMenu({ includeMarkup = false } = {}) {
    const containers = modelMenuContainers();
    const records = modelMenuItems().map(modelMenuItemRecord);
    const routeRows = records.filter(record => modelRouteRowIsSelectable(record, { includeDisabled: true }));
    const modelRows = routeRows.filter(modelRowIsSelectable);
    const selected = routeRows.find(record => record.checked) || null;
    const proRow = records.find(record => /^\s*pro\s*$/i.test(record.text)) || null;
    const slider = effortSliderFromMenu(containers);
    let viewToggle = null;
    for (const container of containers) {
      viewToggle = q('[data-model-picker-view-toggle]', container) || q('[aria-label="Select model"]', container);
      if (viewToggle) break;
    }
    const maximumMarker = !!(viewToggle && q('[data-maximum="true"]', viewToggle)) || containers.some(container => !!q('[data-maximum="true"]', container));
    const viewToggleLabel = cleanElementVisibleText(viewToggle);
    const publicRecord = (record, withMarkup = false) => {
      if (!record) return null;
      const result = {
        index: record.index,
        text: record.text,
        role: record.role,
        checked: record.checked,
        disabled: record.disabled,
        ariaLabel: record.ariaLabel,
        dataTestId: record.dataTestId,
        version: record.version,
      };
      if (withMarkup) {
        const markup = String(record.element && record.element.outerHTML || '');
        result.markup = { chars: markup.length, hash: fnv1a64(markup), head: trunc(markup, MODEL_SURVEY_MARKUP_HEAD_CHARS) };
      }
      return result;
    };
    return {
      at: nowIso(),
      button: (() => { const observed = directModelObservation(); return { label: observed.label, family: observed.family, hasPro: observed.hasPro, transient: observed.transient }; })(),
      containerCount: containers.length,
      // Markup is retained once per unique menu row. Derived route/model lists
      // remain compact references so one survey does not triple the same DOM.
      items: records.slice(0, 24).map(record => publicRecord(record, includeMarkup)),
      routeRows: routeRows.slice(0, 24).map(record => publicRecord(record, false)),
      modelRows: modelRows.slice(0, 16).map(record => publicRecord(record, false)),
      selectedRoute: selected ? selected.text : null,
      selectedRouteKey: selected ? modelRouteKey(selected.text) : null,
      selectedModel: selected ? selected.text : null,
      viewToggleLabel,
      maximumMarker,
      proRow: publicRecord(proRow, false),
      slider: slider ? { min: slider.min, max: slider.max, now: slider.now, valueText: slider.valueText } : null,
      effortAttribute: findModelButton() && findModelButton().getAttribute('data-selected-reasoning-effort'),
      _elements: { records, routeRows, modelRows, selected, proRow, slider, viewToggle },
    };
  }
  function stripModelInspection(inspection) {
    if (!inspection) return null;
    const copy = { ...inspection };
    delete copy._elements;
    return copy;
  }
  function sameModelFamily(a, b) {
    const av = parseModelVersion(a);
    const bv = parseModelVersion(b);
    if (av && bv) return compareModelVersions(av, bv) === 0;
    const aa = String(a || '').toLowerCase().replace(/[^a-z0-9.]+/g, '');
    const bb = String(b || '').toLowerCase().replace(/[^a-z0-9.]+/g, '');
    if (/latest/.test(aa) || /latest/.test(bb)) return aa === bb;
    return !!aa && !!bb && (aa.includes(bb) || bb.includes(aa));
  }
  async function setEffortToMaximum(inspection, guard = null) {
    effectCheckpoint(guard, 'setEffortToMaximum:entry');
    let slider = inspection && inspection._elements && inspection._elements.slider;
    if (!slider || slider.now == null || slider.max == null) return { ok: false, reason: 'no usable effort slider', before: inspection && inspection.slider };
    const before = { min: slider.min, max: slider.max, now: slider.now };
    const target = slider.max;
    let focus = slider.row || slider.thumb;
    try { focus.focus(); } catch (_) {}
    let presses = 0;
    while (presses < 16) {
      slider = effortSliderFromMenu();
      if (!slider || slider.now == null || slider.now >= target) break;
      focus = slider.row || slider.thumb || focus;
      for (const type of ['keydown', 'keyup']) {
        effectCheckpoint(guard, `model-effort-before-${type}`);
        try { focus.dispatchEvent(new KeyboardEvent(type, { key: 'ArrowRight', code: 'ArrowRight', keyCode: 39, which: 39, bubbles: true, cancelable: true })); } catch (_) {}
      }
      presses += 1;
      state.modelGate.effortSteps += 1;
      await effectWait(MODEL_EFFORT_STEP_MS, guard, 'setEffortToMaximum');
    }
    slider = effortSliderFromMenu();
    return {
      ok: !!slider && slider.now != null && slider.now >= target,
      before,
      after: slider ? { min: slider.min, max: slider.max, now: slider.now } : null,
      presses,
    };
  }
  async function setEffortToIndex(inspection, targetIndex, guard = null) {
    effectCheckpoint(guard, 'setEffortToIndex:entry');
    let slider = inspection && inspection._elements && inspection._elements.slider;
    if (!slider || slider.now == null || slider.min == null || slider.max == null) {
      return { ok: false, reason: 'no usable effort slider', target: targetIndex, before: inspection && inspection.slider };
    }
    const target = Math.max(slider.min, Math.min(slider.max, Number(targetIndex)));
    const before = { min: slider.min, max: slider.max, now: slider.now, valueText: slider.valueText || null };
    let presses = 0;
    while (presses < 24) {
      slider = effortSliderFromMenu();
      if (!slider || slider.now == null || slider.now === target) break;
      const direction = slider.now < target ? 'ArrowRight' : 'ArrowLeft';
      const focus = slider.row || slider.thumb;
      try { focus.focus(); } catch (_) {}
      for (const type of ['keydown', 'keyup']) {
        effectCheckpoint(guard, `model-effort-${direction}-${type}`);
        try { focus.dispatchEvent(new KeyboardEvent(type, { key: direction, code: direction, keyCode: direction === 'ArrowRight' ? 39 : 37, which: direction === 'ArrowRight' ? 39 : 37, bubbles: true, cancelable: true })); } catch (_) {}
      }
      presses += 1;
      state.modelGate.effortSteps += 1;
      await effectWait(MODEL_EFFORT_STEP_MS, guard, 'setEffortToIndex');
    }
    slider = effortSliderFromMenu();
    return {
      ok: !!slider && slider.now === target,
      target,
      before,
      after: slider ? { min: slider.min, max: slider.max, now: slider.now, valueText: slider.valueText || null } : null,
      presses,
    };
  }
  function effortTargetIndex(inspection, effortPolicy) {
    const policy = normalizeModelEffortPolicy(effortPolicy);
    const slider = inspection && inspection.slider;
    if (!slider || slider.min == null || slider.max == null || slider.now == null) return policy === 'keep' ? null : undefined;
    const min = slider.min;
    const max = slider.max;
    const proRow = inspection && inspection.proRow;
    const proAvailable = !!(proRow && !proRow.disabled) || !!(inspection && inspection.maximumMarker && modelLabelIndicatesPro(inspection.viewToggleLabel));
    const highestNonPro = Math.max(min, proAvailable ? max - 1 : max);
    const fullSpan = Math.max(0, max - min);
    if (policy === 'keep') return slider.now;
    if (policy === 'minimum') return min;
    if (policy === 'low') return Math.min(highestNonPro, min + Math.max(1, Math.floor(fullSpan / 3)));
    if (policy === 'medium') return Math.min(highestNonPro, Math.round((min + max) / 2));
    if (policy === 'high') return highestNonPro;
    if (policy === 'pro') return max;
    return undefined;
  }
  async function setSelectedEffortInOpenMenu(effortPolicy, initialInspection = null, guard = null) {
    effectCheckpoint(guard, 'setSelectedEffortInOpenMenu:entry');
    const policy = normalizeModelEffortPolicy(effortPolicy);
    let inspection = initialInspection && initialInspection._elements ? initialInspection : inspectOpenModelMenu({ includeMarkup: true });
    if (policy === 'keep') return { ok: true, policy, targetIndex: inspection.slider && inspection.slider.now, changed: false, inspection: stripModelInspection(inspection) };
    const targetIndex = effortTargetIndex(inspection, policy);
    if (targetIndex === undefined) return { ok: false, policy, reason: 'the selected model exposes no usable effort control', inspection: stripModelInspection(inspection) };
    let movement = await setEffortToIndex(inspection, targetIndex, guard);
    await effectWait(MODEL_MENU_SETTLE_MS, guard, 'setSelectedEffortInOpenMenu');
    if (!modelMenuIsOpen()) {
      const reopened = await openModelMenu({ quiet: true, guard });
      if (!reopened.ok) return { ok: false, policy, targetIndex, reason: reopened.reason, movement };
      await effectWait(MODEL_MENU_SETTLE_MS, guard, 'setSelectedEffortInOpenMenu');
    }
    inspection = inspectOpenModelMenu({ includeMarkup: true });
    if (policy === 'high' && inspection.slider && inspection.slider.now === inspection.slider.max
        && (inspection.maximumMarker || (inspection.proRow && inspection.proRow.checked))) {
      movement = await setEffortToIndex(inspection, Math.max(inspection.slider.min, inspection.slider.max - 1), guard);
      await effectWait(MODEL_MENU_SETTLE_MS, guard, 'setSelectedEffortInOpenMenu-non-pro');
      inspection = inspectOpenModelMenu({ includeMarkup: true });
    }
    let clickedProRow = false;
    if (policy === 'pro') {
      const proRecord = inspection._elements.proRow;
      if (proRecord && !proRecord.disabled && !proRecord.checked) {
        clickedProRow = activateModelControl(proRecord.element, guard);
        if (clickedProRow) await effectWait(MODEL_SELECTION_SETTLE_MS, guard, 'setSelectedEffortInOpenMenu');
        if (!modelMenuIsOpen()) {
          const reopened = await openModelMenu({ quiet: true, guard });
          if (reopened.ok) await effectWait(MODEL_MENU_SETTLE_MS, guard, 'setSelectedEffortInOpenMenu');
        }
        inspection = inspectOpenModelMenu({ includeMarkup: true });
      }
    }
    const actualIndex = inspection.slider && inspection.slider.now;
    movement = { ...movement, after: inspection.slider };
    return { ok: actualIndex === targetIndex, policy, targetIndex, actualIndex, changed: movement.presses > 0 || clickedProRow, clickedProRow, movement, inspection: stripModelInspection(inspection), _inspection: inspection };
  }
  function flexibleModelConfirmation(inspection, snapshot) {
    const direct = directModelObservation();
    const selectedLabel = inspection && (inspection.selectedRoute || inspection.selectedModel);
    const selectedKey = modelRouteKey(selectedLabel);
    const labels = [inspection && inspection.viewToggleLabel, direct.label, selectedLabel].filter(Boolean);
    let concreteLabel = selectedLabel || null;
    let version = parseModelVersion(selectedLabel);
    for (const label of labels) {
      const parsed = parseModelVersion(label);
      if (parsed) { concreteLabel = label; version = parsed; break; }
    }
    const proRow = inspection && inspection.proRow;
    const explicitProLabel = labels.some(modelLabelIndicatesPro);
    const checkedProRow = !!(proRow && proRow.checked);
    const maximumEffortProof = !!(inspection && inspection.maximumMarker && inspection.slider
      && inspection.slider.now != null && inspection.slider.max != null && inspection.slider.now >= inspection.slider.max);
    const hasPro = !proRow?.disabled && (explicitProLabel || checkedProRow || maximumEffortProof);
    const policy = normalizeModelPolicy(snapshot && snapshot.policy);
    const target = snapshot && snapshot.target || { label: '', key: '', effort: 'keep' };
    const effortPolicy = normalizeModelEffortPolicy(target.effort);
    const targetIndex = effortTargetIndex(inspection, effortPolicy);
    const actualIndex = inspection && inspection.slider && inspection.slider.now;
    const selectedRecord = inspection && inspection._elements && inspection._elements.selected;
    let ok = !!selectedLabel && !(selectedRecord && selectedRecord.disabled);
    let reason = ok ? 'selected ChatGPT model and effort were confirmed from the live model menu' : 'the live model menu did not expose an enabled selected model route';
    if (ok && policy === MODEL_POLICY_PIN && (!target.key || selectedKey !== target.key)) {
      ok = false;
      reason = `the selected route ${selectedLabel || 'unknown'} does not match pinned ${target.label || target.key || 'target'}`;
    }
    if (ok && policy === MODEL_POLICY_PIN && effortPolicy === 'pro' && !hasPro) {
      ok = false;
      reason = 'the pinned model did not expose confirmed Pro effort';
    }
    if (ok && policy === MODEL_POLICY_PIN && effortPolicy !== 'keep' && effortPolicy !== 'pro' && actualIndex !== targetIndex) {
      ok = false;
      reason = `the selected effort index ${actualIndex} does not match pinned ${effortPolicy} index ${targetIndex}`;
    }
    return {
      ok,
      reason,
      policy,
      target: { label: target.label || '', key: target.key || '', version: normalizeModelVersionHint(target.version, target.label), effort: effortPolicy },
      candidate: selectedLabel,
      selectedLabel,
      routeKey: selectedKey,
      concreteLabel,
      version,
      family: version ? Number(version.slice(0, 2).join('.')) : null,
      hasPro: !!hasPro,
      pill: direct.label,
      effort: {
        policy: effortPolicy,
        index: actualIndex == null ? null : actualIndex,
        targetIndex: targetIndex == null ? null : targetIndex,
        min: inspection && inspection.slider && inspection.slider.min,
        max: inspection && inspection.slider && inspection.slider.max,
        valueText: inspection && inspection.slider && inspection.slider.valueText || null,
        attribute: inspection && inspection.effortAttribute || direct.effortAttribute || null,
      },
      evidence: {
        source: policy === MODEL_POLICY_PIN ? 'pinned-live-menu-confirmation' : 'follow-current-live-menu-confirmation',
        viewToggleLabel: inspection && inspection.viewToggleLabel,
        proRow: inspection && inspection.proRow,
        maximumMarker: !!(inspection && inspection.maximumMarker),
        proSignals: { explicitProLabel, checkedProRow, maximumEffortProof },
      },
    };
  }
  function modelConfirmationFromInspection(inspection, candidateLabel) {
    const direct = directModelObservation();
    const selectedLabel = inspection && inspection.selectedModel;
    const selectedVersion = parseModelVersion(selectedLabel);
    const candidateIsLatest = /\blatest\b/i.test(String(candidateLabel || selectedLabel || ''));
    const labels = [inspection && inspection.viewToggleLabel, direct.label, selectedLabel].filter(Boolean);
    let concreteLabel = null;
    let concreteVersion = null;
    for (const label of labels) {
      const version = parseModelVersion(label);
      if (modelVersionIsAllowed(version) && !(candidateIsLatest && /\blatest\b/i.test(label))) {
        concreteLabel = label;
        concreteVersion = version;
        break;
      }
    }
    if (!concreteVersion && !candidateIsLatest && modelVersionIsAllowed(selectedVersion)) {
      concreteLabel = selectedLabel;
      concreteVersion = selectedVersion;
    }
    const proRow = inspection && inspection.proRow;
    const proBlocked = !!(proRow && proRow.disabled && !proRow.checked);
    const explicitProLabel = labels.some(modelLabelIndicatesPro);
    const checkedProRow = !!(proRow && proRow.checked);
    const maximumEffortProof = !!(inspection && inspection.maximumMarker && inspection.slider
      && inspection.slider.now != null && inspection.slider.max != null && inspection.slider.now >= inspection.slider.max);
    const proConfirmed = !proBlocked && (explicitProLabel || checkedProRow || maximumEffortProof);
    const family = concreteVersion ? Number(concreteVersion.slice(0, 2).join('.')) : null;
    let reason = 'menu evidence did not confirm an eligible concrete Pro model';
    if (proBlocked) reason = 'the selected route exposes a disabled Pro row';
    else if (!concreteVersion) reason = 'the selected route did not reveal a concrete GPT-5.6-or-newer model';
    else if (!proConfirmed) reason = 'the selected model did not expose local Pro confirmation';
    return {
      ok: !!concreteVersion && proConfirmed,
      reason: concreteVersion && proConfirmed ? 'eligible concrete Pro model confirmed from the live model menu' : reason,
      selectedLabel,
      candidateLabel,
      concreteLabel,
      version: concreteVersion,
      family,
      hasPro: proConfirmed,
      directLabel: direct.label,
      viewToggleLabel: inspection && inspection.viewToggleLabel,
      slider: inspection && inspection.slider,
      proRow,
      maximumMarker: !!(inspection && inspection.maximumMarker),
      proSignals: { explicitProLabel, checkedProRow, maximumEffortProof },
    };
  }
  function chooseModelRowFromOpenMenu(candidate, inspection, guard = null) {
    effectCheckpoint(guard, 'chooseModelRowFromOpenMenu:entry');
    const live = inspection && inspection._elements ? inspection : inspectOpenModelMenu({ includeMarkup: true });
    const row = live._elements.modelRows.find(record => sameModelFamily(record.text, candidate.text));
    if (!row) return { ok: false, reason: 'candidate row disappeared', inspection: stripModelInspection(live) };
    if (row.disabled) return { ok: false, reason: 'candidate row is disabled', inspection: stripModelInspection(live) };
    const clicked = !row.checked && activateModelControl(row.element, guard);
    if (clicked) state.modelGate.selections += 1;
    return { ok: row.checked || clicked, clicked, row: { text: row.text, version: row.version, checked: row.checked }, inspection: stripModelInspection(live), reusedOpenMenu: true };
  }
  async function chooseModelRow(candidate, guard = null) {
    effectCheckpoint(guard, 'chooseModelRow:entry');
    const opened = await openModelMenu({ guard });
    if (!opened.ok) return { ok: false, reason: opened.reason };
    await effectWait(MODEL_MENU_SETTLE_MS, guard, 'chooseModelRow');
    const selection = chooseModelRowFromOpenMenu(candidate, inspectOpenModelMenu({ includeMarkup: true }), guard);
    if (selection.clicked) await effectWait(MODEL_SELECTION_SETTLE_MS, guard, 'chooseModelRow');
    closeModelMenu(guard);
    await effectWait(180, guard, 'chooseModelRow');
    return selection;
  }
  function legacyLatestPinnedTarget(target) {
    const label = normalizeCompactText(target && target.label || '').toLocaleLowerCase('en-US');
    const key = target && (target.key || modelRouteKey(target.label));
    return label === 'latest' || key === modelRouteKey('Latest');
  }
  function selectedPinnedRouteResolution(target, live) {
    const rows = live && live._elements && live._elements.routeRows || [];
    const targetKey = target && (target.key || modelRouteKey(target.label));
    const exact = rows.find(record => modelRouteKey(record.text) === targetKey);
    if (exact) return { row: exact, matchKind: 'exact-route-key', alias: false };
    const selectedRows = rows.filter(record => record.checked && !record.disabled);
    if (selectedRows.length !== 1) return null;
    const row = selectedRows[0];
    const rowVersion = normalizeModelVersionHint(row.version, row.text);
    const targetVersion = normalizeModelVersionHint(target && target.version, target && target.label);
    if (legacyLatestPinnedTarget(target) && rowVersion && rowVersion[0] === 6) {
      return { row, matchKind: 'legacy-Latest-to-selected-GPT-6', alias: true, rowVersion, targetVersion };
    }
    const targetStem = modelRouteSemanticStem(target && target.label);
    const rowStem = modelRouteSemanticStem(row.text);
    if (targetVersion && rowVersion && modelVersionHintsEqual(targetVersion, rowVersion)
        && targetStem && rowStem && (targetStem === rowStem || targetStem.startsWith(rowStem) || rowStem.startsWith(targetStem))) {
      return { row, matchKind: 'selected-same-version-label-drift', alias: true, rowVersion, targetVersion };
    }
    return null;
  }
  function reconcilePinnedRouteAlias(target, resolution, origin, guard = null) {
    if (!target || !resolution || !resolution.alias || !resolution.row) return null;
    effectCheckpoint(guard, 'reconcilePinnedRouteAlias:entry');
    const before = {
      label: trunc(target.label || '', 180),
      key: trunc(target.key || modelRouteKey(target.label), 220),
      version: normalizeModelVersionHint(target.version, target.label),
      effort: normalizeModelEffortPolicy(target.effort),
    };
    const after = {
      label: trunc(resolution.row.text || '', 180),
      key: modelRouteKey(resolution.row.text),
      version: normalizeModelVersionHint(resolution.row.version, resolution.row.text),
      effort: before.effort,
    };
    Object.assign(target, after);
    if (state.modelGate.target && (state.modelGate.target.key === before.key || modelRouteKey(state.modelGate.target.label) === before.key)) {
      state.modelGate.target = { ...state.modelGate.target, ...after };
    }
    if (settings.modelPolicy === MODEL_POLICY_PIN
        && (settings.modelTargetKey === before.key || modelRouteKey(settings.modelTargetLabel) === before.key)) {
      settings.modelTargetLabel = after.label;
      settings.modelTargetKey = after.key;
      settings.modelTargetVersion = after.version;
    }
    const receipt = {
      schema: 'qomrade.pinned-route-alias-reconciliation.v1',
      at: nowIso(), origin, matchKind: resolution.matchKind,
      before, after,
      selectedAlready: true,
      clickedRoute: false,
      authority: 'canonicalize an already-selected route after bounded label drift; never select a different alias or relax pinned effort proof',
    };
    state.modelGate.pinnedRouteAliasReconciliations += 1;
    state.modelGate.lastPinnedRouteAliasReconciliation = receipt;
    boundedReceipt(state.modelGate.pinnedRouteAliasReceipts, receipt, 12);
    state.uiModelObservation = null;
    logEvent('pinned-model-route-reconciled', `Reconciled pinned ${before.label || before.key} to the already-selected ${after.label}.`, receipt);
    void saveTabRecord('pinned-model-route-reconciled', { suppressUnchangedSettings: false });
    return receipt;
  }
  function chooseExactModelRowFromOpenMenu(target, inspection, guard = null) {
    effectCheckpoint(guard, 'chooseExactModelRowFromOpenMenu:entry');
    const live = inspection && inspection._elements ? inspection : inspectOpenModelMenu({ includeMarkup: true });
    const targetKey = target && (target.key || modelRouteKey(target.label));
    const resolution = selectedPinnedRouteResolution(target, live);
    if (!resolution) return { ok: false, reason: `pinned model route was not discovered (${target && target.label || targetKey || 'unset'})`, inspection: stripModelInspection(live) };
    const row = resolution.row;
    if (row.disabled) return { ok: false, reason: `pinned model route is currently disabled (${row.text})`, inspection: stripModelInspection(live) };
    const reconciliation = resolution.alias ? reconcilePinnedRouteAlias(target, resolution, 'send-local-model-survey', guard) : null;
    const clicked = !row.checked && activateModelControl(row.element, guard);
    if (clicked) state.modelGate.selections += 1;
    return {
      ok: row.checked || clicked,
      clicked,
      matchKind: resolution.matchKind,
      reconciliation,
      row: { text: row.text, key: modelRouteKey(row.text), version: normalizeModelVersionHint(row.version, row.text), checked: row.checked },
      inspection: stripModelInspection(live),
      reusedOpenMenu: true,
    };
  }
  function modelCatalogFromInspection(inspection) {
    const rows = (inspection && inspection.routeRows || []).map(row => ({
      label: row.text,
      key: modelRouteKey(row.text),
      version: row.version || parseModelVersion(row.text),
      disabled: !!row.disabled,
      selected: !!row.checked,
    })).filter(row => row.label && row.key);
    return {
      schema: 'qomrade.model-catalog.v1',
      observedAt: nowIso(),
      rows,
      selectedKey: inspection && inspection.selectedRouteKey || null,
      selectedLabel: inspection && inspection.selectedRoute || null,
      effort: inspection ? {
        index: inspection.slider && inspection.slider.now,
        min: inspection.slider && inspection.slider.min,
        max: inspection.slider && inspection.slider.max,
        valueText: inspection.slider && inspection.slider.valueText || null,
        attribute: inspection.effortAttribute || null,
        proAvailable: !!(inspection.proRow && !inspection.proRow.disabled) || !!inspection.maximumMarker,
      } : null,
    };
  }
  async function discoverModelCatalog({ operatorInitiated = false } = {}) {
    if (state.modelGate.catalogBusy) return state.modelGate.catalog;
    if (operatorInitiated && state.running && !state.paused) {
      showMessage('Pause qomrade before refreshing model choices. This avoids racing an in-flight Send.', true);
      return null;
    }
    state.modelGate.catalogBusy = true;
    state.modelGate.catalogError = null;
    render();
    try {
      return await serializeModelMenu(async () => {
        const opened = await openModelMenu({ quiet: !operatorInitiated });
        if (!opened.ok) throw new Error(opened.reason || 'model menu could not be opened');
        await effectWait(MODEL_MENU_SETTLE_MS, null, 'discoverModelCatalog');
        const inspection = inspectOpenModelMenu({ includeMarkup: false });
        const catalog = modelCatalogFromInspection(inspection);
        state.modelGate.catalog = catalog;
        if (operatorInitiated && settings.modelPolicy === MODEL_POLICY_PIN && !settings.modelTargetKey && catalog.selectedKey) {
          const selectedRow = catalog.rows.find(row => row.key === catalog.selectedKey) || null;
          settings.modelTargetKey = catalog.selectedKey;
          settings.modelTargetLabel = catalog.selectedLabel || '';
          settings.modelTargetVersion = normalizeModelVersionHint(selectedRow && selectedRow.version, settings.modelTargetLabel);
          applyModelPolicySettingChange('operator-model-catalog-default');
          debounceSaveSettings();
        } else if (settings.modelPolicy === MODEL_POLICY_PIN && settings.modelTargetKey) {
          const rememberedTarget = modelPolicySnapshot(settings).target;
          const resolution = selectedPinnedRouteResolution(rememberedTarget, inspection);
          if (resolution && resolution.alias) reconcilePinnedRouteAlias(rememberedTarget, resolution, operatorInitiated ? 'operator-model-catalog-refresh' : 'model-catalog-refresh');
        }
        logEvent('model-catalog-observed', `Observed ${catalog.rows.length} model route${catalog.rows.length === 1 ? '' : 's'} from the live ChatGPT menu.`, catalog);
        return catalog;
      });
    } catch (error) {
      state.modelGate.catalogError = String(error && error.message || error);
      logEvent('model-catalog-failed', 'Could not refresh model choices from the live ChatGPT menu.', { error: state.modelGate.catalogError });
      if (operatorInitiated) showMessage(`Refresh model choices failed: ${state.modelGate.catalogError}`, true);
      return null;
    } finally {
      closeModelMenu();
      state.modelGate.catalogBusy = false;
      render({ forceModel: true });
    }
  }
  function acceptFlexibleModelConfirmation(survey, confirmation) {
    survey.ok = true;
    survey.selected = confirmation.selectedLabel;
    survey.confirmation = confirmation;
    survey.pillAfter = directModelObservation().label;
    const confirmed = {
      schema: 'qomrade.model-confirmation.v4',
      confirmedAt: nowIso(),
      confirmedT: Date.now(),
      policy: confirmation.policy,
      target: confirmation.target,
      candidate: confirmation.candidate,
      selectedLabel: confirmation.selectedLabel,
      routeKey: confirmation.routeKey,
      concreteLabel: confirmation.concreteLabel,
      version: confirmation.version,
      family: confirmation.family,
      hasPro: confirmation.hasPro,
      effort: confirmation.effort,
      pill: survey.pillAfter,
      evidence: confirmation.evidence,
    };
    state.modelGate.confirmed = confirmed;
    state.modelGate.nextSurveyAt = 0;
    rememberModelSurvey(survey);
    logEvent('model-confirmed', `Confirmed ${confirmed.selectedLabel || confirmed.concreteLabel || 'selected model'} at ${MODEL_EFFORT_LABELS[confirmed.effort?.policy] || confirmed.effort?.policy || 'current effort'}.`, { confirmation: confirmed, survey });
    return survey;
  }
  async function surveyConfiguredModel(reason, guard, snapshot) {
    effectCheckpoint(guard, 'surveyConfiguredModel:entry');
    return serializeModelMenu(async () => {
      effectCheckpoint(guard, 'configured-model-serial-admission');
      state.modelGate.active = true;
      state.modelGate.surveys += 1;
      const survey = {
        schema: 'qomrade.model-survey.v4',
        at: nowIso(), reason,
        policy: snapshot.policy,
        target: { ...snapshot.target, version: normalizeModelVersionHint(snapshot.target && snapshot.target.version, snapshot.target && snapshot.target.label) },
        pillBefore: (() => { const item = directModelObservation(); return { label: item.label, family: item.family, hasPro: item.hasPro, effortAttribute: item.effortAttribute, ok: item.ok }; })(),
        discovery: null, attempts: [], selected: null, ok: false,
      };
      try {
        const opened = await openModelMenu({ guard });
        if (!opened.ok) {
          survey.why = opened.reason;
          survey.surfaceFailure = !!opened.surfaceFailure;
          survey.menuSurface = state.modelGate.lastMenuSurface;
          rememberModelSurvey(survey);
          return survey;
        }
        await effectWait(MODEL_MENU_SETTLE_MS, guard, 'surveyConfiguredModel');
        let inspection = inspectOpenModelMenu({ includeMarkup: true });
        survey.discovery = stripModelInspection(inspection);
        state.modelGate.catalog = modelCatalogFromInspection(inspection);
        if (snapshot.policy === MODEL_POLICY_PIN) {
          if (!snapshot.target.key) {
            survey.why = 'Pin model & effort requires a discovered model choice';
            rememberModelSurvey(survey);
            return survey;
          }
          const requestedTarget = { ...snapshot.target, version: normalizeModelVersionHint(snapshot.target.version, snapshot.target.label) };
          const selection = chooseExactModelRowFromOpenMenu(snapshot.target, inspection, guard);
          survey.attempts.push({ kind: 'route', target: requestedTarget, effectiveTarget: { ...snapshot.target }, selection });
          if (selection.reconciliation) survey.effectiveTarget = { ...snapshot.target };
          if (!selection.ok) {
            survey.why = selection.reason;
            rememberModelSurvey(survey);
            return survey;
          }
          if (selection.clicked) {
            await effectWait(MODEL_SELECTION_SETTLE_MS, guard, 'surveyConfiguredModel');
            if (!modelMenuIsOpen()) {
              const reopened = await openModelMenu({ quiet: true, guard });
              if (!reopened.ok) { survey.why = reopened.reason; rememberModelSurvey(survey); return survey; }
              await effectWait(MODEL_MENU_SETTLE_MS, guard, 'surveyConfiguredModel');
            }
          }
          inspection = inspectOpenModelMenu({ includeMarkup: true });
          if (modelRouteKey(inspection.selectedRoute) !== snapshot.target.key) {
            survey.why = 'the pinned model route did not remain selected after the bounded selection step';
            rememberModelSurvey(survey);
            return survey;
          }
          const effort = await setSelectedEffortInOpenMenu(snapshot.target.effort, inspection, guard);
          survey.attempts.push({ kind: 'effort', target: snapshot.target.effort, effort: { ...effort, _inspection: undefined } });
          if (!effort.ok) {
            survey.why = effort.reason || `the pinned effort ${snapshot.target.effort} could not be selected`;
            rememberModelSurvey(survey);
            return survey;
          }
          inspection = effort._inspection || inspectOpenModelMenu({ includeMarkup: true });
        }
        const confirmation = flexibleModelConfirmation(inspection, snapshot);
        if (!confirmation.ok) {
          survey.why = confirmation.reason;
          survey.confirmation = confirmation;
          rememberModelSurvey(survey);
          return survey;
        }
        closeModelMenu(guard);
        await effectWait(180, guard, 'surveyConfiguredModel-close');
        const directAfter = directModelObservation();
        confirmation.pill = directAfter.label;
        if (confirmation.effort) confirmation.effort.attribute = directAfter.effortAttribute || confirmation.effort.attribute;
        confirmation.evidence = { ...confirmation.evidence, pillAfter: directAfter.label, effortAttributeAfter: directAfter.effortAttribute || null };
        return acceptFlexibleModelConfirmation(survey, confirmation);
      } finally {
        if (!guard || guard.valid()) closeModelMenu(guard);
        state.modelGate.active = false;
      }
    });
  }
  async function ensureConfiguredModel(reason = 'before every send', guard = null, requestedPreference = null) {
    const snapshot = activeModelPolicySnapshot();
    if (snapshot.policy === MODEL_POLICY_SMART_PRO) return ensureEligibleProModel(reason, guard, requestedPreference);
    if (snapshot.policy === MODEL_POLICY_PIN && !snapshot.target.key) {
      return { ok: false, reason: 'Pin model & effort is selected, but no model route has been chosen. Pause, refresh choices, and select a model.', policy: snapshot.policy };
    }
    if (state.modelGate.nextSurveyAt && Date.now() < state.modelGate.nextSurveyAt) {
      const previousReason = state.modelGate.lastSurvey && state.modelGate.lastSurvey.why;
      return { ok: false, reason: previousReason
        ? `${previousReason}; next bounded confirmation after ${new Date(state.modelGate.nextSurveyAt).toLocaleTimeString()}`
        : `waiting until ${new Date(state.modelGate.nextSurveyAt).toLocaleTimeString()} for the next bounded model confirmation`, retryAt: state.modelGate.nextSurveyAt, policy: snapshot.policy };
    }
    setPhase('SURVEYING_MODELS', snapshot.policy === MODEL_POLICY_PIN
      ? `Confirming pinned ${snapshot.target.label || snapshot.target.key} at ${MODEL_EFFORT_LABELS[snapshot.target.effort] || snapshot.target.effort}.`
      : 'Confirming the model and effort currently selected in ChatGPT without changing them.');
    const survey = await surveyConfiguredModel(reason, guard, snapshot);
    if (survey.ok && state.modelGate.confirmed) return { ok: true, reason: survey.confirmation.reason, confirmation: state.modelGate.confirmed, survey, direct: false, policy: snapshot.policy };
    state.modelGate.nextSurveyAt = Date.now() + (survey.surfaceFailure ? MODEL_SURFACE_RECHECK_MS : MODEL_RECHECK_MS);
    logEvent('model-hold', survey.why || 'configured model could not be confirmed', { survey, policy: snapshot.policy, target: snapshot.target, retryAt: state.modelGate.nextSurveyAt });
    return { ok: false, reason: survey.why || 'configured model could not be confirmed', survey, policy: snapshot.policy, target: snapshot.target, retryAt: state.modelGate.nextSurveyAt };
  }
  async function inspectAndMaximizeSelectedInOpenMenu(candidateLabel, initialInspection = null, guard = null) {
    effectCheckpoint(guard, 'inspectAndMaximizeSelectedInOpenMenu:entry');
    let inspection = initialInspection && initialInspection._elements ? initialInspection : inspectOpenModelMenu({ includeMarkup: true });
    if (!inspection.selectedModel || !sameModelFamily(inspection.selectedModel, candidateLabel)) {
      return { ok: false, reason: 'a different model row is selected', selectedModel: inspection.selectedModel, inspection: stripModelInspection(inspection), reusedOpenMenu: true };
    }
    const effort = await setEffortToMaximum(inspection, guard);
    await effectWait(MODEL_MENU_SETTLE_MS, guard, 'inspectAndMaximizeSelectedInOpenMenu');
    inspection = inspectOpenModelMenu({ includeMarkup: true });
    const proRecord = inspection._elements.proRow;
    let clickedProRow = false;
    if (proRecord && !proRecord.disabled && !proRecord.checked) {
      clickedProRow = activateModelControl(proRecord.element, guard);
      if (clickedProRow) await effectWait(MODEL_SELECTION_SETTLE_MS, guard, 'inspectAndMaximizeSelectedInOpenMenu');
      if (!modelMenuIsOpen()) {
        const reopened = await openModelMenu({ quiet: true, guard });
        if (reopened.ok) await effectWait(MODEL_MENU_SETTLE_MS, guard, 'inspectAndMaximizeSelectedInOpenMenu');
      }
      inspection = inspectOpenModelMenu({ includeMarkup: true });
    }
    const confirmation = modelConfirmationFromInspection(inspection, candidateLabel);
    return { ok: confirmation.ok, reason: confirmation.reason, effort, clickedProRow, confirmation, inspection: stripModelInspection(inspection), reusedOpenMenu: true };
  }
  async function inspectAndMaximizeSelected(candidateLabel, guard = null) {
    effectCheckpoint(guard, 'inspectAndMaximizeSelected:entry');
    const opened = await openModelMenu({ guard });
    if (!opened.ok) return { ok: false, reason: opened.reason };
    await effectWait(MODEL_MENU_SETTLE_MS, guard, 'inspectAndMaximizeSelected');
    const result = await inspectAndMaximizeSelectedInOpenMenu(candidateLabel, inspectOpenModelMenu({ includeMarkup: true }), guard);
    closeModelMenu(guard);
    await effectWait(180, guard, 'inspectAndMaximizeSelected');
    return result;
  }
  function rankModelRows(inspection, preference = '5.6-first') {
    return (inspection.modelRows || [])
      .filter(row => !row.disabled && modelCandidateLabelAllowed(row.text))
      .map((row, index) => ({ ...row, score: modelCandidateScore(row.text, row.index == null ? index : row.index, preference) }))
      .sort((a, b) => b.score - a.score)
      .slice(0, MAX_MODEL_CANDIDATES);
  }
  function rememberModelSurvey(survey) {
    const bytes = utf8Bytes(JSON.stringify(survey));
    state.modelGate.retainedSurveyBytes = bytes;
    state.modelGate.retainedSurveyMaxBytes = Math.max(state.modelGate.retainedSurveyMaxBytes || 0, bytes);
    state.modelGate.lastSurvey = survey;
    state.modelGate.recentSurveys.push(survey);
    if (state.modelGate.recentSurveys.length > MAX_MODEL_SURVEY_RECORDS) {
      state.modelGate.recentSurveys.splice(0, state.modelGate.recentSurveys.length - MAX_MODEL_SURVEY_RECORDS);
    }
    state.uiModelObservation = null;
  }
  function acceptModelSurveyConfirmation(survey, candidate, availability) {
    const confirmation = availability.confirmation;
    survey.ok = true;
    survey.selected = candidate.text;
    survey.confirmation = confirmation;
    survey.pillAfter = directModelObservation().label;
    const confirmed = {
      schema: 'qomrade.model-confirmation.v3',
      confirmedAt: nowIso(),
      confirmedT: Date.now(),
      candidate: candidate.text,
      selectedLabel: confirmation.selectedLabel,
      concreteLabel: confirmation.concreteLabel,
      version: confirmation.version,
      family: confirmation.family,
      hasPro: true,
      pill: survey.pillAfter,
      evidence: {
        viewToggleLabel: confirmation.viewToggleLabel,
        slider: confirmation.slider,
        proRow: confirmation.proRow,
        maximumMarker: confirmation.maximumMarker,
        discoveryMenuReused: !!availability.reusedOpenMenu,
      },
    };
    state.modelGate.confirmed = confirmed;
    state.modelGate.nextSurveyAt = 0;
    if (survey.preference === '5.6-first' && modelVersionIsExplicitSixOrNewer(confirmation.version)) {
      state.modelGate.runPreference = '6-fallback';
      state.modelGate.lastPreferenceSwitch = {
        at: nowIso(), from: '5.6-first', to: '6-fallback',
        reason: '5.6 unavailable or unconfirmed for this Send; GPT-6 fallback remains only until a stable reply succeeds',
        selected: confirmed.concreteLabel || confirmed.selectedLabel || confirmed.candidate,
      };
      logEvent('model-fallback-armed', 'GPT-5.6 could not be confirmed; GPT-6 is preferred only until a stable reply succeeds.', state.modelGate.lastPreferenceSwitch);
    }
    rememberModelSurvey(survey);
    logEvent('model-confirmed', `Confirmed ${confirmed.concreteLabel || confirmed.selectedLabel || confirmed.candidate} at Pro.`, { confirmation: confirmed, survey });
    return survey;
  }
  async function surveyAndSelectEligiblePro(reason = 'before every send', guard = null, preference = '5.6-first') {
    effectCheckpoint(guard, 'surveyAndSelectEligiblePro:entry');
    return serializeModelMenu(async () => {
      effectCheckpoint(guard, 'model-serial-admission');
      state.modelGate.active = true;
      state.modelGate.surveys += 1;
      const survey = {
        schema: 'qomrade.model-survey.v3',
        at: nowIso(),
        reason,
        preference,
        pillBefore: (() => { const item = directModelObservation(); return { label: item.label, family: item.family, hasPro: item.hasPro, ok: item.ok }; })(),
        discovery: null,
        candidates: [],
        attempts: [],
        selected: null,
        discoveryMenuReused: false,
        ok: false,
      };
      try {
        const opened = await openModelMenu({ guard });
        if (!opened.ok) {
          survey.why = opened.reason;
          survey.surfaceFailure = !!opened.surfaceFailure;
          survey.menuSurface = state.modelGate.lastMenuSurface;
          rememberModelSurvey(survey);
          return survey;
        }
        await effectWait(MODEL_MENU_SETTLE_MS, guard, 'surveyAndSelectEligiblePro');
        let inspection = inspectOpenModelMenu({ includeMarkup: true });
        survey.discovery = stripModelInspection(inspection);
        survey.candidates = rankModelRows(inspection, preference);
        if (!survey.candidates.length) {
          closeModelMenu(guard);
          survey.why = preference === '6-fallback'
            ? 'no selectable GPT-6-or-newer, Latest, GPT-5.6, or other eligible model row was discovered'
            : 'no selectable GPT-5.6, GPT-6-or-newer, other eligible, or Latest model row was discovered';
          rememberModelSurvey(survey);
          return survey;
        }
        // The discovery menu already contains the selected row, effort slider,
        // view toggle, and Pro evidence. Reuse it for the first ranked candidate
        // instead of closing and reopening the same menu two more times.
        const first = survey.candidates[0];
        state.modelGate.attempts += 1;
        const firstAttempt = { candidate: first, startedAt: nowIso(), discoveryMenuReused: true };
        firstAttempt.selection = chooseModelRowFromOpenMenu(first, inspection, guard);
        if (firstAttempt.selection.clicked) {
          await effectWait(MODEL_SELECTION_SETTLE_MS, guard, 'surveyAndSelectEligiblePro');
          if (!modelMenuIsOpen()) {
            const reopened = await openModelMenu({ quiet: true, guard });
            if (reopened.ok) await effectWait(MODEL_MENU_SETTLE_MS, guard, 'surveyAndSelectEligiblePro');
          }
          inspection = inspectOpenModelMenu({ includeMarkup: true });
        }
        if (firstAttempt.selection.ok && modelMenuIsOpen()) {
          firstAttempt.availability = await inspectAndMaximizeSelectedInOpenMenu(first.text, inspection, guard);
          firstAttempt.verdict = firstAttempt.availability.ok ? 'confirmed-pro' : 'pro-unavailable-or-unconfirmed';
        } else {
          firstAttempt.verdict = 'selection-failed';
        }
        survey.attempts.push(firstAttempt);
        survey.discoveryMenuReused = true;
        closeModelMenu(guard);
        await effectWait(180, guard, 'surveyAndSelectEligiblePro');
        if (firstAttempt.availability && firstAttempt.availability.ok) {
          return acceptModelSurveyConfirmation(survey, first, firstAttempt.availability);
        }
        for (const candidate of survey.candidates.slice(1)) {
          state.modelGate.attempts += 1;
          const attempt = { candidate, startedAt: nowIso(), discoveryMenuReused: false };
          attempt.selection = await chooseModelRow(candidate, guard);
          if (!attempt.selection.ok) {
            attempt.verdict = 'selection-failed';
            survey.attempts.push(attempt);
            continue;
          }
          attempt.availability = await inspectAndMaximizeSelected(candidate.text, guard);
          attempt.verdict = attempt.availability.ok ? 'confirmed-pro' : 'pro-unavailable-or-unconfirmed';
          survey.attempts.push(attempt);
          if (!attempt.availability.ok) continue;
          return acceptModelSurveyConfirmation(survey, candidate, attempt.availability);
        }
        survey.why = 'no discovered model route could be confirmed at Pro';
        survey.pillAfter = directModelObservation().label;
        rememberModelSurvey(survey);
        return survey;
      } finally {
        if (!guard || guard.valid()) closeModelMenu(guard);
        state.modelGate.active = false;
      }
    });
  }
  function acceptDirectEligiblePro(direct, evidenceSource, extraEvidence = {}) {
    const confirmed = {
      schema: 'qomrade.model-confirmation.v3',
      confirmedAt: nowIso(),
      confirmedT: Date.now(),
      candidate: direct.label,
      selectedLabel: direct.label,
      concreteLabel: direct.label,
      version: direct.version,
      family: direct.family,
      hasPro: true,
      pill: direct.label,
      evidence: { source: evidenceSource, ...extraEvidence },
    };
    state.modelGate.confirmed = confirmed;
    state.modelGate.nextSurveyAt = 0;
    return { ok: true, reason: direct.reason, confirmation: confirmed, direct: true };
  }
  async function ensureEligibleProModel(reason = 'before every send', guard = null, requestedPreference = null) {
    effectCheckpoint(guard, 'ensureEligibleProModel:entry');
    const preference = requestedPreference === '6-fallback' || state.modelGate.runPreference === '6-fallback'
      ? '6-fallback' : '5.6-first';
    const preferSix = preference === '6-fallback';
    const direct = directModelObservation();
    if (direct.ok && ((!preferSix && modelVersionIsPreferred56(direct.version))
        || (preferSix && modelVersionIsExplicitSixOrNewer(direct.version)))) {
      return acceptDirectEligiblePro(direct, preferSix
        ? 'visible-explicit-6-pill-run-fallback'
        : 'visible-preferred-5.6-pill-no-menu-needed', { preference });
    }
    if (direct.ok && !settings.autoSelectEligiblePro) {
      return acceptDirectEligiblePro(direct, 'visible-eligible-pill-auto-selection-disabled', { preference: 'operator-visible-choice' });
    }
    if (!settings.autoSelectEligiblePro) return { ok: false, reason: direct.reason, direct };
    if (state.modelGate.nextSurveyAt && Date.now() < state.modelGate.nextSurveyAt) {
      return { ok: false, reason: `waiting until ${new Date(state.modelGate.nextSurveyAt).toLocaleTimeString()} for the next bounded model survey`, retryAt: state.modelGate.nextSurveyAt, direct };
    }
    setPhase('SURVEYING_MODELS', preferSix
      ? 'The current failed lineage is using GPT-6 Pro fallback; success returns Smart Pro to GPT-5.6 first.'
      : 'Surveying for preferred GPT-5.6 Pro, then GPT-6 Pro fallback.');
    const survey = await surveyAndSelectEligiblePro(reason, guard, preference);
    if (survey.ok && state.modelGate.confirmed) return { ok: true, reason: `live model menu confirmed ${preference} eligible Pro`, confirmation: state.modelGate.confirmed, survey, direct: false, preference };
    // Retain a concrete already-visible eligible route only after the preferred
    // bounded survey fails and the same live family survives menu cleanup.
    const directIsFallback = direct.ok && (preferSix
      ? modelVersionIsPreferred56(direct.version)
      : modelVersionIsExplicitSixOrNewer(direct.version));
    if (directIsFallback) {
      const fallback = directModelObservation();
      const sameFallbackClass = fallback.ok && (preferSix
        ? modelVersionIsPreferred56(fallback.version)
        : modelVersionIsExplicitSixOrNewer(fallback.version));
      if (sameFallbackClass && compareModelVersions(fallback.version, direct.version) === 0
          && !modelMenuAdvertisedOpen()) {
        if (!preferSix && modelVersionIsExplicitSixOrNewer(fallback.version)) {
          state.modelGate.runPreference = '6-fallback';
          state.modelGate.lastPreferenceSwitch = {
            at: nowIso(), from: '5.6-first', to: '6-fallback',
            reason: '5.6-first survey failed while the same concrete GPT-6 Pro route remained live; fallback clears after a stable reply',
            selected: fallback.label,
          };
          logEvent('model-fallback-armed', 'GPT-5.6 could not be confirmed; retaining GPT-6 until a stable reply succeeds.', state.modelGate.lastPreferenceSwitch);
        }
        const accepted = acceptDirectEligiblePro(fallback, preferSix
          ? 'visible-5.6-last-resort-after-6-survey'
          : 'visible-explicit-6-fallback-after-5.6-survey', {
          preference,
          surveyWhy: survey.why || null,
          surfaceFailure: !!survey.surfaceFailure,
        });
        accepted.survey = survey;
        accepted.directFallback = true;
        accepted.preference = preference;
        return accepted;
      }
    }
    state.modelGate.nextSurveyAt = Date.now() + (survey.surfaceFailure ? MODEL_SURFACE_RECHECK_MS : MODEL_RECHECK_MS);
    logEvent('model-hold', survey.why || 'eligible Pro could not be confirmed', { survey, preference, retryAt: state.modelGate.nextSurveyAt });
    if (survey.surfaceFailure) {
      captureDomishEvent('model-surface-failure', {
        reason: survey.why || 'eligible Pro surface unavailable',
        severity: 'warn',
        origin: 'model-gate',
        primaryNodes: [findModelButton()].filter(Boolean),
        key: fnv1a64(JSON.stringify(['model-surface-failure', survey.why || null, survey.menuSurface?.stage || null, !!findComposer(), materializedTurns().length])),
        context: { preference, retryAt: state.modelGate.nextSurveyAt, menuSurface: survey.menuSurface || null, direct: { label: direct.label, reason: direct.reason } },
      });
    }
    return { ok: false, reason: survey.why || 'eligible Pro could not be confirmed', survey, preference, retryAt: state.modelGate.nextSurveyAt, direct };
  }
  // A collapsed "Pro" pill omits the family; it does not contradict a concrete
  // confirmation from the menu this very send just inspected. Keep that proof
  // local to the effect operation, not in currentModelObservation(). Last-page
  // continuity and old modelGate.confirmed objects never grant this exception.
  function captureSendModelWitness(gate, guard) {
    effectCheckpoint(guard, 'capture-send-model-witness');
    const direct = directModelObservation();
    const confirmation = gate && gate.confirmation;
    const button = direct.element;
    const witness = {
      operationId: guard.operation.id,
      epoch: guard.operation.epoch,
      pathname: location.pathname,
      conversationId: conversationIdFromPath(),
      confirmation,
      confirmationCopy: confirmation ? JSON.parse(JSON.stringify(confirmation)) : null,
      gateOk: !!(gate && gate.ok),
      gateDirect: !!(gate && gate.direct),
      button,
      capturedAt: nowIso(),
      capturedT: Date.now(),
      pill: direct.label,
      reasoningAttribute: button && button.getAttribute('data-selected-reasoning-effort'),
      interrupted: null,
      released: false,
    };
    // Three temporary listeners on one control, removed on every exit. They do
    // not prevent events, inspect other tabs, watch the DOM, or run a poll.
    const types = ['pointerdown', 'click', 'keydown'];
    const interrupt = event => {
      if (!witness.interrupted) witness.interrupted = { at: nowIso(), type: event.type };
    };
    if (button) for (const type of types) button.addEventListener(type, interrupt, { capture: true, passive: true });
    witness.release = () => {
      if (button) for (const type of types) button.removeEventListener(type, interrupt, true);
      witness.released = true;
    };
    return witness;
  }
  function observeSendModelCommit(witness, guard) {
    const live = directModelObservation();
    const confirmed = witness && witness.confirmationCopy;
    const policy = normalizeModelPolicy(confirmed && confirmed.policy || MODEL_POLICY_SMART_PRO);
    const ageMs = confirmed && Number.isFinite(confirmed.confirmedT) ? Date.now() - confirmed.confirmedT : null;
    const sameVersion = !!(confirmed && confirmed.version && live.version
      && compareModelVersions(live.version, confirmed.version) === 0);
    const sameEffortAttribute = !!(witness && live.element
      && live.element.getAttribute('data-selected-reasoning-effort') === witness.reasoningAttribute);
    const samePill = normalizeCompactText(live.label).toLowerCase() === normalizeCompactText(witness && witness.pill).toLowerCase();
    const smartConcreteProof = !!(witness && witness.gateOk && confirmed && confirmed.hasPro
      && modelVersionIsAllowed(confirmed.version));
    const flexibleConcreteProof = !!(witness && witness.gateOk && confirmed && confirmed.routeKey
      && [MODEL_POLICY_PIN, MODEL_POLICY_FOLLOW].includes(policy));
    let reason = policy === MODEL_POLICY_SMART_PRO ? 'same-operation-concrete-Pro' : 'same-operation-configured-model';
    let ok = false;
    let evidenceSource = null;
    if (!witness || witness.released || witness.operationId !== guard.operation.id || witness.epoch !== guard.operation.epoch || !guard.valid()) reason = 'model-witness-operation-revoked';
    else if (!(policy === MODEL_POLICY_SMART_PRO ? smartConcreteProof : flexibleConcreteProof) || witness.confirmation !== state.modelGate.confirmed) reason = 'model-witness-missing-or-superseded';
    else if (witness.pathname !== location.pathname || witness.conversationId !== conversationIdFromPath()) reason = 'model-witness-conversation-changed';
    else if (ageMs == null || ageMs < 0 || ageMs > MODEL_COMMIT_MAX_AGE_MS) reason = 'model-witness-expired';
    else if (!live.element || !witness.button || !witness.button.isConnected || live.element !== witness.button || !isEnabled(live.element)) reason = 'model-control-replaced-or-unavailable';
    else if (witness.interrupted) reason = 'model-control-used-after-confirmation';
    else if (live.element.getAttribute('aria-expanded') === 'true' || live.element.getAttribute('data-state') === 'open') reason = 'model-menu-open-after-confirmation';
    else if (live.version && confirmed.version && !sameVersion) reason = 'model-family-changed-after-confirmation';
    else if (!sameEffortAttribute) reason = 'model-surface-no-longer-matches-confirmation';
    else if (policy === MODEL_POLICY_SMART_PRO) {
      if (!live.hasPro) reason = 'model-no-longer-visibly-Pro';
      else if (live.ok && sameVersion) {
        ok = true;
        evidenceSource = 'live-concrete-pill-plus-send-local-confirmation';
      } else if (normalizeCompactText(live.label).toLowerCase() === 'pro'
          && (normalizeCompactText(witness.pill).toLowerCase() === 'pro'
            || (modelLabelIndicatesPro(witness.pill) && compareModelVersions(parseModelVersion(witness.pill), confirmed.version) === 0))) {
        ok = true;
        reason = 'same-operation-confirmation-with-collapsed-Pro';
        evidenceSource = witness.gateDirect ? 'send-local-concrete-pill-then-collapsed-Pro' : 'send-local-menu-confirmation-plus-collapsed-Pro';
      } else reason = 'model-surface-no-longer-matches-confirmation';
    } else if (samePill || sameVersion || modelLabelIsTransient(live.label)) {
      ok = true;
      reason = policy === MODEL_POLICY_PIN ? 'same-operation-pinned-model-confirmation' : 'same-operation-follow-current-confirmation';
      evidenceSource = samePill ? 'unchanged-trigger-plus-send-local-menu-confirmation'
        : sameVersion ? 'same-family-trigger-plus-send-local-menu-confirmation'
          : 'effort-only-trigger-plus-send-local-menu-confirmation';
    } else reason = 'model-surface-no-longer-matches-confirmation';
    const receipt = {
      schema: 'qomrade.model-send-commit.v2',
      at: nowIso(), ok, reason, evidenceSource, policy,
      operationId: guard.operation.id, epoch: guard.operation.epoch,
      confirmationAgeMs: ageMs, maxAgeMs: MODEL_COMMIT_MAX_AGE_MS,
      confirmed: confirmed ? {
        policy: confirmed.policy || MODEL_POLICY_SMART_PRO,
        target: confirmed.target || null,
        candidate: confirmed.candidate,
        selectedLabel: confirmed.selectedLabel || null,
        routeKey: confirmed.routeKey || null,
        concreteLabel: confirmed.concreteLabel,
        version: confirmed.version,
        hasPro: confirmed.hasPro,
        effort: confirmed.effort || null,
        confirmedAt: confirmed.confirmedAt,
        evidence: confirmed.evidence,
      } : null,
      live: { label: live.label, version: live.version, hasPro: live.hasPro, effortAttribute: live.effortAttribute, directOk: live.ok, reason: live.reason },
      capturedPill: witness && witness.pill,
      capturedEffortAttribute: witness && witness.reasoningAttribute,
      controlSame: !!(witness && witness.button && live.element === witness.button),
      controlInteraction: witness && witness.interrupted,
      authority: 'this-send-only; never-restored; UI-evidence-not-backend-model-attestation',
    };
    state.modelGate.lastCommit = receipt;
    return receipt;
  }
  function editorNodeText(node) {
    if (!node) return '';
    if (node.nodeType === Node.TEXT_NODE) return node.nodeValue || '';
    if (node.nodeType !== Node.ELEMENT_NODE) return '';
    if (node.tagName === 'BR') return '\n';
    let output = '';
    for (const child of node.childNodes) output += editorNodeText(child);
    return output;
  }
  function editorBlockText(node) {
    const text = normalizePromptLineEndings(editorNodeText(node));
    // ProseMirror represents an empty editor as <p><br></p>. innerText reports
    // that placeholder as a newline even though there is no operator text.
    if (!node.textContent && /^\n*$/.test(text)) return '';
    return text;
  }
  function readComposerText(composer) {
    if (!composer) return '';
    if (composer instanceof HTMLTextAreaElement || composer instanceof HTMLInputElement) {
      return normalizePromptLineEndings(composer.value || '');
    }
    const blocks = Array.from(composer.children || []).filter(node => node && (node.tagName === 'P' || node.tagName === 'DIV'));
    if (blocks.length) return normalizePromptLineEndings(blocks.map(editorBlockText).join('\n'));
    return normalizePromptLineEndings(editorNodeText(composer));
  }
  function editorPromptPayload(prompt) {
    const raw = normalizePromptLineEndings(prompt);
    const payload = raw.replace(/\n+$/g, '');
    return {
      raw,
      payload,
      rawChars: raw.length,
      rawHash: fnv1a64(raw),
      payloadChars: payload.length,
      payloadHash: fnv1a64(payload),
      terminalNewlinesRemoved: raw.length - payload.length,
    };
  }
  function renderedPromptProjection(value) {
    return normalizeCompactText(normalizeForEditorCompare(value).replace(/`([^`\n]+)`/g, '$1'));
  }
  function compareRenderedPrompt(turnTextValue, promptValue) {
    const turnText = normalizeLineEndings(turnTextValue);
    const prompt = normalizeLineEndings(promptValue);
    const exactMatch = normalizeForEditorCompare(turnText) === normalizeForEditorCompare(prompt);
    const compactMatch = !exactMatch && normalizeCompactText(turnText) === normalizeCompactText(prompt);
    const inlineCodeRenderedMatch = !exactMatch && !compactMatch && normalizeCompactText(turnText) === renderedPromptProjection(prompt);
    return {
      ok: exactMatch || compactMatch || inlineCodeRenderedMatch,
      kind: exactMatch ? 'exact-rendered-text' : compactMatch ? 'compact-rendered-text-after-exact-composer-custody' : inlineCodeRenderedMatch ? 'inline-code-rendered-text-after-exact-composer-custody' : null,
      turnHash: fnv1a64(turnText),
      promptHash: fnv1a64(prompt),
      turnCompactHash: fnv1a64(normalizeCompactText(turnText)),
      promptCompactHash: fnv1a64(normalizeCompactText(prompt)),
      promptProjectionHash: fnv1a64(renderedPromptProjection(prompt)),
    };
  }
  function composerIsEmpty(composer) {
    return normalizeForEditorCompare(readComposerText(composer)).trim() === '';
  }
  function setNativeValue(control, value, guard = null) {
    effectCheckpoint(guard, 'native-value-before-write');
    const prototype = control instanceof HTMLTextAreaElement ? HTMLTextAreaElement.prototype : HTMLInputElement.prototype;
    const descriptor = Object.getOwnPropertyDescriptor(prototype, 'value');
    if (descriptor && descriptor.set) descriptor.set.call(control, value);
    else control.value = value;
    effectCheckpoint(guard, 'native-value-before-input');
    control.dispatchEvent(new Event('input', { bubbles: true, composed: true }));
    effectCheckpoint(guard, 'native-value-before-change');
    control.dispatchEvent(new Event('change', { bubbles: true, composed: true }));
  }
  function selectAllEditableContent(element) {
    const selection = getSelection();
    if (!selection) return;
    const range = document.createRange();
    range.selectNodeContents(element);
    selection.removeAllRanges();
    selection.addRange(range);
  }
  function dispatchComposerInput(element, text, inputType = 'insertText') {
    try {
      element.dispatchEvent(new InputEvent('input', {
        bubbles: true,
        composed: true,
        inputType,
        data: text,
      }));
    } catch (_) {
      element.dispatchEvent(new Event('input', { bubbles: true, composed: true }));
    }
  }
  function replaceContentEditableFallback(element, text, guard = null) {
    effectCheckpoint(guard, 'direct-editor-before-replacement');
    const fragment = document.createDocumentFragment();
    const lines = normalizeLineEndings(text).split('\n');
    for (const line of lines) {
      const paragraph = document.createElement('p');
      if (line) paragraph.append(document.createTextNode(line));
      else paragraph.append(document.createElement('br'));
      fragment.append(paragraph);
    }
    element.replaceChildren(fragment);
    dispatchComposerInput(element, text, 'insertText');
  }
  function clearOwnedComposerAttempt(element, expectedPayload, guard = null) {
    effectCheckpoint(guard, 'owned-composer-clear-admission');
    const observed = readComposerText(element);
    const normalizedObserved = normalizeForEditorCompare(observed);
    const normalizedExpected = normalizeForEditorCompare(expectedPayload);
    const represented = editorPayloadEquivalent(observed, expectedPayload);
    const owned = !normalizedObserved || represented.ok || normalizeCompactText(normalizedObserved) === normalizeCompactText(normalizedExpected);
    if (!owned) return { ok: false, reason: 'composer changed to text qomrade cannot prove it owns', observed };
    try {
      element.focus({ preventScroll: true });
      effectCheckpoint(guard, 'owned-composer-clear-after-focus');
      if (readComposerText(element) !== observed) return { ok: false, reason: 'composer changed during focus; clear refused', observed: readComposerText(element) };
      if (element instanceof HTMLTextAreaElement || element instanceof HTMLInputElement) setNativeValue(element, '', guard);
      else {
        selectAllEditableContent(element);
        try { document.execCommand('delete', false); } catch (_) {}
        effectCheckpoint(guard, 'owned-composer-clear-after-delete');
        if (!composerIsEmpty(element)) {
          const paragraph = document.createElement('p');
          paragraph.append(document.createElement('br'));
          element.replaceChildren(paragraph);
          dispatchComposerInput(element, null, 'deleteContentBackward');
        }
      }
      return { ok: composerIsEmpty(element), observed: readComposerText(element) };
    } catch (error) {
      if (error && error.qomradeEffectCancelled) throw error;
      return { ok: false, reason: String(error && error.message || error), observed: readComposerText(element) };
    }
  }
  function insertionAttemptRecord(name, custody, observed, ok, error, advance, extra = {}) {
    return {
      name,
      ok: !!ok,
      error: error ? String(error && error.message || error) : null,
      observedChars: observed.length,
      observedHash: fnv1a64(observed),
      normalizedObservedChars: normalizeForEditorCompare(observed).length,
      normalizedObservedHash: fnv1a64(normalizeForEditorCompare(observed)),
      expectedPayloadChars: custody.payloadChars,
      expectedPayloadHash: custody.payloadHash,
      advance: advance ? {
        advanced: !!advance.advanced,
        safeMatch: !!advance.safeMatch,
        generating: !!advance.generating,
        assistantAdvanced: !!advance.assistantAdvanced,
        assistantOnlyAdvance: !!advance.assistantOnlyAdvance,
        rebaselined: !!advance.rebaselined,
        newTurnCount: advance.newTurnCount || 0,
        matchedUserTurnId: advance.matchedUserTurn && advance.matchedUserTurn.id || null,
        matchKind: advance.match && advance.match.kind || null,
      } : null,
      ...extra,
    };
  }
  // @QOMRADE-CHUNK id=30.composer title="Exact composer insertion, terminal-newline custody, and pre-click advance sensing"
  async function insertExactPrompt(composer, prompt, { observeAdvance = null, guard = null } = {}) {
    effectCheckpoint(guard, 'composer-admission');
    if (!composer) return { ok: false, reason: 'composer not found', attempts: [] };
    const custody = editorPromptPayload(prompt);
    if (custody.raw.length > MAX_PROMPT_CHARS) {
      return { ok: false, reason: `prompt is ${custody.raw.length} characters; the hard limit is ${MAX_PROMPT_CHARS}`, attempts: [], custody };
    }
    if (!custody.payload) return { ok: false, reason: 'prompt contains only editor-irrelevant terminal newlines', attempts: [], custody };
    if (!composerIsEmpty(composer)) {
      return { ok: false, reason: 'composer is not empty; qomrade will not overwrite operator text', attempts: [], custody, observed: readComposerText(composer) };
    }
    const attempts = [];
    const inspectAdvance = async name => {
      if (typeof observeAdvance !== 'function') return null;
      try { return await observeAdvance(name); }
      catch (error) {
        if (error.qomradeEffectCancelled) throw error;
        recordPageError({ kind: 'composer-advance-observer-error', method: name, message: String(error && error.message || error), stack: trunc(error && error.stack || '', 2_000) });
        return null;
      }
    };
    const finishAttempt = async (name, ok, error = null, extra = {}) => {
      await effectWait(INSERT_SETTLE_MS, guard, 'composer-settle');
      const observed = readComposerText(composer);
      const advance = await inspectAdvance(name);
      effectCheckpoint(guard, 'composer-after-advance');
      const representation = editorPayloadEquivalent(observed, custody.payload);
      const exact = representation.ok;
      const record = insertionAttemptRecord(name, custody, observed, ok && exact, error, advance, { ...extra, methodReportedSuccess: !!ok, exact, exactCodePoints: representation.exactCodePoints, browserSpaceRepresentation: representation.browserSpaceRepresentation });
      attempts.push(record);
      state.composerAttemptCount += 1;
      if (advance && advance.advanced) return { kind: 'advance', observed, advance, record };
      if (ok && exact) return { kind: 'success', observed, record };
      return { kind: 'failure', observed, advance, record };
    };
    effectCheckpoint(guard, 'composer-focus-and-insertion');
    composer.focus({ preventScroll: true });
    effectCheckpoint(guard, 'composer-after-focus');
    if (!composerIsEmpty(composer)) return { ok: false, reason: 'composer changed during focus; insertion refused', attempts, custody, observed: readComposerText(composer) };
    if (composer instanceof HTMLTextAreaElement || composer instanceof HTMLInputElement) {
      let error = null;
      try { setNativeValue(composer, custody.payload, guard); } catch (caught) { if (caught && caught.qomradeEffectCancelled) throw caught; error = caught; }
      const result = await finishAttempt('native-value', !error, error);
      if (result.kind === 'advance') return { ok: false, advanced: true, method: 'native-value', observed: result.observed, advance: result.advance, attempts, custody };
      if (result.kind === 'success') {
        logEvent('prompt-inserted', 'Exact normalized prompt inserted via native-value.', { custody, attempts });
        return { ok: true, method: 'native-value', observed: result.observed, attempts, custody };
      }
      return { ok: false, reason: 'textarea value did not match the exact normalized prompt', observed: result.observed, attempts, custody };
    }
    let execWorked = false;
    let execError = null;
    try {
      selectAllEditableContent(composer);
      effectCheckpoint(guard, 'composer-before-insertText');
      execWorked = document.execCommand && document.execCommand('insertText', false, custody.payload) !== false;
    } catch (caught) { if (caught && caught.qomradeEffectCancelled) throw caught; execError = caught; }
    let result = await finishAttempt('execCommand-insertText', execWorked, execError);
    if (result.kind === 'advance') return { ok: false, advanced: true, method: 'execCommand-insertText', observed: result.observed, advance: result.advance, attempts, custody };
    if (result.kind === 'success') {
      logEvent('prompt-inserted', 'Exact normalized prompt inserted via execCommand-insertText.', { custody, attempts });
      return { ok: true, method: 'execCommand-insertText', observed: result.observed, attempts, custody };
    }
    let cleared = clearOwnedComposerAttempt(composer, custody.payload, guard);
    if (!cleared.ok) return { ok: false, reason: cleared.reason || 'failed insertion left unowned composer text; fallback refused', observed: cleared.observed, attempts, custody };
    let directError = null;
    try { replaceContentEditableFallback(composer, custody.payload, guard); } catch (caught) { if (caught && caught.qomradeEffectCancelled) throw caught; directError = caught; }
    result = await finishAttempt('direct-editor', !directError, directError);
    if (result.kind === 'advance') return { ok: false, advanced: true, method: 'direct-editor', observed: result.observed, advance: result.advance, attempts, custody };
    if (result.kind === 'success') {
      logEvent('prompt-inserted', 'Exact normalized prompt inserted via direct-editor.', { custody, attempts });
      return { ok: true, method: 'direct-editor', observed: result.observed, attempts, custody };
    }
    cleared = clearOwnedComposerAttempt(composer, custody.payload, guard);
    if (!cleared.ok) return { ok: false, reason: cleared.reason || 'direct-editor left unowned composer text; paste fallback refused', observed: cleared.observed, attempts, custody };
    let pasteWorked = false;
    let pasteError = null;
    try {
      effectCheckpoint(guard, 'composer-focus-and-insertion');
      composer.focus({ preventScroll: true });
      effectCheckpoint(guard, 'composer-before-paste');
      if (typeof DataTransfer === 'function' && typeof ClipboardEvent === 'function') {
        const transfer = new DataTransfer();
        transfer.setData('text/plain', custody.payload);
        pasteWorked = composer.dispatchEvent(new ClipboardEvent('paste', { clipboardData: transfer, bubbles: true, composed: true, cancelable: true }));
      }
    } catch (caught) { if (caught && caught.qomradeEffectCancelled) throw caught; pasteError = caught; }
    result = await finishAttempt('paste-event', pasteWorked, pasteError);
    if (result.kind === 'advance') return { ok: false, advanced: true, method: 'paste-event', observed: result.observed, advance: result.advance, attempts, custody };
    if (result.kind === 'success') {
      logEvent('prompt-inserted', 'Exact normalized prompt inserted via paste-event.', { custody, attempts });
      return { ok: true, method: 'paste-event', observed: result.observed, attempts, custody };
    }
    const observed = readComposerText(composer);
    logEvent('prompt-insertion-failed', 'No bounded insertion method produced exact normalized prompt equality.', { custody, attempts, observedChars: observed.length, observedHash: fnv1a64(observed), composer: elementSummary(composer, { redactContent: true }) });
    return { ok: false, reason: 'composer text did not match the exact normalized prompt after bounded insertion attempts', observed: trunc(observed, 500), attempts, custody };
  }
  async function waitForSendButton(timeoutMs = SEND_BUTTON_WAIT_MS, guard = null) {
    effectCheckpoint(guard, 'send-control-wait');
    const deadline = Date.now() + timeoutMs;
    while (Date.now() < deadline) {
      const button = findSendButton();
      if (button) return button;
      await effectWait(100, guard, 'send-control-wait');
    }
    return null;
  }
  // @QOMRADE-CHUNK id=40.turns title="Classic and virtualized conversation adapters"
  const turnMeta = new WeakMap();
  let materializedTurnCache = null;
  let observationTextCache = null;
  // This cache exists only during one synchronous observation. It never spans
  // a timer, await, input insertion or Send, and holds no historical DOM roots.
  function withReadSnapshot(label, operation) {
    const outer = observationTextCache;
    if (!outer) observationTextCache = new WeakMap();
    const started = performance.now();
    const queries = state.metrics.selectorQueries;
    const reads = state.metrics.turnTextReads;
    const hits = state.metrics.turnTextCacheHits;
    try { return operation(); }
    finally {
      const durationMs = Math.max(0, performance.now() - started);
      const prior = state.metrics.synchronousSections[label] || { samples: 0, totalMs: 0, lastMs: 0, maxMs: 0, lastQueries: 0, lastTextReads: 0, lastCacheHits: 0 };
      prior.samples += 1;
      prior.totalMs = Math.round((prior.totalMs + durationMs) * 100) / 100;
      prior.lastMs = Math.round(durationMs * 100) / 100;
      prior.lastCompletedAt = nowIso();
      prior.maxMs = Math.max(prior.maxMs, prior.lastMs);
      prior.lastQueries = state.metrics.selectorQueries - queries;
      prior.lastTextReads = state.metrics.turnTextReads - reads;
      prior.lastCacheHits = state.metrics.turnTextCacheHits - hits;
      state.metrics.synchronousSections[label] = prior;
      observationTextCache = outer;
    }
  }
  function semanticAssistantText(element) {
    // Keep clone/remove/textContent semantics, but descend in JavaScript only
    // along paths to excluded controls. Other subtrees use native textContent;
    // this avoids both cloned nodes and a JS visit to every message text node.
    const excluded = new Set(qa('h4[data-conversation-role="assistant"],button[aria-label="Copy response"],button[aria-label="Good response"],button[aria-label="Bad response"],button[aria-label="More actions"]', element));
    const paths = new Set();
    for (const hidden of excluded) {
      for (let parent = hidden.parentNode; parent && parent !== element && !paths.has(parent); parent = parent.parentNode) paths.add(parent);
    }
    const parts = [];
    let node = element.firstChild;
    while (node) {
      state.metrics.semanticTextNodesVisited += 1;
      if (!excluded.has(node)) {
        if (paths.has(node) && node.firstChild) { node = node.firstChild; continue; }
        if (node.nodeType === 1 || node.nodeType === 3 || node.nodeType === 4) {
          parts.push(node.textContent || '');
          state.metrics.semanticSubtreeReads += 1;
        }
      }
      while (node && node !== element && !node.nextSibling) node = node.parentNode;
      if (!node || node === element) break;
      node = node.nextSibling;
    }
    return parts.join('');
  }
  function invalidateTurnCache(reason = 'unspecified') {
    materializedTurnCache = null;
    if (observationTextCache) observationTextCache = new WeakMap();
    return reason;
  }
  function searchTurnGroup(element) {
    return element && element.closest ? element.closest('[data-content-search-turn-key],[data-turn-key]') : null;
  }
  function fallbackTurnIndex(element) {
    if (!element) return null;
    const group = searchTurnGroup(element);
    const candidates = [
      element.getAttribute && element.getAttribute('data-chatgpt-search-unit-key'),
      element.getAttribute && element.getAttribute('data-content-search-unit-key'),
      element.getAttribute && element.getAttribute('data-content-search-turn-key'),
      group && (group.getAttribute('data-content-search-turn-key') || group.getAttribute('data-turn-key')),
    ];
    for (const value of candidates) {
      const match = /fallback-turn-(\d+)/.exec(String(value || ''));
      if (match) return Number.parseInt(match[1], 10);
    }
    return null;
  }
  function setTurnMeta(element, meta) {
    if (!element) return element;
    turnMeta.set(element, { ...(turnMeta.get(element) || {}), ...(meta || {}) });
    return element;
  }
  function turnRole(element) {
    if (!element) return 'unknown';
    const meta = turnMeta.get(element);
    if (meta && meta.role) return meta.role;
    const unitKey = element.getAttribute && (element.getAttribute('data-chatgpt-search-unit-key') || element.getAttribute('data-content-search-unit-key')) || '';
    if (/:user$/.test(unitKey)) return 'user';
    if (/:assistant$/.test(unitKey)) return 'assistant';
    const direct = (element.getAttribute('data-turn') || element.getAttribute('data-message-author-role') || '').toLowerCase();
    if (direct === 'assistant' || direct === 'user') return direct;
    const child = q('[data-message-author-role]', element);
    const childRole = child && (child.getAttribute('data-message-author-role') || '').toLowerCase();
    if (childRole === 'assistant' || childRole === 'user') return childRole;
    if ((element.matches && element.matches('[data-user-message-bubble]')) || q('[data-user-message-bubble]', element)) return 'user';
    if ((element.matches && element.matches('[data-chatgpt-agent-turn-start]')) || q('[data-chatgpt-agent-turn-start]', element) || q('[data-conversation-role="assistant"]', element)) return 'assistant';
    const heading = cleanVisibleText(element.querySelector('h4, [class*="sr-only"]')?.textContent || '');
    if (/chatgpt said|assistant/i.test(heading)) return 'assistant';
    if (/you said|user/i.test(heading)) return 'user';
    return 'unknown';
  }
  function turnOrdinal(element) {
    if (!element) return null;
    const meta = turnMeta.get(element);
    if (meta && meta.ordinal != null) return meta.ordinal;
    const match = /conversation-turn-(\d+)/.exec(element.getAttribute && element.getAttribute('data-testid') || '');
    if (match) return Number.parseInt(match[1], 10);
    const index = fallbackTurnIndex(element);
    return index == null ? null : index * 2 + (turnRole(element) === 'assistant' ? 2 : 1);
  }
  function turnId(element, index) {
    const meta = turnMeta.get(element);
    if (meta && meta.id) return meta.id;
    const direct = element.getAttribute('data-turn-id')
      || element.getAttribute('data-turn-id-container')
      || element.getAttribute('data-testid');
    if (direct) return direct;
    const ids = element.getAttribute('data-chatgpt-search-message-ids');
    if (ids) return ids.trim().split(/\s+/)[0] || `materialized-${index}`;
    const unit = element.getAttribute('data-chatgpt-search-unit-key') || element.getAttribute('data-content-search-unit-key');
    if (unit) return unit;
    const group = searchTurnGroup(element);
    const groupKey = group && (group.getAttribute('data-content-search-turn-key') || group.getAttribute('data-turn-key'));
    return groupKey ? `${groupKey}:${turnRole(element)}` : `materialized-${index}`;
  }
  function modernSearchTurns() {
    const groups = qa('[data-content-search-turn-key]');
    if (!groups.length) return [];
    const output = [];
    const seen = new Set();
    for (const group of groups) {
      const groupKey = group.getAttribute('data-content-search-turn-key') || group.getAttribute('data-turn-key') || '';
      const units = qa('[data-chatgpt-search-unit-key]', group).filter(unit => searchTurnGroup(unit) === group);
      const logical = [];
      for (const unit of units) {
        const key = unit.getAttribute('data-chatgpt-search-unit-key') || '';
        const role = /:assistant$/.test(key) ? 'assistant' : /:user$/.test(key) ? 'user' : null;
        if (!role) continue;
        logical.push(setTurnMeta(unit, {
          role,
          groupKey,
          id: (unit.getAttribute('data-chatgpt-search-message-ids') || '').trim().split(/\s+/)[0] || key,
          ordinal: fallbackTurnIndex(unit) == null ? null : fallbackTurnIndex(unit) * 2 + (role === 'assistant' ? 2 : 1),
          adapter: 'content-search-unit',
        }));
      }
      if (!logical.some(element => turnRole(element) === 'assistant')) {
        const marker = qa('[data-chatgpt-agent-turn-start]', group).find(node => searchTurnGroup(node) === group);
        const host = marker && marker.parentElement;
        const text = host && readableNodeText(host).trim();
        const structural = host && !!q('[data-testid^="cot-"],[data-testid*="cot-v"],[data-testid*="error" i]', host);
        if (host && (text || structural)) logical.push(setTurnMeta(host, {
          role: 'assistant',
          groupKey,
          id: `${groupKey}:assistant`,
          ordinal: fallbackTurnIndex(group) == null ? null : fallbackTurnIndex(group) * 2 + 2,
          adapter: 'agent-turn-fallback',
        }));
      }
      logical.sort((a, b) => {
        if (a === b) return 0;
        try { return a.compareDocumentPosition(b) & Node.DOCUMENT_POSITION_FOLLOWING ? -1 : 1; } catch (_) { return 0; }
      });
      for (const element of logical) {
        if (!element || seen.has(element)) continue;
        seen.add(element);
        output.push(element);
      }
    }
    return output;
  }
  function materializedTurns() {
    if (materializedTurnCache) return materializedTurnCache;
    const modern = modernSearchTurns();
    const elements = modern.length ? modern : uniqueElements(SELECTORS.turns, document).map(element => element.closest?.('[data-testid^="conversation-turn-"]') || element);
    const seen = new Set();
    const output = [];
    for (const element of elements) {
      if (!element || seen.has(element)) continue;
      seen.add(element);
      const index = output.length;
      const meta = turnMeta.get(element) || {};
      output.push({
        element,
        role: turnRole(element),
        id: turnId(element, index),
        ordinal: turnOrdinal(element),
        adapter: meta.adapter || 'classic-turn',
        index,
      });
    }
    materializedTurnCache = output;
    return materializedTurnCache;
  }
  function readableNodeText(element) {
    if (!element) return '';
    const rendered = element.innerText;
    return rendered != null ? rendered : element.textContent || '';
  }
  function turnText(element) {
    if (!element) return '';
    if (observationTextCache && observationTextCache.has(element)) {
      state.metrics.turnTextCacheHits += 1;
      return observationTextCache.get(element);
    }
    state.metrics.turnTextReads += 1;
    const role = turnRole(element);
    let text = '';
    if (role === 'user') {
      const bubble = (element.matches && element.matches('[data-user-message-bubble]')) ? element : q('[data-user-message-bubble]', element);
      text = readableNodeText((bubble && (q('[data-search-result-target]', bubble) || bubble)) || element);
    } else if (role === 'assistant' && (element.hasAttribute('data-chatgpt-search-unit-key') || element.hasAttribute('data-content-search-unit-key'))) {
      text = semanticAssistantText(element);
    } else {
      const preferred = role === 'assistant' ? q('[data-message-author-role="assistant"], .markdown, [class*="markdown"]', element) : null;
      text = readableNodeText(preferred || element);
    }
    const result = normalizeLineEndings(text).replace(/^\s*(?:You|ChatGPT) said\s*:\s*/i, '').trim();
    state.metrics.turnTextChars += result.length;
    if (observationTextCache) observationTextCache.set(element, result);
    return result;
  }
  function assistantText(element) {
    return turnText(element);
  }
  function assistantWorkOnly(element) {
    if (!element || turnRole(element) !== 'assistant') return false;
    const hasWork = !!q('[data-testid^="cot-"],[data-testid*="cot-v"],[data-testid*="chain-of-thought" i],[data-testid*="reasoning-trace" i]', element);
    const isFinalUnit = /:assistant$/.test(element.getAttribute('data-chatgpt-search-unit-key') || '');
    const hasFinal = isFinalUnit || !!q('.markdown,[class*="markdown"],[data-testid*="final-answer" i],[data-message-author-role="assistant"]', element);
    return hasWork && !hasFinal;
  }
  function latestAssistantTurn({ readText = true } = {}) {
    const turns = materializedTurns();
    for (let i = turns.length - 1; i >= 0; i -= 1) {
      if (turns[i].role !== 'assistant') continue;
      const base = { ...turns[i], workOnly: assistantWorkOnly(turns[i].element) };
      if (!readText) {
        state.metrics.turnTextReadsSuppressedWhileGenerating += 1;
        return { ...base, text: null, fingerprint: null, textDeferred: true };
      }
      const text = assistantText(turns[i].element);
      const bounded = text.length > 80_000 ? `${text.slice(0, 40_000)}\n…\n${text.slice(-40_000)}` : text;
      return { ...base, text, fingerprint: fnv1a32(bounded), textDeferred: false };
    }
    return null;
  }
  function hydrateAssistantTurnText(assistant) {
    if (!assistant || assistant.text != null) return assistant;
    const text = assistantText(assistant.element);
    const bounded = text.length > 80_000 ? `${text.slice(0, 40_000)}\n…\n${text.slice(-40_000)}` : text;
    return { ...assistant, text, fingerprint: fnv1a32(bounded), textDeferred: false };
  }
  // Typed wording is inherited from 0.14.6; recovery now has its own request-scoped policy.
  // The field reports add "input stream", concatenated Retry, and "Think failed".
  function classifyPipelineFailureText(value) {
    const text = normalizeCompactText(String(value || ''));
    if (!text || text.length > 640) return null;
    const networkSentence = /^a network error occurred\.? please check your connection and try again[.!]?$/i.test(text);
    const core = (networkSentence ? text : text.replace(/\s*(?:retry|try again)\s*$/i, '')).trim().replace(/[.!]$/, '');
    let faultKind = null;
    if (/^(?:think|thinking) failed$/i.test(core)) faultKind = 'thinking-failed';
    else if (/^error in (?:the )?input stream$/i.test(core)) faultKind = 'input-stream-error';
    else if (/^error in (?:the )?message stream$/i.test(core)) faultKind = 'message-stream-error';
    else if (/^error in (?:the )?(?:response|output) stream$/i.test(core)) faultKind = 'response-stream-error';
    else if (/^(?:network error|a network error occurred)(?:\.? please check your connection and try again(?:\.? if this issue persists,? please contact us through our help center at help\.openai\.com)?)?$/i.test(core)) faultKind = 'network-error';
    else if (/^internal server error$/i.test(core)) faultKind = 'internal-server-error';
    else if (/^something went wrong(?: while generating (?:a|the) response)?$/i.test(core)) faultKind = 'something-went-wrong';
    else if (/^(?:there was an error generating|error generating|unable to generate) (?:a|the) response$/i.test(core)) faultKind = 'response-generation-error';
    else if (/^service unavailable$/i.test(core)) faultKind = 'service-unavailable';
    else if (/^bad gateway$/i.test(core)) faultKind = 'bad-gateway';
    else if (/^gateway timeout$/i.test(core)) faultKind = 'gateway-timeout';
    else if (/^(?:the )?message delivery timed out(?:\.? please try again)?$/i.test(core)) faultKind = 'message-delivery-timeout';
    return faultKind ? { kind: 'generation-error', faultKind, text, core } : null;
  }
  function classifyPipelineMaintenanceText(value) {
    const text = normalizeCompactText(String(value || ''));
    if (!text || text.length > 640) return null;
    // Strip only the adjacent action label. The phrase "try again" is part of
    // the field-observed maintenance sentence and must not be removed.
    const core = text.replace(/\s*retry\s*$/i, '').trim().replace(/[.!]$/, '');
    let maintenanceKind = null;
    if (/^(?:the|this) conversation is stale[,.]?\s+please reload(?: (?:the )?page)? and try again$/i.test(core)) maintenanceKind = 'conversation-stale';
    else if (/^(?:could not|unable to) load (?:this )?(?:chatgpt )?conversation$/i.test(core)) maintenanceKind = 'conversation-load-failed';
    return maintenanceKind ? {
      kind: 'page-shell-maintenance',
      maintenanceKind,
      text,
      core,
      action: 'safe-refresh-only',
      authority: 'operator-enabled Safe refresh evidence only; never Retry or prompt-send authority',
    } : null;
  }
  function maintenanceAllowsActiveRequestRefresh(kind) {
    return kind === 'conversation-stale' || kind === 'conversation-load-failed';
  }
  // Only small candidate subtrees are walked; no body text, clone, innerText,
  // network observer, or page mutation. Controls and hidden/prose subtrees are
  // excluded before text is accumulated. A display:contents host need not have
  // a box of its own; the actual text node's parent supplies rendering evidence.
  function boundedFaultLabel(root) {
    let visited = 0, text = '', visibleText = false, complete = true;
    let node = root;
    while (node) {
      if (++visited > 96) { complete = false; break; }
      let skip = false;
      if (node.nodeType === 1) {
        skip = node !== root && node.matches('button,[role="button"],svg,script,style,pre,code,blockquote,h4,[hidden],[aria-hidden="true"],.sr-only');
        if (!skip && node !== root && node.hasAttribute('style') && node.style.display === 'none') skip = true;
      } else if (node.nodeType === 3) {
        const part = node.nodeValue || '';
        if (text.length + part.length > 640) { complete = false; break; }
        text += part;
        if (part.trim() && !visibleText) {
          const parent = node.parentElement;
          // isVisible checks this element's computed style and rendered boxes.
          // The ancestor walk also rules out opacity/hidden ancestry.
          let hidden = false, steps = 0;
          for (let ancestor = parent; ancestor && steps < 24; ancestor = ancestor.parentElement, steps += 1) {
            const style = getComputedStyle(ancestor);
            if (ancestor.hidden || ancestor.getAttribute('aria-hidden') === 'true' || style.display === 'none' || style.visibility === 'hidden' || Number(style.opacity) === 0) { hidden = true; break; }
          }
          visibleText = !hidden && isVisible(parent);
          if (!hidden && !visibleText && parent && getComputedStyle(parent).display === 'contents') {
            const range = document.createRange();
            range.selectNodeContents(node);
            visibleText = range.getClientRects().length > 0;
          }
        }
      }
      if (!skip && node.firstChild) { node = node.firstChild; continue; }
      while (node && node !== root && !node.nextSibling) node = node.parentNode;
      if (!node || node === root) break;
      node = node.nextSibling;
    }
    return { text: normalizeCompactText(text), visible: visibleText, visited, complete };
  }
  function compactFaultIncident(fault) {
    if (!fault || typeof fault !== 'object') return null;
    const result = {};
    for (const key of ['id','signature','firstObservedAt','lastObservedAt','origin','sourceId','conversationId','kind','faultKind','text','source','ownerId','ownerRole','scope','activeTransactionId','domSnapshotId']) {
      result[key] = fault[key] == null ? null : trunc(String(fault[key]), key === 'text' ? 640 : 160);
    }
    result.observations = Math.max(1, Math.min(1000000, Number(fault.observations) || 1));
    result.runningAtObservation = !!fault.runningAtObservation;
    result.authority = 'evidence-only-never-retry-or-resume';
    return result;
  }
  function observeVisibleFaults(assistant = latestAssistantTurn({ readText: false }), { origin = 'active-check', includeHistory = false } = {}) {
    const started = performance.now();
    const turns = materializedTurns();
    const newest = turns.length ? turns[turns.length - 1] : null;
    const faults = [], seen = new Set(), reverseTurns = turns.slice().reverse();
    const scan = { candidateLimit: 96, candidatesMatched: 0, candidatesExamined: 0, candidateOverflow: 0, labelNodesVisited: 0, incompleteLabels: 0, rejectedProse: 0, suppressedHistorical: 0 };
    const add = (node, owner, source, allowUnrendered = false) => {
      if (!node || seen.has(node)) return;
      seen.add(node);
      // A quotation in a user message, code block, or final prose is not UI law.
      if (node.closest('pre,code,blockquote,.markdown,[contenteditable="true"],textarea,[data-user-message-bubble],[data-chatgpt-search-unit-key$=":user"]')) { scan.rejectedProse += 1; return; }
      const rootStyle = getComputedStyle(node);
      if (node.closest('[hidden],[aria-hidden="true"]') || rootStyle.display === 'none' || rootStyle.visibility === 'hidden' || Number(rootStyle.opacity) === 0) return;
      let hiddenAncestor = false;
      let ancestryDepth = 0;
      for (let ancestor = node.parentElement; ancestor && ancestryDepth < 24; ancestor = ancestor.parentElement, ancestryDepth += 1) {
        const style = getComputedStyle(ancestor);
        if (ancestor.hidden || ancestor.getAttribute('aria-hidden') === 'true' || style.display === 'none' || style.visibility === 'hidden' || Number(style.opacity) === 0) { hiddenAncestor = true; break; }
      }
      if (hiddenAncestor) return;
      const label = boundedFaultLabel(node);
      scan.labelNodesVisited += label.visited;
      if (!label.complete) { scan.incompleteLabels += 1; return; }
      let typed = classifyPipelineFailureText(label.text);
      if (!typed) typed = classifyPipelineMaintenanceText(label.text);
      if (!typed && source === 'structural-error-node') {
        if (/^(?:the )?message (?:you )?submitted was too long|^submitted was too long/i.test(label.text)) typed = { kind: 'submission-too-large', faultKind: 'submission-too-large', text: label.text };
        else if (/^you(?:’|')ve reached the maximum length for this conversation|^maximum length for this conversation/i.test(label.text)) typed = { kind: 'conversation-maximum', faultKind: 'conversation-maximum', text: label.text };
      }
      if (!typed || (!label.visible && !allowUnrendered)) return;
      const group = searchTurnGroup(node);
      const groupTurns = group ? turns.filter(turn => searchTurnGroup(turn.element) === group) : [];
      const associated = owner || groupTurns[groupTurns.length - 1] || null;
      const atTail = associated ? (newest && (associated.id === newest.id || (group && searchTurnGroup(newest.element) === group))) : true;
      const sidebar = !!node.closest('nav,[data-testid*="sidebar" i]');
      const current = !!atTail && !sidebar;
      if (!current) scan.suppressedHistorical += 1;
      const row = {
        ...typed, source, visible: label.visible,
        ownerId: associated ? associated.id : null,
        ownerRole: associated ? associated.role : null,
        ownerOrdinal: associated ? associated.ordinal : null,
        scope: associated ? (owner ? 'materialized-turn' : 'turn-group') : 'unattributed-page-alert',
        current, blocksAutomation: current && label.visible,
        // Even a materialized terminal skeleton with no box is not a completed answer.
        blocksCompletion: current && source === 'compact-assistant-skeleton',
        activeTransactionId: state.activeSend ? state.activeSend.id : null,
        selectorEvidence: { tag: node.tagName.toLowerCase(), role: node.getAttribute('role'), testId: node.getAttribute('data-testid'), classHint: trunc(String(node.className || ''), 220) },
        authority: typed.kind === 'page-shell-maintenance' ? 'maintenance-hold-or-operator-enabled-safe-refresh' : 'typed-fault-needs-request-owned-recovery-policy', backendOutcome: 'unknown',
      };
      faults.push(row);
      faultNodes.set(row, node);
    };
    // One combined selector query replaces ten repeated document queries.
    const nodes = qa(SELECTORS.errors.join(','));
    scan.candidatesMatched = nodes.length;
    scan.candidateOverflow = Math.max(0, nodes.length - scan.candidateLimit);
    for (let i = nodes.length - 1; i >= Math.max(0, nodes.length - scan.candidateLimit); i -= 1) {
      scan.candidatesExamined += 1;
      const node = nodes[i];
      const owner = reverseTurns.find(turn => turn.element === node || turn.element.contains(node));
      if (owner && owner.role === 'user') { scan.rejectedProse += 1; continue; }
      add(node, owner, 'structural-error-node');
    }
    const candidates = includeHistory ? turns.slice(-12).filter(turn => turn.role === 'assistant') : assistant ? [assistant] : [];
    for (const turn of candidates) {
      const node = turn.element;
      // A semantic assistant unit is normally a final response, not a skeleton.
      // Only a non-final compact host with no prose/answer markers may supply
      // this route, including the field's agent-turn-fallback representation.
      if (!node || /:assistant$/.test(node.getAttribute('data-chatgpt-search-unit-key') || '') || q('.markdown,[class*="markdown"],[data-message-author-role="assistant"],[data-testid*="final-answer" i],pre,code,blockquote', node)) continue;
      add(node, turn, 'compact-assistant-skeleton', true);
    }
    const current = faults.find(row => row.current && row.kind === 'conversation-maximum')
      || faults.find(row => row.current && row.blocksAutomation)
      || faults.find(row => row.current && row.blocksCompletion) || null;
    const at = nowIso();
    const observation = {
      schema: 'qomrade.fault-observation.v1', at, origin,
      mode: origin === 'officer-handoff' || origin === 'compact-diagnostics' ? 'operator-on-demand' : 'active-sample',
      runningAtObservation: state.running, pausedAtObservation: state.paused,
      current, signals: faults.slice(0, 24), scan,
      coverage: 'sampled materialized DOM only; stopped/paused/hidden intervals are not continuously monitored',
      backendOutcome: 'unknown', automaticRecovery: !!(state.running && !state.paused && !state.quarantine), recoveryCapability: true,
      durationMs: Math.round((performance.now() - started) * 100) / 100,
    };
    if (current) {
      const signature = fnv1a64(JSON.stringify([conversationIdFromPath(), current.faultKind, current.ownerId, current.text, current.source]));
      const previous = state.faultIncidents[state.faultIncidents.length - 1];
      if (signature === state.lastFaultSignature && previous && previous.signature === signature) {
        previous.lastObservedAt = at; previous.observations += 1;
      } else {
        const incidentId = `fault-${Date.now().toString(36)}-${state.eventSeq}`;
        const domSnapshotId = captureDomishEvent('fault-first-observed', {
          reason: current.faultKind || current.kind,
          severity: current.current ? 'error' : 'warn',
          origin,
          primaryNodes: [faultNodes.get(current)].filter(Boolean),
          relatedIds: [incidentId, signature],
          key: fnv1a64(`fault|${signature}`),
          context: { fault: compactFaultIncident(current), current: !!current.current, blocksAutomation: !!current.blocksAutomation },
        });
        const incident = compactFaultIncident({ ...current, id: incidentId, signature, firstObservedAt: at, lastObservedAt: at, origin, sourceId: QOMRADE_SOURCE_ID, conversationId: conversationIdFromPath(), runningAtObservation: state.running, observations: 1, domSnapshotId });
        state.faultIncidents.push(incident);
        if (state.faultIncidents.length > 12) state.faultIncidents.splice(0, state.faultIncidents.length - 12);
        logEvent('fault-observed', `Observed ${current.faultKind || current.maintenanceKind || current.kind || 'pipeline-surface'}; backend outcome remains unknown.`, incident);
      }
      state.lastFaultSignature = signature;
    } else state.lastFaultSignature = null;
    state.faultObservation = observation;
    return observation;
  }
  function classifyVisibleError(assistant = null) {
    return observeVisibleFaults(assistant || latestAssistantTurn({ readText: false })).current;
  }
  // @QOMRADE-CHUNK id=46.recovery title="Request-owned recovery; restored from released 0.18.2 and reconciled with 0.18.4"
  // Explicit failures are recoverable states, not successful replies or automatic
  // Halts. No absence-of-progress timeout authorizes a mutation. All actions are
  // current-tab-only, journaled, revocable, and tied to one rendered request.
  const FAULT_SETTLE_MS = 15_000;
  const FAULT_PARTIAL_OUTPUT_SETTLE_MS = 30_000;
  const FAULT_RETRY_GAP_MS = 45_000;
  const FAULT_RELOAD_LIMIT = 1;
  const FAULT_LEDGER_LIMIT = 16;
  const faultNodes = new WeakMap();
  let recoveryWriteBusy = false;
  let recoveryWriteQueued = false;
  let cancelRecoveryRead = null;
  let recoveryFixtureClockOffset = 0;
  let recoveryNavigationCommitted = false;
  let recoveryReplayPermit = null;
  let preexistingFailureAdvancePermit = null;
  function recoveryNow() { return Date.now() + (TEST_MODE ? recoveryFixtureClockOffset : 0); }
  function stableRequestId(id) { return typeof id === 'string' && !!id && !/^(?:pending-chatgpt-submit|fallback-turn|conversation-turn)-?[:\d]/.test(id); }
  function faultOwner(node) {
    const turns = materializedTurns();
    const users = turns.filter(turn => turn.role === 'user');
    const last = users[users.length - 1];
    const group = node && (node.closest('[data-turn-key]') || searchTurnGroup(node));
    let user = null;
    let method = null;
    if (group) {
      const contained = users.filter(turn => group.contains(turn.element));
      if (contained.length === 1) { user = contained[0]; method = 'same-request-group'; }
    } else if (node && node.closest('main')) {
      const before = users.filter(turn => !!(turn.element.compareDocumentPosition(node) & Node.DOCUMENT_POSITION_FOLLOWING));
      user = before[before.length - 1] || null;
      if (user) method = 'materialized-thread-order';
    }
    const stable = !!(user && stableRequestId(user.id));
    const latest = !!(user && last && last.id === user.id);
    return { userId: user?.id || null, stable, isLatestUser: latest,
      belongsToActive: !!(stable && latest && state.activeSend && state.activeSend.userTurnId === user.id),
      method, requestGroupKey: group?.getAttribute('data-turn-key') || group?.getAttribute('data-content-search-turn-key') || null };
  }
  function nativeRetryForFault(fault) {
    const node = faultNodes.get(fault);
    if (!node || !node.isConnected || fault.kind !== 'generation-error' || !fault.visible) return null;
    const card = node.closest('[role="alert"]') || node;
    const owner = faultOwner(card);
    if (!owner.stable || !owner.isLatestUser) return null;
    const controls = qa('button,[role="button"]', card).filter(control => isVisible(control) && isEnabled(control)
      && /^(?:retry|try again)$/i.test(normalizeCompactText(cleanElementVisibleText(control) || control.getAttribute('aria-label') || ''))
      && !/faster|new.chat|stop|continue|switch|upgrade/i.test(`${control.getAttribute('data-testid') || ''} ${control.getAttribute('aria-label') || ''}`));
    if (controls.length !== 1) return null;
    const control = controls[0];
    const known = /^(?:regenerate-thread-error-button|retry-thread-error-button)$/i.test(control.getAttribute('data-testid') || '');
    const field = card.matches('aside[role="alert"]') && /(?:^|\s)text-danger(?:\s|$)/.test(String(card.className || '')) && owner.method === 'same-request-group';
    if (!known && !field) return null;
    return { control, evidence: { label: normalizeCompactText(cleanElementVisibleText(control)), testId: control.getAttribute('data-testid'), adapter: known ? 'known-thread-error-id' : 'field-aside-danger-card' } };
  }
  function decorateRecoveryFault(fault) {
    if (!fault) return null;
    fault.owner = faultOwner(faultNodes.get(fault));
    fault.signature = fnv1a64(JSON.stringify([fault.faultKind, fault.text, fault.owner.userId]));
    const native = nativeRetryForFault(fault);
    fault.nativeRetry = native ? native.evidence : null;
    fault.authority = fault.owner.belongsToActive ? 'bounded-request-owned-recovery' : 'evidence-only';
    return fault;
  }
  function promoteCurrentOwnedConversationStale(fault) {
    if (!fault || fault.kind !== 'page-shell-maintenance' || fault.maintenanceKind !== 'conversation-stale' || !fault.current || !fault.visible || !state.activeSend) return fault;
    const owner = faultOwner(faultNodes.get(fault));
    if (!owner.belongsToActive) return fault;
    fault.kind = 'generation-error';
    fault.faultKind = 'conversation-stale';
    fault.recoveryOrigin = 'current-request-owned-conversation-stale';
    fault.owner = owner;
    fault.authority = 'bounded-request-owned-recovery';
    fault.action = 'fresh-message-recovery-never-native-retry';
    return fault;
  }
  function pipelineFaultObservation(assistant = null) {
    const observation = observeVisibleFaults(assistant || latestAssistantTurn({ readText: false }), { origin: 'recovery-sample' });
    for (const rawFault of observation.signals) {
      const fault = promoteCurrentOwnedConversationStale(rawFault);
      if (fault.kind === 'generation-error') decorateRecoveryFault(fault);
      else {
        fault.signature = fnv1a64(JSON.stringify([fault.kind, fault.maintenanceKind || fault.faultKind || null, fault.text, fault.ownerId || null]));
        fault.authority = fault.kind === 'page-shell-maintenance' ? 'maintenance-hold-or-operator-enabled-safe-refresh' : 'evidence-only';
      }
    }
    const owned = observation.signals.filter(fault => fault.current && fault.kind === 'generation-error' && fault.visible);
    const hardTerminal = observation.signals.find(fault => fault.current && ['conversation-maximum','submission-too-large'].includes(fault.kind));
    const maintenance = observation.signals.find(fault => fault.current && fault.kind === 'page-shell-maintenance');
    observation.current = hardTerminal || owned.find(fault => fault.nativeRetry) || owned[0] || maintenance || observation.current;
    if (observation.current && observation.current.kind === 'generation-error' && !observation.current.owner) decorateRecoveryFault(observation.current);
    observation.automaticRecovery = !!(state.running && !state.paused && !state.quarantine);
    observation.recoveryCapability = true;
    return observation;
  }
  function recoveryScheduleSnapshot() {
    const entry = state.faultRecovery.ledger.find(item => item.key === state.faultRecovery.activeKey);
    const suspended = !state.running || state.paused || state.quarantine || (pauseForHidden() && document.hidden) || panelEditorFocused();
    const nextAt = !suspended && entry && entry.lastSignature ? entry.nextAt : null;
    return { entryKey: entry?.key || null, at: nextAt, iso: nextAt ? new Date(nextAt).toISOString() : null,
      conditional: true, blocked: suspended ? 'operator-or-visibility-suspension' : state.faultRecovery.lastDecision?.blocked || null,
      meaning: 'earliest re-evaluation; not a promised click or a backend termination deadline' };
  }
  function recoverySnapshot() {
    return JSON.parse(JSON.stringify({ ...state.faultRecovery,
      policy: { action: 'send-exact-prompt-as-new-message', quietMs: faultQuietMs(), partialOutputQuietMs: FAULT_PARTIAL_OUTPUT_SETTLE_MS,
        partialOutputDisposition: 'preserve-and-resend-after-terminal-red-letter', minimumResendGapMs: FAULT_RETRY_GAP_MS, maximumResendBackoffMs: 300_000,
        nativeRetry: false, automaticReload: false, maxCommittedResendsPerFailedUser: 1, ledgerLimit: FAULT_LEDGER_LIMIT,
        differentLatestRequest: 'after stable user-bound failure evidence, preserve prior output and use the configured prompt as an ordinary cadence-bound next turn; never claim recovery authorship' },
      nextAttempt: recoveryScheduleSnapshot(),
      pendingTicket: state.recoveryResume ? { nonce: state.recoveryResume.nonce, armed: state.recoveryResume.armed, entryKey: state.recoveryResume.entryKey } : null,
      restorePending: state.recoveryRestorePending, writeInFlight: recoveryWriteBusy || autoRefreshWriteBusy,
      authority: 'current-tab explicit failure only; stopped means no recovery; no backend termination or exactly-once guarantee',
    }));
  }
  function recoveryOutcome(entry, outcome, detail = null) {
    const record = { at: nowIso(), outcome, detail, backendOutcome: 'unknown' };
    entry.status = outcome;
    entry.outcomes.push(record);
    entry.outcomes = entry.outcomes.slice(-12);
    logEvent('fault-recovery-outcome', outcome, { key: entry.key, ...record });
  }
  function recoveryHold(reason, delayMs = 30_000) {
    setPhase('RECOVERY_HOLD', reason);
    if (!state.running || state.paused || state.quarantine || (pauseForHidden() && document.hidden) || panelEditorFocused()) {
      clearControllerTimer('recovery suspended by operator or visibility');
      return;
    }
    scheduleTick(Math.max(500, Math.min(delayMs, 60_000)), 'request-owned recovery hold');
  }
  function preexistingFailureAdvanceEvidence(fault, { ownedComposer = false } = {}) {
    decorateRecoveryFault(fault);
    const turns = materializedTurns(), owner = fault?.owner;
    const user = owner?.userId ? turns.find(turn => turn.role === 'user' && turn.id === owner.userId) : null;
    const userText = user ? turnText(user.element) : '', promptMatch = !!(user && compareRenderedPrompt(userText, state.runPrompt).ok);
    const assistant = user ? turns.filter(turn => turn.role === 'assistant' && turn.index > user.index).slice(-1)[0] || null : null;
    const assistantText = assistant ? turnText(assistant.element) : '', work = workEvidenceObservation({ scope: 'all' });
    const partialOutputPresent = !!((assistantText && !classifyPipelineFailureText(assistantText)) || work.blocking), composer = findComposer();
    let blocked = null;
    if (!state.running || state.paused || state.quarantine || state.activeSend) blocked = 'run-not-ready-for-ordinary-next-turn';
    else if (!fault || fault.kind !== 'generation-error' || !fault.visible) blocked = 'generation-fault-not-visible';
    else if (!owner?.stable || !owner.isLatestUser || !user) blocked = 'fault-owner-not-stable-latest-user';
    else if (promptMatch) blocked = 'latest-failed-request-matches-configured-prompt';
    else if (!state.anchorConversationId || conversationIdFromPath() !== state.anchorConversationId) blocked = 'conversation-not-anchored';
    else if (pauseForHidden() && document.hidden) blocked = 'hidden-tab-pause';
    else if (panelEditorFocused()) blocked = 'operator-editing-qomrade';
    else if (!composer) blocked = 'composer-unavailable';
    else if (!ownedComposer && !composerIsEmpty(composer)) blocked = 'composer-not-empty';
    else if (ownedComposer && !editorPayloadEquivalent(readComposerText(composer), editorPromptPayload(state.runPrompt).payload).ok) blocked = 'composer-not-owned-prompt';
    else if (conversationBarrierObservation().present) blocked = 'conversation-terminal';
    else if (surfaceAuthenticityObservation({ detail: false }).hard) blocked = 'hard-false-gui';
    else if (visibleDialogObservation().blocking) blocked = 'dialog-visible';
    else if (continuationObservation().available) blocked = 'continuation-visible';
    else if (findStopButton()) blocked = 'generation-advertised';
    return { blocked, owner, userId: user?.id || null, userOrdinal: user?.ordinal ?? null,
      userTextHash: user ? fnv1a64(userText) : null, userTextChars: userText.length, promptMatch, partialOutputPresent,
      assistantId: assistant?.id || null, progressSignature: fnv1a64(JSON.stringify([fault?.signature || null, assistant?.id || null, assistant?.fingerprint || null, work.signature])),
      work: { blocking: work.blocking, overlapHazard: work.overlapHazard, signature: work.signature, records: work.records.length, unresolved: work.unresolved.length }, backendOutcome: 'unknown' };
  }
  function settlePreexistingFailureAdvance(observation, origin = 'controller') {
    const fault = observation?.current;
    if (!fault || fault.kind !== 'generation-error' || state.activeSend) return { handled: false, ready: false };
    const evidence = preexistingFailureAdvanceEvidence(fault);
    if (!evidence.owner?.stable || !evidence.owner.isLatestUser || evidence.promptMatch) return { handled: false, ready: false, evidence };
    const now = recoveryNow(), key = fnv1a64(JSON.stringify([state.anchorConversationId, evidence.userId, fault.faultKind, fault.text, fnv1a64(state.runPrompt)]));
    let record = state.faultRecovery.preexistingAdvance;
    if (!record || record.key !== key) {
      record = state.faultRecovery.preexistingAdvance = { schema: 'qomrade.preexisting-failure-advance.v1', key, firstObservedAt: nowIso(), firstObservedT: now,
        origin, conversationId: state.anchorConversationId, faultKind: fault.faultKind, faultText: fault.text, faultSignature: fault.signature,
        userId: evidence.userId, userOrdinal: evidence.userOrdinal, userTextHash: evidence.userTextHash, userTextChars: evidence.userTextChars,
        samples: 0, nextAt: now + (evidence.partialOutputPresent ? FAULT_PARTIAL_OUTPUT_SETTLE_MS : faultQuietMs()), status: 'settling', outcomes: [],
        authority: 'operator-authorized ordinary next turn after a stable latest different-request failure; never recovery authorship or native Retry authority' };
      logEvent('preexisting-failure-observed', 'The latest different request ended in a red-letter failure. qomrade will preserve it and wait for stable evidence before the configured ordinary next turn.', { key, faultKind: fault.faultKind, userId: evidence.userId, userOrdinal: evidence.userOrdinal, partialOutputPresent: evidence.partialOutputPresent, origin });
    }
    const settleMs = evidence.partialOutputPresent ? FAULT_PARTIAL_OUTPUT_SETTLE_MS : faultQuietMs();
    const changed = record.faultSignature !== fault.signature || record.progressSignature !== evidence.progressSignature;
    if (changed || evidence.blocked) { record.samples = 0; record.nextAt = Math.max(record.nextAt || 0, now + settleMs); }
    Object.assign(record, { lastObservedAt: nowIso(), lastObservedT: now, faultKind: fault.faultKind, faultText: fault.text, faultSignature: fault.signature,
      progressSignature: evidence.progressSignature, partialOutputPresent: evidence.partialOutputPresent, assistantId: evidence.assistantId, work: evidence.work,
      blocked: evidence.blocked, nextAt: record.nextAt });
    state.faultRecovery.lastObservation = observation;
    state.faultRecovery.lastDecision = { at: nowIso(), mode: 'ordinary-next-turn-after-different-request-failure', key, faultKind: fault.faultKind,
      userId: evidence.userId, samples: record.samples, blocked: evidence.blocked, partialOutput: evidence.partialOutputPresent, nextAt: record.nextAt, backendOutcome: 'unknown' };
    if (!evidence.blocked) record.samples += 1;
    if (evidence.blocked) { record.status = 'blocked'; recoveryHold(`A different latest request failed. The configured next turn waits: ${evidence.blocked}.`); return { handled: true, ready: false, record, evidence }; }
    if (record.samples < 2 || now < record.nextAt) {
      record.status = 'settling';
      setPhase('FOREIGN_FAULT_SETTLING', `A different latest request failed. Its partial work is preserved; qomrade will attempt the configured prompt as an ordinary next turn after stable evidence at ${new Date(record.nextAt).toISOString()}.`);
      scheduleTick(Math.min(replyPollMs(), Math.max(500, record.nextAt - now)), 'pre-existing different-request failure settlement');
      return { handled: true, ready: false, record, evidence };
    }
    if (Date.now() < state.nextSendAt) { record.status = 'waiting-ordinary-gap'; setPhase('WAITING_GAP', 'A different latest request failed and settled. qomrade will send the configured prompt when the ordinary send-to-send gap is due.'); scheduleGapTick(); return { handled: true, ready: false, record, evidence }; }
    preexistingFailureAdvancePermit = { epoch: state.effectControl.epoch, key, signature: fault.signature, userId: evidence.userId,
      conversationId: state.anchorConversationId, promptHash: fnv1a64(state.runPrompt), expiresAt: now + 120_000, consumed: false };
    record.status = 'authorized-next-turn'; record.authorizedAt = nowIso(); record.blocked = null;
    setPhase('READY_TO_SEND', 'A different latest request ended in a stable red-letter failure. qomrade is attempting the configured prompt as the next ordinary turn.');
    return { handled: true, ready: true, record, evidence };
  }
  function preexistingFailureAdvanceAllows(fault, options = {}) {
    const permit = preexistingFailureAdvancePermit;
    if (!permit || permit.consumed || permit.epoch !== state.effectControl.epoch || recoveryNow() > permit.expiresAt
      || permit.conversationId !== state.anchorConversationId || permit.promptHash !== fnv1a64(state.runPrompt) || state.activeSend) return false;
    const evidence = preexistingFailureAdvanceEvidence(fault, options);
    return !evidence.blocked && fault.signature === permit.signature && evidence.userId === permit.userId;
  }
  function attachPreexistingFailureAdvance(transaction) {
    const permit = preexistingFailureAdvancePermit;
    if (!permit || permit.consumed || permit.epoch !== state.effectControl.epoch) return;
    const record = state.faultRecovery.preexistingAdvance; permit.consumed = true;
    transaction.preexistingFailureAdvance = { schema: 'qomrade.preexisting-failure-advance-receipt.v1', key: permit.key,
      faultKind: record?.faultKind || null, faultText: record?.faultText || null, failedUserId: permit.userId, failedUserOrdinal: record?.userOrdinal ?? null,
      partialOutputPreserved: !!record?.partialOutputPresent, settledSamples: record?.samples || 0, settledAt: record?.authorizedAt || null,
      noRecoveryAuthorshipClaimed: true, authority: 'operator-authorized ordinary next turn after a stable latest different-request failure; no native Retry and no claim that qomrade owned the failed request' };
    transaction.authority = `${transaction.authority}; advanced only after a stable latest different-request failure under explicit run authority`;
    if (record) { record.status = 'committed'; record.committedAt = nowIso(); record.transactionId = transaction.id;
      record.outcomes = [...(record.outcomes || []), { at: record.committedAt, outcome: 'ordinary-next-turn-committed', transactionId: transaction.id }].slice(-8); }
    state.faultRecovery.preexistingAdvanceCount += 1;
    logEvent('preexisting-failure-advanced', 'Sent the configured prompt as an ordinary next turn after a stable failure on a different latest request.', transaction.preexistingFailureAdvance);
  }
  function faultRecoveryEntry(fault) {
    const root = state.activeSend?.recoveryRootKey;
    let entry = state.faultRecovery.ledger.find(item => item.conversationId === state.anchorConversationId
      && ((root && item.key === root) || item.userIds.includes(fault.owner.userId)));
    if (!entry) {
      const key = fnv1a64(`${state.anchorConversationId}|${fault.owner.userId}`);
      entry = { key, conversationId: state.anchorConversationId, userId: fault.owner.userId, userIds: [fault.owner.userId],
        firstSeenAt: nowIso(), nativeAttempts: 0, reloadAttempts: 0, replayAttempts: 0, samples: 0,
        nextAt: recoveryNow() + faultQuietMs(), lastSignature: null, progressSignature: null, status: 'settling', outcomes: [] };
      state.faultRecovery.ledger.push(entry);
      state.faultRecovery.ledger = state.faultRecovery.ledger.slice(-FAULT_LEDGER_LIMIT);
    }
    state.activeSend.recoveryRootKey = entry.key;
    state.faultRecovery.activeKey = entry.key;
    return entry;
  }
  function recoveryEvidence(fault, { reload = false, ownedComposer = false } = {}) {
    return withReadSnapshot('recoveryEvidence', () => {
      let blocked = null;
      const composer = findComposer();
      const turns = materializedTurns();
      const active = state.activeSend;
      const user = active && turns.find(turn => turn.role === 'user' && turn.id === active.userTurnId);
      const answer = latestAssistantTurn();
      const answerPresent = !!(user && answer && answer.index > user.index && answer.text
        && !classifyPipelineFailureText(answer.text) && (/:assistant$/.test(answer.element.getAttribute('data-chatgpt-search-unit-key') || '')
          || answer.element.matches('[data-message-author-role="assistant"]')
          || q('.markdown,[class*="markdown"],[data-markdown-text-style="assistant-message"],[data-message-author-role="assistant"],[data-testid*="final-answer" i]', answer.element)));
      const work = workEvidenceObservation({ scope: 'active-response' });
      const explicitFailure = !!(fault && fault.kind === 'generation-error' && fault.owner?.belongsToActive && user);
      const partialOutputPresent = !!(explicitFailure && (answerPresent || work.blocking));
      if (!state.running || state.paused || state.quarantine || !active || active.outcome) blocked = 'run-not-authorized';
      else if (!state.anchorConversationId || conversationIdFromPath() !== state.anchorConversationId) blocked = 'conversation-not-anchored';
      else if (pauseForHidden() && document.hidden) blocked = 'hidden-tab-pause';
      else if (panelEditorFocused()) blocked = 'operator-editing-qomrade';
      else if (!composer) blocked = 'composer-unavailable';
      else if (!ownedComposer && !composerIsEmpty(composer)) blocked = 'composer-not-empty';
      else if (conversationBarrierObservation().present) blocked = 'conversation-terminal';
      else if (surfaceAuthenticityObservation({ detail: false }).hard) blocked = 'hard-false-gui';
      else if (visibleDialogObservation().blocking) blocked = 'dialog-visible';
      else if (continuationObservation().available) blocked = 'continuation-visible';
      else if (findStopButton()) blocked = 'generation-advertised';
      else if (!explicitFailure) blocked = 'fault-not-owned-by-active-request';
      else if (recoveryNow() < state.faultRecovery.postReloadUntil) blocked = 'post-reload-settling';
      return { blocked, answerPresent, partialOutputPresent, userId: user?.id || null, assistantId: answer?.id || null,
        progressSignature: fnv1a64(JSON.stringify([answer?.id || null, answer?.fingerprint || null, work.signature])),
        work: { blocking: work.blocking, overlapHazard: work.overlapHazard, signature: work.signature,
          records: work.records.length, unresolved: work.unresolved.length,
          disposition: partialOutputPresent ? 'preserve-and-resend-after-terminal-fault' : work.authority },
        backendOutcome: 'unknown' };
    });
  }
  async function persistRecoveryBarrier(reason, expectedKey, epoch) {
    if (recoveryWriteBusy || autoRefreshWriteBusy || typeof GM_getTab !== 'function' || typeof GM_saveTab !== 'function') return false;
    recoveryWriteBusy = true;
    const built = buildTabRecord(reason);
    const record = built.record;
    const marker = `recovery-${epoch}-${Date.now().toString(36)}-${Math.random().toString(36).slice(2)}`;
    record.recoveryWriteWitness = marker;
    const expected = record.faultRecovery.ledger.find(item => item.key === expectedKey);
    const started = performance.now();
    let verified = false;
    let cancelThisRead = null;
    let saveRejected = false;
    try {
      state.persistence.writes += 1;
      state.persistence.lastWriteAt = nowIso();
      state.persistence.lastWriteReason = reason;
      state.persistence.lastWriteBytes = utf8Bytes(JSON.stringify(record));
      state.persistence.maxWriteBytes = Math.max(state.persistence.maxWriteBytes, state.persistence.lastWriteBytes);
      const result = GM_saveTab(record);
      if (result && typeof result.then === 'function') result.catch(() => { saveRejected = true; if (cancelThisRead) cancelThisRead(); });
      verified = await new Promise(resolve => {
        let done = false;
        let retryTimer = null;
        const finish = ok => { if (done) return; done = true; clearTimeout(timeout); if (retryTimer) clearTimeout(retryTimer); cancelRecoveryRead = null; resolve(!!ok); };
        const timeout = setTimeout(() => finish(false), 2_500);
        cancelThisRead = () => finish(false);
        cancelRecoveryRead = cancelThisRead;
        const read = () => {
          if (done || saveRejected || epoch !== state.effectControl.epoch) return finish(false);
          try {
            GM_getTab(value => {
              if (done || saveRejected || epoch !== state.effectControl.epoch) return finish(false);
              const actual = value?.faultRecovery?.ledger?.find(item => item.key === expectedKey);
              const countsMatch = !expectedKey || !!(actual && expected
                && ['nativeAttempts','reloadAttempts','replayAttempts'].every(key => actual[key] === expected[key]));
              const ticketMatch = JSON.stringify(value?.recoveryResume ?? null) === JSON.stringify(record.recoveryResume ?? null);
              if (value?.sourceId === QOMRADE_SOURCE_ID && value?.recoveryWriteWitness === marker && countsMatch && ticketMatch) return finish(true);
              retryTimer = setTimeout(read, 100);
            });
          } catch (_) { finish(false); }
        };
        read();
      });
    } catch (error) {
      state.persistence.writeErrors += 1;
      logEvent('recovery-persistence-error', 'Recovery journal write or read-back failed.', { message: String(error?.message || error) });
    } finally {
      state.faultRecovery.writeReceipts.push({ at: nowIso(), reason, marker, epoch, verified, elapsedMs: Math.round(performance.now() - started) });
      state.faultRecovery.writeReceipts = state.faultRecovery.writeReceipts.slice(-8);
      recoveryWriteBusy = false;
      if (recoveryWriteQueued) { recoveryWriteQueued = false; saveTabRecord('recovery-write-reconcile'); }
    }
    return verified;
  }
  function recoveryReplayAllows(fault) {
    const permit = recoveryReplayPermit;
    if (!permit || permit.consumed || permit.epoch !== state.effectControl.epoch || recoveryNow() > permit.expiresAt
      || state.activeSend?.id !== permit.parentId) return false;
    decorateRecoveryFault(fault);
    if (fault?.signature !== permit.signature || fault.owner.userId !== permit.userId) return false;
    return !recoveryEvidence(fault, { ownedComposer: true }).blocked;
  }
  function attachRecoveryReplayLineage(transaction) {
    const permit = recoveryReplayPermit;
    if (!permit || permit.consumed || permit.epoch !== state.effectControl.epoch || state.activeSend?.id !== permit.parentId) return;
    const entry = state.faultRecovery.ledger.find(item => item.key === permit.entryKey);
    const parentModel = state.activeSend && state.activeSend.model ? JSON.parse(JSON.stringify(state.activeSend.model)) : null;
    transaction.recoveryRootKey = permit.entryKey;
    transaction.recoveryParentId = permit.parentId;
    transaction.recoveryKind = 'fresh-prompt-after-explicit-failure';
    transaction.recoveryModelPolicy = permit.modelPolicy || state.modelGate.runPolicy || MODEL_POLICY_SMART_PRO;
    transaction.recoveryModelPreference = permit.modelPreference || state.modelGate.runPreference || '5.6-first';
    const parentFamily = parentModel && Number(parentModel.family);
    transaction.recoveryModelTransition = {
      from: parentModel,
      to: transaction.model ? JSON.parse(JSON.stringify(transaction.model)) : null,
      scope: transaction.recoveryModelPolicy === MODEL_POLICY_SMART_PRO ? 'failed-request-lineage-until-success' : 'operator-selected-policy',
      reason: transaction.recoveryModelPolicy !== MODEL_POLICY_SMART_PRO
        ? `operator-selected ${transaction.recoveryModelPolicy} model policy retained for this recovery lineage`
        : transaction.recoveryModelPreference === '6-fallback'
          ? (parentFamily === 5.6
            ? 'the GPT-5.6-backed request failed; use GPT-6-first for this failed request lineage until a stable reply succeeds'
            : 'continue GPT-6-first for this unresolved failed request lineage until a stable reply succeeds')
          : 'ordinary GPT-5.6-first recovery selection',
    };
    transaction.backendDuplicateRisk = 'A new operator-authorized message; UI cannot prove that prior backend work terminated.';
    finalizeTurnReceipt(null, 'superseded-by-prompt-resend');
    permit.consumed = true;
    if (entry) {
      entry.resendsCommitted = (entry.resendsCommitted || 0) + 1;
      entry.resendUserIds = [...(entry.resendUserIds || []), permit.userId].slice(-16);
      entry.nextAt = recoveryNow() + Math.min(300_000, FAULT_RETRY_GAP_MS * 2 ** Math.min(4, entry.resendsCommitted - 1));
      recoveryOutcome(entry, 'prompt-resend-committed', { transactionId: transaction.id,
        parentId: permit.parentId, failedUserId: permit.userId, promptHash: transaction.promptHash,
        nativeRetryClicked: false, newMessage: true, modelPreference: transaction.recoveryModelPreference, modelTransition: transaction.recoveryModelTransition });
    }
  }
  async function requestExactFaultRestart(entry, fault, guard) {
    effectCheckpoint(guard, 'prompt-resend-entry');
    const user = materializedTurns().find(turn => turn.id === fault.owner.userId && turn.role === 'user');
    if (!user || !compareRenderedPrompt(turnText(user.element), state.runPrompt).ok) {
      recoveryHold('Fresh prompt Send waits for the matching stable latest failed request.');
      return;
    }
    if ((entry.resendUserIds || []).includes(user.id)) {
      recoveryHold('A new-message Send was already committed for this failed request; waiting for the new request instead of sending it twice.');
      return;
    }
    // This counts preparation reservations. Actual committed resends are tracked
    // separately so a menu/content hold cannot exhaust an action budget.
    entry.replayAttempts += 1;
    entry.nextAt = Math.max(entry.nextAt || 0, recoveryNow() + faultQuietMs());
    recoveryOutcome(entry, 'prompt-resend-reserved', { parentId: state.activeSend.id,
      failedUserId: user.id, promptHash: fnv1a64(state.runPrompt), risk: 'prior backend termination unknown' });
    const saved = await persistRecoveryBarrier('before-fresh-prompt-resend', entry.key, guard.operation.epoch);
    effectCheckpoint(guard, 'prompt-resend-after-persistence');
    invalidateTurnCache('prompt-resend-reservation-commit');
    const fresh = pipelineFaultObservation().current;
    const evidence = recoveryEvidence(fresh);
    if (!saved || evidence.blocked || fresh?.signature !== fault.signature) {
      if (!saved) {
        entry.persistenceFailures = (entry.persistenceFailures || 0) + 1;
        const delay = Math.min(300_000, 30_000 * 2 ** Math.min(4, entry.persistenceFailures - 1));
        entry.nextAt = recoveryNow() + delay;
        recoveryOutcome(entry, 'persistence-unconfirmed', { reason: 'journal-readback-unconfirmed',
          persistenceFailures: entry.persistenceFailures, nextAt: entry.nextAt, retryable: true });
        recoveryHold('Fresh prompt journal read-back was not confirmed. No unjournaled Send occurred; qomrade will reconcile and try this same failed request again.', delay);
      } else {
        recoveryOutcome(entry, 'prompt-resend-cancelled', { reason: evidence.blocked || 'fault-changed' });
        recoveryHold('Fresh prompt Send cancelled because request evidence changed.');
      }
      return;
    }
    entry.persistenceFailures = 0;
    const parentModel = state.activeSend && state.activeSend.model;
    const modelPolicy = state.modelGate.runPolicy || MODEL_POLICY_SMART_PRO;
    const parentWasPreferred56 = modelPolicy === MODEL_POLICY_SMART_PRO && parentModel && (Number(parentModel.family) === 5.6
      || modelVersionIsPreferred56(parseModelVersion(parentModel.label || '')));
    const inheritedSixFallback = modelPolicy === MODEL_POLICY_SMART_PRO && (state.activeSend?.recoveryModelPreference === '6-fallback'
      || state.modelGate.runPreference === '6-fallback');
    const modelPreference = modelPolicy === MODEL_POLICY_SMART_PRO
      ? (parentWasPreferred56 || inheritedSixFallback ? '6-fallback' : '5.6-first')
      : state.modelGate.runPreference;
    if (modelPolicy === MODEL_POLICY_SMART_PRO && parentWasPreferred56 && state.modelGate.runPreference !== '6-fallback') {
      state.modelGate.runPreference = '6-fallback';
      state.modelGate.lastPreferenceSwitch = {
        at: nowIso(), from: '5.6-first', to: '6-fallback',
        reason: `explicit ${fresh.faultKind || 'generation'} failure on a GPT-5.6-backed request; fallback is scoped until a stable reply succeeds`,
        failedTransactionId: state.activeSend.id,
        failedUserId: fresh.owner.userId,
      };
      logEvent('model-fallback-armed', 'The GPT-5.6-backed request failed; the fresh prompt will use GPT-6 fallback.', state.modelGate.lastPreferenceSwitch);
    }
    recoveryReplayPermit = { epoch: guard.operation.epoch, parentId: state.activeSend.id,
      entryKey: entry.key, userId: fresh.owner.userId, signature: fresh.signature,
      expiresAt: recoveryNow() + 60_000, consumed: false, modelPolicy, modelPreference };
    try {
      setPhase('RESENDING_PROMPT', 'Sending the exact operator prompt again as a new message. No Retry button.');
      await sendPrompt();
      if (guard.valid() && !recoveryReplayPermit?.consumed) {
        recoveryOutcome(entry, 'prompt-resend-not-dispatched', { draftPreserved: true });
        recoveryHold('The fresh prompt was not sent. Still observing; any remaining draft is untouched.');
      }
    } finally { recoveryReplayPermit = null; }
  }
  async function handlePipelineFault(observation) {
    const fault = observation?.current;
    if (!fault || fault.kind !== 'generation-error') return false;
    state.faultRecovery.lastObservation = observation;
    state.stableSamples = 0;
    if (!fault.owner?.belongsToActive) {
      const adopted = adoptExactPromptSuccessor({ expectedUserId: fault.owner?.userId || null, origin: 'fault-owner-successor' });
      if (adopted) decorateRecoveryFault(fault);
    }
    if (!fault.owner?.belongsToActive) {
      recoveryHold('A structural failure is visible, but its latest user request does not render the exact captured prompt for this run.');
      return true;
    }
    const entry = faultRecoveryEntry(fault);
    let evidence = recoveryEvidence(fault);
    const partialOutput = !!evidence.partialOutputPresent;
    const settleMs = partialOutput ? FAULT_PARTIAL_OUTPUT_SETTLE_MS : faultQuietMs();
    const changed = entry.lastSignature !== fault.signature || entry.progressSignature !== evidence.progressSignature;
    if (changed || evidence.blocked) {
      entry.samples = 0;
      entry.nextAt = Math.max(entry.nextAt || 0, recoveryNow() + settleMs);
    }
    entry.lastSignature = fault.signature;
    entry.progressSignature = evidence.progressSignature;
    entry.lastKind = fault.faultKind;
    entry.lastFault = { kind: fault.faultKind, text: fault.text, userId: fault.owner.userId, signature: fault.signature };
    entry.samples += evidence.blocked ? 0 : 1;
    entry.lastSeenAt = nowIso();
    if (partialOutput && entry.partialOutputSignature !== evidence.progressSignature) {
      entry.partialOutputSignature = evidence.progressSignature;
      entry.partialOutputObservedAt = nowIso();
      entry.partialOutput = { assistantId: evidence.assistantId, answerPresent: evidence.answerPresent,
        work: evidence.work, disposition: 'preserved; terminal red-letter authorizes a later fresh prompt after quiet settlement' };
      const assistant = latestAssistantTurn();
      if (assistant) {
        captureZipFromAssistant(assistant);
        scheduleZipRescan(assistant);
      }
      logEvent('fault-partial-output-preserved', 'Partial answer or structural work was preserved beside a terminal red-letter failure; it will not strand the run.', entry.partialOutput);
    }
    const witness = state.faultRecovery.postReloadWitness;
    if (witness?.entryKey === entry.key && recoveryNow() >= state.faultRecovery.postReloadUntil) {
      witness.observedAt = nowIso();
      witness.verdict = evidence.blocked ? 'post-reload-signals-conflict' : partialOutput ? 'persistent-failure-with-preserved-partial-output' : 'persistent-owned-failure';
      witness.post = { userId: fault.owner.userId, faultKind: fault.faultKind, signature: fault.signature,
        assistantId: evidence.assistantId, answerPresent: evidence.answerPresent, partialOutput, blocked: evidence.blocked,
        workSignature: evidence.work.signature, sameUserAsPre: fault.owner.userId === witness.pre.userId,
        sameFaultAsPre: fault.signature === witness.pre.signature, backendOutcome: 'unknown' };
    }
    state.faultRecovery.lastDecision = { at: nowIso(), key: entry.key, faultKind: fault.faultKind, userId: fault.owner.userId,
      samples: entry.samples, blocked: evidence.blocked, answerConflict: false, partialOutput,
      partialOutputSettleMs: settleMs, nextAt: entry.nextAt, backendOutcome: 'unknown' };
    if (evidence.blocked) {
      if (evidence.blocked === 'hard-false-gui') enforceHardFalseGui('fault-recovery');
      else if (evidence.blocked === 'conversation-terminal') stopForConversationTerminal(conversationBarrierObservation(), 'fault-recovery');
      else recoveryHold(`Fault: ${fault.text}. Recovery waits: ${evidence.blocked}.`);
      return true;
    }
    if (entry.samples < 2 || recoveryNow() < entry.nextAt) {
      const preservation = partialOutput ? ' Partial output is preserved; it is not a completion or overlap blocker.' : '';
      setPhase('FAULT_SETTLING', `Fault: ${fault.text}.${preservation} Earliest fresh prompt ${new Date(entry.nextAt).toISOString()}; checking this same request.`);
      scheduleTick(Math.min(replyPollMs(), Math.max(500, entry.nextAt - recoveryNow())), 'fault quiet settlement');
      return true;
    }
    const guard = createEffectGuard();
    try {
      effectCheckpoint(guard, 'fault-prompt-resend-admission');
      await requestExactFaultRestart(entry, fault, guard);
    } catch (error) {
      if (error?.qomradeEffectCancelled) recordEffectCancellation(error);
      else throw error;
    } finally {
      if (state.effectControl.active?.id === guard.operation.id) state.effectControl.active = null;
    }
    return true;
  }
  function noteRecoveryFaultCleared() {
    const entry = state.faultRecovery.ledger.find(item => item.key === state.activeSend?.recoveryRootKey);
    if (!entry || entry.lastSignature === null) return;
    entry.lastSignature = null;
    entry.samples = 0;
    if (state.faultRecovery.postReloadWitness?.entryKey === entry.key) {
      state.faultRecovery.postReloadWitness.verdict = 'fault-not-visible-completion-not-established';
      state.faultRecovery.postReloadWitness.observedAt = nowIso();
    }
    recoveryOutcome(entry, 'fault-no-longer-visible', { completionEstablished: false });
  }
  function tryAdoptExistingFailedRequest(observation = null, origin = 'start') {
    if (!state.running || state.paused || state.quarantine || state.activeSend || !state.runPrompt
      || !state.anchorConversationId || conversationIdFromPath() !== state.anchorConversationId) return false;
    const composer = findComposer();
    if (!composer || !composerIsEmpty(composer)) return false;
    observation = observation || pipelineFaultObservation();
    const fault = observation.current;
    if (!fault || fault.kind !== 'generation-error' || !fault.owner?.stable || !fault.owner.isLatestUser) return false;
    const turns = materializedTurns();
    const user = turns.find(turn => turn.role === 'user' && turn.id === fault.owner.userId);
    if (!user || !compareRenderedPrompt(turnText(user.element), state.runPrompt).ok) return false;
    const before = turns.slice(0, user.index);
    const previous = before.filter(turn => turn.role === 'assistant').slice(-1)[0];
    state.activeSend = { schema: 'qomrade.send-transaction.v2', id: `recover-adopt-${Date.now().toString(36)}`, startedAt: nowIso(),
      clickedAt: null, clickMode: 'operator-start-adopted-existing-failed-request', promptHash: fnv1a64(state.runPrompt), promptChars: state.runPrompt.length,
      preTurnIds: before.map(turn => turn.id), preMaxOrdinal: null, userTurnId: user.id, userTurnOrdinal: user.ordinal,
      userAdoptedAt: nowIso(), baselineAssistantId: previous?.id || null, model: null, outcome: null,
      adoptionOrigin: origin,
      authority: 'operator Start plus latest matching failed request; no earlier Send authorship claimed' };
    state.baselineAssistantId = previous?.id || null;
    state.waitingSince = Date.now();
    state.lastSendAt = Date.now();
    state.nextSendAt = Date.now() + settings.gapMinutes * 60_000;
    state.adoptedWithoutClick += 1;
    decorateRecoveryFault(fault);
    const entry = faultRecoveryEntry(fault);
    entry.samples = 0;
    entry.nextAt = Math.max(entry.nextAt || 0, recoveryNow() + faultQuietMs());
    logEvent('failed-request-adopted', 'Tracking the matching failed request before resending the operator prompt as a new message.', { origin, userId: user.id, transactionId: state.activeSend.id, rootKey: entry.key });
    setPhase('FAULT_SETTLING', 'Confirming the matching request failure before sending the exact operator prompt again.');
    scheduleTick(replyPollMs(), 'observe adopted failure');
    return true;
  }
  async function restoreRecoveryTicket(record) {
    state.recoveryResume = null;
    state.recoveryRestorePending = false;
    logEvent('recovery-ticket-refused', 'Automatic reload recovery tickets are retired; ordinary Start is required.', { previousTicketPresent: !!record?.recoveryResume });
    persistContinuity('retired-recovery-ticket-cleared');
    render();
  }
  function elementSummary(element, { redactContent = false, includePresentation = false } = {}) {
    if (!element) return null;
    const attributes = {};
    for (const attribute of Array.from(element.attributes || [])) {
      if (/^(?:data-|aria-|role$|name$|type$|href$|download$|contenteditable$|class$|id$)/i.test(attribute.name)) {
        attributes[attribute.name] = trunc(attribute.value, 500);
      }
    }
    let presentation = null;
    let rect = null;
    if (includePresentation) {
      try {
        const style = getComputedStyle(element);
        presentation = {
          color: style.color,
          backgroundColor: style.backgroundColor,
          borderColor: style.borderColor,
          display: style.display,
          visibility: style.visibility,
          opacity: style.opacity,
        };
      } catch (_) {}
      try {
        const box = element.getBoundingClientRect();
        rect = { x: Math.round(box.x), y: Math.round(box.y), width: Math.round(box.width), height: Math.round(box.height) };
      } catch (_) {}
    }
    return {
      tag: element.tagName.toLowerCase(),
      id: element.id || null,
      className: trunc(typeof element.className === 'string' ? element.className : '', 500) || null,
      testId: element.getAttribute('data-testid'),
      ariaLabel: element.getAttribute('aria-label'),
      role: element.getAttribute('role'),
      visible: isVisible(element),
      enabled: isEnabled(element),
      text: redactContent ? null : trunc(normalizeCompactText(element.textContent || ''), 600),
      html: redactContent ? null : trunc(element.outerHTML || '', 2_400),
      childCount: element.childElementCount,
      attributes,
      presentation,
      rect,
    };
  }
  function domishAttributeMap(element) {
    const attributes = {};
    if (!(element instanceof Element)) return attributes;
    for (const attribute of Array.from(element.attributes || [])) {
      if (!/^(?:id$|class$|role$|name$|type$|title$|href$|download$|contenteditable$|disabled$|hidden$|data-|aria-)/i.test(attribute.name)) continue;
      attributes[attribute.name] = trunc(attribute.value, 800);
      if (Object.keys(attributes).length >= 36) break;
    }
    return attributes;
  }
  function domishNodeIdentity(element) {
    if (!(element instanceof Element)) return null;
    return {
      tag: element.tagName.toLowerCase(),
      id: element.id || null,
      className: trunc(typeof element.className === 'string' ? element.className : '', 700) || null,
      role: element.getAttribute('role'),
      testId: element.getAttribute('data-testid'),
      ariaLabel: element.getAttribute('aria-label'),
      dataState: element.getAttribute('data-state'),
      dataTurnKey: element.getAttribute('data-turn-key') || element.getAttribute('data-content-search-turn-key') || null,
      contentSearchKey: element.getAttribute('data-content-search-unit-key') || null,
      chatgptSearchKey: element.getAttribute('data-chatgpt-search-unit-key') || null,
      messageIds: trunc(element.getAttribute('data-chatgpt-search-message-ids') || '', 500) || null,
    };
  }
  function domishLocator(element) {
    if (!(element instanceof Element)) return null;
    const parts = [];
    let node = element;
    for (let depth = 0; node && node !== document.documentElement && depth < 10; depth += 1, node = node.parentElement) {
      let part = node.tagName.toLowerCase();
      if (node.id) {
        part += `#${trunc(node.id, 120)}`;
        parts.unshift(part);
        break;
      }
      const testId = node.getAttribute('data-testid');
      const role = node.getAttribute('role');
      const key = node.getAttribute('data-content-search-unit-key') || node.getAttribute('data-chatgpt-search-unit-key') || node.getAttribute('data-turn-key');
      if (testId) part += `[data-testid="${trunc(testId, 120)}"]`;
      else if (key) part += `[data-key="${trunc(key, 120)}"]`;
      else if (role) part += `[role="${trunc(role, 80)}"]`;
      else if (node.parentElement) {
        const siblings = Array.from(node.parentElement.children).filter(child => child.tagName === node.tagName);
        if (siblings.length > 1) part += `:nth-of-type(${siblings.indexOf(node) + 1})`;
      }
      parts.unshift(part);
    }
    return parts.join(' > ');
  }
  function domishPresentation(element) {
    if (!(element instanceof Element)) return null;
    let style = null, rect = null;
    try {
      const computed = getComputedStyle(element);
      style = {
        display: computed.display,
        visibility: computed.visibility,
        opacity: computed.opacity,
        position: computed.position,
        color: computed.color,
        backgroundColor: computed.backgroundColor,
        borderColor: computed.borderColor,
        overflow: computed.overflow,
      };
    } catch (_) {}
    try {
      const box = element.getBoundingClientRect();
      rect = { x: Math.round(box.x), y: Math.round(box.y), width: Math.round(box.width), height: Math.round(box.height), top: Math.round(box.top), bottom: Math.round(box.bottom) };
    } catch (_) {}
    return { style, rect };
  }
  function domishMarkupRecord(element, limit = MAX_DOMISH_MARKUP_CHARS) {
    let html = '';
    try { html = element && element.outerHTML || ''; } catch (_) {}
    const half = Math.floor(limit / 2);
    return {
      chars: html.length,
      hash: fnv1a64(html),
      head: html.slice(0, half),
      tail: html.length > limit ? html.slice(-half) : '',
      truncated: html.length > limit,
    };
  }
  function domishTextRecord(element, limit = MAX_DOMISH_TEXT_CHARS) {
    const redacted = !!(element && (element.isContentEditable || element.matches?.('textarea,input')));
    const text = redacted ? '' : normalizeLineEndings(element && element.textContent || '');
    const half = Math.floor(limit / 2);
    return {
      redacted,
      chars: text.length,
      hash: fnv1a64(text),
      head: text.slice(0, half),
      tail: text.length > limit ? text.slice(-half) : '',
      truncated: text.length > limit,
    };
  }
  function domishAncestry(element) {
    const rows = [];
    let node = element && element.parentElement;
    for (let depth = 0; node && depth < 10; depth += 1, node = node.parentElement) {
      rows.push({ depth: depth + 1, locator: domishLocator(node), identity: domishNodeIdentity(node) });
      if (node.matches('main,body,[data-turn-key],[data-content-search-turn-key],[role="alert"],[role="dialog"]')) break;
    }
    return rows;
  }
  function domishSiblingSummary(element) {
    const summarize = node => node instanceof Element ? {
      locator: domishLocator(node), identity: domishNodeIdentity(node), text: domishTextRecord(node, 800), childCount: node.childElementCount,
    } : null;
    return { previous: summarize(element && element.previousElementSibling), next: summarize(element && element.nextElementSibling) };
  }
  function domishTreeRecord(root) {
    const budget = { nodes: 0 };
    const visit = (element, depth) => {
      if (!(element instanceof Element) || budget.nodes >= MAX_DOMISH_TREE_NODES) return null;
      budget.nodes += 1;
      const row = {
        identity: domishNodeIdentity(element),
        locator: domishLocator(element),
        visible: isVisible(element),
        enabled: isEnabled(element),
        childCount: element.childElementCount,
        text: domishTextRecord(element, depth === 0 ? 2_400 : 700),
      };
      if (depth < MAX_DOMISH_TREE_DEPTH) {
        row.children = Array.from(element.children || []).slice(0, 18).map(child => visit(child, depth + 1)).filter(Boolean);
        row.childrenOmitted = Math.max(0, element.childElementCount - row.children.length);
      }
      return row;
    };
    return { root: visit(root, 0), nodesCaptured: budget.nodes, nodeLimit: MAX_DOMISH_TREE_NODES, depthLimit: MAX_DOMISH_TREE_DEPTH };
  }
  function domishTurnContext(element) {
    if (!(element instanceof Element)) return null;
    const turnSelector = '[data-message-author-role],[data-turn],[data-turn-key],[data-content-search-turn-key],[data-content-search-unit-key],[data-chatgpt-search-unit-key],article';
    const shell = element.closest(turnSelector) || element;
    const shellKeys = new Set([
      shell.getAttribute && shell.getAttribute('data-turn-id'),
      shell.getAttribute && shell.getAttribute('data-turn-key'),
      shell.getAttribute && shell.getAttribute('data-content-search-turn-key'),
      shell.getAttribute && shell.getAttribute('data-content-search-unit-key'),
      shell.getAttribute && shell.getAttribute('data-chatgpt-search-unit-key'),
    ].filter(Boolean));
    const turns = materializedTurns();
    const turn = turns.find(item => {
      if (item.element === shell || item.element === element || item.element.contains(element) || shell.contains(item.element)) return true;
      const keys = [item.id,
        item.element.getAttribute('data-turn-id'), item.element.getAttribute('data-turn-key'),
        item.element.getAttribute('data-content-search-turn-key'), item.element.getAttribute('data-content-search-unit-key'),
        item.element.getAttribute('data-chatgpt-search-unit-key')].filter(Boolean);
      return keys.some(key => shellKeys.has(key));
    });
    if (!turn) return null;
    const text = turnText(turn.element);
    return {
      id: turn.id,
      ordinal: turn.ordinal,
      role: turn.role,
      adapter: turn.adapter,
      chars: text.length,
      textHash: fnv1a64(text),
      head: trunc(normalizeCompactText(text), 600),
    };
  }
  function domishRootHost(element) {
    if (!(element instanceof Element)) return null;
    if (/^(?:button|a|input|textarea|select|option)$/i.test(element.tagName)) {
      return element.closest('[role="alert"],[data-testid*="error" i],[data-state="error"],[data-error],[data-turn-key],[data-content-search-turn-key],[data-chatgpt-search-unit-key],main') || element.parentElement || element;
    }
    return element.closest('[role="alert"],[data-testid*="error" i],[data-state="error"],[data-error],[data-turn-key],[data-content-search-turn-key],[data-chatgpt-search-unit-key]') || element;
  }
  function domishLowValueLiveRegion(element) {
    if (!(element instanceof Element)) return false;
    const id = element.id || '';
    const role = element.getAttribute('role') || '';
    const text = normalizeCompactText(element.textContent || '');
    const style = getComputedStyle(element);
    const clipped = style.clip !== 'auto' || style.clipPath !== 'none' || style.width === '1px' || style.height === '1px';
    return !text && ((/^DndLiveRegion-/i.test(id)) || (role === 'status' && clipped));
  }
  function domishTurnShell(element) {
    if (!(element instanceof Element)) return null;
    return element.closest('[data-message-author-role],[data-turn],[data-turn-key],[data-content-search-turn-key],[data-content-search-unit-key],[data-chatgpt-search-unit-key],article');
  }
  function domishVisibleCandidateRoots(primaryNodes = []) {
    const output = [];
    const add = (node, { primary = false } = {}) => {
      const host = domishRootHost(node);
      if (!(host instanceof Element) || (ui.host && ui.host.contains(host)) || output.includes(host)) return;
      if (!primary && domishLowValueLiveRegion(host)) return;
      output.push(host);
    };
    for (const node of primaryNodes || []) {
      add(node, { primary: true });
      const host = domishRootHost(node);
      const turn = domishTurnShell(host || node);
      if (turn && turn !== host) add(turn);
    }
    for (const node of uniqueElements(SELECTORS.errors, document).filter(isVisible).slice(-4)) add(node);
    for (const node of uniqueElements(SELECTORS.retry, document).filter(isVisible).slice(-4)) add(node);
    if (output.length < 2) {
      for (const node of uniqueElements(SELECTORS.system, document).filter(isVisible).slice(-8)) {
        const text = normalizeCompactText(node.textContent || '');
        if (/error|failed|retry|try again|loading|unavailable|problem|stale|reload/i.test(text)) add(node);
      }
    }
    if (!output.length) add(q('main') || document.body, { primary: true });
    return output.slice(0, MAX_DOMISH_ROOTS);
  }
  function domishShellSnapshot() {
    const composer = findComposer();
    const model = findModelButton();
    const send = findSendButton();
    const stop = findStopButton();
    const turns = materializedTurns();
    const visibleErrors = uniqueElements(SELECTORS.errors, document).filter(isVisible);
    const visibleRetry = uniqueElements(SELECTORS.retry, document).filter(isVisible);
    return {
      readyState: document.readyState,
      visibility: document.visibilityState,
      focused: document.hasFocus(),
      title: document.title,
      conversationId: conversationIdFromPath(),
      pathname: location.pathname,
      counts: {
        allElements: document.getElementsByTagName('*').length,
        main: qa('main').length,
        forms: qa('form').length,
        turns: turns.length,
        errors: visibleErrors.length,
        retryControls: visibleRetry.length,
        dialogs: uniqueElements(SELECTORS.dialogs, document).filter(isVisible).length,
        continuations: uniqueElements(SELECTORS.continue, document).filter(isVisible).length,
      },
      controls: {
        composer: composer ? { locator: domishLocator(composer), identity: domishNodeIdentity(composer) } : null,
        model: model ? { locator: domishLocator(model), identity: domishNodeIdentity(model), text: domishTextRecord(model, 600) } : null,
        send: send ? { locator: domishLocator(send), identity: domishNodeIdentity(send) } : null,
        stop: stop ? { locator: domishLocator(stop), identity: domishNodeIdentity(stop) } : null,
      },
      turnTail: turns.slice(-6).map(turn => ({ id: turn.id, ordinal: turn.ordinal, role: turn.role, adapter: turn.adapter, chars: (turn.text || turnText(turn.element)).length })),
    };
  }
  function domishRootRecord(element, label, index) {
    return {
      index,
      label,
      locator: domishLocator(element),
      identity: domishNodeIdentity(element),
      attributes: domishAttributeMap(element),
      visible: isVisible(element),
      enabled: isEnabled(element),
      presentation: domishPresentation(element),
      text: domishTextRecord(element),
      markup: domishMarkupRecord(element),
      ancestry: domishAncestry(element),
      siblings: domishSiblingSummary(element),
      turnContext: domishTurnContext(element),
      subtree: domishTreeRecord(element),
    };
  }
  function fitDomishSnapshot(snapshot) {
    let json = JSON.stringify(snapshot);
    if (utf8Bytes(json) > MAX_DOMISH_SNAPSHOT_UTF8_BYTES) {
      for (const root of snapshot.roots) root.subtree = { omitted: true, reason: 'snapshot-byte-budget' };
      snapshot.omissions.push('subtrees omitted to respect the per-snapshot byte budget');
      json = JSON.stringify(snapshot);
    }
    if (utf8Bytes(json) > MAX_DOMISH_SNAPSHOT_UTF8_BYTES) {
      for (const root of snapshot.roots) {
        root.markup.head = root.markup.head.slice(0, 2_000);
        root.markup.tail = root.markup.tail.slice(-2_000);
        root.text.head = root.text.head.slice(0, 1_000);
        root.text.tail = root.text.tail.slice(-1_000);
      }
      snapshot.omissions.push('root text and markup further reduced to respect the per-snapshot byte budget');
      json = JSON.stringify(snapshot);
    }
    if (utf8Bytes(json) > MAX_DOMISH_SNAPSHOT_UTF8_BYTES && snapshot.roots.length > 2) {
      snapshot.roots = snapshot.roots.slice(0, 2);
      snapshot.omissions.push('additional roots omitted to respect the per-snapshot byte budget');
      json = JSON.stringify(snapshot);
    }
    snapshot.utf8Bytes = utf8Bytes(JSON.stringify(snapshot));
    snapshot.complete = snapshot.utf8Bytes <= MAX_DOMISH_SNAPSHOT_UTF8_BYTES;
    if (!snapshot.complete) snapshot.omissions.push('snapshot remained above the declared per-snapshot byte budget');
    snapshot.utf8Bytes = utf8Bytes(JSON.stringify(snapshot));
    return snapshot;
  }
  function captureDomishEvent(kind, { reason = null, severity = 'warn', origin = 'runtime-edge', primaryNodes = [], context = null, relatedIds = [], key = null, force = false } = {}) {
    if (!document || !document.documentElement) return null;
    const roots = domishVisibleCandidateRoots(primaryNodes);
    const shell = domishShellSnapshot();
    const rootRecords = roots.map((element, index) => domishRootRecord(element, index === 0 ? 'primary' : 'related', index));
    const structuralKey = key || fnv1a64(JSON.stringify([
      conversationIdFromPath(), kind, reason, state.phase, shell.counts,
      rootRecords.map(root => [root.identity, root.text.hash, root.markup.hash]),
    ]));
    const previous = state.domForensics.snapshots[state.domForensics.snapshots.length - 1];
    const existing = !force && state.domForensics.snapshots.find(row => row && row.key === structuralKey);
    if (existing) {
      state.domForensics.deduplicated += 1;
      existing.repeatCount = Math.max(1, Number(existing.repeatCount) || 1) + 1;
      existing.lastSeenAt = nowIso();
      return existing.id;
    }
    const now = Date.now();
    const snapshot = fitDomishSnapshot({
      schema: 'qomrade.domish-event-snapshot.v1',
      id: `domish-${now.toString(36)}-${state.domForensics.captures + 1}`,
      key: structuralKey,
      at: new Date(now).toISOString(),
      t: now,
      trigger: {
        kind,
        reason,
        severity,
        origin,
        phase: state.phase,
        phaseReason: state.phaseReason,
        activeTransactionId: state.activeSend?.id || null,
        relatedIds: Array.isArray(relatedIds) ? relatedIds.slice(0, 16) : [],
      },
      shell,
      roots: rootRecords,
      context: boundedEventDetail(context),
      omissions: [],
      coverage: 'bounded visible DOM captured synchronously on an existing controller/event edge; no MutationObserver, network interception, or full-page archive',
      authority: 'forensic evidence only; never click, Send, reload, or model authority',
    });
    state.domForensics.captures += 1;
    state.domForensics.lastCaptureAt = snapshot.at;
    state.domForensics.lastKey = structuralKey;
    state.domForensics.snapshots.push(snapshot);
    while (state.domForensics.snapshots.length > MAX_DOMISH_SNAPSHOTS) {
      state.domForensics.snapshots.shift();
      state.domForensics.dropped += 1;
    }
    state.domForensics.totalUtf8Bytes = state.domForensics.snapshots.reduce((sum, row) => sum + (Number(row.utf8Bytes) || utf8Bytes(JSON.stringify(row))), 0);
    while (state.domForensics.totalUtf8Bytes > MAX_DOMISH_TOTAL_UTF8_BYTES && state.domForensics.snapshots.length > 1) {
      state.domForensics.snapshots.shift();
      state.domForensics.dropped += 1;
      state.domForensics.totalUtf8Bytes = state.domForensics.snapshots.reduce((sum, row) => sum + (Number(row.utf8Bytes) || utf8Bytes(JSON.stringify(row))), 0);
    }
    logEvent('domish-snapshot-captured', `Captured bounded DOMish evidence for ${kind}.`, { snapshotId: snapshot.id, key: structuralKey, reason, severity, rootCount: snapshot.roots.length, utf8Bytes: snapshot.utf8Bytes });
    return snapshot.id;
  }
  function domForensicsSummary({ includeSnapshots = true } = {}) {
    return {
      schema: state.domForensics.schema,
      captures: state.domForensics.captures,
      deduplicated: state.domForensics.deduplicated,
      dropped: state.domForensics.dropped,
      restoredAcrossRefresh: state.domForensics.restoredAcrossRefresh,
      totalUtf8Bytes: state.domForensics.totalUtf8Bytes,
      lastCaptureAt: state.domForensics.lastCaptureAt,
      lastKey: state.domForensics.lastKey,
      snapshotCount: state.domForensics.snapshots.length,
      limits: {
        snapshots: MAX_DOMISH_SNAPSHOTS,
        totalUtf8Bytes: MAX_DOMISH_TOTAL_UTF8_BYTES,
        perSnapshotUtf8Bytes: MAX_DOMISH_SNAPSHOT_UTF8_BYTES,
        persistenceUtf8Bytes: MAX_DOMISH_PERSIST_UTF8_BYTES,
      },
      snapshots: includeSnapshots ? state.domForensics.snapshots.map(row => JSON.parse(JSON.stringify(row))) : undefined,
      authority: 'forensic evidence only',
    };
  }
  function domForensicsPersistentSnapshot() {
    const base = domForensicsSummary({ includeSnapshots: false });
    base.snapshots = [];
    let used = utf8Bytes(JSON.stringify(base));
    for (const snapshot of state.domForensics.snapshots.slice().reverse()) {
      const bytes = Number(snapshot.utf8Bytes) || utf8Bytes(JSON.stringify(snapshot));
      if (base.snapshots.length && used + bytes > MAX_DOMISH_PERSIST_UTF8_BYTES) break;
      if (used + bytes > MAX_DOMISH_PERSIST_UTF8_BYTES) continue;
      base.snapshots.unshift(JSON.parse(JSON.stringify(snapshot)));
      used += bytes;
    }
    base.persistenceComplete = base.snapshots.length === state.domForensics.snapshots.length;
    base.persistenceOmission = base.persistenceComplete ? null : 'Only the newest bounded DOMish snapshots fit in the safe-refresh ticket.';
    base.persistenceUtf8Bytes = utf8Bytes(JSON.stringify(base));
    return base;
  }
  function restoreDomForensics(snapshot) {
    if (!snapshot || snapshot.schema !== 'qomrade.domish-event-buffer.v1' || !Array.isArray(snapshot.snapshots)) return false;
    state.domForensics = {
      schema: 'qomrade.domish-event-buffer.v1',
      captures: Math.max(Number(snapshot.captures) || 0, snapshot.snapshots.length),
      deduplicated: Number(snapshot.deduplicated) || 0,
      dropped: Number(snapshot.dropped) || 0,
      restoredAcrossRefresh: true,
      totalUtf8Bytes: 0,
      lastCaptureAt: snapshot.lastCaptureAt || null,
      lastKey: snapshot.lastKey || null,
      snapshots: snapshot.snapshots.slice(-MAX_DOMISH_SNAPSHOTS).map(row => JSON.parse(JSON.stringify(row))),
    };
    state.domForensics.totalUtf8Bytes = state.domForensics.snapshots.reduce((sum, row) => sum + (Number(row.utf8Bytes) || utf8Bytes(JSON.stringify(row))), 0);
    if (snapshot.persistenceComplete === false) state.domForensics.dropped += 1;
    logEvent('domish-snapshots-restored', 'Restored bounded DOMish event evidence from the exact safe-refresh ticket.', { snapshots: state.domForensics.snapshots.length, persistenceComplete: snapshot.persistenceComplete !== false });
    return true;
  }
  function domForensicsContinuitySummary() {
    const latest = state.domForensics.snapshots[state.domForensics.snapshots.length - 1] || null;
    return {
      schema: 'qomrade.domish-event-continuity.v1',
      captures: state.domForensics.captures,
      snapshotCount: state.domForensics.snapshots.length,
      lastCaptureAt: state.domForensics.lastCaptureAt,
      lastKey: state.domForensics.lastKey,
      latest: latest ? {
        id: latest.id,
        key: latest.key,
        at: latest.at,
        trigger: latest.trigger,
        shell: latest.shell,
        roots: latest.roots.slice(0, 1).map(root => ({ locator: root.locator, identity: root.identity, text: { chars: root.text.chars, hash: root.text.hash, head: trunc(root.text.head, 1_200) }, markup: { chars: root.markup.chars, hash: root.markup.hash, head: trunc(root.markup.head, 2_000) } })),
      } : null,
      authority: 'evidence-only-never-resume-control',
    };
  }
  function selectorRoute(element, selectors) {
    if (!element) return { matched: false, index: null, selector: null, fallback: false };
    for (let index = 0; index < selectors.length; index += 1) {
      try {
        if (element.matches(selectors[index])) return { matched: true, index, selector: selectors[index], fallback: false };
      } catch (_) {}
    }
    return { matched: true, index: null, selector: null, fallback: true };
  }
  function summarizeControl(element, index = 0) {
    if (!element) return null;
    const href = element instanceof HTMLAnchorElement ? element.href || '' : '';
    const download = element instanceof HTMLAnchorElement ? element.download || '' : '';
    return {
      index,
      tag: element.tagName.toLowerCase(),
      text: trunc(normalizeCompactText(element.textContent || ''), 500),
      ariaLabel: element.getAttribute('aria-label'),
      testId: element.getAttribute('data-testid'),
      role: element.getAttribute('role'),
      href: trunc(href, 1_000) || null,
      download: trunc(download, 500) || null,
      visible: isVisible(element),
      enabled: isEnabled(element),
      html: trunc(element.outerHTML || '', 2_000),
    };
  }
  function safeProbe(name, fn, failures, fallback = null) {
    try {
      return fn();
    } catch (error) {
      if (Array.isArray(failures) && failures.length < MAX_PROBE_FAILURES) {
        failures.push({ name, at: nowIso(), message: String(error && error.message || error), stack: trunc(error && error.stack, 2_000) });
      }
      return fallback;
    }
  }
  function selectorFamilyProbe(name, selectors, chosen = null) {
    const candidates = selectors.map((selector, index) => {
      let nodes = [];
      let error = null;
      state.metrics.selectorQueries += 1;
      try { nodes = Array.from(document.querySelectorAll(selector)); }
      catch (caught) { error = String(caught && caught.message || caught); }
      return {
        index,
        selector,
        count: nodes.length,
        visibleCount: nodes.filter(isVisible).length,
        enabledVisibleCount: nodes.filter(node => isVisible(node) && isEnabled(node)).length,
        error,
        first: nodes.length ? elementSummary(nodes[0], { redactContent: name === 'composer' }) : null,
      };
    });
    return {
      name,
      chosen: elementSummary(chosen, { redactContent: name === 'composer' }),
      route: selectorRoute(chosen, selectors),
      candidates,
    };
  }
  function historyObservation() {
    const elements = uniqueElements(SELECTORS.history, document);
    return {
      schema: 'qomrade.history-observation.v2',
      mode: 'full',
      present: elements.length > 0,
      count: elements.length,
      visibleCount: elements.filter(isVisible).length,
      records: elements.slice(0, 40).map((element, index) => ({
        index,
        href: element instanceof HTMLAnchorElement ? trunc(element.href || '', 1_000) : null,
        text: trunc(normalizeCompactText(element.textContent || ''), 300),
        visible: isVisible(element),
        testId: element.getAttribute('data-testid'),
        conversationKey: element.getAttribute('data-sidebar-chatgpt-conversation-key'),
      })),
    };
  }
  function historyPresenceObservation() {
    const selector = SELECTORS.history.join(',');
    state.metrics.selectorQueries += 1;
    let element = null;
    let error = null;
    try { element = document.querySelector(selector); }
    catch (caught) { error = String(caught && caught.message || caught); }
    return {
      schema: 'qomrade.history-observation.v2',
      mode: 'presence-only',
      present: !!element,
      count: null,
      visibleCount: null,
      records: [],
      selector,
      error,
      first: element ? { tag: element.tagName.toLowerCase(), testId: element.getAttribute('data-testid'), conversationKey: element.getAttribute('data-sidebar-chatgpt-conversation-key') } : null,
    };
  }
  function surfaceAuthenticityObservation({ detail = true } = {}) {
    if (detail) state.metrics.authenticityFullProbes += 1;
    else state.metrics.authenticityLightProbes += 1;
    const model = currentModelObservation();
    const history = detail ? historyObservation() : historyPresenceObservation();
    const turns = detail ? materializedTurns() : [];
    const label = normalizeCompactText(model.label || '');
    const falseModel53 = model.family === 5.3 || /(?:^|\D)5\.3(?:\D|$)/.test(label);
    const noHistory = history.present === false;
    const hard = noHistory && falseModel53;
    const evidenceBearing = detail && (turns.length > 0 || history.present);
    return {
      schema: 'qomrade.surface-authenticity.v3',
      at: nowIso(),
      probeMode: detail ? 'full' : 'hard-signature-only',
      pathname: location.pathname,
      href: location.href,
      referrer: detail ? document.referrer || '' : null,
      readyState: document.readyState,
      visibility: document.visibilityState,
      focused: document.hasFocus(),
      composerPresent: detail ? !!findComposer() : null,
      model: { ok: model.ok, reason: model.reason, label: model.label, family: model.family, hasPro: model.hasPro },
      history,
      turnCount: detail ? turns.length : null,
      noHistory,
      falseModel53,
      hard,
      verdict: hard ? 'hard-false-gui' : evidenceBearing ? 'evidence-bearing' : detail ? 'unknown-or-settling' : 'no-hard-false-signature',
      reason: hard ? 'operator-defined no-history plus 5.3 signature' : evidenceBearing ? 'history-or-conversation-evidence-present' : detail ? 'insufficient positive provenance' : 'light probe found no hard signature; positive provenance was intentionally not inventoried',
      authority: hard ? 'quarantine-before-chatgpt-effects' : 'evidence-only',
    };
  }
  function stylesheetHealthObservation() {
    const sheets = Array.from(document.styleSheets || []);
    const links = Array.from(document.querySelectorAll('link[rel~="stylesheet" i]'));
    let enabledSheets = 0;
    let disabledSheets = 0;
    let readableSheets = 0;
    let unreadableSheets = 0;
    for (const sheet of sheets) {
      if (sheet.disabled) { disabledSheets += 1; continue; }
      enabledSheets += 1;
      try { void sheet.cssRules; readableSheets += 1; }
      catch (_) { unreadableSheets += 1; }
    }
    const loadedLinks = links.filter(link => {
      try { return !!link.sheet; } catch (_) { return false; }
    }).length;
    const pendingLinks = links.filter(link => {
      try { return !link.sheet; } catch (_) { return true; }
    }).slice(0, 12).map(link => ({ href: trunc(link.href || link.getAttribute('href') || '', 500), media: trunc(link.media || '', 120), disabled: !!link.disabled }));
    return {
      schema: 'qomrade.stylesheet-health.v1',
      sheetCount: sheets.length,
      enabledSheets,
      disabledSheets,
      readableSheets,
      unreadableSheets,
      linkCount: links.length,
      loadedLinks,
      pendingLinks,
      likelyUnavailable: enabledSheets === 0 || (links.length > 0 && loadedLinks === 0),
      authority: 'surface evidence only; browser page-style settings, failed fetches, CSP, and application hydration are not distinguished',
    };
  }
  function pageShellLoadingProfileNode() {
    const candidates = uniqueElements(['[role="status"]','[aria-live="polite"]','[aria-live="assertive"]','[data-testid*="status" i]'], document);
    return candidates.find(node => isStructurallyRendered(node) && /\bloading profile\b/i.test(normalizeCompactText(node.textContent || ''))) || null;
  }
  function pageShellFallbackComposer() {
    return findComposer() || document.querySelector('textarea[placeholder*="ChatGPT" i],textarea[aria-label*="ChatGPT" i],[contenteditable="true"][aria-label*="ChatGPT" i]');
  }
  function pageShellHealthObservation({ detail = true } = {}) {
    const observedT = Date.now();
    const ageMs = Math.max(0, observedT - Number(state.boot.startedT || observedT));
    const readyState = document.readyState;
    const ageSettled = ageMs >= SHELL_HEALTH_BOOT_PROBE_MS;
    const composer = pageShellFallbackComposer();
    const modelControl = findModelButton();
    const loadFailure = (!composer || !modelControl) ? visibleConversationLoadFailureMaintenance() : null;
    const explicitLoadFailure = !!(loadFailure && ageSettled);
    const settled = (readyState === 'complete' && ageSettled) || explicitLoadFailure;
    // The healthy fast path avoids a stylesheet/control inventory on ordinary ticks.
    if (composer && modelControl && !loadFailure) {
      return {
        schema: 'qomrade.page-shell-health-observation.v1', at: new Date(observedT).toISOString(), t: observedT,
        degraded: false, kind: null, reason: 'composer and model control are present', key: null,
        settled, readyState, ageMs, composerPresent: true, modelControlPresent: true,
        materializedTurns: detail ? materializedTurns().length : null,
        authority: 'observation only',
      };
    }
    const turns = detail ? materializedTurns() : [];
    const loadingProfile = pageShellLoadingProfileNode();
    const styleHealth = stylesheetHealthObservation();
    const bodyStyle = document.body ? getComputedStyle(document.body) : null;
    const bodyFontFamily = normalizeCompactText(bodyStyle?.fontFamily || '');
    const bodyLooksDefaultSerif = /(?:times|serif)/i.test(bodyFontFamily) && !/(?:system-ui|inter|arial|helvetica|sans-serif)/i.test(bodyFontFamily);
    const viewport = { width: window.innerWidth || 0, height: window.innerHeight || 0 };
    let composerRect = null;
    try {
      const rect = composer && composer.getBoundingClientRect ? composer.getBoundingClientRect() : null;
      if (rect) composerRect = { x: Math.round(rect.x), y: Math.round(rect.y), width: Math.round(rect.width), height: Math.round(rect.height) };
    } catch (_) {}
    const tinyDesktopComposer = !!(composerRect && viewport.width >= 900 && composerRect.width > 0 && composerRect.width <= 360 && composerRect.height > 0 && composerRect.height <= 180);
    const controls = Array.from(document.querySelectorAll('button,input,textarea,select')).filter(isStructurallyRendered).slice(0, 32);
    const nativeLike = controls.filter(control => {
      try {
        const css = getComputedStyle(control);
        const radius = parseFloat(css.borderTopLeftRadius || '0') || 0;
        const appearance = String(css.appearance || css.webkitAppearance || '').toLowerCase();
        const compact = control.getBoundingClientRect ? control.getBoundingClientRect() : null;
        return radius <= 4 && (!appearance || appearance === 'auto' || appearance === 'button' || appearance === 'textfield')
          && (!compact || compact.width < 420);
      } catch (_) { return false; }
    });
    const mainPresent = !!document.querySelector('main');
    const turnCount = turns.length;
    const stylesheetUnavailable = !!styleHealth.likelyUnavailable;
    const defaultNativeScene = bodyLooksDefaultSerif && tinyDesktopComposer && nativeLike.length >= 4;
    const unstyled = settled && !explicitLoadFailure && !modelControl && (stylesheetUnavailable || defaultNativeScene)
      && (!!loadingProfile || !mainPresent || turnCount === 0);
    const hydrationStalled = settled && ageMs >= SHELL_HEALTH_HYDRATION_MIN_MS && !explicitLoadFailure && !unstyled && !modelControl
      && !!loadingProfile && (turnCount === 0 || !mainPresent);
    const degraded = !!(explicitLoadFailure || unstyled || hydrationStalled);
    const kind = explicitLoadFailure ? 'conversation-load-failed'
      : unstyled ? 'chatgpt-shell-unstyled' : hydrationStalled ? 'chatgpt-shell-hydration-stalled' : null;
    const reason = kind === 'conversation-load-failed'
      ? 'ChatGPT reports that it could not load this conversation.'
      : kind === 'chatgpt-shell-unstyled'
        ? 'ChatGPT author styles appear unavailable or unapplied; the top document resembles native browser controls.'
        : kind === 'chatgpt-shell-hydration-stalled'
          ? 'ChatGPT remained on a partial Loading profile shell without its model surface.'
          : !settled ? 'ChatGPT shell is still inside the bounded boot-settlement window.'
            : 'The incomplete surface does not meet the high-confidence degraded-shell threshold.';
    const key = degraded ? fnv1a64(JSON.stringify([conversationIdFromPath(), kind])) : null;
    const loadFailurePublic = loadFailure ? { ...loadFailure } : null;
    if (loadFailurePublic) delete loadFailurePublic._primaryNodes;
    const primaryNodes = [
      ...(loadFailure?._primaryNodes || []),
      loadingProfile,
      composer && (composer.closest('form') || composer.parentElement || composer),
      controls[0] && (controls[0].parentElement || controls[0]),
      document.querySelector('nav') || document.querySelector('header'),
    ].filter(Boolean);
    return {
      schema: 'qomrade.page-shell-health-observation.v1', at: new Date(observedT).toISOString(), t: observedT,
      degraded, kind, reason, key, settled, readyState, ageMs,
      visibility: document.visibilityState, focused: document.hasFocus(),
      composerPresent: !!composer, modelControlPresent: !!modelControl, materializedTurns: turnCount, mainPresent,
      conversationLoadFailure: loadFailurePublic,
      loadingProfile: loadingProfile ? { text: trunc(normalizeCompactText(loadingProfile.textContent || ''), 240), element: elementSummary(loadingProfile, { includePresentation: true }) } : null,
      stylesheetHealth: styleHealth,
      presentation: { bodyFontFamily, bodyLooksDefaultSerif, viewport, composerRect, tinyDesktopComposer, nativeLikeControls: nativeLike.length, sampledControls: controls.length },
      scores: { conversationLoadFailure: explicitLoadFailure, stylesheetUnavailable, defaultNativeScene, unstyled, hydrationStalled },
      _primaryNodes: primaryNodes,
      authority: degraded ? 'maintenance evidence only; never Send, Retry, or backend-state authority' : 'observation only',
    };
  }
  function publicPageShellHealthObservation(observation) {
    if (!observation) return null;
    const copy = { ...observation };
    delete copy._primaryNodes;
    return copy;
  }
  function shellHealthSurface(observation) {
    if (!observation?.degraded) return null;
    const publicObservation = publicPageShellHealthObservation(observation);
    return {
      key: observation.key,
      reason: observation.kind,
      maintenanceKind: observation.kind,
      allowActiveSend: true,
      domSnapshotId: state.shellHealth.current?.domSnapshotId || null,
      evidence: { shellHealth: publicObservation, domSnapshotId: state.shellHealth.current?.domSnapshotId || null },
    };
  }
  function shellHealthSummary({ includeIncidents = true } = {}) {
    return {
      schema: state.shellHealth.schema,
      current: state.shellHealth.current ? JSON.parse(JSON.stringify(state.shellHealth.current)) : null,
      lastObservation: state.shellHealth.lastObservation ? JSON.parse(JSON.stringify(state.shellHealth.lastObservation)) : null,
      incidents: includeIncidents ? state.shellHealth.incidents.slice(-MAX_SHELL_HEALTH_INCIDENTS).map(row => JSON.parse(JSON.stringify(row))) : undefined,
      lastKey: state.shellHealth.lastKey,
      recoveredAt: state.shellHealth.recoveredAt,
      bootProbeAt: state.shellHealth.bootProbeAt,
      authority: 'high-confidence page-shell maintenance evidence only',
    };
  }
  function observePageShellHealth(origin = 'controller-observation', { capture = true } = {}) {
    const observation = pageShellHealthObservation({ detail: true });
    const publicObservation = publicPageShellHealthObservation(observation);
    const priorKey = state.shellHealth.current?.key || null;
    let shouldRender = false;
    state.shellHealth.lastObservation = publicObservation;
    if (observation.degraded) {
      const existing = state.shellHealth.current;
      let domSnapshotId = existing?.key === observation.key ? existing.domSnapshotId || null : null;
      if (!existing || existing.key !== observation.key) {
        if (capture) {
          domSnapshotId = captureDomishEvent('page-shell-degraded', {
            reason: observation.reason,
            severity: 'error',
            origin,
            primaryNodes: observation._primaryNodes || [],
            relatedIds: [observation.key],
            key: fnv1a64(`page-shell-degraded|${observation.key}`),
            force: true,
            context: { shellHealth: publicObservation },
          });
        }
        const incident = { id: `shell-${Date.now().toString(36)}`, key: observation.key, kind: observation.kind, firstObservedAt: observation.at, lastObservedAt: observation.at, observations: 1, origin, domSnapshotId, evidence: publicObservation };
        state.shellHealth.incidents.push(incident);
        if (state.shellHealth.incidents.length > MAX_SHELL_HEALTH_INCIDENTS) state.shellHealth.incidents.splice(0, state.shellHealth.incidents.length - MAX_SHELL_HEALTH_INCIDENTS);
        logEvent('page-shell-degraded', observation.reason, { key: observation.key, kind: observation.kind, origin, domSnapshotId, evidence: publicObservation });
        shouldRender = true;
      } else {
        const incident = state.shellHealth.incidents.slice().reverse().find(row => row.key === observation.key);
        if (incident) { incident.lastObservedAt = observation.at; incident.observations = Number(incident.observations || 0) + 1; }
      }
      state.shellHealth.current = { ...publicObservation, domSnapshotId };
      state.shellHealth.lastKey = observation.key;
      if (!state.running && !state.quarantine && !state.terminalStop) {
        if (state.phase !== 'SURFACE_HOLD' || state.phaseReason !== `${observation.reason} qomrade will not Send into this surface.`) shouldRender = true;
        state.phase = 'SURFACE_HOLD';
        state.phaseReason = `${observation.reason} qomrade will not Send into this surface.`;
      }
    } else if (state.shellHealth.current) {
      const prior = state.shellHealth.current;
      state.shellHealth.current = null;
      state.shellHealth.recoveredAt = observation.at;
      shouldRender = true;
      logEvent('page-shell-recovered', 'The ChatGPT composer and model shell are available again.', { origin, priorKey: prior.key, priorKind: prior.kind });
      if (state.autoRefresh.healingPending?.key === prior.key) cancelHealingRefresh('degraded-page-shell-recovered');
      if (!state.running && state.phase === 'SURFACE_HOLD' && !state.terminalStop) {
        state.phase = 'STOPPED';
        state.phaseReason = 'fresh start';
      }
    }
    if (shouldRender || priorKey !== (state.shellHealth.current?.key || null)) render();
    return observation;
  }
  function normalizeConversationTerminalText(value) {
    return normalizeCompactText(String(value || ''))
      .replace(/[’]/g, "'")
      .replace(/\s*(?:retry|try again)\s*$/i, '')
      .trim()
      .toLowerCase();
  }
  function conversationTerminalMatch(value) {
    const normalized = normalizeConversationTerminalText(value);
    if (!normalized) return null;
    for (const row of CONVERSATION_TERMINAL_TEXTS) {
      const expected = normalizeConversationTerminalText(row.text);
      if (normalized === expected) return { kind: row.kind, text: row.text, normalized };
    }
    if (/^(?:the|this) conversation is too long[,.]?\s+please start a new (?:one|chat)\.?$/.test(normalized)) {
      return { kind: 'conversation-too-long', text: CURRENT_CONVERSATION_TOO_LONG_TEXT, normalized };
    }
    return null;
  }
  function conversationBarrierObservation({ includeProse = true } = {}) {
    const candidates = [];
    // A terminal conversation barrier can only govern the current tail.
    // While generation is explicitly advertised, structural alerts remain
    // globally authoritative and prose fallback is deferred to avoid repeatedly
    // allocating the growing assistant answer on every background poll.
    if (includeProse) {
      for (const turn of materializedTurns().filter(row => row.role === 'assistant').slice(-4)) {
        const text = normalizeCompactText(turnText(turn.element));
        const match = conversationTerminalMatch(text);
        if (match) {
          const owner = faultOwner(turn.element);
          candidates.push({ id: turn.id, ordinal: turn.ordinal, adapter: turn.adapter, terminalKind: match.kind,
            text: trunc(text, 1_000), cleanText: match.text, owner, element: elementSummary(turn.element) });
        }
      }
    } else state.metrics.barrierProseScansSuppressedWhileGenerating += 1;
    for (const node of uniqueElements(SELECTORS.errors, document).filter(isVisible)) {
      const text = normalizeCompactText(node.textContent || '');
      const match = conversationTerminalMatch(text);
      if (match) {
        candidates.push({ id: null, ordinal: null, adapter: 'structural-error-node', terminalKind: match.kind,
          text: trunc(text, 1_000), cleanText: match.text, owner: faultOwner(node), element: elementSummary(node, { includePresentation: true }) });
      }
    }
    return {
      schema: 'qomrade.conversation-barrier-snapshot.v3',
      at: nowIso(),
      present: candidates.length > 0,
      current: candidates.length ? candidates[candidates.length - 1] : null,
      candidates,
      authority: candidates.length ? 'terminal-current-conversation-no-more-turns' : 'none',
    };
  }
  function terminalRequestStage(current = null) {
    const active = state.activeSend;
    const composer = findComposer();
    const realUserTurn = !!(active?.userAdoptedAt && stableRequestId(active.userTurnId));
    const observedOwner = current?.owner || null;
    const latestUser = realUserTurn ? materializedTurns().filter(turn => turn.role === 'user').at(-1) || null : null;
    const inferredFromAcceptedRequest = !!(active && realUserTurn && latestUser?.id === active.userTurnId && !observedOwner?.userId);
    const owner = inferredFromAcceptedRequest ? {
      userId: active.userTurnId, stable: true, isLatestUser: true, belongsToActive: true,
      method: 'active-request-terminal-after-adoption', requestGroupKey: active.userTurnId,
    } : observedOwner;
    const ownerBelongsToActive = !!(owner && active && realUserTurn && (owner.belongsToActive || owner.userId === active.userTurnId
      || owner.requestGroupKey === active.userTurnId || (active.userTurnAliases || []).includes(owner.userId)));
    return {
      schema: 'qomrade.terminal-request-stage.v1', activeTransactionId: active?.id || null,
      sendActivated: !!active?.clickedAt, clickedAt: active?.clickedAt || null,
      userTurnMaterialized: realUserTurn, userTurnId: realUserTurn ? active.userTurnId : null,
      userTurnOrdinal: realUserTurn && active.userTurnOrdinal != null ? active.userTurnOrdinal : null,
      userAdoptedAt: realUserTurn ? active.userAdoptedAt : null,
      assistantTurnMaterialized: !!active?.assistantTurnId, assistantTurnId: active?.assistantTurnId || null,
      composerPresent: !!composer, composerEmpty: composer ? composerIsEmpty(composer) : null,
      barrierOwner: owner ? { userId: owner.userId || null, stable: !!owner.stable, isLatestUser: !!owner.isLatestUser,
        belongsToActive: ownerBelongsToActive, method: owner.method || null, requestGroupKey: owner.requestGroupKey || null } : null,
      interpretation: realUserTurn
        ? 'The exact prompt became a real user turn before ChatGPT returned the terminal barrier; an empty composer is expected after Send.'
        : active?.clickedAt
          ? 'Send was activated, but no stable matching user turn was observed before ChatGPT returned the terminal barrier.'
          : 'The terminal barrier was observed without an active qomrade Send.',
    };
  }
  function compactConversationTerminal(barrier, source) {
    const current = barrier?.current || null;
    return {
      schema: 'qomrade.session-terminal.v1', at: nowIso(), kind: 'conversation-complete', source,
      terminalKind: current?.terminalKind || 'conversation-terminal', text: current?.cleanText || current?.text || null,
      observedText: current?.text || null, adapter: current?.adapter || null, turnId: current?.id || null,
      turnOrdinal: current?.ordinal == null ? null : current.ordinal, requestStage: terminalRequestStage(current),
      action: 'stop-no-more-turns', nativeRetry: false, automaticReload: false, freshPrompt: false,
      barrierSchema: barrier?.schema || null,
    };
  }
  function stopForConversationTerminal(barrier, source = 'runtime') {
    if (state.activeSend && !state.activeSend.outcome) captureActiveSendAdoption();
    const observed = barrier?.present ? barrier : conversationBarrierObservation();
    if (!observed?.present) return false;
    const terminal = compactConversationTerminal(observed, source);
    const stage = terminal.requestStage;
    const reason = stage.userTurnMaterialized
      ? 'Conversation complete — qomrade sent a real user turn; ChatGPT accepted it into the context river, then returned the max-length barrier before an assistant reply. The empty composer is expected after Send. qomrade stopped and will send no more turns.'
      : stage.sendActivated
        ? 'Conversation complete — qomrade activated Send, but no stable matching user turn materialized before ChatGPT returned the max-length barrier. qomrade stopped and will send no more turns.'
        : 'Conversation complete — ChatGPT says this conversation is too long. qomrade stopped and will send no more turns.';
    stopRun(reason, { terminal });
    return true;
  }
  function workEvidenceObservation({ scope = 'all' } = {}) {
    const allTurns = materializedTurns();
    let selected = allTurns;
    if (scope === 'active-response') {
      const userIndex = state.activeSend
        ? allTurns.findIndex(turn => turn.role === 'user' && turn.id === state.activeSend.userTurnId)
        : -1;
      selected = userIndex >= 0 ? allTurns.slice(userIndex + 1) : allTurns.slice(-20);
    } else if (scope === 'active') {
      const floor = state.activeSend && Number.isFinite(state.activeSend.preMaxOrdinal) ? state.activeSend.preMaxOrdinal - 1 : null;
      selected = floor == null
        ? allTurns.slice(-20)
        : allTurns.filter(turn => turn.ordinal == null || turn.ordinal >= floor);
    } else if (scope === 'recent') selected = allTurns.slice(-24);
    const selectedSet = new Set(selected.map(turn => turn.element));
    const records = [];
    const unresolved = [];
    const overlap = [];
    for (let index = 0; index < allTurns.length; index += 1) {
      const turn = allTurns[index];
      if (!selectedSet.has(turn.element) || turn.role !== 'assistant') continue;
      const workMarkers = uniqueElements(SELECTORS.work.slice(0, 4), turn.element);
      if (!workMarkers.length) continue;
      const finalMarkers = uniqueElements(SELECTORS.finalAnswer, turn.element);
      const text = turnText(turn.element);
      const finalEvidence = finalMarkers.length > 0 && !!text;
      const record = {
        index,
        id: turn.id,
        ordinal: turn.ordinal,
        adapter: turn.adapter,
        workMarkerCount: workMarkers.length,
        finalMarkerCount: finalMarkers.length,
        finalAnswerEvidence: finalEvidence,
        textChars: text.length,
        textHash: fnv1a32(text.length > 80_000 ? text.slice(0, 40_000) + text.slice(-40_000) : text),
        workMarkers: workMarkers.slice(0, 12).map(node => elementSummary(node)),
      };
      records.push(record);
      if (!finalEvidence) {
        const laterUsers = allTurns.slice(index + 1).filter(candidate => candidate.role === 'user').map(candidate => ({ id: candidate.id, ordinal: candidate.ordinal, textHash: fnv1a32(turnText(candidate.element)) }));
        const unresolvedRecord = { ...record, laterUsers };
        unresolved.push(unresolvedRecord);
        if (laterUsers.length) overlap.push(unresolvedRecord);
      }
    }
    return {
      schema: 'qomrade.work-evidence.v5',
      signature: fnv1a64(JSON.stringify(records.map(row => [row.id, row.workMarkerCount, row.finalMarkerCount, row.textHash]))),
      at: nowIso(),
      scope,
      totalMaterializedTurnCount: allTurns.length,
      scannedTurnCount: selected.length,
      records,
      unresolved,
      latestUnresolved: unresolved.length ? unresolved[unresolved.length - 1] : null,
      overlap,
      overlapHazard: overlap.length > 0,
      blocking: unresolved.length > 0,
      authority: overlap.length ? 'halt-possible-overlap' : unresolved.length ? 'hold-existing-work' : 'none',
    };
  }
  function visibleDialogObservation() {
    const dialogs = uniqueElements(SELECTORS.dialogs, document)
      .filter(element => isVisible(element) && !(ui.host && ui.host.contains(element)))
      .slice(0, 30);
    return {
      schema: 'qomrade.dialog-observation.v1',
      at: nowIso(),
      count: dialogs.length,
      blocking: dialogs.length > 0,
      dialogs: dialogs.map((element, index) => ({ index, ...elementSummary(element, { includePresentation: true }) })),
      authority: dialogs.length ? 'observe-and-block-send-never-dismiss' : 'none',
    };
  }
  function continuationObservation(assistant = latestAssistantTurn()) {
    const candidates = [];
    const add = element => { if (element && !candidates.includes(element)) candidates.push(element); };
    const scopes = assistant && assistant.element ? [assistant.element, document] : [document];
    for (const scope of scopes) {
      for (const element of uniqueElements(SELECTORS.continue, scope)) add(element);
      for (const element of qa('button,a', scope)) {
        const text = normalizeCompactText(`${element.textContent || ''} ${element.getAttribute('aria-label') || ''} ${element.getAttribute('data-testid') || ''}`);
        if (/\b(?:continue generating|keep generating|continue response)\b/i.test(text)) add(element);
      }
    }
    const controls = candidates.filter(isVisible).slice(0, 30);
    return {
      schema: 'qomrade.continuation-observation.v2',
      at: nowIso(),
      available: controls.length > 0,
      assistantId: assistant ? assistant.id : null,
      scopeCoverage: assistant && assistant.element ? 'latest-assistant-plus-document' : 'document',
      controls: controls.map(element => ({
        ...summarizeControl(element),
        insideLatestAssistant: !!(assistant && assistant.element && assistant.element.contains(element)),
      })),
      authority: 'observe-and-hold-never-click',
    };
  }
  function retryControlContext(element, assistant = latestAssistantTurn()) {
    if (!element) return null;
    const retryLabel = normalizeCompactText(`${element.textContent || ''} ${element.getAttribute('aria-label') || ''} ${element.getAttribute('data-testid') || ''}`);
    const errorSelector = SELECTORS.errors.join(',');
    let host = null;
    try { host = element.closest(errorSelector); } catch (_) { host = null; }
    const actionableHost = node => !!(node && typeof node.matches === 'function' && node.matches('button,a,[role="button"],input,select,textarea'));
    if (host) {
      const initial = boundedFaultLabel(host);
      if (host === element || actionableHost(host) || !initial.text || initial.text === retryLabel) host = null;
    }
    let depth = 0;
    if (!host) {
      for (let node = element.parentElement; node && node !== document.body && depth < 10; node = node.parentElement, depth += 1) {
        if (actionableHost(node)) continue;
        const label = boundedFaultLabel(node);
        const typed = classifyPipelineFailureText(label.text);
        const maintenance = classifyPipelineMaintenanceText(label.text);
        const usefulText = label.text && label.text !== retryLabel && label.text.length <= 640;
        if (typed || maintenance || (usefulText && (label.complete || label.text.length <= 320))) { host = node; break; }
      }
    }
    if (!host) return null;
    const label = boundedFaultLabel(host);
    const typed = classifyPipelineFailureText(label.text);
    const maintenance = classifyPipelineMaintenanceText(label.text);
    const turn = host.closest('[data-message-author-role],[data-turn],[data-content-search-unit-key],[data-chatgpt-search-unit-key],article');
    const contextText = trunc(label.text || '', 640);
    return {
      text: contextText,
      textHash: contextText ? fnv1a64(contextText) : null,
      typed: typed ? { kind: typed.kind, faultKind: typed.faultKind, text: trunc(typed.text || contextText, 640), core: trunc(typed.core || contextText, 640) } : null,
      maintenance: maintenance ? { kind: maintenance.kind, maintenanceKind: maintenance.maintenanceKind, text: trunc(maintenance.text || contextText, 640), core: trunc(maintenance.core || contextText, 640), action: maintenance.action } : null,
      labelVisible: !!label.visible,
      labelComplete: !!label.complete,
      labelNodesVisited: Number(label.visited) || 0,
      host: {
        tag: host.tagName ? host.tagName.toLowerCase() : null,
        role: host.getAttribute && host.getAttribute('role'),
        testId: host.getAttribute && host.getAttribute('data-testid'),
        classHint: trunc(String(host.className || ''), 220),
      },
      turn: turn ? {
        role: turn.getAttribute('data-message-author-role') || turn.getAttribute('data-turn') || null,
        contentKey: turn.getAttribute('data-content-search-unit-key') || null,
        chatgptKey: turn.getAttribute('data-chatgpt-search-unit-key') || null,
        messageIds: trunc(turn.getAttribute('data-chatgpt-search-message-ids') || '', 320) || null,
      } : null,
      insideLatestAssistant: !!(assistant && assistant.element && assistant.element.contains(host)),
      observation: 'nearest bounded non-control failure-card context; literal visible wording may remain unclassified or be classified as maintenance-only',
    };
  }
  function retryObservation(assistant = latestAssistantTurn()) {
    const candidates = [];
    const add = element => { if (element && !candidates.includes(element)) candidates.push(element); };
    const scopes = assistant && assistant.element ? [assistant.element, document] : [document];
    for (const scope of scopes) {
      for (const element of uniqueElements(SELECTORS.retry, scope)) add(element);
      for (const element of qa('button,a', scope)) {
        const text = normalizeCompactText(`${element.textContent || ''} ${element.getAttribute('aria-label') || ''} ${element.getAttribute('data-testid') || ''}`);
        if (/^(?:retry|try again)\b/i.test(text)) add(element);
      }
    }
    const controls = candidates.filter(isVisible).slice(0, 30);
    return {
      schema: 'qomrade.retry-observation.v2',
      at: nowIso(),
      available: controls.length > 0,
      assistantId: assistant ? assistant.id : null,
      controls: controls.map(element => ({
        ...summarizeControl(element),
        insideLatestAssistant: !!(assistant && assistant.element && assistant.element.contains(element)),
        context: retryControlContext(element, assistant),
      })),
      authority: 'observe-only-never-click',
    };
  }
  function visibleConversationLoadFailureMaintenance() {
    const assistant = latestAssistantTurn();
    const candidates = [];
    const add = element => { if (element && !candidates.includes(element)) candidates.push(element); };
    for (const element of uniqueElements(SELECTORS.retry, document)) add(element);
    for (const element of qa('button,a', document)) {
      const label = normalizeCompactText(`${element.textContent || ''} ${element.getAttribute('aria-label') || ''} ${element.getAttribute('data-testid') || ''}`);
      if (/^(?:retry|try again)\b/i.test(label)) add(element);
    }
    for (const control of candidates.filter(isVisible).slice(0, 30)) {
      const context = retryControlContext(control, assistant);
      const maintenance = context?.maintenance || classifyPipelineMaintenanceText(context?.text || '');
      if (maintenance?.maintenanceKind !== 'conversation-load-failed') continue;
      const primary = control.closest('main,[data-app-shell-main-surface]') || control.parentElement || control;
      return {
        schema: 'qomrade.page-load-maintenance-observation.v1',
        at: nowIso(),
        maintenanceKind: maintenance.maintenanceKind,
        text: trunc(maintenance.text || context?.text || '', 640),
        core: trunc(maintenance.core || context?.text || '', 640),
        key: fnv1a64(JSON.stringify([conversationIdFromPath(), maintenance.maintenanceKind])),
        retryContext: context ? JSON.parse(JSON.stringify(context)) : null,
        retryControl: summarizeControl(control),
        _primaryNodes: [primary, control].filter(Boolean),
        authority: 'exact visible conversation-load failure; maintenance evidence only; never native Retry or prompt-send authority',
      };
    }
    return null;
  }
  function redSignalObservation() {
    const nodes = uniqueElements(SELECTORS.errors, document).filter(isVisible).slice(-MAX_RED_SIGNAL_RECORDS);
    return {
      schema: 'qomrade.red-signals-snapshot.v2',
      at: nowIso(),
      count: nodes.length,
      signals: nodes.map((element, index) => ({ index, ...elementSummary(element, { includePresentation: true }) })),
      authority: 'measured-evidence-only-unless-a-class-specific-law-applies',
    };
  }
  function systemSurfaceObservation() {
    const nodes = uniqueElements(SELECTORS.system, document)
      .filter(element => isVisible(element) && !(ui.host && ui.host.contains(element)))
      .slice(0, 60);
    return {
      schema: 'qomrade.system-surfaces.v1',
      at: nowIso(),
      count: nodes.length,
      surfaces: nodes.map((element, index) => ({ index, ...elementSummary(element, { includePresentation: true }) })),
      authority: 'evidence-only',
    };
  }
  function outputObservation(assistant = latestAssistantTurn()) {
    const inventory = zipInventory(assistant);
    return { schema: 'qomrade.output-observation.v3', at: nowIso(),
      turn: assistant ? { id: assistant.id, ordinal: assistant.ordinal, adapter: assistant.adapter, chars: (assistant.text || '').length, textHash: fnv1a64(assistant.text || '') } : null,
      controls: inventory.controls.slice(0, MAX_CONTROL_RECORDS).map(summarizeControl),
      candidates: inventory.candidates.map(({ element, ...row }) => row),
      scanned: inventory.scanned, overflow: inventory.overflow, activatedKey: state.lastZipKey,
      zipClicks: state.zipClicks, zipActivationErrors: state.zipActivationErrors, capture: zipCaptureSnapshot() };
  }
  function outputControlsObservation(assistant = latestAssistantTurn()) {
    const observation = outputObservation(assistant);
    return { ...observation, artifactControlIntent: !!(observation.candidates && observation.candidates.length) };
  }
  function resourceTimingObservation() {
    const available = !!(performance && typeof performance.getEntriesByType === 'function');
    const entries = available ? performance.getEntriesByType('resource') : [];
    const endpoints = Object.create(null);
    let endpointOverflowEntries = 0;
    for (const entry of entries) {
      let path = '';
      try { path = new URL(entry.name, location.href).pathname.replace(/\/c\/[0-9a-f-]+/ig, '/c/<id>').replace(/\/conversations\/[0-9a-f-]+/ig, '/conversations/<id>'); }
      catch (_) { path = trunc(entry.name || '', 500); }
      if (Object.prototype.hasOwnProperty.call(endpoints, path)) endpoints[path] += 1;
      else if (Object.keys(endpoints).length < MAX_RESOURCE_ENDPOINTS) endpoints[path] = 1;
      else endpointOverflowEntries += 1;
    }
    state.metrics.resourceEndpointOverflowEntries = Math.max(state.metrics.resourceEndpointOverflowEntries, endpointOverflowEntries);
    const records = entries.slice(-MAX_RESOURCE_RECORDS).map(entry => {
      let url = null;
      try { const parsed = new URL(entry.name, location.href); url = { origin: parsed.origin, pathname: parsed.pathname, searchKeys: Array.from(parsed.searchParams.keys()).slice(0, 20) }; }
      catch (_) { url = { raw: trunc(entry.name || '', 1_000) }; }
      return {
        name: url,
        initiatorType: entry.initiatorType || null,
        startTime: Math.round(entry.startTime || 0),
        durationMs: Math.round(entry.duration || 0),
        transferSize: Number.isFinite(entry.transferSize) ? entry.transferSize : null,
        encodedBodySize: Number.isFinite(entry.encodedBodySize) ? entry.encodedBodySize : null,
        decodedBodySize: Number.isFinite(entry.decodedBodySize) ? entry.decodedBodySize : null,
        responseStatus: Number.isFinite(entry.responseStatus) ? entry.responseStatus : null,
      };
    });
    return {
      schema: 'qomrade.resource-timing.v1',
      at: nowIso(),
      mode: 'explicit-on-demand-read-no-observer-no-buffer-mutation',
      available,
      entryCount: entries.length,
      oldestStartTime: entries.length ? Math.round(entries[0].startTime || 0) : null,
      newestStartTime: entries.length ? Math.round(entries[entries.length - 1].startTime || 0) : null,
      bufferLikelyCapped: entries.length >= 250,
      endpoints,
      endpointLimit: MAX_RESOURCE_ENDPOINTS,
      endpointOverflowEntries,
      endpointsTruncated: endpointOverflowEntries > 0,
      recent: records,
      limitations: ['No active-request count or stream-byte timing is available without page interposition or an observer.', 'The page Resource Timing buffer may omit older entries; qomrade does not resize or clear it.'],
    };
  }
  function semanticDomObservation() {
    const composer = findComposer();
    const model = findModelButton();
    const turns = materializedTurns();
    const all = qa('[data-testid],[data-turn-key],[data-content-search-turn-key],[data-chatgpt-search-unit-key],[data-message-author-role],[data-composer-markdown],[role],[aria-label],[contenteditable]');
    const records = [];
    const pattern = /chatgpt|composer|turn|message|conversation|reason|model|send|stop|retry|continue|error|alert|dialog|status|assistant|user/i;
    for (const element of all) {
      if (records.length >= MAX_DOM_SEMANTIC_RECORDS) break;
      const signature = Array.from(element.attributes || []).map(attribute => `${attribute.name}=${attribute.value}`).join(' ');
      if (!pattern.test(`${element.tagName} ${signature}`)) continue;
      records.push(elementSummary(element, { redactContent: element.isContentEditable }));
    }
    const weak = !composer || !model || turns.length === 0;
    let fallback = null;
    if (weak) {
      const root = q('main') || document.body;
      let html = '';
      try { html = root ? root.outerHTML || '' : ''; } catch (_) {}
      const limit = 160_000;
      fallback = {
        reason: { composerMissing: !composer, modelMissing: !model, turnsMissing: turns.length === 0 },
        rootTag: root && root.tagName ? root.tagName.toLowerCase() : null,
        totalChars: html.length,
        head: html.slice(0, Math.floor(limit / 2)),
        tail: html.length > limit ? html.slice(-Math.floor(limit / 2)) : '',
      };
    }
    return {
      schema: 'qomrade.semantic-dom-observation.v1',
      at: nowIso(),
      totalElementCount: document.getElementsByTagName('*').length,
      mainCount: qa('main').length,
      formCount: qa('form').length,
      semanticCandidateCount: all.length,
      records,
      weakAdapterEvidence: weak,
      fallback,
    };
  }
  function pageObservation() {
    return {
      schema: 'qomrade.page-observation.v1',
      at: nowIso(),
      href: location.href,
      origin: location.origin,
      pathname: location.pathname,
      searchKeys: Array.from(new URL(location.href).searchParams.keys()).slice(0, 30),
      title: document.title,
      titleLength: document.title.length,
      referrer: document.referrer || '',
      readyState: document.readyState,
      visibility: document.visibilityState,
      focused: document.hasFocus(),
      historyLength: history.length,
      lang: document.documentElement.lang || null,
      viewport: { width: innerWidth, height: innerHeight, devicePixelRatio },
      scroll: { x: Math.round(scrollX), y: Math.round(scrollY) },
      userAgent: navigator.userAgent,
      platform: navigator.platform,
      language: navigator.language,
      timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
      secureContext: isSecureContext,
    };
  }
  function userscriptEnvironmentObservation() {
    const info = typeof GM_info === 'object' && GM_info ? GM_info : null;
    const script = info && info.script && typeof info.script === 'object' ? info.script : null;
    return {
      schema: 'qomrade.userscript-environment.v1',
      available: !!info,
      manager: info ? info.scriptHandler || null : null,
      managerVersion: info ? info.version || null : null,
      sandboxMode: info ? info.sandboxMode || null : null,
      isIncognito: info ? !!info.isIncognito : null,
      script: script ? {
        name: script.name || null,
        namespace: script.namespace || null,
        version: script.version || null,
        description: script.description || null,
        runAt: script['run-at'] || script.run_at || null,
        grants: Array.isArray(script.grant) ? script.grant.slice(0, 40) : [],
        matches: Array.isArray(script.matches) ? script.matches.slice(0, 20) : [],
        excludes: Array.isArray(script.excludes) ? script.excludes.slice(0, 20) : [],
      } : null,
      observedOnly: true,
    };
  }
  function notificationEnvironmentObservation() {
    return {
      schema: 'qomrade.notification-environment.v2',
      userscriptDesktopNotificationCapability: false,
      constructorAvailable: typeof Notification === 'function',
      permission: typeof Notification === 'function' ? Notification.permission : null,
      serviceWorkerSupported: 'serviceWorker' in navigator,
      controllerScriptURL: navigator.serviceWorker && navigator.serviceWorker.controller ? navigator.serviceWorker.controller.scriptURL : null,
      fileOutcomeObserver: { active: !!ui.fileOutcomeObserver, watch: state.zipCapture.outcomeWatch, notices: state.zipCapture.notices.slice(-MAX_FILE_NOTICES) },
      observedOnly: true,
      qomradeMutations: false,
    };
  }
  function currentControlsObservation() {
    const composer = findComposer();
    const send = findSendButton();
    const stop = findStopButton();
    const model = findModelButton();
    return {
      schema: 'qomrade.controls-observation.v1',
      at: nowIso(),
      composer: { summary: elementSummary(composer, { redactContent: true }), route: selectorRoute(composer, SELECTORS.composer) },
      send: { summary: elementSummary(send), route: selectorRoute(send, SELECTORS.send) },
      stop: { summary: elementSummary(stop), route: selectorRoute(stop, SELECTORS.stop) },
      model: { summary: elementSummary(model), route: selectorRoute(model, SELECTORS.model), observation: (() => { const item = currentModelObservation(); return { ok: item.ok, reason: item.reason, label: item.label, family: item.family, hasPro: item.hasPro }; })() },
      families: {
        composer: selectorFamilyProbe('composer', SELECTORS.composer, composer),
        send: selectorFamilyProbe('send', SELECTORS.send, send),
        stop: selectorFamilyProbe('stop', SELECTORS.stop, stop),
        model: selectorFamilyProbe('model', SELECTORS.model, model),
        turns: selectorFamilyProbe('turns', SELECTORS.turns, null),
        history: selectorFamilyProbe('history', SELECTORS.history, null),
      },
    };
  }
  function actionReceiptSnapshot() {
    const history = state.turnReceipts.slice(-MAX_TURN_RECEIPTS);
    return {
      active: state.activeSend ? JSON.parse(JSON.stringify(state.activeSend)) : null,
      latest: history.length ? history[history.length - 1] : null,
      history,
      modelAtSend: state.modelAtSend,
      modelDrifts: state.modelDrifts.slice(-20),
      modelIndicatorEdges: state.modelIndicatorEdges.slice(-20),
      modelGate: {
        ...state.modelGate,
        recentSurveys: state.modelGate.recentSurveys.slice(-MAX_MODEL_SURVEY_RECORDS),
      },
      science: {
        ...state.science,
        pulses: state.science.pulses.slice(-MAX_SCIENCE_PULSES),
        surfaceEdges: state.science.surfaceEdges.slice(-MAX_PIPELINE_SURFACE_EDGES),
      },
    };
  }
  function adoptExactPromptSuccessor({ turns = null, expectedUserId = null, origin = 'active-observation' } = {}) {
    const active = state.activeSend;
    if (!active || active.outcome || !state.runPrompt || !stableRequestId(active.userTurnId)) return false;
    turns = turns || materializedTurns();
    const activeUser = turns.find(turn => turn.role === 'user' && turn.id === active.userTurnId);
    const users = turns.filter(turn => turn.role === 'user');
    const latestUser = users[users.length - 1] || null;
    if (!activeUser || !latestUser || latestUser.id === active.userTurnId || latestUser.index <= activeUser.index
      || !stableRequestId(latestUser.id) || (expectedUserId && latestUser.id !== expectedUserId)) return false;
    const successorTurns = users.filter(turn => turn.index > activeUser.index && turn.index <= latestUser.index);
    const successorEvidence = successorTurns.map(turn => {
      const text = turnText(turn.element);
      return { turn, text, match: compareRenderedPrompt(text, state.runPrompt) };
    });
    // A same-text successor may extend the active run. Any different intervening
    // user turn remains operator intervention and cannot be silently crossed.
    if (!successorEvidence.length || successorEvidence.some(item => !item.match.ok)) return false;
    const before = turns.filter(turn => turn.index < latestUser.index);
    const previousAssistant = before.filter(turn => turn.role === 'assistant').slice(-1)[0] || null;
    const prior = JSON.parse(JSON.stringify(active));
    prior.completedAt = nowIso();
    prior.outcome = 'superseded-by-exact-successor';
    prior.supersededByUserId = latestUser.id;
    prior.successorUserIds = successorEvidence.map(item => item.turn.id);
    prior.authority = `${prior.authority || 'active request custody'}; released only to a later stable user turn rendering the exact captured prompt`;
    if (previousAssistant && previousAssistant.index > activeUser.index) {
      prior.assistantTurnId = previousAssistant.id;
      prior.assistantTurnOrdinal = previousAssistant.ordinal;
      prior.assistantAdapter = previousAssistant.adapter;
      const previousAssistantText = turnText(previousAssistant.element);
      prior.assistantTextChars = previousAssistantText.length;
      prior.assistantTextHash = fnv1a64(previousAssistantText);
    }
    state.turnReceipts.push(prior);
    if (state.turnReceipts.length > MAX_TURN_RECEIPTS) state.turnReceipts.splice(0, state.turnReceipts.length - MAX_TURN_RECEIPTS);
    const adoptedAt = nowIso();
    const adoptedT = Date.now();
    const rootKey = active.recoveryRootKey || null;
    const preMaxOrdinal = before.reduce((maximum, turn) => turn.ordinal == null ? maximum : maximum == null ? turn.ordinal : Math.max(maximum, turn.ordinal), null);
    state.activeSend = {
      schema: 'qomrade.send-transaction.v2',
      id: `recover-successor-${adoptedT.toString(36)}-${state.adoptedWithoutClick + 1}`,
      startedAt: adoptedAt,
      clickedAt: null,
      clickMode: 'exact-prompt-successor-adopted-without-qomrade-click',
      promptHash: fnv1a64(state.runPrompt),
      promptChars: state.runPrompt.length,
      preTurnIds: before.map(turn => turn.id),
      preMaxOrdinal,
      userTurnId: latestUser.id,
      userTurnOrdinal: latestUser.ordinal,
      userAdoptedAt: adoptedAt,
      userTextHash: fnv1a64(successorEvidence[successorEvidence.length - 1].text),
      userTextChars: successorEvidence[successorEvidence.length - 1].text.length,
      userAdoptionMatch: successorEvidence[successorEvidence.length - 1].match.kind,
      userAdoptionEvidence: successorEvidence[successorEvidence.length - 1].match,
      baselineAssistantId: previousAssistant?.id || null,
      model: null,
      modelPreference: state.modelGate.runPreference || '5.6-first',
      outcome: null,
      adoptionOrigin: origin,
      recoveryRootKey: rootKey,
      recoveryParentId: active.id,
      predecessorUserId: active.userTurnId,
      successorUserIds: successorEvidence.map(item => item.turn.id),
      authority: 'active operator run plus a stable later user turn rendering the exact captured prompt; no Send authorship or model identity is claimed for that successor',
    };
    state.baselineAssistantId = previousAssistant?.id || null;
    state.latestAssistantId = null;
    state.latestAssistantFingerprint = null;
    state.stableSamples = 0;
    state.modelAtSend = null;
    state.lastError = null;
    state.waitingSince = adoptedT;
    state.lastSendAt = adoptedT;
    state.nextSendAt = adoptedT + Math.round(settings.gapMinutes * 60_000);
    state.adoptedWithoutClick += 1;
    const entry = rootKey ? state.faultRecovery.ledger.find(item => item.key === rootKey) : null;
    if (entry) {
      entry.userIds = Array.isArray(entry.userIds) ? entry.userIds : [entry.userId].filter(Boolean);
      for (const item of successorEvidence) if (!entry.userIds.includes(item.turn.id)) entry.userIds.push(item.turn.id);
      entry.userId = latestUser.id;
      entry.samples = 0;
      entry.lastSignature = null;
      entry.progressSignature = null;
      entry.nextAt = recoveryNow() + faultQuietMs();
      recoveryOutcome(entry, 'exact-successor-adopted', {
        fromUserId: active.userTurnId,
        toUserId: latestUser.id,
        transactionId: state.activeSend.id,
        predecessorTransactionId: active.id,
        successorCount: successorEvidence.length,
        noSendAuthorshipClaimed: true,
      });
    }
    logEvent('exact-prompt-successor-adopted', 'A newer stable user turn rendered the exact captured prompt. qomrade transferred reply and recovery custody instead of treating it as foreign ownership.', {
      origin,
      fromUserId: active.userTurnId,
      toUserId: latestUser.id,
      predecessorTransactionId: active.id,
      transactionId: state.activeSend.id,
      successorUserIds: successorEvidence.map(item => item.turn.id),
      baselineAssistantId: state.baselineAssistantId,
    });
    captureSessionTurns('exact-prompt-successor-adopted');
    persistContinuity('exact-prompt-successor-adopted');
    return true;
  }
  function captureActiveSendAdoption() {
    const active = state.activeSend;
    if (!active) return active;
    const turns = materializedTurns();
    if (active.userAdoptedAt && stableRequestId(active.userTurnId)) {
      adoptExactPromptSuccessor({ turns, origin: 'active-observation' });
      return state.activeSend;
    }
    const priorIds = new Set(Array.isArray(active.preTurnIds) ? active.preTurnIds : []);
    const candidates = turns.filter(turn => turn.role === 'user' && !priorIds.has(turn.id));
    active.userAdoptionCandidates = candidates.slice(0, 8).map(turn => {
      const text = turnText(turn.element);
      return { id: turn.id, ordinal: turn.ordinal, chars: text.length, textHash: fnv1a64(text), compactHash: fnv1a64(normalizeCompactText(text)), head: trunc(normalizeCompactText(text), 240) };
    });
    for (const turn of candidates.slice(-1)) {
      const text = turnText(turn.element);
      const match = compareRenderedPrompt(text, state.runPrompt);
      if (match.ok) {
        if (active.userTurnId && active.userTurnId !== turn.id) {
          active.userTurnAliases = [...(active.userTurnAliases || []), active.userTurnId].slice(-4);
          logEvent('request-id-promoted', 'Promoted provisional request identity without resending.', { from: active.userTurnId, to: turn.id, transactionId: active.id });
        }
        active.userTurnId = turn.id;
        const recoveryEntry = state.faultRecovery.ledger.find(item => item.key === active.recoveryRootKey);
        if (recoveryEntry && stableRequestId(turn.id) && !recoveryEntry.userIds.includes(turn.id)) recoveryEntry.userIds.push(turn.id);
        active.userTurnOrdinal = turn.ordinal;
        active.userAdoptedAt = nowIso();
        active.userTextHash = fnv1a64(text);
        active.userTextChars = text.length;
        active.userAdoptionMatch = match.kind;
        active.userAdoptionEvidence = match;
        logEvent('send-adopted', active.clickedAt ? 'The clicked prompt appeared as one new user turn after Send.' : 'A no-click transaction adopted one conservatively matching new user turn.', { transactionId: active.id, userTurnId: turn.id, userTurnOrdinal: turn.ordinal, match: active.userAdoptionMatch, clickMode: active.clickMode });
        captureSessionTurns('send-adopted');
        persistContinuity('send-adopted');
        break;
      }
    }
    if (!active.userAdoptedAt && candidates.length) active.userAdoptionStatus = 'new-user-turn-present-but-rendered-text-not-equal';
    else if (!candidates.length) active.userAdoptionStatus = 'no-new-user-turn-materialized-yet';
    return active;
  }
  function normalizeDownloadSuffixList(value, { fallback = true } = {}) {
    const source = Array.isArray(value) ? value.join(',') : String(value == null ? '' : value);
    const suffixes = [];
    for (let item of source.split(/[,;\n]+/)) {
      item = item.trim().toLocaleLowerCase('en-US').replace(/^\*+/, '');
      if (!item) continue;
      if (!item.startsWith('.')) item = `.${item}`;
      if (item.length > 48 || !/^\.[a-z0-9][a-z0-9._+-]*$/i.test(item)) continue;
      if (!suffixes.includes(item)) suffixes.push(item);
      if (suffixes.length >= MAX_DOWNLOAD_SUFFIXES) break;
    }
    if (!suffixes.length && fallback) suffixes.push(DEFAULT_DOWNLOAD_SUFFIXES);
    suffixes.sort((a, b) => b.length - a.length || a.localeCompare(b));
    return { suffixes, text: suffixes.join(', '), source: trunc(source, MAX_DOWNLOAD_SUFFIX_CHARS) };
  }
  function activeDownloadSuffixes() {
    return normalizeDownloadSuffixList(settings.downloadSuffixes, { fallback: true }).suffixes;
  }
  function matchingDownloadFilename(value, suffixes = activeDownloadSuffixes()) {
    let text = String(value || '').trim();
    if (!text || text.length > 1024) return null;
    try { text = decodeURIComponent(text); } catch (_) {}
    text = text.replace(/^(?:Download|Open preview of)\s+/i, '').split(/[?#]/, 1)[0];
    const name = text.split(/[\\/]/).at(-1).trim();
    if (!name || /[\x00-\x1f<>]/.test(name)) return null;
    const lower = name.toLocaleLowerCase('en-US');
    const suffix = suffixes.find(item => lower.endsWith(item));
    return suffix ? { filename: name, suffix } : null;
  }
  // Explicit file controls are scanned before generic actions. A short
  // operator-configured settling period gives ChatGPT's generated-file service time
  // to finish publishing the object before qomrade activates the native control.
  const FILE_PRIMARY_CONTROL_SELECTOR = '[data-file-reference],a[download],[aria-label^="Download " i],[aria-label="Download file" i],[data-markdown-copy-text]';
  const ZIP_CONTROL_SELECTOR = 'a,button,[role="button"],[role="link"],[data-file-reference]';
  const FILE_NOTICE_SELECTOR = '[role="alert"],[aria-live="assertive"],[aria-live="polite"],[data-testid*="toast" i],[data-testid*="notification" i],[data-sonner-toast],[class*="toast" i],[class*="notification" i]';
  const ZIP_SCAN_LIMIT = 128;
  function explicitFileDownloadAuthority(element) {
    if (!(element instanceof Element)) return null;
    const attr = name => element.getAttribute(name) || '';
    const label = normalizeCompactText(attr('aria-label') || element.textContent || '');
    if (element.hasAttribute('data-file-reference')) return 'data-file-reference';
    if (element.tagName === 'A' && element.hasAttribute('download')) return 'anchor-download-attribute';
    if (/^Download(?:\s|$)/i.test(label)) return 'download-labelled-control';
    return null;
  }
  function zipFilename(value) { const match = matchingDownloadFilename(value); return match && match.filename; }
  function zipControlDescriptor(element, assistantId) {
    const attr = name => element.getAttribute(name) || '';
    const href = element.tagName === 'A' ? attr('href') : '';
    const download = attr('download'), ariaLabel = attr('aria-label'), copyName = attr('data-markdown-copy-text');
    const text = trunc(normalizeCompactText(element.textContent || ''), 512);
    if (/^Open preview\b/i.test(ariaLabel) || element.closest('pre,code')) return null;
    if (href && /^[a-z][a-z0-9+.-]*:/i.test(href) && !/^(?:https?:|blob:|sandbox:)/i.test(href)) return null;
    const suffixes = activeDownloadSuffixes();
    const matched = matchingDownloadFilename(copyName, suffixes) || matchingDownloadFilename(download, suffixes)
      || matchingDownloadFilename(href, suffixes) || matchingDownloadFilename(ariaLabel, suffixes) || matchingDownloadFilename(text, suffixes);
    let filename = matched && matched.filename, matchedSuffix = matched && matched.suffix;
    const explicitAuthority = explicitFileDownloadAuthority(element);
    if (element.tagName === 'A' && !explicitAuthority) return null;
    let adapter = attr('data-file-reference') ? 'inline-file-reference'
      : element.tagName === 'A' && element.hasAttribute('download') ? 'anchor-download-attribute'
      : element.tagName === 'A' ? 'anchor-download-labelled' : 'named-download-control';
    if (!filename && /^Download file$/i.test(ariaLabel)) {
      let parent = element.parentElement;
      for (let depth = 0; parent && depth < 3; depth++, parent = parent.parentElement) {
        if (parent.querySelectorAll('[aria-label="Download file"]').length !== 1) break;
        const matches = Array.from(parent.querySelectorAll('[data-markdown-copy-text],[aria-label^="Open preview of "]')).slice(0, 8)
          .map(node => matchingDownloadFilename(node.getAttribute('data-markdown-copy-text') || node.getAttribute('aria-label'), suffixes)).filter(Boolean);
        const names = [...new Map(matches.map(item => [item.filename, item])).values()];
        if (names.length === 1) { filename = names[0].filename; matchedSuffix = names[0].suffix; adapter = 'file-card-download'; break; }
        if (names.length > 1) break;
      }
    }
    if (!filename || (!explicitAuthority && adapter !== 'file-card-download')) return null;
    if (element.tagName !== 'A' && element.tagName !== 'BUTTON' && !['button','link'].includes(attr('role'))) return null;
    const key = fnv1a64(`${location.pathname}|${assistantId}|${filename}`);
    return { element, key, filename, matchedSuffix, adapter, downloadAuthority: explicitAuthority || 'unique-file-card-download', href: trunc(href, 512), text,
      visible: isVisible(element), enabled: isEnabled(element), busy: attr('aria-busy') === 'true',
      ariaLabel: trunc(ariaLabel, 512), download: trunc(download, 512), copyName: trunc(copyName, 512) };
  }
  function zipInventory(assistant) {
    if (!assistant?.element) return { controls: [], candidates: [], scanned: 0, overflow: 0, primaryMatched: 0, ignoredProseAnchors: 0 };
    const primary = uniqueElements([FILE_PRIMARY_CONTROL_SELECTOR], assistant.element);
    const all = uniqueElements([FILE_PRIMARY_CONTROL_SELECTOR, ZIP_CONTROL_SELECTOR], assistant.element);
    const controls = all.slice(0, ZIP_SCAN_LIMIT);
    const ignoredProseAnchors = all.filter(node => node.tagName === 'A' && !explicitFileDownloadAuthority(node)
      && !!(matchingDownloadFilename(node.getAttribute('href')) || matchingDownloadFilename(node.textContent))).length;
    const candidates = [...new Map(controls.map(node => zipControlDescriptor(node, assistant.id)).filter(Boolean)
      .sort((a,b) => Number(b.visible && b.enabled && !b.busy) - Number(a.visible && a.enabled && !a.busy)).map(row => [row.key,row])).values()];
    return { controls, candidates, scanned: controls.length, primaryMatched: primary.length, ignoredProseAnchors, overflow: Math.max(0, all.length - controls.length) };
  }
  function classifyFileDownloadNotice(text, host = null) {
    const value = normalizeCompactText(text);
    if (!value || value.length > 1_500) return null;
    if (/^(?:Response complete|ChatGPT is responding|Analyzed|Thinking|Loading(?: older messages)?[.…]*|Our systems are thinking a bit more about this request before responding\.)$/i.test(value))
      return { text: value, ignored: true, ignoreReason: 'generic-chat-status' };
    const failure = /(?:download|file|attachment).*(?:could(?:n['’]?t| not)|unable|failed|failure|error|unavailable|expired|try again)|(?:could(?:n['’]?t| not)|unable|failed|failure|error).*(?:download|file|attachment)/i.test(value);
    const related = /\b(?:download|file|attachment)\b/i.test(value);
    const alertish = host instanceof Element && (host.getAttribute('role') === 'alert' || host.getAttribute('aria-live') === 'assertive'
      || /(?:toast|notification)/i.test(`${host.getAttribute('data-testid') || ''} ${typeof host.className === 'string' ? host.className : ''}`));
    if (!failure && !related && !alertish) return null;
    const ambiguous = !failure && !related;
    return { text: value, failure, ambiguous, kind: failure ? 'file-download-failure' : ambiguous ? 'file-download-ambiguous-notice' : 'file-download-notice' };
  }
  function clearFileOutcomeObserver(reason = 'cleared') {
    if (ui.fileOutcomeObserver) ui.fileOutcomeObserver.disconnect();
    if (ui.fileOutcomeTimer) clearTimeout(ui.fileOutcomeTimer);
    ui.fileOutcomeObserver = ui.fileOutcomeTimer = null;
    if (state.zipCapture.outcomeWatch) state.zipCapture.outcomeWatch.endedAt = nowIso(), state.zipCapture.outcomeWatch.endReason = reason;
  }
  function fileNoticeHosts(node) {
    const root = node instanceof Element ? node : node?.parentElement;
    if (!root) return [];
    const found = [];
    if (root.matches(FILE_NOTICE_SELECTOR)) found.push(root);
    const closest = root.closest(FILE_NOTICE_SELECTOR); if (closest) found.push(closest);
    found.push(...Array.from(root.querySelectorAll(FILE_NOTICE_SELECTOR)).slice(0, 12));
    return [...new Set(found)].filter(host => !host.closest('[data-message-author-role],[data-testid^="conversation-turn-"],[data-content-search-turn-key],[data-chatgpt-search-unit-key]'));
  }
  function recordFileDownloadNotice(host, origin = 'mutation') {
    if (!(host instanceof Element)) return null;
    const classified = classifyFileDownloadNotice(host.innerText || host.textContent || '', host);
    if (!classified) return null;
    if (classified.ignored) {
      const signature = fnv1a64(`${classified.ignoreReason}|${classified.text}`), prior = state.zipCapture.lastIgnoredNeutralNotice;
      if (!prior || prior.signature !== signature || Date.now() - prior.observedT > FILE_OUTCOME_WATCH_MS) {
        state.zipCapture.ignoredNeutralNotices += 1;
        state.zipCapture.lastIgnoredNeutralNotice = { at: nowIso(), observedT: Date.now(), signature, text: classified.text, reason: classified.ignoreReason };
      }
      return null;
    }
    const rect = elementSummary(host, { includePresentation: true })?.rect || null, signature = fnv1a64(`${classified.kind}|${classified.text}`);
    if (state.zipCapture.notices.some(row => row.signature === signature && Date.now() - row.observedT < FILE_OUTCOME_WATCH_MS)) return null;
    const activations = state.zipCapture.outcomeWatch?.activations || [];
    const activation = [...activations].reverse().find(row => Date.now() - row.activatedT <= FILE_OUTCOME_WATCH_MS) || null;
    const notice = { schema: 'qomrade.file-download-notice.v1', observedAt: nowIso(), observedT: Date.now(), origin,
      ...classified, signature, role: host.getAttribute('role'), ariaLive: host.getAttribute('aria-live'), dataTestId: host.getAttribute('data-testid'),
      classHint: trunc(typeof host.className === 'string' ? host.className : '', 400), rect, activationId: activation?.id || null,
      filename: activation?.filename || null, activationSource: activation?.source || null };
    boundedReceipt(state.zipCapture.notices, notice, MAX_FILE_NOTICES);
    const receipt = activation && state.zipCapture.receipts.find(row => row.id === activation.id);
    if (receipt) {
      receipt.noticeSignature = signature; receipt.noticeText = classified.text; receipt.noticeAt = notice.observedAt;
      if (classified.failure) {
        receipt.outcome = 'failure-notice-observed';
        if (activation.source === 'qomrade' && (receipt.attempt || 1) < 2) receipt.retryEligibleAtT = Date.now() + FILE_FAILURE_RETRY_DELAY_MS;
      }
    }
    const snapshotId = captureDomishEvent('file-download-notification', { reason: classified.text, severity: classified.failure ? 'error' : 'warn',
      origin: 'file-outcome-observer', primaryNodes: [host], force: classified.failure || classified.ambiguous, context: notice });
    notice.domSnapshotId = snapshotId || null;
    logEvent(classified.kind, classified.failure ? 'Observed a page notification indicating that a file activation failed.'
      : classified.ambiguous ? 'Observed an ambiguous top-level alert after file activation; preserved as evidence only.'
        : 'Observed a file-related page notification after activation.', notice);
    if (classified.failure && activation?.source === 'qomrade' && state.running && !state.paused && state.zipCapture.pending) armZipRescan();
    render();
    return notice;
  }
  function armFileOutcomeObserver(activation) {
    if (!activation) return;
    const now = Date.now();
    if (!state.zipCapture.outcomeWatch || state.zipCapture.outcomeWatch.expiresAtT < now) {
      state.zipCapture.outcomeWatch = { schema: 'qomrade.file-outcome-watch.v1', startedAt: nowIso(), expiresAtT: now + FILE_OUTCOME_WATCH_MS, activations: [] };
    }
    state.zipCapture.outcomeWatch.expiresAtT = now + FILE_OUTCOME_WATCH_MS;
    boundedReceipt(state.zipCapture.outcomeWatch.activations, activation, 8);
    if (!ui.fileOutcomeObserver && typeof MutationObserver === 'function' && document.body) {
      ui.fileOutcomeObserver = new MutationObserver(records => {
        for (const record of records) {
          for (const node of [record.target, ...record.addedNodes]) for (const host of fileNoticeHosts(node)) recordFileDownloadNotice(host);
        }
      });
      ui.fileOutcomeObserver.observe(document.body, { childList: true, subtree: true, characterData: true });
    }
    if (ui.fileOutcomeTimer) clearTimeout(ui.fileOutcomeTimer);
    ui.fileOutcomeTimer = setTimeout(() => clearFileOutcomeObserver('watch-expired'), FILE_OUTCOME_WATCH_MS);
  }
  function manualFileClickObservation(event) {
    if (!event.isTrusted) return;
    const control = event.target instanceof Element && event.target.closest(FILE_PRIMARY_CONTROL_SELECTOR + ',button,[role="button"]');
    if (!control) return;
    const turn = materializedTurns().find(row => row.role === 'assistant' && row.element.contains(control));
    const descriptor = turn && zipControlDescriptor(control, turn.id);
    if (!descriptor) return;
    armFileOutcomeObserver({ id: `manual-${Date.now().toString(36)}`, activatedAt: nowIso(), activatedT: Date.now(), source: 'operator', turnId: turn.id, key: descriptor.key, filename: descriptor.filename, attempt: 1 });
  }
  function zipCaptureSnapshot() {
    const normalized = normalizeDownloadSuffixList(settings.downloadSuffixes, { fallback: true });
    return { schema: 'qomrade.file-capture.v2', legacySchema: 'qomrade.zip-capture.v3', enabled: settings.autoZip, autoZip: settings.autoZip,
      suffixes: normalized.suffixes, suffixText: normalized.text, settleSeconds: normalizeFileDelaySeconds(settings.fileDelaySeconds),
      maxPerReply: 4, scanPassLimit: FILE_SCAN_MAX_PASSES, pending: state.zipCapture.pending ? { ...state.zipCapture.pending } : null,
      lastScan: state.zipCapture.lastScan, receipts: state.zipCapture.receipts.slice(-32), notices: state.zipCapture.notices.slice(-MAX_FILE_NOTICES),
      outcomeWatch: state.zipCapture.outcomeWatch, autoRetries: state.zipCapture.autoRetries,
      ignoredNeutralNotices: state.zipCapture.ignoredNeutralNotices, lastIgnoredNeutralNotice: state.zipCapture.lastIgnoredNeutralNotice,
      fileRequests: state.zipClicks, fileActivationErrors: state.zipActivationErrors, diskWriteVerified: false,
      completionEvidence: 'native activation plus bounded page-notification evidence; browser disk completion remains unobservable',
      identity: 'conversation + assistant turn + exact named matching file; filename equality is not byte equality' };
  }
  function fileRetryReceipt(turnId, key) {
    return [...state.zipCapture.receipts].reverse().find(row => row.turnId === turnId && row.key === key && row.outcome === 'failure-notice-observed' && (row.attempt || 1) < 2 && !row.retryCommittedAt) || null;
  }
  function captureZipFromAssistant(assistant) {
    const blocked = !state.running ? 'stopped' : state.paused ? 'paused' : state.quarantine ? 'quarantined'
      : !settings.autoZip ? 'disabled' : pauseForHidden() && document.hidden ? 'hidden-policy-hold' : null;
    if (blocked || !assistant?.element) return false;
    const inventory = zipInventory(assistant), now = Date.now(), settleMs = normalizeFileDelaySeconds(settings.fileDelaySeconds) * 1_000;
    const prior = state.zipCapture.receipts.filter(row => row.turnId === assistant.id);
    const audit = { at: nowIso(), turnId: assistant.id, hidden: document.hidden, controlsScanned: inventory.scanned,
      primaryControlsMatched: inventory.primaryMatched, ignoredProseAnchors: inventory.ignoredProseAnchors, overflow: inventory.overflow, candidates: [], reason: inventory.candidates.length ? 'candidates-found' : 'no-named-matching-file-control' };
    state.zipCapture.lastScan = audit;
    if (prior.length >= 4) { audit.reason = 'per-reply-budget'; return false; }
    for (const candidate of inventory.candidates) {
      const seen = state.zipCapture.seen[candidate.key] || (state.zipCapture.seen[candidate.key] = { firstSeenAt: nowIso(), firstSeenT: now });
      const retry = fileRetryReceipt(assistant.id, candidate.key), already = state.zipKeys.includes(candidate.key);
      const eligibleAtT = retry ? Number(retry.retryEligibleAtT) || Infinity : seen.firstSeenT + settleMs;
      audit.candidates.push({ ...Object.fromEntries(Object.entries(candidate).filter(([key]) => key !== 'element')), alreadyAttempted: already, firstSeenAt: seen.firstSeenAt, eligibleAt: new Date(eligibleAtT).toISOString(), settleRemainingMs: Math.max(0, eligibleAtT - now), retry: !!retry });
      if (!candidate.visible || !candidate.enabled || candidate.busy || now < eligibleAtT || (already && !retry)) continue;
      const attempt = retry ? 2 : 1, id = `file-${Date.now().toString(36)}-${Math.random().toString(36).slice(2,7)}`;
      if (!already) { state.lastZipKey = candidate.key; state.zipKeys.push(candidate.key); if (state.zipKeys.length > MAX_ZIP_KEYS) state.zipKeys.splice(0, state.zipKeys.length - MAX_ZIP_KEYS); }
      if (retry) retry.retryCommittedAt = nowIso(), state.zipCapture.autoRetries += 1;
      const receipt = { id, at: nowIso(), activatedT: now, turnId: assistant.id, key: candidate.key, filename: candidate.filename,
        matchedSuffix: candidate.matchedSuffix, adapter: candidate.adapter, downloadAuthority: candidate.downloadAuthority, hidden: document.hidden,
        attempt, retryOf: retry?.id || null, outcome: 'activation-reserved', diskWriteVerified: false };
      boundedReceipt(state.zipCapture.receipts, receipt, 32);
      armFileOutcomeObserver({ id, activatedAt: receipt.at, activatedT: now, source: 'qomrade', turnId: assistant.id, key: candidate.key, filename: candidate.filename, attempt });
      try {
        candidate.element.click(); state.zipClicks += 1; if (receipt.hidden) state.background.hiddenZipActivations += 1;
        receipt.outcome = 'activation-dispatched'; audit.reason = receipt.outcome;
        logEvent('file-download-click', 'Activated a matching native file control; a bounded notification watch is active, but disk completion is not observed.', { ...receipt });
        persistContinuity('file-activation'); render(); return true;
      } catch (error) {
        state.zipActivationErrors += 1; receipt.outcome = 'activation-error'; receipt.message = trunc(error?.message || error, 400); audit.reason = receipt.outcome;
        const record = { kind: 'file-activation-error', ...receipt }; recordPageError(record);
        logEvent('file-activation-error', 'File activation threw synchronously; reply custody remains successful.', record);
        persistContinuity('file-activation-error'); render(); return false;
      }
    }
    audit.reason = audit.candidates.some(row => row.settleRemainingMs > 0) ? 'waiting-for-file-settle-delay'
      : inventory.candidates.length ? 'all-candidates-duplicate-busy-or-unavailable' : 'no-named-matching-file-control';
    return false;
  }
  function armZipRescan() {
    if (ui.zipRescanTimer) clearTimeout(ui.zipRescanTimer);
    ui.zipRescanTimer = null;
    const pending = state.zipCapture.pending;
    if (!pending || !state.running || state.paused || state.quarantine || !settings.autoZip || (pauseForHidden() && document.hidden)) return;
    if (pending.pathname !== location.pathname || pending.passes >= FILE_SCAN_MAX_PASSES || Date.now() >= pending.deadlineAtT) { state.zipCapture.pending = null; return; }
    ui.zipRescanTimer = setTimeout(() => {
      ui.zipRescanTimer = null;
      if (state.zipCapture.pending !== pending || !state.running || state.paused || state.quarantine || !settings.autoZip) return;
      if (pauseForHidden() && document.hidden) return;
      if (pending.pathname !== location.pathname) { state.zipCapture.pending = null; return; }
      pending.passes += 1; invalidateTurnCache('file-rescan');
      const turn = materializedTurns().find(row => row.id === pending.assistantId && row.role === 'assistant');
      if (turn) captureZipFromAssistant(turn);
      const attempts = state.zipCapture.receipts.filter(row => row.turnId === pending.assistantId).length;
      if (pending.passes >= FILE_SCAN_MAX_PASSES || attempts >= 4 || Date.now() >= pending.deadlineAtT) {
        state.zipCapture.pending = null; wakeOverdueAutoRefresh('file-rescan-complete', ['zip-rescan-pending','generation-advertised']);
      } else armZipRescan();
    }, ZIP_RESCAN_DELAY_MS);
  }
  function scheduleZipRescan(assistant) {
    if (ui.zipRescanTimer) clearTimeout(ui.zipRescanTimer);
    ui.zipRescanTimer = null;
    if (!settings.autoZip || !assistant) return;
    const now = Date.now(), delay = normalizeFileDelaySeconds(settings.fileDelaySeconds) * 1_000;
    state.zipCapture.pending = { assistantId: assistant.id, pathname: location.pathname, passes: 0, startedAt: nowIso(), deadlineAtT: now + Math.max(45_000, delay + FILE_FAILURE_RETRY_DELAY_MS + 20_000) };
    armZipRescan();
  }
  // @QOMRADE-CHUNK id=48.resilience title="Opt-in old-turn DOM trimming and hourly safe refresh/resume"
  function boundedReceipt(list, row, limit = 24) {
    list.push(row);
    if (list.length > limit) list.splice(0, list.length - limit);
    return row;
  }
  function noteMaintenanceBlock(bucket, blocked) {
    const at = nowIso();
    if (bucket.lastBlocked === blocked) bucket.blockedStreak = Math.max(0, Number(bucket.blockedStreak) || 0) + 1;
    else {
      bucket.lastBlocked = blocked;
      bucket.blockedStreak = 1;
      bucket.blockedSince = at;
      bucket.blockerChanges = Math.max(0, Number(bucket.blockerChanges) || 0) + 1;
    }
    return { at, streak: bucket.blockedStreak, since: bucket.blockedSince };
  }
  function clearMaintenanceBlock(bucket) {
    bucket.lastBlocked = null;
    bucket.blockedStreak = 0;
    bucket.blockedSince = null;
    if ('retryDelayMs' in bucket) bucket.retryDelayMs = 0;
  }
  function composerAttachmentObservation(composer = findComposer()) {
    if (!composer) return { present: false, count: 0, names: [], root: null };
    const root = composer.closest('form') || composer.parentElement || document;
    const container = q('[data-composer-attachments]', root);
    const nodes = [];
    if (container) {
      for (const child of Array.from(container.children || [])) {
        if (child.matches?.('[data-visible-attachments]') || q('[data-visible-attachments],button[aria-label^="Remove " i],[data-file-name],[data-filename]', child)) nodes.push(child);
      }
    }
    for (const control of qa('button[aria-label^="Remove " i]', root)) {
      if (!nodes.some(node => node === control || node.contains(control))) nodes.push(control);
    }
    const names = [...new Set(nodes.flatMap(node => {
      const values = [node.getAttribute?.('data-file-name'), node.getAttribute?.('data-filename'), node.getAttribute?.('aria-label')];
      for (const nested of qa('[data-file-name],[data-filename],button[aria-label^="Remove " i]', node).slice(0, 8)) values.push(nested.getAttribute('data-file-name'), nested.getAttribute('data-filename'), nested.getAttribute('aria-label'));
      return values.map(value => normalizeCompactText(String(value || '')).replace(/^(?:Remove|Delete)\s+/i, '')).filter(Boolean);
    }))].slice(0, 12);
    return { present: nodes.length > 0, count: nodes.length, names, root: container || null };
  }
  function turnTrimUnit(turn) {
    if (!turn?.element) return null;
    const element = turn.element;
    const group = element.closest?.('[data-content-search-turn-key]');
    const classic = element.closest?.('[data-testid^="conversation-turn-"]');
    const unit = group || classic || element;
    if (!unit || unit === document.documentElement || unit === document.body || unit === document.querySelector('main')) return null;
    if (ui.host && (unit === ui.host || unit.contains(ui.host))) return null;
    const composer = findComposer();
    if (composer && (unit === composer || unit.contains(composer))) return null;
    return unit;
  }
  function domTrimProtectedTurnIds() {
    const ids = new Set([state.baselineAssistantId, state.latestAssistantId]);
    const active = state.activeSend;
    if (active) for (const value of [active.userTurnId, active.assistantTurnId, active.baselineAssistantId]) if (value) ids.add(value);
    const entry = state.faultRecovery.ledger.find(item => item.key === state.faultRecovery.activeKey);
    for (const value of entry?.userIds || []) if (value) ids.add(value);
    if (state.zipCapture.pending?.assistantId) ids.add(state.zipCapture.pending.assistantId);
    return ids;
  }
  function domTrimPlan() {
    invalidateTurnCache('dom-trim-plan');
    const turns = materializedTurns().filter(turn => turn.role === 'user' || turn.role === 'assistant');
    const cutoff = Math.max(0, turns.length - DOM_TRIM_KEEP_LOGICAL_TURNS);
    const protectedIds = domTrimProtectedTurnIds();
    const units = new Map();
    turns.forEach((turn, index) => {
      const unit = turnTrimUnit(turn);
      if (!unit) return;
      const row = units.get(unit) || { unit, turns: [], first: index, last: index };
      row.turns.push(turn); row.first = Math.min(row.first, index); row.last = Math.max(row.last, index);
      units.set(unit, row);
    });
    const candidates = [...units.values()].filter(row => row.last < cutoff
      && row.turns.every(turn => !protectedIds.has(turn.id))
      && row.unit.isConnected
      && !q('[data-testid="stop-button"],button[aria-label^="Stop" i]', row.unit));
    return { turns, cutoff, candidates, protectedIds: [...protectedIds].filter(Boolean) };
  }
  function domTrimBlocker() {
    if (!settings.trimOldTurns) return 'disabled';
    if (!state.running) return 'stopped';
    if (state.paused) return 'paused';
    if (state.quarantine) return 'quarantined';
    if (pauseForHidden() && document.hidden) return 'hidden-policy-hold';
    if (state.tickBusy) return 'controller-busy';
    if (state.effectControl.active) return 'effect-in-flight';
    if (panelEditorFocused()) return 'operator-editing-qomrade';
    if (findStopButton()) return 'generation-advertised';
    if (visibleDialogObservation().blocking) return 'dialog-visible';
    if (continuationObservation().available) return 'continuation-visible';
    const composer = findComposer();
    if (!composer) return 'composer-unavailable';
    if (!composerIsEmpty(composer)) return 'composer-not-empty';
    if (composerAttachmentObservation(composer).present) return 'composer-attachment-present';
    if (state.domTrim.lastAt && Date.now() - Date.parse(state.domTrim.lastAt) < DOM_TRIM_MIN_INTERVAL_MS) return 'minimum-interval';
    return null;
  }
  function domTrimRetryDelay(blocked) {
    if (blocked === 'controller-busy' || blocked === 'effect-in-flight') return DOM_TRIM_TRANSIENT_RETRY_MS;
    if (blocked === 'composer-unavailable') return AUTO_REFRESH_RETRY_MS;
    if (blocked === 'minimum-interval') {
      const elapsed = state.domTrim.lastAt ? Date.now() - Date.parse(state.domTrim.lastAt) : DOM_TRIM_MIN_INTERVAL_MS;
      return Math.max(1_000, DOM_TRIM_MIN_INTERVAL_MS - elapsed);
    }
    if (blocked === 'generation-advertised') return null;
    if (['hidden-policy-hold','operator-editing-qomrade','dialog-visible','continuation-visible','composer-not-empty','composer-attachment-present'].includes(blocked)) return DOM_TRIM_STATIC_RETRY_MS;
    return null;
  }
  function domTrimSnapshot() {
    const nextAttemptAt = state.domTrim.nextAttemptAt || 0;
    return { ...state.domTrim, enabled: settings.trimOldTurns, keepLogicalTurns: DOM_TRIM_KEEP_LOGICAL_TURNS,
      nextAttemptAt: nextAttemptAt || null, nextAttemptIso: nextAttemptAt ? new Date(nextAttemptAt).toISOString() : null,
      timerActive: !!ui.domTrimTimer, receipts: state.domTrim.receipts.slice(-24),
      counterScope: 'attempts/successes are restored lifetime totals; page* counters describe only this loaded page',
      retryPolicy: 'generation waits for reply/lifecycle edges; transient controller effects retry in 5s; operator/UI blockers retry no faster than 5m',
      restoration: 'removed React-owned nodes return only after a page refresh; disabling the checkbox prevents later trims but does not reconstruct removed nodes' };
  }
  function armDomTrim(delayMs = 1_000, origin = 'scheduled') {
    if (ui.domTrimTimer) clearTimeout(ui.domTrimTimer);
    ui.domTrimTimer = null;
    state.domTrim.nextAttemptAt = 0;
    if (!settings.trimOldTurns || !state.running || state.paused || state.quarantine) return;
    const delay = Math.max(0, Number(delayMs) || 0);
    state.domTrim.nextAttemptAt = Date.now() + delay;
    state.domTrim.retryMode = delay ? 'timer' : 'immediate-edge';
    ui.domTrimTimer = setTimeout(() => {
      ui.domTrimTimer = null;
      state.domTrim.nextAttemptAt = 0;
      attemptDomTrim(origin);
    }, delay);
  }
  function attemptDomTrim(origin = 'manual-check') {
    const terminalBarrier = conversationBarrierObservation();
    if (terminalBarrier.present) {
      stopForConversationTerminal(terminalBarrier, `dom-trim:${origin}`);
      return { ok: false, blocked: 'conversation-terminal' };
    }
    state.domTrim.attempts += 1;
    state.domTrim.pageAttempts += 1;
    const at = nowIso();
    const blocked = domTrimBlocker();
    if (blocked) {
      const block = noteMaintenanceBlock(state.domTrim, blocked);
      const retryDelayMs = domTrimRetryDelay(blocked);
      state.domTrim.retryMode = retryDelayMs == null ? 'surface-edge' : 'timer';
      state.domTrim.nextAttemptAt = retryDelayMs == null ? 0 : Date.now() + retryDelayMs;
      const receipt = boundedReceipt(state.domTrim.receipts, { at, origin, outcome: 'blocked', blocked, blockedStreak: block.streak, retryMode: state.domTrim.retryMode, retryDelayMs, nextAttemptAt: state.domTrim.nextAttemptAt || null });
      if (retryDelayMs == null) {
        state.domTrim.suppressedRetries += 1;
        clearDomTrimTimer();
        state.domTrim.retryMode = 'surface-edge';
      } else if (settings.trimOldTurns && state.running && !state.paused && !state.quarantine) {
        armDomTrim(retryDelayMs, `retry:${blocked}`);
      }
      return { ok: false, blocked, ...receipt };
    }
    clearMaintenanceBlock(state.domTrim);
    state.domTrim.nextAttemptAt = 0;
    state.domTrim.retryMode = null;
    captureSessionTurns(`before-dom-trim:${origin}`);
    const plan = domTrimPlan();
    if (!plan.candidates.length) {
      boundedReceipt(state.domTrim.receipts, { at, origin, outcome: 'nothing-to-trim', materializedTurns: plan.turns.length, keepLogicalTurns: DOM_TRIM_KEEP_LOGICAL_TURNS });
      return { ok: true, removedUnits: 0, removedLogicalTurns: 0 };
    }
    let removedUnits = 0, removedLogicalTurns = 0;
    for (const row of plan.candidates) {
      if (!row.unit.isConnected) continue;
      try {
        row.unit.remove();
        removedUnits += 1;
        removedLogicalTurns += row.turns.length;
      } catch (error) {
        recordPageError({ kind: 'dom-trim-error', message: String(error?.message || error), origin });
        break;
      }
    }
    invalidateTurnCache('dom-trim-complete');
    state.domTrim.lastAt = at;
    state.domTrim.lastReason = origin;
    state.domTrim.unitsRemoved += removedUnits;
    state.domTrim.logicalTurnsRemoved += removedLogicalTurns;
    state.domTrim.pageUnitsRemoved += removedUnits;
    state.domTrim.pageLogicalTurnsRemoved += removedLogicalTurns;
    if (removedUnits) { state.domTrim.successes += 1; state.domTrim.pageSuccesses += 1; }
    const receipt = boundedReceipt(state.domTrim.receipts, { at, origin, outcome: removedUnits ? 'trimmed' : 'no-connected-candidates', removedUnits, removedLogicalTurns,
      beforeLogicalTurns: plan.turns.length, keepLogicalTurns: DOM_TRIM_KEEP_LOGICAL_TURNS, protectedTurnIds: plan.protectedIds,
      removedTurnIds: plan.candidates.flatMap(row => row.turns.map(turn => turn.id)).filter(Boolean).slice(0, 24) });
    if (removedUnits) {
      logEvent('dom-trim', `Removed ${removedLogicalTurns} old rendered logical turns in ${removedUnits} DOM units; the newest ${DOM_TRIM_KEEP_LOGICAL_TURNS} logical turns and active custody were retained.`, receipt);
      persistContinuity('dom-trim');
      render();
    }
    return { ok: true, ...receipt };
  }
  function autoRefreshSnapshot() {
    const dueAt = state.autoRefresh.dueAt || 0;
    return { schema: state.autoRefresh.schema, enabled: settings.hourlyRefresh, intervalMs: autoRefreshIntervalMs(),
      dueAt: dueAt || null, dueIso: dueAt ? new Date(dueAt).toISOString() : null,
      retryAt: state.autoRefresh.retryAt || null, retryIso: state.autoRefresh.retryAt ? new Date(state.autoRefresh.retryAt).toISOString() : null,
      timerActive: !!ui.autoRefreshTimer, attempts: state.autoRefresh.attempts, reloads: state.autoRefresh.reloads,
      deferrals: state.autoRefresh.deferrals, lastAttemptAt: state.autoRefresh.lastAttemptAt, lastReloadAt: state.autoRefresh.lastReloadAt,
      lastBlocked: state.autoRefresh.lastBlocked, lastReadback: state.autoRefresh.lastReadback,
      restorePending: state.autoRefresh.restorePending, pendingResume: state.autoRefresh.pendingResume ? { nonce: state.autoRefresh.pendingResume.nonce, createdAt: state.autoRefresh.pendingResume.createdAt, expiresAt: state.autoRefresh.pendingResume.expiresAt } : null,
      blockedStreak: state.autoRefresh.blockedStreak, blockedSince: state.autoRefresh.blockedSince, blockerChanges: state.autoRefresh.blockerChanges, retryDelayMs: state.autoRefresh.retryDelayMs,
      pageAttempts: state.autoRefresh.pageAttempts, pageReloads: state.autoRefresh.pageReloads, pageDeferrals: state.autoRefresh.pageDeferrals,
      healingPending: state.autoRefresh.healingPending ? { ...state.autoRefresh.healingPending } : null,
      healingHistory: state.autoRefresh.healingHistory.slice(-8), healingReloads: state.autoRefresh.healingReloads,
      healingSuppressed: state.autoRefresh.healingSuppressed, lastHealingAt: state.autoRefresh.lastHealingAt,
      lastHealingKey: state.autoRefresh.lastHealingKey, lastFaultSurfaceKey: state.autoRefresh.lastFaultSurfaceKey,
      lastFaultSurfaceAt: state.autoRefresh.lastFaultSurfaceAt, restoreStartedAt: state.autoRefresh.restoreStartedAt || null,
      restoreDeadlineAt: state.autoRefresh.restoreDeadlineAt || null,
      receipts: state.autoRefresh.receipts.slice(-24),
      counterScope: 'attempts/reloads/deferrals are restored lifetime totals; page* counters describe only this loaded page',
      policy: 'operator-enabled safe refresh: selected interval plus one bounded healing refresh for a newly appeared historical/unowned pipeline-failure surface; exact conversation-stale or conversation-load-failed shell wording may heal while preserving active request custody; current owned generation failures keep fresh-message recovery; exact run resumes only from a source/conversation/prompt-bound one-shot ticket with confirmed per-tab readback' };
  }
  function clearDomTrimTimer() {
    if (ui.domTrimTimer) clearTimeout(ui.domTrimTimer);
    ui.domTrimTimer = null;
    state.domTrim.nextAttemptAt = 0;
  }
  function clearAutoRefreshTimer() {
    if (ui.autoRefreshTimer) clearTimeout(ui.autoRefreshTimer);
    ui.autoRefreshTimer = null;
  }
  function scheduleNextAutoRefresh(origin = 'scheduled', from = Date.now()) {
    clearAutoRefreshTimer();
    if (!settings.hourlyRefresh || !state.running || state.paused || state.quarantine) return;
    state.autoRefresh.scheduledAt = Date.now();
    state.autoRefresh.dueAt = Math.max(Date.now() + 1_000, Number(from) + autoRefreshIntervalMs());
    state.autoRefresh.retryAt = 0;
    boundedReceipt(state.autoRefresh.receipts, { at: nowIso(), origin, outcome: 'scheduled', dueAt: state.autoRefresh.dueAt, dueIso: new Date(state.autoRefresh.dueAt).toISOString() });
    armAutoRefresh(origin);
  }
  function armAutoRefresh(origin = 'armed') {
    clearAutoRefreshTimer();
    if (!settings.hourlyRefresh || !state.running || state.paused || state.quarantine) return;
    if (!state.autoRefresh.dueAt) state.autoRefresh.dueAt = Date.now() + autoRefreshIntervalMs();
    const healingEligibleAt = state.autoRefresh.healingPending ? Number(state.autoRefresh.healingPending.eligibleAt) || 0 : 0;
    const target = Math.max(state.autoRefresh.dueAt, state.autoRefresh.retryAt || 0, healingEligibleAt && state.autoRefresh.dueAt <= healingEligibleAt ? healingEligibleAt : 0);
    const delay = Math.max(250, target - Date.now());
    ui.autoRefreshTimer = setTimeout(() => {
      ui.autoRefreshTimer = null;
      void maybeAutoRefresh(origin);
    }, delay);
  }
  function autoRefreshBlocker({ healing = false } = {}) {
    if (!settings.hourlyRefresh) return 'disabled';
    if (!state.running) return 'stopped';
    if (state.paused) return 'paused';
    if (state.quarantine) return 'quarantined';
    if (pauseForHidden() && document.hidden) return 'hidden-policy-hold';
    if (state.tickBusy) return 'controller-busy';
    if (state.effectControl.active) return 'effect-in-flight';
    if (panelEditorFocused()) return 'operator-editing-qomrade';
    if (!isEligibleRoute()) return 'ineligible-route';
    if (state.anchorConversationId && conversationIdFromPath() && state.anchorConversationId !== conversationIdFromPath()) return 'conversation-changed';
    if (findStopButton()) return 'generation-advertised';
    if (visibleDialogObservation().blocking) return 'dialog-visible';
    if (continuationObservation().available) return 'continuation-visible';
    const composer = findComposer();
    if (!composer && !healing) return 'composer-unavailable';
    if (composer && !composerIsEmpty(composer)) return 'composer-not-empty';
    if (composer && composerAttachmentObservation(composer).present) return 'composer-attachment-present';
    if (state.zipCapture.pending) return 'zip-rescan-pending';
    return null;
  }
  function autoRefreshRetryDelay(blocked, streak = 1) {
    if (blocked === 'generation-advertised') return AUTO_REFRESH_GENERATION_RETRY_MS;
    if (blocked === 'controller-busy' || blocked === 'effect-in-flight') return AUTO_REFRESH_TRANSIENT_RETRY_MS;
    if (blocked === 'zip-rescan-pending') return 30_000;
    if (blocked === 'composer-unavailable') return AUTO_REFRESH_RETRY_MS;
    if (['hidden-policy-hold','operator-editing-qomrade','dialog-visible','continuation-visible','composer-not-empty','composer-attachment-present'].includes(blocked)) return AUTO_REFRESH_UI_RETRY_MS;
    if (blocked === 'persistence-unverified' || blocked === 'ticket-consume-unverified' || blocked === 'reload-call-failed') {
      return Math.min(AUTO_REFRESH_MAX_RETRY_MS, AUTO_REFRESH_RETRY_MS * (2 ** Math.min(4, Math.max(0, streak - 1))));
    }
    return AUTO_REFRESH_RETRY_MS;
  }
  function deferAutoRefresh(blocked, origin, outcome = 'deferred', extra = {}) {
    state.autoRefresh.deferrals += 1;
    state.autoRefresh.pageDeferrals += 1;
    const block = noteMaintenanceBlock(state.autoRefresh, blocked);
    const retryDelayMs = autoRefreshRetryDelay(blocked, block.streak);
    state.autoRefresh.retryDelayMs = retryDelayMs;
    state.autoRefresh.retryAt = Date.now() + retryDelayMs;
    const receipt = boundedReceipt(state.autoRefresh.receipts, { at: nowIso(), origin, outcome, blocked, blockedStreak: block.streak, retryDelayMs, retryAt: state.autoRefresh.retryAt, ...extra });
    armAutoRefresh(`retry:${blocked}`);
    return receipt;
  }
  function wakeOverdueAutoRefresh(origin, resetBlockers = []) {
    if (!settings.hourlyRefresh || !state.running || state.paused || state.quarantine || !state.autoRefresh.dueAt || Date.now() < state.autoRefresh.dueAt) return false;
    if (resetBlockers.includes(state.autoRefresh.lastBlocked)) {
      state.autoRefresh.retryAt = 0;
      state.autoRefresh.retryDelayMs = 0;
    }
    void maybeAutoRefresh(origin);
    return true;
  }
  function compactHealingHistory(now = Date.now()) {
    state.autoRefresh.healingHistory = (Array.isArray(state.autoRefresh.healingHistory) ? state.autoRefresh.healingHistory : [])
      .filter(row => row && typeof row.key === 'string' && Number.isFinite(Number(row.at)) && now - Number(row.at) <= AUTO_REFRESH_HEALING_WINDOW_MS)
      .slice(-AUTO_REFRESH_HEALING_LIMIT);
    return state.autoRefresh.healingHistory;
  }
  function cancelHealingRefresh(reason = 'surface-cleared') {
    const pending = state.autoRefresh.healingPending;
    if (!pending) return false;
    state.autoRefresh.healingPending = null;
    state.autoRefresh.lastFaultSurfaceKey = null;
    const ordinaryDueAt = Number(pending.ordinaryDueAt) || (Date.now() + autoRefreshIntervalMs());
    state.autoRefresh.dueAt = Math.max(Date.now() + 1_000, ordinaryDueAt);
    state.autoRefresh.retryAt = 0;
    state.autoRefresh.retryDelayMs = 0;
    boundedReceipt(state.autoRefresh.receipts, { at: nowIso(), origin: 'pipeline-failure-edge', outcome: 'healing-cancelled', reason, key: pending.key, dueAt: state.autoRefresh.dueAt });
    armAutoRefresh('healing-cancelled');
    return true;
  }
  function requestHealingRefresh(surface, origin = 'pipeline-science-edge') {
    if (!surface || !settings.hourlyRefresh || !state.running || state.paused || state.quarantine || state.terminalStop) return false;
    const now = Date.now();
    state.autoRefresh.lastFaultSurfaceKey = surface.key;
    state.autoRefresh.lastFaultSurfaceAt = new Date(now).toISOString();
    if (state.activeSend && !surface.allowActiveSend) {
      state.autoRefresh.healingSuppressed += 1;
      boundedReceipt(state.autoRefresh.receipts, { at: nowIso(), origin, outcome: 'healing-suppressed', reason: 'current-request-recovery-has-priority', key: surface.key, surface });
      return false;
    }
    const pending = state.autoRefresh.healingPending;
    if (pending && pending.key === surface.key) return true;
    const recent = compactHealingHistory(now);
    const sameRecent = recent.slice().reverse().find(row => row.key === surface.key && now - Number(row.at) < AUTO_REFRESH_HEALING_DEDUP_MS);
    const lastAt = sameRecent ? Number(sameRecent.at) : state.autoRefresh.lastHealingKey === surface.key && state.autoRefresh.lastHealingAt ? Date.parse(state.autoRefresh.lastHealingAt) : 0;
    if (lastAt && now - lastAt < AUTO_REFRESH_HEALING_DEDUP_MS) {
      state.autoRefresh.healingSuppressed += 1;
      boundedReceipt(state.autoRefresh.receipts, { at: nowIso(), origin, outcome: 'healing-suppressed', reason: 'same-surface-dedup-window', key: surface.key, lastHealingAt: new Date(lastAt).toISOString() });
      return false;
    }
    if (recent.length >= AUTO_REFRESH_HEALING_LIMIT) {
      state.autoRefresh.healingSuppressed += 1;
      boundedReceipt(state.autoRefresh.receipts, { at: nowIso(), origin, outcome: 'healing-suppressed', reason: 'bounded-healing-budget', key: surface.key, recent });
      return false;
    }
    const ordinaryDueAt = pending ? Number(pending.ordinaryDueAt) || state.autoRefresh.dueAt : state.autoRefresh.dueAt || (now + autoRefreshIntervalMs());
    const eligibleAt = now + AUTO_REFRESH_HEALING_SETTLE_MS;
    const domSnapshotId = surface.domSnapshotId || surface.evidence?.domSnapshotId || captureDomishEvent('healing-refresh-armed', {
      reason: surface.reason,
      severity: 'warn',
      origin,
      relatedIds: [surface.key],
      key: fnv1a64(`healing-refresh|${surface.key}`),
      context: surface.evidence,
    });
    state.autoRefresh.healingPending = {
      schema: 'qomrade.auto-refresh-healing.v1', key: surface.key, reason: surface.reason,
      firstSeenAt: new Date(now).toISOString(), firstSeenT: now, eligibleAt,
      ordinaryDueAt, origin, allowActiveSend: !!surface.allowActiveSend, maintenanceKind: surface.maintenanceKind || null,
      evidence: { ...surface.evidence, domSnapshotId }, domSnapshotId,
    };
    state.autoRefresh.dueAt = eligibleAt;
    state.autoRefresh.retryAt = 0;
    state.autoRefresh.retryDelayMs = 0;
    clearMaintenanceBlock(state.autoRefresh);
    boundedReceipt(state.autoRefresh.receipts, { at: nowIso(), origin, outcome: 'healing-armed', key: surface.key, reason: surface.reason, eligibleAt, ordinaryDueAt, evidence: surface.evidence });
    logEvent('auto-refresh-healing-armed', 'A newly appeared page-shell maintenance or historical/unowned pipeline surface armed one bounded Safe refresh.', { key: surface.key, reason: surface.reason, eligibleAt, evidence: surface.evidence });
    armAutoRefresh('pipeline-failure-edge');
    render();
    return true;
  }
  function pipelineFailureSurfaceFromPulse(pulse) {
    if (!pulse || !state.running || state.paused || state.quarantine) return null;
    const systemRows = (pulse.system || []).map(item => ({
      item,
      typed: classifyPipelineFailureText(item.text || ''),
      maintenance: classifyPipelineMaintenanceText(item.text || ''),
    }));
    const systemFaults = systemRows.filter(row => row.typed && row.typed.kind === 'generation-error');
    const systemMaintenance = systemRows.filter(row => row.maintenance);
    const retry = pulse.retry || {};
    const retryRows = (retry.contexts || []).map(context => ({
      context,
      typed: context.typed || classifyPipelineFailureText(context.text || ''),
      maintenance: context.maintenance || classifyPipelineMaintenanceText(context.text || ''),
    }));
    const retryContextFaults = retryRows.filter(row => row.typed && row.typed.kind === 'generation-error');
    const retryMaintenance = retryRows.filter(row => row.maintenance);
    const maintenanceRows = [...systemMaintenance, ...retryMaintenance];
    const exactMaintenance = maintenanceRows.find(row => maintenanceAllowsActiveRequestRefresh(row.maintenance?.maintenanceKind));
    const maintenanceKind = exactMaintenance?.maintenance?.maintenanceKind || null;
    const outsideRetry = Number(retry.outsideLatestAssistantCount) > 0 || (!!retry.available && !pulse.assistant);
    const currentTypedFault = !!(pulse.error && pulse.error.kind === 'generation-error');
    const allowActiveSend = !!exactMaintenance && !currentTypedFault && !systemFaults.length && !retryContextFaults.length;
    if (state.activeSend && !allowActiveSend) return null;
    if (!systemFaults.length && !retryContextFaults.length && !outsideRetry && !currentTypedFault && !maintenanceRows.length) return null;
    const reason = maintenanceKind === 'conversation-stale' ? 'conversation-stale-shell'
      : maintenanceKind === 'conversation-load-failed' ? 'conversation-load-failed-shell'
        : systemFaults.length ? `historical-${systemFaults[0].typed.faultKind || 'generation-error'}`
          : retryContextFaults.length ? `historical-${retryContextFaults[0].typed.faultKind || 'generation-error'}`
            : currentTypedFault ? `unowned-${pulse.error.faultKind || 'generation-error'}` : 'historical-retry-control';
    const evidence = {
      reason,
      phase: pulse.phase,
      error: pulse.error || null,
      maintenanceSurfaces: maintenanceRows.map(row => ({
        maintenanceKind: row.maintenance.maintenanceKind,
        text: trunc(row.maintenance.text || row.item?.text || row.context?.text || '', 640),
        source: row.item ? 'system-surface' : 'retry-card-context',
        role: row.item?.role || null,
        host: row.context?.host || null,
        turn: row.context?.turn || null,
      })).slice(0, MAX_RETRY_CONTEXTS),
      systemFaults: systemFaults.map(row => ({ faultKind: row.typed.faultKind, text: trunc(row.typed.text || row.item.text || '', 640), role: row.item.role || null })).slice(0, MAX_RETRY_CONTEXTS),
      retry: {
        available: !!retry.available,
        count: Number(retry.count) || 0,
        outsideLatestAssistantCount: Number(retry.outsideLatestAssistantCount) || 0,
        labels: (retry.labels || []).slice(0, MAX_RETRY_CONTEXTS),
        contexts: retryRows.map(row => ({
          text: trunc(row.context.text || '', 640),
          textHash: row.context.textHash || null,
          faultKind: row.typed?.faultKind || null,
          maintenanceKind: row.maintenance?.maintenanceKind || null,
          labelVisible: row.context.labelVisible,
          labelComplete: row.context.labelComplete,
          host: row.context.host || null,
          turn: row.context.turn || null,
        })).slice(0, MAX_RETRY_CONTEXTS),
      },
      assistant: pulse.assistant ? { id: pulse.assistant.id, ordinal: pulse.assistant.ordinal } : null,
      activeTransactionId: pulse.activeTransactionId || null,
      allowActiveSend,
      observation: 'literal Retry-card context is retained; exact page-shell maintenance wording is Safe-refresh evidence only, never Retry or resend authority',
    };
    evidence.environment = {
      hidden: document.hidden,
      visibility: document.visibilityState,
      focused: document.hasFocus(),
      timeSinceLastSendMs: state.lastSendAt ? Math.max(0, Date.now() - state.lastSendAt) : null,
      backgroundMode: state.background.current?.mode || null,
      lastRecoveryDecision: state.faultRecovery.lastDecision || null,
      lastRecoveryOutcome: state.faultRecovery.ledger.slice(-1)[0]?.outcomes?.slice(-1)[0] || null,
    };
    const key = maintenanceAllowsActiveRequestRefresh(maintenanceKind)
      ? fnv1a64(JSON.stringify([conversationIdFromPath(), maintenanceKind]))
      : fnv1a64(JSON.stringify([conversationIdFromPath(), reason, evidence.maintenanceSurfaces, evidence.systemFaults, evidence.retry]));
    return { key, reason, allowActiveSend, maintenanceKind, evidence };
  }
  function considerHealingRefreshFromScienceEdge(pulse, origin = 'pipeline-science-edge') {
    if (!settings.hourlyRefresh || !state.running || state.paused || state.quarantine) return false;
    const surface = pipelineFailureSurfaceFromPulse(pulse);
    if (!surface) {
      if (state.autoRefresh.healingPending && state.autoRefresh.lastFaultSurfaceKey) cancelHealingRefresh('pipeline-failure-surface-cleared');
      state.autoRefresh.lastFaultSurfaceKey = null;
      return false;
    }
    return requestHealingRefresh(surface, origin);
  }
  function visiblePageShellMaintenanceSurface(origin = 'controller-observation') {
    const shellHealth = observePageShellHealth(origin, { capture: true });
    if (shellHealth.degraded) return { ...shellHealthSurface(shellHealth), origin };
    const assistant = latestAssistantTurn();
    const retry = retryObservation(assistant);
    const pulse = {
      phase: state.phase,
      activeTransactionId: state.activeSend?.id || null,
      assistant: assistant ? { id: assistant.id, ordinal: assistant.ordinal } : null,
      error: null,
      system: compactSystemScienceSurface(),
      retry: retry ? {
        available: !!retry.available,
        count: retry.controls ? retry.controls.length : 0,
        outsideLatestAssistantCount: (retry.controls || []).filter(row => !row.insideLatestAssistant).length,
        labels: (retry.controls || []).map(row => trunc(normalizeCompactText(`${row.text || ''} ${row.ariaLabel || ''} ${row.testId || ''}`), 120)).filter(Boolean).slice(0, MAX_RETRY_CONTEXTS),
        contexts: (retry.controls || []).map(row => row.context).filter(Boolean).slice(0, MAX_RETRY_CONTEXTS),
      } : null,
    };
    const surface = pipelineFailureSurfaceFromPulse(pulse);
    return surface && maintenanceAllowsActiveRequestRefresh(surface.maintenanceKind) ? { ...surface, origin } : null;
  }
  function pageShellMaintenanceLabel(surface) {
    if (surface?.maintenanceKind === 'conversation-stale') return 'ChatGPT says this conversation is stale';
    if (surface?.maintenanceKind === 'conversation-load-failed') return 'ChatGPT could not load this conversation';
    if (surface?.maintenanceKind === 'chatgpt-shell-unstyled') return 'ChatGPT loaded as an unstyled native-control shell';
    if (surface?.maintenanceKind === 'chatgpt-shell-hydration-stalled') return 'ChatGPT is stuck on a partial Loading profile shell';
    return 'ChatGPT is showing a degraded application shell';
  }
  function holdForPageShellMaintenance(surface, origin = 'controller-observation') {
    if (!surface) return false;
    const armed = settings.hourlyRefresh ? requestHealingRefresh(surface, origin) : false;
    const label = pageShellMaintenanceLabel(surface);
    const reason = armed
      ? `${label}. Safe refresh is settling exact shell evidence before one ticketed reload; qomrade will not Send or click Retry.`
      : settings.hourlyRefresh
        ? `${label}. qomrade will not Send into this surface; the bounded repair is unavailable or was already used. Use the page Retry control or reload this tab manually.`
        : `${label}. qomrade will not Send into this surface. Enable Safe refresh, use the page Retry control, or reload this tab manually.`;
    setPhase('SURFACE_HOLD', reason);
    scheduleTick(Math.max(replyPollMs(), 15_000), `${surface.maintenanceKind || 'page-shell'} maintenance hold`);
    return true;
  }
  function compactActiveSendForRefresh(active) {
    if (!active) return null;
    return {
      schema: active.schema || 'qomrade.send-transaction.v2', id: active.id || null, startedAt: active.startedAt || null,
      clickedAt: active.clickedAt || null, clickMode: active.clickMode || null, promptHash: active.promptHash || null,
      promptChars: active.promptChars == null ? null : active.promptChars, userTurnId: active.userTurnId || null,
      userTurnOrdinal: active.userTurnOrdinal == null ? null : active.userTurnOrdinal, userAdoptedAt: active.userAdoptedAt || null,
      baselineAssistantId: active.baselineAssistantId || state.baselineAssistantId || null, assistantTurnId: active.assistantTurnId || null,
      model: active.model || null, modelPolicy: active.modelPolicy || state.modelGate.runPolicy || MODEL_POLICY_SMART_PRO,
      modelTarget: active.modelTarget || (state.modelGate.target ? { ...state.modelGate.target } : null),
      modelPreference: active.modelPreference || state.modelGate.runPreference || '5.6-first',
      recoveryRootKey: active.recoveryRootKey || null, recoveryParentId: active.recoveryParentId || null,
      successorUserIds: Array.isArray(active.successorUserIds) ? active.successorUserIds.slice(-8) : [], outcome: active.outcome || null,
    };
  }
  function buildAutoRefreshResumeTicket() {
    captureSessionTurns('hourly-refresh-preflight');
    const now = Date.now();
    return {
      schema: 'qomrade.auto-refresh-resume.v1', sourceId: QOMRADE_SOURCE_ID, version: VERSION,
      nonce: `refresh-${now.toString(36)}-${Math.random().toString(36).slice(2)}`,
      createdAt: new Date(now).toISOString(), createdT: now, expiresAt: new Date(now + AUTO_REFRESH_TICKET_MAX_AGE_MS).toISOString(), expiresT: now + AUTO_REFRESH_TICKET_MAX_AGE_MS,
      conversationId: state.anchorConversationId || conversationIdFromPath(), pathname: location.pathname,
      promptHash: fnv1a64(state.runPrompt), promptChars: state.runPrompt.length,
      nextRefreshAt: now + autoRefreshIntervalMs(),
      maintenanceTrigger: state.autoRefresh.healingPending ? { kind: 'pipeline-failure-edge', ...state.autoRefresh.healingPending } : { kind: 'interval' },
      sessionArchive: sessionArchivePersistentSnapshot(),
      domForensics: domForensicsPersistentSnapshot(),
      run: {
        startedAt: state.startedAt, lastSendAt: state.lastSendAt, nextSendAt: state.nextSendAt, waitingSince: state.waitingSince,
        phase: state.phase, phaseReason: state.phaseReason, sends: state.sends, completedReplies: state.completedReplies,
        startAttempts: state.startAttempts, startAccepted: state.startAccepted, startRefused: state.startRefused,
        startTransaction: state.startTransaction ? JSON.parse(JSON.stringify(state.startTransaction)) : null,
        adoptedWithoutClick: state.adoptedWithoutClick, preClickAdvanceHolds: state.preClickAdvanceHolds,
        composerAttemptCount: state.composerAttemptCount,
        modelPolicy: state.modelGate.runPolicy || MODEL_POLICY_SMART_PRO,
        modelTarget: state.modelGate.target ? { ...state.modelGate.target } : null,
        modelPreference: state.modelGate.runPreference || '5.6-first',
        baselineAssistantId: state.baselineAssistantId, activeSend: compactActiveSendForRefresh(state.activeSend),
      },
      authority: 'operator-enabled safe refresh on this exact tab; selected interval or one bounded stale-failure/shell-maintenance edge; one-shot source/conversation/prompt-bound resume only',
    };
  }
  let autoRefreshWriteBusy = false;
  let autoRefreshWriteQueued = false;
  async function persistAutoRefreshBarrier(reason, expectedTicket) {
    if (autoRefreshWriteBusy || recoveryWriteBusy || typeof GM_getTab !== 'function' || typeof GM_saveTab !== 'function') return false;
    autoRefreshWriteBusy = true;
    const marker = `auto-refresh-${Date.now().toString(36)}-${Math.random().toString(36).slice(2)}`;
    const record = buildTabRecord(reason).record;
    record.autoRefreshResume = expectedTicket == null ? null : JSON.parse(JSON.stringify(expectedTicket));
    record.autoRefreshWriteWitness = marker;
    const started = performance.now();
    let verified = false, saveRejected = false;
    try {
      state.persistence.writes += 1;
      state.persistence.lastWriteAt = nowIso();
      state.persistence.lastWriteReason = reason;
      state.persistence.lastWriteBytes = utf8Bytes(JSON.stringify(record));
      state.persistence.maxWriteBytes = Math.max(state.persistence.maxWriteBytes, state.persistence.lastWriteBytes);
      const result = GM_saveTab(record);
      if (result && typeof result.then === 'function') result.catch(() => { saveRejected = true; });
      verified = await new Promise(resolve => {
        let done = false, retryTimer = null;
        const finish = ok => { if (done) return; done = true; clearTimeout(timeout); if (retryTimer) clearTimeout(retryTimer); resolve(!!ok); };
        const timeout = setTimeout(() => finish(false), 3_000);
        const read = () => {
          if (done || saveRejected) return finish(false);
          try {
            GM_getTab(value => {
              if (done || saveRejected) return finish(false);
              const actual = value?.autoRefreshResume ?? null;
              const ticketMatch = JSON.stringify(actual) === JSON.stringify(record.autoRefreshResume ?? null);
              if (value?.sourceId === QOMRADE_SOURCE_ID && value?.autoRefreshWriteWitness === marker && ticketMatch) return finish(true);
              retryTimer = setTimeout(read, 100);
            });
          } catch (_) { finish(false); }
        };
        read();
      });
    } catch (error) {
      state.persistence.writeErrors += 1;
      recordPageError({ kind: 'auto-refresh-persistence-error', message: String(error?.message || error), reason });
    } finally {
      state.autoRefresh.lastReadback = { at: nowIso(), reason, marker, verified, elapsedMs: Math.round(performance.now() - started) };
      autoRefreshWriteBusy = false;
      if (autoRefreshWriteQueued || recoveryWriteQueued) {
        autoRefreshWriteQueued = false;
        if (!state.boot.tabRead.pendingLate || state.boot.operatorTouched) {
          recoveryWriteQueued = false;
          saveTabRecord('auto-refresh-write-reconcile');
        }
      }
    }
    return verified;
  }
  function performHourlyReload(ticket) {
    if (TEST_MODE && typeof window.__QOMRADE_TEST_RELOAD__ === 'function') return window.__QOMRADE_TEST_RELOAD__(JSON.parse(JSON.stringify(ticket)));
    location.reload();
  }
  async function maybeAutoRefresh(origin = 'timer') {
    const terminalBarrier = conversationBarrierObservation();
    if (terminalBarrier.present) {
      stopForConversationTerminal(terminalBarrier, `auto-refresh:${origin}`);
      return false;
    }
    const healing = state.autoRefresh.healingPending && Date.now() >= (Number(state.autoRefresh.healingPending.eligibleAt) || 0);
    if (state.autoRefresh.healingPending && state.activeSend && !state.autoRefresh.healingPending.allowActiveSend) {
      state.autoRefresh.healingSuppressed += 1;
      cancelHealingRefresh('current-request-custody-acquired');
      boundedReceipt(state.autoRefresh.receipts, { at: nowIso(), origin, outcome: 'healing-suppressed', reason: 'current-request-recovery-has-priority' });
      return false;
    }
    if (state.autoRefresh.healingPending && !healing) {
      armAutoRefresh(origin);
      return false;
    }
    if (state.autoRefresh.inFlight || !state.autoRefresh.dueAt || Date.now() < state.autoRefresh.dueAt || Date.now() < (state.autoRefresh.retryAt || 0)) {
      armAutoRefresh(origin);
      return false;
    }
    state.autoRefresh.attempts += 1;
    state.autoRefresh.pageAttempts += 1;
    state.autoRefresh.lastAttemptAt = nowIso();
    const blocked = autoRefreshBlocker({ healing: !!healing });
    if (blocked) {
      const receipt = deferAutoRefresh(blocked, origin);
      logEvent('auto-refresh-deferred', `Safe refresh deferred: ${blocked}.`, receipt);
      render();
      return false;
    }
    clearMaintenanceBlock(state.autoRefresh);
    state.autoRefresh.retryAt = 0;
    state.autoRefresh.inFlight = true;
    const authorityEpoch = state.effectControl.epoch;
    const ticket = buildAutoRefreshResumeTicket();
    state.autoRefresh.resumeTicket = ticket;
    const refreshReason = healing ? 'pipeline-failure-healing-refresh-armed' : 'hourly-refresh-armed';
    const verified = await persistAutoRefreshBarrier(refreshReason, ticket);
    if (!verified) {
      state.autoRefresh.resumeTicket = null;
      state.autoRefresh.inFlight = false;
      const receipt = deferAutoRefresh('persistence-unverified', origin);
      logEvent('auto-refresh-deferred', 'Safe refresh ticket could not be confirmed by exact per-tab readback; no reload occurred.', { ...state.autoRefresh.lastReadback, ...receipt });
      render();
      return false;
    }
    const cancelled = state.effectControl.epoch !== authorityEpoch || !state.running || state.paused || state.quarantine || !settings.hourlyRefresh || !isEligibleRoute()
      || (state.anchorConversationId && conversationIdFromPath() !== state.anchorConversationId);
    if (cancelled) {
      state.autoRefresh.resumeTicket = null;
      state.autoRefresh.inFlight = false;
      state.autoRefresh.lastBlocked = 'authority-revoked-after-ticket-write';
      await persistAutoRefreshBarrier('hourly-refresh-cancelled', null);
      boundedReceipt(state.autoRefresh.receipts, { at: nowIso(), origin, outcome: 'cancelled', blocked: state.autoRefresh.lastBlocked });
      logEvent('auto-refresh-cancelled', 'Safe refresh authority changed while its ticket was being confirmed; no reload occurred.', { origin, authorityEpoch, currentEpoch: state.effectControl.epoch });
      if (settings.hourlyRefresh && state.running && !state.paused && !state.quarantine) { state.autoRefresh.retryAt = Date.now() + AUTO_REFRESH_RETRY_MS; armAutoRefresh('cancelled-recheck'); }
      render();
      return false;
    }
    if (healing && state.activeSend && !state.autoRefresh.healingPending?.allowActiveSend) {
      state.autoRefresh.resumeTicket = null;
      state.autoRefresh.inFlight = false;
      await persistAutoRefreshBarrier('pipeline-failure-healing-cancelled-current-request', null);
      state.autoRefresh.healingSuppressed += 1;
      cancelHealingRefresh('current-request-custody-acquired-during-ticket-readback');
      boundedReceipt(state.autoRefresh.receipts, { at: nowIso(), origin, outcome: 'healing-suppressed', reason: 'current-request-recovery-has-priority-after-readback' });
      render();
      return false;
    }
    if (healing && state.activeSend && state.autoRefresh.healingPending?.allowActiveSend) {
      const currentOwnedFault = classifyVisibleError(latestAssistantTurn());
      if (currentOwnedFault && currentOwnedFault.kind === 'generation-error') {
        state.autoRefresh.resumeTicket = null;
        state.autoRefresh.inFlight = false;
        await persistAutoRefreshBarrier('pipeline-failure-healing-cancelled-current-owned-fault', null);
        state.autoRefresh.healingSuppressed += 1;
        cancelHealingRefresh('current-owned-generation-fault-takes-priority');
        boundedReceipt(state.autoRefresh.receipts, { at: nowIso(), origin, outcome: 'healing-suppressed', reason: 'current-owned-generation-fault-takes-priority' });
        render();
        return false;
      }
    }
    const finalTerminalBarrier = conversationBarrierObservation();
    if (finalTerminalBarrier.present) {
      state.autoRefresh.resumeTicket = null;
      state.autoRefresh.inFlight = false;
      await persistAutoRefreshBarrier('hourly-refresh-terminal-stop', null);
      stopForConversationTerminal(finalTerminalBarrier, `auto-refresh-final:${origin}`);
      return false;
    }
    const finalBlocked = autoRefreshBlocker({ healing: !!healing });
    if (finalBlocked) {
      state.autoRefresh.resumeTicket = null;
      state.autoRefresh.inFlight = false;
      await persistAutoRefreshBarrier('hourly-refresh-final-preflight-deferred', null);
      const receipt = deferAutoRefresh(finalBlocked, origin, 'deferred-after-readback');
      logEvent('auto-refresh-deferred', `Safe refresh final preflight deferred: ${finalBlocked}. No reload occurred.`, receipt);
      render();
      return false;
    }
    state.autoRefresh.lastReloadAt = nowIso();
    if (healing && state.autoRefresh.healingPending) {
      const row = { key: state.autoRefresh.healingPending.key, at: Date.now(), reason: state.autoRefresh.healingPending.reason };
      state.autoRefresh.healingHistory.push(row);
      compactHealingHistory();
      state.autoRefresh.healingReloads += 1;
      state.autoRefresh.lastHealingAt = state.autoRefresh.lastReloadAt;
      state.autoRefresh.lastHealingKey = row.key;
    }
    boundedReceipt(state.autoRefresh.receipts, { at: state.autoRefresh.lastReloadAt, origin, outcome: healing ? 'healing-reload-committed' : 'reload-committed', nonce: ticket.nonce, nextRefreshAt: ticket.nextRefreshAt, maintenanceTrigger: ticket.maintenanceTrigger });
    logEvent('auto-refresh-committed', healing ? 'Committed one bounded stale-failure healing refresh after exact ticket readback.' : 'Committed the opt-in interval page refresh after exact ticket readback. The new page may resume only this source, conversation, and prompt.', { origin, nonce: ticket.nonce, nextRefreshAt: ticket.nextRefreshAt, maintenanceTrigger: ticket.maintenanceTrigger });
    revokeEffectAuthority('hourly-auto-refresh');
    clearControllerTimer('hourly auto refresh committed');
    clearDomTrimTimer();
    clearAutoRefreshTimer();
    try { performHourlyReload(ticket); }
    catch (error) {
      state.autoRefresh.inFlight = false;
      const receipt = deferAutoRefresh('reload-call-failed', origin, 'reload-call-failed');
      recordPageError({ kind: 'auto-refresh-reload-error', message: String(error?.message || error), receipt });
      return false;
    }
    return true;
  }
  function validAutoRefreshTicket(ticket) {
    const now = Date.now();
    if (!ticket || ticket.schema !== 'qomrade.auto-refresh-resume.v1') return { ok: false, reason: 'schema' };
    if (ticket.sourceId !== QOMRADE_SOURCE_ID || ticket.version !== VERSION) return { ok: false, reason: 'source' };
    if (!settings.hourlyRefresh) return { ok: false, reason: 'setting-disabled' };
    if (ticket.conversationId !== conversationIdFromPath() || ticket.pathname !== location.pathname) return { ok: false, reason: 'conversation' };
    const trigger = ticket.maintenanceTrigger || { kind: 'interval' };
    if (!['interval','pipeline-failure-edge'].includes(trigger.kind)) return { ok: false, reason: 'maintenance-trigger' };
    if (trigger.kind === 'pipeline-failure-edge' && (typeof trigger.key !== 'string' || !trigger.key || typeof trigger.reason !== 'string')) return { ok: false, reason: 'maintenance-trigger-detail' };
    if (ticket.promptHash !== fnv1a64(settings.prompt) || ticket.promptChars !== settings.prompt.length || !settings.prompt) return { ok: false, reason: 'prompt' };
    if (!Number.isFinite(ticket.createdT) || !Number.isFinite(ticket.expiresT) || ticket.createdT > now + 60_000 || ticket.expiresT < now) return { ok: false, reason: 'age' };
    return { ok: true };
  }
  function bindAutoRefreshActiveSend(ticket) {
    const saved = ticket?.run?.activeSend;
    if (!saved) return true;
    invalidateTurnCache('auto-refresh-bind');
    const turns = materializedTurns();
    const users = turns.filter(turn => turn.role === 'user');
    let user = users.find(turn => turn.id === saved.userTurnId);
    if (!user) user = users.slice().reverse().find(turn => compareRenderedPrompt(turnText(turn.element), state.runPrompt).ok);
    if (!user) return false;
    const laterUsers = users.filter(turn => turn.index > user.index);
    if (laterUsers.some(turn => !compareRenderedPrompt(turnText(turn.element), state.runPrompt).ok)) {
      stopRun('Safe refresh resume found different later user text; qomrade stopped instead of claiming custody.', { error: { kind: 'auto-refresh-unrelated-user', expectedPromptHash: fnv1a64(state.runPrompt), laterUserIds: laterUsers.map(turn => turn.id) } });
      return true;
    }
    if (laterUsers.length) user = laterUsers[laterUsers.length - 1];
    const before = turns.slice(0, user.index);
    const previousAssistant = before.filter(turn => turn.role === 'assistant').slice(-1)[0];
    state.activeSend = { ...saved, schema: 'qomrade.send-transaction.v2', id: saved.id || `refresh-resume-${Date.now().toString(36)}`,
      userTurnId: user.id, userTurnOrdinal: user.ordinal, userAdoptedAt: saved.userAdoptedAt || nowIso(),
      baselineAssistantId: previousAssistant?.id || null, preTurnIds: before.map(turn => turn.id), preMaxOrdinal: null,
      outcome: null,
      modelPolicy: saved.modelPolicy || ticket.run.modelPolicy || MODEL_POLICY_SMART_PRO,
      modelTarget: saved.modelTarget || ticket.run.modelTarget || null,
      modelPreference: saved.modelPreference || ticket.run.modelPreference || '5.6-first',
      authority: 'confirmed one-shot hourly-refresh ticket plus latest exact rendered prompt; no new Send occurred during restore' };
    state.baselineAssistantId = previousAssistant?.id || null;
    state.modelAtSend = saved.model || null;
    return true;
  }
  function resolveAutoRefreshRestore() {
    if (!state.autoRefresh.restorePending || !state.autoRefresh.pendingResume) return true;
    const now = Date.now();
    if (!state.autoRefresh.restoreStartedAt) state.autoRefresh.restoreStartedAt = now;
    if (!state.autoRefresh.restoreDeadlineAt) state.autoRefresh.restoreDeadlineAt = state.autoRefresh.restoreStartedAt + AUTO_REFRESH_RESTORE_MAX_MS;
    if (!bindAutoRefreshActiveSend(state.autoRefresh.pendingResume)) {
      if (now >= state.autoRefresh.restoreDeadlineAt) {
        const snapshotId = captureDomishEvent('auto-refresh-restore-timeout', {
          reason: 'Exact request custody did not rematerialize before the bounded restore deadline',
          severity: 'error', origin: 'safe-refresh-restore',
          key: fnv1a64(JSON.stringify(['auto-refresh-restore-timeout', state.autoRefresh.pendingResume?.nonce || null, state.autoRefresh.restoreStartedAt])),
          context: { restoreStartedAt: state.autoRefresh.restoreStartedAt, restoreDeadlineAt: state.autoRefresh.restoreDeadlineAt, ticketNonce: state.autoRefresh.pendingResume?.nonce || null },
        });
        state.autoRefresh.restorePending = false;
        state.autoRefresh.pendingResume = null;
        stopRun('Safe refresh could not rematerialize the exact saved request before its bounded deadline. qomrade stopped without sending.', {
          error: { kind: 'auto-refresh-restore-timeout', snapshotId, restoreStartedAt: state.autoRefresh.restoreStartedAt, restoreDeadlineAt: state.autoRefresh.restoreDeadlineAt },
        });
        return false;
      }
      setPhase('REFRESH_RESTORE_HOLD', `Safe refresh resumed the controller, but the exact active request is not materialized yet. Waiting without sending until ${new Date(state.autoRefresh.restoreDeadlineAt).toLocaleTimeString()}.`);
      scheduleTick(document.hidden ? HIDDEN_REPLY_POLL_MS : 5_000, 'safe refresh hydration hold');
      return false;
    }
    if (!state.running) {
      state.autoRefresh.restorePending = false;
      state.autoRefresh.pendingResume = null;
      return false;
    }
    state.autoRefresh.restorePending = false;
    state.autoRefresh.pendingResume = null;
    state.autoRefresh.restoreStartedAt = 0;
    state.autoRefresh.restoreDeadlineAt = 0;
    if (state.activeSend) {
      state.waitingSince = state.waitingSince || Date.now();
      setPhase('WAITING_REPLY', 'Safe refresh restored exact request custody; re-observing the current response before any new message.');
      scheduleTick(0, 'safe refresh active request restored');
    } else if (Date.now() < state.nextSendAt) {
      setPhase('WAITING_GAP', 'Safe refresh restored the run at a safe gap checkpoint.');
      scheduleGapTick();
    } else {
      setPhase('READY_TO_SEND', 'Safe refresh restored the run after its ordinary gap elapsed.');
      scheduleTick(0, 'safe refresh ready');
    }
    scheduleNextAutoRefresh('post-refresh-resume', Date.now());
    armDomTrim(5_000, 'post-refresh-resume');
    persistContinuity('hourly-refresh-resumed');
    return true;
  }
  async function restoreAutoRefreshResumeTicket() {
    if (state.autoRefresh.restoreInFlight || !state.autoRefresh.pendingResume || state.quarantine) return false;
    state.autoRefresh.restoreInFlight = true;
    const ticket = state.autoRefresh.pendingResume;
    const verdict = validAutoRefreshTicket(ticket);
    if (!verdict.ok) {
      state.autoRefresh.resumeTicket = null;
      state.autoRefresh.pendingResume = null;
      state.autoRefresh.restorePending = false;
      await persistAutoRefreshBarrier('hourly-refresh-ticket-refused', null);
      boundedReceipt(state.autoRefresh.receipts, { at: nowIso(), outcome: 'resume-refused', reason: verdict.reason });
      logEvent('auto-refresh-resume-refused', 'Discarded an invalid or stale safe-refresh ticket.', verdict);
      state.autoRefresh.restoreInFlight = false;
      render();
      return false;
    }
    state.autoRefresh.resumeTicket = null;
    const consumed = await persistAutoRefreshBarrier('hourly-refresh-ticket-consumed', null);
    if (!consumed) {
      state.autoRefresh.resumeTicket = ticket;
      state.autoRefresh.restoreInFlight = false;
      state.autoRefresh.restorePending = true;
      state.autoRefresh.lastBlocked = 'ticket-consume-unverified';
      boundedReceipt(state.autoRefresh.receipts, { at: nowIso(), outcome: 'resume-deferred', reason: 'ticket-consume-unverified' });
      clearAutoRefreshTimer();
      ui.autoRefreshTimer = setTimeout(() => { ui.autoRefreshTimer = null; void restoreAutoRefreshResumeTicket(); }, AUTO_REFRESH_RETRY_MS);
      render();
      return false;
    }
    const run = ticket.run || {};
    state.running = true;
    state.paused = false;
    state.runPrompt = settings.prompt;
    state.startedAt = Number(run.startedAt) || Date.now();
    state.lastSendAt = Number(run.lastSendAt) || 0;
    state.nextSendAt = Number(run.nextSendAt) || Date.now();
    state.waitingSince = Number(run.waitingSince) || 0;
    state.anchorConversationId = ticket.conversationId;
    state.sends = Math.max(state.sends, Number(run.sends) || 0);
    state.completedReplies = Math.max(state.completedReplies, Number(run.completedReplies) || 0);
    state.startAttempts = Math.max(state.startAttempts, Number(run.startAttempts) || 0);
    state.startAccepted = Math.max(state.startAccepted, Number(run.startAccepted) || 0);
    state.startRefused = Math.max(state.startRefused, Number(run.startRefused) || 0);
    state.startTransaction = run.startTransaction || state.startTransaction;
    state.adoptedWithoutClick = Math.max(state.adoptedWithoutClick, Number(run.adoptedWithoutClick) || 0);
    state.preClickAdvanceHolds = Math.max(state.preClickAdvanceHolds, Number(run.preClickAdvanceHolds) || 0);
    state.composerAttemptCount = Math.max(state.composerAttemptCount, Number(run.composerAttemptCount) || 0);
    state.modelGate.runPolicy = normalizeModelPolicy(run.modelPolicy || settings.modelPolicy);
    state.modelGate.target = run.modelTarget && typeof run.modelTarget === 'object'
      ? { label: trunc(run.modelTarget.label || '', 180), key: trunc(run.modelTarget.key || modelRouteKey(run.modelTarget.label || ''), 220), version: normalizeModelVersionHint(run.modelTarget.version, run.modelTarget.label), effort: normalizeModelEffortPolicy(run.modelTarget.effort) }
      : modelPolicySnapshot(settings).target;
    state.modelGate.runPreference = state.modelGate.runPolicy === MODEL_POLICY_SMART_PRO
      ? (run.modelPreference === '6-fallback' ? '6-fallback' : '5.6-first')
      : state.modelGate.runPolicy === MODEL_POLICY_PIN ? 'pinned' : 'follow';
    state.baselineAssistantId = run.baselineAssistantId || null;
    state.activeSend = null;
    restoreSessionArchive(ticket.sessionArchive);
    restoreDomForensics(ticket.domForensics);
    state.autoRefresh.dueAt = Number(ticket.nextRefreshAt) || Date.now() + autoRefreshIntervalMs();
    state.autoRefresh.retryAt = 0;
    state.autoRefresh.lastReloadAt = nowIso();
    state.autoRefresh.reloads += 1;
    state.autoRefresh.pageReloads += 1;
    const maintenanceTrigger = ticket.maintenanceTrigger || { kind: 'interval' };
    if (maintenanceTrigger.kind === 'pipeline-failure-edge' && typeof maintenanceTrigger.key === 'string') {
      state.autoRefresh.lastHealingKey = maintenanceTrigger.key;
      state.autoRefresh.lastHealingAt = ticket.createdAt || state.autoRefresh.lastReloadAt;
      const healingAt = Number(ticket.createdT) || Date.now();
      if (!state.autoRefresh.healingHistory.some(row => row.key === maintenanceTrigger.key && Math.abs(Number(row.at) - healingAt) < 1_000)) {
        state.autoRefresh.healingHistory.push({ key: maintenanceTrigger.key, at: healingAt, reason: maintenanceTrigger.reason || 'pipeline-failure-edge' });
        state.autoRefresh.healingReloads += 1;
      }
      compactHealingHistory();
    }
    state.autoRefresh.healingPending = null;
    state.autoRefresh.restorePending = !!run.activeSend;
    state.autoRefresh.pendingResume = run.activeSend ? ticket : null;
    state.autoRefresh.restoreStartedAt = run.activeSend ? Date.now() : 0;
    state.autoRefresh.restoreDeadlineAt = run.activeSend ? Date.now() + AUTO_REFRESH_RESTORE_MAX_MS : 0;
    state.autoRefresh.restoreInFlight = false;
    state.autoRefresh.inFlight = false;
    logEvent('auto-refresh-resumed', maintenanceTrigger.kind === 'pipeline-failure-edge' ? 'Consumed the one-shot page-shell maintenance healing ticket and restored only its exact source, conversation, prompt, and run checkpoint.' : 'Consumed the one-shot interval refresh ticket and restored only its exact source, conversation, prompt, and run checkpoint.', { nonce: ticket.nonce, phase: run.phase, activeSend: !!run.activeSend, maintenanceTrigger });
    if (run.activeSend) return resolveAutoRefreshRestore();
    if (Date.now() < state.nextSendAt) {
      setPhase('WAITING_GAP', 'Safe refresh restored the run at a safe gap checkpoint.');
      scheduleGapTick();
    } else {
      setPhase('READY_TO_SEND', 'Safe refresh restored the run after its ordinary gap elapsed.');
      scheduleTick(0, 'safe refresh ready');
    }
    scheduleNextAutoRefresh('post-refresh-resume', Date.now());
    armDomTrim(5_000, 'post-refresh-resume');
    persistContinuity('hourly-refresh-resumed');
    return true;
  }
  function maybeBeginAutoRefreshRestore() {
    if (!state.autoRefresh.pendingResume || state.autoRefresh.restoreInFlight || !state.boot.settingsReadyAt || !state.boot.oneShotAuthenticityCheckedAt || state.quarantine) return;
    void restoreAutoRefreshResumeTicket();
  }
  // @QOMRADE-CHUNK id=45.science title="Active-only bounded change-edge pipeline science"
  function compactSystemScienceSurface() {
    const combined = [...SELECTORS.system, ...SELECTORS.errors].join(',');
    const records = [];
    const seen = new Set();
    for (const node of qa(combined).slice(0, 24)) {
      if (!isVisible(node) || seen.has(node)) continue;
      seen.add(node);
      const text = trunc(normalizeCompactText(node.textContent || node.getAttribute('aria-label') || ''), 320);
      if (!text) continue;
      records.push({
        text,
        role: node.getAttribute('role'),
        ariaLive: node.getAttribute('aria-live'),
        dataTestId: node.getAttribute('data-testid'),
        classHint: trunc(String(node.className || ''), 220),
        insideAssistant: !!node.closest('[data-message-author-role="assistant"],[data-turn="assistant"],[data-chatgpt-search-unit-key$=":assistant"]'),
      });
    }
    return records.slice(0, 12);
  }
  function pipelineSurfaceEdgeFromPulse(pulse) {
    if (!pulse) return null;
    const literalTexts = [];
    const addText = (text, source, extra = {}) => {
      const value = trunc(normalizeCompactText(text || ''), 640);
      if (!value || literalTexts.some(row => row.text === value && row.source === source)) return;
      const typed = classifyPipelineFailureText(value);
      const maintenance = classifyPipelineMaintenanceText(value);
      literalTexts.push({
        source,
        text: value,
        textHash: fnv1a64(value),
        faultKind: typed ? typed.faultKind : null,
        maintenanceKind: maintenance ? maintenance.maintenanceKind : null,
        classificationKind: typed ? 'generation-fault' : maintenance ? 'maintenance' : 'unknown',
        ...extra,
      });
    };
    if (pulse.error && pulse.error.text) addText(pulse.error.text, 'classifier-error', { faultKind: pulse.error.faultKind || null });
    for (const item of pulse.system || []) addText(item.text, 'system-surface', { role: item.role || null, dataTestId: item.dataTestId || null });
    for (const context of pulse.retry?.contexts || []) addText(context.text, 'retry-card-context', {
      faultKind: context.typed?.faultKind || null,
      maintenanceKind: context.maintenance?.maintenanceKind || null,
      hostRole: context.host?.role || null,
      hostTestId: context.host?.testId || null,
      turn: context.turn || null,
      labelVisible: context.labelVisible,
      labelComplete: context.labelComplete,
    });
    const retryVisible = !!pulse.retry?.available;
    const typedFailure = literalTexts.some(row => row.faultKind);
    const maintenance = literalTexts.some(row => row.maintenanceKind);
    const unknown = literalTexts.some(row => !row.faultKind && !row.maintenanceKind);
    if (!retryVisible && !pulse.error && !typedFailure && !maintenance) return null;
    const key = fnv1a64(JSON.stringify([
      conversationIdFromPath(), pulse.phase, pulse.assistant?.ordinal || null,
      retryVisible, (pulse.retry?.labels || []).slice(0, MAX_RETRY_CONTEXTS),
      literalTexts.map(row => [row.source, row.textHash, row.faultKind, row.maintenanceKind]),
    ]));
    return {
      schema: 'qomrade.pipeline-surface-edge.v1',
      key,
      at: pulse.at,
      origin: pulse.origin,
      phase: pulse.phase,
      activeTransactionId: pulse.activeTransactionId || null,
      generating: !!pulse.generating,
      assistant: pulse.assistant ? { id: pulse.assistant.id || null, ordinal: pulse.assistant.ordinal == null ? null : pulse.assistant.ordinal } : null,
      retry: pulse.retry ? {
        available: !!pulse.retry.available,
        count: Number(pulse.retry.count) || 0,
        insideLatestAssistantCount: Number(pulse.retry.insideLatestAssistantCount) || 0,
        outsideLatestAssistantCount: Number(pulse.retry.outsideLatestAssistantCount) || 0,
        labels: (pulse.retry.labels || []).slice(0, MAX_RETRY_CONTEXTS),
      } : null,
      literalTexts,
      classified: typedFailure || maintenance,
      typedFailure,
      maintenance,
      unknown,
      severity: typedFailure ? 'error' : 'warn',
      coverage: 'bounded visible DOM: classifier output, compact system surfaces, and nearest non-control context around visible Retry controls',
      authority: 'evidence-only; generation-fault wording, maintenance wording, and unknown text remain separate classifications and never grant Retry or prompt-send authority',
    };
  }
  function recordPipelineSurfaceEdge(pulse) {
    const edge = pipelineSurfaceEdgeFromPulse(pulse);
    if (!edge) return null;
    const previous = state.science.surfaceEdges[state.science.surfaceEdges.length - 1];
    if (previous && previous.key === edge.key) return previous;
    edge.domSnapshotId = captureDomishEvent('pipeline-surface-edge', {
      reason: edge.unknown ? 'visible pipeline surface changed with unclassified literal wording'
        : edge.maintenance ? 'visible page-shell maintenance surface changed'
          : 'visible pipeline failure surface changed',
      severity: edge.severity,
      origin: edge.origin || 'pipeline-science',
      relatedIds: [edge.key],
      key: fnv1a64(`pipeline-surface|${edge.key}`),
      context: edge,
    });
    state.science.surfaceEdges.push(edge);
    if (state.science.surfaceEdges.length > MAX_PIPELINE_SURFACE_EDGES) {
      state.science.surfaceEdges.splice(0, state.science.surfaceEdges.length - MAX_PIPELINE_SURFACE_EDGES);
    }
    logEvent('pipeline-surface-edge', 'Recorded literal visible pipeline-surface evidence, including nearby Retry-card wording even when unclassified.', edge);
    return edge;
  }
  function captureBoundedSciencePulse(origin, evidence = {}) {
    if (!settings.boundedScience || !state.running) return null;
    const assistant = Object.prototype.hasOwnProperty.call(evidence, 'assistant') ? evidence.assistant : latestAssistantTurn();
    const work = evidence.work || workEvidenceObservation({ scope: 'active' });
    const continuation = evidence.continuation || continuationObservation(assistant);
    const retry = evidence.retry || retryObservation(assistant);
    const error = Object.prototype.hasOwnProperty.call(evidence, 'error') ? evidence.error : classifyVisibleError(assistant);
    const model = directModelObservation();
    const pulse = {
      schema: 'qomrade.pipeline-science-pulse.v1',
      at: nowIso(),
      t: Date.now(),
      origin,
      phase: state.phase,
      activeTransactionId: state.activeSend && state.activeSend.id || null,
      generating: Object.prototype.hasOwnProperty.call(evidence, 'generating') ? !!evidence.generating : !!findStopButton(),
      assistant: assistant ? { id: assistant.id, ordinal: assistant.ordinal, fingerprint: assistant.fingerprint, textChars: assistant.text ? assistant.text.length : 0, workOnly: !!assistant.workOnly } : null,
      work: work ? { blocking: !!work.blocking, overlapHazard: !!work.overlapHazard, signature: work.signature || null, active: work.latestUnresolved ? { id: work.latestUnresolved.id, ordinal: work.latestUnresolved.ordinal, qcotMarkers: work.latestUnresolved.workMarkerCount } : null } : null,
      continuation: continuation ? { available: !!continuation.available, count: continuation.controls ? continuation.controls.length : 0 } : null,
      retry: retry ? { available: !!retry.available, count: retry.controls ? retry.controls.length : 0,
        insideLatestAssistantCount: (retry.controls || []).filter(row => row.insideLatestAssistant).length,
        outsideLatestAssistantCount: (retry.controls || []).filter(row => !row.insideLatestAssistant).length,
        labels: (retry.controls || []).map(row => trunc(normalizeCompactText(`${row.text || ''} ${row.ariaLabel || ''} ${row.testId || ''}`), 120)).filter(Boolean).slice(0, MAX_RETRY_CONTEXTS),
        contexts: (retry.controls || []).map(row => row.context).filter(Boolean).slice(0, MAX_RETRY_CONTEXTS) } : null,
      error: error ? { kind: error.kind || null, faultKind: error.faultKind || null, text: trunc(error.text || error.message || '', 320) } : null,
      model: { label: model.label, family: model.family, hasPro: model.hasPro, transient: model.transient },
      system: compactSystemScienceSurface(),
    };
    const signature = fnv1a64(JSON.stringify({
      phase: pulse.phase,
      generating: pulse.generating,
      assistant: pulse.assistant && [pulse.assistant.id, pulse.assistant.fingerprint, pulse.assistant.workOnly],
      work: pulse.work && [pulse.work.blocking, pulse.work.overlapHazard, pulse.work.signature],
      continuation: pulse.continuation,
      retry: pulse.retry,
      error: pulse.error,
      model: pulse.model,
      system: pulse.system.map(item => [item.text, item.role, item.dataTestId]),
    }));
    pulse.signature = signature;
    state.science.samples += 1;
    state.science.lastAt = pulse.at;
    if (signature !== state.science.lastSignature) {
      const from = state.science.lastSignature;
      state.science.lastSignature = signature;
      state.science.lastChangedAt = pulse.at;
      state.science.changes += 1;
      state.science.pulses.push(pulse);
      if (state.science.pulses.length > MAX_SCIENCE_PULSES) state.science.pulses.splice(0, state.science.pulses.length - MAX_SCIENCE_PULSES);
      logEvent('science-edge', 'Bounded pipeline evidence changed.', { from, pulse });
      recordPipelineSurfaceEdge(pulse);
      considerHealingRefreshFromScienceEdge(pulse, `science-edge:${origin}`);
    }
    return pulse;
  }
  // @QOMRADE-CHUNK id=50.controller title="Single-tab controller, action receipts, scheduling, holds, and stop authority"
  function setPhase(phase, reason) {
    const changed = state.phase !== phase || state.phaseReason !== reason;
    state.phase = phase;
    state.phaseReason = reason;
    if (phase === 'MODEL_HOLD' && document.hidden) noteHiddenModelHold(reason);
    if (changed) logEvent('phase', `${phase}: ${reason}`);
    render();
  }
  function clearControllerTimer(reason = 'cleared') {
    if (state.timer) clearTimeout(state.timer);
    state.timer = null;
    state.scheduler.dueAt = 0;
    state.scheduler.lastClearedAt = Date.now();
    state.scheduler.lastClearReason = reason;
  }
  function markActiveSendOutcome(outcome, detail = null) {
    if (!state.activeSend) return;
    state.activeSend.outcome = outcome;
    state.activeSend.outcomeAt = nowIso();
    if (detail != null) state.activeSend.outcomeDetail = detail;
  }
  function quarantineHardFalseGui(observation, source = 'runtime-check') {
    if (state.quarantine) return true;
    revokeEffectAuthority('quarantine');
    const quarantine = {
      schema: 'qomrade.quarantine.v1',
      kind: 'hard-no-history-plus-5.3',
      at: nowIso(),
      source,
      observation,
      sourceId: QOMRADE_SOURCE_ID,
      authority: 'all-chatgpt-effects-revoked',
    };
    markActiveSendOutcome('quarantined', quarantine);
    state.quarantine = quarantine;
    state.running = false;
    state.paused = false;
    state.runPrompt = '';
    state.nextSendAt = 0;
    state.waitingSince = 0;
    clearControllerTimer('hard false-GUI quarantine');
    if (ui.zipRescanTimer) clearTimeout(ui.zipRescanTimer);
    ui.zipRescanTimer = null;
    clearFileOutcomeObserver('runtime-stopped');
    clearDomTrimTimer();
    clearAutoRefreshTimer();
    state.autoRefresh.dueAt = 0;
    state.autoRefresh.retryAt = 0;
    state.autoRefresh.healingPending = null;
    state.autoRefresh.lastFaultSurfaceKey = null;
    state.autoRefresh.resumeTicket = null;
    state.autoRefresh.pendingResume = null;
    state.autoRefresh.restorePending = false;
    state.autoRefresh.inFlight = false;
    state.lastError = { kind: 'hard-false-gui', quarantine };
    state.phase = 'OFF';
    state.phaseReason = 'Hard no-history plus 5.3 false-GUI signature; all ChatGPT effects are off.';
    logEvent('quarantine', state.phaseReason, quarantine);
    persistContinuity('hard-false-gui-quarantine');
    render();
    return true;
  }
  function enforceHardFalseGui(source = 'runtime-check', { detail = false } = {}) {
    let observation = surfaceAuthenticityObservation({ detail });
    if (observation.hard && !detail) {
      try { observation = surfaceAuthenticityObservation({ detail: true }); }
      catch (_) {}
    }
    state.lastAuthenticity = observation;
    if (observation.hard) return quarantineHardFalseGui(observation, source);
    return false;
  }
  function stopRun(reason = 'operator stopped qomrade', { error = null, terminal = null } = {}) {
    if (error || terminal) {
      const primary = error ? faultNodes.get(error) : null;
      captureDomishEvent(terminal ? 'terminal-conversation-boundary' : 'controller-halt', {
        reason,
        severity: terminal ? 'info' : 'error',
        origin: terminal ? 'terminal-stop' : 'halt',
        primaryNodes: [primary].filter(Boolean),
        force: true,
        context: { error, terminal, activeSendId: state.activeSend?.id || null },
      });
    }
    captureSessionTurns(terminal ? 'conversation-complete' : error ? 'halt' : 'operator-stop');
    if (state.sessionArchive?.sessionId) state.sessionArchive.endedAt = nowIso();
    const completed = !!terminal;
    const mode = error ? 'halt' : completed ? 'complete' : 'stop';
    revokeEffectAuthority(mode);
    if (state.activeSend && !state.activeSend.outcome) {
      markActiveSendOutcome(error ? 'halted' : completed ? 'conversation-complete' : 'operator-stopped', error || terminal || { reason });
    }
    state.running = false;
    state.paused = false;
    state.runPrompt = '';
    state.nextSendAt = 0;
    state.waitingSince = 0;
    state.baselineAssistantId = null;
    state.latestAssistantId = null;
    state.latestAssistantFingerprint = null;
    state.stableSamples = 0;
    state.lastError = error;
    state.terminalStop = completed ? JSON.parse(JSON.stringify(terminal)) : null;
    clearControllerTimer(mode);
    if (ui.shellHealthTimer) clearTimeout(ui.shellHealthTimer);
    ui.shellHealthTimer = null;
    if (ui.zipRescanTimer) clearTimeout(ui.zipRescanTimer);
    ui.zipRescanTimer = null;
    clearFileOutcomeObserver('runtime-stopped');
    clearDomTrimTimer();
    clearAutoRefreshTimer();
    state.autoRefresh.dueAt = 0;
    state.autoRefresh.retryAt = 0;
    state.autoRefresh.healingPending = null;
    state.autoRefresh.lastFaultSurfaceKey = null;
    state.autoRefresh.resumeTicket = null;
    state.autoRefresh.pendingResume = null;
    state.autoRefresh.restorePending = false;
    state.autoRefresh.inFlight = false;
    state.zipCapture.pending = null;
    setPhase(error ? 'HALTED' : completed ? 'COMPLETE' : 'STOPPED', reason);
    logEvent(error ? 'halt' : completed ? 'complete' : 'stop', reason, error || terminal);
    persistContinuity(mode);
    render();
  }
  function pauseRun() {
    if (!state.running || state.paused) return;
    revokeEffectAuthority('pause');
    state.paused = true;
    clearControllerTimer('operator pause');
    if (ui.zipRescanTimer) clearTimeout(ui.zipRescanTimer);
    ui.zipRescanTimer = null;
    clearDomTrimTimer();
    clearAutoRefreshTimer();
    state.autoRefresh.resumeTicket = null;
    state.autoRefresh.pendingResume = null;
    state.autoRefresh.restorePending = false;
    state.autoRefresh.inFlight = false;
    logEvent('pause', 'Operator paused qomrade.');
    persistContinuity('pause');
    render();
  }
  function resumeRun() {
    if (!state.running || !state.paused || state.quarantine) return;
    state.paused = false;
    logEvent('resume', 'Operator resumed qomrade.');
    persistContinuity('resume');
    render();
    scheduleTick(0, 'operator resume');
    armZipRescan();
    if (settings.trimOldTurns) armDomTrim(1_000, 'operator-resume');
    if (settings.hourlyRefresh) {
      if (!state.autoRefresh.dueAt) scheduleNextAutoRefresh('operator-resume');
      else { state.autoRefresh.retryAt = 0; armAutoRefresh('operator-resume'); }
    }
  }
  function pauseForHidden() { return settings.pauseWhenHidden; }
  function faultQuietMs() { return FAULT_SETTLE_MS; }
  function backgroundMode() {
    return !state.running ? 'stopped' : state.paused ? 'paused' : document.hidden
      ? (pauseForHidden() ? 'hidden-policy-hold' : 'background-running') : 'foreground-running';
  }
  function recordBackgroundEdge(origin) {
    const mode = backgroundMode(), hidden = document.hidden, now = Date.now();
    const previous = state.background.current;
    if (previous && previous.mode === mode && previous.hidden === hidden) return;
    if (previous) {
      state.background.intervals.push({ ...previous, endedAt: nowIso(), durationMs: Math.max(0, now - previous.startedT),
        hiddenTicks: state.background.hiddenTicks - previous.hiddenTicksAtStart });
      if (state.background.intervals.length > 24) state.background.intervals.shift();
    }
    state.background.current = { mode, hidden, startedAt: nowIso(), startedT: now, origin,
      hiddenTicksAtStart: state.background.hiddenTicks };
  }
  function noteHiddenModelHold(reason) {
    const now = Date.now();
    const pending = state.background.pendingHiddenModelHold;
    if (pending && pending.reason === reason) {
      pending.lastObservedAt = nowIso();
      pending.observations += 1;
      return pending;
    }
    state.background.pendingHiddenModelHold = {
      startedAt: nowIso(), startedT: now, lastObservedAt: nowIso(), observations: 1,
      reason: trunc(reason || 'model hold', 400),
      menuSurface: state.modelGate.lastMenuSurface ? {
        stage: state.modelGate.lastMenuSurface.stage,
        controlledId: state.modelGate.lastMenuSurface.controlledId,
        controlledItems: state.modelGate.lastMenuSurface.controlledItems,
        backgroundStructuralReady: state.modelGate.lastMenuSurface.backgroundStructuralReady,
        backgroundPaintSuppressed: state.modelGate.lastMenuSurface.backgroundPaintSuppressed,
      } : null,
    };
    return state.background.pendingHiddenModelHold;
  }
  function noteBackgroundLifecycle(kind) {
    const at = nowIso();
    if (kind === 'visible') state.background.lastVisibilityAt = at;
    if (kind === 'focus') state.background.lastFocusAt = at;
  }
  function noteBackgroundProgress(kind) {
    const now = Date.now();
    const pending = state.background.pendingHiddenModelHold;
    if (document.hidden) {
      state.background.hiddenProgresses += 1;
      state.background.lastHiddenProgressAt = nowIso();
      if (pending) state.background.pendingHiddenModelHold = null;
      return;
    }
    if (!pending) return;
    const activationAt = Math.max(
      state.background.lastVisibilityAt ? Date.parse(state.background.lastVisibilityAt) : 0,
      state.background.lastFocusAt ? Date.parse(state.background.lastFocusAt) : 0,
    );
    if (activationAt && now - activationAt <= BACKGROUND_RESCUE_WINDOW_MS) {
      state.background.foregroundRescues.push({
        at: nowIso(), kind, holdStartedAt: pending.startedAt, holdReason: pending.reason,
        activationAt: new Date(activationAt).toISOString(),
        activationToProgressMs: Math.max(0, now - activationAt),
        hiddenHoldDurationMs: Math.max(0, now - pending.startedT),
        observations: pending.observations,
      });
      if (state.background.foregroundRescues.length > 12) state.background.foregroundRescues.shift();
    }
    state.background.pendingHiddenModelHold = null;
  }
  function recordBackgroundExecutionGap({ dueAt, firedAt, latenessMs, reason }) {
    if (!document.hidden || latenessMs < BACKGROUND_EXECUTION_GAP_MS) return;
    state.background.executionGaps.push({ at: nowIso(), dueAt, firedAt, latenessMs, reason: trunc(reason, 300) });
    if (state.background.executionGaps.length > 12) state.background.executionGaps.shift();
  }
  function backgroundSnapshot() {
    const current = state.background.current;
    return { schema: 'qomrade.background-observability.v1', ...state.background,
      mode: backgroundMode(), hidden: document.hidden, pauseWhenHidden: pauseForHidden(), configuredPauseWhenHidden: settings.pauseWhenHidden,
      current: current ? { ...current, durationMs: Math.max(0, Date.now() - current.startedT) } : null,
      intervals: state.background.intervals.slice(-24),
      limitation: 'callback evidence only; browser throttling, suspension, OS sleep and backend liveness are not controlled by qomrade' };
  }
  function replyPollMs() {
    return document.hidden ? HIDDEN_REPLY_POLL_MS : VISIBLE_REPLY_POLL_MS;
  }
  function gapPollMs() {
    return document.hidden ? HIDDEN_GAP_POLL_MS : VISIBLE_GAP_POLL_MS;
  }
  function scheduleTick(delayMs, reason = state.phase) {
    clearControllerTimer('reschedule');
    if (!state.running || state.paused || state.quarantine || (pauseForHidden() && document.hidden)) return;
    const nominal = Math.max(0, Number(delayMs) || 0);
    const scheduledAt = Date.now();
    const dueAt = scheduledAt + nominal;
    state.scheduler.scheduledAt = scheduledAt;
    state.scheduler.dueAt = dueAt;
    state.scheduler.nominalDelayMs = nominal;
    state.scheduler.reason = reason;
    state.timer = setTimeout(() => {
      state.timer = null;
      const firedAt = Date.now();
      const lateness = Math.max(0, firedAt - dueAt);
      state.scheduler.lastFiredAt = firedAt;
      state.scheduler.lastLatenessMs = lateness;
      state.scheduler.maxLatenessMs = Math.max(state.scheduler.maxLatenessMs, lateness);
      state.scheduler.fires += 1;
      if (lateness >= TIMER_LATE_THRESHOLD_MS) {
        state.scheduler.lateCount += 1;
        logEvent('timer-late', `Controller timer fired ${lateness} ms late.`, { dueAt, firedAt, latenessMs: lateness, reason });
      }
      recordBackgroundExecutionGap({ dueAt, firedAt, latenessMs: lateness, reason });
      void tick();
    }, nominal);
  }
  function validateConversationAnchor() {
    const current = conversationIdFromPath();
    if (!state.anchorConversationId && current) {
      state.anchorConversationId = current;
      logEvent('anchor', 'Established the current conversation anchor after ChatGPT created the thread URL.', { conversationId: current });
      persistContinuity('conversation-anchor-established');
      return true;
    }
    if (state.anchorConversationId && current && current !== state.anchorConversationId) {
      stopRun('ChatGPT changed to a different conversation; qomrade stopped.', {
        error: { kind: 'conversation-changed', expected: state.anchorConversationId, observed: current },
      });
      return false;
    }
    return true;
  }
  function preEffectInterlock(context = 'before-send') {
    return withReadSnapshot('preEffectInterlock', () => {
    if (state.quarantine || enforceHardFalseGui(context)) return { ok: false, reason: 'hard-false-gui' };
    const barrier = conversationBarrierObservation();
    if (barrier.present) {
      stopForConversationTerminal(barrier, 'conversation-wide-pre-effect-scan');
      return { ok: false, reason: 'conversation-terminal' };
    }
    const observation = pipelineFaultObservation();
    const fault = observation.current;
    const shellSurface = fault?.kind === 'generation-error' ? null : visiblePageShellMaintenanceSurface(`pre-effect:${context}`);
    if (shellSurface) {
      holdForPageShellMaintenance(shellSurface, `pre-effect:${context}`);
      return { ok: false, reason: 'page-shell-maintenance', surface: shellSurface };
    }
    if (fault?.kind === 'page-shell-maintenance') {
      const surface = visiblePageShellMaintenanceSurface(`pre-effect:${context}`) || {
        key: fnv1a64(JSON.stringify([conversationIdFromPath(), fault.maintenanceKind || 'page-shell-maintenance'])),
        reason: fault.maintenanceKind || 'page-shell-maintenance', maintenanceKind: fault.maintenanceKind || null,
        allowActiveSend: maintenanceAllowsActiveRequestRefresh(fault.maintenanceKind), evidence: { fault, context },
      };
      holdForPageShellMaintenance(surface, `pre-effect:${context}`);
      return { ok: false, reason: 'page-shell-maintenance', fault, surface };
    }
    const replayAllowed = !!fault && recoveryReplayAllows(fault);
    const nextTurnAllowed = !!fault && preexistingFailureAdvanceAllows(fault, { ownedComposer: context === 'immediately-before-send-click' });
    if (recoveryReplayPermit && !recoveryReplayPermit.consumed && !replayAllowed) {
      recoveryHold('Prompt resend cancelled: the original failure, request, or live conditions changed.');
      return { ok: false, reason: 'resend-evidence-changed', fault };
    }
    if (fault && preexistingFailureAdvancePermit && !preexistingFailureAdvancePermit.consumed && !nextTurnAllowed) {
      preexistingFailureAdvancePermit = null;
      recoveryHold('The pre-existing failure or its request identity changed before the ordinary next turn. qomrade is observing again.');
      return { ok: false, reason: 'preexisting-failure-evidence-changed', fault };
    }
    if (fault && !replayAllowed && !nextTurnAllowed) {
      if (fault.kind === 'generation-error') {
        if (!tryAdoptExistingFailedRequest(observation, 'deferred-fault')) {
          const advance = settlePreexistingFailureAdvance(observation, `pre-effect:${context}`);
          if (advance.handled) return { ok: false, reason: advance.ready ? 'preexisting-failure-next-turn-reentry' : 'preexisting-failure-settling', fault, advance };
          state.faultRecovery.lastObservation = observation;
          state.faultRecovery.lastDecision = { at: nowIso(), faultKind: fault.faultKind, blocked: 'latest-request-match-or-empty-composer-unresolved', backendOutcome: 'unknown' };
          recoveryHold(`Fault: ${fault.text}. Waiting for stable request identity and an empty composer before any fresh prompt.`);
        }
        return { ok: false, reason: 'recoverable-fault', fault };
      }
      stopRun(`ChatGPT shows a non-recoverable ${fault.kind} condition.`, { error: fault });
      return { ok: false, reason: fault.kind, fault };
    }
    const dialogs = visibleDialogObservation();
    if (dialogs.blocking) {
      setPhase('DIALOG_HOLD', 'A visible dialog is present. qomrade will not send through it and will not dismiss it.');
      scheduleTick(replyPollMs(), 'dialog hold');
      return { ok: false, reason: 'dialog', dialogs };
    }
    const continuation = continuationObservation();
    if (continuation.available) {
      setPhase('CONTINUATION_HOLD', 'ChatGPT offers Continue/Keep generating. qomrade will not send through it and will not click it.');
      scheduleTick(replyPollMs(), 'pre-existing continuation hold');
      return { ok: false, reason: 'continuation', continuation };
    }
    const faultBypass = replayAllowed || nextTurnAllowed;
    const work = workEvidenceObservation({ scope: faultBypass ? 'active-response' : 'all' });
    if (!faultBypass && work.overlapHazard) {
      stopRun('A later user turn exists beneath unresolved structural qCoT/tool work. qomrade halted for possible overlap.', {
        error: { kind: 'qcot-overlap', work },
      });
      return { ok: false, reason: 'qcot-overlap', work };
    }
    if (!faultBypass && work.blocking) {
      setPhase('WORK_HOLD', 'Unresolved structural qCoT/tool work exists. qomrade will wait and will not send, reload, or click Continue.');
      scheduleTick(replyPollMs(), 'existing work hold');
      return { ok: false, reason: 'work-hold', work };
    }
    return { ok: true, barrier, dialogs, work,
      preservedFaultWork: faultBypass && work.blocking ? { signature: work.signature, unresolved: work.unresolved.length } : null,
      preexistingFailureAdvance: nextTurnAllowed ? state.faultRecovery.preexistingAdvance : null };
    });
  }
  function transactionBaseline(beforeTurns, beforeAssistant) {
    const preMaxOrdinal = beforeTurns.reduce((maximum, turn) => turn.ordinal == null ? maximum : maximum == null ? turn.ordinal : Math.max(maximum, turn.ordinal), null);
    return {
      turns: beforeTurns,
      turnIds: beforeTurns.map(turn => turn.id),
      turnCount: beforeTurns.length,
      preMaxOrdinal,
      assistantId: beforeAssistant ? beforeAssistant.id : null,
      assistantFingerprint: beforeAssistant ? beforeAssistant.fingerprint : null,
    };
  }
  function observePreClickAdvance(baseline, prompt, origin = 'composer-transaction') {
    return withReadSnapshot('observePreClickAdvance', () => {
    invalidateTurnCache(`pre-click-advance:${origin}`);
    const turns = materializedTurns();
    const priorIds = new Set(baseline.turnIds || []);
    const newTurns = turns.filter(turn => !priorIds.has(turn.id) && (turn.ordinal == null || baseline.preMaxOrdinal == null || turn.ordinal > baseline.preMaxOrdinal));
    const newUsers = newTurns.filter(turn => turn.role === 'user');
    let matchedUserTurn = null;
    let match = null;
    for (const turn of newUsers) {
      const candidateMatch = compareRenderedPrompt(turnText(turn.element), prompt);
      if (candidateMatch.ok) {
        matchedUserTurn = turn;
        match = candidateMatch;
        break;
      }
    }
    const assistant = latestAssistantTurn();
    const assistantAdvanced = !!(assistant && assistant.id !== baseline.assistantId && (!baseline.assistantFingerprint || assistant.fingerprint !== baseline.assistantFingerprint));
    const generating = !!findStopButton();
    // A late assistant identity/materialization change is not a submitted user turn.
    // Preserve duplicate prevention for real new turns and active generation, but let
    // the caller rebaseline this narrow assistant-only case before continuing.
    const assistantOnlyAdvance = !!(assistantAdvanced && !generating && newTurns.length === 0 && !matchedUserTurn);
    return {
      schema: 'qomrade.pre-click-advance-observation.v2',
      at: nowIso(),
      origin,
      advanced: !!matchedUserTurn || newTurns.length > 0 || assistantAdvanced || generating,
      safeMatch: !!matchedUserTurn,
      generating,
      assistantAdvanced,
      assistantOnlyAdvance,
      latestAssistantId: assistant && assistant.id || null,
      latestAssistantFingerprint: assistant && assistant.fingerprint || null,
      newTurnCount: newTurns.length,
      newTurns: newTurns.slice(0, 8).map(turn => {
        const text = turnText(turn.element);
        return { id: turn.id, ordinal: turn.ordinal, role: turn.role, chars: text.length, textHash: fnv1a64(text), head: trunc(normalizeCompactText(text), 240) };
      }),
      matchedUserTurn: matchedUserTurn ? { id: matchedUserTurn.id, ordinal: matchedUserTurn.ordinal, text: turnText(matchedUserTurn.element) } : null,
      match,
    };
    });
  }
  function rebaselineAssistantOnlyPreClickAdvance(baseline, observation, origin) {
    if (!observation?.assistantOnlyAdvance) return observation;
    const turns = materializedTurns();
    const assistant = latestAssistantTurn();
    const next = transactionBaseline(turns, assistant);
    baseline.turns = next.turns;
    baseline.turnIds = next.turnIds;
    baseline.turnCount = next.turnCount;
    baseline.preMaxOrdinal = next.preMaxOrdinal;
    baseline.assistantId = next.assistantId;
    baseline.assistantFingerprint = next.assistantFingerprint;
    const rebaselined = {
      ...observation,
      advanced: false,
      rebaselined: true,
      rebaseline: {
        origin,
        assistantId: baseline.assistantId,
        assistantFingerprint: baseline.assistantFingerprint,
        turnCount: baseline.turnCount,
        preMaxOrdinal: baseline.preMaxOrdinal,
      },
    };
    logEvent('pre-click-assistant-rebaseline', 'A late assistant identity/materialization change appeared before Send. No new user turn or generation was present, so qomrade rebaselined and continued.', rebaselined.rebaseline);
    return rebaselined;
  }
  async function settlePreClickAdvance(baseline, prompt, origin, guard = null) {
    effectCheckpoint(guard, `advance:${origin}`);
    let observation = observePreClickAdvance(baseline, prompt, origin);
    if (observation.assistantOnlyAdvance) return rebaselineAssistantOnlyPreClickAdvance(baseline, observation, origin);
    if (!observation.advanced || observation.safeMatch) return observation;
    const deadline = Date.now() + PRE_CLICK_ADVANCE_SETTLE_MS;
    while (Date.now() < deadline) {
      await effectWait(PRE_CLICK_ADVANCE_POLL_MS, guard, `advance:${origin}`);
      observation = observePreClickAdvance(baseline, prompt, origin);
      if (observation.assistantOnlyAdvance) return rebaselineAssistantOnlyPreClickAdvance(baseline, observation, origin);
      if (observation.safeMatch) return observation;
      if (!observation.advanced) return observation;
    }
    return observation;
  }
  function buildSendTransaction(model, insertion, baseline) {
    const startedT = Date.now();
    const custody = insertion && insertion.custody || editorPromptPayload(state.runPrompt);
    return {
      schema: 'qomrade.send-transaction.v2',
      id: `send-${startedT.toString(36)}-${state.sends + state.adoptedWithoutClick + 1}`,
      startedAt: nowIso(),
      clickedAt: null,
      clickMode: 'pending',
      promptChars: state.runPrompt.length,
      promptHash: fnv1a64(state.runPrompt),
      editorPayloadChars: custody.payloadChars,
      editorPayloadHash: custody.payloadHash,
      terminalNewlinesRemoved: custody.terminalNewlinesRemoved,
      model: { label: model.label, selectedLabel: model.selectedLabel || null, routeKey: model.routeKey || null, family: model.family, version: model.version || null, hasPro: model.hasPro, policy: model.policy || state.modelGate.runPolicy, target: model.target || null, effort: model.effort || null },
      modelPolicy: state.modelGate.runPolicy || MODEL_POLICY_SMART_PRO,
      modelTarget: state.modelGate.target ? { ...state.modelGate.target } : null,
      modelPreference: state.modelGate.runPreference || '5.6-first',
      insertionMethod: insertion && insertion.method || null,
      insertionAttempts: insertion && insertion.attempts || [],
      composerObservedHash: fnv1a64(normalizeForEditorCompare(insertion && insertion.observed || '')),
      preTurnCount: baseline.turnCount,
      preTurnIds: baseline.turnIds,
      preMaxOrdinal: baseline.preMaxOrdinal,
      baselineAssistantId: baseline.assistantId,
      userTurnId: null,
      userTurnOrdinal: null,
      userAdoptedAt: null,
      assistantTurnId: null,
      outcome: null,
      authority: 'pending witnessed transaction; no Send authority after any pre-click conversation advance',
    };
  }
  function enterWaitingReplyCustody(transaction, effectiveAtT) {
    attachRecoveryReplayLineage(transaction);
    attachPreexistingFailureAdvance(transaction);
    state.activeSend = transaction;
    state.modelAtSend = transaction.model;
    state.baselineAssistantId = transaction.baselineAssistantId;
    state.latestAssistantId = null;
    state.latestAssistantFingerprint = null;
    state.stableSamples = 0;
    state.lastError = null;
    state.lastSendAt = effectiveAtT;
    state.waitingSince = effectiveAtT;
    state.nextSendAt = effectiveAtT + Math.round(settings.gapMinutes * 60_000);
  }
  function syncTransactionPreClickBaseline(transaction, baseline) {
    if (!transaction || !baseline) return transaction;
    transaction.preTurnCount = baseline.turnCount;
    transaction.preTurnIds = Array.isArray(baseline.turnIds) ? baseline.turnIds.slice() : [];
    transaction.preMaxOrdinal = baseline.preMaxOrdinal;
    transaction.baselineAssistantId = baseline.assistantId;
    transaction.baselineAssistantFingerprint = baseline.assistantFingerprint;
    return transaction;
  }
  function adoptPreClickAdvance(transaction, observation, origin) {
    const matched = observation && observation.matchedUserTurn;
    if (!matched || !observation.safeMatch) return false;
    const effectiveAtT = Date.now();
    transaction.clickMode = 'suppressed-after-pre-click-advance';
    transaction.clickSuppressedAt = nowIso();
    transaction.clickSuppressedReason = 'a conservatively matching user turn materialized before qomrade clicked Send';
    transaction.preClickAdvance = observation;
    transaction.userTurnId = matched.id;
    transaction.userTurnOrdinal = matched.ordinal;
    transaction.userAdoptedAt = nowIso();
    transaction.userTextHash = fnv1a64(matched.text || '');
    transaction.userTextChars = (matched.text || '').length;
    transaction.userAdoptionMatch = observation.match && observation.match.kind || 'conservative-rendered-match';
    transaction.authority = 'no Send click; matching pre-click conversation advance adopted under duplicate-prevention custody';
    state.adoptedWithoutClick += 1;
    enterWaitingReplyCustody(transaction, effectiveAtT);
    logEvent('pre-click-advance-adopted', 'A matching user turn appeared before qomrade clicked Send. Send was suppressed and the existing turn was adopted.', { transactionId: transaction.id, origin, observation });
    persistContinuity('pre-click-advance-adopted');
    setPhase('WAITING_REPLY', 'A matching user turn appeared before qomrade clicked Send; duplicate Send was suppressed and qomrade is observing the reply.');
    scheduleTick(replyPollMs(), 'pre-click advance adopted');
    return true;
  }
  function haltForUnattributedPreClickAdvance(observation, insertion, origin) {
    state.preClickAdvanceHolds += 1;
    stopRun('The conversation advanced before qomrade clicked Send, but no conservatively matching new user turn could be attributed. qomrade stopped without resending.', {
      error: {
        kind: 'pre-click-advance-unattributed',
        origin,
        observation,
        insertion: insertion ? { method: insertion.method || null, attempts: insertion.attempts || [], custody: insertion.custody || null, observed: trunc(insertion.observed || '', 500) } : null,
        duplicatePrevention: true,
      },
    });
  }
  async function sendPrompt() {
    if (!state.running || state.paused || state.quarantine) return;
    const recoveryReplay = !!(recoveryReplayPermit && !recoveryReplayPermit.consumed);
    const entryNow = Date.now();
    if (!recoveryReplay && state.nextSendAt && entryNow < state.nextSendAt) {
      setPhase('WAITING_GAP', 'The hard send-cadence invariant deferred an early ordinary Send.');
      scheduleGapTick();
      return;
    }
    if (!recoveryReplay && state.lastSendAt && entryNow - state.lastSendAt < MIN_SEND_CLICK_FLOOR_MS) {
      const remainingFloor = Math.max(500, MIN_SEND_CLICK_FLOOR_MS - (entryNow - state.lastSendAt));
      setPhase('WAITING_GAP', 'The hard minimum click floor deferred a near-duplicate Send.');
      scheduleTick(remainingFloor, 'hard send click floor');
      return;
    }
    const guard = createEffectGuard();
    const prompt = state.runPrompt;
    let modelWitness = null;
    try {
    if (panelEditorFocused()) {
      if (state.phase !== 'PANEL_EDIT_HOLD') {
        state.metrics.panelEditHolds += 1;
        logEvent('panel-edit-hold', 'Deferred ChatGPT composer focus and Send while a qomrade editor owns focus.', panelFocusObservation());
      }
      clearControllerTimer('operator panel editor owns focus');
      setPhase('PANEL_EDIT_HOLD', 'A qomrade text or number editor has focus. Composer focus and Send are deferred until the operator leaves that editor.');
      return;
    }
    if (!validateConversationAnchor()) return;
    const interlock = preEffectInterlock('before-send');
    if (!interlock.ok) return;
    if (findStopButton()) {
      setPhase('WAITING_FOR_IDLE', 'ChatGPT is already generating; qomrade will not send over it.');
      scheduleTick(replyPollMs(), 'wait for idle');
      return;
    }
    const policySnapshot = activeModelPolicySnapshot();
    const modelPreference = policySnapshot.policy === MODEL_POLICY_SMART_PRO
      ? (recoveryReplayPermit?.modelPreference || state.modelGate.runPreference || '5.6-first')
      : state.modelGate.runPreference;
    const modelGate = await ensureConfiguredModel(
      policySnapshot.policy === MODEL_POLICY_SMART_PRO && modelPreference === '6-fallback'
        ? 'GPT-6 fallback after GPT-5.6 failure'
        : 'before every send',
      guard, modelPreference);
    effectCheckpoint(guard, 'after-model-selection');
    invalidateTurnCache('after-model-selection');
    if (!modelGate.ok) {
      setPhase('MODEL_HOLD', modelGate.reason);
      captureBoundedSciencePulse('model-hold', { assistant: latestAssistantTurn() });
      const retryAt = modelGate.retryAt || (Date.now() + MODEL_RECHECK_MS);
      scheduleTick(Math.max(1_000, retryAt - Date.now()), 'bounded model hold');
      return;
    }
    modelWitness = captureSendModelWitness(modelGate, guard);
    const postModelInterlock = preEffectInterlock('after-model-selection');
    if (!postModelInterlock.ok) return;
    const model = {
      label: modelGate.confirmation.concreteLabel || modelGate.confirmation.selectedLabel || modelGate.confirmation.candidate,
      selectedLabel: modelGate.confirmation.selectedLabel || null,
      routeKey: modelGate.confirmation.routeKey || modelRouteKey(modelGate.confirmation.selectedLabel || modelGate.confirmation.candidate),
      family: modelGate.confirmation.family,
      version: modelGate.confirmation.version,
      hasPro: !!modelGate.confirmation.hasPro,
      policy: modelGate.confirmation.policy || policySnapshot.policy,
      target: modelGate.confirmation.target || policySnapshot.target,
      effort: modelGate.confirmation.effort || null,
      pill: modelGate.confirmation.pill,
      evidence: modelGate.confirmation.evidence,
    };
    const composer = findComposer();
    if (!composer) {
      captureDomishEvent('composer-surface-missing', {
        reason: 'ChatGPT composer not found before an authorized Send',
        severity: 'warn',
        origin: 'send-preflight',
        key: fnv1a64(JSON.stringify(['composer-missing', state.phase, !!findModelButton(), materializedTurns().length, document.readyState])),
        context: { phase: state.phase, phaseReason: state.phaseReason, modelGate: { policy: policySnapshot.policy, preference: modelPreference, target: policySnapshot.target, ok: modelGate.ok, reason: modelGate.reason } },
      });
      setPhase('SURFACE_HOLD', 'ChatGPT composer not found; waiting for the current UI to settle.');
      scheduleTick(replyPollMs(), 'surface hold');
      return;
    }
    const beforeTurns = materializedTurns();
    const beforeAssistant = latestAssistantTurn();
    const baseline = transactionBaseline(beforeTurns, beforeAssistant);
    const insertion = await insertExactPrompt(composer, prompt, {
      guard,
      observeAdvance: origin => settlePreClickAdvance(baseline, prompt, `after-${origin}`, guard),
    });
    effectCheckpoint(guard, 'after-insertion');
    let transaction = buildSendTransaction(model, insertion, baseline);
    if (insertion.advanced && insertion.advance) {
      if (adoptPreClickAdvance(transaction, insertion.advance, `during-${insertion.method || 'insertion'}`)) return;
      haltForUnattributedPreClickAdvance(insertion.advance, insertion, `during-${insertion.method || 'insertion'}`);
      return;
    }
    if (!insertion.ok) {
      const afterFailure = await settlePreClickAdvance(baseline, prompt, 'after-insertion-failure', guard);
      syncTransactionPreClickBaseline(transaction, baseline);
      if (afterFailure.advanced) {
        if (adoptPreClickAdvance(transaction, afterFailure, 'after-insertion-failure')) return;
        haltForUnattributedPreClickAdvance(afterFailure, insertion, 'after-insertion-failure');
        return;
      }
      stopRun(`Prompt insertion stopped: ${insertion.reason}`, { error: { kind: 'prompt-insertion', ...insertion, composer: elementSummary(composer, { redactContent: true }) } });
      return;
    }
    let advance = await settlePreClickAdvance(baseline, prompt, 'after-exact-insertion', guard);
    syncTransactionPreClickBaseline(transaction, baseline);
    if (advance.advanced) {
      if (adoptPreClickAdvance(transaction, advance, 'after-exact-insertion')) return;
      haltForUnattributedPreClickAdvance(advance, insertion, 'after-exact-insertion');
      return;
    }
    const sendButton = await waitForSendButton(SEND_BUTTON_WAIT_MS, guard);
    advance = await settlePreClickAdvance(baseline, prompt, 'while-waiting-for-send-control', guard);
    syncTransactionPreClickBaseline(transaction, baseline);
    if (advance.advanced) {
      if (adoptPreClickAdvance(transaction, advance, 'while-waiting-for-send-control')) return;
      haltForUnattributedPreClickAdvance(advance, insertion, 'while-waiting-for-send-control');
      return;
    }
    if (!sendButton) {
      stopRun('Prompt was inserted exactly, but the Send control was not found. The text was left in the composer for the operator.', {
        error: { kind: 'send-control-missing', insertionMethod: insertion.method, insertionAttempts: insertion.attempts, controls: currentControlsObservation() },
      });
      return;
    }
    const finalObserved = readComposerText(composer);
    if (!editorPayloadEquivalent(finalObserved, insertion.custody.payload).ok) {
      advance = await settlePreClickAdvance(baseline, prompt, 'composer-changed-before-click', guard);
      syncTransactionPreClickBaseline(transaction, baseline);
      if (advance.advanced) {
        if (adoptPreClickAdvance(transaction, advance, 'composer-changed-before-click')) return;
        haltForUnattributedPreClickAdvance(advance, insertion, 'composer-changed-before-click');
        return;
      }
      stopRun('Composer equality changed after insertion and before Send. qomrade stopped without clicking Send.', {
        error: { kind: 'composer-drift-before-send', observed: trunc(finalObserved, 500), observedHash: fnv1a64(finalObserved), expectedPayloadHash: insertion.custody.payloadHash, insertionAttempts: insertion.attempts },
      });
      return;
    }
    if (!state.running || state.paused || state.quarantine) return;
    advance = await settlePreClickAdvance(baseline, prompt, 'immediately-before-send-click', guard);
    syncTransactionPreClickBaseline(transaction, baseline);
    if (advance.advanced) {
      if (adoptPreClickAdvance(transaction, advance, 'immediately-before-send-click')) return;
      haltForUnattributedPreClickAdvance(advance, insertion, 'immediately-before-send-click');
      return;
    }
    effectCheckpoint(guard, 'send-commit');
    invalidateTurnCache('send-commit');
    const finalInterlock = preEffectInterlock('immediately-before-send-click');
    if (!finalInterlock.ok) return;
    effectCheckpoint(guard, 'send-commit-after-interlocks');
    const liveComposer = findComposer();
    const liveSend = findSendButton();
    const liveModel = observeSendModelCommit(modelWitness, guard);
    const changed = !composer.isConnected || liveComposer !== composer ? 'composer-replaced'
      : !editorPayloadEquivalent(readComposerText(composer), insertion.custody.payload).ok ? 'composer-drift-before-send'
      : !sendButton.isConnected || liveSend !== sendButton || !isEnabled(sendButton) ? 'send-control-replaced-or-disabled'
      : findStopButton() ? 'generation-became-active'
      : !liveModel.ok ? 'model-drift-before-send' : null;
    if (changed) {
      stopRun('The live send surface changed after settlement; no Send was clicked and composer text was left untouched.', { error: { kind: changed, operationId: guard.operation.id, modelCommit: liveModel, draftDisposition: 'left-unchanged' } });
      return;
    }
    const commitNow = Date.now();
    const commitRecoveryReplay = !!(recoveryReplayPermit && !recoveryReplayPermit.consumed);
    const cadenceViolation = (!commitRecoveryReplay && state.nextSendAt && commitNow < state.nextSendAt) ? 'ordinary-next-send-not-reached'
      : !commitRecoveryReplay && state.lastSendAt && commitNow - state.lastSendAt < MIN_SEND_CLICK_FLOOR_MS ? 'minimum-click-floor' : null;
    if (cadenceViolation) {
      stopRun('The final synchronous Send commit detected a cadence violation. No Send was clicked; the exact composer text was left for inspection.', {
        error: { kind: 'send-cadence-invariant', violation: cadenceViolation, now: commitNow, lastSendAt: state.lastSendAt || null, nextSendAt: state.nextSendAt || null, recoveryReplay: commitRecoveryReplay, draftDisposition: 'left-unchanged' },
      });
      return;
    }
    // Atomic cooperative commit: no await may be inserted below this check.
    effectCheckpoint(guard, 'send-click');
    const clickedAtT = Date.now();
    transaction.modelCommit = liveModel;
    transaction.sendButton = elementSummary(sendButton);
    transaction.sendRoute = selectorRoute(sendButton, SELECTORS.send);
    transaction.authority = 'one exact click attempt for the captured prompt after repeated no-advance checks';
    transaction.clickMode = 'qomrade-send-button-click';
    enterWaitingReplyCustody(transaction, clickedAtT);
    state.sends += 1;
    if (document.hidden) state.background.hiddenSends += 1;
    logEvent('send-intent', 'Exact prompt, visible model, structured composer equality, no pre-click advance, and Send control were witnessed before click.', transaction);
    sendButton.click();
    invalidateTurnCache('send-click');
    transaction.clickedAt = nowIso();
    logEvent('send-click', 'Activated the witnessed Send control once.', { transactionId: transaction.id, clickedAt: transaction.clickedAt });
    persistContinuity('send-click');
    effectCheckpoint(guard, 'send-click-returned');
    setPhase('WAITING_REPLY', 'Exact prompt Send was activated; waiting for user-turn adoption and a stable completed assistant turn.');
    scheduleTick(replyPollMs(), 'wait for reply');
    } catch (error) {
      if (!error || !error.qomradeEffectCancelled) {
        try { effectCheckpoint(guard, 'operation-rejected'); }
        catch (cancelled) {
          if (!cancelled || !cancelled.qomradeEffectCancelled) throw cancelled;
          cancelled.receipt.interruptedError = trunc(String(error && error.message || error), 800);
          recordEffectCancellation(cancelled);
          return;
        }
        throw error;
      }
      recordEffectCancellation(error);
    } finally {
      if (modelWitness) modelWitness.release();
      if (state.effectControl.active && state.effectControl.active.id === guard.operation.id) state.effectControl.active = null;
    }
  }
  function resetSmartProFallbackAfterSuccess(receipt) {
    if (state.modelGate.runPolicy !== MODEL_POLICY_SMART_PRO || state.modelGate.runPreference !== '6-fallback') return null;
    const previous = state.modelGate.lastPreferenceSwitch ? JSON.parse(JSON.stringify(state.modelGate.lastPreferenceSwitch)) : null;
    const reset = {
      at: nowIso(),
      from: '6-fallback',
      to: '5.6-first',
      reason: 'a stable assistant reply completed; Smart Pro returns the next ordinary turn to GPT-5.6 first',
      completedTransactionId: receipt && receipt.id || null,
      completedModel: receipt && receipt.model ? {
        label: receipt.model.label || null,
        selectedLabel: receipt.model.selectedLabel || null,
        family: receipt.model.family == null ? null : receipt.model.family,
        version: Array.isArray(receipt.model.version) ? receipt.model.version.slice() : null,
      } : null,
      previous,
      scope: 'fallback-lineage-ended-by-success',
    };
    state.modelGate.runPreference = '5.6-first';
    state.modelGate.lastPreferenceSwitch = reset;
    logEvent('model-fallback-cleared', 'A stable reply completed; Smart Pro will probe GPT-5.6 first on the next ordinary turn.', reset);
    return reset;
  }
  function assistantModelSlugObservation(assistant) {
    const element = assistant?.element;
    if (!element) return { available: false, slugs: [], authority: 'evidence-only; not backend attestation' };
    const nodes = [element, ...qa('[data-message-model-slug]', element)];
    const slugs = [...new Set(nodes.map(node => node.getAttribute && node.getAttribute('data-message-model-slug')).filter(Boolean))].slice(0, 8);
    return { available: slugs.length > 0, slugs, authority: 'DOM attribute evidence only; never overrides send-local model proof' };
  }
  function finalizeTurnReceipt(assistant, outcome = 'reply-complete') {
    captureActiveSendAdoption();
    const active = state.activeSend;
    if (!active) return null;
    active.assistantTurnId = assistant ? assistant.id : null;
    active.assistantTurnOrdinal = assistant ? assistant.ordinal : null;
    active.assistantAdapter = assistant ? assistant.adapter : null;
    active.assistantTextChars = assistant ? assistant.text.length : null;
    active.assistantTextHash = assistant ? fnv1a64(assistant.text) : null;
    active.assistantModelSlug = assistantModelSlugObservation(assistant);
    active.completedAt = nowIso();
    active.outcome = outcome;
    const receipt = JSON.parse(JSON.stringify(active));
    state.turnReceipts.push(receipt);
    if (state.turnReceipts.length > MAX_TURN_RECEIPTS) state.turnReceipts.splice(0, state.turnReceipts.length - MAX_TURN_RECEIPTS);
    state.activeSend = null;
    return receipt;
  }
  function observeReply() {
    return withReadSnapshot('observeReply', () => {
    captureActiveSendAdoption();
    const generating = !!findStopButton();
    const terminalBarrier = conversationBarrierObservation({ includeProse: !generating });
    if (terminalBarrier.present) {
      stopForConversationTerminal(terminalBarrier, 'reply-observation');
      return { terminal: terminalBarrier };
    }
    if (recoveryNow() < state.faultRecovery.postReloadUntil) {
      recoveryHold('Waiting for the post-reload quiet window; no completion or new prompt yet.', replyPollMs());
      return;
    }
    if (state.faultRecovery.postReloadWitness && !materializedTurns().some(turn => turn.role === 'user' && turn.id === state.activeSend?.userTurnId)) {
      state.faultRecovery.postReloadWitness.verdict = 'request-not-materialized';
      state.faultRecovery.postReloadWitness.observedAt = nowIso();
      recoveryHold('The saved request is not materialized after reload. Its disappearance never authorizes a blind resend.');
      return;
    }
    let assistant = latestAssistantTurn({ readText: !generating });
    const recoveryObservation = pipelineFaultObservation(assistant);
    const error = recoveryObservation.current;
    if (error && error.kind === 'generation-error') return { recover: recoveryObservation };
    if (!error) noteRecoveryFaultCleared();
    if (error) {
      captureBoundedSciencePulse('reply-error', { assistant, error });
      markActiveSendOutcome(error.kind, error);
      const reason = error.kind === 'submission-too-large'
        ? 'ChatGPT rejected this submission as too long. qomrade stopped without treating the conversation as exhausted.'
        : error.kind === 'conversation-maximum'
          ? 'ChatGPT reported a terminal conversation boundary.'
          : `ChatGPT showed a non-recoverable submission fault: ${error.faultKind || error.kind}.`;
      if (error.kind === 'conversation-maximum') stopForConversationTerminal(conversationBarrierObservation(), 'reply-fault');
      else stopRun(reason, { error });
      return;
    }
    const work = workEvidenceObservation({ scope: 'active-response' });
    if (work.overlapHazard) {
      stopRun('A later user turn exists beneath unresolved structural qCoT/tool work. qomrade halted for possible overlap.', { error: { kind: 'qcot-overlap', work } });
      return;
    }
    const continuation = continuationObservation(assistant);
    if (continuation.available) {
      state.stableSamples = 0;
      setPhase('CONTINUATION_HOLD', 'ChatGPT offers Continue/Keep generating. qomrade will not click it or accept this reply as complete.');
      scheduleTick(replyPollMs(), 'continuation hold');
      return;
    }
    captureBoundedSciencePulse('reply-observation', { assistant, error: null, work, continuation, generating });
    const isNewAssistant = assistant && assistant.id !== state.baselineAssistantId;
    if (!isNewAssistant) {
      state.stableSamples = 0;
      setPhase(state.phase === 'WORK_HOLD' ? 'WORK_HOLD' : 'WAITING_REPLY', generating ? 'ChatGPT is generating.' : work.blocking ? 'Unresolved structural work remains visible.' : 'Waiting for a new assistant turn to appear.');
      scheduleTick(replyPollMs(), 'wait for new assistant');
      return;
    }
    const adoptedUser = state.activeSend && materializedTurns().find(turn => turn.role === 'user' && turn.id === state.activeSend.userTurnId);
    if (state.activeSend && (!adoptedUser || assistant.index <= adoptedUser.index)) {
      state.stableSamples = 0;
      setPhase('WAITING_REPLY', 'An assistant turn is visible, but it does not follow the stable adopted user in materialized thread order.');
      scheduleTick(replyPollMs(), 'assistant ownership hold');
      return;
    }
    if (generating) {
      state.stableSamples = 0;
      setPhase('WAITING_REPLY', 'ChatGPT is generating; the newest assistant turn is not complete.');
      scheduleTick(replyPollMs(), 'generation active');
      return;
    }
    assistant = hydrateAssistantTurnText(assistant);
    if (state.latestAssistantId !== assistant.id || state.latestAssistantFingerprint !== assistant.fingerprint) {
      state.latestAssistantId = assistant.id;
      state.latestAssistantFingerprint = assistant.fingerprint;
      state.stableSamples = 1;
    } else state.stableSamples += 1;
    if (assistant.workOnly || work.blocking) {
      state.stableSamples = 0;
      setPhase('WORK_HOLD', 'Structural qCoT/tool work is visible without final-answer evidence. qomrade will wait and will not reload or resend.');
      scheduleTick(replyPollMs(), 'work hold');
      return;
    }
    if (!assistant.text || state.stableSamples < COMPLETION_STABLE_SAMPLES) {
      setPhase('WAITING_REPLY', `Assistant turn found; confirming stability (${state.stableSamples}/${COMPLETION_STABLE_SAMPLES}).`);
      scheduleTick(replyPollMs(), 'stability confirmation');
      return;
    }
    const modelNow = currentModelObservation();
    if (state.modelAtSend && modelNow.label && modelNow.label !== state.modelAtSend.label) {
      if (modelNow.transient && !modelNow.family) {
        state.modelGate.transientLabelsIgnored += 1;
        const edge = { at: nowIso(), kind: 'effort-only-or-menu-transient', from: state.modelAtSend, visibleLabel: modelNow.label, transactionId: state.activeSend && state.activeSend.id };
        state.modelIndicatorEdges.push(edge);
        if (state.modelIndicatorEdges.length > 20) state.modelIndicatorEdges.splice(0, state.modelIndicatorEdges.length - 20);
        logEvent('model-indicator-transient', 'An effort-only model control label was retained as evidence but not promoted to model-family drift.', edge);
      } else if (modelNow.family != null || modelNow.hasPro) {
        const drift = { at: nowIso(), from: state.modelAtSend, to: { label: modelNow.label, family: modelNow.family, hasPro: modelNow.hasPro }, transactionId: state.activeSend && state.activeSend.id };
        state.modelDrifts.push(drift);
        if (state.modelDrifts.length > 20) state.modelDrifts.splice(0, state.modelDrifts.length - 20);
        logEvent('model-drift', 'Concrete visible model evidence changed between Send and reply completion.', drift);
      }
    }
    const recoveredEntry = state.faultRecovery.ledger.find(item => item.key === state.activeSend?.recoveryRootKey);
    if (recoveredEntry) {
      recoveryOutcome(recoveredEntry, 'reply-complete-after-recovery', { assistantId: assistant.id });
      state.faultRecovery.activeKey = null;
      if (state.faultRecovery.postReloadWitness) state.faultRecovery.postReloadWitness.verdict = 'completed-reply-observed';
    }
    captureSessionTurns('reply-complete');
    state.completedReplies += 1;
    const receipt = finalizeTurnReceipt(assistant, 'reply-complete');
    const modelPreferenceReset = resetSmartProFallbackAfterSuccess(receipt);
    logEvent('reply-complete', 'Accepted one stable assistant turn as complete.', {
      assistantId: assistant.id,
      ordinal: assistant.ordinal,
      adapter: assistant.adapter,
      textChars: assistant.text.length,
      fingerprint: assistant.fingerprint,
      transactionId: receipt && receipt.id,
      userAdopted: !!(receipt && receipt.userAdoptedAt),
      modelPreferenceReset,
    });
    captureZipFromAssistant(assistant);
    scheduleZipRescan(assistant);
    armDomTrim(1_000, 'reply-complete');
    wakeOverdueAutoRefresh('reply-complete', ['generation-advertised','zip-rescan-pending']);
    state.baselineAssistantId = assistant.id;
    state.latestAssistantId = null;
    state.latestAssistantFingerprint = null;
    state.stableSamples = 0;
    state.waitingSince = 0;
    state.nextSendAt = Math.max(state.nextSendAt, Date.now() + MIN_POST_COMPLETE_MS);
    persistContinuity('reply-complete');
    setPhase('WAITING_GAP', 'Reply complete; waiting for the send-to-send gap.');
    scheduleGapTick();
    });
  }
  function scheduleGapTick() {
    if (!state.running || state.paused || state.quarantine) return;
    const remaining = Math.max(0, state.nextSendAt - Date.now());
    scheduleTick(Math.min(gapPollMs(), Math.max(500, remaining)), 'waiting gap');
  }
  async function tick() {
    invalidateTurnCache('controller-tick');
    if (!state.running || state.paused || state.quarantine) return;
    if (state.sessionArchive.backfill?.active) { scheduleTick(1_000, 'session-history-backfill'); return; }
    if (state.tickBusy) {
      state.scheduler.skippedBusy += 1;
      state.scheduler.pendingWake = { epoch: state.effectControl.epoch, requestedAt: nowIso() };
      return;
    }
    state.tickBusy = true;
    if (document.hidden) { state.background.hiddenTicks += 1; state.background.lastHiddenTickAt = nowIso(); }
    else { state.background.visibleTicks += 1; state.background.lastVisibleTickAt = nowIso(); }
    recordBackgroundEdge('controller-tick');
    const started = performance.now();
    const queriesBefore = state.metrics.selectorQueries;
    try {
      if (!isEligibleRoute()) {
        stopRun('Qomrade stopped because this is not an eligible ChatGPT chat route.', { error: { kind: 'ineligible-route', pathname: location.pathname } });
        return;
      }
      if (!validateConversationAnchor()) return;
      if (enforceHardFalseGui('controller-tick')) return;
      const terminalBarrier = conversationBarrierObservation();
      if (terminalBarrier.present) {
        stopForConversationTerminal(terminalBarrier, 'controller-tick');
        return;
      }
      if (pauseForHidden() && document.hidden) {
        clearControllerTimer('hidden-tab hold');
        render();
        return;
      }
      if (!resolveAutoRefreshRestore()) return;
      if (settings.hourlyRefresh && state.autoRefresh.dueAt && Date.now() >= state.autoRefresh.dueAt && Date.now() >= (state.autoRefresh.retryAt || 0)) {
        armAutoRefresh('controller-overdue');
      }
      const tickFaultObservation = pipelineFaultObservation();
      if (!state.activeSend) {
        const deferredFailure = tickFaultObservation;
        if (deferredFailure.current?.kind === 'generation-error') {
          if (tryAdoptExistingFailedRequest(deferredFailure, 'post-completion-red-letter')) await handlePipelineFault(pipelineFaultObservation());
          else { const advance = settlePreexistingFailureAdvance(deferredFailure, 'controller-no-active-request');
            if (advance.ready) await sendPrompt();
            else if (!advance.handled) recoveryHold('A current red-letter failure is visible; waiting for stable request identity before any fresh prompt.'); }
          return;
        }
      }
      if (tickFaultObservation.current?.kind !== 'generation-error') {
        const advance = state.faultRecovery.preexistingAdvance;
        if (advance && !['committed','fault-cleared-before-next-turn'].includes(advance.status)) {
          advance.status = 'fault-cleared-before-next-turn'; advance.clearedAt = nowIso(); advance.blocked = null; preexistingFailureAdvancePermit = null;
          logEvent('preexisting-failure-cleared', 'The different-request failure cleared before the configured next turn; ordinary run policy resumes.', { key: advance.key, userId: advance.userId });
        }
        const maintenanceSurface = visiblePageShellMaintenanceSurface('controller-tick');
        if (maintenanceSurface && holdForPageShellMaintenance(maintenanceSurface, 'controller-tick')) return;
      }
      if (state.phase === 'CONTINUATION_HOLD' && !state.activeSend) {
        const continuation = continuationObservation();
        if (continuation.available) {
          render();
          scheduleTick(replyPollMs(), 'pre-existing continuation remains visible');
          return;
        }
        setPhase('READY_TO_SEND', 'The pre-existing Continue/Keep generating control is gone; pre-send checks will run again.');
      }
      if (state.phase === 'WORK_HOLD' && !state.activeSend) {
        const failure = pipelineFaultObservation();
        if (failure.current?.kind === 'generation-error') {
          if (tryAdoptExistingFailedRequest(failure, 'deferred-work-fault')) await handlePipelineFault(pipelineFaultObservation());
          else { const advance = settlePreexistingFailureAdvance(failure, 'deferred-work-fault');
            if (advance.ready) await sendPrompt();
            else if (!advance.handled) recoveryHold('A work failure is visible; waiting for stable request identity before any fresh prompt.'); }
          return;
        }
        const work = workEvidenceObservation();
        if (work.overlapHazard) {
          stopRun('A later user turn exists beneath unresolved structural qCoT/tool work. qomrade halted for possible overlap.', { error: { kind: 'qcot-overlap', work } });
          return;
        }
        if (work.blocking) {
          render();
          scheduleTick(replyPollMs(), 'pre-existing structural work remains visible');
          return;
        }
        setPhase('READY_TO_SEND', 'The pre-existing structural work hold cleared; pre-send checks will run again.');
      }
      if (state.activeSend && !state.activeSend.outcome) {
        const result = observeReply();
        if (result?.recover) await handlePipelineFault(result.recover);
        return;
      }
      if (state.phase === 'DIALOG_HOLD') {
        const dialogs = visibleDialogObservation();
        if (dialogs.blocking) {
          render();
          scheduleTick(replyPollMs(), 'dialog remains visible');
          return;
        }
        setPhase('READY_TO_SEND', 'The blocking dialog is no longer visible; pre-send checks will run again.');
      }
      if (state.phase === 'WAITING_GAP') {
        captureBoundedSciencePulse('waiting-gap', { assistant: latestAssistantTurn() });
        const gapMaintenance = visiblePageShellMaintenanceSurface('waiting-gap');
        if (gapMaintenance && holdForPageShellMaintenance(gapMaintenance, 'waiting-gap')) return;
        if (Date.now() < state.nextSendAt) {
          render();
          scheduleGapTick();
          return;
        }
        setPhase('READY_TO_SEND', 'Send-to-send gap elapsed.');
      }
      if (state.phase === 'WAITING_FOR_IDLE' || state.phase === 'MODEL_HOLD' || state.phase === 'SURFACE_HOLD' || state.phase === 'PANEL_EDIT_HOLD' || state.phase === 'READY_TO_SEND' || state.phase === 'DIALOG_HOLD') {
        await sendPrompt();
        return;
      }
      setPhase('READY_TO_SEND', 'Preparing the first exact send.');
      await sendPrompt();
    } catch (error) {
      recordPageError({ kind: 'qomrade-controller-error', message: String(error && error.message || error), stack: trunc(error && error.stack, 4_000) });
      stopRun(`Unexpected qomrade error: ${error && error.message || error}`, {
        error: { kind: 'unexpected', message: String(error && error.message || error), stack: trunc(error && error.stack, 4_000) },
      });
    } finally {
      const duration = Math.max(0, performance.now() - started);
      const queries = Math.max(0, state.metrics.selectorQueries - queriesBefore);
      state.metrics.ticks += 1;
      state.metrics.tickTotalMs += duration;
      state.metrics.tickLastMs = Math.round(duration * 100) / 100;
      state.metrics.tickMaxMs = Math.max(state.metrics.tickMaxMs, state.metrics.tickLastMs);
      state.metrics.tickLastQueries = queries;
      state.metrics.tickMaxQueries = Math.max(state.metrics.tickMaxQueries, queries);
      state.tickBusy = false;
      const pending = state.scheduler.pendingWake;
      state.scheduler.pendingWake = null;
      if (pending && pending.epoch === state.effectControl.epoch && state.running && !state.paused && !state.quarantine && !(pauseForHidden() && document.hidden)) {
        state.scheduler.deferredWakes += 1;
        scheduleTick(0, 'explicit wake deferred by previous operation');
      }
    }
  }
  function startReceipt(status, reason, detail = null, attemptId = null) {
    const prior = state.startTransaction;
    const id = attemptId || (prior && prior.id) || `start-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 7)}`;
    const same = !!(prior && prior.id === id);
    const updatedT = Date.now();
    const startedT = same && Number.isFinite(prior.startedT) ? prior.startedT : updatedT;
    state.startTransaction = {
      schema: 'qomrade.start-transaction.v2',
      id,
      status,
      reason,
      startedAt: same && prior.startedAt ? prior.startedAt : new Date(startedT).toISOString(),
      startedT,
      updatedAt: new Date(updatedT).toISOString(),
      updatedT,
      elapsedMs: Math.max(0, updatedT - startedT),
      conversationId: conversationIdFromPath(),
      pathname: location.pathname,
      detail: detail == null ? null : JSON.parse(JSON.stringify(detail)),
    };
    return state.startTransaction;
  }
  function refuseStart(attemptId, reason, message, detail = null, options = {}) {
    state.startRefused += 1;
    const receipt = startReceipt('refused', reason, detail, attemptId);
    if (options.error) state.lastError = options.error;
    logEvent(options.eventKind || 'start-refused', message, { receipt, detail });
    if (options.persist !== false) persistContinuity(options.persistReason || `start-refused-${reason}`);
    if (options.show !== false) showMessage(`START REFUSED — ${message}`, true);
    return receipt;
  }
  function startRun() {
    invalidateTurnCache('operator-start');
    const attemptId = `start-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 7)}`;
    state.startAttempts += 1;
    startReceipt('checking', 'operator Start received; evaluating restore, quarantine, conversation barrier, prompt custody, and scheduler admission', {
      phase: state.phase,
      running: state.running,
      tabReadStatus: state.boot.tabRead.status,
      quarantineKind: state.quarantine && state.quarantine.kind || null,
    }, attemptId);
    if (state.running) return refuseStart(attemptId, 'already-running', 'This tab already has an active qomrade run.', { phase: state.phase });
    if (state.quarantine) {
      return refuseStart(attemptId, 'quarantined', 'qomrade is OFF because this page carries the hard no-history plus 5.3 false-GUI quarantine.', { quarantine: { kind: state.quarantine.kind || null, at: state.quarantine.at || null } });
    }
    if (state.recoveryRestorePending || state.autoRefresh.restorePending || state.autoRefresh.restoreInFlight || ['not-started', 'in-flight'].includes(state.boot.tabRead.status)) {
      return refuseStart(attemptId, 'tab-restore-pending', "qomrade is still restoring this tab's bounded settings. Start will be available when that read settles.", { tabRead: { status: state.boot.tabRead.status, timeoutMs: state.boot.tabRead.timeoutMs } }, { persist: false });
    }
    if (enforceHardFalseGui('operator-start', { detail: true })) {
      return refuseStart(attemptId, 'hard-false-gui', state.phaseReason || 'The hard no-history plus 5.3 surface was detected.', { quarantine: state.quarantine ? { kind: state.quarantine.kind || null, at: state.quarantine.at || null } : null }, { show: false, persistReason: 'start-refused-hard-false-gui' });
    }
    const barrier = conversationBarrierObservation();
    if (barrier.present) {
      stopForConversationTerminal(barrier, 'start-interlock');
      return refuseStart(attemptId, 'conversation-terminal', state.phaseReason, { barrier, terminal: state.terminalStop }, {
        eventKind: 'start-refused-conversation-terminal', persistReason: 'start-refused-conversation-terminal', show: true,
      });
    }
    markOperatorInteraction('start');
    const prompt = normalizePromptLineEndings(settings.prompt);
    if (!prompt) {
      return refuseStart(attemptId, 'missing-prompt', 'Enter one exact prompt before starting.', { promptChars: 0 });
    }
    if (prompt.length > MAX_PROMPT_CHARS) {
      return refuseStart(attemptId, 'prompt-too-large', `Prompt is ${prompt.length} characters. qomrade ${VERSION} refuses prompts longer than ${MAX_PROMPT_CHARS}.`, { promptChars: prompt.length, maxPromptChars: MAX_PROMPT_CHARS, promptHash: fnv1a64(prompt) });
    }
    const requestedModelPolicy = modelPolicySnapshot(settings);
    if (requestedModelPolicy.policy === MODEL_POLICY_PIN && !requestedModelPolicy.target.key) {
      return refuseStart(attemptId, 'model-target-missing', 'Pin exact model & effort is selected, but no model route has been chosen. Use Refresh choices, select a model, and Start again.', { modelPolicy: requestedModelPolicy });
    }
    revokeEffectAuthority('new-start');
    state.running = true;
    state.paused = false;
    state.runPrompt = prompt;
    state.startedAt = Date.now();
    state.lastSendAt = 0;
    state.nextSendAt = Date.now() + INITIAL_SEND_DELAY_MS;
    state.waitingSince = 0;
    state.baselineAssistantId = latestAssistantTurn()?.id || null;
    state.latestAssistantId = null;
    state.latestAssistantFingerprint = null;
    state.stableSamples = 0;
    state.anchorConversationId = conversationIdFromPath();
    beginSessionArchive('operator-start');
    captureSessionTurns('operator-start');
    state.lastError = null;
    state.terminalStop = null;
    state.activeSend = null;
    state.modelAtSend = null;
    state.faultRecovery.preexistingAdvance = null;
    applyModelPolicyToRun('operator-start');
    state.autoRefresh.pendingResume = null;
    state.autoRefresh.restorePending = false;
    state.autoRefresh.inFlight = false;
    state.science.lastSignature = null;
    state.science.lastAt = null;
    state.science.lastChangedAt = null;
    state.startAccepted += 1;
    const receipt = startReceipt('accepted', 'controller scheduled independently of continuity persistence', {
      promptChars: prompt.length,
      promptHash: fnv1a64(prompt),
      gapMinutes: settings.gapMinutes,
      modelPolicy: activeModelPolicySnapshot(),
      initialSendDelayMs: INITIAL_SEND_DELAY_MS,
      nextSendAt: state.nextSendAt,
      anchorConversationId: state.anchorConversationId,
      authenticityReason: state.lastAuthenticity && state.lastAuthenticity.reason || null,
    }, attemptId);
    logEvent('start', 'Started the single-tab exact-prompt loop with bounded forensic observability.', {
      receipt,
      promptChars: prompt.length,
      promptHash: fnv1a64(prompt),
      gapMinutes: settings.gapMinutes,
      modelPolicy: activeModelPolicySnapshot(),
      anchorConversationId: state.anchorConversationId,
      authenticity: state.lastAuthenticity,
    });
    const startShellHealth = observePageShellHealth('operator-start', { capture: true });
    if (startShellHealth.degraded) {
      const surface = shellHealthSurface(startShellHealth);
      holdForPageShellMaintenance(surface, 'operator-start');
      persistContinuity('start-degraded-shell-hold');
      return receipt;
    }
    if (tryAdoptExistingFailedRequest()) {
      persistContinuity('start-adopted-failure');
      if (settings.trimOldTurns) armDomTrim(5_000, 'operator-start-adopted-failure');
      if (settings.hourlyRefresh) scheduleNextAutoRefresh('operator-start-adopted-failure');
      return receipt;
    }
    persistContinuity('start');
    setPhase('READY_TO_SEND', 'Operator started qomrade.');
    scheduleTick(INITIAL_SEND_DELAY_MS, 'initial send');
    if (settings.trimOldTurns) armDomTrim(5_000, 'operator-start');
    if (settings.hourlyRefresh) scheduleNextAutoRefresh('operator-start');
    return receipt;
  }
  function formatDuration(ms) {
    if (!Number.isFinite(ms) || ms <= 0) return 'now';
    const totalSeconds = Math.ceil(ms / 1_000);
    const hours = Math.floor(totalSeconds / 3_600);
    const minutes = Math.floor((totalSeconds % 3_600) / 60);
    const seconds = totalSeconds % 60;
    if (hours) return `${hours}h ${minutes}m`;
    if (minutes) return `${minutes}m ${seconds}s`;
    return `${seconds}s`;
  }
  function currentStatusText() {
    if (state.quarantine) return `OFF — ${state.phaseReason}`;
    if (state.running && state.paused) return `PAUSED — ${state.phase}: ${state.phaseReason}`;
    if (state.running && pauseForHidden() && document.hidden) return `HIDDEN HOLD — ${state.phase}: ${state.phaseReason}`;
    if (state.phase === 'WAITING_GAP' && state.nextSendAt) return `${state.phase} — next attempt in ${formatDuration(state.nextSendAt - Date.now())}`;
    return `${state.phase} — ${state.phaseReason}`;
  }
  function showMessage(message, bad = false) {
    if (ui.refs.message) {
      ui.refs.message.textContent = message;
      ui.refs.message.dataset.bad = bad ? 'true' : 'false';
    }
  }
  // @QOMRADE-CHUNK id=60.persistence title="Bounded per-tab settings and evidence-only continuity"
  function debounceSaveSettings() {
    markOperatorInteraction('settings-edit');
    if (ui.saveTimer) clearTimeout(ui.saveTimer);
    ui.saveTimer = setTimeout(() => {
      ui.saveTimer = null;
      saveTabRecord('settings-change', { suppressUnchangedSettings: true });
    }, 1_000);
  }
  function sanitizeLoadedSettings(value) {
    const source = value && typeof value === 'object' ? value : {};
    const loaded = source.schema === STORAGE_SCHEMA && source.settings && typeof source.settings === 'object'
      ? source.settings
      : source.settings && typeof source.settings === 'object'
        ? source.settings
        : source;
    settings.prompt = trunc(normalizePromptLineEndings(loaded.prompt || ''), MAX_PROMPT_CHARS);
    settings.gapMinutes = clamp(loaded.gapMinutes == null ? DEFAULTS.gapMinutes : loaded.gapMinutes, 1, 1_440);
    // 0.18.7 persisted its hidden-pause default without recording whether it was chosen.
    // This release explicitly migrates that legacy policy to background operation once.
    settings.pauseWhenHidden = loaded.backgroundPolicyVersion === 1 && loaded.pauseWhenHidden != null ? !!loaded.pauseWhenHidden : DEFAULTS.pauseWhenHidden;
    if (loaded.backgroundPolicyVersion !== 1 && loaded.pauseWhenHidden != null) {
      state.background.migration = { at: nowIso(), fromPauseWhenHidden: !!loaded.pauseWhenHidden, toPauseWhenHidden: settings.pauseWhenHidden,
        reason: '0.18.8 background-by-default upgrade; later explicit hidden-pause choices are retained' };
      logEvent('background-policy-migrated', 'Upgraded the legacy hidden-pause default to background operation.', state.background.migration);
    }
    settings.autoZip = loaded.autoZip == null ? DEFAULTS.autoZip : !!loaded.autoZip;
    settings.downloadSuffixes = normalizeDownloadSuffixList(loaded.downloadSuffixes == null ? DEFAULTS.downloadSuffixes : loaded.downloadSuffixes, { fallback: true }).text;
    settings.fileDelaySeconds = normalizeFileDelaySeconds(loaded.fileDelaySeconds, DEFAULTS.fileDelaySeconds);
    settings.requireVisibleFamily = loaded.requireVisibleFamily == null ? DEFAULTS.requireVisibleFamily : !!loaded.requireVisibleFamily;
    const legacyAutoSelect = loaded.autoSelectEligiblePro == null ? DEFAULTS.autoSelectEligiblePro : !!loaded.autoSelectEligiblePro;
    settings.modelPolicy = normalizeModelPolicy(loaded.modelPolicy || (legacyAutoSelect ? MODEL_POLICY_SMART_PRO : MODEL_POLICY_FOLLOW));
    settings.modelTargetLabel = trunc(loaded.modelTargetLabel || '', 180);
    settings.modelTargetKey = trunc(loaded.modelTargetKey || modelRouteKey(settings.modelTargetLabel), 220);
    settings.modelTargetVersion = normalizeModelVersionHint(loaded.modelTargetVersion, settings.modelTargetLabel);
    settings.modelTargetEffort = normalizeModelEffortPolicy(loaded.modelTargetEffort || DEFAULTS.modelTargetEffort);
    settings.autoSelectEligiblePro = settings.modelPolicy !== MODEL_POLICY_FOLLOW;
    settings.boundedScience = loaded.boundedScience == null ? DEFAULTS.boundedScience : !!loaded.boundedScience;
    const resilienceDefaultsCurrent = Number(loaded.resilienceDefaultsVersion) === RESILIENCE_DEFAULTS_VERSION;
    settings.trimOldTurns = resilienceDefaultsCurrent && loaded.trimOldTurns != null ? !!loaded.trimOldTurns : DEFAULTS.trimOldTurns;
    settings.hourlyRefresh = resilienceDefaultsCurrent && loaded.hourlyRefresh != null ? !!loaded.hourlyRefresh : DEFAULTS.hourlyRefresh;
    if (!resilienceDefaultsCurrent) {
      state.resilienceDefaultsMigration = { at: nowIso(), version: RESILIENCE_DEFAULTS_VERSION,
        from: { trimOldTurns: loaded.trimOldTurns == null ? null : !!loaded.trimOldTurns, hourlyRefresh: loaded.hourlyRefresh == null ? null : !!loaded.hourlyRefresh },
        to: { trimOldTurns: settings.trimOldTurns, hourlyRefresh: settings.hourlyRefresh },
        reason: '0.18.28 enables bounded trimming and ticketed Safe refresh by default; later explicit choices are retained' };
      logEvent('resilience-defaults-migrated', 'Enabled the new default memory-hygiene and Safe-refresh policy for this tab.', state.resilienceDefaultsMigration);
    }
    settings.refreshMinutes = normalizeRefreshMinutes(loaded.refreshMinutes, DEFAULTS.refreshMinutes);
    state.priorContinuity = source.continuity && typeof source.continuity === 'object' ? source.continuity : null;
    const priorTrim = state.priorContinuity?.domTrim;
    if (priorTrim) {
      state.domTrim.attempts = Math.max(0, Number(priorTrim.attempts) || 0);
      state.domTrim.successes = Math.max(0, Number(priorTrim.successes) || 0);
      state.domTrim.unitsRemoved = Math.max(0, Number(priorTrim.unitsRemoved) || 0);
      state.domTrim.logicalTurnsRemoved = Math.max(0, Number(priorTrim.logicalTurnsRemoved) || 0);
      state.domTrim.lastAt = priorTrim.lastAt || null;
    }
    const priorRefresh = state.priorContinuity?.autoRefresh;
    if (priorRefresh) {
      state.autoRefresh.attempts = Math.max(0, Number(priorRefresh.attempts) || 0);
      state.autoRefresh.reloads = Math.max(0, Number(priorRefresh.reloads) || 0);
      state.autoRefresh.deferrals = Math.max(0, Number(priorRefresh.deferrals) || 0);
      state.autoRefresh.lastAttemptAt = priorRefresh.lastAttemptAt || null;
      state.autoRefresh.lastReloadAt = priorRefresh.lastReloadAt || null;
      state.autoRefresh.healingReloads = Math.max(0, Number(priorRefresh.healingReloads) || 0);
      state.autoRefresh.healingSuppressed = Math.max(0, Number(priorRefresh.healingSuppressed) || 0);
      state.autoRefresh.lastHealingAt = priorRefresh.lastHealingAt || null;
      state.autoRefresh.lastHealingKey = typeof priorRefresh.lastHealingKey === 'string' ? priorRefresh.lastHealingKey : null;
      state.autoRefresh.healingHistory = (Array.isArray(priorRefresh.healingHistory) ? priorRefresh.healingHistory : [])
        .filter(row => row && typeof row.key === 'string' && Number.isFinite(Number(row.at))).slice(-AUTO_REFRESH_HEALING_LIMIT);
      compactHealingHistory();
    }
    state.autoRefresh.pendingResume = source.autoRefreshResume && typeof source.autoRefreshResume === 'object' ? source.autoRefreshResume : null;
    state.autoRefresh.resumeTicket = state.autoRefresh.pendingResume;
    state.autoRefresh.restorePending = !!state.autoRefresh.pendingResume;
    state.faultRecovery.ledger = (Array.isArray(source.faultRecovery?.ledger) ? source.faultRecovery.ledger : []).slice(-FAULT_LEDGER_LIMIT).filter(item => item && typeof item.key === 'string' && typeof item.userId === 'string' && typeof item.conversationId === 'string').map(item => ({
      key: item.key, conversationId: item.conversationId, userId: item.userId, userIds: (Array.isArray(item.userIds) ? item.userIds : [item.userId]).filter(stableRequestId).slice(-3),
      nativeAttempts: Math.max(0, Math.min(1_000_000_000, Math.floor(Number(item.nativeAttempts) || 0))),
      reloadAttempts: Math.max(0, Math.min(FAULT_RELOAD_LIMIT, Math.floor(Number(item.reloadAttempts) || 0))),
      replayAttempts: Math.max(0, Math.min(1_000_000_000, Math.floor(Number(item.replayAttempts) || 0))),
      resendsCommitted: Math.max(0, Math.min(1_000_000_000, Math.floor(Number(item.resendsCommitted) || 0))),
      resendUserIds: (Array.isArray(item.resendUserIds) ? item.resendUserIds : []).filter(stableRequestId).slice(-16),
      firstSeenAt: item.firstSeenAt || null, reloadObservedAt: item.reloadObservedAt || null,
      nextAt: Math.min(recoveryNow() + 300_000, Math.max(recoveryNow() + faultQuietMs(), Number(item.nextAt) || 0)),
      samples: 0, lastSignature: null, progressSignature: null, status: String(item.status || 'restored-budget').slice(0, 100),
      outcomes: (Array.isArray(item.outcomes) ? item.outcomes : []).slice(-6).map(row => ({ at: row.at || null, outcome: String(row.outcome || '').slice(0, 100), detail: row.detail ? trunc(JSON.stringify(row.detail), 1200) : null })),
    }));
    state.faultIncidents = state.priorContinuity && Array.isArray(state.priorContinuity.faultIncidents)
      ? state.priorContinuity.faultIncidents.slice(-12).map(compactFaultIncident).filter(Boolean) : [];
    state.zipKeys = state.priorContinuity && Array.isArray(state.priorContinuity.zipKeys)
      ? state.priorContinuity.zipKeys.map(value => String(value)).filter(Boolean).slice(-MAX_ZIP_KEYS)
      : [];
    state.lastZipKey = state.zipKeys.length ? state.zipKeys[state.zipKeys.length - 1] : null;
    if (state.priorContinuity && state.priorContinuity.quarantine && source.sourceId === QOMRADE_SOURCE_ID) {
      state.quarantine = state.priorContinuity.quarantine;
      state.lastError = { kind: 'hard-false-gui-quarantine-restored', quarantine: state.quarantine };
      state.phase = 'OFF';
      state.phaseReason = 'Persisted hard false-GUI quarantine from this exact qomrade source.';
    }
  }
  function compactPersistedEvent(event) {
    let detail = null;
    if (event && event.detail != null) {
      try { detail = trunc(JSON.stringify(event.detail), 1_200); }
      catch (_) { detail = trunc(String(event.detail), 1_200); }
    }
    return {
      seq: event && event.seq || null,
      t: event && event.t || null,
      at: event && event.at || null,
      kind: event && event.kind || null,
      message: trunc(event && event.message || '', 800),
      detail,
    };
  }
  function continuitySnapshot(reason) {
    return {
      schema: 'qomrade.single-tab-continuity.v2',
      sourceId: QOMRADE_SOURCE_ID,
      version: VERSION,
      capturedAt: nowIso(),
      reason,
      runningAtCapture: state.running,
      pausedAtCapture: state.paused,
      phase: state.phase,
      phaseReason: state.phaseReason,
      anchorConversationId: state.anchorConversationId,
      pathname: location.pathname,
      lastSendAt: state.lastSendAt || null,
      nextSendAt: state.nextSendAt || null,
      sends: state.sends,
      startAttempts: state.startAttempts,
      startAccepted: state.startAccepted,
      startRefused: state.startRefused,
      startTransaction: state.startTransaction ? JSON.parse(JSON.stringify(state.startTransaction)) : null,
      adoptedWithoutClick: state.adoptedWithoutClick,
      preClickAdvanceHolds: state.preClickAdvanceHolds,
      composerAttemptCount: state.composerAttemptCount,
      completedReplies: state.completedReplies,
      zipClicks: state.zipClicks,
      zipActivationErrors: state.zipActivationErrors,
      zipKeys: state.zipKeys.slice(-MAX_ZIP_KEYS),
      runPromptHash: state.runPrompt ? fnv1a64(state.runPrompt) : null,
      runPromptChars: state.runPrompt.length,
      modelPolicy: activeModelPolicySnapshot(),
      modelPreference: state.modelGate.runPreference || '5.6-first',
      activeSend: state.activeSend ? {
        id: state.activeSend.id,
        clickedAt: state.activeSend.clickedAt,
        userAdoptedAt: state.activeSend.userAdoptedAt || null,
        userTurnId: state.activeSend.userTurnId || null,
        assistantTurnId: state.activeSend.assistantTurnId || null,
        outcome: state.activeSend.outcome || null,
        promptHash: state.activeSend.promptHash,
        promptChars: state.activeSend.promptChars,
        model: state.activeSend.model,
      } : null,
      latestReceipt: state.turnReceipts.length ? state.turnReceipts[state.turnReceipts.length - 1] : null,
      lastModelConfirmation: state.modelGate.confirmed ? JSON.parse(JSON.stringify(state.modelGate.confirmed)) : null,
      lastModelCommit: state.modelGate.lastCommit ? JSON.parse(JSON.stringify(state.modelGate.lastCommit)) : null,
      lastModelSurvey: state.modelGate.lastSurvey ? JSON.parse(JSON.stringify(state.modelGate.lastSurvey)) : null,
      lastError: state.lastError ? JSON.parse(JSON.stringify(state.lastError)) : null,
      terminalStop: state.terminalStop ? JSON.parse(JSON.stringify(state.terminalStop)) : null,
      quarantine: state.quarantine ? JSON.parse(JSON.stringify(state.quarantine)) : null,
      scheduler: { ...state.scheduler },
      effectControl: JSON.parse(JSON.stringify(state.effectControl)),
      faultIncidents: state.faultIncidents.slice(-12).map(compactFaultIncident),
      events: state.events.slice(-MAX_CONTINUITY_EVENTS).map(compactPersistedEvent),
      domTrim: domTrimSnapshot(),
      autoRefresh: autoRefreshSnapshot(),
      resilienceDefaultsMigration: state.resilienceDefaultsMigration,
      domForensics: domForensicsContinuitySummary(),
      authority: 'evidence-only-never-resume-control',
    };
  }
  function buildTabRecord(reason) {
    const settingsOnly = {
      backgroundPolicyVersion: 1,
      prompt: settings.prompt,
      gapMinutes: settings.gapMinutes,
      pauseWhenHidden: settings.pauseWhenHidden,
      autoZip: settings.autoZip,
      downloadSuffixes: normalizeDownloadSuffixList(settings.downloadSuffixes, { fallback: true }).text,
      fileDelaySeconds: normalizeFileDelaySeconds(settings.fileDelaySeconds),
      requireVisibleFamily: settings.requireVisibleFamily,
      autoSelectEligiblePro: settings.modelPolicy !== MODEL_POLICY_FOLLOW,
      modelPolicy: settings.modelPolicy,
      modelTargetLabel: settings.modelTargetLabel,
      modelTargetKey: settings.modelTargetKey,
      modelTargetVersion: settings.modelTargetVersion,
      modelTargetEffort: settings.modelTargetEffort,
      boundedScience: settings.boundedScience,
      resilienceDefaultsVersion: RESILIENCE_DEFAULTS_VERSION,
      trimOldTurns: settings.trimOldTurns,
      hourlyRefresh: settings.hourlyRefresh,
      refreshMinutes: settings.refreshMinutes,
    };
    const record = {
      schema: STORAGE_SCHEMA,
      version: VERSION,
      sourceId: QOMRADE_SOURCE_ID,
      savedAt: nowIso(),
      settings: settingsOnly,
      continuity: continuitySnapshot(reason),
      faultRecovery: { schema: 'qomrade.fault-recovery.v3', ledger: state.faultRecovery.ledger.slice(-FAULT_LEDGER_LIMIT).map(entry => ({ ...entry, outcomes: entry.outcomes.slice(-6).map(row => ({ at: row.at, outcome: row.outcome, backendOutcome: 'unknown', detail: row.detail == null ? null : trunc(typeof row.detail === 'string' ? row.detail : JSON.stringify(row.detail), 1200) })) })),
        preexistingAdvance: state.faultRecovery.preexistingAdvance ? { ...state.faultRecovery.preexistingAdvance, outcomes: (state.faultRecovery.preexistingAdvance.outcomes || []).slice(-4) } : null,
        preexistingAdvanceCount: state.faultRecovery.preexistingAdvanceCount },
      recoveryResume: state.recoveryResume,
      autoRefreshResume: state.autoRefresh.resumeTicket,
    };
    let serialized = JSON.stringify(record);
    if (utf8Bytes(serialized) > MAX_CONTINUITY_BYTES) {
      record.continuity.events = record.continuity.events.slice(-4);
      if (record.continuity.lastError) record.continuity.lastError = { kind: record.continuity.lastError.kind || 'bounded', note: 'details omitted to reduce per-tab continuity size' };
      if (record.continuity.latestReceipt) record.continuity.latestReceipt = { id: record.continuity.latestReceipt.id || null, outcome: record.continuity.latestReceipt.outcome || null };
      if (record.continuity.startTransaction) record.continuity.startTransaction = { id: record.continuity.startTransaction.id || null, status: record.continuity.startTransaction.status || null, reason: record.continuity.startTransaction.reason || null };
      if (record.continuity.activeSend) record.continuity.activeSend = { id: record.continuity.activeSend.id || null, outcome: record.continuity.activeSend.outcome || null, promptHash: record.continuity.activeSend.promptHash || null };
      if (record.continuity.quarantine) record.continuity.quarantine = { kind: record.continuity.quarantine.kind || 'bounded', at: record.continuity.quarantine.at || null, sourceId: record.continuity.quarantine.sourceId || null };
      if (record.continuity.domForensics && record.continuity.domForensics.latest) {
        record.continuity.domForensics.latest = { id: record.continuity.domForensics.latest.id, key: record.continuity.domForensics.latest.key, at: record.continuity.domForensics.latest.at, trigger: record.continuity.domForensics.latest.trigger };
      }
      serialized = JSON.stringify(record);
    }
    if (utf8Bytes(serialized) > MAX_CONTINUITY_BYTES) {
      // Preserve attempt counters, aliases and the ticket; drop verbose outcome
      // detail before accepting any extra persistent bytes. Handoffs retain the
      // richer live evidence, but automatic writes stay small.
      for (const entry of record.faultRecovery.ledger) entry.outcomes = entry.outcomes.slice(-2).map(row => ({ at: row.at, outcome: row.outcome, backendOutcome: 'unknown', detail: row.detail ? trunc(row.detail, 160) : null }));
      serialized = JSON.stringify(record);
    }
    const settingsJson = JSON.stringify(settingsOnly);
    const settingsBytes = utf8Bytes(settingsJson);
    record.continuity.persistenceSizing = {
      maxRecordBytesTarget: MAX_CONTINUITY_BYTES,
      settingsBytes,
      recordBytes: 0,
      targetMet: true,
      note: 'bounded record target met',
    };
    for (let pass = 0; pass < 12; pass += 1) {
      serialized = JSON.stringify(record);
      const recordBytes = utf8Bytes(serialized);
      const targetMet = recordBytes <= MAX_CONTINUITY_BYTES;
      const note = targetMet ? 'bounded record target met' : settingsBytes >= MAX_CONTINUITY_BYTES ? 'exact settings dominate the target; prompt custody was not truncated' : 'exact settings and minimum recovery/continuity evidence exceed the target; prompt and attempt counters were not truncated';
      const sizing = record.continuity.persistenceSizing;
      if (sizing.recordBytes === recordBytes && sizing.targetMet === targetMet && sizing.note === note) break;
      sizing.recordBytes = recordBytes;
      sizing.targetMet = targetMet;
      sizing.note = note;
    }
    serialized = JSON.stringify(record);
    return { record, serialized, settingsJson };
  }
  function flushDeferredTabWrite(reason = 'deferred-tab-write-reconcile') {
    if (!recoveryWriteQueued || recoveryWriteBusy || autoRefreshWriteBusy || (state.boot.tabRead.pendingLate && !state.boot.operatorTouched)) return false;
    recoveryWriteQueued = false;
    state.boot.tabRead.writeQueued = false;
    return saveTabRecord(reason);
  }
  function markOperatorInteraction(reason = 'operator-interaction') {
    if (!state.boot.operatorTouched) logEvent('operator-settings-authority', 'Operator interaction ended the late tab-read adoption window.', { reason, tabReadStatus: state.boot.tabRead.status });
    state.boot.operatorTouched = true;
    if (state.boot.tabRead.pendingLate) {
      state.boot.tabRead.pendingLate = false;
      state.boot.tabRead.lateDiscardedAt = nowIso();
      state.boot.tabRead.lateDiscardReason = reason;
    }
    flushDeferredTabWrite('operator-interaction-reconcile');
  }
  async function applyLoadedTabRecord(record, origin = 'initial-read') {
    if (record) {
      sanitizeLoadedSettings(record);
      if (record.recoveryResume) await restoreRecoveryTicket(record);
      if (!record.autoRefreshResume) saveTabRecord(`post-restore-normalization:${origin}`, { suppressUnchangedSettings: false });
    }
    state.boot.settingsReadyAt = nowIso();
    state.uiModelObservation = null;
    render({ forceModel: true });
    maybeBeginAutoRefreshRestore();
  }
  function loadTabSettings() {
    state.persistence.reads += 1;
    state.persistence.lastReadAt = nowIso();
    state.boot.tabRead.status = 'in-flight';
    state.boot.tabRead.startedAt = nowIso();
    const started = performance.now();
    if (typeof GM_getTab !== 'function') {
      state.boot.tabRead.status = 'unavailable';
      state.boot.tabRead.elapsedMs = 0;
      return Promise.resolve(null);
    }
    return new Promise(resolve => {
      let settled = false;
      const adoptLate = value => {
        state.boot.tabRead.lateCallbacks += 1;
        const elapsed = Math.round(performance.now() - started);
        if (!value) return;
        if (state.boot.operatorTouched || state.startAttempts > 0 || state.running) {
          state.boot.tabRead.pendingLate = false;
          state.boot.tabRead.lateDiscardedAt = nowIso();
          state.boot.tabRead.lateDiscardReason = 'operator-started-or-edited';
          flushDeferredTabWrite('late-tab-read-discard-reconcile');
          return;
        }
        state.boot.tabRead.pendingLate = false;
        state.boot.tabRead.status = 'completed-late';
        state.boot.tabRead.elapsedMs = elapsed;
        state.boot.tabRead.recordPresent = true;
        state.boot.tabRead.lateAdoptedAt = nowIso();
        state.persistence.lastReadElapsedMs = elapsed;
        void applyLoadedTabRecord(value, 'late-callback').then(() => flushDeferredTabWrite('late-tab-read-adopted-reconcile'));
      };
      const finish = (value, status, error = null) => {
        if (settled) { adoptLate(value); return; }
        settled = true;
        const elapsed = Math.round(performance.now() - started);
        state.persistence.lastReadElapsedMs = elapsed;
        state.boot.tabRead.status = status;
        state.boot.tabRead.elapsedMs = elapsed;
        state.boot.tabRead.recordPresent = !!value;
        state.boot.tabRead.error = error;
        state.boot.tabRead.pendingLate = status === 'timed-out';
        if (status === 'timed-out') state.persistence.readTimeouts += 1;
        if (status === 'error') state.persistence.readErrors += 1;
        resolve(value || null);
      };
      const timeout = setTimeout(() => finish(null, 'timed-out'), state.boot.tabRead.timeoutMs);
      try {
        GM_getTab(value => {
          clearTimeout(timeout);
          finish(value, 'completed');
        });
      } catch (error) {
        clearTimeout(timeout);
        finish(null, 'error', String(error && error.message || error));
      }
    });
  }
  function saveTabRecord(reason = 'unspecified', { suppressUnchangedSettings = false } = {}) {
    if (recoveryWriteBusy || autoRefreshWriteBusy || (state.boot.tabRead.pendingLate && !state.boot.operatorTouched)) {
      recoveryWriteQueued = true;
      if (autoRefreshWriteBusy) autoRefreshWriteQueued = true;
      if (state.boot.tabRead.pendingLate) state.boot.tabRead.writeQueued = true;
      return false;
    }
    if (typeof GM_saveTab !== 'function') return false;
    const built = buildTabRecord(reason);
    if (suppressUnchangedSettings && built.settingsJson === lastSavedSettingsJson) return false;
    lastSavedSettingsJson = built.settingsJson;
    const bytes = utf8Bytes(built.serialized);
    state.persistence.writes += 1;
    state.persistence.lastWriteAt = nowIso();
    state.persistence.lastWriteBytes = bytes;
    state.persistence.maxWriteBytes = Math.max(state.persistence.maxWriteBytes, bytes);
    state.persistence.lastWriteReason = reason;
    try {
      const result = GM_saveTab(built.record);
      if (result && typeof result.then === 'function') {
        result.catch(error => {
          state.persistence.writeErrors += 1;
          lastSavedSettingsJson = '';
          recordPageError({ kind: 'persistence-write-rejection', message: String(error && error.message || error) });
        });
      }
      return true;
    } catch (error) {
      state.persistence.writeErrors += 1;
      lastSavedSettingsJson = '';
      recordPageError({ kind: 'persistence-write-error', message: String(error && error.message || error) });
      return false;
    }
  }
  function saveTabSettings() {
    return saveTabRecord('settings-snapshot', { suppressUnchangedSettings: true });
  }
  function persistContinuity(reason) {
    return saveTabRecord(reason, { suppressUnchangedSettings: false });
  }
  const DOCUMENT_CONSTITUTION = Object.freeze([
    'one code-point-faithful operator prompt per run; only CRLF/CR becomes LF and terminal editor newlines are explicitly removed; later rendered-turn custody uses a declared lossy projection that never changes the Send payload',
    'operator-selected per-tab model policy before every Send: Smart Pro defaults to explicit GPT-5.6 Pro and uses GPT-6 only for one unconfirmed Send or the unresolved failed lineage until a stable reply succeeds; Pin requires one exact live-discovered route and effort with no silent fallback and may be non-Pro; Follow changes nothing and witnesses the current route and effort; all proof is send-local UI evidence',
    'single-tab isolation; no discovery, listeners, shared control keys, or cross-tab coordination',
    'ordinary exact-prompt recovery retained; no dev dogfooder, browser file-plan interpreter, temporary trials, or automatic diagnostic upload',
    'no recurring controller timer while stopped; background work is the default; optional hidden pause, bounded DOM trimming, and safe-checkpoint refresh remain operator-selected',
    'one complete qomrade.user.js is authoritative; sandpeople return complete revised files and never re-embed recursive release archives',
    'Session Handoff is only the ordered user/assistant transcript captured from the ChatGPT context river; Developer Handoff is copied to the clipboard and diagnoses qomrade; Flight Recorder is compact saved qomrade operational evidence; none is automatic control authority',
    'hard no-history plus visible 5.3 is a persistent single-tab OFF quarantine before consequential effects',
    'complete structural, resource-timing, error, and DOM inventories run only on explicit diagnostics or handoff; selected odd-event edges may preserve bounded DOMish scenes without a continuous observer',
    'ordinary per-tab continuity is evidence-only; a verified source/conversation/prompt-bound one-shot ticket may resume only the same safe-refresh run',
    'panel controls use a separate local iframe event path; active qomrade editors defer composer focus and Send',
    'active-only bounded pipeline science records change edges without page interposition; consequential odd edges may attach bounded DOMish evidence capsules, never action authority',
    'current owned generation faults use a fresh exact-prompt Send and never native Retry or reload; terminal conversation-length notices end the run as COMPLETE; operator-enabled Safe refresh may separately heal a qualifying stale surface',
    'structured ProseMirror insertion removes only terminal editor newlines, records each attempt, and suppresses Send after any pre-click conversation advance',
    'asynchronous browser effects hold revocable per-operation epochs; final Send checks and click form one synchronous commit; cancelled work never borrows a later run',
    'send-local model proof never survives cancellation or reload; a collapsed or effort-only label is acceptable only with same-operation route-and-effort evidence required by the active Smart, Pin, or Follow policy',
    'bounded trimming and ticketed Safe refresh are enabled by default from 0.18.28; either remains individually operator-disableable, while interval recommendations are advice only',
    'the bounded session recorder captures every user and assistant turn qomrade actually observes, preserves it before trimming, records visible file/image-card names without embedding bytes, captures newly materialized turns on natural scrolling, exports without moving the viewport, and states explicit omissions for unavailable or over-budget history',
    'with Safe refresh enabled, a new historical or unowned failure edge may arm one exact-ticket healing refresh after 15 seconds; missing composer is allowed only in that mode, 30-minute dedup plus a two-per-hour budget prevent loops, and current typed request recovery takes priority',
    'Developer Handoff v2 is amnesia-first: readMeFirst, incidentIndex, canonical timeline, evidence catalog, compatible deep sections, and bounded event-triggered DOMish snapshots carried through exact Safe-refresh tickets',
    'exact conversation-stale and conversation-load-failed notices are maintenance-only: Safe refresh may preserve active request custody through one exact-ticket reload, but any current typed request fault cancels it and neither Retry nor prompt resend is authorized',
    'Developer Handoff normalizes live pipeline surfaces with equivalent contexts retained in DOMish snapshots; terminal-barrier Retry is expected terminal UI, and empty clipped live regions are omitted from related DOMish roots when they add no evidence',
    'per-tab writes are serialized across recovery, Safe refresh, ordinary continuity and late-read reconciliation; a late record is adoptable only before operator action, and exact refresh custody has a bounded restore deadline',
    'ordinary Sends enforce nextSendAt and a minimum click floor both before asynchronous work and at the final synchronous commit; phase names alone never authorize a click',
    'while hidden, only the live model trigger’s exact controlled open populated menu may be read despite missing geometry or paint suppression; menu mutation additionally requires non-inert non-aria-hidden state, every other consequential control keeps ordinary visibility checks, and true browser suspension remains outside userscript control',
    'Pin remains no-fallback when ChatGPT renames a route: only one already-selected enabled row may reconcile legacy Latest to explicit GPT-6 or same-version prefix-compatible label drift; qomrade persists the canonical label, key and version, never clicks a different alias, and still requires fresh effort proof',
    'observation pressure is purpose-bounded: full growing assistant prose is deferred while generation is advertised; operation-scoped model-menu and post-file-activation observers disconnect at success/timeout/cancellation; Session Handoff export never scrolls, natural-scroll transcript capture is passive and debounced, duplicate page errors coalesce, and no persistent page-global observer or heap claim is introduced',
  ]);
  const DOCUMENT_OFFICE = Object.freeze({
    schema: 'qomrade.office.v1',
    authority: 'The live operator request outranks inherited prose. Complete-file revision authority is broad; browser effects remain bounded by the constitution and explicit operator controls.',
    accepted: 'The stable kernel is exact-prompt custody, operator-selected send-local model custody with a GPT-5.6-first Smart Pro default, selected-route-only pin reconciliation, hidden trigger-bound model proof, fresh-message fault recovery, terminal conversation completion, explicit native-file authority, cancellation, single-tab isolation, bounded maintenance, and evidence-rich handoffs.',
    current: '0.18.36 expands the bottom-anchored panel with top-strip clearance, accepts exact per-tab Safe-refresh minutes, restores content-derived source identity, improves readMeFirst with active-request model and operator-setting evidence, and adds cloudtainer officer CLI commands for environment, multi-handoff study, and verified release.',
    learned: 'The five 0.18.35 handoffs were mostly healthy and actively running, but all declared source_id=pending. Current page model pills also often collapsed to effort-only Pro during generation even though active transaction receipts retained concrete send-local model evidence.',
    open: 'Firefox may still throttle, suspend, unload, or recreate inactive tabs, and ordinary page APIs do not expose trustworthy per-tab process memory. Field study should distinguish those browser effects from controller liveness and qomrade retained evidence.',
    next: 'Install 0.18.36, choose the exact refresh interval you prefer, and use cloudtainer study for batches of Developer Handoffs or cloudtainer release for a reproducible JS/ZIP delivery.',
    hold: 'No keep-awake audio, worker fleet, cross-tab coordination, persistent page-global observer, general invisible-control bypass, un-ticketed resume, or automatic maintenance-setting change. Cloudtainer commands are offline officer tooling only.',
    operator: 'Smart Pro, Pin and Follow remain per-tab. New and migrated tabs start with trimming and Safe refresh checked, a 60-minute interval, a 30-minute send gap, and background work on. Session Handoff is transcript only; Developer Handoff is clipboard forensics; Flight Recorder is compact saved evidence.',
  });
  const DOCUMENT_HERITAGE = Object.freeze({
    schema: 'qomrade.heritage.v1',
    runtimeKeep: ['code-point-faithful prompt transport','declared rendered-text projection','exact-successor request custody','latest-only Start receipt','structured ProseMirror adapter','pre-click duplicate prevention','hard final cadence gate','operator-selected model policy with Smart-Pro default, exact pin and follow-current modes','selected-route-only pinned-label reconciliation with persisted canonical identity','exact trigger-controlled paint-independent hidden model-menu proof','bounded operation-scoped model-menu hydration observation','low-churn generation-time assistant observation','truthful scheduling','fresh-message fault recovery','terminal conversation completion','ZIP custody','serialized per-tab persistence','bounded late-read adoption','bounded refresh-restore deadline','single-tab quarantine','event-isolated panel','bounded DOM trimming','safe-checkpoint refresh and exact resume','block-preserving session transcript','exact conversation-stale, conversation-load-failed and degraded-shell maintenance classification'],
    probeKeep: ['semantic turn adapters','red/error evidence','normalized live and DOMish-restored pipeline surfaces','live-discovered model catalog and send-local route/effort receipts','pinned-route reconciliation receipts','hidden model-menu style, rectangle, blocker, and structural-acceptance receipts','resource timing on demand','governor surfaces','selector families','page errors','performance metrics','serialized memory-pressure proxy','foreground-rescue and hidden execution-gap evidence','contradictions','compact flight recording','terminal-aware Retry context'],
    documentKeep: ['office','current dialogue','release scars','bounded lineage','tests','Bash workbench','cloudtainer officer CLI','candidate workspace','deterministic embedding','Humpty byte identity'],
    retiredRuntime: ['dev dogfooder and browser developer exchange','temporary behavior trials','automatic diagnostic upload','Officer self-prompting loop','fleet and cross-tab coordination','desktop notifications','page-global network interception','persistent page-global hot observers','recursive embedded release archives'],
    rejectedOrDeferred: ['native Retry as recovery','reload of a current typed owned failure','timeout-only reload','silent resend without explicit failure','automatic new-chat creation','automatic maintenance-setting changes'],
    principle: 'transcript fidelity, selected-route custody, separated powers, bounded effects, sane defaults with explicit overrides, and no silent fallback',
  });
  const DOCUMENT_DIALOGUE = Object.freeze([
    { at: '2026-10-11', role: 'operator', classification: 'operator_request', statement: 'Ordinary use is now boring and mundane in a good way; make the bottom-anchored panel about one-third taller, allow an exact refresh interval, and keep improving observability and cloudtainer CLI tools for the officer.' },
    { at: '2026-10-11', role: 'officer', classification: 'measured_fact', statement: 'Five 0.18.35 Developer Handoffs were actively running, but every artifact declared source_id=pending; several orientation records also showed only a collapsed Pro pill while the active transaction retained concrete send-local model proof.' },
    { at: '2026-10-11', role: 'officer', classification: 'decision', statement: 'Reserve ChatGPT top-strip clearance while expanding the panel, accept exact bounded refresh minutes, expose active-request model and operator settings in readMeFirst, restore exact source identity, and add tested cloudtainer env/study/release commands.' },
    { at: '2026-10-11', role: 'operator', classification: 'operator_request', statement: 'Red-team qomrade for outside-the-box flaws.' },
    { at: '2026-10-11', role: 'officer', classification: 'measured_fact', statement: 'The 0.18.34 delivery evidence was internally contradictory, and ordinary prose links plus page-wide generic submit fallbacks had more authority than intended.' },
    { at: '2026-10-11', role: 'officer', classification: 'decision', statement: 'Require explicit native-file authority, prioritize real file controls, scope generic submit to the owned composer, and require independent package readback.' },
    { at: '2026-10-11', role: 'operator', classification: 'operator_request', statement: 'Smart Pro used GPT-6 after a prior failure and file downloading needed comma-separated suffixes with .zip on by default.' },
    { at: '2026-10-11', role: 'officer', classification: 'decision', statement: 'Keep GPT-6 only through the unresolved failed lineage, clear Smart Pro after stable success, classify message-delivery timeout, and retain bounded native-file suffix configuration.' },
    { at: '2026-10-08', role: 'operator', classification: 'operator_request', statement: 'Continue research on Firefox inactive-tab operation, RAM pressure, and useful observability improvements.' },
    { at: '2026-10-08', role: 'officer', classification: 'measured_fact', statement: 'Field handoffs proved real hidden Sends and file activations but also showed tens of millions of repeated assistant-text characters, large survey retention, and occasional long hidden callback gaps.' },
    { at: '2026-10-08', role: 'officer', classification: 'decision', statement: 'Defer growing prose during generation, compact model surveys, use one operation-scoped menu mutation wait, coalesce repeated page errors, and export memory, navigation, rescue, and hidden-gap evidence.' },
    { at: '2026-10-07', role: 'operator', classification: 'operator_request', statement: 'The pinned model was visibly selected and the pinner could see it; MODEL_HOLD should not stop the run.' },
    { at: '2026-10-07', role: 'officer', classification: 'decision', statement: 'Reconcile only the already-selected route for legacy Latest to GPT-6 or same-version label drift, persist the current identity, and never click a different alias.' },
  ]);
  const DOCUMENT_HISTORY = Object.freeze([
    { version: '0.18.40', source: QOMRADE_SOURCE_ID, closed: 'non-scrolling Session Handoff; natural-scroll transcript capture; visible context-item metadata; final terminal-owner reconciliation' },
    { version: '0.18.39', source: '572788869f1e8a5eb225fa6576d465e69103c9c36507237dc7cd150b351d2afe', closed: 'accepted-user-turn terminal stage; truthful empty-composer explanation; barrier-owner evidence; terminal handoff clarity' },
    { version: '0.18.38', source: 'bff69c1faf3720795e19a368f51d4b500bb4c3d69f1f181d4bd8c4f98ae3dd35', closed: 'settled file activation; bounded top-level download-notice evidence and one failure retry; boot-started transcript capture; bounded history backfill; ordinal coverage' },
    { version: '0.18.36', source: '1a9b9cf9544273779220debde5e9a211a7678aed7437e573d8084cb69cf7b2d1', closed: 'taller bottom panel with top clearance; exact Safe-refresh minutes; active-request/settings orientation; cloudtainer officer CLI; restored source identity and package readback' },
    { version: '0.18.35', source: 'pending', closed: 'field-working release whose declared source identity remained pending; explicit file-control authority; priority file scan; composer-scoped Send; red-team regressions' },
    { version: '0.18.34', source: 'f9c01ecd7d335190a02cab9c30e28935c0bd0b21209c68a2cd2913dcc58e6a59', closed: 'Smart Pro fallback reset; delivery-timeout recovery; configurable file suffixes; release verification contradiction discovered by later audit' },
    { version: '0.18.33', source: '03b778676b27eae03a62197cc24838f09b4613ff2532c2df4685b6c20fcabeb4', closed: 'low-churn generation observation; compact model surveys; bounded menu mutation wait; rescue and hidden-gap evidence; memory proxy' },
    { version: '0.18.32', source: 'a10a35641f70873f7fcb53d602474d95c47c6f7f1c45fb11b8925dea85d17747', closed: 'selected-route pin reconciliation; legacy Latest to checked GPT-6; persisted canonical identity' },
    { version: '0.18.31', source: '5c74934db4d513cac751c257ed78c6e580db70dc971618894fb0c8c352f2423d', closed: 'hidden pinned-model paint-transition bypass and background Send without foreground' },
    { version: '0.18.30', source: '2fbe45d81848738a8f55d9949d5aa8688016e30550157bd3ab6064c4a35c3600', closed: 'conversation-load-failed maintenance classification and exact-ticket repair' },
    { version: '0.18.29', source: '56e0db296502e984251595c93bf51bdb05cc5d7815f7d162e6d3bf6497c768ae', closed: 'high-confidence degraded-shell detection and Start-authorized repair' },
    { version: '0.18.28', source: 'c9034617f56cafa3fe8346838ece19a6c58480927383bfe581e4f7d2740a2a53', closed: 'hidden structural model-menu evidence; default trimming and Safe refresh' },
    { version: '0.18.27', source: 'c8d5d0665dd655fc154398e21b03c0d39d3e1af79da40f62baefb2b73a3d95a2', closed: 'Smart Pro, exact Pin, and Follow-current model policies' },
    { version: '0.18.26', source: '4061b0040e08cfaf8964267f6c32f1710fc0e8dad940529dceaf065cf62cf0be', closed: 'Unicode-faithful prompt transport; serialized persistence; bounded restore; hard final cadence' },
    { version: '0.18.24', source: '3e2f1c821f574cc9bf955931fc5849c728be076a47c825e04ae4505b5149f91e', closed: 'amnesia-first Developer Handoff v2 and DOMish evidence' },
    { version: '0.18.21', source: '55aebe861dc53e98bf171068d7300a3a255ebd012bb90518da8bdfd82b261d75', closed: 'transcript-only Session Handoff and separated evidence products' },
    { version: '0.18.18', closed: 'conversation-too-long completion and clean terminal stop' },
    { version: '0.18.17', closed: 'bounded DOM trimming and ticketed Safe refresh' },
    { version: '0.18.13', closed: 'fresh exact-prompt recovery; native Retry and fault-triggered reload retired' },
    { version: '0.18.11', closed: 'developer runtime removed; compact standalone workbench' },
    { version: '0.18.3', closed: 'revocable asynchronous effects and synchronous final Send commit' },
    { version: '0.17.0', closed: 'living workbench, office, lineage, and on-demand handoff' },
  ]);
  const SANDPERSON_PROTOCOL = Object.freeze([
    'Receive the complete qomrade.user.js and the newest Developer Handoffs when diagnosing qomrade; Session Handoff remains only conversation transcript evidence.',
    'Begin in the cloud container with `bash qomrade.user.js cloudtainer env`, then run doctor and read document brief before changing source.',
    'For several field artifacts, run `bash qomrade.user.js cloudtainer study HANDOFF...`; treat its findings as an index into the original evidence, not a replacement for it.',
    'Create a disposable candidate workspace; accepted source remains immutable and patches are evidence rather than the returned product.',
    'Revise the complete candidate plus living office, bounded dialogue, lineage, tests, fixtures, and workbench; remove stale prose when current decisions supersede it.',
    'Rebuild the deterministic embedded workbench, inject the content-derived source identity, and run doctor, core tests, relevant browser fixtures, and Humpty byte identity.',
    'Use `bash qomrade.user.js cloudtainer release OUTDIR` for independently reopened JS/ZIP/checksum/manifest delivery; add `--browser` when the environment can qualify browser suites.',
    'Return the complete verified qomrade.user.js and one-member ZIP every revision; never claim a path exists until it has been created and read back.',
    'Keep observations, hypotheses, browser limits, backend unknowns, and operator authority distinct.',
  ]);
  // @QOMRADE-CHUNK id=70.handoff title="Developer diagnostics, transcript-only session handoff, and compact flight recording"
  function compactTurnSummaries() {
    return materializedTurns().slice(-12).map(turn => {
      const text = turnText(turn.element);
      const bounded = text.length > 12_000 ? `${text.slice(0, 6_000)}${text.slice(-6_000)}` : text;
      return {
        id: turn.id,
        ordinal: turn.ordinal,
        adapter: turn.adapter,
        role: turn.role,
        chars: text.length,
        hash: fnv1a32(bounded),
        head: turn.role === 'assistant' ? trunc(normalizeCompactText(text), 320) : null,
        workOnly: turn.role === 'assistant' ? assistantWorkOnly(turn.element) : false,
      };
    });
  }
  function selectorDiagnostics() {
    return currentControlsObservation();
  }
  function schedulerSnapshot() {
    return {
      schema: 'qomrade.scheduler-observability.v1',
      timerActive: !!state.timer,
      saveTimerActive: !!ui.saveTimer,
      zipRescanTimerActive: !!ui.zipRescanTimer,
      fileOutcomeObserverActive: !!ui.fileOutcomeObserver,
      bootAuthenticityTimerActive: !!ui.bootAuthenticityTimer,
      shellHealthTimerActive: !!ui.shellHealthTimer,
      domTrimTimerActive: !!ui.domTrimTimer,
      autoRefreshTimerActive: !!ui.autoRefreshTimer,
      ...state.scheduler,
      dueIso: state.scheduler.dueAt ? new Date(state.scheduler.dueAt).toISOString() : null,
      lastFiredIso: state.scheduler.lastFiredAt ? new Date(state.scheduler.lastFiredAt).toISOString() : null,
      cadence: { hidden: document.hidden, pauseWhenHidden: pauseForHidden(), configuredPauseWhenHidden: settings.pauseWhenHidden, replyPollMs: replyPollMs(), gapPollMs: gapPollMs() },
    };
  }
  function metricsSnapshot() {
    return {
      ...state.metrics,
      synchronousSections: Object.fromEntries(Object.entries(state.metrics.synchronousSections).map(([key, record]) => [key, { ...record }])),
      tickTimingMeaning: 'wall time including awaits; not a main-thread blocking measurement',
      synchronousTimingMeaning: 'inclusive synchronous sections; nested durations must not be summed',
      synchronousSampleWindow: 'completed sections available before this snapshot; current handoff buildDurationMs is recorded separately',
      semanticTraversalMeaning: 'JavaScript subtree-boundary visits and native bulk text reads; not a count of all browser-internal nodes processed',
      tickAverageMs: state.metrics.ticks ? Math.round((state.metrics.tickTotalMs / state.metrics.ticks) * 100) / 100 : 0,
    };
  }
  function runtimeSnapshot() {
    return {
      schema: QOMRADE_RUNTIME_SCHEMA,
      running: state.running,
      paused: state.paused,
      phase: state.phase,
      phaseReason: state.phaseReason,
      startedAt: state.startedAt ? new Date(state.startedAt).toISOString() : null,
      lastSendAt: state.lastSendAt ? new Date(state.lastSendAt).toISOString() : null,
      nextSendAt: state.nextSendAt ? new Date(state.nextSendAt).toISOString() : null,
      waitingSince: state.waitingSince ? new Date(state.waitingSince).toISOString() : null,
      anchorConversationId: state.anchorConversationId,
      sends: state.sends,
      startAttempts: state.startAttempts,
      startAccepted: state.startAccepted,
      startRefused: state.startRefused,
      startTransaction: state.startTransaction,
      adoptedWithoutClick: state.adoptedWithoutClick,
      preClickAdvanceHolds: state.preClickAdvanceHolds,
      composerAttemptCount: state.composerAttemptCount,
      completedReplies: state.completedReplies,
      zipClicks: state.zipClicks,
      zipActivationErrors: state.zipActivationErrors,
      lastZipKey: state.lastZipKey,
      zipKeyCount: state.zipKeys.length,
      lastError: state.lastError,
      terminalStop: state.terminalStop,
      faultObservation: state.faultObservation,
      faultIncidents: state.faultIncidents.slice(-12),
      faultRecovery: recoverySnapshot(),
      background: backgroundSnapshot(),
      domTrim: domTrimSnapshot(),
      autoRefresh: autoRefreshSnapshot(),
      resilienceDefaultsMigration: state.resilienceDefaultsMigration,
      shellHealth: shellHealthSummary(),
      domForensics: domForensicsSummary({ includeSnapshots: false }),
      sessionArchive: sessionArchiveSummary(),
      maintenanceRecommendation: maintenanceRecommendation(),
      zipCapture: zipCaptureSnapshot(),
      quarantine: state.quarantine,
      timerActive: !!state.timer,
      tickBusy: state.tickBusy,
      effectControl: JSON.parse(JSON.stringify(state.effectControl)),
      baselineAssistantId: state.baselineAssistantId,
      latestAssistantId: state.latestAssistantId,
      stableSamples: state.stableSamples,
      activeSend: state.activeSend,
      latestReceipt: state.turnReceipts.length ? state.turnReceipts[state.turnReceipts.length - 1] : null,
      turnReceipts: state.turnReceipts.slice(-MAX_TURN_RECEIPTS),
      modelAtSend: state.modelAtSend,
      modelDrifts: state.modelDrifts.slice(-20),
      modelIndicatorEdges: state.modelIndicatorEdges.slice(-20),
      modelGate: {
        ...state.modelGate,
        recentSurveys: state.modelGate.recentSurveys.slice(-MAX_MODEL_SURVEY_RECORDS),
      },
      science: {
        ...state.science,
        pulses: state.science.pulses.slice(-MAX_SCIENCE_PULSES),
        surfaceEdges: state.science.surfaceEdges.slice(-MAX_PIPELINE_SURFACE_EDGES),
      },
      scheduler: schedulerSnapshot(),
      metrics: metricsSnapshot(),
    };
  }
  function compactReceiptForDiagnostics(receipt) {
    if (!receipt || typeof receipt !== 'object') return null;
    return {
      schema: receipt.schema || null,
      id: receipt.id || null,
      startedAt: receipt.startedAt || null,
      clickedAt: receipt.clickedAt || null,
      clickMode: receipt.clickMode || null,
      editorPayloadChars: receipt.editorPayloadChars == null ? null : receipt.editorPayloadChars,
      terminalNewlinesRemoved: receipt.terminalNewlinesRemoved == null ? null : receipt.terminalNewlinesRemoved,
      userAdoptedAt: receipt.userAdoptedAt || null,
      completedAt: receipt.completedAt || null,
      outcome: receipt.outcome || null,
      promptChars: receipt.promptChars == null ? null : receipt.promptChars,
      promptHash: receipt.promptHash || null,
      model: receipt.model ? { label: receipt.model.label || null, family: receipt.model.family == null ? null : receipt.model.family, hasPro: !!receipt.model.hasPro } : null,
      userTurnId: receipt.userTurnId || null,
      userTurnOrdinal: receipt.userTurnOrdinal == null ? null : receipt.userTurnOrdinal,
      assistantTurnId: receipt.assistantTurnId || null,
      assistantTurnOrdinal: receipt.assistantTurnOrdinal == null ? null : receipt.assistantTurnOrdinal,
      assistantTextChars: receipt.assistantTextChars == null ? null : receipt.assistantTextChars,
      assistantTextHash: receipt.assistantTextHash || null,
      outcomeDetail: receipt.outcomeDetail ? {
        kind: receipt.outcomeDetail.kind || null,
        text: trunc(receipt.outcomeDetail.text || receipt.outcomeDetail.message || '', 1_000),
        requestStage: receipt.outcomeDetail.requestStage ? {
          userTurnMaterialized: !!receipt.outcomeDetail.requestStage.userTurnMaterialized,
          userTurnId: receipt.outcomeDetail.requestStage.userTurnId || null,
          userTurnOrdinal: receipt.outcomeDetail.requestStage.userTurnOrdinal == null ? null : receipt.outcomeDetail.requestStage.userTurnOrdinal,
          assistantTurnMaterialized: !!receipt.outcomeDetail.requestStage.assistantTurnMaterialized,
          composerEmpty: receipt.outcomeDetail.requestStage.composerEmpty == null ? null : !!receipt.outcomeDetail.requestStage.composerEmpty,
          barrierBelongsToActive: !!receipt.outcomeDetail.requestStage.barrierOwner?.belongsToActive,
        } : null,
      } : null,
    };
  }
  function buildDiagnostics() {
    return withReadSnapshot('buildDiagnostics', () => {
    invalidateTurnCache('compact-diagnostics');
    const started = performance.now();
    state.metrics.diagnostics += 1;
    const probeFailures = [];
    const faults = safeProbe('faults', () => observeVisibleFaults(latestAssistantTurn(), { origin: 'compact-diagnostics', includeHistory: true }), probeFailures, null);
    const resource = safeProbe('resource-timing', resourceTimingObservation, probeFailures, { available: false, entryCount: null, recent: [], endpoints: {} });
    const runtime = runtimeSnapshot();
    const payload = {
      schema: 'qomrade.compact-diagnostics.v3',
      faults,
      generatedAt: nowIso(),
      source: { product: 'qomrade', version: VERSION, sourceId: QOMRADE_SOURCE_ID, singleTab: true, crossTabCoordination: false },
      userscriptEnvironment: safeProbe('userscript-environment', userscriptEnvironmentObservation, probeFailures, { available: false }),
      page: safeProbe('page', pageObservation, probeFailures, { pathname: location.pathname }),
      runtime,
      settings: {
        promptChars: settings.prompt.length,
        promptHash: fnv1a64(settings.prompt),
        runPromptChars: state.runPrompt.length,
        runPromptHash: state.runPrompt ? fnv1a64(state.runPrompt) : null,
        gapMinutes: settings.gapMinutes,
        pauseWhenHidden: settings.pauseWhenHidden,
        autoZip: settings.autoZip,
        downloadSuffixes: settings.downloadSuffixes,
        requireVisibleFamily: settings.requireVisibleFamily,
        autoSelectEligiblePro: settings.autoSelectEligiblePro,
        boundedScience: settings.boundedScience,
        trimOldTurns: settings.trimOldTurns,
        hourlyRefresh: settings.hourlyRefresh,
        maxPromptChars: MAX_PROMPT_CHARS,
      },
      authenticity: safeProbe('authenticity', surfaceAuthenticityObservation, probeFailures),
      barrier: safeProbe('barrier', conversationBarrierObservation, probeFailures),
      work: safeProbe('work', workEvidenceObservation, probeFailures),
      dialogs: safeProbe('dialogs', visibleDialogObservation, probeFailures),
      continuation: safeProbe('continuation', continuationObservation, probeFailures),
      retry: safeProbe('retry', retryObservation, probeFailures),
      redSignals: safeProbe('red-signals', redSignalObservation, probeFailures),
      systemSurfaces: safeProbe('system-surfaces', systemSurfaceObservation, probeFailures),
      selectors: safeProbe('selectors', selectorDiagnostics, probeFailures),
      turns: safeProbe('turns', compactTurnSummaries, probeFailures, []),
      actions: actionReceiptSnapshot(),
      boot: state.boot,
      persistence: { ...state.persistence, priorContinuity: state.priorContinuity },
      pageErrors: state.pageErrors.slice(-MAX_PAGE_ERROR_RECORDS),
      resourceTiming: { available: resource.available, entryCount: resource.entryCount, bufferLikelyCapped: resource.bufferLikelyCapped, endpoints: resource.endpoints, recent: (resource.recent || []).slice(-12), limitations: resource.limitations },
      events: state.events.slice(-50),
      probeFailures,
      boundaries: {
        automaticModelSelection: 'bounded-newest-eligible-Pro-before-every-Send',
        modelSelectionCrossTabAuthority: false,
        noAutomaticRetry: true,
        automaticRetryScope: 'none; native Retry is not clicked',
        noFaultTriggeredReload: true,
        automaticReloadScope: settings.hourlyRefresh ? 'operator-enabled safe refresh: selected interval plus bounded newly appeared historical/unowned pipeline-failure healing; never current owned fault recovery' : 'disabled; no reload path',
        noKeepAwakeAudio: true,
        noCrossTabDiscovery: true,
        noCrossTabListener: true,
        noOfficerSelfLoop: true,
        noRecurringTimerWhileStopped: true,
        noMutationObserver: true,
        noPerformanceObserver: true,
        onDemandOfficerHandoff: true,
        polyglotBashWorkbench: true,
        officeAndBoundedLineage: true,
      },
    };
    let text = JSON.stringify(payload, null, 2);
    if (utf8Bytes(text) > MAX_DIAGNOSTIC_UTF8_BYTES) {
      payload.events = payload.events.slice(-16);
      payload.turns = payload.turns.slice(-4);
      payload.pageErrors = payload.pageErrors.slice(-8).map(row => ({ ...row, stack: trunc(row && row.stack || '', 800) }));
      if (payload.redSignals && payload.redSignals.signals) payload.redSignals.signals = payload.redSignals.signals.slice(-8);
      if (payload.systemSurfaces && payload.systemSurfaces.surfaces) payload.systemSurfaces.surfaces = payload.systemSurfaces.surfaces.slice(-8);
      if (payload.resourceTiming) {
        payload.resourceTiming.recent = (payload.resourceTiming.recent || []).slice(-8);
        const entries = Object.entries(payload.resourceTiming.endpoints || {}).sort((a, b) => b[1] - a[1]).slice(0, 40);
        payload.resourceTiming.endpoints = Object.fromEntries(entries);
      }
      if (payload.persistence && payload.persistence.priorContinuity) {
        const prior = payload.persistence.priorContinuity;
        payload.persistence.priorContinuity = { schema: prior.schema || null, version: prior.version || null, sourceId: prior.sourceId || null, capturedAt: prior.capturedAt || null, reason: prior.reason || null, runningAtCapture: !!prior.runningAtCapture, phase: prior.phase || null, authority: prior.authority || null, note: 'details reduced for compact diagnostics' };
      }
      payload.diagnosticsManifest = { maxUtf8Bytes: MAX_DIAGNOSTIC_UTF8_BYTES, reduced: true, complete: true };
      text = JSON.stringify(payload, null, 2);
    }
    if (utf8Bytes(text) > MAX_DIAGNOSTIC_UTF8_BYTES) {
      const originalBytes = utf8Bytes(text);
      const minimal = {
        schema: payload.schema,
        generatedAt: payload.generatedAt,
        source: payload.source,
        page: payload.page,
        runtime: {
          schema: payload.runtime.schema, running: payload.runtime.running, paused: payload.runtime.paused, phase: payload.runtime.phase, phaseReason: payload.runtime.phaseReason, sends: payload.runtime.sends, completedReplies: payload.runtime.completedReplies, zipClicks: payload.runtime.zipClicks, zipActivationErrors: payload.runtime.zipActivationErrors, lastError: payload.runtime.lastError ? { kind: payload.runtime.lastError.kind || null, message: trunc(payload.runtime.lastError.message || payload.runtime.phaseReason || '', 1_000) } : null, scheduler: payload.runtime.scheduler, metrics: payload.runtime.metrics,
        },
        actions: { active: compactReceiptForDiagnostics(payload.actions.active), latest: compactReceiptForDiagnostics(payload.actions.latest) },
        pageErrors: payload.pageErrors.slice(-4),
        probeFailures: payload.probeFailures,
        diagnosticsManifest: { maxUtf8Bytes: MAX_DIAGNOSTIC_UTF8_BYTES, reduced: true, complete: false, originalBytes, note: 'fallback summary emitted as valid JSON instead of truncating serialized text' },
      };
      text = JSON.stringify(minimal, null, 2);
    }
    const duration = Math.max(0, performance.now() - started);
    state.metrics.diagnosticsLastMs = Math.round(duration * 100) / 100;
    state.metrics.diagnosticsMaxMs = Math.max(state.metrics.diagnosticsMaxMs, state.metrics.diagnosticsLastMs);
    return `QOMRADE-COMPACT-DIAGNOSTICS-BEGIN\n${text}\nQOMRADE-COMPACT-DIAGNOSTICS-END`;
    });
  }
  async function copyDiagnostics() {
    const text = buildDiagnostics();
    try {
      await copyTextToClipboard(text);
      showMessage(`Copied ${text.length.toLocaleString()} characters of current-tab diagnostics.`, false);
      logEvent('diagnostics', 'Copied compact current-tab diagnostics.', { chars: text.length, buildDurationMs: state.metrics.diagnosticsLastMs });
    } catch (error) {
      recordPageError({ kind: 'diagnostics-copy-error', message: String(error && error.message || error) });
      showMessage(`Copy diagnostics failed: ${error && error.message || error}`, true);
    }
  }
  function utf8Bytes(value) {
    return new TextEncoder().encode(String(value == null ? '' : value)).length;
  }
  function fnv1a64(value) {
    let hash = 0xcbf29ce484222325n;
    const prime = 0x100000001b3n;
    const text = String(value == null ? '' : value);
    for (let i = 0; i < text.length; i += 1) {
      const code = text.charCodeAt(i);
      hash ^= BigInt(code & 0xff);
      hash = BigInt.asUintN(64, hash * prime);
      if (code >>> 8) {
        hash ^= BigInt(code >>> 8);
        hash = BigInt.asUintN(64, hash * prime);
      }
    }
    return hash.toString(16).padStart(16, '0');
  }
  function uniquePush(array, value) {
    if (value && !array.includes(value)) array.push(value);
  }
  function structuredSessionNodeText(root) {
    if (!(root instanceof Node)) return '';
    const skip = 'button,[role="button"],svg,script,style,noscript,[aria-hidden="true"],[role="separator"],time,.turn-action-controls,[data-markdown-copy="exclude"],h4.sr-only,[class~="sr-only"],[data-testid*="copy" i],[aria-label*="Copy response" i],[aria-label*="Good response" i],[aria-label*="Bad response" i],[aria-label*="More actions" i]';
    const blocks = new Set(['P','DIV','SECTION','ARTICLE','LI','PRE','BLOCKQUOTE','H1','H2','H3','H4','H5','H6','UL','OL','TABLE','TR']);
    let output = '';
    const br = () => { if (output && !output.endsWith('\n')) output += '\n'; };
    const visit = node => {
      if (node.nodeType === Node.TEXT_NODE) { output += node.nodeValue || ''; return; }
      if (node.nodeType !== Node.ELEMENT_NODE) return;
      const element = node;
      if (element.matches(skip) || element.hidden) return;
      if (element.tagName === 'BR') { output += '\n'; return; }
      const block = blocks.has(element.tagName), cell = element.tagName === 'TD' || element.tagName === 'TH';
      if (block) br();
      for (const child of element.childNodes) visit(child);
      if (cell) output += '\t'; else if (block) br();
    };
    visit(root);
    return normalizePromptLineEndings(output).replace(/[ \t]+\n/g, '\n').replace(/\n{3,}/g, '\n\n').trim();
  }
  function sessionArtifactFilename(node) {
    if (!(node instanceof Element)) return null;
    const attr = name => node.getAttribute(name) || '';
    for (let value of [attr('data-markdown-copy-text'), attr('download'), attr('aria-label'), attr('title'), node.tagName === 'A' ? attr('href') : '', node.textContent || '']) {
      value = normalizeCompactText(value).replace(/^(?:Download|Open preview of|Attached file:?|File:?|Image:?)[\s:]+/i, '').split(/[?#]/, 1)[0];
      try { value = decodeURIComponent(value); } catch (_) {}
      value = value.split(/[\\/]/).at(-1).trim();
      if (value && value.length <= 300 && /\.[a-z0-9][a-z0-9._+-]{0,30}$/i.test(value)) return value;
    }
    return null;
  }
  function sessionTurnArtifacts(turn) {
    if (!turn?.element) return [];
    const output = [], seen = new Set();
    const add = row => { const key = `${row.kind}|${row.name || row.label}`; if (!seen.has(key)) seen.add(key), output.push(row); };
    for (const node of uniqueElements(['[data-file-reference]','[data-markdown-copy-text]','a[download]','[aria-label^="Download " i]'], turn.element).slice(0, 64)) {
      if (node.closest('pre,code')) continue;
      const name = sessionArtifactFilename(node) || sessionArtifactFilename(node.parentElement);
      if (name) add({ kind: turn.role === 'user' ? 'attached-file' : 'generated-file', name, label: trunc(normalizeCompactText(node.textContent || node.getAttribute('aria-label') || ''), 300) || null });
    }
    for (const image of qa('img[alt]', turn.element).slice(0, 16)) {
      const label = normalizeCompactText(image.getAttribute('alt') || '');
      if (label && !/^(?:image|icon|avatar|logo)$/i.test(label)) add({ kind: turn.role === 'user' ? 'attached-image' : 'generated-image', name: null, label: trunc(label, 300) });
    }
    return output.slice(0, 32);
  }
  function sessionTurnText(turn) {
    const roots = turn?.role === 'assistant' && turn.element ? qa('[data-message-author-role="assistant"]', turn.element).filter(node => !node.parentElement?.closest('[data-message-author-role="assistant"]')) : [];
    return turn?.element ? (roots.length ? roots.map(structuredSessionNodeText).filter(Boolean).join('\n\n') : structuredSessionNodeText(turn.element)).replace(/^\s*(?:You|ChatGPT) said\s*:\s*/i, '').trim() : '';
  }
  function clipSessionTurnText(value) {
    const text = normalizePromptLineEndings(value);
    if (text.length <= MAX_SESSION_TURN_CHARS) return { text, truncated: false };
    const keep = Math.floor((MAX_SESSION_TURN_CHARS - 120) / 2);
    return { text: `${text.slice(0, keep)}\n\n[... middle omitted because this single turn exceeded the Session Handoff turn limit ...]\n\n${text.slice(-keep)}`, truncated: true };
  }
  function beginSessionArchive(origin = 'page-boot') {
    const conversationId = state.anchorConversationId || conversationIdFromPath(), explicitStart = origin === 'operator-start', prior = state.sessionArchive;
    if (prior?.sessionId && Array.isArray(prior.turns) && prior.conversationId === conversationId && prior.pathname === location.pathname) {
      prior.schema = 'qomrade.session-record.v3'; prior.endedAt = null;
      prior.visibleArtifactCount = Number(prior.visibleArtifactCount) || prior.turns.reduce((sum, row) => sum + (Array.isArray(row.artifacts) ? row.artifacts.length : 0), 0);
      prior.naturalScrollCaptures = Number(prior.naturalScrollCaptures) || 0; prior.lastNaturalScrollAt ||= null; prior.lastSurfaceSignature ||= null;
      if (state.runPrompt) prior.promptHash = fnv1a64(state.runPrompt), prior.promptChars = state.runPrompt.length;
      if (explicitStart) prior.runStarts = (Number(prior.runStarts) || 0) + 1, prior.lastStartAt = nowIso();
      logEvent('session-record-continued', explicitStart ? 'Continued the same ChatGPT transcript across another explicit Start.' : 'Continued observing the same ChatGPT transcript.', { origin, sessionId: prior.sessionId, conversationId, runStarts: prior.runStarts, turns: prior.turns.length });
      return prior;
    }
    const at = nowIso();
    state.sessionArchive = { schema: 'qomrade.session-record.v3', sessionId: `session-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 8)}`, startedAt: at, endedAt: null,
      runStarts: explicitStart ? 1 : 0, lastStartAt: explicitStart ? at : null, conversationId, pathname: location.pathname,
      promptHash: state.runPrompt ? fnv1a64(state.runPrompt) : null, promptChars: state.runPrompt.length, captures: 0, lastCaptureAt: null, turns: [], totalUtf8Bytes: 0,
      visibleArtifactCount: 0, truncatedTurns: 0, skippedTurns: 0, restoredAcrossRefresh: false,
      omissions: ['Only user and assistant content that appeared in this ChatGPT tab is available; unloaded, never-materialized, or already-missing content may be absent.', 'Visible file and image cards can be named, but their bytes are not embedded in the transcript.'],
      naturalScrollCaptures: 0, lastNaturalScrollAt: null, lastSurfaceSignature: null, backfill: { active: false, attempts: 0, last: null } };
    logEvent('session-record-started', 'Started observing the ChatGPT context-river transcript.', { origin, sessionId: state.sessionArchive.sessionId, conversationId });
    return state.sessionArchive;
  }
  function sessionTurnKey(turn) {
    const role = turn?.role || 'unknown', ordinal = Number(turn?.ordinal);
    return turn?.id ? `${role}:id:${turn.id}` : Number.isFinite(ordinal) ? `${role}:ordinal:${ordinal}` : `${role}:unknown`;
  }
  function sessionMaterializedSignature(turns = materializedTurns()) {
    return fnv1a64(turns.filter(turn => turn.role === 'user' || turn.role === 'assistant').map(turn => `${turn.role}|${turn.id || ''}|${turn.ordinal ?? ''}|${turn.adapter || ''}`).join('\n'));
  }
  function captureSessionTurns(origin = 'surface-edge') {
    invalidateTurnCache(`session-capture:${origin}`);
    const archive = state.sessionArchive?.sessionId ? state.sessionArchive : beginSessionArchive('page-observation');
    const turns = materializedTurns().filter(turn => turn.role === 'user' || turn.role === 'assistant');
    let captured = 0, skipped = 0;
    for (const turn of turns) {
      const raw = sessionTurnText(turn), artifacts = sessionTurnArtifacts(turn);
      if (!raw && !artifacts.length) continue;
      const key = sessionTurnKey(turn), ordinal = Number(turn.ordinal), rawHash = fnv1a64(raw), artifactHash = fnv1a64(JSON.stringify(artifacts));
      const ordinalUnique = Number.isFinite(ordinal) && turns.filter(row => row.role === turn.role && Number(row.ordinal) === ordinal).length === 1;
      const existing = archive.turns.find(row => row.key === key || (turn.id && row.role === turn.role && row.id === turn.id) || (ordinalUnique && row.role === turn.role && Number(row.ordinal) === ordinal));
      if (existing && raw.length === existing.originalChars && rawHash === existing.textHash && artifactHash === (existing.artifactHash || fnv1a64(JSON.stringify(existing.artifacts || [])))) {
        existing.id = turn.id || existing.id; existing.key = key; existing.adapter = turn.adapter || existing.adapter; existing.lastObservedAt = nowIso(); continue;
      }
      const clipped = clipSessionTurnText(raw), bytes = utf8Bytes(clipped.text) + utf8Bytes(JSON.stringify(artifacts)), observedAt = nowIso();
      if (existing) {
        const wasTruncated = !!existing.truncated;
        archive.totalUtf8Bytes = Math.max(0, archive.totalUtf8Bytes - (Number(existing.utf8Bytes) || 0) + bytes);
        Object.assign(existing, { key, id: turn.id, ordinal: turn.ordinal, adapter: turn.adapter, role: turn.role, text: clipped.text, artifacts, originalChars: raw.length,
          utf8Bytes: bytes, textHash: rawHash, artifactHash, truncated: clipped.truncated, lastObservedAt: observedAt, unresolvedWork: turn.role === 'assistant' ? assistantWorkOnly(turn.element) : false });
        if (clipped.truncated !== wasTruncated) archive.truncatedTurns = Math.max(0, archive.truncatedTurns + (clipped.truncated ? 1 : -1));
        captured += 1; continue;
      }
      if (archive.turns.length >= MAX_SESSION_TURNS || archive.totalUtf8Bytes + bytes > MAX_SESSION_ARCHIVE_UTF8_BYTES) {
        archive.skippedTurns += 1; skipped += 1;
        uniquePush(archive.omissions, `The bounded transcript recorder reached ${MAX_SESSION_TURNS} turns or ${MAX_SESSION_ARCHIVE_UTF8_BYTES} UTF-8 bytes; later newly observed turns may be omitted.`); continue;
      }
      archive.turns.push({ key, id: turn.id, ordinal: turn.ordinal, adapter: turn.adapter, role: turn.role, text: clipped.text, artifacts, originalChars: raw.length,
        utf8Bytes: bytes, textHash: rawHash, artifactHash, truncated: clipped.truncated, firstObservedAt: observedAt, lastObservedAt: observedAt,
        unresolvedWork: turn.role === 'assistant' ? assistantWorkOnly(turn.element) : false });
      archive.totalUtf8Bytes += bytes; if (clipped.truncated) archive.truncatedTurns += 1; captured += 1;
    }
    archive.visibleArtifactCount = archive.turns.reduce((sum, row) => sum + (Array.isArray(row.artifacts) ? row.artifacts.length : 0), 0);
    archive.captures += 1; archive.lastCaptureAt = nowIso(); archive.lastSurfaceSignature = sessionMaterializedSignature(turns);
    if (origin.startsWith('natural-scroll')) archive.naturalScrollCaptures += 1, archive.lastNaturalScrollAt = archive.lastCaptureAt;
    if (captured || skipped) logEvent('session-record-captured', 'Updated the bounded ChatGPT context-river transcript.', { origin, captured, skipped, turns: archive.turns.length, visibleArtifacts: archive.visibleArtifactCount, totalUtf8Bytes: archive.totalUtf8Bytes });
    return { captured, skipped, turns: archive.turns.length, visibleArtifacts: archive.visibleArtifactCount };
  }
  function captureSessionTurnsIfSurfaceChanged(origin = 'natural-scroll') {
    const archive = state.sessionArchive?.sessionId ? state.sessionArchive : beginSessionArchive('page-observation');
    invalidateTurnCache(`session-surface:${origin}`);
    const signature = sessionMaterializedSignature();
    return signature === archive.lastSurfaceSignature ? { captured: 0, skipped: 0, turns: archive.turns.length, reason: 'surface-unchanged' } : captureSessionTurns(origin);
  }
  function scheduleNaturalScrollSessionCapture() {
    if (ui.sessionScrollTimer) clearTimeout(ui.sessionScrollTimer);
    ui.sessionScrollTimer = setTimeout(() => {
      ui.sessionScrollTimer = null;
      try { captureSessionTurnsIfSurfaceChanged('natural-scroll-settled'); }
      catch (error) { recordPageError({ kind: 'session-scroll-capture-error', message: String(error && error.message || error) }); }
    }, 650);
  }
  function sessionOrdinalCoverage() {
    const ordinals = [...new Set(state.sessionArchive.turns.map(row => Number(row.ordinal)).filter(Number.isFinite))].sort((a,b)=>a-b), missing = [];
    if (ordinals.length) for (let n=ordinals[0]; n<=ordinals.at(-1) && missing.length<64; n++) if (!ordinals.includes(n)) missing.push(n);
    return { first: ordinals[0] ?? null, last: ordinals.at(-1) ?? null, count: ordinals.length, missing, missingTruncated: missing.length >= 64 };
  }
  function sessionArchiveSummary() {
    const archive = state.sessionArchive, coverage = sessionOrdinalCoverage();
    return { schema: archive.schema, sessionId: archive.sessionId, startedAt: archive.startedAt, endedAt: archive.endedAt, runStarts: Number(archive.runStarts) || 0,
      lastStartAt: archive.lastStartAt || null, conversationId: archive.conversationId, promptHash: archive.promptHash, promptChars: archive.promptChars, captures: archive.captures,
      lastCaptureAt: archive.lastCaptureAt, observedTurns: archive.turns.length, totalUtf8Bytes: archive.totalUtf8Bytes, visibleArtifactCount: Number(archive.visibleArtifactCount) || 0,
      truncatedTurns: archive.truncatedTurns, skippedTurns: archive.skippedTurns, naturalScrollCaptures: Number(archive.naturalScrollCaptures) || 0, lastNaturalScrollAt: archive.lastNaturalScrollAt || null,
      exportMode: 'no-scroll', ordinalCoverage: coverage, backfill: archive.backfill || null, restoredAcrossRefresh: archive.restoredAcrossRefresh, omissions: archive.omissions.slice(-8),
      archiveLimitBytes: MAX_SESSION_ARCHIVE_UTF8_BYTES, refreshTicketBudgetBytes: MAX_SESSION_ARCHIVE_PERSIST_UTF8_BYTES,
      authority: 'operator-requested conversation transcript evidence only; never a Send permit' };
  }
  async function backfillSessionTranscript(origin = 'session-handoff-export') {
    const archive = beginSessionArchive('page-observation');
    if (archive.backfill?.active) return archive.backfill.last;
    archive.backfill ||= { active: false, attempts: 0, last: null }; archive.backfill.active = true; archive.backfill.attempts += 1;
    const started = performance.now(), before = archive.turns.length;
    try { captureSessionTurns(`${origin}:no-scroll`); }
    finally {
      archive.backfill.active = false;
      archive.backfill.last = { at: nowIso(), origin, attempted: true, mode: 'no-scroll', passes: 0, reachedTop: null, reason: 'no-scroll-export',
        newTurns: archive.turns.length - before, visibleArtifacts: archive.visibleArtifactCount, viewportMoved: false, durationMs: Math.round(performance.now() - started) };
      logEvent('session-export-capture', 'Captured currently available transcript evidence without moving the conversation viewport.', archive.backfill.last);
    }
    return archive.backfill.last;
  }
  function sessionArchivePersistentSnapshot() {
    const archive = state.sessionArchive;
    if (!archive?.sessionId) return null;
    const base = { ...sessionArchiveSummary(), turns: [], persistenceComplete: true, persistenceBudgetBytes: MAX_SESSION_ARCHIVE_PERSIST_UTF8_BYTES };
    const rows = archive.turns.map((turn, index) => ({
      index,
      value: { key: turn.key, id: turn.id, ordinal: turn.ordinal, adapter: turn.adapter, role: turn.role, text: turn.text, artifacts: turn.artifacts || [], originalChars: turn.originalChars, utf8Bytes: turn.utf8Bytes, textHash: turn.textHash, artifactHash: turn.artifactHash || fnv1a64(JSON.stringify(turn.artifacts || [])), truncated: turn.truncated, firstObservedAt: turn.firstObservedAt, lastObservedAt: turn.lastObservedAt, unresolvedWork: turn.unresolvedWork },
    }));
    let bytes = utf8Bytes(JSON.stringify(base));
    const sized = rows.map(row => ({ ...row, bytes: utf8Bytes(JSON.stringify(row.value)) }));
    const total = bytes + sized.reduce((sum, row) => sum + row.bytes, 0);
    if (total <= MAX_SESSION_ARCHIVE_PERSIST_UTF8_BYTES) {
      base.turns = sized.map(row => row.value);
      base.persistenceBytes = total;
      return base;
    }
    base.persistenceComplete = false;
    const selected = new Map();
    const add = row => {
      if (!row || selected.has(row.index) || bytes + row.bytes > MAX_SESSION_ARCHIVE_PERSIST_UTF8_BYTES) return false;
      selected.set(row.index, row.value);
      bytes += row.bytes;
      return true;
    };
    // Keep bounded opening context, then prioritize the newest state and unresolved work.
    for (const row of sized.slice(0, Math.min(6, sized.length))) add(row);
    for (let index = sized.length - 1; index >= 0; index -= 1) add(sized[index]);
    // Use any remaining budget for middle turns in conversation order.
    for (const row of sized) add(row);
    base.turns = [...selected.entries()].sort((a, b) => a[0] - b[0]).map(([, value]) => value);
    base.persistenceBytes = bytes;
    base.persistenceOmission = `The exact hourly-refresh ticket preserved ${base.turns.length} of ${rows.length} observed turns within ${MAX_SESSION_ARCHIVE_PERSIST_UTF8_BYTES} UTF-8 bytes, prioritizing opening context and the newest state. Save Session Handoff before refresh when the live transcript is larger.`;
    return base;
  }
  function restoreSessionArchive(snapshot) {
    if (!snapshot || !['qomrade.session-record.v1','qomrade.session-record.v2','qomrade.session-record.v3'].includes(snapshot.schema) || !snapshot.sessionId || !Array.isArray(snapshot.turns)) return false;
    state.sessionArchive = {
      schema: 'qomrade.session-record.v3', sessionId: snapshot.sessionId, startedAt: snapshot.startedAt || nowIso(), endedAt: snapshot.endedAt || null,
      runStarts: Math.max(1, Number(snapshot.runStarts) || 1), lastStartAt: snapshot.lastStartAt || snapshot.startedAt || nowIso(),
      conversationId: snapshot.conversationId || conversationIdFromPath(), pathname: snapshot.pathname || location.pathname,
      promptHash: snapshot.promptHash || null, promptChars: Number(snapshot.promptChars) || 0,
      captures: Number(snapshot.captures) || 0, lastCaptureAt: snapshot.lastCaptureAt || null,
      turns: snapshot.turns.slice(0, MAX_SESSION_TURNS).map(row => ({ ...row, artifacts: Array.isArray(row.artifacts) ? row.artifacts.slice(0, 32) : [] })),
      totalUtf8Bytes: snapshot.turns.reduce((sum, row) => sum + (Number(row.utf8Bytes) || utf8Bytes(row.text || '') + utf8Bytes(JSON.stringify(row.artifacts || []))), 0),
      visibleArtifactCount: Number(snapshot.visibleArtifactCount) || snapshot.turns.reduce((sum, row) => sum + (Array.isArray(row.artifacts) ? row.artifacts.length : 0), 0),
      truncatedTurns: Number(snapshot.truncatedTurns) || 0, skippedTurns: Number(snapshot.skippedTurns) || 0,
      naturalScrollCaptures: Number(snapshot.naturalScrollCaptures) || 0, lastNaturalScrollAt: snapshot.lastNaturalScrollAt || null, lastSurfaceSignature: null,
      restoredAcrossRefresh: true,
      omissions: Array.isArray(snapshot.omissions) ? snapshot.omissions.slice(-8) : [],
      backfill: snapshot.backfill && typeof snapshot.backfill === 'object' ? { ...snapshot.backfill, active: false } : { active: false, attempts: 0, last: null },
    };
    if (snapshot.persistenceComplete === false) uniquePush(state.sessionArchive.omissions, snapshot.persistenceOmission || 'The hourly-refresh ticket carried only a bounded part of the prior page transcript.');
    logEvent('session-record-restored', 'Restored the bounded session transcript carried by the exact hourly-refresh ticket.', { sessionId: snapshot.sessionId, turns: state.sessionArchive.turns.length, persistenceComplete: snapshot.persistenceComplete !== false });
    return true;
  }
  function boundedJsonBytes(value) {
    try { return utf8Bytes(JSON.stringify(value)); }
    catch (_) { return null; }
  }
  function navigationLifecycleObservation() {
    let navigation = null;
    try {
      const entry = performance.getEntriesByType('navigation')[0];
      if (entry) navigation = { type: entry.type || null, startTime: entry.startTime || 0, duration: Math.round((entry.duration || 0) * 100) / 100 };
    } catch (_) {}
    return {
      schema: 'qomrade.navigation-lifecycle.v1',
      navigation,
      timeOrigin: Number.isFinite(performance.timeOrigin) ? performance.timeOrigin : null,
      documentWasDiscardedAvailable: 'wasDiscarded' in document,
      documentWasDiscarded: 'wasDiscarded' in document ? !!document.wasDiscarded : null,
      priorRunEvidence: state.priorContinuity ? {
        runningAtCapture: !!state.priorContinuity.runningAtCapture,
        pausedAtCapture: !!state.priorContinuity.pausedAtCapture,
        phase: state.priorContinuity.phase || null,
        reason: state.priorContinuity.reason || null,
        capturedAt: state.priorContinuity.capturedAt || null,
        exactSafeRefreshTicketPresent: !!state.autoRefresh.pendingResume,
      } : null,
      authority: 'observation only; an unloaded or un-ticketed prior run never resumes automation',
    };
  }
  function memoryPressureObservation() {
    const performanceMemory = performance && performance.memory ? {
      available: true,
      jsHeapSizeLimit: Number(performance.memory.jsHeapSizeLimit) || null,
      totalJSHeapSize: Number(performance.memory.totalJSHeapSize) || null,
      usedJSHeapSize: Number(performance.memory.usedJSHeapSize) || null,
      note: 'non-standard browser estimate; absent in ordinary Firefox',
    } : { available: false, note: 'Firefox exposes no standard per-page JS heap measurement to this userscript.' };
    const retained = {
      events: boundedJsonBytes(state.events),
      modelGate: boundedJsonBytes({ ...state.modelGate, recentSurveys: state.modelGate.recentSurveys.slice(-MAX_MODEL_SURVEY_RECORDS) }),
      science: boundedJsonBytes(state.science),
      turnReceipts: boundedJsonBytes(state.turnReceipts),
      faultEvidence: boundedJsonBytes({ incidents: state.faultIncidents, recovery: state.faultRecovery.ledger }),
      sessionTranscriptText: Number(state.sessionArchive.totalUtf8Bytes) || 0,
      domishSnapshots: Number(state.domForensics.totalUtf8Bytes) || 0,
    };
    const known = Object.values(retained).filter(Number.isFinite).reduce((sum, value) => sum + value, 0);
    return {
      schema: 'qomrade.memory-pressure-proxy.v1',
      at: nowIso(),
      page: {
        elementCount: document.getElementsByTagName('*').length,
        materializedTurns: materializedTurns().length,
        title: document.title,
        hidden: document.hidden,
      },
      qomradeRetainedApproximation: {
        componentsUtf8Bytes: retained,
        knownTotalUtf8Bytes: known,
        meaning: 'serialized evidence-size proxy, not live heap or retained-object size',
      },
      cumulativeWork: {
        selectorQueries: state.metrics.selectorQueries,
        turnTextReads: state.metrics.turnTextReads,
        turnTextCacheHits: state.metrics.turnTextCacheHits,
        turnTextReadsSuppressedWhileGenerating: state.metrics.turnTextReadsSuppressedWhileGenerating,
        turnTextChars: state.metrics.turnTextChars,
        ticks: state.metrics.ticks,
      },
      browser: {
        performanceMemory,
        measureUserAgentSpecificMemoryAvailable: typeof performance.measureUserAgentSpecificMemory === 'function',
        navigatorDeviceMemory: Number.isFinite(Number(navigator.deviceMemory)) ? Number(navigator.deviceMemory) : null,
      },
      navigation: navigationLifecycleObservation(),
      limitation: 'This cannot attribute Firefox process, React, compositor, image, network-cache, or other-tab memory. Use Firefox process/about:memory tools for actual browser attribution.',
      authority: 'evidence only; never changes settings or unloads a tab',
    };
  }
  function maintenanceRecommendation() {
    const replies = state.completedReplies;
    const faults = state.faultIncidents.filter(row => row && row.runningAtObservation).length;
    const reloads = state.autoRefresh.reloads;
    const deferrals = state.autoRefresh.deferrals;
    const late = state.scheduler.lateCount;
    let refreshMinutes = 60, reason = 'One-hour maintenance is the balanced baseline.', confidence = 'low';
    if (reloads >= 2 || faults >= 4 || late >= 4) {
      refreshMinutes = 45;
      reason = 'This tab has repeated refresh use, active faults, or late callbacks; a 45-minute checkpoint may be useful.';
      confidence = 'medium';
    } else if (replies >= 4 && reloads === 0 && faults === 0 && late === 0) {
      refreshMinutes = 120;
      reason = 'This run has several clean replies without refreshes, faults, or late callbacks; two hours may reduce maintenance churn.';
      confidence = 'medium';
    } else if (reloads >= 1 || replies >= 2) {
      confidence = 'medium';
    }
    const trimSuggested = state.sessionArchive.turns.length > 12 || state.metrics.turnTextChars > 500_000;
    return {
      schema: 'qomrade.maintenance-recommendation.v1', generatedAt: nowIso(), refreshMinutes, confidence, reason,
      trim: settings.trimOldTurns ? 'keep-enabled' : trimSuggested ? 'consider-enabling' : 'optional',
      evidence: { completedReplies: replies, faultIncidents: faults, refreshReloads: reloads, refreshDeferrals: deferrals, timerLateCount: late, observedSessionTurns: state.sessionArchive.turns.length },
      authority: 'advice only; qomrade never changes maintenance settings from this recommendation',
    };
  }
  function orderedSessionTranscriptTurns() {
    return state.sessionArchive.turns.map((turn, index) => ({ turn, index })).sort((left, right) => {
      const a = Number(left.turn.ordinal), b = Number(right.turn.ordinal);
      const aKnown = Number.isFinite(a), bKnown = Number.isFinite(b);
      if (aKnown && bKnown && a !== b) return a - b;
      if (aKnown !== bKnown) return aKnown ? -1 : 1;
      return left.index - right.index;
    }).map(row => row.turn);
  }
  function markdownFence(text) {
    const matches = String(text || '').match(/`+/g) || [];
    const longest = matches.reduce((max, value) => Math.max(max, value.length), 0);
    return '`'.repeat(Math.max(3, longest + 1));
  }
  function sessionArtifactMarkdown(artifact) {
    const labels = { 'attached-file': 'Attached file', 'generated-file': 'Generated file', 'attached-image': 'Attached image', 'generated-image': 'Generated image' };
    const value = normalizeCompactText(artifact?.name || artifact?.label || '').replace(/`/g, "'");
    return value ? `- ${labels[artifact.kind] || 'Visible item'}: ${value}` : null;
  }
  function appendSessionTranscriptTurns(lines, turns) {
    for (const turn of turns) {
      const label = turn.role === 'assistant' ? 'Assistant' : 'User', fence = markdownFence(turn.text || ''), artifactLines = (turn.artifacts || []).map(sessionArtifactMarkdown).filter(Boolean);
      lines.push(`### ${label}`, '');
      lines.push(...(turn.text ? [fence, turn.text, fence, ''] : ['(No textual body was available for this turn.)', '']));
      if (artifactLines.length) lines.push('Visible context items:', '', ...artifactLines, '');
    }
  }
  function buildSessionHandoff() {
    if (!state.sessionArchive.sessionId) beginSessionArchive('session-handoff-without-run');
    captureSessionTurns('session-handoff-export');
    const archive = state.sessionArchive, generatedAt = nowIso(), turns = orderedSessionTranscriptTurns(), coverage = sessionOrdinalCoverage();
    const coverageStatus = coverage.first === 1 && !coverage.missing.length ? 'contiguous-from-1' : coverage.missing.length ? 'ordinal-gaps-observed' : 'bounded-observation';
    const lines = [
      'CHATGPT-SESSION-HANDOFF-BEGIN', 'schema=chatgpt.session-handoff.v2', `generated_at=${generatedAt}`,
      `conversation_id=${archive.conversationId || conversationIdFromPath() || ''}`, `captured_turns=${turns.length}`, `capture_started_at=${archive.startedAt || ''}`,
      `first_observed_ordinal=${coverage.first ?? ''}`, `last_observed_ordinal=${coverage.last ?? ''}`, `ordinal_gaps=${coverage.missing.join(',')}`,
      `coverage_status=${coverageStatus}`, 'capture_mode=no-scroll', `visible_context_items=${Number(archive.visibleArtifactCount) || 0}`,
      `history_probe=${archive.backfill?.last?.reason || 'no-scroll-export'}`, '', '# ChatGPT Session Handoff', '',
      'This file contains user and assistant content captured from the ChatGPT web interface, in conversation order.', '', '## Transcript', '',
    ];
    appendSessionTranscriptTurns(lines, turns);
    if (!turns.length) lines.push('(No user or assistant turns were available in the ChatGPT page.)', '');
    lines.push('## Capture note', '', 'This export did not move the conversation viewport. It includes content that appeared in this tab and any visible file or image-card names the page exposed. Content that never materialized, was already unavailable, or existed only inside attached/generated file bytes may still be absent.');
    for (const omission of [...new Set((archive.omissions || []).filter(Boolean))]) lines.push(`- ${String(omission).replace(/qomrade/gi, 'the recorder')}`);
    lines.push('', 'CHATGPT-SESSION-HANDOFF-END');
    let output = lines.join('\n');
    if (utf8Bytes(output) > MAX_SESSION_HANDOFF_UTF8_BYTES) {
      const tailTurns = turns.slice(-64), reduced = ['CHATGPT-SESSION-HANDOFF-BEGIN', 'schema=chatgpt.session-handoff.v2', `generated_at=${generatedAt}`,
        `conversation_id=${archive.conversationId || conversationIdFromPath() || ''}`, `captured_turns=${tailTurns.length}`, 'transcript_reduced=true', 'capture_mode=no-scroll', '',
        '# ChatGPT Session Handoff', '', `The complete captured transcript exceeded ${MAX_SESSION_HANDOFF_UTF8_BYTES} UTF-8 bytes. The newest ${tailTurns.length} captured turns follow.`, '', '## Transcript', ''];
      appendSessionTranscriptTurns(reduced, tailTurns);
      reduced.push('## Capture note', '', 'This is a bounded no-scroll transcript of content that appeared in the ChatGPT web interface. Earlier captured turns were omitted only because the generated file exceeded its declared size limit.', '', 'CHATGPT-SESSION-HANDOFF-END');
      output = reduced.join('\n');
    }
    return output;
  }
  function compactFlightEvent(event) {
    return { seq: event.seq || null, at: event.at || null, kind: event.kind || null, message: trunc(event.message || '', 600), detail: event.detail == null ? null : trunc(typeof event.detail === 'string' ? event.detail : JSON.stringify(event.detail), 1_500) };
  }
  function buildFlightRecorder() {
    captureSessionTurns('flight-recorder-export');
    const payload = {
      schema: 'qomrade.flight-recorder.v1', generatedAt: nowIso(),
      source: { product: 'qomrade', version: VERSION, sourceId: QOMRADE_SOURCE_ID },
      conversation: { id: conversationIdFromPath(), pathname: location.pathname, title: document.title },
      session: sessionArchiveSummary(),
      state: { running: state.running, paused: state.paused, phase: state.phase, phaseReason: state.phaseReason, terminalStop: state.terminalStop, quarantine: state.quarantine },
      settings: { gapMinutes: settings.gapMinutes, pauseWhenHidden: settings.pauseWhenHidden, autoZip: settings.autoZip, downloadSuffixes: settings.downloadSuffixes, fileDelaySeconds: settings.fileDelaySeconds, trimOldTurns: settings.trimOldTurns, hourlyRefresh: settings.hourlyRefresh, refreshMinutes: settings.refreshMinutes },
      counters: { sends: state.sends, replies: state.completedReplies, zipClicks: state.zipClicks, zipActivationErrors: state.zipActivationErrors, hiddenTicks: state.background.hiddenTicks, lateTimers: state.scheduler.lateCount },
      model: { preference: state.modelGate.runPreference, lastConfirmation: state.modelGate.confirmed, lastCommit: state.modelGate.lastCommit, transitions: state.modelGate.recentSurveys.slice(-8) },
      actions: state.turnReceipts.slice(-MAX_TURN_RECEIPTS).map(compactReceiptForDiagnostics),
      recoveries: recoverySnapshot(),
      maintenance: { domTrim: domTrimSnapshot(), autoRefresh: autoRefreshSnapshot(), recommendation: maintenanceRecommendation() },
      memory: memoryPressureObservation(),
      zipCapture: zipCaptureSnapshot(),
      faults: state.faultIncidents.slice(-16).map(compactFaultIncident),
      pipelineSurfaces: handoffPipelineSurfaceHistory(),
      events: state.events.slice(-MAX_EVENT_RECORDS).map(compactFlightEvent),
      authority: 'compact operator-requested evidence; never a prompt, model, retry, reload, or cross-tab permit',
    };
    let text = JSON.stringify(payload, null, 2);
    if (utf8Bytes(text) > MAX_FLIGHT_RECORDER_UTF8_BYTES) {
      payload.events = payload.events.slice(-32);
      payload.model.transitions = payload.model.transitions.slice(-4);
      payload.faults = payload.faults.slice(-8);
      payload.manifest = { reduced: true, maxUtf8Bytes: MAX_FLIGHT_RECORDER_UTF8_BYTES };
      text = JSON.stringify(payload, null, 2);
    }
    return text;
  }
  function handoffTurns() {
    return materializedTurns().slice(-MAX_HANDOFF_TURNS).map(turn => {
      const text = turnText(turn.element);
      const workMarkers = turn.role === 'assistant' ? uniqueElements(SELECTORS.work.slice(0, 4), turn.element) : [];
      const finalMarkers = turn.role === 'assistant' ? uniqueElements(SELECTORS.finalAnswer, turn.element) : [];
      return {
        index: turn.index,
        id: turn.id,
        ordinal: turn.ordinal,
        adapter: turn.adapter,
        role: turn.role,
        chars: text.length,
        textHash: fnv1a64(text.length > 128_000 ? `${text.slice(0, 64_000)}${text.slice(-64_000)}` : text),
        text: trunc(text, MAX_HANDOFF_TURN_CHARS),
        workMarkerCount: workMarkers.length,
        finalMarkerCount: finalMarkers.length,
        unresolvedWork: turn.role === 'assistant' ? assistantWorkOnly(turn.element) : false,
        structural: {
          turnElement: elementSummary(turn.element, { redactContent: true }),
          workMarkers: workMarkers.slice(0, 12).map(element => elementSummary(element)),
          finalMarkers: finalMarkers.slice(0, 12).map(element => elementSummary(element, { redactContent: true })),
        },
      };
    });
  }
  function contradictionsObservation(authenticity, barrier, work, dialogs, continuation, model) {
    const findings = [];
    if (!state.running && state.timer) findings.push({ kind: 'timer-while-stopped', severity: 'error' });
    if (state.running && state.quarantine) findings.push({ kind: 'running-while-quarantined', severity: 'error' });
    if (authenticity && authenticity.hard && !state.quarantine) findings.push({ kind: 'hard-false-gui-not-yet-quarantined', severity: 'error' });
    if (barrier && barrier.present && state.running) findings.push({ kind: 'running-with-conversation-barrier', severity: 'error' });
    if (work && work.overlapHazard && state.running) findings.push({ kind: 'running-with-qcot-overlap', severity: 'error' });
    if (dialogs && dialogs.blocking && state.phase !== 'DIALOG_HOLD' && state.running) findings.push({ kind: 'visible-dialog-without-dialog-hold', severity: 'warn' });
    if (continuation && continuation.available && state.phase !== 'CONTINUATION_HOLD' && state.running) findings.push({ kind: 'continue-control-without-continuation-hold', severity: 'warn' });
    if (state.running && model && !model.ok && state.phase !== 'MODEL_HOLD' && state.phase !== 'WAITING_REPLY' && state.phase !== 'WORK_HOLD' && state.phase !== 'CONTINUATION_HOLD') findings.push({ kind: 'running-with-unconfirmed-model', severity: 'warn', reason: model.reason });
    return findings;
  }
  function handoffSeverity(kind, message = '') {
    const value = `${kind || ''} ${message || ''}`.toLowerCase();
    if (/quarantine|halt|controller-error|fault-observed|pipeline-fault|qcot-overlap|conversation-replaced|hard-false|error/.test(value)) return 'error';
    if (/hold|deferred|missing|surface|retry|healing|model|continuation|dialog|warning|blocked/.test(value)) return 'warn';
    return 'info';
  }
  function normalizePipelineSurfaceEdgeForHandoff(edge, { domSnapshotId = null, source = 'live' } = {}) {
    if (!edge || typeof edge !== 'object') return null;
    const copy = JSON.parse(JSON.stringify(edge));
    copy.literalTexts = (Array.isArray(copy.literalTexts) ? copy.literalTexts : []).map(row => {
      const value = trunc(normalizeCompactText(row?.text || ''), 640);
      const typed = classifyPipelineFailureText(value);
      const maintenance = classifyPipelineMaintenanceText(value);
      return {
        ...row,
        text: value,
        textHash: row?.textHash || (value ? fnv1a64(value) : null),
        faultKind: row?.faultKind || typed?.faultKind || null,
        maintenanceKind: row?.maintenanceKind || maintenance?.maintenanceKind || null,
        classificationKind: (row?.faultKind || typed) ? 'generation-fault' : (row?.maintenanceKind || maintenance) ? 'maintenance' : 'unknown',
      };
    });
    copy.typedFailure = copy.literalTexts.some(row => row.faultKind);
    copy.maintenance = copy.literalTexts.some(row => row.maintenanceKind);
    copy.unknown = copy.literalTexts.some(row => !row.faultKind && !row.maintenanceKind);
    copy.classified = copy.typedFailure || copy.maintenance;
    copy.severity = copy.typedFailure ? 'error' : 'warn';
    copy.domSnapshotId = copy.domSnapshotId || domSnapshotId || null;
    copy.evidenceSource = source;
    return copy;
  }
  function handoffPipelineSurfaceHistory() {
    const rows = new Map();
    let restoredFromDomishCount = 0;
    for (const snapshot of state.domForensics.snapshots) {
      const context = snapshot && snapshot.context;
      if (!context || context.schema !== 'qomrade.pipeline-surface-edge.v1' || !context.key) continue;
      const normalized = normalizePipelineSurfaceEdgeForHandoff(context, { domSnapshotId: snapshot.id, source: 'domish-restored' });
      if (!normalized) continue;
      rows.set(normalized.key, normalized);
      restoredFromDomishCount += 1;
    }
    for (const edge of state.science.surfaceEdges) {
      const normalized = normalizePipelineSurfaceEdgeForHandoff(edge, { source: 'live' });
      if (!normalized) continue;
      const prior = rows.get(normalized.key);
      if (prior && !normalized.domSnapshotId) normalized.domSnapshotId = prior.domSnapshotId || null;
      rows.set(normalized.key, normalized);
    }
    const edges = [...rows.values()].sort((a, b) => (Date.parse(a.at || '') || 0) - (Date.parse(b.at || '') || 0)).slice(-MAX_PIPELINE_SURFACE_EDGES);
    return {
      schema: 'qomrade.pipeline-surface-history.v1',
      edges,
      liveCount: state.science.surfaceEdges.length,
      restoredFromDomishCount,
      normalizedCount: edges.length,
      coverage: 'live bounded surface-edge ring plus pipeline-surface contexts restored from retained DOMish snapshots',
      authority: 'forensic evidence only; normalization never grants Retry, Send, reload, model, or setting authority',
    };
  }
  function terminalSurfaceTexts(barrier) {
    return [state.terminalStop?.text, state.terminalStop?.observedText, barrier?.current?.text, barrier?.current?.observedText]
      .map(value => normalizeCompactText(value || '').replace(/\s*retry\s*$/i, '').trim())
      .filter(Boolean);
  }
  function retryContextBelongsToTerminal(retry, barrier) {
    if (!(state.terminalStop || barrier?.present) || !retry?.available) return false;
    const terminalTexts = terminalSurfaceTexts(barrier);
    if (!terminalTexts.length) return false;
    return (retry.controls || []).some(control => {
      const texts = [control?.context?.text, control?.text, control?.ariaLabel]
        .map(value => normalizeCompactText(value || '').replace(/\s*retry\s*$/i, '').trim())
        .filter(Boolean);
      return texts.some(value => terminalTexts.some(terminal => value.includes(terminal) || terminal.includes(value)));
    });
  }
  function redSignalsOnlyTerminal(redSignals, barrier) {
    const signals = redSignals?.signals || [];
    if (!signals.length) return true;
    const terminalTexts = terminalSurfaceTexts(barrier);
    if (!terminalTexts.length) return false;
    return signals.every(signal => {
      const value = normalizeCompactText(signal?.text || '').replace(/\s*retry\s*$/i, '').trim();
      return !value || terminalTexts.some(terminal => value.includes(terminal) || terminal.includes(value));
    });
  }
  function canonicalHandoffTimeline(pipelineSurfaces = handoffPipelineSurfaceHistory()) {
    const rows = [];
    const seen = new Set();
    const push = row => {
      if (!row || !row.id || seen.has(row.id)) return;
      seen.add(row.id);
      rows.push(row);
    };
    for (const event of state.events.slice(-MAX_EVENT_RECORDS)) {
      push({
        id: `event:${event.seq}`,
        at: event.at || null,
        t: Number(event.t) || Date.parse(event.at || '') || 0,
        source: 'controller-event',
        kind: event.kind || 'event',
        severity: handoffSeverity(event.kind, event.message),
        summary: trunc(event.message || event.kind || 'event', 1_000),
        evidenceRefs: [`/events/${Math.max(0, state.events.indexOf(event))}`],
        detail: event.detail == null ? null : boundedEventDetail(event.detail),
      });
    }
    for (const fault of state.faultIncidents.slice(-16)) {
      push({
        id: `fault:${fault.id || fault.signature}`,
        at: fault.lastObservedAt || fault.firstObservedAt || null,
        t: Date.parse(fault.lastObservedAt || fault.firstObservedAt || '') || 0,
        source: 'fault-incident',
        kind: fault.faultKind || fault.kind || 'fault',
        severity: 'error',
        summary: trunc(`${fault.faultKind || fault.kind || 'fault'}: ${fault.text || ''}`, 1_000),
        evidenceRefs: ['/runtime/faultIncidents', ...(fault.domSnapshotId ? [`domish:${fault.domSnapshotId}`] : [])],
        detail: { ownerId: fault.ownerId || null, ownerRole: fault.ownerRole || null, observations: fault.observations || 1, activeTransactionId: fault.activeTransactionId || null },
      });
    }
    for (const edge of pipelineSurfaces.edges) {
      push({
        id: `surface:${edge.key}`,
        at: edge.at || null,
        t: Date.parse(edge.at || '') || 0,
        source: 'pipeline-surface-edge',
        kind: 'pipeline-surface-edge',
        severity: edge.severity || (edge.typedFailure ? 'error' : 'warn'),
        summary: trunc(edge.literalTexts?.map(row => row.text).filter(Boolean).join(' | ') || 'visible Retry/pipeline surface changed', 1_000),
        evidenceRefs: ['/pipelineSurfaces/edges', ...(edge.domSnapshotId ? [`domish:${edge.domSnapshotId}`] : [])],
        detail: { retry: edge.retry || null, classified: !!edge.classified, typedFailure: !!edge.typedFailure, maintenance: !!edge.maintenance, unknown: !!edge.unknown, evidenceSource: edge.evidenceSource || null, activeTransactionId: edge.activeTransactionId || null },
      });
    }
    for (const snapshot of state.domForensics.snapshots) {
      push({
        id: `domish:${snapshot.id}`,
        at: snapshot.at || null,
        t: Number(snapshot.t) || Date.parse(snapshot.at || '') || 0,
        source: 'domish-snapshot',
        kind: snapshot.trigger?.kind || 'domish-snapshot',
        severity: snapshot.trigger?.severity || 'warn',
        summary: trunc(snapshot.trigger?.reason || `DOMish snapshot ${snapshot.id}`, 1_000),
        evidenceRefs: [`/domForensics/snapshots/${Math.max(0, state.domForensics.snapshots.indexOf(snapshot))}`],
        detail: { snapshotId: snapshot.id, key: snapshot.key, phase: snapshot.trigger?.phase || null, rootCount: snapshot.roots?.length || 0, utf8Bytes: snapshot.utf8Bytes || null },
      });
    }
    for (const receipt of state.turnReceipts.slice(-MAX_TURN_RECEIPTS)) {
      const at = receipt.completedAt || receipt.clickedAt || receipt.startedAt || null;
      push({
        id: `turn:${receipt.id || fnv1a64(JSON.stringify(receipt))}`,
        at,
        t: Date.parse(at || '') || 0,
        source: 'turn-receipt',
        kind: receipt.outcome || receipt.clickMode || 'turn-receipt',
        severity: handoffSeverity(receipt.outcome, receipt.clickMode),
        summary: trunc(`${receipt.clickMode || 'turn'} → ${receipt.outcome || 'pending'}`, 1_000),
        evidenceRefs: ['/actions/history'],
        detail: compactReceiptForDiagnostics(receipt),
      });
    }
    rows.sort((a, b) => (a.t || 0) - (b.t || 0) || a.id.localeCompare(b.id));
    return {
      schema: 'qomrade.canonical-forensic-timeline.v1',
      ordering: 'ascending observed time; ties break by stable evidence ID',
      count: Math.min(rows.length, MAX_CANONICAL_TIMELINE_RECORDS),
      records: rows.slice(-MAX_CANONICAL_TIMELINE_RECORDS),
      coverage: 'controller events, fault incidents, pipeline-surface edges, DOMish snapshots, and turn receipts retained in this page instance or restored by an exact Safe-refresh ticket',
    };
  }
  function handoffIncidentIndex({ faults, barrier, authenticity, model, turns, controls, probeFailures, pipelineSurfaces }) {
    const current = [];
    const recent = [];
    if (state.terminalStop || barrier?.present) current.push({ id: 'current:terminal', type: 'conversation-terminal', severity: 'info', status: 'complete', summary: state.terminalStop?.text || barrier?.current?.text || 'terminal conversation boundary', evidenceRefs: ['/wake/terminal','/conversationBarrier'] });
    if (state.quarantine || authenticity?.hard) current.push({ id: 'current:quarantine', type: 'surface-quarantine', severity: 'error', status: state.quarantine ? 'active' : 'detected', summary: state.quarantine?.kind || authenticity?.reason || 'hard false-GUI evidence', evidenceRefs: ['/wake/quarantine','/authenticity'] });
    if (faults?.current) current.push({ id: `current:fault:${faults.current.signature || faults.current.faultKind || 'unknown'}`, type: 'pipeline-fault', severity: 'error', status: state.activeSend ? 'request-owned-or-evaluating' : 'unowned-or-historical', summary: `${faults.current.faultKind || faults.current.kind}: ${faults.current.text || ''}`, evidenceRefs: ['/faults/current'] });
    const shellHealth = state.shellHealth.current;
    if (shellHealth?.degraded) current.push({ id: `current:shell:${shellHealth.key}`, type: 'application-shell-degraded', severity: 'error', status: 'active', summary: `${shellHealth.kind}: ${shellHealth.reason}`, evidenceRefs: ['/runtime/shellHealth','/readMeFirst/currentSituation/pageShell/health', ...(shellHealth.domSnapshotId ? [`domish:${shellHealth.domSnapshotId}`] : [])] });
    if (state.phase === 'MODEL_HOLD') current.push({ id: 'current:model-hold', type: 'model-surface-hold', severity: 'warn', status: 'active', summary: state.phaseReason, evidenceRefs: ['/wake','/liveProbe/model','/runtime/modelGate'] });
    const preexistingAdvance = state.faultRecovery.preexistingAdvance;
    if (preexistingAdvance && !['committed','fault-cleared-before-next-turn'].includes(preexistingAdvance.status)) current.push({ id: `current:preexisting-failure:${preexistingAdvance.key}`, type: 'ordinary-next-turn-after-different-request-failure', severity: 'warn', status: preexistingAdvance.status, summary: `Different latest request failed with ${preexistingAdvance.faultKind}; qomrade is preserving it and preparing the configured prompt as an ordinary next turn.`, evidenceRefs: ['/runtime/faultRecovery/preexistingAdvance','/faults/current'] });
    if (state.autoRefresh.healingPending) current.push({ id: `current:healing:${state.autoRefresh.healingPending.key}`, type: 'stale-surface-healing', severity: 'warn', status: 'pending', summary: state.autoRefresh.healingPending.reason, evidenceRefs: ['/runtime/autoRefresh/healingPending', ...(state.autoRefresh.healingPending.domSnapshotId ? [`domish:${state.autoRefresh.healingPending.domSnapshotId}`] : [])] });
    if (state.activeSend) {
      const terminalReceipt = state.activeSend.outcome === 'conversation-complete';
      current.push({
        id: `current:turn:${state.activeSend.id}`,
        type: terminalReceipt ? 'terminal-request-receipt' : 'active-request-custody',
        severity: 'info',
        status: state.activeSend.outcome || 'pending',
        summary: terminalReceipt
          ? (state.terminalStop?.requestStage?.userTurnMaterialized
            ? `qomrade sent the exact prompt as real user turn ${state.terminalStop.requestStage.userTurnOrdinal ?? '?'} (${state.terminalStop.requestStage.userTurnId}); ChatGPT then returned the terminal conversation-length barrier before an assistant reply.`
            : 'qomrade encountered the terminal conversation-length barrier before a stable matching user turn materialized.')
          : `${state.activeSend.clickMode || 'request'} with user=${state.activeSend.userTurnId || 'unmaterialized'} assistant=${state.activeSend.assistantTurnId || 'unmaterialized'}`,
        evidenceRefs: ['/wake/activeTurn','/actions/active'],
      });
    }
    if (preexistingAdvance && ['committed','fault-cleared-before-next-turn'].includes(preexistingAdvance.status)) recent.push({ id: `preexisting-failure:${preexistingAdvance.key}`, type: 'ordinary-next-turn-after-different-request-failure', severity: 'info', at: preexistingAdvance.committedAt || preexistingAdvance.clearedAt || preexistingAdvance.lastObservedAt || null, summary: `${preexistingAdvance.faultKind}: ${preexistingAdvance.status}`, evidenceRefs: ['/runtime/faultRecovery/preexistingAdvance','/actions'] });
    for (const fault of state.faultIncidents.slice(-12)) recent.push({ id: `fault:${fault.id || fault.signature}`, type: 'fault-incident', severity: 'error', at: fault.lastObservedAt || fault.firstObservedAt || null, summary: `${fault.faultKind || fault.kind}: ${fault.text || ''}`, evidenceRefs: ['/runtime/faultIncidents', ...(fault.domSnapshotId ? [`domish:${fault.domSnapshotId}`] : [])] });
    for (const edge of pipelineSurfaces.edges.slice(-12)) recent.push({ id: `surface:${edge.key}`, type: 'pipeline-surface-edge', severity: edge.severity || 'warn', at: edge.at || null, summary: edge.literalTexts?.map(row => row.text).filter(Boolean).join(' | ') || 'visible pipeline surface changed', evidenceRefs: ['/pipelineSurfaces/edges', ...(edge.domSnapshotId ? [`domish:${edge.domSnapshotId}`] : [])] });
    for (const snapshot of state.domForensics.snapshots.slice(-8)) recent.push({ id: `domish:${snapshot.id}`, type: 'domish-snapshot', severity: snapshot.trigger?.severity || 'warn', at: snapshot.at, summary: snapshot.trigger?.reason || snapshot.trigger?.kind, evidenceRefs: [`/domForensics/snapshots/${Math.max(0, state.domForensics.snapshots.indexOf(snapshot))}`] });
    for (const error of state.pageErrors.slice(-8)) recent.push({ id: `page-error:${error.t || fnv1a64(JSON.stringify(error))}`, type: 'qomrade-page-error', severity: 'error', at: error.at || null, summary: `${error.kind || 'page-error'}: ${error.message || ''}`, evidenceRefs: ['/pageErrors'] });
    recent.sort((a, b) => (Date.parse(b.at || '') || 0) - (Date.parse(a.at || '') || 0));
    const incidents = [...current, ...recent.slice(0, 40)];
    return {
      schema: 'qomrade.incident-index.v1',
      incidents,
      current,
      recent: recent.slice(0, 40),
      counts: { current: current.length, recent: Math.min(recent.length, 40), faults: state.faultIncidents.length, shellHealthIncidents: state.shellHealth.incidents.length, pipelineSurfaceEdges: pipelineSurfaces.edges.length, pipelineSurfaceEdgesLive: pipelineSurfaces.liveCount, pipelineSurfaceEdgesRestoredFromDomish: pipelineSurfaces.restoredFromDomishCount, domishSnapshots: state.domForensics.snapshots.length, pageErrors: state.pageErrors.length, probeFailures: probeFailures.length },
      interpretation: 'mechanical index only; incident summaries point to evidence and do not claim backend causation',
    };
  }
  function handoffHeadlineFindings({ faults, barrier, authenticity, model, turns, retry, probeFailures, incidentIndex, pipelineSurfaces, terminalRetry }) {
    const findings = [];
    const add = (id, severity, statement, evidenceRefs) => findings.push({ id, severity, statement, evidenceRefs });
    if (barrier?.present || state.terminalStop) add('terminal-conversation', 'info', state.terminalStop?.requestStage?.userTurnMaterialized
      ? 'qomrade sent a real user turn and ChatGPT then returned the terminal length barrier before an assistant reply; the empty composer is expected and no duplicate Send is authorized.'
      : 'The conversation is at a terminal length boundary; qomrade should remain COMPLETE and send nothing further.', ['/conversationBarrier','/wake/terminal']);
    if (faults?.current) add('current-pipeline-fault', 'error', `A current ${faults.current.faultKind || faults.current.kind} is visible: ${faults.current.text || ''}`, ['/faults/current']);
    if (state.shellHealth.current?.degraded) add('degraded-shell', 'error', `${state.shellHealth.current.kind}: ${state.shellHealth.current.reason}`, ['/runtime/shellHealth','/readMeFirst/currentSituation/pageShell/health', ...(state.shellHealth.current.domSnapshotId ? [`domish:${state.shellHealth.current.domSnapshotId}`] : [])]);
    else if (state.running && (!findComposer() || !findModelButton() || !turns.length)) add('incomplete-shell-below-repair-threshold', 'warn', `The running page shell is incomplete but did not meet the high-confidence automatic-repair threshold: composer=${!!findComposer()}, model=${!!findModelButton()}, turns=${turns.length}.`, ['/liveProbe/health','/runtime/shellHealth']);
    if (retry?.available && !faults?.current && !terminalRetry && !state.shellHealth.current?.degraded) add('retry-without-classified-current-fault', 'warn', 'A visible Retry control exists without a classified current fault or terminal context. Consult the normalized pipeline-surface history and DOMish snapshot for literal wording and structure.', ['/governor/retry','/pipelineSurfaces/edges','/domForensics']);
    const latestEdge = pipelineSurfaces.edges[pipelineSurfaces.edges.length - 1];
    if (latestEdge && latestEdge.unknown) add('unclassified-pipeline-wording', 'warn', 'The newest pipeline surface contains literal wording not recognized as a generation fault or maintenance signal; the wording and DOMish scene are preserved as evidence only.', ['/pipelineSurfaces/edges', ...(latestEdge.domSnapshotId ? [`domish:${latestEdge.domSnapshotId}`] : [])]);
    if (latestEdge && latestEdge.maintenance) add('page-shell-maintenance-surface', 'warn', 'The newest pipeline surface is classified as page-shell maintenance rather than a generation fault. Safe refresh may heal it only under the explicit bounded maintenance policy.', ['/pipelineSurfaces/edges', ...(latestEdge.domSnapshotId ? [`domish:${latestEdge.domSnapshotId}`] : [])]);
    if (state.phase === 'MODEL_HOLD') add('model-hold', 'warn', `The controller is in MODEL_HOLD: ${state.phaseReason}`, ['/wake','/runtime/modelGate','/domForensics']);
    if (state.faultRecovery.preexistingAdvance && !['committed','fault-cleared-before-next-turn'].includes(state.faultRecovery.preexistingAdvance.status)) add('different-request-failure-next-turn', 'warn', 'A stable latest request different from the configured qomrade prompt failed. qomrade is preserving its output and will attempt the configured prompt as an ordinary cadence-bound next turn rather than holding forever.', ['/runtime/faultRecovery/preexistingAdvance','/faults/current']);
    if (state.autoRefresh.healingPending) add('healing-refresh-pending', 'warn', `A bounded stale-surface healing refresh is pending: ${state.autoRefresh.healingPending.reason}`, ['/runtime/autoRefresh']);
    if (authenticity?.hard) add('hard-surface-authenticity-failure', 'error', authenticity.reason || 'hard false-GUI signature', ['/authenticity']);
    if (probeFailures.length) add('probe-failures', 'warn', `${probeFailures.length} explicit handoff probe(s) failed; inspect /probeFailures before treating absent evidence as negative evidence.`, ['/probeFailures']);
    if (!findings.length) add('no-current-critical-anomaly', 'info', 'No current critical anomaly was mechanically identified. Recent incidents and the canonical timeline remain available for review.', ['/incidentIndex','/timeline']);
    return findings;
  }
  function buildHandoffOrientation({ generatedAt, model, faults, authenticity, barrier, turns, retry, controls, probeFailures, incidentIndex, headlineFindings }) {
    const active = state.activeSend;
    const activeRequestModel = active ? {
      transactionId: active.id || null, clickedAt: active.clickedAt || null, userTurnId: active.userTurnId || null, assistantTurnId: active.assistantTurnId || null, outcome: active.outcome || null,
      model: active.model ? { label: active.model.label || null, selectedLabel: active.model.selectedLabel || null, routeKey: active.model.routeKey || null, family: active.model.family ?? null, version: active.model.version || null, hasPro: active.model.hasPro == null ? null : !!active.model.hasPro, policy: active.model.policy || active.modelPreference || null, target: active.model.target || null } : null,
      modelCommit: active.modelCommit ? { ok: !!active.modelCommit.ok, reason: active.modelCommit.reason || null, evidenceSource: active.modelCommit.evidenceSource || null, at: active.modelCommit.at || null } : null,
      authority: 'send-local browser evidence for the active request; not backend model attestation',
    } : null;
    return {
      schema: 'qomrade.developer-handoff-orientation.v1',
      purpose: 'Self-contained qomrade engineering evidence for a fresh developer or sandperson. This is not the conversation Session Handoff and carries no automatic control authority.',
      amnesiaPrimer: {
        product: 'qomrade is a single-tab Tampermonkey userscript that repeatedly sends one exact operator prompt under strict model, draft, cancellation, recovery, and maintenance guards.',
        artifactBoundary: 'Developer Handoff explains qomrade and the current browser surface. Session Handoff separately exports only the observed user/assistant conversation transcript. Flight Recorder is a smaller qomrade first look.',
        stableKernel: ['exact prompt custody','operator-selected model policy with GPT-5.6-first Smart Pro default','fresh-message recovery for current typed failures','terminal conversation completion','automatic ZIP activation','optional bounded DOM trim','optional Safe refresh','single-tab isolation'],
        trustRule: 'Treat fields as browser-observed evidence. Do not infer backend state, other-tab state, or exactly-once execution from the UI.',
      },
      currentSituation: {
        generatedAt,
        conversationId: conversationIdFromPath(),
        pathname: location.pathname,
        running: state.running,
        paused: state.paused,
        phase: state.phase,
        phaseReason: state.phaseReason,
        activeTransactionId: state.activeSend?.id || null,
        terminal: state.terminalStop || null,
        quarantine: state.quarantine || null,
        model: { ok: !!model?.ok, label: model?.label || '', family: model?.family ?? null, reason: model?.reason || null, policy: activeModelPolicySnapshot(), preference: state.modelGate.runPreference || null, lastConfirmed: model?.lastConfirmed || null, activeRequest: activeRequestModel },
        operatorSettings: { gapMinutes: settings.gapMinutes, pauseWhenHidden: settings.pauseWhenHidden, automaticFiles: settings.autoZip, fileSuffixes: normalizeDownloadSuffixList(settings.downloadSuffixes, { fallback: true }).suffixes, fileSettleSeconds: normalizeFileDelaySeconds(settings.fileDelaySeconds), trimOldTurns: settings.trimOldTurns, safeRefresh: settings.hourlyRefresh, refreshMinutes: normalizeRefreshMinutes(settings.refreshMinutes), modelPolicy: modelPolicySnapshot(settings) },
        panel: panelViewportObservation(),
        sourceIdentity: { declared: QOMRADE_SOURCE_ID, pending: QOMRADE_SOURCE_ID === 'pending', version: QOMRADE_VERSION },
        pageShell: { readyState: document.readyState, composerPresent: !!pageShellFallbackComposer(), modelControlPresent: !!findModelButton(), materializedTurns: turns.length, retryAvailable: !!retry?.available, currentFault: faults?.current?.faultKind || null, health: shellHealthSummary() },
      },
      headlineFindings,
      readOrder: [
        { step: 1, path: '/readMeFirst', purpose: 'orientation, current situation, findings, unknowns, and trust boundaries' },
        { step: 2, path: '/incidentIndex', purpose: 'current and recent incidents with stable evidence references' },
        { step: 3, path: '/timeline', purpose: 'canonical chronological sequence across controller events, faults, surfaces, DOMish captures, and turn receipts' },
        { step: 4, path: '/domForensics', purpose: 'bounded DOMish scenes captured when odd events occurred' },
        { step: 5, path: '/faults and /pipelineSurfaces/edges', purpose: 'typed fault evidence and normalized live/restored pipeline-surface edges' },
        { step: 6, path: '/liveProbe, /governor, /actions, /persistence, /memoryPressure', purpose: 'current surface, controls, action custody, continuity, and bounded memory/lifecycle evidence' },
        { step: 7, path: '/document', purpose: 'durable qomrade office, decisions, lineage, and succession protocol' },
      ],
      pathIndex: {
        currentState: '/wake', runtime: '/runtime', shellHealth: '/runtime/shellHealth', currentFault: '/faults/current', historicalFaults: '/runtime/faultIncidents', pipelineSurfaces: '/pipelineSurfaces/edges', domishSnapshots: '/domForensics/snapshots', currentControls: '/liveProbe/controls', materializedTurns: '/conversation/turns', actions: '/actions', persistence: '/persistence', memoryPressure: '/memoryPressure', policies: '/constitution', developerMemory: '/document', omissions: '/manifest/omissions',
      },
      unknowns: [
        'Unmaterialized or virtualized ChatGPT turns may be absent.',
        'Network request bodies, stream bytes, and backend execution state are not observed.',
        'Other tabs are intentionally unknown.',
        'A visible error or Retry control does not prove that remote work terminated.',
      ],
      authority: 'read-only forensic orientation; no Send, Retry, reload, model, setting, or cross-tab authority',
    };
  }
  function handoffEvidenceCatalog({ turns, probeFailures, pipelineSurfaces }) {
    return {
      schema: 'qomrade.evidence-catalog.v1',
      pathIndex: {
        orientation: '/readMeFirst', incidents: '/incidentIndex/incidents', timeline: '/timeline/records',
        domish: '/domForensics/snapshots', shellHealth: '/runtime/shellHealth', faults: '/faults', pipelineSurfaces: '/pipelineSurfaces/edges',
        controls: '/liveProbe/controls', actions: '/actions', persistence: '/persistence', memoryPressure: '/memoryPressure', developerMemory: '/document',
      },
      records: [
        { id: 'domish', path: '/domForensics/snapshots', count: state.domForensics.snapshots.length, meaning: 'bounded structural scenes captured on odd-event edges' },
        { id: 'shell-health', path: '/runtime/shellHealth', count: state.shellHealth.incidents.length, meaning: 'exact conversation-load failure plus high-confidence missing-style or stalled-hydration shell observations and repair evidence' },
        { id: 'faults', path: '/faults', count: state.faultIncidents.length, meaning: 'typed current and historical pipeline-fault observations' },
        { id: 'surfaces', path: '/pipelineSurfaces/edges', count: pipelineSurfaces.edges.length, meaning: 'normalized literal Retry/system/error surface changes from live state and retained DOMish contexts' },
        { id: 'timeline', path: '/timeline/records', count: null, meaning: 'normalized cross-source chronology' },
        { id: 'turns', path: '/conversation/turns', count: turns.length, meaning: 'currently materialized logical turns, not the full Session Handoff transcript' },
        { id: 'events', path: '/events', count: state.events.length, meaning: 'raw bounded controller event ring' },
        { id: 'memory', path: '/memoryPressure', count: null, meaning: 'on-demand DOM, navigation, cumulative work, and serialized qomrade evidence-size proxy; not Firefox process heap' },
        { id: 'probes', path: '/probeFailures', count: probeFailures.length, meaning: 'explicit failures encountered while building this handoff' },
      ],
      referenceSyntax: { jsonPointer: '/path/to/field', stableEvidenceId: 'fault:<id> | surface:<key> | domish:<snapshot-id> | event:<seq> | turn:<receipt-id>' },
    };
  }
  function buildHandoffPayload() {
    return withReadSnapshot('buildHandoffPayload', () => {
    invalidateTurnCache('officer-handoff');
    const started = performance.now();
    state.metrics.handoffs += 1;
    const probeFailures = [];
    const page = safeProbe('page', pageObservation, probeFailures, { pathname: location.pathname, readyState: document.readyState });
    const modelRaw = safeProbe('model', currentModelObservation, probeFailures, { ok: false, reason: 'model probe failed', label: '', family: null, hasPro: false, element: null });
    const model = { ok: modelRaw.ok, directOk: modelRaw.directOk, reason: modelRaw.reason, label: modelRaw.label, family: modelRaw.family, version: modelRaw.version, hasPro: modelRaw.hasPro, transient: modelRaw.transient, evidenceSource: modelRaw.evidenceSource, lastConfirmed: modelRaw.lastConfirmed, gate: { ...state.modelGate, recentSurveys: state.modelGate.recentSurveys.slice(-MAX_MODEL_SURVEY_RECORDS) }, element: elementSummary(modelRaw.element) };
    const turns = safeProbe('conversation-turns', handoffTurns, probeFailures, []);
    const latest = safeProbe('latest-assistant', latestAssistantTurn, probeFailures, null);
    const faults = safeProbe('faults', () => observeVisibleFaults(latest, { origin: 'officer-handoff', includeHistory: true }), probeFailures, null);
    const authenticity = safeProbe('authenticity', surfaceAuthenticityObservation, probeFailures, null);
    const barrier = safeProbe('conversation-barrier', conversationBarrierObservation, probeFailures, null);
    const work = safeProbe('work-evidence', workEvidenceObservation, probeFailures, null);
    const dialogs = safeProbe('dialogs', visibleDialogObservation, probeFailures, null);
    const continuation = safeProbe('continuation', () => continuationObservation(latest), probeFailures, null);
    const retry = safeProbe('retry', () => retryObservation(latest), probeFailures, null);
    const redSignals = safeProbe('red-signals', redSignalObservation, probeFailures, null);
    const systemSurfaces = safeProbe('system-surfaces', systemSurfaceObservation, probeFailures, null);
    const controls = safeProbe('controls', currentControlsObservation, probeFailures, null);
    const outputs = safeProbe('outputs', () => outputObservation(latest), probeFailures, null);
    const resources = safeProbe('resource-timing', resourceTimingObservation, probeFailures, null);
    const semanticDom = safeProbe('semantic-dom', semanticDomObservation, probeFailures, null);
    const notifications = safeProbe('notification-environment', notificationEnvironmentObservation, probeFailures, null);
    const userscriptEnvironment = safeProbe('userscript-environment', userscriptEnvironmentObservation, probeFailures, null);
    const generatedAt = nowIso();
    const handoffShellHealth = safeProbe('page-shell-health', () => observePageShellHealth('developer-handoff', { capture: true }), probeFailures, null);
    const weakShell = !!handoffShellHealth?.degraded || (state.running && (!pageShellFallbackComposer() || !findModelButton() || turns.length === 0));
    const terminalRetry = retryContextBelongsToTerminal(retry, barrier);
    const terminalOnlySurface = terminalRetry && !faults?.current && !weakShell && redSignalsOnlyTerminal(redSignals, barrier);
    const strongCurrentSurface = !!faults?.current || weakShell || (!terminalOnlySurface && !!retry?.available);
    if (strongCurrentSurface) {
      captureDomishEvent('developer-handoff-current-surface', {
        reason: faults?.current ? `${faults.current.faultKind || faults.current.kind}: ${faults.current.text || ''}`
          : retry?.available ? 'visible Retry control at Developer Handoff time'
            : weakShell ? (handoffShellHealth?.reason || 'running ChatGPT shell is incomplete at Developer Handoff time')
              : 'visible red/error surface at Developer Handoff time',
        severity: faults?.current || weakShell ? 'error' : 'warn',
        origin: 'developer-handoff',
        primaryNodes: [faults?.current ? faultNodes.get(faults.current) : null].filter(Boolean),
        key: fnv1a64(JSON.stringify(['developer-handoff-current-surface', faults?.current?.faultKind || null, !!retry?.available, weakShell, state.phase])),
        context: { currentFault: faults?.current || null, retryAvailable: !!retry?.available, weakShell, shellHealth: publicPageShellHealthObservation(handoffShellHealth), redSignalCount: redSignals?.count || 0 },
      });
    }
    const runtime = runtimeSnapshot();
    const pipelineSurfaces = handoffPipelineSurfaceHistory();
    const incidentIndex = handoffIncidentIndex({ faults, barrier, authenticity, model, turns, controls, probeFailures, pipelineSurfaces });
    const headlineFindings = handoffHeadlineFindings({ faults, barrier, authenticity, model, turns, retry, probeFailures, incidentIndex, pipelineSurfaces, terminalRetry });
    const timeline = canonicalHandoffTimeline(pipelineSurfaces);
    const readMeFirst = buildHandoffOrientation({ generatedAt, model, faults, authenticity, barrier, turns, retry, controls, probeFailures, incidentIndex, headlineFindings });
    const evidenceCatalog = handoffEvidenceCatalog({ turns, probeFailures, pipelineSurfaces });
    const payload = {
      schema: QOMRADE_HANDOFF_SCHEMA,
      generatedAt,
      artifact: {
        schema: 'qomrade.developer-handoff-artifact.v1',
        kind: 'developer-forensic',
        structureVersion: 2,
        product: 'qomrade',
        version: QOMRADE_VERSION,
        sourceId: QOMRADE_SOURCE_ID,
        conversationId: conversationIdFromPath(),
        pathname: location.pathname,
        audience: 'fresh qomrade developer or sandperson, including one waking without prior conversation memory',
        previousSchema: 'qomrade.handoff.v1',
        compatibility: 'legacy section names remain present; qomrade tooling accepts both schemas',
      },
      readMeFirst,
      incidentIndex,
      timeline,
      evidenceCatalog,
      pipelineSurfaces,
      domForensics: domForensicsSummary(),
      generatedBy: {
        source: {
          product: 'qomrade',
          version: QOMRADE_VERSION,
          documentSchema: QOMRADE_DOCUMENT_SCHEMA,
          runtimeSchema: QOMRADE_RUNTIME_SCHEMA,
          handoffSchema: QOMRADE_HANDOFF_SCHEMA,
          sourceId: QOMRADE_SOURCE_ID,
          browserMode: 'single-tab-low-churn-forensic-on-demand',
          crossTabCoordination: false,
          dogfooderRuntime: false, legacyOfficerLoopRuntime: false,
      devDogfooderCapability: false,
        },
        userscriptEnvironment,
      },
      wake: {
        state: state.quarantine ? 'OFF' : state.paused ? 'PAUSED' : state.phase,
        stateReason: state.phaseReason,
        running: state.running,
        paused: state.paused,
        halt: state.lastError,
        terminal: state.terminalStop,
        observedPageFault: faults && faults.current || null,
        faultObservationMode: faults && faults.mode || 'unavailable',
        quarantine: state.quarantine,
        activeTurn: state.activeSend,
        startReceipt: state.startTransaction,
        latestReceipt: state.turnReceipts.length ? state.turnReceipts[state.turnReceipts.length - 1] : null,
        conversationId: conversationIdFromPath(),
        modelPill: model.label,
        effectiveNext: currentStatusText(),
        unknowns: [
          ...(model.ok || (model.lastConfirmed && model.lastConfirmed.ageMs <= MODEL_CONFIRMATION_MAX_AGE_MS) ? [] : [model.reason]),
          'Unmaterialized virtualized conversation turns are not visible to DOM-only qomrade.',
          'Other tabs are intentionally unknown because this runtime has no discovery or coordination API.',
          'Active network request and stream-byte truth are unavailable without page interposition or an observer.',
        ],
      },
      constitution: DOCUMENT_CONSTITUTION.map((statement, index) => ({ id: `single-tab-${index + 1}`, statement })),
      office: DOCUMENT_OFFICE,
      document: {
        schema: QOMRADE_DOCUMENT_SCHEMA,
        sourceId: QOMRADE_SOURCE_ID,
        sourceOfTruth: 'one complete qomrade.user.js',
        succession: SANDPERSON_PROTOCOL,
        heritage: DOCUMENT_HERITAGE,
        dialogue: DOCUMENT_DIALOGUE,
        boundedLineage: DOCUMENT_HISTORY,
        relationship: 'The office capsule, explicit heritage/scars, bounded dialogue, and lineage are the durable conversation between the operator and successive sandpeople. The browser handoff supplies measured current-tab evidence; the complete source carries accepted intent and revisions forward without silent self-adoption.',
      },
      operatorRequest: {
        classification: 'operator_request',
        exactPrompt: settings.prompt,
        promptHash: fnv1a64(settings.prompt),
        promptChars: settings.prompt.length,
        activeRunPromptHash: state.runPrompt ? fnv1a64(state.runPrompt) : null,
        activeRunPromptChars: state.runPrompt.length,
        note: 'Ordinary qomrade may send only the exact prompt captured when Start was pressed. This handoff is never sent automatically.',
      },
      page,
      runtime: runtimeSnapshot(),
      schedule: {
        running: state.running,
        paused: state.paused,
        phase: state.phase,
        at: state.nextSendAt || null,
        iso: state.nextSendAt ? new Date(state.nextSendAt).toISOString() : null,
        reason: state.phaseReason,
        controller: schedulerSnapshot(),
        nextRecovery: recoveryScheduleSnapshot(),
        atMeaning: 'ordinary prompt send-to-send floor; nextRecovery is a separate conditional recovery deadline',
      },
      boot: state.boot,
      persistence: {
        schema: 'qomrade.persistence-observability.v1',
        mode: 'bounded-current-tab-settings-plus-evidence-only-continuity',
        metrics: state.persistence,
        priorContinuity: state.priorContinuity,
        currentContinuity: continuitySnapshot('handoff-preview'),
        controlAuthority: false,
        controlAuthorityScope: 'ordinary continuity only; never a Send permit',
        recoveryTicket: recoverySnapshot().pendingTicket,
        recoveryTicketAuthority: 'separate one-shot source/conversation/prompt/request-bound observation ticket, consumed by verified read-back',
      },
      authenticity,
      conversationBarrier: barrier,
      redSignals,
      faults,
      work,
      governor: {
        dialogs,
        continuation,
        retry,
        systemSurfaces,
        policy: 'Observe structural controls; block where named; never click Retry, Continue, Stop, New chat, or dismiss dialogs.',
      },
      liveProbe: {
        at: generatedAt,
        conversation: { id: conversationIdFromPath(), pathname: location.pathname, href: location.href },
        health: { readyState: document.readyState, visibility: document.visibilityState, focused: document.hasFocus(), turnCount: turns.length, composer: !!findComposer(), generating: !!findStopButton() },
        thread: { count: turns.length, records: turns },
        model,
        controls,
        semanticDom,
      },
      conversation: {
        scope: 'all currently materialized logical turns; Session Handoff separately preserves the bounded observed ChatGPT transcript',
        visibleTurnCount: turns.length,
        turns,
        sessionArchive: { summary: sessionArchiveSummary(), note: 'the recorded conversation transcript is exported only by Session Handoff; no transcript is duplicated here' },
      },
      actions: actionReceiptSnapshot(),
      outputs,
      resourceTiming: resources,
      memoryPressure: memoryPressureObservation(),
      pageErrors: state.pageErrors.slice(-MAX_PAGE_ERROR_RECORDS),
      surfaceAdapter: {
        mode: modernSearchTurns().length ? 'virtualized-search-group' : 'classic-turn',
        selectors: SELECTORS,
        controls,
        semanticDomWeakEvidence: semanticDom && semanticDom.weakAdapterEvidence,
      },
      selfFootprint: {
        schema: 'qomrade.single-tab-footprint.v3',
        panelHostConnected: !!(ui.host && ui.host.isConnected),
        panelIsolation: ui.frame ? 'separate-same-origin-iframe-document' : null,
        panelFrameConnected: !!(ui.frame && ui.frame.isConnected),
        panelFocus: panelFocusObservation(),
        mutationObserverInstalled: false,
        persistentPageGlobalMutationObserverInstalled: false,
        boundedModelMenuMutationObserver: { operationScoped: true, activeOnlyDuringMenuWait: true, waits: state.modelGate.menuObserverWaits, resolutions: state.modelGate.menuObserverResolutions, timeouts: state.modelGate.menuObserverTimeouts, mutations: state.modelGate.menuObserverMutations },
        performanceObserverInstalled: false,
        pageErrorListenersInstalled: true,
        lifecycleListenersInstalled: true,
        pageGlobalsModified: false,
        pageNetworkApisModified: false,
        keepAwakeAudio: false,
        crossTabApis: false,
        crossTabListeners: false,
        dogfooderRuntime: false, legacyOfficerLoopRuntime: false,
      devDogfooderCapability: false,
        automaticRetry: false,
        automaticPromptResend: true,
        automaticReload: settings.hourlyRefresh && state.running,
        automaticReloadScope: 'operator-enabled interval refresh plus bounded stale/unowned pipeline-surface healing; never current owned fault recovery',
        domTrimming: settings.trimOldTurns && state.running,
        automaticRecoveryRunning: state.running && !state.paused,
        recoveryPolicy: recoverySnapshot().policy,
        faultObservationWhileStopped: 'operator-on-demand-only',
        automaticContinue: false,
        automaticDialogDismissal: false,
        handoffClipboardAvailable: typeof GM_setClipboard === 'function',
        sessionAndFlightFileDownloadAvailable: typeof Blob === 'function' && typeof URL !== 'undefined' && typeof URL.createObjectURL === 'function' && !!document.body,
        recurringTimerWhileStopped: !state.running && !!state.timer,
        timers: schedulerSnapshot(),
        metrics: { ...state.metrics },
        residualObservableSurfaces: [
          'one fixed host containing one local iframe document; panel UI events do not enter ChatGPT\'s document event path',
          'script-dispatched composer input, Send, optional ZIP clicks, opt-in old-turn removals, and opt-in hourly location reload remain observable; no trusted-event spoofing',
          'model and DOM reads consume bounded browser work on active ticks',
          'resource timing and semantic DOM inventories are read only when the operator explicitly builds a handoff or diagnostics',
          'Developer Handoff is copied explicitly to the clipboard; Session Handoff and Flight Recorder remain file downloads',
        ],
      },
      fleet: { mode: 'disabled-by-design', reports: [], note: 'No tab discovery, shared control key, listener, or coordination API exists in this runtime.' },
      notifications: notifications || { userscriptDesktopNotificationCapability: false },
      contradictions: [
        ...contradictionsObservation(authenticity, barrier, work, dialogs, continuation, model),
        ...(faults && faults.current && state.running ? [{ kind: 'current-page-fault-while-controller-running', severity: 'error', faultKind: faults.current.faultKind }] : []),
        ...(faults && faults.current && !state.running && !state.lastError ? [{ kind: 'page-fault-observed-on-demand-while-stopped', severity: 'info', note: 'Not a missed active-loop detection claim.' }] : []),
      ],
      events: state.events.slice(-MAX_EVENT_RECORDS),
      probeFailures,
      manifest: {
        schema: 'qomrade.developer-handoff-manifest.v1',
        maxUtf8Bytes: MAX_HANDOFF_UTF8_BYTES,
        structureVersion: 2,
        legacyPathsPreserved: true,
        sectionSchemas: {
          orientation: readMeFirst.schema,
          incidentIndex: incidentIndex.schema,
          timeline: timeline.schema,
          evidenceCatalog: evidenceCatalog.schema,
          domForensics: state.domForensics.schema,
          runtime: runtime.schema,
        },
        evidenceCounts: {
          incidentsCurrent: incidentIndex.current.length,
          incidentsRecent: incidentIndex.recent.length,
          timeline: timeline.records.length,
          domishSnapshots: state.domForensics.snapshots.length,
          pipelineSurfaceEdges: pipelineSurfaces.edges.length,
          pipelineSurfaceEdgesLive: pipelineSurfaces.liveCount,
          pipelineSurfaceEdgesRestoredFromDomish: pipelineSurfaces.restoredFromDomishCount,
          faultIncidents: state.faultIncidents.length,
          materializedTurns: turns.length,
          rawEvents: state.events.length,
        },
        omissions: [
          'cookies and ChatGPT origin local/session storage',
          'IndexedDB contents',
          'other tabs by design',
          'unmaterialized virtualized turns',
          'active request and stream-byte truth',
          'complete body HTML; bounded DOMish scenes are captured only on selected odd-event edges and explicit Developer Handoff inspection',
          'events that occurred before this qomrade page instance or after evidence was evicted by declared ring/byte limits',
        ],
        jsonBytes: 0,
        buildDurationMs: 0,
        complete: true,
        probeFailureCount: probeFailures.length,
      },
    };
    const serializeExact = () => {
      let json = '';
      for (let pass = 0; pass < 8; pass += 1) {
        json = JSON.stringify(payload, null, 2);
        const bytes = utf8Bytes(json);
        if (bytes === payload.manifest.jsonBytes) return json;
        payload.manifest.jsonBytes = bytes;
      }
      return JSON.stringify(payload, null, 2);
    };
    let json = serializeExact();
    while (utf8Bytes(json) > MAX_HANDOFF_UTF8_BYTES && payload.conversation.turns.length > 8) {
      payload.conversation.turns.shift();
      payload.liveProbe.thread.records = payload.conversation.turns;
      payload.liveProbe.thread.count = payload.conversation.turns.length;
      payload.conversation.visibleTurnCount = payload.conversation.turns.length;
      payload.manifest.omissions.push('oldest materialized turn omitted to respect the handoff byte cap');
      json = serializeExact();
    }
    if (utf8Bytes(json) > MAX_HANDOFF_UTF8_BYTES) {
      for (const turn of payload.conversation.turns) turn.text = trunc(turn.text, 16_000);
      payload.manifest.omissions.push('turn text further truncated to respect the handoff byte cap');
      json = serializeExact();
    }
    if (utf8Bytes(json) > MAX_HANDOFF_UTF8_BYTES && payload.domForensics?.snapshots?.length > 4) {
      payload.domForensics.snapshots = payload.domForensics.snapshots.slice(-4);
      payload.domForensics.snapshotCount = payload.domForensics.snapshots.length;
      payload.manifest.omissions.push('oldest DOMish snapshots omitted to respect the handoff byte cap');
      json = serializeExact();
    }
    if (utf8Bytes(json) > MAX_HANDOFF_UTF8_BYTES) {
      if (payload.resourceTiming && payload.resourceTiming.recent) payload.resourceTiming.recent = payload.resourceTiming.recent.slice(-20);
      if (payload.liveProbe && payload.liveProbe.semanticDom && payload.liveProbe.semanticDom.records) payload.liveProbe.semanticDom.records = payload.liveProbe.semanticDom.records.slice(0, 40);
      if (payload.governor && payload.governor.systemSurfaces && payload.governor.systemSurfaces.surfaces) payload.governor.systemSurfaces.surfaces = payload.governor.systemSurfaces.surfaces.slice(-20);
      if (payload.redSignals && payload.redSignals.signals) payload.redSignals.signals = payload.redSignals.signals.slice(-20);
      payload.manifest.omissions.push('large probe record arrays reduced to respect the handoff byte cap');
      json = serializeExact();
    }
    const duration = Math.max(0, performance.now() - started);
    state.metrics.handoffLastMs = Math.round(duration * 100) / 100;
    state.metrics.handoffMaxMs = Math.max(state.metrics.handoffMaxMs, state.metrics.handoffLastMs);
    payload.manifest.buildDurationMs = state.metrics.handoffLastMs;
    payload.manifest.probeFailureCount = probeFailures.length;
    payload.runtime.metrics = metricsSnapshot();
    payload.selfFootprint.metrics = metricsSnapshot();
    const overCapNote = 'handoff remained above the byte cap after all bounded reductions';
    for (let pass = 0; pass < 16; pass += 1) {
      json = JSON.stringify(payload, null, 2);
      const bytes = utf8Bytes(json);
      const complete = bytes <= MAX_HANDOFF_UTF8_BYTES;
      let changed = false;
      if (payload.manifest.jsonBytes !== bytes) {
        payload.manifest.jsonBytes = bytes;
        changed = true;
      }
      if (payload.manifest.complete !== complete) {
        payload.manifest.complete = complete;
        changed = true;
      }
      if (!complete && !payload.manifest.omissions.includes(overCapNote)) {
        payload.manifest.omissions.push(overCapNote);
        changed = true;
      }
      if (!changed) break;
    }
    json = JSON.stringify(payload, null, 2);
    return { payload, json };
    });
  }
  function buildOfficerHandoff() {
    const { payload, json } = buildHandoffPayload();
    const jsonBytes = utf8Bytes(json);
    const digest = fnv1a64(json);
    return [
      'QOMRADE-HANDOFF-BEGIN',
      'kind=developer-forensic',
      `schema=${QOMRADE_HANDOFF_SCHEMA}`,
      'format=amnesia-first-v2',
      'read_first=/readMeFirst',
      `domish_snapshots=${payload.domForensics?.snapshots?.length || 0}`,
      `version=${QOMRADE_VERSION}`,
      `source_id=${QOMRADE_SOURCE_ID}`,
      `generated_at=${payload.generatedAt}`,
      `json_bytes=${jsonBytes}`,
      `json_fnv1a64=${digest}`,
      '---JSON---',
      json,
      '---END-JSON---',
      'QOMRADE-HANDOFF-END',
      `complete=${payload.manifest.complete ? 'true' : 'false'}`,
    ].join('\n');
  }
  // @QOMRADE-CHUNK id=77.local-evidence title="Operator-only local evidence downloads"
  function safeTimestampForFilename(value = nowIso()) {
    return value.replace(/[:.]/g, '-');
  }
  const pendingTextDownloads = new Set();
  function downloadTextFile(filename, text) {
    if (pendingTextDownloads.size >= 4) throw new Error('four recent file downloads are still within their release grace period; no new download started');
    if (typeof Blob !== 'function' || typeof URL === 'undefined' || typeof URL.createObjectURL !== 'function' || !document.body) {
      throw new Error('local file download APIs are unavailable on this page');
    }
    const blob = new Blob([text], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    pendingTextDownloads.add(url);
    let anchor = null;
    try {
      anchor = document.createElement('a');
      anchor.href = url;
      anchor.download = filename;
      anchor.rel = 'noopener';
      anchor.style.display = 'none';
      document.body.append(anchor);
      anchor.click();
    } finally {
      if (anchor) anchor.remove();
      // A bounded grace period avoids revoking before a browser consumes the download.
      setTimeout(() => {
        try { URL.revokeObjectURL(url); } finally { pendingTextDownloads.delete(url); }
      }, 30_000);
    }
    return { filename, bytes: utf8Bytes(text), outcome: 'browser-download-requested', diskWriteVerified: false };
  }
  async function saveSessionHandoffFile() {
    try {
      logEvent('session-handoff-file-requested', 'Operator requested a transcript-only ChatGPT Session Handoff.');
      showMessage('Session Handoff: capturing available conversation content without moving the page…', false);
      await backfillSessionTranscript('session-handoff-export');
      const text = buildSessionHandoff();
      const conversation = conversationIdFromPath() || 'unknown-conversation';
      const receipt = downloadTextFile(`chatgpt-session-handoff-${conversation}-${safeTimestampForFilename()}.md`, text);
      state.metrics.sessionHandoffsSaved += 1;
      showMessage(`Session Handoff requested: ${receipt.filename} (${receipt.bytes.toLocaleString()} UTF-8 bytes).`, false);
      logEvent('session-handoff-file-saved', 'Browser download requested for the transcript-only Session Handoff; disk write is not observable.', receipt);
      persistContinuity('session-handoff-file-saved');
    } catch (error) {
      state.metrics.sessionHandoffErrors += 1;
      const record = { kind: 'session-handoff-file-error', message: String(error && error.message || error), stack: trunc(error && error.stack || '', 2_000) };
      recordPageError(record);
      showMessage(`Save Session Handoff failed: ${record.message}`, true);
      logEvent('session-handoff-file-failed', 'Save Session Handoff failed.', record);
    }
  }
  function saveFlightRecorderFile() {
    try {
      logEvent('flight-recorder-file-requested', 'Operator requested a compact qomrade Flight Recorder.');
      const text = buildFlightRecorder();
      const receipt = downloadTextFile(`qomrade-flight-recorder-${safeTimestampForFilename()}.json`, text);
      state.metrics.flightRecordersSaved += 1;
      showMessage(`Flight Recorder requested: ${receipt.filename} (${receipt.bytes.toLocaleString()} UTF-8 bytes).`, false);
      logEvent('flight-recorder-file-saved', 'Browser download requested for the compact Flight Recorder; disk write is not observable.', receipt);
      persistContinuity('flight-recorder-file-saved');
    } catch (error) {
      state.metrics.flightRecorderErrors += 1;
      const record = { kind: 'flight-recorder-file-error', message: String(error && error.message || error), stack: trunc(error && error.stack || '', 2_000) };
      recordPageError(record);
      showMessage(`Save Flight Recorder failed: ${record.message}`, true);
      logEvent('flight-recorder-file-failed', 'Save Flight Recorder failed.', record);
    }
  }
  async function copyTextToClipboard(text) {
    if (typeof GM_setClipboard === 'function') {
      const result = GM_setClipboard(text, 'text');
      if (result && typeof result.then === 'function') await result;
      return;
    }
    if (navigator.clipboard && navigator.clipboard.writeText) {
      await navigator.clipboard.writeText(text);
      return;
    }
    throw new Error('clipboard API unavailable');
  }
  async function copyOfficerHandoff() {
    try {
      logEvent('handoff-requested', 'Operator requested a forensic on-demand Developer Handoff.');
      const text = buildOfficerHandoff();
      await copyTextToClipboard(text);
      state.metrics.developerHandoffsCopied += 1;
      showMessage(`Copied Developer Handoff (${utf8Bytes(text).toLocaleString()} UTF-8 bytes) to the clipboard.`, false);
      logEvent('handoff-copied', 'Copied the forensic on-demand Developer Handoff.', { bytes: utf8Bytes(text), buildDurationMs: state.metrics.handoffLastMs });
      persistContinuity('handoff-copied');
    } catch (error) {
      state.metrics.developerHandoffCopyErrors += 1;
      recordPageError({ kind: 'handoff-copy-error', message: String(error && error.message || error), stack: trunc(error && error.stack, 2_000) });
      showMessage(`Copy Developer Handoff failed: ${error && error.message || error}`, true);
      logEvent('handoff-failed', 'Copy Developer Handoff failed.', { message: String(error && error.message || error) });
    }
  }
  function panelActiveElement() {
    try { return ui.panelDocument && ui.panelDocument.activeElement; }
    catch (_) { return null; }
  }
  function panelEditorFocused() {
    if (!ui.frame || document.activeElement !== ui.frame) return false;
    const active = panelActiveElement();
    if (!active || typeof active.matches !== 'function') return false;
    return active.matches('textarea, select, input[type="number"], input[type="text"], input:not([type]), [contenteditable="true"]');
  }
  function panelFocusObservation() {
    const active = panelActiveElement();
    return {
      schema: 'qomrade.panel-focus.v1',
      frameIsTopDocumentActiveElement: !!(ui.frame && document.activeElement === ui.frame),
      activeTag: active && active.tagName ? active.tagName.toLowerCase() : null,
      activeControl: active && active.getAttribute ? active.getAttribute('data-q') : null,
      editorFocused: panelEditorFocused(),
    };
  }
  function updatePanelViewport() {
    if (!ui.host || !ui.frame) return;
    const width = `min(${PANEL_WIDTH_PX}px, calc(100vw - 24px))`;
    const height = ui.collapsed
      ? `${PANEL_COLLAPSED_HEIGHT_PX}px`
      : `min(${PANEL_EXPANDED_MAX_HEIGHT_PX}px, calc(100vh - ${PANEL_VIEWPORT_TOP_RESERVE_PX}px))`;
    if (ui.host.style.width !== width) ui.host.style.width = width;
    if (ui.host.style.height !== height) ui.host.style.height = height;
  }
  function panelViewportObservation() {
    let rect = null;
    try {
      const box = ui.host && ui.host.getBoundingClientRect ? ui.host.getBoundingClientRect() : null;
      if (box) rect = { x: Math.round(box.x), y: Math.round(box.y), width: Math.round(box.width), height: Math.round(box.height), top: Math.round(box.top), bottom: Math.round(box.bottom) };
    } catch (_) {}
    return {
      schema: 'qomrade.panel-viewport.v1',
      anchor: 'bottom-right',
      collapsed: !!ui.collapsed,
      configured: { widthPx: PANEL_WIDTH_PX, expandedMaxHeightPx: PANEL_EXPANDED_MAX_HEIGHT_PX, viewportTopReservePx: PANEL_VIEWPORT_TOP_RESERVE_PX, collapsedHeightPx: PANEL_COLLAPSED_HEIGHT_PX },
      viewport: { width: window.innerWidth || 0, height: window.innerHeight || 0 },
      hostRect: rect,
      authority: 'observation only; the panel never moves itself away from the bottom-right anchor',
    };
  }
  function modelObservationForUi(force = false) {
    const cached = state.uiModelObservation;
    const active = panelActiveElement();
    const promptFocused = active === ui.refs.prompt;
    if (!force && cached && (promptFocused || Date.now() - cached.observedT < 5_000)) return cached;
    const observation = currentModelObservation();
    const policy = activeModelPolicySnapshot();
    let policyOk = observation.ok;
    let policyReason = observation.reason;
    if (policy.policy === MODEL_POLICY_FOLLOW) {
      policyOk = observation.present;
      policyReason = observation.present
        ? 'Follow mode will confirm the selected route and effort from the live menu before Send.'
        : 'The ChatGPT model selector is not currently visible.';
    } else if (policy.policy === MODEL_POLICY_PIN) {
      const confirmed = observation.lastConfirmed;
      const confirmedTarget = confirmed && confirmed.policy === MODEL_POLICY_PIN && confirmed.target
        && confirmed.target.key === policy.target.key && confirmed.ageMs <= MODEL_CONFIRMATION_MAX_AGE_MS;
      policyOk = !!confirmedTarget || observation.present;
      policyReason = confirmedTarget
        ? `Pinned route ${policy.target.label || policy.target.key} was confirmed for the current Send operation.`
        : observation.present
          ? `Pinned route ${policy.target.label || policy.target.key || 'not selected'} will be selected and confirmed before Send.`
          : 'The ChatGPT model selector is not currently visible.';
    }
    state.uiModelObservation = {
      observedAt: nowIso(),
      observedT: Date.now(),
      ok: policyOk,
      directOk: observation.ok,
      reason: policyReason,
      directReason: observation.reason,
      label: observation.label,
      family: observation.family,
      hasPro: observation.hasPro,
      present: observation.present,
      transient: observation.transient,
      policy,
      lastConfirmed: observation.lastConfirmed,
    };
    return state.uiModelObservation;
  }
  function formatModelConfirmation(confirmation) {
    if (!confirmation) return '';
    const base = confirmation.selectedLabel || confirmation.concreteLabel || confirmation.candidate || 'selected model';
    const effort = confirmation.effort && (confirmation.effort.valueText
      || MODEL_EFFORT_LABELS[confirmation.effort.policy]
      || confirmation.effort.attribute);
    const proSuffix = confirmation.hasPro && !modelLabelIndicatesPro(base) && !/\bpro\b/i.test(String(effort || '')) ? ' · Pro' : '';
    return `${base}${effort ? ` · ${effort}` : proSuffix}`;
  }
  function renderModelTargetOptions(select) {
    if (!select) return;
    const active = panelActiveElement();
    if (active === select) return;
    const catalogRows = Array.isArray(state.modelGate.catalog?.rows) ? state.modelGate.catalog.rows : [];
    const remembered = settings.modelTargetKey ? [{ label: settings.modelTargetLabel || settings.modelTargetKey, key: settings.modelTargetKey, disabled: false, remembered: true }] : [];
    const byKey = new Map();
    for (const row of [...remembered, ...catalogRows]) {
      if (!row || !row.key || byKey.has(row.key)) continue;
      byKey.set(row.key, row);
    }
    const rows = [...byKey.values()];
    select.replaceChildren();
    if (!rows.length) {
      const option = select.ownerDocument.createElement('option');
      option.value = '';
      option.textContent = 'Refresh choices to choose a model';
      select.append(option);
    } else {
      for (const row of rows) {
        const option = select.ownerDocument.createElement('option');
        option.value = row.key;
        option.textContent = `${row.label}${row.disabled ? ' · unavailable' : ''}${row.remembered && !catalogRows.some(item => item.key === row.key) ? ' · remembered' : ''}`;
        option.disabled = !!row.disabled;
        select.append(option);
      }
    }
    select.value = settings.modelTargetKey || '';
  }
  function render({ forceModel = false } = {}) {
    if (!ui.mounted) return;
    const refs = ui.refs;
    const status = currentStatusText();
    if (refs.status) {
      refs.status.textContent = status;
      refs.status.dataset.bad = state.quarantine || state.phase === 'HALTED' || state.phase === 'OFF' ? 'true' : 'false';
    }
    recordBackgroundEdge('panel-render');
    if (refs.counts) {
      const lastTick = state.metrics.ticks ? `${state.metrics.tickLastMs}ms/${state.metrics.tickLastQueries}q` : 'none';
      const refreshText = settings.hourlyRefresh && state.autoRefresh.dueAt ? `refresh ${settings.refreshMinutes}m/${formatDuration(state.autoRefresh.dueAt - Date.now())}` : 'refresh off';
      refs.counts.textContent = `sends ${state.sends} · replies ${state.completedReplies} · model surveys ${state.modelGate.surveys}/${state.modelGate.selections} selections · file requests ${state.zipClicks}/${state.zipActivationErrors} errors · trim ${state.domTrim.logicalTurnsRemoved} turns · ${refreshText} · ${pauseForHidden() ? 'Hidden pause on' : 'Background on'} (${state.background.hiddenTicks} hidden ticks) · late timers ${state.scheduler.lateCount} · last tick ${lastTick}`;
    }
    if (refs.model) {
      const observation = modelObservationForUi(forceModel);
      const confirmation = observation.lastConfirmed;
      const confirmationText = confirmation && confirmation.ageMs <= MODEL_CONFIRMATION_MAX_AGE_MS
        ? formatModelConfirmation(confirmation)
        : null;
      const shell = state.shellHealth.current;
      refs.model.textContent = shell?.degraded
        ? `page shell degraded · ${shell.kind}`
        : observation.ok
          ? (observation.label || observation.reason)
          : confirmationText
            ? `${observation.label || 'effort-only'} · last confirmed ${confirmationText}`
            : (observation.label || observation.reason);
      refs.model.dataset.ok = shell?.degraded ? 'false' : observation.ok || !!confirmationText ? 'true' : 'false';
      refs.model.title = shell?.degraded
        ? `${shell.reason} · ${shell.key}`
        : `${observation.reason} · ${modelPolicySummary()} · observed ${observation.observedAt}`;
    }
    if (refs.modelPolicy && panelActiveElement() !== refs.modelPolicy) refs.modelPolicy.value = settings.modelPolicy;
    renderModelTargetOptions(refs.modelTarget);
    if (refs.modelEffort && panelActiveElement() !== refs.modelEffort) refs.modelEffort.value = settings.modelTargetEffort;
    const pinned = settings.modelPolicy === MODEL_POLICY_PIN;
    if (refs.modelPinControls) refs.modelPinControls.hidden = !pinned;
    if (refs.modelTarget) refs.modelTarget.disabled = !pinned || state.modelGate.catalogBusy;
    if (refs.modelEffort) refs.modelEffort.disabled = !pinned || state.modelGate.catalogBusy;
    if (refs.modelRefresh) {
      refs.modelRefresh.disabled = state.modelGate.catalogBusy || (state.running && !state.paused);
      refs.modelRefresh.textContent = state.modelGate.catalogBusy ? 'Reading choices…' : 'Refresh choices';
    }
    if (refs.modelNote) {
      const catalogAt = state.modelGate.catalog?.observedAt ? ` Choices observed ${new Date(state.modelGate.catalog.observedAt).toLocaleTimeString()}.` : '';
      const error = state.modelGate.catalogError ? ` Last refresh failed: ${state.modelGate.catalogError}` : '';
      const shellNotice = state.shellHealth.current?.degraded ? ` ${state.shellHealth.current.reason} ${settings.hourlyRefresh ? 'Start will repair the page before any Send.' : 'Reload manually or enable Safe refresh.'}` : '';
      refs.modelNote.textContent = (settings.modelPolicy === MODEL_POLICY_SMART_PRO
        ? `Recommended default. qomrade selects GPT-5.6 Pro, then uses GPT-6 Pro only for the unresolved fallback lineage until success.${catalogAt}${error}`
        : settings.modelPolicy === MODEL_POLICY_PIN
          ? `No fallback. qomrade confirms the exact chosen route and effort before every Send.${catalogAt}${error}`
          : `qomrade does not change model or effort. It opens the live menu only to witness the current ChatGPT choice before every Send.${catalogAt}${error}`) + shellNotice;
    }
    const restorePending = state.autoRefresh.restorePending || state.autoRefresh.restoreInFlight || ['not-started', 'in-flight'].includes(state.boot.tabRead.status);
    if (refs.start) {
      refs.start.disabled = restorePending || state.running || !!state.quarantine || !normalizePromptLineEndings(settings.prompt)
        || (settings.modelPolicy === MODEL_POLICY_PIN && !settings.modelTargetKey);
      refs.start.textContent = state.shellHealth.current?.degraded ? 'Repair & Start' : 'Start';
    }
    if (refs.stop) refs.stop.disabled = !state.running;
    if (refs.pause) {
      refs.pause.disabled = !state.running;
      refs.pause.textContent = state.paused ? 'Resume' : 'Pause';
    }
    const panelActive = panelActiveElement();
    if (refs.prompt) {
      refs.prompt.disabled = restorePending;
      if (panelActive !== refs.prompt && refs.prompt.value !== settings.prompt) refs.prompt.value = settings.prompt;
    }
    if (refs.gap && panelActive !== refs.gap) refs.gap.value = String(settings.gapMinutes);
    if (refs.pauseHidden) refs.pauseHidden.checked = settings.pauseWhenHidden;
    if (refs.autoZip) refs.autoZip.checked = settings.autoZip;
    if (refs.downloadSuffixes && panelActiveElement() !== refs.downloadSuffixes) refs.downloadSuffixes.value = normalizeDownloadSuffixList(settings.downloadSuffixes, { fallback: true }).text;
    if (refs.fileDelaySeconds && panelActiveElement() !== refs.fileDelaySeconds) refs.fileDelaySeconds.value = String(normalizeFileDelaySeconds(settings.fileDelaySeconds));
    if (refs.trimOldTurns) refs.trimOldTurns.checked = settings.trimOldTurns;
    if (refs.hourlyRefresh) refs.hourlyRefresh.checked = settings.hourlyRefresh;
    if (refs.refreshMinutes && panelActive !== refs.refreshMinutes) refs.refreshMinutes.value = String(settings.refreshMinutes);
    if (refs.refreshMinutes) refs.refreshMinutes.disabled = !settings.hourlyRefresh;
    if (refs.maintenanceAdvice) {
      const advice = maintenanceRecommendation();
      refs.maintenanceAdvice.textContent = `Recommendation: ${advice.refreshMinutes}m (${advice.confidence}) · ${advice.reason} · trim ${advice.trim.replace('-', ' ')}`;
      refs.maintenanceAdvice.title = JSON.stringify(advice.evidence);
    }
    if (refs.lock) {
      refs.lock.textContent = restorePending
        ? "Restoring this tab's bounded settings; prompt editing and Start are temporarily disabled."
        : state.quarantine
          ? 'All ChatGPT effects are revoked for this tab. Copy a Developer Handoff or copy diagnostics for evidence.'
          : state.running
            ? `Current run prompt locked: ${state.runPrompt.length} chars · ${fnv1a32(state.runPrompt)}`
            : 'Prompt will be captured when Start is pressed. Session Handoff exports the ChatGPT transcript; Developer Handoff diagnoses qomrade.';
    }
    updatePanelViewport();
  }
  // @QOMRADE-CHUNK id=80.ui title="Event-isolated operator panel and menu controls"
  function buildPanelDocument(panelDocument) {
    if (!panelDocument || !panelDocument.documentElement || !panelDocument.head || !panelDocument.body) {
      throw new Error('iframe document skeleton was unavailable');
    }
    const make = (tag, className = '', textContent = '') => {
      const element = panelDocument.createElement(tag);
      if (className) element.className = className;
      if (textContent) element.textContent = textContent;
      return element;
    };
    const control = (tag, key, textContent = '') => {
      const element = make(tag, '', textContent);
      element.setAttribute('data-q', key);
      return element;
    };
    const row = () => make('div', 'row');
    const small = textContent => make('div', 'small', textContent);
    const checkboxLabel = (key, labelText) => {
      const label = make('label');
      const input = control('input', key);
      input.type = 'checkbox';
      label.append(input, panelDocument.createTextNode(` ${labelText}`));
      return label;
    };
    panelDocument.documentElement.lang = 'en';
    panelDocument.documentElement.setAttribute('data-qomrade-panel-document', '');
    const charset = panelDocument.createElement('meta');
    charset.setAttribute('charset', 'utf-8');
    const colorScheme = panelDocument.createElement('meta');
    colorScheme.name = 'color-scheme';
    colorScheme.content = 'dark';
    const title = make('title', '', 'qomrade');
    const style = make('style');
    style.textContent = `
      :root { color-scheme: dark; }
      html, body { width:100%; height:100%; margin:0; padding:0; overflow:hidden; background:transparent; }
      * { box-sizing: border-box; }
      .panel { width:100%; height:100%; display:flex; flex-direction:column; color:#f4f4f5; background:rgba(24,24,27,.96); border:1px solid #52525b; border-radius:12px; box-shadow:0 14px 40px rgba(0,0,0,.38); font:13px/1.35 system-ui,sans-serif; overflow:hidden; }
      .head { flex:0 0 auto; display:flex; align-items:center; justify-content:space-between; gap:8px; padding:9px 10px; border-bottom:1px solid #3f3f46; }
      .title { font-weight:700; }
      .sub { color:#a1a1aa; font-size:11px; }
      .body { flex:1 1 auto; min-height:0; padding:10px; display:grid; align-content:start; gap:8px; overflow:auto; }
      .collapsed .body { display:none; }
      textarea, input[type="number"], input[type="text"] { width:100%; color:#fafafa; background:#09090b; border:1px solid #52525b; border-radius:7px; padding:7px; font:inherit; }
      textarea { min-height:92px; resize:vertical; white-space:pre-wrap; }
      .row { display:flex; gap:7px; align-items:center; }
      .row > * { flex:1; }
      .section { display:grid; gap:7px; padding:8px; border:1px solid #3f3f46; border-radius:9px; background:rgba(9,9,11,.34); }
      .section-title { color:#d4d4d8; font-size:11px; font-weight:700; letter-spacing:.04em; text-transform:uppercase; }
      .evidence-grid { display:grid; grid-template-columns:1fr 1fr; gap:7px; }
      .evidence-grid button { min-height:42px; }
      .transcript { background:#1e3a5f; border-color:#60a5fa; }
      select { width:100%; color:#fafafa; background:#09090b; border:1px solid #52525b; border-radius:7px; padding:7px; font:inherit; }
      .advice { color:#bfdbfe; font-size:11px; border-left:2px solid #60a5fa; padding-left:7px; }
      button { color:#fafafa; background:#3f3f46; border:1px solid #71717a; border-radius:7px; padding:7px 9px; font:inherit; cursor:pointer; }
      button:hover:not(:disabled) { background:#52525b; }
      button:disabled { opacity:.45; cursor:default; }
      .start { background:#14532d; border-color:#22c55e; }
      .stop { background:#7f1d1d; border-color:#ef4444; }
      .status { padding:7px; border-radius:7px; background:#18181b; border:1px solid #3f3f46; word-break:break-word; }
      .status[data-bad="true"] { color:#fecaca; border-color:#991b1b; background:#450a0a; }
      .model[data-ok="true"] { color:#86efac; }
      .model[data-ok="false"] { color:#fca5a5; }
      .model-card { display:grid; gap:7px; }
      .model-target-grid { display:grid; grid-template-columns:minmax(0,1fr) minmax(0,.8fr); gap:7px; }
      .model-target-grid[hidden] { display:none; }
      .model-actions { display:grid; grid-template-columns:1fr auto; gap:7px; align-items:center; }
      .model-note { color:#c4b5fd; font-size:11px; border-left:2px solid #8b5cf6; padding-left:7px; }
      .small { color:#a1a1aa; font-size:11px; }
      .message { min-height:16px; color:#a7f3d0; }
      .message[data-bad="true"] { color:#fca5a5; }
      .checks { display:grid; gap:5px; }
      label { display:flex; align-items:center; gap:6px; }
      label input[type="checkbox"] { flex:0 0 auto; }
      .collapse { flex:0 0 auto; padding:4px 7px; }
    `;
    panelDocument.head.replaceChildren(charset, colorScheme, title, style);
    const panel = make('section', 'panel');
    panel.setAttribute('data-q-panel', '');
    const head = make('div', 'head');
    const heading = make('div');
    heading.append(
      make('div', 'title', `qomrade ${VERSION}`),
      make('div', 'sub', 'run · resilience · transcript · no fleet'),
    );
    const collapse = control('button', 'collapse', '−');
    collapse.type = 'button';
    collapse.className = 'collapse';
    collapse.title = 'Collapse qomrade';
    head.append(heading, collapse);
    const body = make('div', 'body');
    const status = control('div', 'status');
    status.className = 'status';
    const modelSection = make('div', 'section model-card');
    modelSection.append(make('div', 'section-title', 'Model'));
    const modelLine = small('Visible model: ');
    const model = control('span', 'model');
    model.className = 'model';
    modelLine.append(model);
    const policyLabel = make('label');
    policyLabel.append(panelDocument.createTextNode('Policy '));
    const modelPolicy = control('select', 'model-policy');
    for (const [value, label] of [
      [MODEL_POLICY_SMART_PRO, 'Smart Pro · 5.6 first · 6 until success'],
      [MODEL_POLICY_PIN, 'Pin exact model & effort'],
      [MODEL_POLICY_FOLLOW, 'Follow ChatGPT selection · any tier'],
    ]) {
      const option = make('option', '', label);
      option.value = value;
      modelPolicy.append(option);
    }
    policyLabel.append(modelPolicy);
    const pinControls = control('div', 'model-pin-controls');
    pinControls.className = 'model-target-grid';
    const targetLabel = make('label');
    targetLabel.append(panelDocument.createTextNode('Model '));
    const modelTarget = control('select', 'model-target');
    targetLabel.append(modelTarget);
    const effortLabel = make('label');
    effortLabel.append(panelDocument.createTextNode('Effort '));
    const modelEffort = control('select', 'model-effort');
    for (const value of MODEL_EFFORT_VALUES) {
      const option = make('option', '', MODEL_EFFORT_LABELS[value]);
      option.value = value;
      modelEffort.append(option);
    }
    effortLabel.append(modelEffort);
    pinControls.append(targetLabel, effortLabel);
    const modelActions = make('div', 'model-actions');
    const modelNote = control('div', 'model-note');
    modelNote.className = 'model-note';
    const modelRefresh = control('button', 'model-refresh', 'Refresh choices');
    modelRefresh.type = 'button';
    modelRefresh.title = 'Pause or stop qomrade, then inspect the live ChatGPT model menu and refresh the exact route list.';
    modelActions.append(modelNote, modelRefresh);
    modelSection.append(modelLine, policyLabel, pinControls, modelActions);
    const runSection = make('div', 'section');
    runSection.append(make('div', 'section-title', 'Run'));
    const prompt = control('textarea', 'prompt');
    prompt.maxLength = MAX_PROMPT_CHARS;
    prompt.spellcheck = false;
    prompt.placeholder = 'One exact prompt';
    const lock = control('div', 'lock');
    lock.className = 'small';
    const runRow = row();
    const start = control('button', 'start', 'Start');
    start.type = 'button';
    start.className = 'start';
    const pause = control('button', 'pause', 'Pause');
    pause.type = 'button';
    const stop = control('button', 'stop', 'Stop');
    stop.type = 'button';
    stop.className = 'stop';
    runRow.append(start, pause, stop);
    const gapRow = row();
    const gapLabel = make('label');
    gapLabel.append(panelDocument.createTextNode('Gap minutes '));
    const gap = control('input', 'gap');
    gap.type = 'number'; gap.min = '1'; gap.max = '1440'; gap.step = '1';
    gapLabel.append(gap);
    gapRow.append(gapLabel);
    runSection.append(prompt, lock, runRow, gapRow);
    const reliabilitySection = make('div', 'section');
    reliabilitySection.append(make('div', 'section-title', 'Reliability'));
    const checks = make('div', 'checks');
    checks.append(
      checkboxLabel('pause-hidden', 'Pause work while this tab is hidden'),
      checkboxLabel('auto-zip', 'Automatically request matching files after completed replies'),
      checkboxLabel('trim-old-turns', 'Trim old rendered turns (keep newest 4; refresh restores)'),
      checkboxLabel('hourly-refresh', 'Safe refresh: interval + stale pipeline or degraded-shell repair'),
    );
    const suffixLabel = make('label');
    suffixLabel.append(panelDocument.createTextNode('File suffixes '));
    const downloadSuffixes = control('input', 'download-suffixes');
    downloadSuffixes.type = 'text';
    downloadSuffixes.maxLength = MAX_DOWNLOAD_SUFFIX_CHARS;
    downloadSuffixes.placeholder = '.zip, .tar.gz, .json';
    downloadSuffixes.title = 'Comma-separated filename suffixes. qomrade activates only explicitly named native download controls. The default is .zip.';
    suffixLabel.append(downloadSuffixes);
    const suffixNote = small('Comma-separated suffixes; .zip is the default. Matching is case-insensitive and supports compound suffixes such as .tar.gz.');
    const fileDelayRow = row();
    const fileDelayLabel = make('label');
    fileDelayLabel.append(panelDocument.createTextNode('File settle seconds '));
    const fileDelaySeconds = control('input', 'file-delay-seconds');
    fileDelaySeconds.type = 'number'; fileDelaySeconds.min = '0'; fileDelaySeconds.max = String(FILE_SETTLE_MAX_SECONDS); fileDelaySeconds.step = '1';
    fileDelaySeconds.title = 'Wait this long after a generated file control first appears before activating it. A bounded page-notification watch records download failures.';
    fileDelayLabel.append(fileDelaySeconds); fileDelayRow.append(fileDelayLabel);
    const refreshRow = row();
    const refreshLabel = make('label');
    refreshLabel.append(panelDocument.createTextNode('Refresh interval '));
    const refreshMinutes = control('input', 'refresh-minutes');
    refreshMinutes.type = 'number';
    refreshMinutes.min = String(AUTO_REFRESH_MIN_MINUTES);
    refreshMinutes.max = String(AUTO_REFRESH_MAX_MINUTES);
    refreshMinutes.step = '1';
    refreshMinutes.inputMode = 'numeric';
    refreshMinutes.title = `Exact per-tab Safe-refresh interval from ${AUTO_REFRESH_MIN_MINUTES} through ${AUTO_REFRESH_MAX_MINUTES} minutes.`;
    refreshLabel.append(refreshMinutes);
    refreshRow.append(refreshLabel);
    const maintenanceAdvice = control('div', 'maintenance-advice');
    maintenanceAdvice.className = 'advice';
    reliabilitySection.append(checks, suffixLabel, suffixNote, fileDelayRow, refreshRow, maintenanceAdvice);
    const conversationSection = make('div', 'section');
    conversationSection.append(make('div', 'section-title', 'Conversation'));
    const sessionButton = control('button', 'session-handoff', 'Session Handoff');
    sessionButton.type = 'button';
    sessionButton.className = 'transcript';
    sessionButton.title = 'Save the captured user and assistant conversation plus visible file/image-card names without scrolling the page. No qomrade diagnostics or authored brief.';
    conversationSection.append(sessionButton, small('Transcript only: captured ChatGPT conversation in order, with visible context-item names. Export does not scroll the page.'));
    const evidenceSection = make('div', 'section');
    evidenceSection.append(make('div', 'section-title', 'qomrade evidence'));
    const evidenceGrid = make('div', 'evidence-grid');
    for (const [key, label, titleText] of [
      ['developer-handoff', 'Copy Developer Handoff', 'Copy full forensic qomrade state to the clipboard for development and debugging.'],
      ['flight-recorder', 'Flight Recorder', 'Save compact qomrade state transitions, actions, recoveries, models, file downloads, and maintenance evidence.'],
      ['diagnostics', 'Copy Diagnostics', 'Copy a bounded current-tab qomrade diagnostic snapshot.'],
    ]) {
      const button = control('button', key, label);
      button.type = 'button';
      button.title = titleText;
      evidenceGrid.append(button);
    }
    evidenceSection.append(evidenceGrid, small('Developer Handoff = full qomrade internals copied to clipboard · Flight Recorder = compact saved first look · Diagnostics = compact clipboard snapshot'));
    const counts = control('div', 'counts');
    counts.className = 'small';
    const message = control('div', 'message');
    message.className = 'message';
    body.append(status, modelSection, runSection, reliabilitySection, conversationSection, evidenceSection, counts, message);
    panel.append(head, body);
    panelDocument.body.replaceChildren(panel);
  }
  function mountPanelFailureNotice(host, error, stage = 'panel mount') {
    const message = trunc(error && error.message || error || 'unknown panel mount failure', 700);
    state.boot.panelMountStatus = 'failed';
    state.boot.panelMountError = { at: nowIso(), stage, message };
    recordPageError({ kind: 'panel-mount-error', stage, message, stack: trunc(error && error.stack || '', 2_000) });
    host.replaceChildren();
    host.setAttribute('data-qomrade-panel-state', 'failed');
    host.style.position = 'fixed';
    host.style.right = '12px';
    host.style.bottom = '12px';
    host.style.zIndex = '2147483646';
    host.style.pointerEvents = 'auto';
    host.style.contain = 'layout style paint';
    host.style.width = 'min(420px, calc(100vw - 24px))';
    host.style.height = 'auto';
    const notice = document.createElement('div');
    notice.style.cssText = 'color:#fecaca;background:rgba(69,10,10,.97);border:1px solid #ef4444;border-radius:10px;padding:10px;box-shadow:0 14px 40px rgba(0,0,0,.38);font:13px/1.4 system-ui,sans-serif;white-space:pre-wrap;word-break:break-word;';
    const heading = document.createElement('strong');
    heading.textContent = `qomrade ${VERSION} panel failed to mount`;
    const detail = document.createElement('div');
    detail.style.marginTop = '6px';
    detail.textContent = `${stage}: ${message}`;
    const fallback = document.createElement('div');
    fallback.style.cssText = 'margin-top:6px;color:#fda4af;font-size:11px;';
    fallback.textContent = state.boot.menusRegistered
      ? 'Automation remains stopped. Tampermonkey menu commands were registered first; use Save Session Handoff for the ChatGPT transcript, or Copy Developer Handoff, Save Flight Recorder, or Copy compact diagnostics for qomrade evidence from that menu.'
      : 'Automation remains stopped. No Tampermonkey menu fallback was registered; reinstall the userscript and reload the tab.';
    notice.append(heading, detail, fallback);
    host.append(notice);
    ui.host = host;
    ui.frame = null;
    ui.panelDocument = null;
    ui.refs = Object.create(null);
    ui.mounted = false;
  }
  function mountUi() {
    if (ui.mounted || !document.body || !isEligibleRoute()) return;
    const host = document.createElement('div');
    host.id = 'qomrade-single-tab-host';
    host.setAttribute('data-qomrade-panel-state', 'starting');
    host.style.position = 'fixed';
    host.style.right = '12px';
    host.style.bottom = '12px';
    host.style.zIndex = '2147483646';
    host.style.pointerEvents = 'auto';
    host.style.contain = 'layout style paint';
    const frame = document.createElement('iframe');
    frame.id = 'qomrade-panel-frame';
    frame.title = 'qomrade operator panel';
    frame.setAttribute('aria-label', 'qomrade operator panel');
    frame.setAttribute('data-qomrade-panel-frame', '');
    frame.setAttribute('referrerpolicy', 'no-referrer');
    frame.style.display = 'block';
    frame.style.width = '100%';
    frame.style.height = '100%';
    frame.style.border = '0';
    frame.style.background = 'transparent';
    frame.style.colorScheme = 'dark';
    host.append(frame);
    document.body.append(host);
    ui.host = host;
    ui.frame = frame;
    state.boot.panelMountStatus = 'building';
    try {
      const panelDocument = frame.contentDocument;
      if (!panelDocument) throw new Error('iframe contentDocument was unavailable');
      buildPanelDocument(panelDocument);
      ui.panelDocument = panelDocument;
      updatePanelViewport();
      for (const key of ['panel', 'status', 'model', 'model-policy', 'model-pin-controls', 'model-target', 'model-effort', 'model-refresh', 'model-note', 'prompt', 'lock', 'start', 'pause', 'stop', 'gap', 'pause-hidden', 'auto-zip', 'download-suffixes', 'file-delay-seconds', 'trim-old-turns', 'hourly-refresh', 'refresh-minutes', 'maintenance-advice', 'session-handoff', 'developer-handoff', 'flight-recorder', 'diagnostics', 'counts', 'message', 'collapse']) {
        ui.refs[key.replace(/-([a-z])/g, (_, char) => char.toUpperCase())] = panelDocument.querySelector(`[data-q="${key}"]`) || panelDocument.querySelector(`[data-q-${key}]`);
      }
      ui.refs.panel = panelDocument.querySelector('[data-q-panel]');
      const missing = Object.entries(ui.refs).filter(([, element]) => !element).map(([key]) => key);
      if (missing.length) throw new Error(`panel controls missing after direct DOM construction: ${missing.join(', ')}`);
      if (TEST_MODE) {
        host.setAttribute('data-qomrade-fixture-host', '');
        host.__qomradePanelDocumentForFixture = panelDocument;
        host.__qomradeFrameForFixture = frame;
      }
      ui.refs.prompt.addEventListener('input', () => {
        settings.prompt = trunc(normalizePromptLineEndings(ui.refs.prompt.value), MAX_PROMPT_CHARS);
        debounceSaveSettings();
        render();
      });
      ui.refs.gap.addEventListener('change', () => {
        settings.gapMinutes = clamp(ui.refs.gap.value, 1, 1_440);
        debounceSaveSettings();
        render();
      });
      ui.refs.pauseHidden.addEventListener('change', () => {
        settings.pauseWhenHidden = ui.refs.pauseHidden.checked;
        debounceSaveSettings();
        if (state.running && !state.paused) scheduleTick(0, 'pause-when-hidden setting changed');
        render();
      });
      ui.refs.autoZip.addEventListener('change', () => {
        settings.autoZip = ui.refs.autoZip.checked;
        debounceSaveSettings();
        render();
      });
      ui.refs.fileDelaySeconds.addEventListener('change', () => {
        settings.fileDelaySeconds = normalizeFileDelaySeconds(ui.refs.fileDelaySeconds.value);
        ui.refs.fileDelaySeconds.value = String(settings.fileDelaySeconds);
        debounceSaveSettings(); render();
      });
      ui.refs.downloadSuffixes.addEventListener('change', () => {
        const normalized = normalizeDownloadSuffixList(ui.refs.downloadSuffixes.value, { fallback: true });
        settings.downloadSuffixes = normalized.text;
        ui.refs.downloadSuffixes.value = normalized.text;
        debounceSaveSettings();
        showMessage(`Automatic file suffixes: ${normalized.text}`, false);
        render();
      });
      ui.refs.modelPolicy.addEventListener('change', () => {
        settings.modelPolicy = normalizeModelPolicy(ui.refs.modelPolicy.value);
        applyModelPolicySettingChange('operator-model-policy-change');
        debounceSaveSettings();
        showMessage(`Model policy: ${modelPolicySummary(modelPolicySnapshot(settings))}`, false);
        render({ forceModel: true });
      });
      ui.refs.modelTarget.addEventListener('change', () => {
        const key = ui.refs.modelTarget.value;
        const row = (state.modelGate.catalog?.rows || []).find(item => item.key === key);
        settings.modelTargetKey = key;
        settings.modelTargetLabel = row ? row.label : (ui.refs.modelTarget.selectedOptions[0]?.textContent || key).replace(/ · (?:unavailable|remembered)$/,'');
        settings.modelTargetVersion = normalizeModelVersionHint(row && row.version, settings.modelTargetLabel);
        applyModelPolicySettingChange('operator-model-target-change');
        debounceSaveSettings();
        render({ forceModel: true });
      });
      ui.refs.modelEffort.addEventListener('change', () => {
        settings.modelTargetEffort = normalizeModelEffortPolicy(ui.refs.modelEffort.value);
        applyModelPolicySettingChange('operator-model-effort-change');
        debounceSaveSettings();
        render({ forceModel: true });
      });
      ui.refs.modelRefresh.addEventListener('click', () => {
        markOperatorInteraction('model-catalog-refresh');
        void discoverModelCatalog({ operatorInitiated: true }).then(catalog => {
          if (catalog) {
            debounceSaveSettings();
            showMessage(`Observed ${catalog.rows.length} live model route${catalog.rows.length === 1 ? '' : 's'}.`, false);
          }
        });
      });
      ui.refs.trimOldTurns.addEventListener('change', () => {
        settings.trimOldTurns = ui.refs.trimOldTurns.checked;
        debounceSaveSettings();
        if (settings.trimOldTurns && state.running && !state.paused) armDomTrim(0, 'setting-enabled');
        else clearDomTrimTimer();
        if (!settings.trimOldTurns && state.domTrim.logicalTurnsRemoved) showMessage('Old rendered turns already removed by qomrade return after a page refresh; later trims are disabled.', false);
        render();
      });
      ui.refs.refreshMinutes.addEventListener('change', () => {
        settings.refreshMinutes = normalizeRefreshMinutes(ui.refs.refreshMinutes.value);
        ui.refs.refreshMinutes.value = String(settings.refreshMinutes);
        debounceSaveSettings();
        if (settings.hourlyRefresh && state.running && !state.paused) scheduleNextAutoRefresh('interval-changed');
        render();
      });
      ui.refs.hourlyRefresh.addEventListener('change', () => {
        settings.hourlyRefresh = ui.refs.hourlyRefresh.checked;
        debounceSaveSettings();
        if (settings.hourlyRefresh && state.running && !state.paused) scheduleNextAutoRefresh('setting-enabled');
        else {
          clearAutoRefreshTimer();
          state.autoRefresh.dueAt = 0; state.autoRefresh.retryAt = 0; state.autoRefresh.healingPending = null; state.autoRefresh.lastFaultSurfaceKey = null; state.autoRefresh.resumeTicket = null;
          if (!settings.hourlyRefresh) saveTabRecord('hourly-refresh-disabled', { suppressUnchangedSettings: false });
        }
        render();
      });
      ui.refs.start.addEventListener('click', startRun);
      ui.refs.stop.addEventListener('pointerdown', event => {
        event.preventDefault();
        stopRun('operator stopped qomrade');
      });
      ui.refs.stop.addEventListener('click', event => {
        if (state.running) {
          event.preventDefault();
          stopRun('operator stopped qomrade');
        }
      });
      ui.refs.pause.addEventListener('click', () => state.paused ? resumeRun() : pauseRun());
      ui.refs.sessionHandoff.addEventListener('click', () => void saveSessionHandoffFile());
      ui.refs.developerHandoff.addEventListener('click', () => void copyOfficerHandoff());
      ui.refs.flightRecorder.addEventListener('click', saveFlightRecorderFile);
      ui.refs.diagnostics.addEventListener('click', () => void copyDiagnostics());
      ui.refs.collapse.addEventListener('click', () => {
        ui.collapsed = !ui.collapsed;
        ui.refs.panel.classList.toggle('collapsed', ui.collapsed);
        ui.refs.collapse.textContent = ui.collapsed ? '+' : '−';
        updatePanelViewport();
      });
      panelDocument.addEventListener('focusin', event => {
        if (!state.effectControl.active || !event.target || !event.target.matches('textarea,input,[contenteditable="true"]')) return;
        revokeEffectAuthority('panel-editor-focus');
        if (state.running && !state.paused && !state.activeSend) {
          clearControllerTimer('panel editor cancelled pending send');
          setPhase('PANEL_EDIT_HOLD', 'Operator editing cancelled pending effects; any composer text remains untouched.');
        }
      });
      panelDocument.addEventListener('focusout', () => {
        setTimeout(() => {
          if (!state.running || state.paused || state.quarantine || state.phase !== 'PANEL_EDIT_HOLD' || panelEditorFocused()) return;
          state.metrics.panelEditReleases += 1;
          logEvent('panel-edit-release', 'qomrade editor released focus; controller work may resume.', panelFocusObservation());
          scheduleTick(0, 'qomrade editor released focus');
        }, 0);
      });
      window.addEventListener('resize', updatePanelViewport, { passive: true });
      ui.mounted = true;
      host.setAttribute('data-qomrade-panel-state', 'ready');
      state.boot.panelMountStatus = 'ready';
      state.boot.panelMountError = null;
      state.boot.panelMountedAt = nowIso();
      render();
    } catch (error) {
      mountPanelFailureNotice(host, error, 'direct-DOM iframe construction');
    }
  }
  function registerMenus() {
    if (typeof GM_registerMenuCommand !== 'function') return;
    const registrations = [
      ['qomrade — Start', startRun],
      ['qomrade — Pause/Resume', () => state.paused ? resumeRun() : pauseRun()],
      ['qomrade — Stop', () => stopRun('operator stopped qomrade')],
      ['qomrade — Copy Developer Handoff', () => void copyOfficerHandoff()],
      ['qomrade — Save ChatGPT Session Handoff', () => void saveSessionHandoffFile()],
      ['qomrade — Save Flight Recorder', saveFlightRecorderFile],
      ['qomrade — Copy compact diagnostics', () => void copyDiagnostics()],
    ];
    for (const [label, handler] of registrations) {
      try {
        GM_registerMenuCommand(label, handler);
        state.boot.menusRegistered += 1;
      } catch (error) {
        recordPageError({ kind: 'menu-registration-error', label, message: String(error && error.message || error) });
      }
    }
  }
  // @QOMRADE-CHUNK id=90.boot title="Single-tab boot and lifecycle wakeups"
  function boot() {
    if (!isEligibleRoute()) return;
    const onWindowError = event => {
      recordPageError({
        kind: 'window-error',
        message: trunc(event && event.message || 'window error', 2_000),
        filename: trunc(event && event.filename || '', 1_000),
        lineno: event && event.lineno || null,
        colno: event && event.colno || null,
        stack: trunc(event && event.error && event.error.stack || '', 4_000),
      });
    };
    const onUnhandledRejection = event => {
      const reason = event && event.reason;
      recordPageError({
        kind: 'unhandled-rejection',
        message: trunc(reason && reason.message || reason || 'unhandled rejection', 2_000),
        stack: trunc(reason && reason.stack || '', 4_000),
      });
    };
    window.addEventListener('error', onWindowError);
    window.addEventListener('unhandledrejection', onUnhandledRejection);
    document.addEventListener('click', manualFileClickObservation, true);
    document.addEventListener('scroll', scheduleNaturalScrollSessionCapture, { capture: true, passive: true });
    registerMenus();
    try {
      mountUi();
    } catch (error) {
      const host = ui.host || document.getElementById('qomrade-single-tab-host') || document.body.appendChild(document.createElement('div'));
      if (!host.id) host.id = 'qomrade-single-tab-host';
      mountPanelFailureNotice(host, error, 'uncaught panel bootstrap');
    }
    state.boot.readyAt = nowIso();
    logEvent('boot', 'qomrade single-tab runtime initialized; expensive observability remains operator-triggered.', {
      panelMounted: ui.mounted,
      panelMountStatus: state.boot.panelMountStatus,
      panelMountError: state.boot.panelMountError,
      menusRegistered: state.boot.menusRegistered,
      pathname: location.pathname,
      visibility: document.visibilityState,
    });
    void loadTabSettings().then(async record => { await applyLoadedTabRecord(record, 'initial-read'); beginSessionArchive('page-boot'); captureSessionTurns('page-boot');
      if (ui.sessionBootTimer) clearTimeout(ui.sessionBootTimer); ui.sessionBootTimer = setTimeout(() => { ui.sessionBootTimer = null; beginSessionArchive('page-observation'); captureSessionTurns('page-boot-settled'); }, 4_000);
    }).catch(error => {
      state.boot.tabRead.status = 'error';
      state.boot.settingsReadyAt = nowIso();
      recordPageError({ kind: 'boot-restore-error', message: String(error && error.message || error), stack: trunc(error && error.stack || '', 4_000) });
      render();
    });
    ui.bootAuthenticityTimer = setTimeout(() => {
      ui.bootAuthenticityTimer = null;
      state.boot.oneShotAuthenticityCheckedAt = nowIso();
      try {
        const observation = surfaceAuthenticityObservation({ detail: false });
        state.lastAuthenticity = observation;
        logEvent('boot-authenticity', `One-shot boot hard-signature verdict: ${observation.verdict}.`, observation);
        if (observation.hard) quarantineHardFalseGui(observation, 'one-shot-boot-authenticity');
        else { render({ forceModel: true }); maybeBeginAutoRefreshRestore(); }
      } catch (error) {
        recordPageError({ kind: 'boot-authenticity-error', message: String(error && error.message || error), stack: trunc(error && error.stack || '', 4_000) });
      }
    }, BOOT_AUTHENTICITY_DELAY_MS);
    ui.shellHealthTimer = setTimeout(() => {
      ui.shellHealthTimer = null;
      state.shellHealth.bootProbeAt = nowIso();
      try {
        const observation = observePageShellHealth('bounded-boot-probe', { capture: true });
        if (observation.degraded && state.running && !state.paused) holdForPageShellMaintenance(shellHealthSurface(observation), 'bounded-boot-probe');
      } catch (error) {
        recordPageError({ kind: 'page-shell-health-probe-error', message: String(error && error.message || error), stack: trunc(error && error.stack || '', 4_000) });
      }
    }, SHELL_HEALTH_BOOT_PROBE_MS);
    document.addEventListener('visibilitychange', () => {
      recordBackgroundEdge('visibilitychange');
      if (!document.hidden) noteBackgroundLifecycle('visible');
      logEvent('lifecycle', `visibilitychange: ${document.visibilityState}`);
      state.uiModelObservation = null;
      if (!document.hidden && state.shellHealth.current) observePageShellHealth('tab-became-visible', { capture: true });
      if (!document.hidden) { beginSessionArchive('page-observation'); captureSessionTurns('visibility-visible'); }
      render({ forceModel: !document.hidden });
      if (state.running && !state.paused && !document.hidden) {
        if (state.modelGate.lastSurvey?.surfaceFailure && !state.modelGate.active) state.modelGate.nextSurveyAt = 0;
        if (!wakeOverdueAutoRefresh('tab-became-visible', ['generation-advertised','hidden-policy-hold','operator-editing-qomrade','dialog-visible','continuation-visible','composer-not-empty','composer-attachment-present','composer-unavailable'])) scheduleTick(0, 'tab became visible');
        armZipRescan();
        if (settings.trimOldTurns) armDomTrim(1_000, 'tab-became-visible');
      }
      else if (state.running && pauseForHidden() && document.hidden) {
        revokeEffectAuthority('tab-hidden');
        clearControllerTimer('tab became hidden');
        if (ui.zipRescanTimer) clearTimeout(ui.zipRescanTimer);
        ui.zipRescanTimer = null;
      }
      else if (state.running && !state.paused && document.hidden) {
        if (state.phase === 'WAITING_GAP') scheduleGapTick();
        else scheduleTick(replyPollMs(), 'tab hidden; reduced controller cadence');
      }
    }, { passive: true });
    window.addEventListener('focus', () => {
      noteBackgroundLifecycle('focus');
      logEvent('lifecycle', 'window focus');
      state.uiModelObservation = null;
      if (state.shellHealth.current) observePageShellHealth('window-focus', { capture: true });
      beginSessionArchive('page-observation'); captureSessionTurns('window-focus');
      render({ forceModel: true });
      if (state.running && !state.paused) {
        if (!wakeOverdueAutoRefresh('window-focus', ['generation-advertised','hidden-policy-hold','operator-editing-qomrade','dialog-visible','continuation-visible','composer-not-empty','composer-attachment-present','composer-unavailable'])) scheduleTick(0, 'window focus');
        if (settings.trimOldTurns) armDomTrim(1_000, 'window-focus');
      }
    }, { passive: true });
    window.addEventListener('blur', () => {
      logEvent('lifecycle', 'window blur');
    }, { passive: true });
    window.addEventListener('pageshow', event => {
      logEvent('lifecycle', 'pageshow', { persisted: !!(event && event.persisted) });
      state.uiModelObservation = null;
      observePageShellHealth('pageshow', { capture: true });
      beginSessionArchive('page-observation'); captureSessionTurns('pageshow');
      render({ forceModel: true });
      if (state.running && !state.paused) { scheduleTick(0, 'pageshow'); if (settings.trimOldTurns) armDomTrim(1_000, 'pageshow'); if (settings.hourlyRefresh) armAutoRefresh('pageshow'); }
    }, { passive: true });
    window.addEventListener('pagehide', event => {
      logEvent('lifecycle', 'pagehide', { persisted: !!(event && event.persisted) });
      revokeEffectAuthority('pagehide');
      clearControllerTimer('pagehide');
      if (ui.shellHealthTimer) clearTimeout(ui.shellHealthTimer);
      ui.shellHealthTimer = null;
      if (ui.sessionScrollTimer) clearTimeout(ui.sessionScrollTimer);
      ui.sessionScrollTimer = null;
      clearDomTrimTimer();
      clearAutoRefreshTimer();
      clearFileOutcomeObserver('pagehide');
      captureSessionTurns('pagehide');
      persistContinuity('pagehide');
    }, { passive: true });
    window.addEventListener('popstate', () => {
      logEvent('lifecycle', 'popstate', { pathname: location.pathname });
      state.uiModelObservation = null;
      if (!isEligibleRoute()) stopRun('qomrade stopped because this route is not an eligible ChatGPT chat route.', { error: { kind: 'ineligible-route', pathname: location.pathname } });
      else if (state.running) validateConversationAnchor();
      render({ forceModel: true });
    }, { passive: true });
    if (TEST_MODE) {
      window.__qomradeFixtureAPI = {
        version: QOMRADE_VERSION,
        startRun,
        stopRun,
        pauseRun,
        resumeRun,
        setPrompt(value) { markOperatorInteraction('fixture-set-prompt'); settings.prompt = trunc(normalizePromptLineEndings(value), MAX_PROMPT_CHARS); render(); },
        setGapMinutes(value) { settings.gapMinutes = clamp(value, 1, 1_440); render(); },
        setModelPolicy(value) { settings.modelPolicy = normalizeModelPolicy(value); applyModelPolicySettingChange('fixture-model-policy'); render({ forceModel: true }); },
        setPinnedModel(label, effort = 'pro') { const row = (state.modelGate.catalog?.rows || []).find(item => item.label === label || item.key === modelRouteKey(label)); settings.modelPolicy = MODEL_POLICY_PIN; settings.modelTargetLabel = trunc(label || '', 180); settings.modelTargetKey = modelRouteKey(label); settings.modelTargetVersion = normalizeModelVersionHint(row && row.version, label); settings.modelTargetEffort = normalizeModelEffortPolicy(effort); applyModelPolicySettingChange('fixture-pinned-model'); render({ forceModel: true }); },
        discoverModelCatalog: () => discoverModelCatalog({ operatorInitiated: true }),
        modelPolicy: () => ({ settings: modelPolicySnapshot(settings), active: activeModelPolicySnapshot(), catalog: JSON.parse(JSON.stringify(state.modelGate.catalog || null)) }),
        setAutoZip(value) { settings.autoZip = !!value; if (!settings.autoZip) { if (ui.zipRescanTimer) clearTimeout(ui.zipRescanTimer); ui.zipRescanTimer = null; state.zipCapture.pending = null; } render(); },
        setDownloadSuffixes(value) { settings.downloadSuffixes = normalizeDownloadSuffixList(value, { fallback: true }).text; render(); },
        setFileDelaySeconds(value) { settings.fileDelaySeconds = normalizeFileDelaySeconds(value); render(); },
        setTrimOldTurns(value) { settings.trimOldTurns = !!value; if (settings.trimOldTurns && state.running) armDomTrim(0, 'fixture'); else clearDomTrimTimer(); render(); },
        setHourlyRefresh(value) { settings.hourlyRefresh = !!value; if (settings.hourlyRefresh && state.running) scheduleNextAutoRefresh('fixture'); else { clearAutoRefreshTimer(); state.autoRefresh.dueAt = 0; state.autoRefresh.healingPending = null; state.autoRefresh.lastFaultSurfaceKey = null; } render(); },
        setRefreshMinutes(value) { settings.refreshMinutes = normalizeRefreshMinutes(value); if (settings.hourlyRefresh && state.running) scheduleNextAutoRefresh('fixture-interval-change'); render(); },
        setAutoRefreshDueAt(value) { state.autoRefresh.dueAt = Number(value) || 0; state.autoRefresh.retryAt = 0; state.autoRefresh.retryDelayMs = 0; },
        attemptDomTrim: origin => attemptDomTrim(origin || 'fixture'),
        attemptAutoRefresh: origin => maybeAutoRefresh(origin || 'fixture'),
        captureSciencePulse: (origin, evidence) => captureBoundedSciencePulse(origin || 'fixture', evidence || {}),
        pipelineSurfaceEdges: () => state.science.surfaceEdges.slice(),
        domForensicsSnapshot: () => domForensicsSummary(),
        shellHealthSnapshot: () => shellHealthSummary(),
        observePageShellHealth: origin => observePageShellHealth(origin || 'fixture', { capture: true }),
        setBootAgeMs(value) { state.boot.startedT = Date.now() - Math.max(0, Number(value) || 0); },
        captureDomishEvent: (kind, options) => captureDomishEvent(kind || 'fixture', options || {}),
        requestHealingRefresh: (surface, origin) => requestHealingRefresh(surface, origin || 'fixture'),
        setHealingEligibleNow() { if (state.autoRefresh.healingPending) { state.autoRefresh.healingPending.eligibleAt = Date.now() - 1; state.autoRefresh.dueAt = Date.now() - 1; state.autoRefresh.retryAt = 0; clearAutoRefreshTimer(); } },
        autoRefreshSnapshot,
        domTrimSnapshot,
        setNextSendAt(value) { state.nextSendAt = Number(value) || 0; },
        state: () => ({ ...runtimeSnapshot(), baselineAssistantId: state.baselineAssistantId, stableSamples: state.stableSamples, boot: JSON.parse(JSON.stringify(state.boot)) }),
        settings: () => ({ ...settings }),
        buildTabRecord: reason => buildTabRecord(reason || 'fixture'),
        saveTabRecord: reason => saveTabRecord(reason || 'fixture'),
        sendPrompt,
        setRestoreDeadlineNow() { state.autoRefresh.restoreStartedAt = Date.now() - AUTO_REFRESH_RESTORE_MAX_MS - 1; state.autoRefresh.restoreDeadlineAt = Date.now() - 1; },
        injectOversizedReceipt(chars = 200_000) {
          const text = 'x'.repeat(Math.max(0, Number(chars) || 0));
          state.activeSend = { schema: 'qomrade.send-transaction.v1', id: 'fixture-oversized-receipt', startedAt: nowIso(), promptChars: 1, promptHash: 'fixture', model: { label: '5.6 Pro', family: 5.6, hasPro: true }, outcome: 'fixture', outcomeDetail: { kind: 'fixture', text } };
        },
        buildDiagnostics,
        buildOfficerHandoff,
        buildSessionHandoff,
        backfillSessionTranscript,
        buildFlightRecorder,
        copyOfficerHandoff,
        saveSessionHandoffFile,
        saveFlightRecorderFile,
        maintenanceRecommendation,
        memoryPressureObservation,
        navigationLifecycleObservation,
        sessionArchiveSummary,
        captureSessionTurns,
        captureSessionTurnsIfSurfaceChanged,
        effectiveCadence: () => ({ replyPollMs: replyPollMs(), gapPollMs: gapPollMs(), hidden: document.hidden, pauseWhenHidden: settings.pauseWhenHidden }),
        panelFocus: panelFocusObservation,
        probes: {
          authenticity: surfaceAuthenticityObservation,
          shellHealth: pageShellHealthObservation,
          barrier: conversationBarrierObservation,
          work: workEvidenceObservation,
          dialogs: visibleDialogObservation,
          continuation: continuationObservation,
          retry: retryObservation,
          faults: () => { invalidateTurnCache('fixture-fault-probe'); return observeVisibleFaults(latestAssistantTurn(), { origin: 'fixture', includeHistory: true }); },
          redSignals: redSignalObservation,
          systemSurfaces: systemSurfaceObservation,
          outputs: outputControlsObservation,
          resources: resourceTimingObservation,
          semanticDom: semanticDomObservation,
          controls: currentControlsObservation,
          page: pageObservation,
          userscript: userscriptEnvironmentObservation,
        },
        currentModelObservation: () => { const model = currentModelObservation(); return { ok: model.ok, directOk: model.directOk, reason: model.reason, label: model.label, family: model.family, version: model.version, hasPro: model.hasPro, transient: model.transient, lastConfirmed: model.lastConfirmed }; },
        surveyAndSelectEligiblePro,
        ensureEligibleProModel,
        ensureConfiguredModel,
        inspectOpenModelMenu: () => stripModelInspection(inspectOpenModelMenu({ includeMarkup: true })),
        modelMenuSurface: stage => recordModelMenuSurface(stage || 'fixture'),
        zipInventory: () => zipInventory(latestAssistantTurn()),
        captureZip: (id) => { invalidateTurnCache('fixture-capture'); return captureZipFromAssistant(materializedTurns().find(turn => turn.id === id) || latestAssistantTurn()); },
        fileCaptureSnapshot: zipCaptureSnapshot,
        recordFileDownloadNotice: selector => recordFileDownloadNotice(document.querySelector(selector), 'fixture'),
        replyPollMs, backgroundSnapshot,
        latestAssistantTurn: options => latestAssistantTurn(options || {}),
        recordPageError,
        classifyPipelineFailureText,
        classifyPipelineMaintenanceText,
        parseModelVersion,
        editorPayloadEquivalent,
        structuredSessionNodeText,
        sessionTurnText: index => { invalidateTurnCache('fixture-session-turn-text'); const turn = materializedTurns()[Number(index) || 0]; return turn ? sessionTurnText(turn) : null; },
        markOperatorInteraction,
        pipelineSurfaceHistory: () => handoffPipelineSurfaceHistory(),
        advanceRecoveryClock(ms) { recoveryFixtureClockOffset += Math.max(0, Number(ms) || 0); },
        recoveryStep: tick,
        recoverySnapshot,
        recoveryProbe: () => { invalidateTurnCache('fixture-recovery-probe'); captureActiveSendAdoption(); return pipelineFaultObservation(); },
        editorPromptPayload,
        readComposerText: () => readComposerText(findComposer()),
        compareRenderedPrompt,
        materializedTurns: () => { invalidateTurnCache('fixture-materialized-turns'); return materializedTurns().map(turn => ({ id: turn.id, role: turn.role, ordinal: turn.ordinal, adapter: turn.adapter, text: turnText(turn.element) })); },
      };
    }
  }
  if (document.body) boot();
  else window.addEventListener('DOMContentLoaded', boot, { once: true });
})();
// QOMRADE-END schema=1 copy-paste-sentinel=present
