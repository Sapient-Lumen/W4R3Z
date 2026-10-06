import pathlib


def ensure_needles(*args):
    # Backward-compatible forms:
    # 1) ensure_needles(path: pathlib.Path, needles: list[str])
    # 2) ensure_needles(root: pathlib.Path, name: str, mapping: dict[str, list[str]])
    if len(args) == 2 and isinstance(args[0], pathlib.Path):
        path, needles = args
        text = path.read_text(encoding="utf-8")
        missing = [needle for needle in needles if needle not in text]
        if missing:
            raise SystemExit(f"{path.name} missing required text: {missing}")
        return
    if len(args) == 3 and isinstance(args[0], pathlib.Path) and isinstance(args[1], str) and isinstance(args[2], dict):
        root, name, mapping = args
        for rel, needles in mapping.items():
            path = root / rel
            text = path.read_text(encoding="utf-8")
            missing = [needle for needle in needles if needle not in text]
            if missing:
                raise SystemExit(f"{name}: {rel} missing required text: {missing}")
        return
    raise TypeError("ensure_needles() expected (path, needles) or (root, name, mapping)")


EXCLUDED_GPUSTORMING_CONTRACTS = {"check_gpustorming_contract.py", "check_gpustorming_crosswalk_contract.py"}

GPUSTORMING_FAMILY_SPECS = [
    {"family": "boundary", "segment": "boundary", "group": "Local-form and protocol controls"},
    {"family": "wrapper", "segment": "wrapper", "group": "Local-form and protocol controls"},
    {"family": "neighborhood", "segment": "neighborhood", "group": "Local-form and protocol controls"},
    {"family": "history", "segment": "history", "group": "Local-form and protocol controls"},
    {"family": "replicate", "segment": "replicate", "group": "Local-form and protocol controls"},
    {"family": "channel", "segment": "channel", "group": "Local-form and protocol controls"},
    {"family": "eval", "segment": "eval", "group": "Local-form and protocol controls"},
    {"family": "script", "segment": "script", "group": "Framing and authority controls"},
    {"family": "provenance", "segment": "prestige", "group": "Framing and authority controls"},
    {"family": "persona", "segment": "persona", "group": "Framing and authority controls"},
    {"family": "pragmatic", "segment": "pragmatic", "group": "Framing and authority controls"},
    {"family": "rubric", "segment": "rubric", "group": "Framing and authority controls"},
    {"family": "scoreframe", "segment": "scoreframe", "group": "Framing and authority controls"},
    {"family": "entanglement", "segment": "entanglement", "group": "Framing and authority controls"},
    {"family": "polarity", "segment": "polarity", "group": "Framing and authority controls"},
    {"family": "expectation", "segment": "expectation", "group": "Framing and authority controls"},
    {"family": "agreement", "segment": "agreement", "group": "Framing and authority controls"},
    {"family": "consensus", "segment": "consensus", "group": "Framing and authority controls"},
    {"family": "overlap", "segment": "overlap", "group": "Framing and authority controls"},
    {"family": "formatting", "segment": "formatting", "group": "Framing and authority controls"},
    {"family": "verbosity", "segment": "verbosity", "group": "Framing and authority controls"},
    {"family": "novelty", "segment": "novelty", "group": "Framing and authority controls"},
    {"family": "freshness", "segment": "freshness", "group": "Evidence and surface controls"},
    {"family": "statusproof", "segment": "status-wrapper", "group": "Evidence and surface controls"},
    {"family": "preview", "segment": "preview", "group": "Evidence and surface controls"},
    {"family": "carrierslot", "segment": "carrier-slot", "group": "Evidence and surface controls"},
    {"family": "derivative", "segment": "derivative-source", "group": "Evidence and surface controls"},
    {"family": "prefill", "segment": "prefill", "group": "Evidence and surface controls"},
    {"family": "queryframe", "segment": "query-frame", "group": "Evidence and surface controls"},
    {"family": "facetframe", "segment": "facet-frame", "group": "Evidence and surface controls"},
    {"family": "rankframe", "segment": "rank-frame", "group": "Evidence and surface controls"},
    {"family": "reasonframe", "segment": "reason-frame", "group": "Evidence and surface controls"},
    {"family": "citationframe", "segment": "citation-frame", "group": "Evidence and surface controls"},
    {"family": "warningframe", "segment": "warning-frame", "group": "Evidence and surface controls"},
    {"family": "stanceframe", "segment": "stance-frame", "group": "Evidence and surface controls"},
    {"family": "excerptframe", "segment": "excerpt-frame", "group": "Evidence and surface controls"},
    {"family": "sourcecluster", "segment": "source-cluster", "group": "Evidence and surface controls"},
    {"family": "schemaslot", "segment": "schema-slot", "group": "Contract and semantics controls"},
    {"family": "claimlabel", "segment": "claim-equivalence", "group": "Contract and semantics controls"},
    {"family": "scopenarrow", "segment": "scope-narrowing", "group": "Contract and semantics controls"},
    {"family": "claimceiling", "segment": "claim-ceiling", "group": "Contract and semantics controls"},
]

