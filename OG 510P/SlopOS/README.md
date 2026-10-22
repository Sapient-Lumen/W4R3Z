# SlopOS

**A different kind of computer: powerful tools, explicit permissions, and interfaces that let people see what their actions would mean.**

SlopOS begins with a demanding question: can a system remain convenient without allowing convenience to quietly grant authority? A command name should not acquire access merely because it can be typed. Restoring a workspace should not silently renew permission to contact somebody. A polished display should not turn a remembered event into a current fact. These are not only kernel questions. They change the design of the desktop, shell, filesystem, browser crossings, service manager and recovery process.

The collection follows that question through ten primary editions and seven companion projects. Its early horizon is a capability-oriented operating system with workstation, cloud, appliance and agent-facing profiles. Its companions imagine how that system could feel to use. Later primary editions build a narrower C++ laboratory around the difficult transition from a justified proposal to one precisely bounded effect. Read those later experiments beside the earlier designs, not as a reason to discard their larger imagination.

[Read the primary architecture and development](PRIMARY.md) · [All 29 original downloads](DOWNLOADS.md) · [Collection provenance](PROVENANCE.md)

## Seven ways into the imagined machine

Each companion has its own center of gravity and development history. These are related works, not seven names for one mechanism or evidence of a completed integrated operating system.

| Work | The problem it makes tangible |
|---|---|
| [Helm](companions/Helm.md) | A desktop where windows, objects, proposed actions and workspace restoration share an inspectable spatial language. Rehearsal cards and quarantine ribbons help distinguish what can be seen from what may be done. |
| [Schell](companions/Schell.md) | Command work as an intelligible episode: proposal, review, decision, result and remembered transcript. Its paper interface cards ask how a terminal can remain truthful when useful structure and plain text must coexist. |
| [ViewFS](companions/ViewFS.md) | Objects and explicit views instead of a pathname being an ambient permission. Its shell designs make parsing, unresolved state and receipt history part of navigation rather than hidden implementation trivia. |
| [Foundry](companions/Foundry.md) | Foreign runtimes and exported representations that do not pretend restored state is fresh authority or that a simplified projection preserves every meaning of its source. This is the SlopOS companion, distinct from W4R3Z's FOUNDRY shelf. |
| [Harbor](companions/Harbor.md) | Crossing between local work and outside/browser-mediated activity while keeping callback, adoption, correction and human response distinct. A returned message is not automatically an accepted result. |
| [Steward](companions/Steward.md) | Service lifecycle and repair made inspectable: when to restart, what a dependency actually permits, and why a stale cycle or an unapproved activation must not quietly become current work. |
| [Ward](companions/Ward.md) | Trust appraisal, quarantine and governance receipts without treating favorable evidence as a power to clear every restriction. It asks what a particular decision establishes, for which subject, and under whose authority. |

## A concrete reading scene

Imagine reopening a workspace containing a document, a foreign application and an unfinished network action. The easy interface answer is to put everything back as it was. SlopOS's more interesting answer asks what “as it was” means.

Helm can restore the arrangement without pretending every action is live. Foundry can distinguish a restored runtime from freshly justified access. ViewFS can expose the document through a selected view rather than giving the application the surrounding host filesystem. Schell can retain the interrupted episode without turning its transcript into permission to repeat it. Harbor can distinguish a callback from adoption. Steward can make restart conditions explicit, and Ward can preserve an outstanding restriction while considering new evidence.

That scene is a way to read the designs together, not a claim that these archives already execute it end to end. Their shared artistic achievement is to make subtle differences inhabitable: a ribbon, card, lane, ghost or diagnostic gutter can express a difference that would otherwise disappear inside a green status light. Their technical work asks which exact fields, state transitions and checks would make those distinctions more than decoration.

## Follow the question that interests you

- **How should a computer feel?** Begin with Helm, Schell and ViewFS. Read their examples as interaction design, not merely specifications awaiting a product verdict.
- **How should work survive interruption?** Follow Foundry, Steward and the primary's later claim-and-effect experiments. Restoration, continuation and renewed permission are different problems.
- **What does evidence permit?** Read Harbor and Ward, then the primary's distinction between a copyable winner value and a consumed action right.
- **What actually exists in source?** The [primary account](PRIMARY.md) distinguishes early Python artifact tools, later C++ state machinery and the Linux filesystem canary. Companion pages identify their own executable validators and models.

The original archives carry much more than the selected passages available for direct browsing here. Use the [download index](DOWNLOADS.md) for complete editions, including source, development histories, fixtures and original notices. Related perspectives elsewhere in W4R3Z include [DeriveBSD](../DeriveBSD/README.md), [Monsternix](../../guides/Monsternix.md) and [EvidenceVault](../EvidenceVault/README.md): different answers to how a system's claims remain connected to what it can actually do.
