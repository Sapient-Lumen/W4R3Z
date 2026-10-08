# Published support surface

`python scripts/published-support-surface.py --pretty` freezes the **citable** support surface separately from the broader support queue.

## Why this exists

`docs/support-records/*.md` and `docs/support-bundles/*/*.json` answer different questions:

- support records say what GlassTTY currently believes about `surface × workflow × lane`
- the support-bundle queue says what named evidence is being reviewed, held, or prepared
- the **published support surface** says what is actually safe to cite as current published support evidence

That split matters because GlassTTY should not treat `candidate`, `hold`, or even `published-ready` bundles as already citable support truth.

## Commands

```bash
python scripts/published-support-surface.py --pretty
python scripts/published-support-surface.py capture --output-dir validation/latest/published-support-surface
python scripts/published-support-surface.py history --pretty
python scripts/published-support-surface.py write-root
python scripts/support-bundle-transition.py --bundle <bundle-key> --to-state <candidate|hold|published-ready|published>
```

## Outputs

The report includes:

- publication posture per surface (`none`, `candidate`, `hold`, `published-ready`, `published`)
- whether the surface is citable **now**
- the current published / published-ready / held / candidate bundle keys
- warnings when support-record strength outruns published bundle availability

## Working rule

A stronger support story can exist in records or held bundles before it becomes citable public truth. Keep those two surfaces separate.


## Relation to the publish gate

The published-support surface is descriptive: it says what is citable now.
The support publish gate is normative: it says whether a bundle may honestly move into stronger publication state at all.

That split keeps queue review, gate review, and current citable truth from collapsing into one folder-state story.
