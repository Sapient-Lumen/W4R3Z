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


EXCLUDED_GPUSTORMING_CONTRACTS = {"check_gpustorming_contract.py", "check_gpustorming_crosswalk_contract.py", "check_gpustorming_registry_contract.py"}

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
    {"family": "facetframe", "segment": "facet-frame", "group": "Evidence and surface controls", "late_search_surface": True, "late_search_variants": {"operator": "facet-hidden, route-scrubbed, or related-question-neutralized variant", "oq": "facet-hidden/route-scrubbed/related-question-neutralized variant", "prompt": "facet-hidden, route-scrubbed, or related-question-neutralized variant worth checking", "runbook": "facet-hidden, route-scrubbed, or related-question-neutralized variant", "alias_prompt": "facet-hidden, route-scrubbed, or related-question-neutralized variant"}},
    {"family": "handoffframe", "segment": "handoff-frame", "group": "Evidence and surface controls", "late_search_surface": True, "late_search_variants": {"operator": "handoff-neutralized, context-reset, or manual-query-replayed variant", "oq": "handoff-neutralized/context-reset/manual-query-replayed variant", "prompt": "handoff-neutralized, context-reset, or manual-query-replayed variant worth checking", "runbook": "handoff-neutralized, context-reset, or manual-query-replayed variant", "alias_prompt": "handoff-neutralized, context-reset, or manual-query-replayed variant"}},
    {"family": "workspaceframe", "segment": "workspace-frame", "group": "Evidence and surface controls", "late_search_surface": True, "late_search_variants": {"operator": "workspace-neutralized, project-state-reset, or underlier-replayed variant", "oq": "workspace-neutralized/project-state-reset/underlier-replayed variant", "prompt": "workspace-neutralized, project-state-reset, or underlier-replayed variant worth checking", "runbook": "workspace-neutralized, project-state-reset, or underlier-replayed variant", "alias_prompt": "workspace-neutralized, project-state-reset, or underlier-replayed variant"}},
    {"family": "uploadframe", "segment": "upload-frame", "group": "Evidence and surface controls", "late_search_surface": True, "late_search_variants": {"operator": "upload-neutralized, attachment-detached, or public-web-replayed variant", "oq": "upload-neutralized/attachment-detached/public-web-replayed variant", "prompt": "upload-neutralized, attachment-detached, or public-web-replayed variant worth checking", "runbook": "upload-neutralized, attachment-detached, or public-web-replayed variant", "alias_prompt": "upload-neutralized, attachment-detached, or public-web-replayed variant"}},
    {"family": "profileframe", "segment": "profile-frame", "group": "Evidence and surface controls", "late_search_surface": True, "late_search_variants": {"operator": "profile-blinded, history-disconnected, or public-basis-replayed variant", "oq": "profile-blinded/history-disconnected/public-basis-replayed variant", "prompt": "profile-blinded, history-disconnected, or public-basis-replayed variant worth checking", "runbook": "profile-blinded, history-disconnected, or public-basis-replayed variant", "alias_prompt": "profile-blinded, history-disconnected, or public-basis-replayed variant"}},
    {"family": "liveframe", "segment": "live-frame", "group": "Evidence and surface controls", "late_search_surface": True, "late_search_variants": {"operator": "live-neutralized, camera-disconnected, or still-basis-replayed variant", "oq": "live-neutralized/camera-disconnected/still-basis-replayed variant", "prompt": "live-neutralized, camera-disconnected, or still-basis-replayed variant worth checking", "runbook": "live-neutralized, camera-disconnected, or still-basis-replayed variant", "alias_prompt": "live-neutralized, camera-disconnected, or still-basis-replayed variant"}},
    {"family": "deepframe", "segment": "deep-frame", "group": "Evidence and surface controls", "late_search_surface": True, "late_search_variants": {"operator": "deep-neutralized, breadth-capped, or seed-query-replayed variant", "oq": "deep-neutralized/breadth-capped/seed-query-replayed variant", "prompt": "deep-neutralized, breadth-capped, or seed-query-replayed variant worth checking", "runbook": "deep-neutralized, breadth-capped, or seed-query-replayed variant", "alias_prompt": "deep-neutralized, breadth-capped, or seed-query-replayed variant"}},
    {"family": "catalogframe", "segment": "catalog-frame", "group": "Evidence and surface controls", "late_search_surface": True, "late_search_variants": {"operator": "catalog-neutralized, feed-disconnected, or open-web-replayed variant", "oq": "catalog-neutralized/feed-disconnected/open-web-replayed variant", "prompt": "catalog-neutralized, feed-disconnected, or open-web-replayed variant worth checking", "runbook": "catalog-neutralized, feed-disconnected, or open-web-replayed variant", "alias_prompt": "catalog-neutralized, feed-disconnected, or open-web-replayed variant"}},
    {"family": "actionframe", "segment": "action-frame", "group": "Evidence and surface controls", "late_search_surface": True, "late_search_variants": {"operator": "action-neutralized, partner-link-scrubbed, or manual-route-replayed variant", "oq": "action-neutralized/partner-link-scrubbed/manual-route-replayed variant", "prompt": "action-neutralized, partner-link-scrubbed, or manual-route-replayed variant worth checking", "runbook": "action-neutralized, partner-link-scrubbed, or manual-route-replayed variant", "alias_prompt": "action-neutralized, partner-link-scrubbed, or manual-route-replayed variant"}},
    {"family": "delegateframe", "segment": "delegate-frame", "group": "Evidence and surface controls", "late_search_surface": True, "late_search_variants": {"operator": "delegate-neutralized, authority-withdrawn, or manual-steps-replayed variant", "oq": "delegate-neutralized/authority-withdrawn/manual-steps-replayed variant", "prompt": "delegate-neutralized, authority-withdrawn, or manual-steps-replayed variant worth checking", "runbook": "delegate-neutralized, authority-withdrawn, or manual-steps-replayed variant", "alias_prompt": "delegate-neutralized, authority-withdrawn, or manual-steps-replayed variant"}},
    {"family": "appframe", "segment": "app-frame", "group": "Evidence and surface controls", "late_search_surface": True, "late_search_variants": {"operator": "app-neutralized, widget-detached, or host-only-replayed variant", "oq": "app-neutralized/widget-detached/host-only-replayed variant", "prompt": "app-neutralized, widget-detached, or host-only-replayed variant worth checking", "runbook": "app-neutralized, widget-detached, or host-only-replayed variant", "alias_prompt": "app-neutralized, widget-detached, or host-only-replayed variant"}},
    {"family": "openframe", "segment": "open-frame", "group": "Evidence and surface controls", "late_search_surface": True, "late_search_variants": {"operator": "search-open-neutralized, host-shell-detached, or source-root-replayed variant", "oq": "search-open-neutralized/host-shell-detached/source-root-replayed variant", "prompt": "search-open-neutralized, host-shell-detached, or source-root-replayed variant worth checking", "runbook": "search-open-neutralized, host-shell-detached, or source-root-replayed variant", "alias_prompt": "search-open-neutralized, host-shell-detached, or source-root-replayed variant"}},
    {"family": "adframe", "segment": "ad-frame", "group": "Evidence and surface controls", "late_search_surface": True, "late_search_variants": {"operator": "ad-hidden, sponsor-scrubbed, or organic-basis-replayed variant", "oq": "ad-hidden/sponsor-scrubbed/organic-basis-replayed variant", "prompt": "ad-hidden, sponsor-scrubbed, or organic-basis-replayed variant worth checking", "runbook": "ad-hidden, sponsor-scrubbed, or organic-basis-replayed variant", "alias_prompt": "ad-hidden, sponsor-scrubbed, or organic-basis-replayed variant"}},
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

