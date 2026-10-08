# Rematch Worlds Need Cap-Robust Preference Certificates

Once a rematch archive has reduced the live choice to two anchors, it is not enough to publish a preference inequality at a couple of sampled hazard caps.

The inheritor needs to know a sharper fact: when is the declared additional-budget cap still capable of reversing the final choice, and when is the winner already robust to every admissible cap in the published policy box?

For the current family `10/20/50/100` rematch proxy, the earlier endpoint-only view was too weak. Comparing caps `10` and `10000` missed the true worst case for stability.

The most stability-favoring hazard term is still at cap `10`, but the most material-favoring hazard term occurs at cap `20`, not at the asymptotic tail.

That changes the handoff contract.

The archive should therefore publish:
- one baseline non-hazard surplus expression,
- one exact all-caps ambiguity strip where cap declaration can still flip the winner,
- and two cap-robust certificates outside that strip.

In the current proxy, the true all-caps strip is materially wider than the endpoint-only strip. So an inheritor who checks only the asymptotic tail can falsely certify stability or falsely certify material even though an interior cap still overturns the verdict.

That is the durable lesson worth keeping: once cap enters the final preference rule, robustness has to be certified against the full allowed cap range, not against a low-end sample and a tail sample.
