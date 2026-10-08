# Scenario — nightly rustdoc doctest JSON and Markdown fallback are not the same extraction basis

This scenario models two ways of building a docs-example inventory:
- one comes directly from `rustdoc -Zunstable-options --output-format=doctest`, with an explicit `format_version`, rewritten wrapper text, and computed doctest attributes;
- the other comes from a fallback Markdown/code-block scrape used only because that nightly output was unavailable.

The point of the receipt is to keep the support claim honest:
- both inventories may enumerate similar-looking examples,
- but they do not have the same authority,
- and downstream line/wrapper/attribute claims should not pretend otherwise.
