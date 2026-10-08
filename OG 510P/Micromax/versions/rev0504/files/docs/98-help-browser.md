# Help browser

This page exists mostly as **test data** for Micromax’s docs-backed help system.
It also acts as a tiny “index” you can navigate *inside* the editor.

It also doubles as a small grouped-picker fixture: the `Links` / `External links` /
other heading buckets below are used by `helpoutlinepick`, `helplinkpick`, and `helpnavpick` to
prove that heading rows keep honest breadcrumb sections instead of collapsing
into one generic `Headings` label. Rev334 adds a small orientation follow-up: successful picker-driven docs moves now also report the real landed target instead of only moving the cursor or opening the doc.

In a docs buffer:
- `Enter` follows the link under the cursor
- `Backspace` goes back
- `y` copies the link target under the cursor
- rev335 also makes these ordinary docs moves speak up: successful `helpfollow`, `helpback`, `help docs ...`, and `helppick`/`docpick` submission now report the real landed help target instead of just changing pages
- rev389 also keeps docs misses in one typed dialect: stale `helpback` entries and missing internal docs links now fail as `help docs: no such doc: TOPIC` instead of older `help: no doc for ...` prose
- rev397 closes the same wording gap for docs-link actions: `helplinkcopy` now reports `helplinkcopy: target`, and confirmed external `helpfollow` opens now report `helpfollow: URL` instead of older generic `help:` / `opened external link` prose
- rev398 closes the tiny remaining `helpfollow` miss gap in that same loop: `helpfollow` now reports `helpfollow: not in a docs buffer` or `helpfollow: no link under cursor` instead of older generic `help:` wording when no followable target exists yet
- rev401 closes the tiny remaining fragment-jump miss gap in that same docs loop: unresolved same-page `#fragment` or `[^footnote]` targets now report `helpjump: no section or footnote: #target` instead of falling back to generic `help:` wording
- rev399 gives `helpback` the same typed identity on its direct paths: successful returns now report `helpback: topic @ line:col`, and empty history now reports `helpback: back stack empty` instead of generic `help:` wording
- rev400 closes the tiny direct-lookup success gap in that same help/docs loop: explicit `help docs TOPIC` opens now report `help docs: topic @ line:col` instead of collapsing back to the broader `help:` success prefix
- rev402 makes docs history itself more exact and inspectable: `helpback` history entries now remember the prior docs cursor target, stale missing-doc entries stay on the stack until they actually reopen, and `status_model()` now exposes current/back docs-history state through stable `help_*` fields instead of forcing future UIs/scripts/LLMs to infer it from the last message
- rev403 gives that same tiny history loop a local forward half: `helpforward` retraces the page reopened by `helpback`, ordinary docs opens clear stale forward history when you branch to a different page, and the inspectable `help_*` status fields now expose separate back/forward targets together with a plain `session` scope instead of looking accidentally persistent
- rev404 tightens the destination side of that same loop: same-page `helpjump`, fragment/footnote `helpfollow`, `helpoutlinepick`, and heading picks from `helpnavpick` now push the prior docs cursor target onto local help history too, while `help_position` keeps same-topic history summaries from flattening distinct landed sections back into one page slug
- rev405 makes that local docs-history loop directly reviewable too: `helphistory` now prints a tiny count-aware current/back/forward register and scripts/future UIs can read the same ordered rows through `help_history_rows()` / `ed.helphistory-rows` instead of inferring the trail from transient messages
- rev406 keeps that same trail honest when it goes off-screen: leaving or closing a docs buffer now preserves one explicit session-local current help target, `helphistory` shows it as `[dormant]`, `help_navigation_summary` names it as `topic (dormant)`, and `helpresume` / `ed.help-resume` reopen it without consuming back/forward history
- rev407 adds the matching exact-action cue on the smallest plain surface too: `status_model()` now exposes `help_resume_command`, `help_back_command`, `help_forward_command`, and ordered `help_navigation_actions`, while plain `showstatus` / `ed.status-summary` surface those cues as `help_nav=...` / `help_actions=...` so humans and future UIs/LLMs do not have to translate dormant/back/forward state back into commands by hand
- rev410 keeps that same local trail continuous across ordinary docs opens too: if you leave the help buffer and open a different docs page from elsewhere, Micromax now treats the dormant current help target as the branch head of the same session-local history, pushes it onto `helpback` with its exact cursor position, and clears stale dormant forward history when the new page diverges
- rev412 closes the matching same-topic reopen seam too: if the dormant current page is reopened by name after its old help buffer was closed, Micromax now restores the remembered session-local cursor target instead of silently resetting that same docs topic back to `1:0`
- rev413 tightens the smallest replay-cue split too: `help_session_*` still witness the current session-local docs head, but `help_resume_available` is now true only when that head is actually dormant and resumable, so an already-active help page no longer pretends `helpresume` is actionable
- rev414 closes the matching active-command seam too: if that same page is already active on-screen, plain `helpresume` / `ed.help-resume` now fail as `helpresume: already active: topic @ line:col` instead of silently replaying the current page
- rev415 keeps stale replay misses in that same typed dialect too: when a remembered `helpresume` / `helpback` / `helpforward` target no longer resolves, the command now fails as `helpresume: missing doc: TOPIC`, `helpback: missing doc: TOPIC`, or `helpforward: missing doc: TOPIC` instead of collapsing back to generic `help docs:` wording
- rev416 keeps ordinary docs opens inside that same tiny replay loop too: when `help docs TOPIC`, `help TOPIC`, or a cross-doc `helpfollow` already matches exactly one adjacent back/forward target, Micromax now reuses that immediate local history step instead of branching a duplicate path or clearing deeper forward history
- rev430 makes docs discovery rows more legible too: docs picker/info summaries now prefer the first meaningful line after the primary heading, so rev-note-heavy archive pages preview as the document itself instead of leading with archive bookkeeping
- rev431 adds the matching exact-inspection sibling too: `showdoc TOPIC` prints one resolved docs detail line and `ed.doc-detail-row` exposes the same `[topic title summary section path]` row, while command-prompt completion for both `showdoc` and `help docs` now reuses that same doc metadata instead of treating exact doc names as opaque strings
- rev438 adds the matching broad-summary sibling too: `showdocs` prints one tiny count-aware docs-family inventory and `ed.doc-section-summary-rows` exposes the same `[[label count sample_name sample_detail] ...]` rows, so scripts/future UIs can answer what docs families exist without walking every grouped picker row
- rev441 adds the matching broad current-page sibling too: `showhelpnav [QUERY]` prints one tiny count-aware summary of the current docs page's heading/link buckets, while `help_nav_section_summary_rows(QUERY)` / `ed.helpnav-section-summary-rows` expose the same `[[label count sample_name sample_detail] ...]` rows instead of forcing scripts or future UIs to open `helpnavpick` or walk every grouped section
- rev432 closes the generic discovery seam too: docs topics now participate in the ordinary `help` / `apropos` / `topicpick` topic rows and prompt completion instead of staying hidden behind docs-specific verbs
- rev433 adds the matching exact current-page heading sibling too: `helpjump QUERY` now reuses `help_heading_detail_row(QUERY)` / `ed.help-heading-detail-row`, which expose one resolved `[topic title fragment level line col section]` row for the same heading target instead of forcing scripts or future UIs to reparse `help_outline_rows()`
- rev435 adds the matching exact current-heading sibling too: `showhelpheading` now gives humans one explicit inspection path for the nearest heading owning the cursor, while `current_help_heading_detail_row()` / `ed.help-current-heading-detail-row` expose the same resolved `[topic title fragment level line col section]` row instead of forcing scripts or future UIs to rescan `help_outline_rows()` or infer the active heading from breadcrumbs alone
- rev434 adds the matching exact current-link sibling too: `showhelplink` now gives humans one explicit inspection path for the link under the cursor, while `help_link_detail_row()` / `ed.help-link-detail-row` expose the same resolved `[topic label target kind line col section]` row that `helpfollow` / `helplinkcopy` already act on instead of forcing scripts or future UIs to rescan `ed.help-link-rows`
- rev408 tightens the stale-history side of that same loop: remembered session/back/forward targets now stay witnessable even after the docs file disappears, but replay commands and `help_actions=` only appear when the target still resolves, while `help_warn=` / `[missing]` cues name blocked replay paths instead of letting stale history masquerade as actionable

