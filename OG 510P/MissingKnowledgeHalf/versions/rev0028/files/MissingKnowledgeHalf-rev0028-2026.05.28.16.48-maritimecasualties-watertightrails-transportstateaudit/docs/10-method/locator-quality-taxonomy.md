# Locator quality taxonomy

Rev0018 refines locator-debt detection. The cube previously treated any occurrence of `search` inside locator text as weak. That overcounted legitimate words such as `research`. The detector now marks a locator weak when it contains explicit tokens such as:

- `search locator`
- `search result`
- `snippet`
- `not extracted`
- `not yet`
- `dynamic page source-index`
- missing locator arrays

This is a detector improvement, not a source-quality victory. Weak locator debt remains real when a claim relies on search-result or snippet text instead of source line/page/section locators.

Future sessions should record both numbers: detector-refactor reductions and genuine source-acquisition reductions.
