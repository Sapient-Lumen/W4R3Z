# 681 — Release safe-extractor lexical output-path canonicality firewall

**Track:** Shared / Release engineering

This document records a v806 release hardening pass. It is a maintainer-control document, not a new voter-facing evidence surface.

## Audit finding

v799 and v800 made the verifier-backed safe extractor reject symlinked output ancestry and reject unsafe output targets before creating parent directories. The intent was also to reject lexical `.` and `..` output components before resolving the operator-supplied path.

The implementation used `pathlib.Path(...).parts` for that lexical check. On Python, `Path` construction normalizes away current-directory components such as `./` before `.parts` is inspected. That meant an output path such as:

```bash
/tmp/release-output/./tree
```

could be accepted as though the operator had supplied `/tmp/release-output/tree`. The resulting extracted tree could still be byte-valid, but the extractor had failed to enforce the promised canonical publication route.

The same audit also identified two adjacent publication-target shapes that should be rejected before any parent-directory creation:

- empty separator components, such as `out//tree`;
- filesystem roots, such as `/`, especially when paired with `--clean`.

## Reconstruction rule

The safe extractor must inspect the raw operator-supplied output string before constructing a `Path` object that can normalize it. A verifier-backed publication target is canonical only when it has:

1. a non-empty path string;
2. no NUL byte;
3. no filesystem-root-only target;
4. no empty separator component, except the single leading separator of an absolute path;
5. no lexical `.` component;
6. no lexical `..` component;
7. no platform alternate separator; and
8. no existing symlink component in the audited ancestry.

This rule is stricter than a generic filesystem path parser because this extractor is the official recipient reconstruction path. The route named by the operator should be the route that is audited and published.

## Enforcement surfaces

v806 refactors `scripts/extract_release_zip.py` so `_output_path_component_problems()` first calls a raw-string lexical policy before creating a normalized `Path`. Only after that raw policy passes does the extractor inspect existing ancestry for symlink components.

The same helper remains used in both preflight and just before final publication, preserving the two-phase check added earlier.

v806 also extends `scripts/check_release_safe_extractor.py` with negative probes for:

- lexical current-directory components such as `component/./out`;
- empty separator components such as `component//out`;
- filesystem-root output targets.

The probes require rejection before parent creation, so the extractor cannot normalize an invalid output route and leave local directories behind.

## Operator effect

Preferred recipient workflow remains:

```bash
python3 scripts/verify_release_zip.py The-Election-Stack-revNNNN.zip
python3 scripts/extract_release_zip.py The-Election-Stack-revNNNN.zip ./election-stack-vNNNN
python3 scripts/verify_manifest.py ./election-stack-vNNNN
```

Choose a direct output path without `.` components, `..` components, doubled separators, symlinked ancestry, or root-directory targets. If replacing an existing non-empty output directory, use `--clean` only with an ordinary, deliberate directory path.

## Non-claims

This does not sandbox extraction, prevent privileged local interference, audit mount namespaces, or make external unzip tools safe. It narrows the shipped safe extractor so it does not hide non-canonical operator output paths behind Python path normalization.

## Compression posture

This revision adds one compact release-engineering document and extends an existing stdlib smoke check. It does not add schemas, registries, external-source bodies, voter-facing public-answer surfaces, or new election-process claims.

## Internal anchors

- `docs/162-release-and-ci-evidence-pipeline.md`
- `docs/668-release-safe-extractor-verified-two-phase-unpack-and-tree-recheck.md`
- `docs/674-release-safe-extractor-output-ancestry-firewall.md`
- `docs/675-release-safe-extractor-side-effect-free-output-preflight.md`
- `scripts/extract_release_zip.py`
- `scripts/check_release_safe_extractor.py`
