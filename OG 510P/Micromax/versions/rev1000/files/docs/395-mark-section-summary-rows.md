# Mark section summary rows

Micromax already had the important mark-inspection scales before rev453:

- `marks` exposed a tiny flat active/here/preview-aware inventory for humans
- `mark_inventory_rows()` / `ed.mark-inventory-rows` exposed that same ordered register to scripts and future UIs
- `showmark NAME` / `mark_detail_row(NAME)` / `ed.mark-detail-row` exposed one exact named mark without mutating state
- `markpick [QUERY]` / `ed.mark-section-rows` exposed grouped browse state by owning buffer

But one small seam still lingered under that model: broad mark state was stronger at flat full inventory, exact single-mark detail, and full grouped picker rows than at the simpler first question future humans/LLMs often ask first:

> what broad mark buckets are visible right now, and roughly what lives in each one?

That sounds small, but it matters for trust and flow. Without one official tiny summary surface, scripts and future UIs have to reopen `markpick`, walk every grouped row, or scrape counts back out of human command text just to answer that first-stop question.

Rev453 keeps the fix deliberately small.

## What landed

- add `mark_section_summary_rows(QUERY)` on the editor
- add hostcall `ed.mark-section-summary-rows`
- add convenience word `mark-section-summaries`
- add plain `showmarkgroups [QUERY]`
- keep the shared row shape aligned with the newer broad-summary surfaces:

```text
[label count sample_name sample_detail]
```

## Example shape

For marks like:

- `here` in buffer `alpha` previewing `target`
- `there` in buffer `beta` previewing `other`

The shared summary rows look like:

```text
[
  ["beta"  1 "there" "other"]
  ["alpha" 1 "here"  "target"]
]
```

That row shape intentionally stays tiny:

- `label` is the owning-buffer bucket already used by grouped `markpick`
- `count` is how many visible mark rows live there
- `sample_name` reuses the first visible mark name from that bucket
- `sample_detail` reuses the preview/detail field from that same first row

Full grouped browse state still belongs to `markpick` / `ed.mark-section-rows`, and exact one-mark inspection still belongs to `showmark NAME` / `ed.mark-detail-row`.

## Human command path

Humans get the same first-stop summary through:

```text
showmarkgroups [QUERY]
```

Examples:

```text
showmarkgroups
showmarkgroups target
showmarkgroups zzz-no-such-mark
```

Example output:

```text
showmarkgroups target: 1 section(s), 1 mark(s)
alpha: 1 (e.g. here — target)
```

And the miss case stays explicit and boring:

```text
showmarkgroups zzz-no-such-mark: 0 section(s), 0 mark(s)
```

## Why this matters

Marks already had a clean three-scale loop for flat inventory, exact detail, and grouped browse state, but they still lacked the tiny broad summary sibling many of Micromax's newer inspectable surfaces already have. `showmarkgroups [QUERY]` and `ed.mark-section-summary-rows` close that gap without adding new navigation behavior or new hidden state. They just make broad mark buckets honest and inspectable.