LATE_SEARCH_CONTRACT_DEFAULTS = {
    "facetframe": {
        "privileges": ["facet privilege", "aspect-route privilege", "related-question privilege"],
        "crosswalk_text": "People Also Ask ladders, related-search modules, facet tabs, or refine-this-search chips",
    },
    "handoffframe": {
        "privileges": ["handoff privilege", "context-carry privilege", "next-query privilege"],
        "crosswalk_text": "follow-up question prompts, continue-exploring links, dive-deeper transitions, or suggested next searches",
    },
    "workspaceframe": {
        "privileges": ["workspace privilege", "project-state privilege", "mutable-artifact privilege"],
        "crosswalk_text": "Canvas side panels, editable draft documents, generated study guides, custom interactive tools, or other in-search workspace artifacts",
    },
    "uploadframe": {
        "privileges": ["upload-context privilege", "attachment-presence privilege", "file-underlier privilege"],
        "crosswalk_text": "uploaded PDFs, images, Google Drive files, or other user-supplied file context",
    },
    "profileframe": {
        "privileges": ["profile privilege", "personal-context privilege", "history-carry privilege"],
        "crosswalk_text": "saved memories, past-search carryover, connected Gmail or Photos context, or other personal-context profile surfaces",
    },
    "liveframe": {
        "privileges": ["live-context privilege", "camera-feed privilege", "motion-scene privilege"],
        "crosswalk_text": "live camera feeds, interactive voice-and-video search turns, moving-scene visual search, or other embodied real-time context",
    },
    "deepframe": {
        "privileges": ["research-depth privilege", "autonomous-browse privilege", "synthesis-breadth privilege"],
        "crosswalk_text": "Deep Search reports, deep research runs, multi-step browsing plans, or agentic research expansions",
    },
    "catalogframe": {
        "privileges": ["catalog privilege", "merchant-feed privilege", "inventory-graph privilege"],
        "crosswalk_text": "Shopping Graph panels, merchant-feed product cards, price/review/inventory aggregates, or other catalog-backed shopping responses",
    },
    "actionframe": {
        "privileges": ["action privilege", "partner-route privilege", "transaction-ready privilege"],
        "crosswalk_text": "booking links, shoppable product cards, reservation-slot panels, agentic checkout surfaces, or direct-action task cards",
    },
    "delegateframe": {
        "privileges": ["delegated-authority privilege", "third-party-actuation privilege", "hidden-subtask privilege"],
        "crosswalk_text": "business-calling runs, browser-executed form fills, website-navigation sessions, or other delegated task-execution episodes",
    },
    "appframe": {
        "privileges": ["app-directory privilege", "embedded-widget privilege", "connector-presence privilege"],
        "crosswalk_text": "app-directory suggestions, approved app cards, embedded widgets or iframes, or connected-service app surfaces",
    },
    "openframe": {
        "privileges": ["host-shell privilege", "source-open-overlay privilege", "in-search-view privilege"],
        "crosswalk_text": "search-hosted side panels, in-search page viewers, retained host-chrome source opens, or other source-open overlays",
    },
    "adframe": {
        "privileges": ["sponsor privilege", "paid-placement privilege", "monetization-eligibility privilege"],
        "crosswalk_text": "sponsored result cards, ads above/below/within AI Overviews, Direct Offers, or other advertiser-shaped commercial answer surfaces",
    },
}