CANONICAL_GPUSTORMING_FAMILY_ORDER = [spec["family"] for spec in GPUSTORMING_FAMILY_SPECS]
FAMILY_TRAJECTORY_SEGMENTS = {spec["family"]: spec["segment"] for spec in GPUSTORMING_FAMILY_SPECS}
FAMILY_GROUPS = {spec["family"]: spec["group"] for spec in GPUSTORMING_FAMILY_SPECS}
FAMILY_SPECS_BY_FAMILY = {spec["family"]: spec for spec in GPUSTORMING_FAMILY_SPECS}


def family_spec_for(family: str) -> dict:
    try:
        return FAMILY_SPECS_BY_FAMILY[family]
    except KeyError as exc:
        raise KeyError(f"unknown gpustorming family: {family}") from exc


def grouped_family_specs():
    groups = []
    seen = {}
    for spec in GPUSTORMING_FAMILY_SPECS:
        title = spec["group"]
        if title not in seen:
            seen[title] = []
            groups.append((title, seen[title]))
        seen[title].append(spec)
    return groups


def canonical_group_titles():
    return [title for title, _ in grouped_family_specs()]


def grouped_family_entries():
    entries = []
    for title, specs in grouped_family_specs():
        entries.append((title, [(spec["family"], family_bullet_needle(spec["family"])) for spec in specs]))
    return entries


def group_section_text(text: str, title: str) -> str:
    heading = f"### {title}"
    start = text.find(heading)
    if start == -1:
        raise KeyError(f"missing group heading for {title}")
    next_positions = [
        text.find(f"### {other}", start + 1)
        for other in canonical_group_titles()
        if text.find(f"### {other}", start + 1) != -1
    ]
    end = min(next_positions) if next_positions else len(text)
    return text[start:end]


def families_for_group(title: str) -> list[str]:
    return [spec["family"] for spec in GPUSTORMING_FAMILY_SPECS if spec["group"] == title]


def group_title_for_family(family: str) -> str:
    return family_spec_for(family)["group"]


def trajectory_problem_phrase(family: str) -> str:
    segments = []
    for slug in CANONICAL_GPUSTORMING_FAMILY_ORDER:
        if slug == family:
            segment = FAMILY_TRAJECTORY_SEGMENTS.get(slug, slug)
            return "family plus placement/density/" + "/".join([*segments, segment]) + " problem"
        segments.append(FAMILY_TRAJECTORY_SEGMENTS.get(slug, slug))
    raise KeyError(f"unknown gpustorming family: {family}")




def family_slice_for_group(title: str) -> list[str]:
    return families_for_group(title)


def family_bullets_for_group(title: str) -> list[str]:
    return [family_bullet_needle(family) for family in families_for_group(title)]

def family_slug_from_contract_path(path: pathlib.Path) -> str:
    name = path.name
    slug = name.removeprefix("check_").removesuffix("_contract.py")
    if slug.startswith("gpustorming_"):
        slug = slug[len("gpustorming_"):]
    return slug.replace("_", "-")


def family_bullet_needle(family: str) -> str:
    return f"- **{family}**"


def discover_gpustorming_contract_files(root: pathlib.Path) -> list[pathlib.Path]:
    discovered = {
        family_slug_from_contract_path(path): path
        for path in (root / "tools").glob("check_gpustorming*_contract.py")
        if path.name not in EXCLUDED_GPUSTORMING_CONTRACTS
    }
    ordered = []
    for family in CANONICAL_GPUSTORMING_FAMILY_ORDER:
        path = discovered.pop(family, None)
        if path is not None:
            ordered.append(path)
    ordered.extend(path for _, path in sorted(discovered.items()))
    return ordered


def discover_gpustorming_families(root: pathlib.Path) -> list[str]:
    return [family_slug_from_contract_path(path) for path in discover_gpustorming_contract_files(root)]


def build_gpustorming_toolchain(root: pathlib.Path) -> list[str]:
    return [
        "check_gpustorming_contract.py",
        *[path.name for path in discover_gpustorming_contract_files(root)],
        "check_gpustorming_crosswalk_contract.py",
    ]


def default_trajectory_intro(family: str) -> str:
    return f"A parallel {family} extension"


def standard_family_contract_map(*, family: str, operator_variant: str, privileges: list[str], crosswalk_text: str, trajectory_intro: str | None = None, oq_variant: str, prompt_variant: str, runbook_variant: str, quarantine_id: str, quarantine_text: str, changelog_text: str, archive_index_text: str) -> dict[str, list[str]]:
    if trajectory_intro is None:
        trajectory_intro = default_trajectory_intro(family)
    return {
        "docs/10-method/operator-tokens-and-bootstrap-grammar.md": [operator_variant, *privileges],
        "docs/10-method/alias-packets-handle-collision-budgets-and-namespace-hygiene.md": [operator_variant, *privileges],
        "docs/10-method/gpustorming-control-family-crosswalk-and-sync-guards.md": [f"- **{family}**", crosswalk_text],
        "docs/00-meta/trajectory-map.md": [trajectory_intro, *privileges, trajectory_problem_phrase(family)],
        "docs/20-constitution/open-question-registry.md": [oq_variant, *privileges],
        "docs/50-promptcraft/prompt-pairs.md": [prompt_variant, *privileges],
        "docs/00-meta/llm-runbook.md": [runbook_variant, *privileges],
        "docs/90-quarantine/wild-speculations-2026-03-08.md": [quarantine_id, quarantine_text],
        "CHANGELOG.md": [changelog_text, f"check_gpustorming_{family}_contract.py"],
        "ARCHIVE_INDEX.md": [archive_index_text],
    }