## Links

The live docs/help TUI now also gives visible supported ordinary markdown links a tiny source-view cue: the non-label scaffolding (`[` / `](` + destination or reference tail / `]`) renders **dim** while the live label stays underlined.

- [Vision](00-vision.md)
- [Softwrap](94-softwrap.md)
- [Host API](31-host-api.md)
- [Open URL under cursor](101-open-url-under-cursor.md)
- [Metadata note](177-docs-cues-image-metadata.md)

## External links

External links are shown as a message by default.

If you enable the capability gate, they can be opened via the host:

```text
set cap.open-url true
```

Even when enabled, Micromax confirms by default before opening external links, and the prompt names where the request came from (help page, cursor URL, or explicit command).
You can turn the confirmation off:

```text
set open-url.confirm false
```

- [micro editor](https://micro-editor.github.io/)



## Reference-style links

Micromax's docs browser also understands common markdown reference links:

The live docs/help TUI now also treats visible reference-definition lines a little less like prose:
- starter lines like `[visionref]:` render **dim** with a **bold marker token**
- tiny wrapped destination/title continuation lines render **dim** too

- [Vision ref][visionref]
- [Vision shortcut]

[visionref]: 00-vision.md
[Vision shortcut]: 00-vision.md

## Nested bracket labels

Micromax now handles a small but useful markdown case that plain regexes trip over: balanced brackets inside link labels.

- [Vision [nested inline]](00-vision.md)
- [Vision [nested ref]][nested-vision-ref]
- [Vision [nested shortcut]]

[nested-vision-ref]: 00-vision.md
[Vision [nested shortcut]]: 00-vision.md

## Fragment links

Micromax also follows markdown fragment links for headings:

- [Outline picker section](#outline-picker)
- [Vision key commitment](00-vision.md#key-commitment)
- [Explicit fragment target](#custom-frag)
- [Image anchor note](177-docs-cues-image-metadata.md#image-metadata-anchor)

## Autolinks

Autolinks are also recognized. The live docs/help TUI now also gives visible supported angle-bracket autolink tokens a tiny source-view cue: the whole `<...>` token renders **bold** while the inner URL still keeps the ordinary docs-link underline.

- <https://micro-editor.github.io/>

## Images

Common markdown image syntax can appear in docs, but Micromax currently treats it as **non-navigable prose** in the tiny help browser until there is a clearer image-aware policy. The live docs/help TUI now also gives visible supported image tokens a tiny inert-source cue by rendering the whole token **dim**:

- ![Vision image](00-vision.md)
- ![Vision ref image][visionimg]

[visionimg]: 00-vision.md

## Nested links inside labels

CommonMark allows balanced brackets inside link text, but valid links may **not** contain other links at any level of nesting. In those cases the tiny docs browser now keeps the outer would-be link as prose and only exposes the valid inner link:

- [Outer prose [Nested inner inline](94-softwrap.md)](00-vision.md)
- [Outer prose [Nested inner ref][visionref]](00-vision.md)

Tiny behavior:
- the outer would-be link stays prose instead of becoming a giant regex-shaped false positive
- the valid inner link remains live for `helpfollow`, `helplinkpick`, and TUI underlining
- this keeps the same shared docs-link matcher aligned with current CommonMark's nested-link rule without committing Micromax to a full inline parser

## Empty or whitespace-only labels

Current CommonMark also requires link labels to contain at least one non-whitespace character, so malformed empty/space-only labels stay prose in the tiny docs browser too:

- Empty inline label stays prose: [](99-empty-inline-should-stay-prose.md)
- Space-only inline label stays prose: [ ](99-space-inline-should-stay-prose.md)
- Space-only reference label stays prose: [  ][space-only-ref]
- Empty shortcut label stays prose: []
- Space-only shortcut label stays prose: [   ]

[space-only-ref]: 99-space-ref-should-stay-prose.md

Tiny behavior:
- empty and whitespace-only labels do **not** become live docs links
- the same guard now applies across inline links, full reference links, and shortcut reference links
- this keeps malformed examples in docs/tutorial prose from turning into invisible or blank picker rows

## Footnotes

Micromax also recognizes common markdown footnote references[^help-footnote].
Following a footnote jumps to its definition in the current docs buffer.

Micromax now also includes a tiny multi-line footnote example[^help-footnote-more].

The live docs/help TUI now also gives visible footnote-reference tokens a tiny source-view cue: the whole `[^id]` token renders **bold** while the inner `^id` still keeps the ordinary docs-link underline.

The live docs/help TUI also treats visible footnote-definition starter lines a little less like prose: starter lines like `[^id]:` render **dim** with a **bold marker token**, and tiny indented continuation lines under those starters also render **dim**.

## Destination escapes and paths

Micromax also now applies a tiny, shared destination parser to inline links and reference definitions, so a few path-like cases stop behaving like regex accidents:

- [Space path doc (escaped space)](103-space\ path.md)
- [Space path doc (percent-encoded)](103-space%20path.md)
- [Paren topic doc](104-paren\(topic\).md)
- [Space path doc ref][space-path-doc]
- [Paren topic doc ref][paren-topic-doc]
- [Space path doc ref (dest next line)][space-path-doc-multiline]
- [Paren topic doc ref (dest + title next line)][paren-topic-doc-multiline]
- [Space path doc ref (title next line)][space-path-doc-title-next-line]
- [Space path doc (inline dest next line)](
  103-space\ path.md)
- [Paren topic doc (inline title next line)](104-paren\(topic\).md
  "tiny wrapped title")
- [Angle space path doc (inline dest next line)](
  <103-space path.md>)
- [Angle space path doc ref (dest next line)][angle-space-path-doc-multiline]
- [Open the wrapped inline links demo doc](108-wrapped-inline-links.md)
- [Open the angle-wrapped links demo doc](109-angle-wrapped-links.md)

[space-path-doc]: 103-space\ path.md
[paren-topic-doc]: 104-paren\(topic\).md
[space-path-doc-multiline]:
  103-space\ path.md
[paren-topic-doc-multiline]:
  104-paren\(topic\).md
  "tiny multiline title"
[space-path-doc-title-next-line]: 103-space\ path.md
  "tiny wrapped title"
[angle-space-path-doc-multiline]:
  <103-space path.md>
  "tiny angle title"

Tiny policy:
- bare destinations keep supporting ordinary `topic.md` forms
- balanced parentheses inside destinations are handled best-effort
- markdown-safe backslash escapes in destinations/definitions are unescaped before local-doc follow
- percent-encoded local paths are also decoded before local-doc follow
- tiny reference definitions can also wrap the destination or title onto the next line
- tiny inline links can now also wrap the destination or title/close across the next line
- angle-bracket destinations now use the same tiny wrapped-inline / wrapped-reference path, while still requiring whitespace before any optional title

This is still intentionally small and editor-facing rather than full CommonMark destination/title parsing.

## Indented code-ish markdown

The tiny docs browser now also keeps a few code-block-ish indentation traps literal: four-space or tab-indented reference definitions / footnote definitions should **not** activate docs links, and four-space or tab-indented ATX headings should stay out of docs outlines and fragment jumps.

- [Open the indented code-ish markdown demo doc](107-indented-codeish-markdown.md)

Tiny behavior:
- markdown block starters in the docs browser keep following the small **up to three leading spaces** rule
- four leading spaces and tab-indented lookalikes stay code-ish prose instead of becoming live docs structure
- this keeps reference definitions, footnote definitions, and headings from leaking out of examples that are really meant to read like indented code

## Indented inline links stay prose

The tiny docs browser now also keeps blank-separated top-level indented code-ish lines inert for inline links/autolinks too:

    [Ghost indented inline link](94-softwrap.md)
    <https://example.invalid/indented-not-a-real-help-link>

Tiny behavior:
- blank-separated top-level indented code-ish runs stay **non-navigable prose** for `helpfollow` / `helplinkpick`
- TUI docs-link underlining also ignores markdown-looking text inside those lines
- the live docs/help TUI also dims those lines a little so source-view code examples read more like code

This stays intentionally small and shared-policy-driven rather than list-aware CommonMark parsing: the goal is better source-view honesty for ordinary top-level examples, not a full markdown block model.

## Escapes

Backslash-escaped markdown stays literal prose in the tiny help browser instead of turning into a live link/image/footnote/autolink:

The live docs/help TUI now also gives visible escaped markdown opener/delimiter pairs a tiny source-view cue by rendering the visible two-character pair **dim**:

- `\[` / `\!` / `\<`
- `\*` / `\_` / `\~`
- ``\```


- \[Literal inline link](00-vision.md)
- \[Literal ref link][literal-ref]
- \[Literal shortcut]
- \[^escaped-help-footnote]
- \<https://example.invalid/escaped-help-autolink>
- \![Escaped Vision image](00-vision.md)

[literal-ref]: 00-vision.md
[Literal shortcut]: 00-vision.md
[^escaped-help-footnote]: Defined on purpose so the escaped reference still stays prose.

This keeps docs that *teach* markdown from becoming accidentally navigable.

## Setext headings

The tiny docs browser now also treats common setext headings as real outline/fragment targets, so a small markdown page can use either heading style without losing help navigation features:

- [Open the setext demo doc](105-setext-headings.md)
- [Jump to the setext outline section](105-setext-headings.md#outline-section)
- [Jump to the explicit setext fragment](105-setext-headings.md#custom-setext-frag)

This stays intentionally small and conservative: single-line and tiny multi-line setext headings participate in outline rows, fragment jumps, heading breadcrumbs, and docs-picker titles without turning Micromax into a full block parser.

- [Open the multi-line setext demo doc](106-multiline-setext-headings.md)
- [Jump to the multi-line setext outline section](106-multiline-setext-headings.md#outline-section-for-multi-line-setext)
- [Jump to the explicit multi-line setext fragment](106-multiline-setext-headings.md#multi-setext-frag)

## Headings in the live TUI

The minimal TUI now also gives docs/help headings a little more parity with the structure the browser already understands:

- `# ATX heading` title lines render **bold**
- setext heading title lines also render **bold**
- setext underline rails (`===` / `---`) render **dim**

This is still intentionally **UI-only** and best-effort: the goal is simply that a heading that already participates in outline rows and fragment jumps should also *look* like a heading in the live docs buffer.

## Fenced code blocks in the live TUI

The minimal TUI now also makes fenced markdown examples read a bit more like code instead of ordinary prose:

- opening/closing fence lines render **bold + dim**
- fenced body lines render **dim**
- this reuses the same tiny shared fence scan already trusted for docs-link/definition precedence, so live rendering and docs actions do not drift

This is still intentionally **UI-only** and conservative: the goal is simply that triple-backtick / tilde examples in repo docs look visibly code-ish without committing Micromax to a fuller markdown renderer.

## HTML comments

The docs browser now also treats raw HTML comments as inert prose for navigation, outline scanning, and link underlining precedence:

- [Visible link before comment](00-vision.md) <!-- [Ghost inline comment link](94-softwrap.md) -->

<!--
## Hidden heading inside comment

- [Ghost block comment link](94-softwrap.md)
[ghost-comment-ref]: 94-softwrap.md
[^ghost-comment-footnote]: This footnote definition lives inside a raw HTML comment.
-->

- [Visible link after comment block](94-softwrap.md)
- [Ghost commented ref][ghost-comment-ref]
- [^ghost-comment-footnote]

Tiny behavior:
- raw HTML comment bodies stay **non-navigable prose** for `helpfollow` / `helplinkpick`
- TUI docs-link underlining also ignores markdown-looking text inside comments
- the live docs/help TUI now also dims raw HTML comment spans so commented-out notes read less like ordinary prose
- reference definitions, footnote definitions, and headings inside comments are ignored too

This stays intentionally small and shared-policy-driven: enough to keep literal markdown examples and commented-out notes from leaking into the live docs browser without committing Micromax to a fuller raw-HTML parser.

## HTML blocks

The docs browser now also treats common raw HTML blocks as inert prose for navigation, outline scanning, and link underlining precedence:

<div>
[Ghost html block link](94-softwrap.md)
[ghost-html-block-ref]: 94-softwrap.md
[^ghost-html-block-footnote]: This footnote definition lives inside a raw HTML block.
## Hidden heading inside raw HTML block
</div>

<pre>
[Ghost pre block link](94-softwrap.md)

still hidden inside pre
</pre>

- [Visible link after raw HTML block](94-softwrap.md)
- [Ghost html block ref][ghost-html-block-ref]
- [^ghost-html-block-footnote]
- [Visible link after pre block](00-vision.md)

Tiny behavior:
- common raw HTML blocks like `<div>...</div>` and `<pre>...</pre>` stay **non-navigable prose** for `helpfollow` / `helplinkpick`
- TUI docs-link underlining also ignores markdown-looking text inside those blocks
- the live docs/help TUI now also dims those raw HTML block lines so embedded HTML examples read less like ordinary prose
- reference definitions, footnote definitions, and headings inside those blocks are ignored too

This stays intentionally small and shared-policy-driven: enough to keep embedded HTML examples from leaking into the live docs browser without committing Micromax to a fuller HTML parser or Markdown-in-HTML model.

## Generic HTML blocks

The docs browser now also treats conservative CommonMark type-7-ish tag-only lines as raw HTML blocks when they start after a blank line (or at the start of a doc):

<widget-box data-kind="demo">
[Ghost generic html block link](94-softwrap.md)
[ghost-generic-html-block-ref]: 94-softwrap.md
[^ghost-generic-html-block-footnote]: This footnote definition lives inside a generic raw HTML block.
## Hidden heading inside generic raw HTML block
</widget-box>

- [Visible link after generic raw HTML block](00-vision.md)
- [Ghost generic html block ref][ghost-generic-html-block-ref]
- [^ghost-generic-html-block-footnote]

Paragraph before generic tag
<span class="inlineish-demo">
[Visible link after paragraph-adjacent generic tag](105-setext-headings.md)

Tiny behavior:
- generic tag-only lines like `<widget-box ...>` / `</widget-box>` now also stay **non-navigable prose** until the next blank line
- this pass is intentionally conservative: it only starts after a blank line (or at doc start), so paragraph-adjacent tags like the `<span ...>` example above do **not** swallow following markdown links
- the same tiny shared block helper still drives `helpfollow`, `helplinkpick`, outline scanning, reference/footnote-definition parsing, and TUI docs-link underlining, while the live docs/help TUI also dims those block lines

This keeps another real CommonMark/GFM-ish literal-docs case safe without committing Micromax to a fuller HTML parser or Markdown-in-HTML model.

## Raw HTML tag precedence

The tiny docs browser now also treats inline raw HTML tags and autolinks as tighter than markdown link grouping inside would-be link labels, so a few CommonMark-shaped regex traps stay literal prose instead of becoming fake links:

- [Fake raw HTML tag <span title="](99-missing.md)">
- [Fake raw HTML ref <span title="][visionref]">
- [Fake raw HTML autolink <https://example.invalid/raw-help-autolink?x=](99-missing.md)>
- [Visible link after raw HTML precedence](00-vision.md)

Tiny behavior:
- raw HTML tags/autolinks that begin inside a would-be link label keep the whole construct non-navigable
- the same small precedence rule is shared by `helpfollow`, `helplinkpick`, and TUI docs-link underlining

## Inline raw HTML tags

The live docs/help TUI now also gives visible inline raw HTML tags a small inert-source cue so source-view prose with literal tags reads less like ordinary text:

- Press <kbd>Ctrl-b</kbd> to open the buffer picker.
- This is <ins>underlined-ish</ins> source text, not a markdown link.
- <a name="inline-raw-anchor"></a>
- <https://example.invalid/inline-autolink> stays an autolink-shaped token rather than sharing the raw-HTML cue.
- [Visible link after inline raw HTML tags](00-vision.md)

Tiny behavior:
- visible inline raw HTML tags like `<kbd>` / `</kbd>` / `<a name=...>` now render dim in the live docs/help TUI
- supported autolinks like `<https://...>` keep their existing bold whole-token cue instead of being treated as raw HTML tags
- the same tiny shared inline raw-HTML helper still drives docs-link precedence, so this stays render-parity rather than a second parser path
- this fixes real CommonMark-style false positives without committing Micromax to a fuller HTML parser

## Inline code

The minimal TUI already dims inline code spans in docs/help buffers, and it now also recognizes equal-length backtick delimiters for the common “literal backtick inside code” case while giving the visible backtick runs a tiny source-view cue too:

- `simple code`
- ``code with `literal backticks` inside``

Tiny behavior:
- code body text is **dim**
- visible opening/closing backtick runs render **bold + dim**
- code spans are masked before link underlining, so markdown-looking text inside code does **not** look clickable
- docs-browser actions also respect that precedence, so `helpfollow` / `helplinkpick` ignore markdown-looking text inside inline code too

This is still intentionally **UI-only** and best-effort: enough to make prose cues easier to scan without committing Micromax to a fuller inline markdown parser or full CommonMark whitespace-normalization rules.

- ``[Fake inline link](99-missing.md)`` stays code-ish prose, not a docs link
- ``[Fake ref link][visionref]`` also stays prose
- ``<https://example.invalid/not-a-real-help-link>`` inside code also stays prose

## Fenced code blocks

The docs browser now also treats fenced code blocks as inert prose for navigation and link-underlining precedence:

```text
[Fake fenced inline link](99-missing.md)
[Fake fenced ref][fake-fenced-ref]
<https://example.invalid/fenced-not-a-real-help-link>
[fake-fenced-ref]: 00-vision.md
```

Tiny behavior:
- fenced examples stay **non-navigable prose** for `helpfollow` / `helplinkpick`
- TUI docs-link underlining also ignores markdown-looking text inside fenced code
- reference definitions inside fenced examples are ignored too

This is still intentionally tiny and shared-policy-driven: enough to keep executable docs and literal markdown examples from fighting each other without committing Micromax to a fuller markdown block parser.

## Inline emphasis

The minimal TUI now also gives a few tiny markdown inline emphasis forms a little scanability polish in docs/help buffers:

- `**strong**` means **strong signal**
- `*emphasis*` or `_emphasis_` means a softer emphasis hint
- `~~obsolete~~` means struck / stale text

Tiny behavior:
- strong body text is **bold**
- emphasis body text is *italic when available* (falling back to underline on terminals without italics)
- strikethrough body text is **dim**
- visible delimiter tokens like `**`, `*`, `_`, and `~~` now also render **dim** so markdown punctuation reads a little more like deliberate source

- **strong delimiter cue**
- *emphasis delimiter cue*
- _underscore delimiter cue_
- ~~strike delimiter cue~~

This is still intentionally **UI-only** and best-effort: enough to make prose cues easier to scan without committing Micromax to a fuller inline markdown parser or exact CommonMark delimiter-run behavior.

## Tables

The minimal TUI now gives simple pipe tables a little scanability polish in docs/help buffers:

| Surface | Tiny behavior |
| --- | --- |
| Header row | bold |
| Delimiter row | dim |
| `|` separators | dim |

This is intentionally **UI-only** and best-effort: enough to make docs tables easier to scan without committing Micromax to a full markdown parser.

## Lists

The minimal TUI now also gives common markdown list markers a little scanability polish in docs/help buffers:

- plain bullet item
+ alternate bullet item
1. ordered item
2) alternate ordered item
    - nested bullet item
      3. nested ordered item

Tiny behavior:
- the list marker token (`-`, `+`, `*`, `1.`, `1)`) is **bold**
- top-level source-view scanability still starts from the conservative small rule (up to three leading spaces)
- the live docs/help TUI now also opts into deeper indentation for **nested** list items after the shared indented-code check has already ruled out real code blocks
- task-list rows reuse that same list marker substrate, then add checkbox-specific styling on top

This is also intentionally **UI-only** and best-effort: enough to make list-heavy docs and worklists easier to scan without committing Micromax to a fuller markdown block parser.

## Task lists

The minimal TUI also recognizes small GFM-style task-list markers in docs/help buffers:

- [ ] Open the outline picker
- [x] Follow a fragment link
1. [X] Jump to a footnote definition
    - [x] nested finished task

Tiny behavior:
- checkbox token (`[ ]` / `[x]`) is **bold**
- checked task bodies are **dim**
- nested task rows now benefit from the same deeper-indent source-view relaxation as ordinary nested lists, but only after indented-code detection has already kept true code blocks inert

This is also intentionally **UI-only** and best-effort: enough to make TODO-like prose easier to scan without committing Micromax to interactive markdown checkboxes.

## Blockquotes

The minimal TUI now also gives common markdown blockquotes a little scanability polish in docs/help buffers:

> Micromax keeps these docs affordances deliberately tiny, local, and replaceable.
> The goal is faster scanning, not a full markdown renderer.
>
> [!NOTE]
> GitHub-style alert markers now also get a tiny source-view cue.

Tiny behavior:
- quote-marker prefix (`> ` / `> > `) is **bold**
- quoted body text is **dim**
- common GitHub-style alert opener tokens inside blockquotes (`[!NOTE]`, `[!TIP]`, `[!IMPORTANT]`, `[!WARNING]`, `[!CAUTION]`) are also **bold**

This is again intentionally **UI-only** and best-effort. The helper model favors the readable common `> ` form and nested quote rails over full CommonMark edge-case coverage.

## Thematic breaks

The minimal TUI now also gives common markdown thematic breaks a little scanability polish in docs/help buffers:

---

* * *

___

Tiny behavior:
- the separator line is **dim**
- the visible marker run (`---`, `* * *`, `___`) is **bold**

This is still intentionally **UI-only** and best-effort: enough to make section separators easier to spot without committing Micromax to a fuller markdown block model.


## Link picker

While in a docs buffer, you can also pick links directly:

- `helplinkpick` (or `helplinkpick QUERY`) — filtered queries can now mix the link label with owning-section terms like `External micro editor` or `Reference Vision ref`

In the TUI, link suggestions are grouped into sections.

- Default: **Docs**, **Files**, and **External** (option: `help.linksections kind`)
- Optional: grouped by the nearest markdown heading (option: `help.linksections heading`)

Picker UX:
- `Up` / `Down` moves the highlighted selection
- `PageUp` / `PageDown` jumps selection by a small window (option: `prompt.page`, default 8)
- `Alt-Up` / `Alt-Down` jumps between section headers
- `Ctrl-y` copies the selected row (for links: copies the target URL/path)
- `Ctrl-Home` / `Ctrl-End` jumps to first/last selection
- Option: `prompt.wrap` controls wrap vs clamp when moving past ends (default: wrap)
- In the minimal TUI, the active section header is repeated as a sticky header when paging through long sections


## Navigator picker

If you just want a single “go to something on this page” picker, use:

- `helpnavpick` (or `helpnavpick QUERY`)

This combines **Headings** and the same link sections used by `helplinkpick` — including `help.linksections heading` when you want links grouped by the nearest heading instead of Docs/Files/External. Status/preview surfaces now reuse those same visible labels too.

Filtered docs-link queries now also reuse that section context, so link searches can mix label text with owning-section terms like `External micro editor` or `Reference Vision ref`. After rev272 they also reuse destination doc titles and destination heading titles, so generic-label searches like `image metadata` or `hidden image metadata anchor` work too.


## Outline picker

Docs pages can also be navigated by headings:

- `helpoutlinepick` (or `helpoutlinepick QUERY`)
- empty-query browse now groups heading rows by their parent heading breadcrumb (`Top`, document title, `Guide › Links`, ...)
- outline preview/status surfaces reuse those same visible breadcrumb labels
- filtered queries now also reuse that breadcrumb context, so `Guide Links` or `Guide Deep dive` can disambiguate repeated headings
- heading queries also reuse the resolved fragment/id for the target heading, so stable-anchor searches like `custom-frag` work through `helpjump`, `helpoutlinepick`, and the heading side of `helpnavpick` too
- scripts/future UIs can read the grouped shape through `ed.help-outline-section-rows`
- `helpjump` (or `helpjump QUERY`) — jump directly to the best-matching heading, including breadcrumb-aware queries like `helpjump Guide Links` and stable-fragment queries like `helpjump custom-frag`

## History register

Micromax now also exposes the local docs trail as a tiny explicit register:

- `helphistory` — prints the current docs target plus the remembered back/forward trail in one count-aware inventory line; when a dormant or replay target no longer resolves, the corresponding row is marked `[... missing]` instead of silently disappearing
- `helpresume` / `ed.help-resume` — reopen the last dormant session-local docs target without consuming `helpback` / `helpforward` history; if the docs page is already active, fail plainly as `helpresume: already active: topic @ line:col`, and if the remembered dormant target no longer resolves, fail as `helpresume: missing doc: TOPIC`
- `helpprune` / `ed.help-prune` — prune only missing session/back/forward docs targets so blocked history stays witnessable until the user explicitly clears the stale head
- `help_history_rows()` / `ed.helphistory-rows` — expose the same ordered `current` / `dormant` / `back` / `forward` rows for scripts and future UIs, now with one tiny trailing state cell (`active`, `ready`, or `missing`)
- the register stays intentionally small and session-local: it is a witness of the current local docs trail, not a persisted browsing log
- ordinary docs opens continue that same local trail even from a dormant current page: opening a different docs topic from outside the help buffer pushes the dormant target onto `helpback`, while diverging dormant forward history clears just like an on-screen branch
- reopening that same dormant docs topic by name now reuses the session-local landing too: if the old help buffer was closed, Micromax restores the remembered cursor target for that same page instead of demoting it to a fresh top-of-file open

## Explicit fragment target {#custom-frag}

Micromax recognizes explicit heading ids in common markdown attribute-list style,
so docs can choose stable fragments without needing a full markdown engine.


[^help-footnote]: This is intentionally tiny, best-effort footnote support for docs/help buffers.
[^help-footnote-more]: This is a tiny multi-line footnote example.
    Indented continuation lines now also read like footnote-body source in the live docs/help TUI.

The browser stays intentionally small and headless-first. Editor-side `help` lookup now also keeps its own surface name visible on direct docs success/miss (`help docs: ...`, `help docs: no such doc: ...`) and on general-topic misses (`help: no such topic: ...`), while `helpback` / `helpforward` / `helpresume` now also keep their own action names visible on stale replay misses instead of collapsing those failures back to generic `help docs:` wording. Current docs-link inspection now stays in that same tiny explicit dialect too: `showhelplink` names the exact link under the cursor when one exists, and fails as `showhelplink: not in a docs buffer` / `showhelplink: no link under cursor` instead of making users infer why `helpfollow` or `helplinkcopy` would fail. Rev402 keeps that same trust-first stance one layer deeper by preserving exact prior docs cursor targets and exposing current/back docs state through stable `help_*` fields; rev403 adds the matching local forward half plus explicit session-only scope; rev404 closes the remaining destination seam by making same-page help jumps/follows part of that same local history so one docs page with multiple meaningful sections stays retraceable without pretending arbitrary cursor motion is persisted history; rev405 adds the matching tiny register surface so the same trail is visible directly through `helphistory` / `ed.helphistory-rows` instead of only through hidden stacks or transient status text; rev406 keeps the current docs target witnessable even after you leave the docs buffer by giving that off-screen state a tiny dormant row plus explicit `helpresume` reopen path instead of collapsing it back into a generic `help -> ...` hint; rev409 adds the matching explicit cleanup path for stale blockers, so blocked missing-doc heads can stay witnessable until the user chooses `helpprune` instead of silently disappearing or trapping the rest of the local trail forever; rev410 keeps ordinary docs opens inside that same local replay loop, so a dormant current page is pushed onto `helpback` before a new docs open overwrites it instead of being silently dropped from the trail; rev411 closes the matching direct-replay seam, so off-screen `helpback` / `helpforward` now also treat that dormant current page as the current branch head and preserve it on the opposite stack instead of silently erasing continuity unless the user `helpresume`s first; and rev412 closes the remaining same-topic reopen seam, so reopening that same dormant docs page by name now restores the exact remembered landing even after the original help buffer was closed instead of silently resetting the session's current page to `1:0`; rev414 closes the matching active-command seam too, so once the same page is already back on-screen `helpresume` / `ed.help-resume` fail explicitly instead of replaying that active page one more time. Rev416 closes one remaining ordinary-open seam too: if `help docs TOPIC`, `help TOPIC`, or a cross-doc `helpfollow` already lands on exactly one adjacent back/forward target, Micromax now reuses that existing replay edge instead of inventing a duplicate branch or clearing deeper forward history just because the destination was named explicitly.