def late_search_standard_family_contract_kwargs(family: str) -> dict:
    defaults = LATE_SEARCH_CONTRACT_DEFAULTS[family]
    return {
        "family": family,
        "operator_variant": late_search_variant(family, "operator"),
        "privileges": defaults["privileges"],
        "crosswalk_text": defaults["crosswalk_text"],
        "oq_variant": late_search_variant(family, "oq"),
        "prompt_variant": late_search_variant(family, "prompt"),
        "runbook_variant": late_search_variant(family, "runbook"),
    }


def validate_late_search_contract_defaults() -> None:
    families = set(late_search_surface_families())
    defaults = set(LATE_SEARCH_CONTRACT_DEFAULTS)
    missing = sorted(families - defaults)
    extra = sorted(defaults - families)
    if missing or extra:
        raise SystemExit(
            f"late-search contract-default drift: missing={missing} extra={extra}"
        )
    for family, payload in LATE_SEARCH_CONTRACT_DEFAULTS.items():
        if not isinstance(payload.get("privileges"), list) or len(payload["privileges"]) != 3:
            raise SystemExit(f"late-search contract defaults for {family} need exactly three privileges")
        if not isinstance(payload.get("crosswalk_text"), str) or not payload["crosswalk_text"].strip():
            raise SystemExit(f"late-search contract defaults for {family} need non-empty crosswalk_text")


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


def canonical_trajectory_path() -> str:
    return "/".join(FAMILY_TRAJECTORY_SEGMENTS[family] for family in CANONICAL_GPUSTORMING_FAMILY_ORDER)


