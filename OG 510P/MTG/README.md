# MTG

## Two ways to ask whether a game has been understood

The two supplied projects meet at Magic: The Gathering but examine different questions.

- **[MTGSim](MTGSim/README.md)** asks how a rules engine can preserve the identity of a declared action, its payment and the events that make it valid. Start here if you are interested in rules, state and faithful execution.
- **[MUCloudtainer](MUCloudtainer/README.md)** studies strategy evaluation. Its selected long-game experiment retains an unresolved stopping condition even alongside favorable numerical results. Start here if you are interested in what a bounded experiment can justify.

In MTGSim's return-to-hand example, the interesting object is not just the card that ends up in a hand. The paid-action record binds a payer, the selected object and its prior zone state to the witnessed move and the declared action. That gives a reader somewhere specific to look when the transaction and its account disagree. The supplied revision reports tests and fuzz runs, but the receipt itself is not proof that every card interaction is correct.

MUCloudtainer makes a different kind of uncertainty visible. Its retained counter-control experiment reports 192 games, a mean score above one half and one game still truncated at the higher decision cap. The project leaves the confidence gate open rather than turning that unfinished game into a decisive outcome. Treating a cap as a half-point draw, adopting a formal repetition rule and changing the agent's objective would answer different questions.

A faithful rules event does not establish a winning strategy, and an attractive strategy score does not establish that every rule was modeled correctly. Read the projects together for that distinction; the shared shelf does not claim that the supplied packages are one integrated system.

Each project keeps its own original upload, separately extracted files and historical evidence. The reported results come from the supplied project records; no game or simulation was run for these reading guides.

*Reading orientation by Lumen, 8 October 2026; expanded 5 November 2026.*

[Catalog](../../CATALOG.md) · [OG 510P](../README.md)
