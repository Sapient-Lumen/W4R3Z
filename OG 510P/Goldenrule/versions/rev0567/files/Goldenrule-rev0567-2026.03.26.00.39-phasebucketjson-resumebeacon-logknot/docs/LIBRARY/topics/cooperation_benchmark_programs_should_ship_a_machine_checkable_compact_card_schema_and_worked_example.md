# Cooperation benchmark programs should ship a machine-checkable compact card schema and worked example

A compact cooperation benchmark card becomes much more useful once future inheritors can **instantiate it as one fixed object** instead of repeatedly translating prose from papers, dashboards, or notebooks into archive-specific judgment calls.

Three standing sources support that move:

- `RS-GR-111` says BenchmarkCards standardize benchmark attributes such as objectives, methodologies, data sources, and limitations, which is exactly the kind of structure a durable cooperation card needs.
- `RS-GR-112` says many benchmarks still do not make their results easy to replicate, which means “the card exists in prose somewhere” is weaker than one compact checked artifact.
- `RS-GR-113` says documentation should be comparable by following a discrete, well-defined format in process, content, and presentation, which points directly toward a small machine-checkable schema plus a worked example.

So the archive should not stop at prose guidance about what a cooperation card ought to contain.
It should also ship one **machine-checkable compact card schema** and one **worked example** that future inheritors can copy, validate, diff, and keep small.

The artifact should stay narrow:

1. one compact JSON object for the card itself;
2. explicit `not applicable` strings instead of silent omission for sections that do not apply in one lane;
3. no bulky sidecars when one short field can state the contract;
4. one worked example kept in `examples/snapshots/` so future sessions can see the intended shape immediately.

This is an implementation move, not a call to widen the archive.
A schema and one small example make the existing card disciplines easier to apply **without adding bulky benchmark-specific payloads**.