def trajectory_prefix_through(family: str) -> str:
    segments = []
    for slug in CANONICAL_GPUSTORMING_FAMILY_ORDER:
        segments.append(FAMILY_TRAJECTORY_SEGMENTS.get(slug, slug))
        if slug == family:
            return "/".join(segments)
    raise KeyError(f"unknown gpustorming family: {family}")



def late_search_problem_chain_anchor_families() -> tuple[str, str]:
    late = [spec["family"] for spec in GPUSTORMING_FAMILY_SPECS if spec.get("late_search_surface")]
    if len(late) < 2:
        raise ValueError("Need at least two late-search families for problem-chain anchoring")
    return late[-2], late[-1]

def trajectory_problem_phrase(family: str) -> str:
    return "family plus placement/density/" + trajectory_prefix_through(family) + " problem"


def late_search_problem_chain_phrases() -> list[str]:
    return [trajectory_problem_phrase(family) for family in late_search_surface_families()]


def late_search_problem_chain_tail() -> str:
    return trajectory_problem_phrase(late_search_surface_families()[-1])


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


def expected_gpustorming_family_contract_names() -> list[str]:
    return [f"check_gpustorming_{family}_contract.py" for family in CANONICAL_GPUSTORMING_FAMILY_ORDER]


def expected_late_search_family_contract_names() -> list[str]:
    return [f"check_gpustorming_{family}_contract.py" for family in late_search_surface_families()]


def build_gpustorming_toolchain(root: pathlib.Path) -> list[str]:
    return [
        "check_gpustorming_contract.py",
        "check_gpustorming_registry_contract.py",
        *[path.name for path in discover_gpustorming_contract_files(root)],
        "check_gpustorming_crosswalk_contract.py",
    ]


def default_trajectory_intro(family: str) -> str:
    return f"A parallel {family} extension"


def derived_variant_forms(operator_variant: str) -> dict[str, str]:
    if not isinstance(operator_variant, str) or not operator_variant.strip():
        raise ValueError("operator_variant must be a non-empty string")
    oq = operator_variant.replace(", or ", "/").replace(", ", "/")
    return {
        "operator": operator_variant,
        "oq": oq,
        "prompt": f"{operator_variant} worth checking",
        "runbook": operator_variant,
    }


def run_phrase_family_contract(root: pathlib.Path, name: str, *, family: str, operator_variant: str, privileges: list[str], crosswalk_text: str, quarantine_id: str, quarantine_text: str, changelog_text: str, archive_index_text: str, trajectory_intro: str | None = None) -> None:
    variants = derived_variant_forms(operator_variant)
    run_standard_family_contract(
        root,
        name,
        family=family,
        operator_variant=variants["operator"],
        privileges=privileges,
        crosswalk_text=crosswalk_text,
        trajectory_intro=trajectory_intro,
        oq_variant=variants["oq"],
        prompt_variant=variants["prompt"],
        runbook_variant=variants["runbook"],
        quarantine_id=quarantine_id,
        quarantine_text=quarantine_text,
        changelog_text=changelog_text,
        archive_index_text=archive_index_text,
    )


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


def check_standard_family_contract(root: pathlib.Path, name: str, **kwargs) -> None:
    ensure_needles(root, name, standard_family_contract_map(**kwargs))


def run_standard_family_contract(root: pathlib.Path, name: str, **kwargs) -> None:
    check_standard_family_contract(root, name, **kwargs)
    print(f"check_{name.replace('-', '_')}_contract: OK")


def late_search_surface_specs() -> list[dict]:
    return [spec for spec in GPUSTORMING_FAMILY_SPECS if spec.get("late_search_surface")]


def late_search_surface_families() -> list[str]:
    families = [spec["family"] for spec in late_search_surface_specs()]
    for family in families:
        family_spec_for(family)
    return families


def late_search_variant(family: str, surface: str) -> str:
    variants = family_spec_for(family).get("late_search_variants")
    if not variants or surface not in variants:
        raise KeyError(f"unknown late-search variant needle for {family}/{surface}")
    return variants[surface]


def ordered_needles_for_family_sequence(*, families: list[str], formatter) -> list[str]:
    return [formatter(family) for family in families]
