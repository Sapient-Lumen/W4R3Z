# ProgRSS: keep the sources, keep the reasons

ProgRSS is a local-first reader for feeds and meaningful changes on web pages. Its larger idea is that a useful reading collection is more than a list of addresses. It also contains choices: which sources belong together, what counts as a meaningful change, why a particular source belongs in a particular folder, and what a recipient should be able to keep or change when that collection is shared.

A neighborhood group could assemble council announcements, local reporting and watched public-notice pages into one collection. A researcher could maintain separate topic folders that reuse some of the same sources. A curator could give someone a complete reading route or just one branch without giving away a private reading history. These are concrete uses of mechanisms present in the source, not a claim that those deployments or user studies have happened.

The current Foundry artifact is the rev0106 Relay workspace Source Note integrity Roadcase. It contains the Chromium and Firefox extension trees, the Python CLI and local Node, fixtures, contracts and release evidence. Its retained product version is 0.80.0, while the current candidate revision is rev0106. That distinction matters: the archive is a continuing whole-product source package, not a claim that every historical release description is the latest authority.

**Current rev0106 / Roadcase:** [Whole-product ZIP](https://github.com/Sapient-Lumen/W4R3Z/releases/download/ProgRSS-rev0106/ProgRSS-rev0106-relay-workspace-source-note-integrity-2026.10.22-Roadcase.zip) · [Matching bootstrap](https://github.com/Sapient-Lumen/W4R3Z/releases/download/ProgRSS-rev0106/BOOTSTRAPROSE.md) · [Read the bootstrap](BOOTSTRAPROSE.md) · [Release](https://github.com/Sapient-Lumen/W4R3Z/releases/tag/ProgRSS-rev0106)

## Reading without losing the route

The ordinary browser interface is organized around Today, Sources and Add. Advanced Workbench sits behind that everyday reading surface. The reader implementation parses RSS, Atom and JSON Feed, preserves language information, extracts bounded readable content, and supports watched-page changes alongside feeds.

Its collection machinery can do more than concatenate subscriptions. The implementation supports union, intersection and subtraction, with filters and provenance paths explaining which sources and collections contributed an item. If a relevant item arrives through several sources, the composition logic retains witnesses rather than treating the newest duplicate as the only explanation. This makes the advanced machinery useful for deliberate research collections while leaving ordinary folders available for simpler reading.

A Source Note supplies a different kind of explanation: a short curator-written reason for one direct folder-to-source relationship. It is not a global rating of the source. The same council feed might belong in a “Local decisions” folder because it carries meeting agendas and in a “Housing” folder because it carries planning decisions. Those two reasons can coexist, and a third placement can have no reason at all.

The native representation bounds each reason to 280 Unicode code points, supports multiline text and Unicode, and distinguishes a missing reason from malformed stored data. The reasons are curator context, not a ProgRSS assurance that a source is trustworthy or safe.

## Share a collection, not an unexamined transfer of authority

ProgRSS separates several actions that are easy to blur together. Sharing a folder produces a portable artifact. Generating a publication package produces a ready-to-host static website ZIP; it does not itself upload the website. Importing a shared collection produces a new local copy. Checking a configured publication address is a deliberate network action that reviews a later copy without applying it.

The Relay CLI makes those distinctions concrete. Its import path writes a new workspace backup instead of overwriting the input, reuses eligible existing sources, and starts newly adopted sources paused. The publication-check path reports whether it saved a verified copy and explicitly records that it did not apply changes. Selecting a branch as an independent excerpt need not retain the parent publication's future-update relationship.

Later copies are not simply allowed to replace local work. The Source Notes reconciliation contract compares the previously received base, the recipient's current text and the curator's newer text. If only one side changed, that change can be retained. If both sides changed differently, the conflict remains unresolved until the recipient chooses which wording to keep. The product includes review and disclosure surfaces for these route-specific reasons rather than treating them as invisible metadata.

Portability also has limits worth saying aloud. ProgRSS's native JSON can preserve Source Notes and page-watch information that ordinary OPML does not represent. OPML export deliberately omits these ProgRSS-specific meanings and reports the omission, rather than inventing a private extension and implying universal interoperability.

## When a website has no useful feed

For a page that must be viewed in a browser, Capture provides a deliberate, bounded observation path. The person reviews an exact active page and the section being captured. The design keeps browser cookies and credentials in the browser and sends bounded text, links and evidence to the Node, not the browser session itself.

The source and accompanying contracts distinguish section structure from page coverage. A selected section may appear steady while the visible page is only part of a paginated or virtualized list. ProgRSS records that distinction so a changing rendered window need not be mistaken for a mass deletion and replacement of the underlying material.

The continuity implementation compares partial observations with the accepted baseline. When the partial-render boundary changes, or sufficiently populated observations have too little overlap, it can hold the new observation and preserve the earlier baseline instead of generating a mass-change alert. Separate review tools explain the observations and allow a deliberate baseline-replacement decision. These are conservative mechanisms, not proof that the whole page was captured or that a selector will remain reliable forever.

Scheduling is another separate boundary. The documented Node scheduling path requires successful Node-reproducible acquisition evidence; a browser-assisted observation does not silently become permission to run a signed-in browser unattended. Extension pairing is described as a bounded, read-only summary relationship, not a general write-through connection to the Node.

## What rev0106 changes

The current change concerns the private workspace files that Relay reads and writes. The supplied before-and-after evidence records an earlier loader accepting an over-limit placement reason and carrying it into a newly written backup. That matters even for a small text field: if one import or export path preserves malformed state, the product's promise that the same relationship has the same meaning across surfaces becomes unreliable.

rev0106 places the shared direct-placement validator at two boundaries in the actual source. The Relay workspace loader audits the private state before the commands use it. The workspace writer audits the derived state again before making a new backup. This is a targeted consistency correction, not a new sharing service or a new browser permission.

The common loader is used by six operations: share-folder, publish-folder, import-bundle, review-bundle, check-publication and update-bundle. It rejects malformed reason placement and invalid reason values instead of quietly repairing stored data. Valid reasons are preserved without rewriting. In the explicit publication-check path, the loader runs before the publication fetch, so rejected private state does not reach that network step.

There is an important distinction between authoring and transfer here. An authoring helper can trim an input or turn an empty entry into absence. A private-state integrity check should not silently change an already stored record while pretending to preserve it. The new boundary rejects noncanonical stored values and leaves the person with a refusal rather than an altered backup.

## Read the current workshop

Begin with the matching bootstrap and root product documents, then follow the ordinary Reader, local Node and Relay workflows before exploring the advanced Workbench. `CLI/relay.py` contains the current read/write boundary; `source_notes_contract/` defines the shared placement semantics. The source, fixtures, explanations and retained negative results travel together in the Roadcase, so a recipient can develop a different continuation rather than receive only an installed extension.

The supplied regression records distinguish nine malformed forms exercised through import from one over-limit form exercised across all six command paths. They do not establish a fully executed nine-by-six matrix. Exact-host Chromium Stable, Firefox Release/ESR, unfamiliar-person and assistive-technology acceptance remain open in the current bootstrap. Remote Nodes and the bounded WebRTC courier are future directions, not already accepted ordinary workflows.

What is present is a broad local reading and sharing implementation with deliberate distinctions between collecting, explaining, reviewing, transferring and scheduling. rev0106 strengthens one of those distinctions: a reason attached to a source's place in a folder should survive a valid transfer exactly, and malformed private state should stop at the boundary rather than travel forward as if nothing happened.

## Exact current pair

- Whole-product ZIP: 29,275,335 bytes; SHA-256 `1ffa1437576d4bf355b2ecf027dbe419378bd0645a87c481be5f9508dea91f19`.
- `BOOTSTRAPROSE.md`: 5,945 bytes; SHA-256 `9a3b5657934491e9ac8ffa2e65fb143d6a31e724cce4f3b461503b590bce5825`.

The supplied bytes remain unchanged. Static intake matched all 1,840 manifest-listed payload records, including sizes, kinds and modes. Runtime receipts remain the supplied project's evidence. Original attribution and notices stay with the work; the [external owner declaration](../../LEGAL-NOTICE.txt) does not replace third-party terms.

## Changelog

- **Received 2026-10-22 · rev0106 / Roadcase** — Relay validates route-specific Source Notes before using a private workspace and before writing its successor, preserving valid reasons without rewriting malformed state.

[Foundry](../README.md) · [Catalog](../../CATALOG.md) · [W4R3Z](../../README.md)
