# Rev291 — exact show-impact commands for slices and facets

## What landed

`mxportable --stdlib-manifest --show-impact` already knew how to expose:

- the current impacted slice,
- exact retest commands for that slice,
- valid next filter facets, and
- exact facet flag fragments like `--impact-word finally`.

Rev291 keeps the same tiny path, but removes one more reconstruction step.

Selected impact slices now carry:

- `selected_words`
- `selected_word_count`
- `show_impact_env`
- `show_impact_argv`
- `show_impact_json_argv`
- `show_impact_command`
- `show_impact_json_command`

And every `impact_filter_options` row now carries the same exact full-command
metadata for the slice you would get by choosing that facet.

## Why this is useful

Rev290 made the valid next facets executable as raw flag fragments, but a human
or future LLM still had to rebuild the surrounding command by hand:

- `--stdlib-manifest`
- the selected boot word roots
- `--show-impact`
- any already-active orthogonal filters
- and then the new facet flag

That was still a lossy handoff.

Now the tool can say both:

- “this is the exact slice you are looking at right now”
- “this is the exact command for the next facet cut”

without adding a scheduler, a persistent workflow layer, or a second dependency
model.

## Important detail

Facet commands are rebuilt with the right family semantics instead of blindly
appending flags.

That matters because some filter families are union-like:

- `--impact-word`
- `--impact-distance`
- `--impact-category`
- `--impact-name`

So choosing one visible facet row replaces that family with the exact selected
row instead of accidentally keeping a broader union alive.

For conjunctive tag filtering, the current tag slice is preserved and the chosen
facet tag is added if needed.

So an `errors` slice can still offer a direct exact command for the narrower
`errors + cleanup` slice.

## Example

For:

```text
PYTHONPATH=src python tools/mxportable.py --stdlib-manifest --word ensure --show-impact --impact-tag errors
```

JSON now carries both the current slice command and the exact next-cut commands.
For example:

```json
{
  "show_impact_command": "PYTHONPATH=src python tools/mxportable.py --stdlib-manifest --word ensure --show-impact --impact-tag errors"
}
```

And one visible tag facet can now carry:

```json
{
  "name": "cleanup",
  "filter_suffix": "--impact-tag cleanup",
  "show_impact_command": "PYTHONPATH=src python tools/mxportable.py --stdlib-manifest --word ensure --show-impact --impact-tag errors --impact-tag cleanup"
}
```

For a union-style facet like one exact impacted word, the command stays exact
instead of preserving the broader union:

```json
{
  "name": "finally",
  "filter_suffix": "--impact-word finally",
  "show_impact_command": "PYTHONPATH=src python tools/mxportable.py --stdlib-manifest --word ensure --show-impact --impact-word finally"
}
```

## Files touched

- `src/micromax/portability_suite.py`
- `tools/mxportable.py`
- `tests/test_portability_suite.py`
- `tests/test_mxcontext.py`

## Practical consequence

Future humans and future LLMs can now move directly from:

- “show me this impacted slice”
- to “show me the exact next refinement command”

without reconstructing the surrounding CLI around a facet fragment.
