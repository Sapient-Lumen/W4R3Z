from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from . import __version__
from .artifact import artifact_audit_markdown, audit_release_artifact
from .campaigns import CampaignLibrary, resolve_cube_reference
from .checkpoints import (
    CHECKPOINT_ROLES,
    assemble_checkpoint_proposal,
    build_checkpoint_dispatch,
    build_checkpoint_request,
    build_checkpoint_task_card,
    checkpoint_dispatch_markdown,
    checkpoint_task_card_markdown,
    commit_checkpoint,
    review_checkpoint,
)
from .checkpoint_runs import (
    INVOCATION_FAILURE_CLASSES,
    accept_checkpoint_run_artifact,
    audit_checkpoint_run,
    begin_checkpoint_continuation_turn,
    begin_checkpoint_run,
    build_checkpoint_continuation_dispatch,
    build_checkpoint_run_dispatch,
    build_checkpoint_run_narrator_capsule,
    checkpoint_run_dispatch_markdown,
    checkpoint_run_markdown,
    checkpoint_run_receipt_markdown,
    committed_checkpoint_history_boundary,
    commit_checkpoint_run,
    normalize_checkpoint_provider_routes,
    record_checkpoint_run_failure,
    recover_checkpoint_run,
)
from .continuation import (
    checkpoint_continuation_dispatch_markdown,
    checkpoint_narrator_capsule_markdown,
)
from .context import build_context
from .entrance import (
    MODEL_PROFILES,
    build_model_brief,
    describe_model_reference,
    model_brief_markdown,
)
from .errors import LacunaError
from .orchestration import (
    ORCHESTRATION_MODES,
    TASK_ROLES,
    build_orchestration_plan,
    build_turn_task_card,
    orchestration_plan_markdown,
    turn_task_card_markdown,
)
from .play import play_start_markdown, start_play
from .providers import PROVIDERS
from .public_history import (
    build_complete_public_history,
    build_public_history,
    public_history_markdown,
)
from .render import context_markdown, turn_packet_markdown, turn_receipt_markdown
from .scenarios import (
    audit_scenario_run,
    begin_scenario_run,
    build_scenario_capsule_template,
    dispatch_scenario_cell,
    record_scenario_cell,
    record_scenario_masking,
    record_scenario_rating,
    recover_scenario_run,
    scenario_contamination_scan,
    scenario_contamination_scan_markdown,
    scenario_driver_markdown,
    scenario_masking_template,
    scenario_rating_template,
    scenario_report_markdown,
    scenario_run_markdown,
    unblind_scenario_run,
)
from .scenario_bundles import (
    audit_scenario_bundle,
    begin_scenario_bundle,
    build_scenario_bundle_plan,
    build_scenario_bundle_witness_template,
    dispatch_scenario_bundle_cell,
    record_scenario_bundle_cell,
    record_scenario_bundle_masking,
    record_scenario_bundle_rating,
    record_scenario_bundle_witness,
    recover_scenario_bundle,
    scenario_bundle_commitment,
    scenario_bundle_masking_template,
    scenario_bundle_rating_template,
    scenario_bundle_report,
    scenario_bundle_report_csv,
    scenario_bundle_report_markdown,
    scenario_bundle_run_markdown,
    seal_scenario_bundle_block,
    unblind_scenario_bundle,
)
from .seals import (
    SEAL_PURPOSES,
    SEAL_VISIBILITIES,
    parse_seal_opening,
    prepare_seal_opening,
)
from .store import Cube
from .turnruns import (
    TURN_RUN_PROVIDERS,
    accept_turn_run_artifact,
    audit_turn_run,
    begin_turn_run,
    build_turn_run_dispatch,
    commit_turn_run,
    recover_turn_run,
    turn_run_dispatch_markdown,
    turn_run_markdown,
)
from .turns import TURN_INPUT_KINDS, build_turn_packet, commit_turn_proposal
from .util import deterministic_claim_id, new_id, parse_json_value, pretty_json


def emit(value: Any) -> None:
    print(pretty_json(value))


def read_json_value_file(path: str, *, error_code: str = "json-read-failed") -> Any:
    try:
        if path == "-":
            return json.load(sys.stdin)
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        raise LacunaError(error_code, str(exc)) from exc


def read_json_object(
    path: str,
    *,
    error_code: str,
    root_code: str,
    label: str,
) -> dict[str, Any]:
    value = read_json_value_file(path, error_code=error_code)
    if not isinstance(value, dict):
        raise LacunaError(root_code, f"{label} root must be a JSON object")
    return value


def read_json_document(path: str) -> dict[str, Any]:
    return read_json_object(
        path,
        error_code="change-set-read-failed",
        root_code="bad-change-set",
        label="change-set",
    )


def read_utf8_text_file(path: str, *, error_code: str = "text-read-failed") -> str:
    try:
        if path == "-":
            return sys.stdin.read()
        with open(path, "r", encoding="utf-8", newline="") as handle:
            return handle.read()
    except (OSError, UnicodeError) as exc:
        raise LacunaError(error_code, str(exc)) from exc


def player_input_from_args(args: argparse.Namespace) -> str:
    direct = getattr(args, "player_input", None)
    path = getattr(args, "player_input_file", None)
    if direct is not None:
        return direct
    if path is not None:
        return read_utf8_text_file(path, error_code="player-input-read-failed")
    raise LacunaError("missing-player-input", "provide --player-input or --player-input-file")


def checkpoint_trigger_from_args(args: argparse.Namespace) -> str:
    direct = getattr(args, "trigger", None)
    path = getattr(args, "trigger_file", None)
    if direct is not None:
        return direct
    if path is not None:
        return read_utf8_text_file(path, error_code="checkpoint-trigger-read-failed")
    raise LacunaError("missing-checkpoint-trigger", "provide --trigger or --trigger-file")


def single_op(cube: Cube, actor_id: str, operation: dict[str, Any], message: str) -> dict[str, Any]:
    return cube.apply_operations(actor_id=actor_id, operations=[operation], message=message)


def parse_particle_assessment(value: str) -> dict[str, Any]:
    """Parse WORLD_ID=LIKELIHOOD for the human CLI entrance."""
    if "=" not in value:
        raise argparse.ArgumentTypeError("assessment must use WORLD_ID=LIKELIHOOD")
    world_id, raw_likelihood = value.rsplit("=", 1)
    world_id = world_id.strip()
    if not world_id:
        raise argparse.ArgumentTypeError("assessment world ID must not be empty")
    try:
        likelihood = float(raw_likelihood)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("assessment likelihood must be numeric") from exc
    if not 0.0 <= likelihood <= 1.0:
        raise argparse.ArgumentTypeError("assessment likelihood must be between 0 and 1")
    return {"world_id": world_id, "likelihood": likelihood, "rationale": None}


def open_cube(reference: str | Path) -> Cube:
    return Cube.open(resolve_cube_reference(reference))


def cmd_init(args: argparse.Namespace) -> int:
    with Cube.init(args.cube, owner_id=args.owner_id, owner_label=args.owner_label) as cube:
        emit(cube.status())
    return 0


def cmd_migrate(args: argparse.Namespace) -> int:
    emit(Cube.migrate(resolve_cube_reference(args.cube)))
    return 0


def cmd_artifact_check(args: argparse.Namespace) -> int:
    report = audit_release_artifact(args.root, strict_members=args.strict_members)
    if args.format == "markdown":
        print(artifact_audit_markdown(report))
    else:
        emit(report)
    return 0 if report["overall_status"] == "pass" else 1


def cmd_status(args: argparse.Namespace) -> int:
    with open_cube(args.cube) as cube:
        emit(cube.status())
    return 0


def cmd_head(args: argparse.Namespace) -> int:
    with open_cube(args.cube) as cube:
        emit({"event": "lacuna.head", "cube_id": cube.meta("cube_id"), "head": cube.head()})
    return 0


def cmd_apply(args: argparse.Namespace) -> int:
    document = read_json_document(args.change_set)
    with open_cube(args.cube) as cube:
        if args.bind_current:
            document["expected_head"] = cube.head()
        emit(cube.apply_changeset(document))
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    with open_cube(args.cube) as cube:
        report = cube.verify()
        emit(report)
        return 0 if report["overall_status"] == "pass" else 1


def cmd_rebuild(args: argparse.Namespace) -> int:
    with open_cube(args.cube) as cube:
        emit(cube.rebuild_projections())
    return 0


def cmd_snapshot(args: argparse.Namespace) -> int:
    with open_cube(args.cube) as cube:
        emit(cube.snapshot())
    return 0


def cmd_events(args: argparse.Namespace) -> int:
    with open_cube(args.cube) as cube:
        emit(
            {
                "event": "lacuna.events",
                "schema": "lacuna.events.v1",
                "cube_id": cube.meta("cube_id"),
                "head": cube.head(),
                "events": cube.events(limit=args.limit, since_seq=args.since_seq),
            }
        )
    return 0


def cmd_changes(args: argparse.Namespace) -> int:
    with open_cube(args.cube) as cube:
        changes = cube.changes()
        emit(
            {
                "event": "lacuna.changes",
                "schema": "lacuna.changes.v1",
                "cube_id": cube.meta("cube_id"),
                "head": cube.head(),
                "change_count": len(changes),
                "changes": changes,
            }
        )
    return 0


def cmd_evidence(args: argparse.Namespace) -> int:
    with open_cube(args.cube) as cube:
        links = cube.evidence_links(world_id=args.world_id)
        emit(
            {
                "event": "lacuna.evidence",
                "schema": "lacuna.evidence.v1",
                "cube_id": cube.meta("cube_id"),
                "head": cube.head(),
                "world_id": args.world_id,
                "link_count": len(links),
                "links": links,
            }
        )
    return 0


def cmd_claims(args: argparse.Namespace) -> int:
    with open_cube(args.cube) as cube:
        emit({"event": "lacuna.claims", "head": cube.head(), "claims": cube.claims()})
    return 0


def cmd_relations(args: argparse.Namespace) -> int:
    with open_cube(args.cube) as cube:
        relations = cube.claim_relations(include_retired=args.include_retired)
        emit(
            {
                "event": "lacuna.claim-relations",
                "schema": "lacuna.claim-relations.v1",
                "cube_id": cube.meta("cube_id"),
                "head": cube.head(),
                "relation_count": len(relations),
                "relations": relations,
            }
        )
    return 0


def cmd_cardinalities(args: argparse.Namespace) -> int:
    with open_cube(args.cube) as cube:
        constraints = cube.cardinality_constraints(include_retired=args.include_retired)
        emit(
            {
                "event": "lacuna.cardinality-constraints",
                "schema": "lacuna.cardinality-constraints.v1",
                "cube_id": cube.meta("cube_id"),
                "head": cube.head(),
                "constraint_count": len(constraints),
                "constraints": constraints,
            }
        )
    return 0


def cmd_revision_impact(args: argparse.Namespace) -> int:
    with open_cube(args.cube) as cube:
        emit(cube.revision_impact(args.assignment_id))
    return 0


def cmd_consequences(args: argparse.Namespace) -> int:
    with open_cube(args.cube) as cube:
        links = cube.consequence_links(
            include_retired=args.include_retired,
            premise_assignment_id=args.premise_assignment_id,
        )
        emit(
            {
                "event": "lacuna.consequences",
                "schema": "lacuna.consequences.v1",
                "cube_id": cube.meta("cube_id"),
                "head": cube.head(),
                "consequence_count": len(links),
                "consequences": links,
            }
        )
    return 0


def cmd_consequence_repairs(args: argparse.Namespace) -> int:
    with open_cube(args.cube) as cube:
        repairs = cube.consequence_repairs()
        emit(
            {
                "event": "lacuna.consequence-repairs",
                "schema": "lacuna.consequence-repairs.v1",
                "cube_id": cube.meta("cube_id"),
                "head": cube.head(),
                "repair_count": len(repairs),
                "repairs": repairs,
            }
        )
    return 0


def cmd_consequence_repair_review(args: argparse.Namespace) -> int:
    with open_cube(args.cube) as cube:
        emit(cube.consequence_repair_review(args.consequence_id))
    return 0


def cmd_consequence_repair_frontier(args: argparse.Namespace) -> int:
    with open_cube(args.cube) as cube:
        frontier = cube.consequence_repair_frontier(world_id=args.world_id)
        emit(
            {
                "event": "lacuna.consequence-repair-frontier",
                "schema": "lacuna.consequence-repair-frontier.v1",
                "cube_id": cube.meta("cube_id"),
                "head": cube.head(),
                "world_id": args.world_id,
                "repair_required_count": len(frontier),
                "reviews": frontier,
            }
        )
    return 0


def cmd_particle_bank(args: argparse.Namespace) -> int:
    with open_cube(args.cube) as cube:
        emit(cube.particle_bank())
    return 0


def cmd_particle_update_review(args: argparse.Namespace) -> int:
    with open_cube(args.cube) as cube:
        emit(cube.particle_update_review(args.evidence_assertion_id))
    return 0


def cmd_particle_updates(args: argparse.Namespace) -> int:
    with open_cube(args.cube) as cube:
        updates = cube.particle_updates(update_id=args.update_id)
        emit(
            {
                "event": "lacuna.particle-updates",
                "schema": "lacuna.particle-updates.v1",
                "cube_id": cube.meta("cube_id"),
                "head": cube.head(),
                "update_count": len(updates),
                "updates": updates,
            }
        )
    return 0


def cmd_particle_reconciliation_review(args: argparse.Namespace) -> int:
    with open_cube(args.cube) as cube:
        emit(cube.particle_reconciliation_review())
    return 0


def cmd_particle_reconciliations(args: argparse.Namespace) -> int:
    with open_cube(args.cube) as cube:
        reconciliations = cube.particle_reconciliations(
            reconciliation_id=args.reconciliation_id
        )
        emit(
            {
                "event": "lacuna.particle-reconciliations",
                "schema": "lacuna.particle-reconciliations.v1",
                "cube_id": cube.meta("cube_id"),
                "head": cube.head(),
                "reconciliation_count": len(reconciliations),
                "reconciliations": reconciliations,
            }
        )
    return 0


def cmd_explain(args: argparse.Namespace) -> int:
    with open_cube(args.cube) as cube:
        emit(cube.explain(args.target_id, agent_id=args.agent_id))
    return 0


def cmd_canon(args: argparse.Namespace) -> int:
    with open_cube(args.cube) as cube:
        emit(cube.canon())
    return 0


def cmd_worlds(args: argparse.Namespace) -> int:
    with open_cube(args.cube) as cube:
        emit({"event": "lacuna.worlds", "head": cube.head(), "worlds": cube.worlds()})
    return 0


def cmd_world(args: argparse.Namespace) -> int:
    with open_cube(args.cube) as cube:
        world = cube._require_world(args.world_id)
        world["assignments"] = cube.world_assignments(args.world_id)
        emit({"event": "lacuna.world", "head": cube.head(), "world": world})
    return 0


def cmd_perspective(args: argparse.Namespace) -> int:
    with open_cube(args.cube) as cube:
        emit(cube.perspective(args.agent_id))
    return 0


def cmd_unknowns(args: argparse.Namespace) -> int:
    with open_cube(args.cube) as cube:
        emit(cube.unknowns())
    return 0


def cmd_conflicts(args: argparse.Namespace) -> int:
    with open_cube(args.cube) as cube:
        conflicts = cube.conflicts()
        emit(
            {
                "event": "lacuna.conflicts",
                "schema": "lacuna.conflicts.v1",
                "cube_id": cube.meta("cube_id"),
                "head": cube.head(),
                "conflict_count": len(conflicts),
                "conflicts": conflicts,
            }
        )
    return 0


def cmd_context(args: argparse.Namespace) -> int:
    with open_cube(args.cube) as cube:
        if args.format == "json":
            emit(build_context(cube, agent_id=args.agent_id, world_id=args.world_id))
        else:
            print(context_markdown(cube, agent_id=args.agent_id, world_id=args.world_id))
    return 0


def cmd_campaign_init(args: argparse.Namespace) -> int:
    library = CampaignLibrary.init(args.library)
    emit(library.summary())
    return 0


def cmd_campaign_create(args: argparse.Namespace) -> int:
    library = CampaignLibrary.ensure(args.library)
    campaign = library.create_campaign(
        slug=args.slug,
        title=args.title or args.slug.replace("-", " ").title(),
        summary=args.summary or "",
        owner_id=args.owner_id,
        owner_label=args.owner_label,
        player_id=args.player_id,
        player_label=args.player_label,
        narrator_id=args.narrator_id,
        narrator_label=args.narrator_label,
    )
    emit(
        {
            "event": "lacuna.campaign.created",
            "schema": "lacuna.campaign-receipt.v1",
            "library_id": library.config["library_id"],
            "campaign": campaign,
        }
    )
    return 0


def _campaign_table(summary: dict[str, Any]) -> str:
    campaigns = summary["campaigns"]
    if not campaigns:
        return "No campaigns."
    widths = {
        "selected": 3,
        "slug": max(4, *(len(item["slug"]) for item in campaigns)),
        "title": max(5, *(len(item["title"]) for item in campaigns)),
        "status": max(6, *(len(item["status"]) for item in campaigns)),
    }
    header = (
        f"{'USE':<{widths['selected']}}  {'SLUG':<{widths['slug']}}  "
        f"{'TITLE':<{widths['title']}}  {'STATUS':<{widths['status']}}"
    )
    rows = [header, "-" * len(header)]
    for item in campaigns:
        rows.append(
            f"{('*' if item['selected'] else ''):<{widths['selected']}}  "
            f"{item['slug']:<{widths['slug']}}  {item['title']:<{widths['title']}}  "
            f"{item['status']:<{widths['status']}}"
        )
    return "\n".join(rows)


def cmd_campaign_list(args: argparse.Namespace) -> int:
    summary = CampaignLibrary.open(args.library).summary()
    if args.format == "json":
        emit(summary)
    else:
        print(_campaign_table(summary))
    return 0


def cmd_campaign_select(args: argparse.Namespace) -> int:
    emit(CampaignLibrary.open(args.library).select(args.selector))
    return 0


def cmd_campaign_show(args: argparse.Namespace) -> int:
    library = CampaignLibrary.open(args.library)
    emit(
        {
            "event": "lacuna.campaign",
            "schema": "lacuna.campaign-view.v1",
            "library_id": library.config["library_id"],
            "campaign": library.resolve(args.selector),
        }
    )
    return 0


def cmd_campaign_path(args: argparse.Namespace) -> int:
    item = CampaignLibrary.open(args.library).resolve(args.selector)
    print(item["path"])
    return 0


def cmd_model_brief(args: argparse.Namespace) -> int:
    target = describe_model_reference(args.cube)
    with Cube.open(target["resolved_cube_path"]) as cube:
        brief = build_model_brief(
            cube,
            reference=target["reference"],
            resolved_cube_path=target["resolved_cube_path"],
            reference_kind=target["reference_kind"],
            campaign=target["campaign"],
            profile=args.profile,
            audience_id=args.audience_id,
            actor_id=args.actor_id,
        )
    if args.format == "markdown":
        print(model_brief_markdown(brief))
    else:
        emit(brief)
    return 0


def cmd_turn_packet(args: argparse.Namespace) -> int:
    with open_cube(args.cube) as cube:
        packet = build_turn_packet(
            cube,
            audience_id=args.audience_id,
            actor_id=args.actor_id,
            player_input=player_input_from_args(args),
            input_kind=args.input_kind,
            director=args.director,
            world_id=args.world_id,
            allow_anchor=args.allow_anchor,
        )
        if args.format == "markdown":
            print(turn_packet_markdown(packet))
        else:
            emit(packet)
    return 0


def cmd_turn_commit(args: argparse.Namespace) -> int:
    document = read_json_document(args.proposal)
    with open_cube(args.cube) as cube:
        receipt = commit_turn_proposal(
            cube,
            document,
            include_planner_context=args.include_planner_context,
        )
        if args.format == "markdown":
            print(turn_receipt_markdown(receipt))
        else:
            emit(receipt)
    return 0


def _emit_scenario_run(manifest: dict[str, Any], format_name: str) -> None:
    if format_name == "markdown":
        print(scenario_run_markdown(manifest))
    else:
        emit(manifest)


def cmd_scenario_template(args: argparse.Namespace) -> int:
    target = describe_model_reference(args.cube)
    with Cube.open(target["resolved_cube_path"]) as cube:
        emit(
            build_scenario_capsule_template(
                cube,
                title=args.title,
                research_question=args.research_question,
            )
        )
    return 0


def cmd_scenario_begin(args: argparse.Namespace) -> int:
    capsule = read_json_object(
        args.capsule,
        error_code="scenario-capsule-read-failed",
        root_code="bad-scenario-capsule",
        label="scenario capsule",
    )
    target = describe_model_reference(args.cube)
    with Cube.open(target["resolved_cube_path"]) as cube:
        manifest = begin_scenario_run(
            cube,
            capsule,
            reference=target["reference"],
            resolved_seed_cube_path=target["resolved_cube_path"],
            root=args.root,
        )
    _emit_scenario_run(manifest, args.format)
    return 0


def cmd_scenario_status(args: argparse.Namespace) -> int:
    _emit_scenario_run(audit_scenario_run(args.run), args.format)
    return 0


def cmd_scenario_recover(args: argparse.Namespace) -> int:
    _emit_scenario_run(recover_scenario_run(args.run), args.format)
    return 0


def cmd_scenario_dispatch(args: argparse.Namespace) -> int:
    driver = dispatch_scenario_cell(args.run)
    if args.format == "markdown":
        print(scenario_driver_markdown(driver))
    else:
        emit(driver)
    return 0


def cmd_scenario_record(args: argparse.Namespace) -> int:
    artifact = read_json_object(
        args.artifact,
        error_code="scenario-cell-return-read-failed",
        root_code="bad-scenario-cell-return",
        label="scenario cell return",
    )
    _emit_scenario_run(record_scenario_cell(args.run, artifact), args.format)
    return 0


def cmd_scenario_contamination(args: argparse.Namespace) -> int:
    if args.format == "markdown":
        print(scenario_contamination_scan_markdown(args.run))
    else:
        emit(scenario_contamination_scan(args.run))
    return 0


def cmd_scenario_rating_template(args: argparse.Namespace) -> int:
    emit(scenario_rating_template(args.run, rater_id=args.rater_id))
    return 0


def cmd_scenario_rate(args: argparse.Namespace) -> int:
    rating = read_json_object(
        args.rating,
        error_code="scenario-rating-read-failed",
        root_code="bad-scenario-rating",
        label="scenario rating",
    )
    _emit_scenario_run(record_scenario_rating(args.run, rating), args.format)
    return 0


def cmd_scenario_masking_template(args: argparse.Namespace) -> int:
    emit(scenario_masking_template(args.run, assessor_id=args.assessor_id))
    return 0


def cmd_scenario_mask(args: argparse.Namespace) -> int:
    masking = read_json_object(
        args.masking,
        error_code="scenario-masking-read-failed",
        root_code="bad-scenario-masking-assessment",
        label="scenario masking assessment",
    )
    _emit_scenario_run(record_scenario_masking(args.run, masking), args.format)
    return 0


def cmd_scenario_unblind(args: argparse.Namespace) -> int:
    report = unblind_scenario_run(args.run)
    if args.format == "markdown":
        print(scenario_report_markdown(report))
    else:
        emit(report)
    return 0


def _emit_scenario_bundle(manifest: dict[str, Any], format_name: str) -> None:
    if format_name == "markdown":
        print(scenario_bundle_run_markdown(manifest))
    else:
        emit(manifest)


def cmd_scenario_bundle_template(args: argparse.Namespace) -> int:
    blocks: list[dict[str, Any]] = []
    for index, (cube_reference, capsule_path) in enumerate(args.block, start=1):
        capsule = read_json_object(
            capsule_path,
            error_code="scenario-capsule-read-failed",
            root_code="bad-scenario-capsule",
            label=f"scenario capsule for block {index}",
        )
        target = describe_model_reference(cube_reference)
        blocks.append(
            {
                "reference": target["reference"],
                "resolved_seed_cube_path": target["resolved_cube_path"],
                "capsule": capsule,
                "replicate": index,
            }
        )
    primary_dimensions = args.primary_dimension or None
    emit(
        build_scenario_bundle_plan(
            blocks,
            title=args.title,
            research_question=args.research_question,
            primary_dimensions=primary_dimensions,
            minimum_receipts_before_execution=args.minimum_witnesses,
            notes=args.notes,
        )
    )
    return 0


def cmd_scenario_bundle_begin(args: argparse.Namespace) -> int:
    plan = read_json_object(
        args.plan,
        error_code="scenario-bundle-plan-read-failed",
        root_code="bad-scenario-bundle-plan",
        label="scenario bundle plan",
    )
    _emit_scenario_bundle(
        begin_scenario_bundle(plan, root=args.root),
        args.format,
    )
    return 0


def cmd_scenario_bundle_status(args: argparse.Namespace) -> int:
    _emit_scenario_bundle(audit_scenario_bundle(args.bundle), args.format)
    return 0


def cmd_scenario_bundle_recover(args: argparse.Namespace) -> int:
    _emit_scenario_bundle(recover_scenario_bundle(args.bundle), args.format)
    return 0


def cmd_scenario_bundle_commitment(args: argparse.Namespace) -> int:
    emit(scenario_bundle_commitment(args.bundle))
    return 0


def cmd_scenario_bundle_witness_template(args: argparse.Namespace) -> int:
    emit(
        build_scenario_bundle_witness_template(
            args.bundle,
            witness_id=args.witness_id,
        )
    )
    return 0


def cmd_scenario_bundle_witness(args: argparse.Namespace) -> int:
    witness = read_json_object(
        args.witness,
        error_code="scenario-bundle-witness-read-failed",
        root_code="bad-scenario-bundle-witness",
        label="scenario bundle witness",
    )
    emit(record_scenario_bundle_witness(args.bundle, witness))
    return 0


def cmd_scenario_bundle_dispatch(args: argparse.Namespace) -> int:
    driver = dispatch_scenario_bundle_cell(args.bundle)
    if args.format == "markdown":
        print(scenario_driver_markdown(driver))
    else:
        emit(driver)
    return 0


def cmd_scenario_bundle_record(args: argparse.Namespace) -> int:
    artifact = read_json_object(
        args.artifact,
        error_code="scenario-cell-return-read-failed",
        root_code="bad-scenario-cell-return",
        label="scenario cell return",
    )
    _emit_scenario_bundle(
        record_scenario_bundle_cell(args.bundle, artifact),
        args.format,
    )
    return 0


def cmd_scenario_bundle_rating_template(args: argparse.Namespace) -> int:
    emit(scenario_bundle_rating_template(args.bundle, rater_id=args.rater_id))
    return 0


def cmd_scenario_bundle_rate(args: argparse.Namespace) -> int:
    rating = read_json_object(
        args.rating,
        error_code="scenario-rating-read-failed",
        root_code="bad-scenario-rating",
        label="scenario rating",
    )
    _emit_scenario_bundle(
        record_scenario_bundle_rating(args.bundle, rating),
        args.format,
    )
    return 0


def cmd_scenario_bundle_masking_template(args: argparse.Namespace) -> int:
    emit(scenario_bundle_masking_template(args.bundle, assessor_id=args.assessor_id))
    return 0


def cmd_scenario_bundle_mask(args: argparse.Namespace) -> int:
    masking = read_json_object(
        args.masking,
        error_code="scenario-masking-read-failed",
        root_code="bad-scenario-masking-assessment",
        label="scenario masking assessment",
    )
    _emit_scenario_bundle(
        record_scenario_bundle_masking(args.bundle, masking),
        args.format,
    )
    return 0


def cmd_scenario_bundle_seal(args: argparse.Namespace) -> int:
    emit(seal_scenario_bundle_block(args.bundle))
    return 0


def cmd_scenario_bundle_unblind(args: argparse.Namespace) -> int:
    report = unblind_scenario_bundle(args.bundle)
    if args.format == "markdown":
        print(scenario_bundle_report_markdown(report))
    else:
        emit(report)
    return 0


def cmd_scenario_bundle_export(args: argparse.Namespace) -> int:
    report = scenario_bundle_report(args.bundle)
    if args.format == "markdown":
        print(scenario_bundle_report_markdown(report))
    elif args.format == "csv":
        print(scenario_bundle_report_csv(report), end="")
    else:
        emit(report)
    return 0


def _read_handoff_object(path: str | None, *, label: str) -> dict[str, Any] | None:
    if path is None:
        return None
    code_stem = label.replace(" ", "-")
    return read_json_object(
        path,
        error_code=f"{code_stem}-read-failed",
        root_code=f"bad-{code_stem}",
        label=label,
    )


def cmd_turn_plan(args: argparse.Namespace) -> int:
    packet = read_json_object(
        args.packet,
        error_code="turn-packet-read-failed",
        root_code="bad-turn-packet",
        label="turn packet",
    )
    plan = build_orchestration_plan(packet, mode=args.mode)
    if args.format == "markdown":
        print(orchestration_plan_markdown(plan))
    else:
        emit(plan)
    return 0


def cmd_turn_card(args: argparse.Namespace) -> int:
    packet = read_json_object(
        args.packet,
        error_code="turn-packet-read-failed",
        root_code="bad-turn-packet",
        label="turn packet",
    )
    card = build_turn_task_card(
        packet,
        role=args.role,
        planner_return=_read_handoff_object(args.planner_return, label="planner return"),
        narrator_return=_read_handoff_object(args.narrator_return, label="narrator return"),
        proposal=_read_handoff_object(args.proposal, label="turn proposal"),
    )
    if args.format == "markdown":
        print(turn_task_card_markdown(card))
    else:
        emit(card)
    return 0


def _emit_turn_run(manifest: dict[str, Any], format_name: str) -> None:
    if format_name == "markdown":
        print(turn_run_markdown(manifest))
    else:
        emit(manifest)


def cmd_turn_run_begin(args: argparse.Namespace) -> int:
    target = describe_model_reference(args.cube)
    with Cube.open(target["resolved_cube_path"]) as cube:
        manifest = begin_turn_run(
            cube,
            reference=target["reference"],
            resolved_cube_path=target["resolved_cube_path"],
            root=args.root,
            player_input=player_input_from_args(args),
            input_kind=args.input_kind,
            audience_id=args.audience_id,
            actor_id=args.actor_id,
            director=args.director,
            world_id=args.world_id,
            allow_anchor=args.allow_anchor,
            mode=args.mode,
            include_planner_context_on_commit=args.include_planner_context,
        )
    _emit_turn_run(manifest, args.format)
    return 0


def cmd_turn_run_status(args: argparse.Namespace) -> int:
    _emit_turn_run(audit_turn_run(args.run), args.format)
    return 0


def cmd_turn_run_recover(args: argparse.Namespace) -> int:
    _emit_turn_run(recover_turn_run(args.run), args.format)
    return 0


def cmd_turn_run_dispatch(args: argparse.Namespace) -> int:
    dispatch = build_turn_run_dispatch(args.run, provider=args.provider)
    if args.format == "markdown":
        print(turn_run_dispatch_markdown(dispatch))
    else:
        emit(dispatch)
    return 0


def cmd_play_start(args: argparse.Namespace) -> int:
    play_input = (
        "Will you DM?"
        if args.player_input is None and args.player_input_file is None
        else player_input_from_args(args)
    )
    result = start_play(
        args.reference,
        root=args.root,
        player_input=play_input,
        profile=args.profile,
        bootstrap=args.bootstrap,
        audience_id=args.audience_id,
        actor_id=args.actor_id,
        campaign_slug=args.campaign_slug,
        campaign_title=args.campaign_title,
        campaign_summary=args.campaign_summary,
    )
    if args.format == "markdown":
        print(play_start_markdown(result))
    else:
        emit(result)
    return 0


def _read_checkpoint_artifact(path: str, *, label: str) -> dict[str, Any]:
    code_stem = label.replace(" ", "-")
    return read_json_object(
        path,
        error_code=f"{code_stem}-read-failed",
        root_code=f"bad-{code_stem}",
        label=label,
    )


def cmd_checkpoint_begin(args: argparse.Namespace) -> int:
    with open_cube(args.cube) as cube:
        emit(
            build_checkpoint_request(
                cube,
                audience_id=args.audience_id,
                actor_id=args.actor_id,
                trigger=checkpoint_trigger_from_args(args),
                candidate_count=args.candidate_count,
                rollout_horizon_turns=args.rollout_horizon_turns,
                compression_max_chars=args.compression_max_chars,
                max_operations=args.max_operations,
            )
        )
    return 0


def cmd_checkpoint_card(args: argparse.Namespace) -> int:
    request = _read_checkpoint_artifact(args.request, label="checkpoint request")
    card = build_checkpoint_task_card(
        request,
        role=args.role,
        candidates_value=(
            _read_checkpoint_artifact(args.candidates, label="checkpoint candidates")
            if args.candidates
            else None
        ),
        judgment_value=(
            _read_checkpoint_artifact(args.judgment, label="checkpoint judgment")
            if args.judgment
            else None
        ),
        proposal_value=(
            _read_checkpoint_artifact(args.proposal, label="checkpoint proposal")
            if args.proposal
            else None
        ),
    )
    if args.format == "markdown":
        print(checkpoint_task_card_markdown(card))
    else:
        emit(card)
    return 0


def cmd_checkpoint_dispatch(args: argparse.Namespace) -> int:
    card = _read_checkpoint_artifact(args.card, label="checkpoint task card")
    dispatch = build_checkpoint_dispatch(card, provider=args.provider)
    if args.format == "markdown":
        print(checkpoint_dispatch_markdown(dispatch))
    else:
        emit(dispatch)
    return 0


def cmd_checkpoint_assemble(args: argparse.Namespace) -> int:
    emit(
        assemble_checkpoint_proposal(
            _read_checkpoint_artifact(args.request, label="checkpoint request"),
            _read_checkpoint_artifact(args.candidates, label="checkpoint candidates"),
            _read_checkpoint_artifact(args.judgment, label="checkpoint judgment"),
            _read_checkpoint_artifact(args.compression, label="checkpoint compression"),
        )
    )
    return 0


def cmd_checkpoint_review(args: argparse.Namespace) -> int:
    request = _read_checkpoint_artifact(args.request, label="checkpoint request")
    candidates = _read_checkpoint_artifact(args.candidates, label="checkpoint candidates")
    judgment = _read_checkpoint_artifact(args.judgment, label="checkpoint judgment")
    proposal = _read_checkpoint_artifact(args.proposal, label="checkpoint proposal")
    verifier = _read_checkpoint_artifact(args.verifier, label="checkpoint verifier return")
    with open_cube(args.cube) as cube:
        emit(review_checkpoint(cube, request, candidates, judgment, proposal, verifier))
    return 0


def cmd_checkpoint_commit(args: argparse.Namespace) -> int:
    request = _read_checkpoint_artifact(args.request, label="checkpoint request")
    candidates = _read_checkpoint_artifact(args.candidates, label="checkpoint candidates")
    judgment = _read_checkpoint_artifact(args.judgment, label="checkpoint judgment")
    proposal = _read_checkpoint_artifact(args.proposal, label="checkpoint proposal")
    verifier = _read_checkpoint_artifact(args.verifier, label="checkpoint verifier return")
    review = _read_checkpoint_artifact(args.review, label="checkpoint review")
    with open_cube(args.cube) as cube:
        emit(commit_checkpoint(cube, request, candidates, judgment, proposal, verifier, review))
    return 0


def _emit_checkpoint_run(manifest: dict[str, Any], format_name: str) -> None:
    if format_name == "markdown":
        print(checkpoint_run_markdown(manifest))
    else:
        emit(manifest)


def cmd_checkpoint_run_begin(args: argparse.Namespace) -> int:
    target = describe_model_reference(args.cube)
    routes = normalize_checkpoint_provider_routes(
        provider=args.provider,
        generator_provider=args.generator_provider,
        judge_provider=args.judge_provider,
        compressor_provider=args.compressor_provider,
        verifier_provider=args.verifier_provider,
    )
    with Cube.open(target["resolved_cube_path"]) as cube:
        manifest = begin_checkpoint_run(
            cube,
            reference=target["reference"],
            resolved_cube_path=target["resolved_cube_path"],
            root=args.root,
            audience_id=args.audience_id,
            actor_id=args.actor_id,
            trigger=checkpoint_trigger_from_args(args),
            candidate_count=args.candidate_count,
            rollout_horizon_turns=args.rollout_horizon_turns,
            compression_max_chars=args.compression_max_chars,
            max_operations=args.max_operations,
            provider_routes=routes,
        )
    _emit_checkpoint_run(manifest, args.format)
    return 0


def cmd_checkpoint_run_status(args: argparse.Namespace) -> int:
    _emit_checkpoint_run(audit_checkpoint_run(args.run), args.format)
    return 0


def cmd_checkpoint_run_recover(args: argparse.Namespace) -> int:
    _emit_checkpoint_run(recover_checkpoint_run(args.run), args.format)
    return 0


def cmd_checkpoint_run_dispatch(args: argparse.Namespace) -> int:
    dispatch = build_checkpoint_run_dispatch(args.run)
    if args.format == "markdown":
        print(checkpoint_run_dispatch_markdown(dispatch))
    else:
        emit(dispatch)
    return 0


def cmd_checkpoint_run_next_turn(args: argparse.Namespace) -> int:
    public_history = None
    if args.public_history is not None:
        public_history = read_json_object(
            args.public_history,
            error_code="public-history-read-failed",
            root_code="bad-public-history",
            label="public history",
        )
    dispatch = begin_checkpoint_continuation_turn(
        args.checkpoint_run,
        player_input=player_input_from_args(args),
        root=args.root,
        provider=args.provider,
        public_history=public_history,
    )
    if args.format == "markdown":
        print(checkpoint_continuation_dispatch_markdown(dispatch))
    else:
        emit(dispatch)
    return 0


def cmd_checkpoint_run_continuation(args: argparse.Namespace) -> int:
    public_history = None
    if args.public_history is not None:
        public_history = read_json_object(
            args.public_history,
            error_code="public-history-read-failed",
            root_code="bad-public-history",
            label="public history",
        )
    dispatch = build_checkpoint_continuation_dispatch(
        args.checkpoint_run,
        args.turn_run,
        provider=args.provider,
        public_history=public_history,
    )
    if args.format == "markdown":
        print(checkpoint_continuation_dispatch_markdown(dispatch))
    else:
        emit(dispatch)
    return 0


def cmd_history_build(args: argparse.Namespace) -> int:
    history = build_public_history(args.turn_runs)
    if args.format == "markdown":
        print(public_history_markdown(history))
    else:
        emit(history)
    return 0


def cmd_history_complete(args: argparse.Namespace) -> int:
    manifest = audit_checkpoint_run(args.checkpoint_run)
    boundary = committed_checkpoint_history_boundary(args.checkpoint_run)
    with Cube.open(manifest["resolved_cube_path"]) as cube:
        history = build_complete_public_history(
            cube,
            checkpoint_boundary=boundary,
            run_roots=args.run_roots,
        )
    if args.format == "markdown":
        print(public_history_markdown(history))
    else:
        emit(history)
    return 0


def cmd_checkpoint_run_accept(args: argparse.Namespace) -> int:
    artifact = read_json_object(
        args.artifact,
        error_code="checkpoint-run-artifact-read-failed",
        root_code="bad-checkpoint-run-artifact",
        label="checkpoint run artifact",
    )
    manifest = accept_checkpoint_run_artifact(
        args.run,
        artifact,
        model=args.model,
        model_version=args.model_version,
        invocation_id=args.invocation_id,
        started_at=args.started_at,
        completed_at=args.completed_at,
        duration_ms=args.duration_ms,
    )
    _emit_checkpoint_run(manifest, args.format)
    return 0


def cmd_checkpoint_run_record_failure(args: argparse.Namespace) -> int:
    manifest = record_checkpoint_run_failure(
        args.run,
        failure_class=args.failure_class,
        failure_message=args.failure_message,
        model=args.model,
        model_version=args.model_version,
        invocation_id=args.invocation_id,
        started_at=args.started_at,
        completed_at=args.completed_at,
        duration_ms=args.duration_ms,
    )
    _emit_checkpoint_run(manifest, args.format)
    return 0


def cmd_checkpoint_run_narrator_capsule(args: argparse.Namespace) -> int:
    capsule = build_checkpoint_run_narrator_capsule(args.run)
    if args.format == "markdown":
        print(checkpoint_narrator_capsule_markdown(capsule))
    else:
        emit(capsule)
    return 0


def cmd_checkpoint_run_commit(args: argparse.Namespace) -> int:
    receipt = commit_checkpoint_run(args.run)
    if args.format == "markdown":
        print(checkpoint_run_receipt_markdown(receipt))
    else:
        emit(receipt)
    return 0


def cmd_turn_run_accept(args: argparse.Namespace) -> int:
    artifact = read_json_object(
        args.artifact,
        error_code="turn-run-artifact-read-failed",
        root_code="bad-turn-run-artifact",
        label="turn run artifact",
    )
    manifest = accept_turn_run_artifact(args.run, artifact)
    _emit_turn_run(manifest, args.format)
    return 0


def cmd_turn_run_commit(args: argparse.Namespace) -> int:
    receipt = commit_turn_run(args.run)
    if args.format == "markdown":
        print(turn_receipt_markdown(receipt))
    else:
        emit(receipt)
    return 0


def cmd_seal_prepare(args: argparse.Namespace) -> int:
    payload = read_json_value_file(args.payload, error_code="seal-payload-read-failed")
    with open_cube(args.cube) as cube:
        seal_id = args.seal_id or new_id("seal")
        if cube._exists("fair_play_seals", "seal_id", seal_id):
            raise LacunaError(
                "duplicate-precommitment-seal",
                f"precommitment seal {seal_id!r} already exists",
            )
        opening = prepare_seal_opening(
            cube_id=cube.meta("cube_id"),
            seal_id=seal_id,
            payload=payload,
            nonce=args.nonce,
        )
        emit(opening)
    return 0


def _opening_for_cube(cube: Cube, path: str) -> dict[str, Any]:
    opening = parse_seal_opening(
        read_json_value_file(path, error_code="seal-opening-read-failed")
    )
    if opening["cube_id"] != cube.meta("cube_id"):
        raise LacunaError(
            "seal-opening-cube-mismatch",
            "seal opening belongs to a different cube",
            {
                "opening_cube_id": opening["cube_id"],
                "cube_id": cube.meta("cube_id"),
            },
        )
    return opening


def cmd_seal_create(args: argparse.Namespace) -> int:
    with open_cube(args.cube) as cube:
        opening = _opening_for_cube(cube, args.opening)
        change = single_op(
            cube,
            args.actor,
            {
                "op": "seal_precommitment",
                "seal_id": opening["seal_id"],
                "commitment_sha256": opening["commitment_sha256"],
                "scheme": opening["scheme"],
                "label": args.label or opening["seal_id"],
                "purpose": args.purpose,
                "visibility": args.visibility,
                "audience": args.audience,
                "source_id": args.source_id,
            },
            "register a fair-play precommitment digest",
        )
        emit(
            {
                "event": "lacuna.fair-play-seal.created",
                "schema": "lacuna.fair-play-seal-created.v1",
                "change": change,
                "receipt": cube.seal_receipt(opening["seal_id"]),
                "custody_warning": (
                    "The opening was not written to the cube. Keep the opening file secret "
                    "and retain or externally anchor the receipt before relying on it against equivocation."
                ),
            }
        )
    return 0


def cmd_seal_list(args: argparse.Namespace) -> int:
    with open_cube(args.cube) as cube:
        seals = cube.seals(agent_id=args.agent_id, status=args.status)
        emit(
            {
                "event": "lacuna.fair-play-seals",
                "schema": "lacuna.fair-play-seals.v1",
                "cube_id": cube.meta("cube_id"),
                "head": cube.head(),
                "agent_id": args.agent_id,
                "seal_count": len(seals),
                "seals": seals,
            }
        )
    return 0


def cmd_seal_receipt(args: argparse.Namespace) -> int:
    with open_cube(args.cube) as cube:
        emit(cube.seal_receipt(args.seal_id, agent_id=args.agent_id))
    return 0


def cmd_seal_verify(args: argparse.Namespace) -> int:
    with open_cube(args.cube) as cube:
        opening = read_json_value_file(
            args.opening, error_code="seal-opening-read-failed"
        )
        report = cube.verify_seal_opening(opening, agent_id=args.agent_id)
        emit(report)
        return 0 if report["overall_status"] == "pass" else 1


def cmd_seal_reveal(args: argparse.Namespace) -> int:
    with open_cube(args.cube) as cube:
        opening = _opening_for_cube(cube, args.opening)
        change = single_op(
            cube,
            args.actor,
            {
                "op": "reveal_precommitment",
                "seal_id": opening["seal_id"],
                "nonce": opening["nonce"],
                "payload": opening["payload"],
                "reason": args.reason,
            },
            "reveal a fair-play precommitment opening",
        )
        emit(
            {
                "event": "lacuna.fair-play-seal.revealed",
                "schema": "lacuna.fair-play-seal-revealed.v1",
                "change": change,
                "receipt": cube.seal_receipt(opening["seal_id"]),
            }
        )
    return 0


def cmd_seal_void(args: argparse.Namespace) -> int:
    with open_cube(args.cube) as cube:
        change = single_op(
            cube,
            args.actor,
            {
                "op": "void_precommitment",
                "seal_id": args.seal_id,
                "reason": args.reason,
            },
            "void an unopened fair-play precommitment",
        )
        emit(
            {
                "event": "lacuna.fair-play-seal.voided",
                "schema": "lacuna.fair-play-seal-voided.v1",
                "change": change,
                "receipt": cube.seal_receipt(args.seal_id),
            }
        )
    return 0


def cmd_agent_add(args: argparse.Namespace) -> int:
    with open_cube(args.cube) as cube:
        agent_id = args.agent_id or new_id("agt")
        receipt = single_op(
            cube,
            args.actor,
            {"op": "register_agent", "agent_id": agent_id, "kind": args.kind, "label": args.label or agent_id, "metadata": {}},
            f"register agent {agent_id}",
        )
        receipt["agent_id"] = agent_id
        emit(receipt)
    return 0


def cmd_source_add(args: argparse.Namespace) -> int:
    with open_cube(args.cube) as cube:
        source_id = args.source_id or new_id("src")
        receipt = single_op(
            cube,
            args.actor,
            {
                "op": "add_source",
                "source_id": source_id,
                "kind": args.kind,
                "label": args.label or source_id,
                "locator": args.locator,
                "content_sha256": args.content_sha256,
                "metadata": {},
            },
            f"add source {source_id}",
        )
        receipt["source_id"] = source_id
        emit(receipt)
    return 0


def cmd_claim_add(args: argparse.Namespace) -> int:
    object_value = parse_json_value(args.object_json)
    claim_id = deterministic_claim_id(args.subject, args.predicate, object_value, args.scope)
    with open_cube(args.cube) as cube:
        receipt = single_op(
            cube,
            args.actor,
            {
                "op": "declare_claim",
                "claim_id": claim_id,
                "subject": args.subject,
                "predicate": args.predicate,
                "object": object_value,
                "scope": args.scope,
            },
            f"declare claim {claim_id}",
        )
        receipt["claim_id"] = claim_id
        emit(receipt)
    return 0


def cmd_relation_add(args: argparse.Namespace) -> int:
    relation_id = args.relation_id or new_id("rel")
    with open_cube(args.cube) as cube:
        receipt = single_op(
            cube,
            args.actor,
            {
                "op": "declare_relation",
                "relation_id": relation_id,
                "left_claim_id": args.left_claim_id,
                "right_claim_id": args.right_claim_id,
                "relation": args.relation,
                "source_id": args.source_id,
                "rationale": args.rationale,
            },
            f"declare claim relation {relation_id}",
        )
        receipt["relation_id"] = relation_id
        emit(receipt)
    return 0


def cmd_relation_retire(args: argparse.Namespace) -> int:
    with open_cube(args.cube) as cube:
        emit(
            single_op(
                cube,
                args.actor,
                {"op": "retire_relation", "relation_id": args.relation_id, "reason": args.reason},
                f"retire claim relation {args.relation_id}",
            )
        )
    return 0


def cmd_cardinality_add(args: argparse.Namespace) -> int:
    constraint_id = args.constraint_id or new_id("crd")
    with open_cube(args.cube) as cube:
        receipt = single_op(
            cube,
            args.actor,
            {
                "op": "declare_cardinality",
                "constraint_id": constraint_id,
                "label": args.label or constraint_id,
                "claim_ids": args.claim_ids,
                "min_true": args.min_true,
                "max_true": args.max_true,
                "source_id": args.source_id,
                "rationale": args.rationale,
            },
            f"declare cardinality constraint {constraint_id}",
        )
        receipt["constraint_id"] = constraint_id
        emit(receipt)
    return 0


def cmd_cardinality_retire(args: argparse.Namespace) -> int:
    with open_cube(args.cube) as cube:
        emit(
            single_op(
                cube,
                args.actor,
                {
                    "op": "retire_cardinality",
                    "constraint_id": args.constraint_id,
                    "reason": args.reason,
                },
                f"retire cardinality constraint {args.constraint_id}",
            )
        )
    return 0


def cmd_assert(args: argparse.Namespace) -> int:
    assertion_id = args.assertion_id or new_id("ast")
    operation = {
        "op": "record_assertion",
        "assertion_id": assertion_id,
        "claim_id": args.claim_id,
        "assertor_id": args.assertor_id,
        "perspective_id": args.perspective_id or args.assertor_id,
        "source_id": args.source_id,
        "stance": args.stance,
        "basis": args.basis,
        "standing": args.standing,
        "confidence": args.confidence,
        "visibility": args.visibility,
        "audience": args.audience,
        "timeline_id": args.timeline_id,
        "valid_from": args.valid_from,
        "valid_to": args.valid_to,
        "note": args.note,
        "supersedes_id": args.supersedes_id,
    }
    with open_cube(args.cube) as cube:
        receipt = single_op(cube, args.actor, operation, f"record assertion {assertion_id}")
        receipt["assertion_id"] = assertion_id
        emit(receipt)
    return 0


def cmd_assertion_supersede(args: argparse.Namespace) -> int:
    with open_cube(args.cube) as cube:
        emit(
            single_op(
                cube,
                args.actor,
                {"op": "supersede_assertion", "assertion_id": args.assertion_id, "reason": args.reason},
                f"supersede assertion {args.assertion_id}",
            )
        )
    return 0


def cmd_world_add(args: argparse.Namespace) -> int:
    world_id = args.world_id or new_id("wld")
    with open_cube(args.cube) as cube:
        receipt = single_op(
            cube,
            args.actor,
            {
                "op": "create_world",
                "world_id": world_id,
                "label": args.label or world_id,
                "parent_world_id": args.parent_world_id,
                "status": args.status,
                "weight": args.weight,
                "rationale": args.rationale,
            },
            f"create world {world_id}",
        )
        receipt["world_id"] = world_id
        emit(receipt)
    return 0


def cmd_world_assign(args: argparse.Namespace) -> int:
    assignment_id = args.assignment_id or new_id("asn")
    with open_cube(args.cube) as cube:
        receipt = single_op(
            cube,
            args.actor,
            {
                "op": "assign_world",
                "assignment_id": assignment_id,
                "world_id": args.world_id,
                "claim_id": args.claim_id,
                "truth": args.truth,
                "commitment": args.commitment,
                "commitment_basis": args.commitment_basis,
                "commitment_source_id": args.commitment_source_id,
                "confidence": args.confidence,
                "rationale": args.rationale,
                "source_assertion_id": args.source_assertion_id,
                "timeline_id": args.timeline_id,
                "valid_from": args.valid_from,
                "valid_to": args.valid_to,
            },
            f"assign {args.claim_id} in {args.world_id}",
        )
        receipt["assignment_id"] = assignment_id
        emit(receipt)
    return 0


def cmd_world_revise(args: argparse.Namespace) -> int:
    assignment_id = args.assignment_id or new_id("asn")
    with open_cube(args.cube) as cube:
        receipt = single_op(
            cube,
            args.actor,
            {
                "op": "revise_world",
                "assignment_id": assignment_id,
                "revises_assignment_id": args.revises_assignment_id,
                "truth": args.truth,
                "commitment": args.commitment,
                "commitment_basis": args.commitment_basis,
                "commitment_source_id": args.commitment_source_id,
                "confidence": args.confidence,
                "rationale": args.rationale,
                "source_assertion_id": args.source_assertion_id,
                "expected_impact_sha256": args.expected_impact_sha256,
                "reason": args.reason,
            },
            f"revise world assignment {args.revises_assignment_id}",
        )
        receipt["assignment_id"] = assignment_id
        emit(receipt)
    return 0


def cmd_commitment_raise(args: argparse.Namespace) -> int:
    transition_id = args.transition_id or new_id("cmt")
    with open_cube(args.cube) as cube:
        receipt = single_op(
            cube,
            args.actor,
            {
                "op": "raise_commitment",
                "transition_id": transition_id,
                "assignment_id": args.assignment_id,
                "commitment": args.commitment,
                "basis": args.basis,
                "source_id": args.source_id,
                "rationale": args.rationale,
            },
            f"raise commitment for {args.assignment_id}",
        )
        receipt["transition_id"] = transition_id
        emit(receipt)
    return 0


def cmd_consequence_link(args: argparse.Namespace) -> int:
    consequence_id = args.consequence_id or new_id("csq")
    with open_cube(args.cube) as cube:
        receipt = single_op(
            cube,
            args.actor,
            {
                "op": "link_consequence",
                "consequence_id": consequence_id,
                "premise_assignment_id": args.premise_assignment_id,
                "dependent_kind": args.dependent_kind,
                "dependent_id": args.dependent_id,
                "relation": args.relation,
                "severity": args.severity,
                "source_id": args.source_id,
                "rationale": args.rationale,
            },
            f"link consequence {consequence_id}",
        )
        receipt["consequence_id"] = consequence_id
        emit(receipt)
    return 0


def cmd_consequence_replace(args: argparse.Namespace) -> int:
    consequence_id = args.consequence_id or new_id("csq")
    repair_id = args.repair_id or new_id("cpr")
    with open_cube(args.cube) as cube:
        receipt = single_op(
            cube,
            args.actor,
            {
                "op": "replace_consequence",
                "repair_id": repair_id,
                "consequence_id": consequence_id,
                "replaces_consequence_id": args.replaces_consequence_id,
                "premise_assignment_id": args.premise_assignment_id,
                "dependent_kind": args.dependent_kind,
                "dependent_id": args.dependent_id,
                "relation": args.relation,
                "severity": args.severity,
                "source_id": args.source_id,
                "rationale": args.rationale,
                "expected_repair_sha256": args.expected_repair_sha256,
                "reason": args.reason,
            },
            f"replace consequence {args.replaces_consequence_id} with {consequence_id}",
        )
        receipt["repair_id"] = repair_id
        receipt["consequence_id"] = consequence_id
        receipt["replaces_consequence_id"] = args.replaces_consequence_id
        emit(receipt)
    return 0


def cmd_consequence_retire(args: argparse.Namespace) -> int:
    with open_cube(args.cube) as cube:
        emit(
            single_op(
                cube,
                args.actor,
                {
                    "op": "retire_consequence",
                    "consequence_id": args.consequence_id,
                    "reason": args.reason,
                },
                f"retire consequence {args.consequence_id}",
            )
        )
    return 0


def cmd_particle_update(args: argparse.Namespace) -> int:
    update_id = args.update_id or new_id("pup")
    with open_cube(args.cube) as cube:
        receipt = single_op(
            cube,
            args.actor,
            {
                "op": "update_particle_bank",
                "update_id": update_id,
                "evidence_assertion_id": args.evidence_assertion_id,
                "expected_bank_sha256": args.expected_bank_sha256,
                "assessments": args.assessments,
                "reason": args.reason,
            },
            f"update particle bank from {args.evidence_assertion_id}",
        )
        receipt["update_id"] = update_id
        emit(receipt)
    return 0


def cmd_particle_reconcile(args: argparse.Namespace) -> int:
    reconciliation_id = args.reconciliation_id or new_id("prc")
    with open_cube(args.cube) as cube:
        receipt = single_op(
            cube,
            args.actor,
            {
                "op": "reconcile_particle_bank",
                "reconciliation_id": reconciliation_id,
                "expected_reconciliation_sha256": args.expected_reconciliation_sha256,
                "reason": args.reason,
            },
            f"reconcile particle factor ledger as {reconciliation_id}",
        )
        receipt["reconciliation_id"] = reconciliation_id
        emit(receipt)
    return 0


def cmd_world_weight(args: argparse.Namespace) -> int:
    with open_cube(args.cube) as cube:
        emit(
            single_op(
                cube,
                args.actor,
                {"op": "set_world_weight", "world_id": args.world_id, "weight": args.weight, "reason": args.reason},
                f"reweight world {args.world_id}",
            )
        )
    return 0


def cmd_world_status(args: argparse.Namespace) -> int:
    with open_cube(args.cube) as cube:
        emit(
            single_op(
                cube,
                args.actor,
                {"op": "set_world_status", "world_id": args.world_id, "status": args.status, "reason": args.reason},
                f"set world status {args.world_id}",
            )
        )
    return 0


def cmd_evidence_link(args: argparse.Namespace) -> int:
    link_id = args.link_id or new_id("evl")
    with open_cube(args.cube) as cube:
        receipt = single_op(
            cube,
            args.actor,
            {
                "op": "link_evidence",
                "link_id": link_id,
                "evidence_assertion_id": args.evidence_assertion_id,
                "target_claim_id": args.target_claim_id,
                "world_id": args.world_id,
                "relation": args.relation,
                "strength": args.strength,
                "rationale": args.rationale,
            },
            f"link evidence {link_id}",
        )
        receipt["link_id"] = link_id
        emit(receipt)
    return 0


def cmd_question_open(args: argparse.Namespace) -> int:
    question_id = args.question_id or new_id("qst")
    with open_cube(args.cube) as cube:
        receipt = single_op(
            cube,
            args.actor,
            {
                "op": "open_question",
                "question_id": question_id,
                "text": args.text,
                "about_claim_id": args.about_claim_id,
                "opened_by": args.opened_by,
                "visibility": args.visibility,
                "audience": args.audience,
            },
            f"open question {question_id}",
        )
        receipt["question_id"] = question_id
        emit(receipt)
    return 0


def cmd_question_close(args: argparse.Namespace) -> int:
    with open_cube(args.cube) as cube:
        emit(
            single_op(
                cube,
                args.actor,
                {
                    "op": "close_question",
                    "question_id": args.question_id,
                    "resolution_assertion_id": args.resolution_assertion_id,
                    "reason": args.reason,
                },
                f"close question {args.question_id}",
            )
        )
    return 0


def demo_operations() -> list[dict[str, Any]]:
    claims = [
        ("bell", "rang_at_tick", 10, "event"),
        ("innkeeper", "voice_trembled", True, "event"),
        ("innkeeper", "is_lost_prince", True, "world"),
        ("broken_cup", "was_deliberate_signal", True, "world"),
        ("innkeeper", "knows_player_identity", True, "world"),
        ("storm", "arrives_before_dawn", True, "world"),
    ]
    claim_ids = {
        (subject, predicate): deterministic_claim_id(subject, predicate, obj, scope)
        for subject, predicate, obj, scope in claims
    }
    operations: list[dict[str, Any]] = [
        {"op": "register_agent", "agent_id": "narrator", "kind": "narrator", "label": "Narrator", "metadata": {}},
        {"op": "register_agent", "agent_id": "player", "kind": "human", "label": "Player", "metadata": {}},
        {"op": "register_agent", "agent_id": "innkeeper", "kind": "character", "label": "The Innkeeper", "metadata": {}},
        {"op": "add_source", "source_id": "scene.001", "kind": "scene", "label": "The Lantern Room", "metadata": {}},
        {"op": "add_source", "source_id": "utterance.001", "kind": "utterance", "label": "The innkeeper's warning", "metadata": {}},
    ]
    for subject, predicate, obj, scope in claims:
        operations.append(
            {
                "op": "declare_claim",
                "claim_id": deterministic_claim_id(subject, predicate, obj, scope),
                "subject": subject,
                "predicate": predicate,
                "object": obj,
                "scope": scope,
            }
        )
    operations.extend(
        [
            {
                "op": "record_assertion",
                "assertion_id": "ast.bell.observed",
                "claim_id": claim_ids[("bell", "rang_at_tick")],
                "assertor_id": "narrator",
                "perspective_id": "narrator",
                "source_id": "scene.001",
                "stance": "true",
                "basis": "observation",
                "standing": "anchored",
                "confidence": 1.0,
                "visibility": "public",
                "timeline_id": "main",
                "valid_from": 10,
                "valid_to": 10,
                "note": "The player heard the bell ring.",
            },
            {
                "op": "record_assertion",
                "assertion_id": "ast.voice.observed",
                "claim_id": claim_ids[("innkeeper", "voice_trembled")],
                "assertor_id": "narrator",
                "perspective_id": "narrator",
                "source_id": "scene.001",
                "stance": "true",
                "basis": "observation",
                "standing": "anchored",
                "confidence": 1.0,
                "visibility": "public",
                "note": "The innkeeper's voice audibly trembled; its cause remains unsettled.",
            },
            {
                "op": "record_assertion",
                "assertion_id": "ast.storm.warning",
                "claim_id": claim_ids[("storm", "arrives_before_dawn")],
                "assertor_id": "innkeeper",
                "perspective_id": "innkeeper",
                "source_id": "utterance.001",
                "stance": "true",
                "basis": "testimony",
                "standing": "reported",
                "confidence": 0.7,
                "visibility": "public",
                "note": "The innkeeper says a storm will arrive before dawn.",
            },
            {
                "op": "record_assertion",
                "assertion_id": "ast.player.cup-suspicion",
                "claim_id": claim_ids[("broken_cup", "was_deliberate_signal")],
                "assertor_id": "player",
                "perspective_id": "player",
                "source_id": "scene.001",
                "stance": "true",
                "basis": "belief",
                "standing": "accepted",
                "confidence": 0.58,
                "visibility": "private",
                "note": "The player suspects the cup was a signal.",
            },
            {
                "op": "create_world",
                "world_id": "world.ordinary",
                "label": "Ordinary accident",
                "status": "live",
                "weight": 0.55,
                "rationale": "The innkeeper is ordinary and the cup broke by accident.",
            },
            {
                "op": "create_world",
                "world_id": "world.heir",
                "label": "The hidden heir",
                "status": "live",
                "weight": 0.25,
                "rationale": "The innkeeper is the lost prince and used the cup as a signal.",
            },
            {
                "op": "create_world",
                "world_id": "world.spy",
                "label": "The watcher",
                "status": "live",
                "weight": 0.20,
                "rationale": "The innkeeper is not the prince but recognized the player and signaled an observer.",
            },
        ]
    )
    assignments = {
        "world.ordinary": [("is_lost_prince", "false"), ("was_deliberate_signal", "false"), ("knows_player_identity", "false")],
        "world.heir": [("is_lost_prince", "true"), ("was_deliberate_signal", "true"), ("knows_player_identity", "true")],
        "world.spy": [("is_lost_prince", "false"), ("was_deliberate_signal", "true"), ("knows_player_identity", "true")],
    }
    predicate_to_subject = {
        "is_lost_prince": "innkeeper",
        "was_deliberate_signal": "broken_cup",
        "knows_player_identity": "innkeeper",
    }
    for world_id, items in assignments.items():
        for predicate, truth in items:
            subject = predicate_to_subject[predicate]
            operations.append(
                {
                    "op": "assign_world",
                    "world_id": world_id,
                    "claim_id": claim_ids[(subject, predicate)],
                    "truth": truth,
                    "commitment": "soft",
                    "confidence": 0.75,
                    "rationale": "Demonstration assignment; revisable until consequences anchor it.",
                }
            )
    operations.extend(
        [
            {
                "op": "link_evidence",
                "link_id": "evl.voice.heir",
                "evidence_assertion_id": "ast.voice.observed",
                "target_claim_id": claim_ids[("innkeeper", "is_lost_prince")],
                "world_id": "world.heir",
                "relation": "supports",
                "strength": 0.45,
                "rationale": "In the hidden-heir hypothesis, the tremor is compatible with fear of recognition.",
            },
            {
                "op": "link_evidence",
                "link_id": "evl.voice.spy",
                "evidence_assertion_id": "ast.voice.observed",
                "target_claim_id": claim_ids[("innkeeper", "knows_player_identity")],
                "world_id": "world.spy",
                "relation": "supports",
                "strength": 0.55,
                "rationale": "In the watcher hypothesis, the tremor is compatible with recognizing the player.",
            },
        ]
    )
    operations.append(
        {
            "op": "open_question",
            "question_id": "qst.cup",
            "text": "Why did the cup break?",
            "about_claim_id": claim_ids[("broken_cup", "was_deliberate_signal")],
            "opened_by": "player",
            "visibility": "public",
        }
    )
    return operations


def cmd_demo(args: argparse.Namespace) -> int:
    path = Path(args.cube)
    if not path.exists():
        with Cube.init(path, owner_id="user", owner_label="User"):
            pass
    with open_cube(args.cube) as cube:
        if cube.has_active_agent("narrator"):
            raise LacunaError("demo-already-present", "this cube already contains the lantern demonstration")
        receipt = cube.apply_operations(actor_id="user", operations=demo_operations(), message="seed the lantern epistemic demonstration")
        receipt["demo"] = "lantern"
        emit(receipt)
    return 0


def add_actor(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--actor", default="user", help="registered agent applying the change (default: user)")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="lacuna",
        description="Lacuna — an epistemic ledger for worlds that have not finished becoming true.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("init", help="initialize a bare cube directory")
    p.add_argument("cube")
    p.add_argument("--owner-id", default="user")
    p.add_argument("--owner-label", default="User")
    p.set_defaults(func=cmd_init)

    p = sub.add_parser("migrate", help="apply a supported forward database migration without rewriting the ledger")
    p.add_argument("cube", help="cube path, or a library path with a selected campaign")
    p.set_defaults(func=cmd_migrate)

    artifact = sub.add_parser(
        "artifact",
        help="audit one extracted Lacuna release without mutating a cube",
    )
    artifact_sub = artifact.add_subparsers(dest="artifact_command", required=True)
    p = artifact_sub.add_parser(
        "check",
        help="verify manifest members, versions, source syntax, documents, and relative links",
    )
    p.add_argument("root", nargs="?", help="extracted release root; defaults to this launcher root")
    p.add_argument("--strict-members", action="store_true", help="fail on every unlisted regular file")
    p.add_argument("--format", choices=["json", "markdown"], default="markdown")
    p.set_defaults(func=cmd_artifact_check)

    campaign = sub.add_parser("campaign", help="create, list, and select human-facing campaigns")
    campaign_sub = campaign.add_subparsers(dest="campaign_command", required=True)

    p = campaign_sub.add_parser("init", help="initialize an empty campaign library")
    p.add_argument("library")
    p.set_defaults(func=cmd_campaign_init)

    p = campaign_sub.add_parser("create", help="create a campaign and its epistemic cube")
    p.add_argument("library")
    p.add_argument("slug")
    p.add_argument("--title")
    p.add_argument("--summary")
    p.add_argument("--owner-id", default="user")
    p.add_argument("--owner-label", default="User")
    p.add_argument("--player-id", default="player")
    p.add_argument("--player-label", default="Player")
    p.add_argument("--narrator-id", default="narrator")
    p.add_argument("--narrator-label", default="Narrator")
    p.set_defaults(func=cmd_campaign_create)

    p = campaign_sub.add_parser("list", help="list campaigns; the selected campaign is marked with *")
    p.add_argument("library")
    p.add_argument("--format", choices=["table", "json"], default="table")
    p.set_defaults(func=cmd_campaign_list)

    p = campaign_sub.add_parser("select", help="select a campaign by slug or campaign ID")
    p.add_argument("library")
    p.add_argument("selector")
    p.set_defaults(func=cmd_campaign_select)

    p = campaign_sub.add_parser("show", help="show a selected or named campaign")
    p.add_argument("library")
    p.add_argument("selector", nargs="?")
    p.set_defaults(func=cmd_campaign_show)

    p = campaign_sub.add_parser("path", help="print the cube path for a selected or named campaign")
    p.add_argument("library")
    p.add_argument("selector", nargs="?")
    p.set_defaults(func=cmd_campaign_path)

    model = sub.add_parser(
        "model",
        help="emit a portable entrance brief for chat, workspace, or orchestrated model hosts",
    )
    model_sub = model.add_subparsers(dest="model_command", required=True)

    p = model_sub.add_parser(
        "brief",
        help="inspect readiness and emit exact model/host instructions without mutating the cube",
    )
    p.add_argument("cube", help="cube path, or a library path with a selected campaign")
    p.add_argument("--profile", choices=MODEL_PROFILES, default="workspace")
    p.add_argument("--audience-id")
    p.add_argument("--actor-id")
    p.add_argument("--format", choices=["json", "markdown"], default="markdown")
    p.set_defaults(func=cmd_model_brief)

    play = sub.add_parser(
        "play",
        help="turn one exact session-control sentence into a governed resumable play run",
    )
    play_sub = play.add_subparsers(dest="play_command", required=True)
    p = play_sub.add_parser(
        "start",
        help="bootstrap or resume a campaign and open the exact message as session control",
    )
    p.add_argument("reference", nargs="?", default=".lacuna-play", help="cube or campaign-library path")
    p.add_argument("--root", default=".lacuna-runs", help="turn-run root")
    p.add_argument("--profile", choices=MODEL_PROFILES, default="orchestrated")
    p.add_argument("--bootstrap", action="store_true", help="initialize an empty path and create a default campaign when needed")
    p.add_argument("--audience-id")
    p.add_argument("--actor-id")
    input_group = p.add_mutually_exclusive_group(required=False)
    input_group.add_argument("--player-input")
    input_group.add_argument("--player-input-file", help="UTF-8 file containing the exact session-control message; use - for stdin")
    p.add_argument("--campaign-slug", default="first-lacuna")
    p.add_argument("--campaign-title", default="First Lacuna")
    p.add_argument("--campaign-summary", default="A campaign bootstrapped from a direct request to play.")
    p.add_argument("--format", choices=["json", "markdown"], default="markdown")
    p.set_defaults(func=cmd_play_start)

    history = sub.add_parser(
        "history",
        help="compile exact player-visible text from audited committed turn runs",
    )
    history_sub = history.add_subparsers(dest="history_command", required=True)
    p = history_sub.add_parser(
        "build",
        help="build one explicit ordered public history without claiming completeness",
    )
    p.add_argument(
        "turn_runs",
        nargs="+",
        help="committed turn run directories or run.json paths, oldest first",
    )
    p.add_argument("--format", choices=["json", "markdown"], default="json")
    p.set_defaults(func=cmd_history_build)

    p = history_sub.add_parser(
        "complete",
        help="prove complete durable audience-turn coverage before one committed checkpoint",
    )
    p.add_argument(
        "checkpoint_run",
        help="committed checkpoint run directory or run.json path",
    )
    p.add_argument(
        "--run-root",
        dest="run_roots",
        action="append",
        default=[],
        help="turn-run root or committed turn-run directory to scan; repeat as needed (may be omitted only when the census is empty)",
    )
    p.add_argument("--format", choices=["json", "markdown"], default="json")
    p.set_defaults(func=cmd_history_complete)

    scenario = sub.add_parser(
        "scenario",
        help="run a fixed four-condition comparative retcon-planning experiment",
    )
    scenario_sub = scenario.add_subparsers(dest="scenario_command", required=True)

    p = scenario_sub.add_parser(
        "template",
        help="bind an editable comparative scenario capsule template to one verified seed cube",
    )
    p.add_argument("cube", help="cube path, or a library path with a selected campaign")
    p.add_argument("--title", default="Retcon planning comparison")
    p.add_argument(
        "--research-question",
        default="Does source-bound retcon planning improve an off-script continuation without producing rubber reality?",
    )
    p.set_defaults(func=cmd_scenario_template)

    p = scenario_sub.add_parser(
        "begin",
        help="freeze a capsule, commit a hidden condition assignment, and publish four exact seed clones",
    )
    p.add_argument("cube", help="the exact seed cube or selected campaign library")
    p.add_argument("capsule", help="edited lacuna.scenario-capsule.v1 JSON file or - for stdin")
    p.add_argument(
        "--root",
        default=".lacuna-scenarios",
        help="directory under which a collision-resistant private scenario run is created",
    )
    p.add_argument("--format", choices=["json", "markdown"], default="markdown")
    p.set_defaults(func=cmd_scenario_begin)

    p = scenario_sub.add_parser(
        "status", help="strictly audit a comparative scenario and show its exact next action"
    )
    p.add_argument("run", help="scenario run directory or run.json path")
    p.add_argument("--format", choices=["json", "markdown"], default="json")
    p.set_defaults(func=cmd_scenario_status)

    p = scenario_sub.add_parser(
        "recover",
        help="repair only a missing or stale deterministic NEXT.md after authoritative custody passes",
    )
    p.add_argument("run", help="scenario run directory or run.json path")
    p.add_argument("--format", choices=["json", "markdown"], default="json")
    p.set_defaults(func=cmd_scenario_recover)

    p = scenario_sub.add_parser(
        "dispatch",
        help="activate or redisplay the next opaque cell's private condition driver",
    )
    p.add_argument("run", help="scenario run directory or run.json path")
    p.add_argument("--format", choices=["json", "markdown"], default="markdown")
    p.set_defaults(func=cmd_scenario_dispatch)

    p = scenario_sub.add_parser(
        "record",
        help="validate and freeze the active cell return, then advance serially",
    )
    p.add_argument("run", help="scenario run directory or run.json path")
    p.add_argument("artifact", help="lacuna.scenario-cell-return.v1 JSON file or - for stdin")
    p.add_argument("--format", choices=["json", "markdown"], default="json")
    p.set_defaults(func=cmd_scenario_record)

    p = scenario_sub.add_parser(
        "contamination",
        help="show the authenticated preregistered exact-canary scan after all four cells are frozen",
    )
    p.add_argument("run", help="scenario run directory or run.json path")
    p.add_argument("--format", choices=["json", "markdown"], default="markdown")
    p.set_defaults(func=cmd_scenario_contamination)

    p = scenario_sub.add_parser(
        "rating-template",
        help="emit the exact blind-rating JSON contract after all four cells are frozen",
    )
    p.add_argument("run", help="scenario run directory or run.json path")
    p.add_argument("--rater-id", default="rater.replace-me")
    p.set_defaults(func=cmd_scenario_rating_template)

    p = scenario_sub.add_parser(
        "rate",
        help="validate and freeze one complete blind rating artifact",
    )
    p.add_argument("run", help="scenario run directory or run.json path")
    p.add_argument("rating", help="lacuna.scenario-rating.v1 JSON file or - for stdin")
    p.add_argument("--format", choices=["json", "markdown"], default="json")
    p.set_defaults(func=cmd_scenario_rate)

    p = scenario_sub.add_parser(
        "masking-template",
        help="emit the post-primary-rating method-identifiability JSON contract",
    )
    p.add_argument("run", help="scenario run directory or run.json path")
    p.add_argument("--assessor-id", default="rater.replace-me")
    p.set_defaults(func=cmd_scenario_masking_template)

    p = scenario_sub.add_parser(
        "mask",
        help="validate and freeze one post-primary-rating masking/method-identifiability artifact",
    )
    p.add_argument("run", help="scenario run directory or run.json path")
    p.add_argument("masking", help="lacuna.scenario-masking-assessment.v1 JSON file or - for stdin")
    p.add_argument("--format", choices=["json", "markdown"], default="json")
    p.set_defaults(func=cmd_scenario_mask)

    p = scenario_sub.add_parser(
        "unblind",
        help="join frozen ratings to the committed condition assignment and emit a descriptive report",
    )
    p.add_argument("run", help="scenario run directory or run.json path")
    p.add_argument("--format", choices=["json", "markdown"], default="markdown")
    p.set_defaults(func=cmd_scenario_unblind)

    bundle = scenario_sub.add_parser(
        "bundle",
        help="run a preregistered multi-block scenario comparison without unblinding between blocks",
    )
    bundle_sub = bundle.add_subparsers(dest="scenario_bundle_command", required=True)

    p = bundle_sub.add_parser(
        "template",
        help="build one editable preregistration from repeated CUBE CAPSULE block pairs",
    )
    p.add_argument(
        "--block",
        action="append",
        nargs=2,
        metavar=("CUBE", "CAPSULE"),
        required=True,
        help="repeat for each block; CUBE may be a selected campaign library and CAPSULE is lacuna.scenario-capsule.v1 JSON",
    )
    p.add_argument("--title", default="Replicated retcon-planning comparison")
    p.add_argument(
        "--research-question",
        default="Across preregistered blocks, how do forward-only, prompt-only retcon, Lacuna serial, and Lacuna role-separated continuations compare?",
    )
    p.add_argument(
        "--primary-dimension",
        action="append",
        choices=[
            "coherence",
            "agency",
            "character_believability",
            "genre_fit",
            "payoff",
            "novelty",
            "coincidence_restraint",
            "mystery_fairness",
            "seam_invisibility",
        ],
        default=[],
        help="repeat to replace the default preregistered primary dimensions",
    )
    p.add_argument(
        "--minimum-witnesses",
        type=int,
        default=0,
        help="external receipt records required before the first child may advance",
    )
    p.add_argument("--notes")
    p.set_defaults(func=cmd_scenario_bundle_template)

    p = bundle_sub.add_parser(
        "begin",
        help="publish every planned child clone and hidden assignment together before execution",
    )
    p.add_argument("plan", help="lacuna.scenario-bundle-plan.v1 JSON file or - for stdin")
    p.add_argument(
        "--root",
        default=".lacuna-scenario-bundles",
        help="directory under which the owner-private bundle is atomically published",
    )
    p.add_argument("--format", choices=["json", "markdown"], default="markdown")
    p.set_defaults(func=cmd_scenario_bundle_begin)

    p = bundle_sub.add_parser(
        "status",
        help="audit the preregistration, every child, seals, witnesses, and exact next action",
    )
    p.add_argument("bundle", help="scenario bundle directory or bundle.json path")
    p.add_argument("--format", choices=["json", "markdown"], default="json")
    p.set_defaults(func=cmd_scenario_bundle_status)

    p = bundle_sub.add_parser(
        "recover",
        help="repair only permitted parent cache or NEXT.md drift after full child custody passes",
    )
    p.add_argument("bundle", help="scenario bundle directory or bundle.json path")
    p.add_argument("--format", choices=["json", "markdown"], default="json")
    p.set_defaults(func=cmd_scenario_bundle_recover)

    p = bundle_sub.add_parser(
        "commitment",
        help="emit the exact public commitment suitable for independent retention",
    )
    p.add_argument("bundle", help="scenario bundle directory or bundle.json path")
    p.set_defaults(func=cmd_scenario_bundle_commitment)

    p = bundle_sub.add_parser(
        "witness-template",
        help="emit the exact local record for one externally retained commitment receipt",
    )
    p.add_argument("bundle", help="scenario bundle directory or bundle.json path")
    p.add_argument("--witness-id", required=True)
    p.set_defaults(func=cmd_scenario_bundle_witness_template)

    p = bundle_sub.add_parser(
        "witness",
        help="freeze one operator-supplied external receipt before any child advances",
    )
    p.add_argument("bundle", help="scenario bundle directory or bundle.json path")
    p.add_argument("witness", help="lacuna.scenario-bundle-witness.v1 JSON file or - for stdin")
    p.set_defaults(func=cmd_scenario_bundle_witness)

    p = bundle_sub.add_parser(
        "dispatch",
        help="activate or redisplay the next opaque cell in the only active block",
    )
    p.add_argument("bundle", help="scenario bundle directory or bundle.json path")
    p.add_argument("--format", choices=["json", "markdown"], default="markdown")
    p.set_defaults(func=cmd_scenario_bundle_dispatch)

    p = bundle_sub.add_parser(
        "record",
        help="freeze the active cell return after cross-block context and invocation preflight",
    )
    p.add_argument("bundle", help="scenario bundle directory or bundle.json path")
    p.add_argument("artifact", help="lacuna.scenario-cell-return.v1 JSON file or - for stdin")
    p.add_argument("--format", choices=["json", "markdown"], default="json")
    p.set_defaults(func=cmd_scenario_bundle_record)

    p = bundle_sub.add_parser(
        "rating-template",
        help="emit the active block's exact blind-rating contract",
    )
    p.add_argument("bundle", help="scenario bundle directory or bundle.json path")
    p.add_argument("--rater-id", default="rater.replace-me")
    p.set_defaults(func=cmd_scenario_bundle_rating_template)

    p = bundle_sub.add_parser(
        "rate",
        help="freeze one complete blind rating for the active block",
    )
    p.add_argument("bundle", help="scenario bundle directory or bundle.json path")
    p.add_argument("rating", help="lacuna.scenario-rating.v1 JSON file or - for stdin")
    p.add_argument("--format", choices=["json", "markdown"], default="json")
    p.set_defaults(func=cmd_scenario_bundle_rate)

    p = bundle_sub.add_parser(
        "masking-template",
        help="emit the active block's post-primary-rating masking contract",
    )
    p.add_argument("bundle", help="scenario bundle directory or bundle.json path")
    p.add_argument("--assessor-id", default="rater.replace-me")
    p.set_defaults(func=cmd_scenario_bundle_masking_template)

    p = bundle_sub.add_parser(
        "mask",
        help="freeze one post-primary-rating masking assessment for the active block",
    )
    p.add_argument("bundle", help="scenario bundle directory or bundle.json path")
    p.add_argument("masking", help="lacuna.scenario-masking-assessment.v1 JSON file or - for stdin")
    p.add_argument("--format", choices=["json", "markdown"], default="json")
    p.set_defaults(func=cmd_scenario_bundle_mask)

    p = bundle_sub.add_parser(
        "seal",
        help="seal the rated active block while keeping it blind, then activate the next block",
    )
    p.add_argument("bundle", help="scenario bundle directory or bundle.json path")
    p.set_defaults(func=cmd_scenario_bundle_seal)

    p = bundle_sub.add_parser(
        "unblind",
        help="after every block is sealed, unblind all children and publish one deterministic report",
    )
    p.add_argument("bundle", help="scenario bundle directory or bundle.json path")
    p.add_argument("--format", choices=["json", "markdown"], default="markdown")
    p.set_defaults(func=cmd_scenario_bundle_unblind)

    p = bundle_sub.add_parser(
        "export",
        help="emit the frozen report as JSON, Markdown, or rater-level CSV",
    )
    p.add_argument("bundle", help="scenario bundle directory or bundle.json path")
    p.add_argument("--format", choices=["json", "markdown", "csv"], default="json")
    p.set_defaults(func=cmd_scenario_bundle_export)

    checkpoint = sub.add_parser(
        "checkpoint",
        help="run a source-bound generator/judge/compressor/verifier retcon checkpoint",
    )
    checkpoint_sub = checkpoint.add_subparsers(dest="checkpoint_command", required=True)

    p = checkpoint_sub.add_parser(
        "begin",
        help="open one narrow checkpoint request and freeze its protected-state boundary",
    )
    p.add_argument("cube", help="cube path, or a library path with a selected campaign")
    p.add_argument("--audience-id", default="player")
    p.add_argument("--actor-id", default="narrator")
    trigger_group = p.add_mutually_exclusive_group(required=True)
    trigger_group.add_argument("--trigger", help="why this exact planning checkpoint is being opened")
    trigger_group.add_argument("--trigger-file", help="UTF-8 trigger text file; use - for stdin")
    p.add_argument("--candidate-count", type=int, default=4)
    p.add_argument("--rollout-horizon-turns", type=int, default=4)
    p.add_argument("--compression-max-chars", type=int, default=6000)
    p.add_argument("--max-operations", type=int, default=32)
    p.set_defaults(func=cmd_checkpoint_begin)

    p = checkpoint_sub.add_parser(
        "card",
        help="manufacture one digest-bound least-context checkpoint role card",
    )
    p.add_argument("request", help="lacuna.checkpoint-request.v1 JSON file")
    p.add_argument("--role", choices=CHECKPOINT_ROLES, required=True)
    p.add_argument("--candidates", help="lacuna.checkpoint-candidates.v1 JSON file")
    p.add_argument("--judgment", help="lacuna.checkpoint-judgment.v1 JSON file")
    p.add_argument("--proposal", help="lacuna.checkpoint-proposal.v1 JSON file")
    p.add_argument("--format", choices=["json", "markdown"], default="json")
    p.set_defaults(func=cmd_checkpoint_card)

    p = checkpoint_sub.add_parser(
        "dispatch",
        help="render a provider-specific handoff around one complete checkpoint card",
    )
    p.add_argument("card", help="lacuna.checkpoint-task-card.v1 JSON file")
    p.add_argument("--provider", choices=PROVIDERS, default="portable")
    p.add_argument("--format", choices=["json", "markdown"], default="markdown")
    p.set_defaults(func=cmd_checkpoint_dispatch)

    p = checkpoint_sub.add_parser(
        "assemble",
        help="validate generator, judge, and compressor artifacts and assemble one narrow turn proposal",
    )
    p.add_argument("request")
    p.add_argument("candidates")
    p.add_argument("judgment")
    p.add_argument("compression")
    p.set_defaults(func=cmd_checkpoint_assemble)

    p = checkpoint_sub.add_parser(
        "review",
        help="require a passing advisory verifier and freeze an exact kernel rollback preparation",
    )
    p.add_argument("cube", help="cube path, or a library path with a selected campaign")
    p.add_argument("request")
    p.add_argument("candidates")
    p.add_argument("judgment")
    p.add_argument("proposal")
    p.add_argument("verifier")
    p.set_defaults(func=cmd_checkpoint_review)

    p = checkpoint_sub.add_parser(
        "commit",
        help="commit or exactly recover the reviewed checkpoint without duplicate events",
    )
    p.add_argument("cube", help="cube path, or a library path with a selected campaign")
    p.add_argument("request")
    p.add_argument("candidates")
    p.add_argument("judgment")
    p.add_argument("proposal")
    p.add_argument("verifier")
    p.add_argument("review")
    p.set_defaults(func=cmd_checkpoint_commit)

    checkpoint_run = checkpoint_sub.add_parser(
        "run",
        help="create and resume one audited generator/judge/compressor/verifier checkpoint sidecar",
    )
    checkpoint_run_sub = checkpoint_run.add_subparsers(
        dest="checkpoint_run_command", required=True
    )

    p = checkpoint_run_sub.add_parser(
        "begin",
        help="open a source-bound checkpoint and create its exact resumable run directory",
    )
    p.add_argument("cube", help="cube path, or a library path with a selected campaign")
    p.add_argument(
        "--root",
        default=".lacuna-checkpoint-runs",
        help="directory under which a collision-resistant checkpoint run is created",
    )
    p.add_argument("--audience-id", default="player")
    p.add_argument("--actor-id", default="narrator")
    trigger_group = p.add_mutually_exclusive_group(required=True)
    trigger_group.add_argument("--trigger")
    trigger_group.add_argument("--trigger-file", help="UTF-8 trigger text file; use - for stdin")
    p.add_argument("--candidate-count", type=int, default=4)
    p.add_argument("--rollout-horizon-turns", type=int, default=4)
    p.add_argument("--compression-max-chars", type=int, default=6000)
    p.add_argument("--max-operations", type=int, default=32)
    p.add_argument(
        "--provider",
        choices=PROVIDERS,
        default="portable",
        help="default provider route for all four roles",
    )
    p.add_argument("--generator-provider", choices=PROVIDERS)
    p.add_argument("--judge-provider", choices=PROVIDERS)
    p.add_argument("--compressor-provider", choices=PROVIDERS)
    p.add_argument("--verifier-provider", choices=PROVIDERS)
    p.add_argument("--format", choices=["json", "markdown"], default="markdown")
    p.set_defaults(func=cmd_checkpoint_run_begin)

    p = checkpoint_run_sub.add_parser(
        "status", help="strictly audit a checkpoint run and show its exact next action"
    )
    p.add_argument("run", help="checkpoint run directory or run.json path")
    p.add_argument("--format", choices=["json", "markdown"], default="json")
    p.set_defaults(func=cmd_checkpoint_run_status)

    p = checkpoint_run_sub.add_parser(
        "recover",
        help="repair only a missing or stale deterministic NEXT.md after authoritative custody passes",
    )
    p.add_argument("run", help="checkpoint run directory or run.json path")
    p.add_argument("--format", choices=["json", "markdown"], default="json")
    p.set_defaults(func=cmd_checkpoint_run_recover)

    p = checkpoint_run_sub.add_parser(
        "dispatch",
        help="render the current configured role as one self-contained least-context handoff",
    )
    p.add_argument("run", help="checkpoint run directory or run.json path")
    p.add_argument("--format", choices=["json", "markdown"], default="markdown")
    p.set_defaults(func=cmd_checkpoint_run_dispatch)

    p = checkpoint_run_sub.add_parser(
        "next-turn",
        help="open one exact audience-only solo play-turn at the committed checkpoint head and render its fresh-narrator handoff",
    )
    p.add_argument("checkpoint_run", help="committed checkpoint run directory or run.json path")
    p.add_argument("--root", help="turn-run root; defaults to a continuation-turns directory beside the checkpoint runs")
    player_input_group = p.add_mutually_exclusive_group(required=True)
    player_input_group.add_argument("--player-input")
    player_input_group.add_argument(
        "--player-input-file",
        help="UTF-8 file containing the exact next player message; use - for stdin",
    )
    p.add_argument("--provider", choices=PROVIDERS, default="portable")
    p.add_argument(
        "--public-history",
        help="optional lacuna.public-history.v2 JSON compiled from committed pre-checkpoint turns",
    )
    p.add_argument("--format", choices=["json", "markdown"], default="markdown")
    p.set_defaults(func=cmd_checkpoint_run_next_turn)

    p = checkpoint_run_sub.add_parser(
        "continuation",
        help="bind one committed checkpoint capsule to one already-open fresh solo play-turn and render the exact narrator handoff",
    )
    p.add_argument("checkpoint_run", help="committed checkpoint run directory or run.json path")
    p.add_argument("turn_run", help="fresh audience-only solo play-turn run directory or run.json path")
    p.add_argument("--provider", choices=PROVIDERS, default="portable")
    p.add_argument(
        "--public-history",
        help="optional lacuna.public-history.v2 JSON compiled from committed pre-checkpoint turns",
    )
    p.add_argument("--format", choices=["json", "markdown"], default="markdown")
    p.set_defaults(func=cmd_checkpoint_run_continuation)

    p = checkpoint_run_sub.add_parser(
        "accept",
        help="validate the current exact worker return, record invocation custody, and manufacture the next card",
    )
    p.add_argument("run", help="checkpoint run directory or run.json path")
    p.add_argument("artifact", help="exact JSON worker return file or - for stdin")
    p.add_argument("--model", default="unknown", help="honest host-declared model name; unknown is permitted")
    p.add_argument("--model-version")
    p.add_argument("--invocation-id")
    p.add_argument("--started-at")
    p.add_argument("--completed-at")
    p.add_argument("--duration-ms", type=int)
    p.add_argument("--format", choices=["json", "markdown"], default="json")
    p.set_defaults(func=cmd_checkpoint_run_accept)

    p = checkpoint_run_sub.add_parser(
        "record-failure",
        help="record one host-declared failed current-role invocation without advancing the checkpoint",
    )
    p.add_argument("run", help="checkpoint run directory or run.json path")
    p.add_argument("--failure-class", choices=sorted(INVOCATION_FAILURE_CLASSES), required=True)
    p.add_argument("--failure-message")
    p.add_argument("--model", default="unknown")
    p.add_argument("--model-version")
    p.add_argument("--invocation-id")
    p.add_argument("--started-at")
    p.add_argument("--completed-at")
    p.add_argument("--duration-ms", type=int)
    p.add_argument("--format", choices=["json", "markdown"], default="json")
    p.set_defaults(func=cmd_checkpoint_run_record_failure)

    p = checkpoint_run_sub.add_parser(
        "commit",
        help="commit or exactly recover the ready managed checkpoint and retain its receipt",
    )
    p.add_argument("run", help="checkpoint run directory or run.json path")
    p.add_argument("--format", choices=["json", "markdown"], default="json")
    p.set_defaults(func=cmd_checkpoint_run_commit)

    p = checkpoint_run_sub.add_parser(
        "narrator-capsule",
        help="compile the committed checkpoint into one exact fresh-narrator information bottleneck",
    )
    p.add_argument("run", help="committed checkpoint run directory or run.json path")
    p.add_argument("--format", choices=["json", "markdown"], default="json")
    p.set_defaults(func=cmd_checkpoint_run_narrator_capsule)

    turn = sub.add_parser("turn", help="prepare or commit a typed model/human turn")
    turn_sub = turn.add_subparsers(dest="turn_command", required=True)

    p = turn_sub.add_parser(
        "packet",
        help="open a source-bound turn request and emit its model/human packet",
    )
    p.add_argument("cube", help="cube path, or a library path with a selected campaign")
    p.add_argument("--audience-id", default="player")
    p.add_argument("--actor-id", default="narrator")
    p.add_argument(
        "--input-kind",
        choices=TURN_INPUT_KINDS,
        default="play-turn",
        help="classify the exact text as an in-world play turn or out-of-world session control",
    )
    input_group = p.add_mutually_exclusive_group(required=True)
    input_group.add_argument("--player-input")
    input_group.add_argument(
        "--player-input-file",
        help="UTF-8 file containing the exact player message; use - for stdin",
    )
    p.add_argument("--director", action="store_true", help="include separately labelled privileged planner context")
    p.add_argument("--world-id", help="restrict privileged planner context and writes to one candidate-world subtree")
    p.add_argument(
        "--allow-anchor",
        action="store_true",
        help="grant this request authority to create anchored assertions (off by default)",
    )
    p.add_argument("--format", choices=["json", "markdown"], default="json")
    p.set_defaults(func=cmd_turn_packet)

    p = turn_sub.add_parser("commit", help="validate and atomically commit a turn proposal")
    p.add_argument("cube", help="cube path, or a library path with a selected campaign")
    p.add_argument("proposal", help="turn proposal JSON file or - for stdin")
    p.add_argument("--include-planner-context", action="store_true")
    p.add_argument("--format", choices=["json", "markdown"], default="json")
    p.set_defaults(func=cmd_turn_commit)

    p = turn_sub.add_parser(
        "plan",
        help="audit a fresh packet and select a deterministic solo, pair, or four-role information-flow plan",
    )
    p.add_argument("packet", help="fresh supported lacuna.turn-request JSON file (v2, v3, or v4)")
    p.add_argument("--mode", choices=ORCHESTRATION_MODES, default="auto")
    p.add_argument("--format", choices=["json", "markdown"], default="json")
    p.set_defaults(func=cmd_turn_plan)

    p = turn_sub.add_parser(
        "card",
        help="emit one digest-bound least-context subagent task card from a fresh packet",
    )
    p.add_argument("packet", help="fresh supported lacuna.turn-request JSON file (v2, v3, or v4)")
    p.add_argument("--role", choices=TASK_ROLES, required=True)
    p.add_argument("--planner-return", help="validated lacuna.planner-return.v1 JSON file")
    p.add_argument("--narrator-return", help="validated lacuna.narrator-return.v1 JSON file")
    p.add_argument("--proposal", help="candidate lacuna.turn-proposal.v2 JSON file")
    p.add_argument("--format", choices=["json", "markdown"], default="json")
    p.set_defaults(func=cmd_turn_card)

    run = turn_sub.add_parser(
        "run",
        help="create and resume a request-scoped packet/card/return sidecar across model invocations",
    )
    run_sub = run.add_subparsers(dest="turn_run_command", required=True)

    p = run_sub.add_parser(
        "begin",
        help="open one source-bound turn and create a resumable run directory with the exact next card",
    )
    p.add_argument("cube", help="cube path, or a library path with a selected campaign")
    p.add_argument("--root", default=".lacuna-runs", help="directory under which a collision-resistant run directory is created")
    p.add_argument("--audience-id", default="player")
    p.add_argument("--actor-id", default="narrator")
    p.add_argument(
        "--input-kind",
        choices=TURN_INPUT_KINDS,
        default="play-turn",
        help="classify the exact text as an in-world play turn or out-of-world session control",
    )
    input_group = p.add_mutually_exclusive_group(required=True)
    input_group.add_argument("--player-input")
    input_group.add_argument(
        "--player-input-file",
        help="UTF-8 file containing the exact player message; use - for stdin",
    )
    p.add_argument("--director", action="store_true", help="include separately labelled privileged planner context")
    p.add_argument("--world-id", help="restrict privileged planner context and writes to one candidate-world subtree")
    p.add_argument("--allow-anchor", action="store_true", help="grant anchored-assertion authority for this run")
    p.add_argument("--mode", choices=ORCHESTRATION_MODES, default="auto")
    p.add_argument(
        "--include-planner-context",
        action="store_true",
        help="include privileged planner context in the eventual commit receipt",
    )
    p.add_argument("--format", choices=["json", "markdown"], default="json")
    p.set_defaults(func=cmd_turn_run_begin)

    p = run_sub.add_parser("status", help="strictly audit a run and show its exact next action")
    p.add_argument("run", help="turn run directory or run.json path")
    p.add_argument("--format", choices=["json", "markdown"], default="json")
    p.set_defaults(func=cmd_turn_run_status)

    p = run_sub.add_parser(
        "recover",
        help="repair only a missing or stale deterministic NEXT.md pointer after a strict run audit",
    )
    p.add_argument("run", help="turn run directory or run.json path")
    p.add_argument("--format", choices=["json", "markdown"], default="json")
    p.set_defaults(func=cmd_turn_run_recover)

    p = run_sub.add_parser(
        "dispatch",
        help="render one provider-routed, self-contained least-context handoff for the current delegated stage",
    )
    p.add_argument("run", help="turn run directory or run.json path")
    p.add_argument("--provider", choices=TURN_RUN_PROVIDERS, default="portable")
    p.add_argument("--format", choices=["json", "markdown"], default="markdown")
    p.set_defaults(func=cmd_turn_run_dispatch)

    p = run_sub.add_parser(
        "accept",
        help="validate one exact expected return, store it, and manufacture the next card",
    )
    p.add_argument("run", help="turn run directory or run.json path")
    p.add_argument("artifact", help="exact JSON return file or - for stdin")
    p.add_argument("--format", choices=["json", "markdown"], default="json")
    p.set_defaults(func=cmd_turn_run_accept)

    p = run_sub.add_parser(
        "commit",
        help="commit the exact accepted proposal for a ready run and write its receipt",
    )
    p.add_argument("run", help="turn run directory or run.json path")
    p.add_argument("--format", choices=["json", "markdown"], default="json")
    p.set_defaults(func=cmd_turn_run_commit)

    seal = sub.add_parser(
        "seal",
        help="prepare, publish, verify, reveal, or void a fair-play precommitment",
    )
    seal_sub = seal.add_subparsers(dest="seal_command", required=True)

    p = seal_sub.add_parser(
        "prepare",
        help="create a secret salted opening without writing it to the cube",
    )
    p.add_argument("cube")
    p.add_argument("payload", help="JSON payload file or - for stdin")
    p.add_argument("--seal-id")
    p.add_argument(
        "--nonce",
        help="64 lowercase hex characters; testing only, otherwise a secure nonce is generated",
    )
    p.set_defaults(func=cmd_seal_prepare)

    p = seal_sub.add_parser(
        "create",
        help="write only an opening's digest and public metadata to the cube",
    )
    p.add_argument("cube")
    p.add_argument("opening", help="seal-opening JSON file")
    p.add_argument("--label")
    p.add_argument("--purpose", choices=sorted(SEAL_PURPOSES), default="other")
    p.add_argument("--visibility", choices=sorted(SEAL_VISIBILITIES), default="public")
    p.add_argument("--audience", action="append")
    p.add_argument("--source-id")
    add_actor(p)
    p.set_defaults(func=cmd_seal_create)

    p = seal_sub.add_parser("list", help="list visible fair-play seal records")
    p.add_argument("cube")
    p.add_argument("--agent-id")
    p.add_argument("--status", choices=["sealed", "revealed", "voided"])
    p.set_defaults(func=cmd_seal_list)

    p = seal_sub.add_parser("receipt", help="export a retainable seal receipt")
    p.add_argument("cube")
    p.add_argument("seal_id")
    p.add_argument("--agent-id")
    p.set_defaults(func=cmd_seal_receipt)

    p = seal_sub.add_parser(
        "verify",
        help="verify an opening against the digest recorded in the cube",
    )
    p.add_argument("cube")
    p.add_argument("opening", help="seal-opening JSON file or - for stdin")
    p.add_argument("--agent-id")
    p.set_defaults(func=cmd_seal_verify)

    p = seal_sub.add_parser("reveal", help="publish a matching opening in a later change-set")
    p.add_argument("cube")
    p.add_argument("opening", help="seal-opening JSON file")
    p.add_argument("--reason", required=True)
    add_actor(p)
    p.set_defaults(func=cmd_seal_reveal)

    p = seal_sub.add_parser("void", help="resolve an unopened seal without revealing it")
    p.add_argument("cube")
    p.add_argument("seal_id")
    p.add_argument("--reason", required=True)
    add_actor(p)
    p.set_defaults(func=cmd_seal_void)

    for name, help_text, func in [
        ("status", "show cube counts and head", cmd_status),
        ("head", "show the current ledger head", cmd_head),
        ("changes", "show atomic change-set receipts", cmd_changes),
        ("verify", "verify SQLite integrity, foreign keys, and the event hash chain", cmd_verify),
        ("rebuild", "rebuild semantic projections from the immutable event ledger", cmd_rebuild),
        ("snapshot", "export the current semantic snapshot", cmd_snapshot),
        ("claims", "list declared claims", cmd_claims),
        ("canon", "show anchors and cross-world consensus", cmd_canon),
        ("worlds", "show candidate worlds and assignments", cmd_worlds),
        ("unknowns", "show explicit questions and unsettled claims", cmd_unknowns),
        ("conflicts", "show epistemic tensions and invariant violations", cmd_conflicts),
    ]:
        q = sub.add_parser(name, help=help_text)
        q.add_argument("cube")
        q.set_defaults(func=func)

    p = sub.add_parser("events", help="show immutable ledger events")
    p.add_argument("cube")
    p.add_argument("--since-seq", type=int, default=0)
    p.add_argument("--limit", type=int)
    p.set_defaults(func=cmd_events)

    p = sub.add_parser("evidence", help="show explicit evidence relations")
    p.add_argument("cube")
    p.add_argument("--world-id", help="include global links plus links scoped to this world")
    p.set_defaults(func=cmd_evidence)

    p = sub.add_parser("relations", help="show explicit cross-claim integrity relations")
    p.add_argument("cube")
    p.add_argument("--include-retired", action="store_true")
    p.set_defaults(func=cmd_relations)

    p = sub.add_parser("cardinalities", help="show explicit multi-claim cardinality constraints")
    p.add_argument("cube")
    p.add_argument("--include-retired", action="store_true")
    p.set_defaults(func=cmd_cardinalities)

    p = sub.add_parser("revision-impact", help="review and digest the impact of revising one assignment")
    p.add_argument("cube")
    p.add_argument("assignment_id")
    p.set_defaults(func=cmd_revision_impact)

    p = sub.add_parser("consequences", help="show explicit assignment consequence custody")
    p.add_argument("cube")
    p.add_argument("--include-retired", action="store_true")
    p.add_argument("--premise-assignment-id")
    p.set_defaults(func=cmd_consequences)

    p = sub.add_parser("consequence-repairs", help="show immutable consequence replacement lineage")
    p.add_argument("cube")
    p.set_defaults(func=cmd_consequence_repairs)

    p = sub.add_parser(
        "consequence-repair-review",
        help="review one consequence and bind a replacement authorization to the current head",
    )
    p.add_argument("cube")
    p.add_argument("consequence_id")
    p.set_defaults(func=cmd_consequence_repair_review)

    p = sub.add_parser(
        "consequence-repair-frontier",
        help="show digest-bound reviews for all currently orphaned consequences",
    )
    p.add_argument("cube")
    p.add_argument("--world-id")
    p.set_defaults(func=cmd_consequence_repair_frontier)

    p = sub.add_parser(
        "particle-bank",
        help="inspect normalized weights, diversity, and valuation fingerprints",
    )
    p.add_argument("cube")
    p.set_defaults(func=cmd_particle_bank)

    p = sub.add_parser(
        "particle-update-review",
        help="issue a digest-bound complete-population evidence update receipt",
    )
    p.add_argument("cube")
    p.add_argument("evidence_assertion_id")
    p.set_defaults(func=cmd_particle_update_review)

    p = sub.add_parser("particle-updates", help="show immutable particle update custody")
    p.add_argument("cube")
    p.add_argument("--update-id")
    p.set_defaults(func=cmd_particle_updates)

    p = sub.add_parser(
        "particle-reconciliation-review",
        help="review deterministic replay of the current particle factor ledger",
    )
    p.add_argument("cube")
    p.set_defaults(func=cmd_particle_reconciliation_review)

    p = sub.add_parser(
        "particle-reconciliations",
        help="show immutable particle factor-ledger reconciliation custody",
    )
    p.add_argument("cube")
    p.add_argument("--reconciliation-id")
    p.set_defaults(func=cmd_particle_reconciliations)

    p = sub.add_parser("explain", help="trace one record's origin, dependencies, and dependents")
    p.add_argument("cube")
    p.add_argument("target_id")
    p.add_argument("--agent-id", help="apply perspective visibility instead of privileged planner access")
    p.set_defaults(func=cmd_explain)

    p = sub.add_parser("apply", help="atomically apply a digest-bound JSON change-set")
    p.add_argument("cube")
    p.add_argument("change_set", help="JSON file or - for stdin")
    p.add_argument("--bind-current", action="store_true", help="replace expected_head with the current head")
    p.set_defaults(func=cmd_apply)

    p = sub.add_parser("world", help="show one candidate world")
    p.add_argument("cube")
    p.add_argument("world_id")
    p.set_defaults(func=cmd_world)

    p = sub.add_parser("perspective", help="project records visible to an epistemic subject")
    p.add_argument("cube")
    p.add_argument("agent_id")
    p.set_defaults(func=cmd_perspective)

    p = sub.add_parser("context", help="render an epistemic context packet")
    p.add_argument("cube", help="cube path, or a library path with a selected campaign")
    p.add_argument("--agent-id", help="perspective scope; cannot be combined with --world-id")
    p.add_argument("--world-id", help="privileged planner scope for one candidate world")
    p.add_argument("--format", choices=["markdown", "json"], default="markdown")
    p.set_defaults(func=cmd_context)

    p = sub.add_parser("agent-add", help="register an agent")
    p.add_argument("cube")
    p.add_argument("--agent-id")
    p.add_argument("--kind", default="other", choices=["human", "character", "narrator", "model", "tool", "system", "organization", "other"])
    p.add_argument("--label")
    add_actor(p)
    p.set_defaults(func=cmd_agent_add)

    p = sub.add_parser("source-add", help="register a provenance source")
    p.add_argument("cube")
    p.add_argument("--source-id")
    p.add_argument("--kind", default="other", choices=["scene", "utterance", "document", "sensor", "model", "user", "tool", "other"])
    p.add_argument("--label")
    p.add_argument("--locator")
    p.add_argument("--content-sha256")
    add_actor(p)
    p.set_defaults(func=cmd_source_add)

    p = sub.add_parser("claim-add", help="declare a neutral proposition")
    p.add_argument("cube")
    p.add_argument("--subject", required=True)
    p.add_argument("--predicate", required=True)
    p.add_argument("--object-json", required=True, help="JSON value, e.g. true, 4, or '\"red\"'")
    p.add_argument("--scope", default="world", choices=["world", "event", "belief", "meta"])
    add_actor(p)
    p.set_defaults(func=cmd_claim_add)

    p = sub.add_parser("relation-add", help="declare an explicit compatibility relation between two claims")
    p.add_argument("cube")
    p.add_argument("--relation-id")
    p.add_argument("--left-claim-id", required=True)
    p.add_argument("--right-claim-id", required=True)
    p.add_argument("--relation", required=True, choices=["excludes", "negates", "entails", "equivalent"])
    p.add_argument("--source-id")
    p.add_argument("--rationale", required=True)
    add_actor(p)
    p.set_defaults(func=cmd_relation_add)

    p = sub.add_parser("relation-retire", help="retire a claim relation without deleting its custody")
    p.add_argument("cube")
    p.add_argument("relation_id")
    p.add_argument("--reason", required=True)
    add_actor(p)
    p.set_defaults(func=cmd_relation_retire)

    p = sub.add_parser(
        "cardinality-add",
        help="declare an open-world true-count bound over two or more claims",
    )
    p.add_argument("cube")
    p.add_argument("--constraint-id")
    p.add_argument("--label")
    p.add_argument(
        "--claim-id",
        dest="claim_ids",
        action="append",
        required=True,
        help="constraint member; repeat for each claim",
    )
    p.add_argument("--min-true", type=int, required=True)
    p.add_argument("--max-true", type=int, required=True)
    p.add_argument("--source-id")
    p.add_argument("--rationale", required=True)
    add_actor(p)
    p.set_defaults(func=cmd_cardinality_add)

    p = sub.add_parser(
        "cardinality-retire",
        help="retire a cardinality constraint without deleting its custody",
    )
    p.add_argument("cube")
    p.add_argument("constraint_id")
    p.add_argument("--reason", required=True)
    add_actor(p)
    p.set_defaults(func=cmd_cardinality_retire)

    p = sub.add_parser("assert", help="record a sourced assertion about a claim")
    p.add_argument("cube")
    p.add_argument("--assertion-id")
    p.add_argument("--claim-id", required=True)
    p.add_argument("--assertor-id", required=True)
    p.add_argument("--perspective-id")
    p.add_argument("--source-id")
    p.add_argument("--stance", required=True, choices=["true", "false", "unknown"])
    p.add_argument("--basis", required=True, choices=["observation", "testimony", "inference", "belief", "hypothesis", "commitment", "metadata"])
    p.add_argument("--standing", default="reported", choices=["reported", "accepted", "anchored"])
    p.add_argument("--confidence", type=float)
    p.add_argument("--visibility", default="private", choices=["public", "private", "restricted"])
    p.add_argument("--audience", action="append", default=[])
    p.add_argument("--timeline-id", default="main")
    p.add_argument("--valid-from", type=int)
    p.add_argument("--valid-to", type=int)
    p.add_argument("--note")
    p.add_argument("--supersedes-id")
    add_actor(p)
    p.set_defaults(func=cmd_assert)

    p = sub.add_parser("assertion-supersede", help="end an active assertion without deleting history")
    p.add_argument("cube")
    p.add_argument("assertion_id")
    p.add_argument("--reason", required=True)
    add_actor(p)
    p.set_defaults(func=cmd_assertion_supersede)

    p = sub.add_parser("world-add", help="create or fork a candidate world")
    p.add_argument("cube")
    p.add_argument("--world-id")
    p.add_argument("--label")
    p.add_argument("--parent-world-id")
    p.add_argument("--status", default="live", choices=["live", "selected", "pruned", "archived"])
    p.add_argument("--weight", type=float, default=1.0)
    p.add_argument("--rationale")
    add_actor(p)
    p.set_defaults(func=cmd_world_add)

    p = sub.add_parser("world-assign", help="assign a truth value to a claim inside one candidate world")
    p.add_argument("cube")
    p.add_argument("--assignment-id")
    p.add_argument("--world-id", required=True)
    p.add_argument("--claim-id", required=True)
    p.add_argument("--truth", required=True, choices=["true", "false", "unknown"])
    p.add_argument("--commitment", default="tentative", choices=["tentative", "soft", "firm", "hard"])
    p.add_argument(
        "--commitment-basis",
        default="planning",
        choices=["planning", "authored", "evidence", "disclosure", "precommitment"],
    )
    p.add_argument("--commitment-source-id")
    p.add_argument("--confidence", type=float)
    p.add_argument("--rationale")
    p.add_argument("--source-assertion-id")
    p.add_argument("--timeline-id", default="main")
    p.add_argument("--valid-from", type=int)
    p.add_argument("--valid-to", type=int)
    add_actor(p)
    p.set_defaults(func=cmd_world_assign)

    p = sub.add_parser("world-revise", help="replace an active assignment through a digest-bound governed revision")
    p.add_argument("cube")
    p.add_argument("revises_assignment_id")
    p.add_argument("truth", choices=["true", "false", "unknown"])
    p.add_argument("--assignment-id")
    p.add_argument("--expected-impact-sha256", required=True)
    p.add_argument("--reason", required=True)
    p.add_argument("--commitment", default="tentative", choices=["tentative", "soft"])
    p.add_argument(
        "--commitment-basis",
        default="planning",
        choices=["planning", "authored", "evidence", "disclosure"],
    )
    p.add_argument("--commitment-source-id")
    p.add_argument("--confidence", type=float)
    p.add_argument("--rationale")
    p.add_argument("--source-assertion-id")
    add_actor(p)
    p.set_defaults(func=cmd_world_revise)

    p = sub.add_parser("commitment-raise", help="raise an assignment commitment by exactly one governed step")
    p.add_argument("cube")
    p.add_argument("assignment_id")
    p.add_argument("commitment", choices=["soft", "firm", "hard"])
    p.add_argument("--transition-id")
    p.add_argument(
        "--basis",
        required=True,
        choices=["planning", "authored", "evidence", "disclosure", "precommitment"],
    )
    p.add_argument("--source-id")
    p.add_argument("--rationale", required=True)
    add_actor(p)
    p.set_defaults(func=cmd_commitment_raise)

    p = sub.add_parser("consequence-link", help="record an explicit consequence of a latent-world assignment")
    p.add_argument("cube")
    p.add_argument("premise_assignment_id")
    p.add_argument("dependent_kind", choices=["assertion", "world_assignment", "question"])
    p.add_argument("dependent_id")
    p.add_argument("relation", choices=["causes", "explains", "discloses", "motivates", "promises", "constrains"])
    p.add_argument("--severity", default="material", choices=["notice", "material", "binding"])
    p.add_argument("--consequence-id")
    p.add_argument("--source-id")
    p.add_argument("--rationale", required=True)
    add_actor(p)
    p.set_defaults(func=cmd_consequence_link)

    p = sub.add_parser("consequence-retire", help="retire an explicit consequence without deleting custody")
    p.add_argument("cube")
    p.add_argument("consequence_id")
    p.add_argument("--reason", required=True)
    add_actor(p)
    p.set_defaults(func=cmd_consequence_retire)

    p = sub.add_parser(
        "consequence-replace",
        help="atomically end one consequence and create a reviewed successor",
    )
    p.add_argument("cube")
    p.add_argument("replaces_consequence_id")
    p.add_argument("premise_assignment_id")
    p.add_argument("dependent_kind", choices=["assertion", "world_assignment", "question"])
    p.add_argument("dependent_id")
    p.add_argument(
        "relation",
        choices=["causes", "explains", "discloses", "motivates", "promises", "constrains"],
    )
    p.add_argument("--severity", required=True, choices=["notice", "material", "binding"])
    p.add_argument("--consequence-id")
    p.add_argument("--repair-id")
    p.add_argument("--source-id")
    p.add_argument("--rationale", required=True)
    p.add_argument("--expected-repair-sha256", required=True)
    p.add_argument("--reason", required=True)
    add_actor(p)
    p.set_defaults(func=cmd_consequence_replace)

    p = sub.add_parser(
        "particle-update",
        help="atomically reweight every live candidate world from one evidence assertion",
    )
    p.add_argument("cube")
    p.add_argument("evidence_assertion_id")
    p.add_argument("--update-id")
    p.add_argument("--expected-bank-sha256", required=True)
    p.add_argument(
        "--assessment",
        dest="assessments",
        type=parse_particle_assessment,
        action="append",
        required=True,
        metavar="WORLD_ID=LIKELIHOOD",
        help="repeat exactly once for every live or selected world",
    )
    p.add_argument("--reason", required=True)
    add_actor(p)
    p.set_defaults(func=cmd_particle_update)

    p = sub.add_parser(
        "particle-reconcile",
        help="replay active factors from an immutable baseline and exclude superseded factors",
    )
    p.add_argument("cube")
    p.add_argument("--reconciliation-id")
    p.add_argument("--expected-reconciliation-sha256", required=True)
    p.add_argument("--reason", required=True)
    add_actor(p)
    p.set_defaults(func=cmd_particle_reconcile)

    p = sub.add_parser("world-weight", help="change a candidate world's weight")
    p.add_argument("cube")
    p.add_argument("world_id")
    p.add_argument("weight", type=float)
    p.add_argument("--reason", required=True)
    add_actor(p)
    p.set_defaults(func=cmd_world_weight)

    p = sub.add_parser("world-status", help="select, prune, archive, or reactivate a world")
    p.add_argument("cube")
    p.add_argument("world_id")
    p.add_argument("status", choices=["live", "selected", "pruned", "archived"])
    p.add_argument("--reason", required=True)
    add_actor(p)
    p.set_defaults(func=cmd_world_status)

    p = sub.add_parser("evidence-link", help="relate an assertion to a target claim")
    p.add_argument("cube")
    p.add_argument("--link-id")
    p.add_argument("--evidence-assertion-id", required=True)
    p.add_argument("--target-claim-id", required=True)
    p.add_argument("--world-id")
    p.add_argument("--relation", required=True, choices=["supports", "refutes", "explains", "contextualizes"])
    p.add_argument("--strength", type=float)
    p.add_argument("--rationale")
    add_actor(p)
    p.set_defaults(func=cmd_evidence_link)

    p = sub.add_parser("question-open", help="record an explicit unknown")
    p.add_argument("cube")
    p.add_argument("--question-id")
    p.add_argument("--text", required=True)
    p.add_argument("--about-claim-id")
    p.add_argument("--opened-by", required=True)
    p.add_argument("--visibility", default="private", choices=["public", "private", "restricted"])
    p.add_argument("--audience", action="append", default=[])
    add_actor(p)
    p.set_defaults(func=cmd_question_open)

    p = sub.add_parser("question-close", help="resolve an explicit unknown")
    p.add_argument("cube")
    p.add_argument("question_id")
    p.add_argument("--resolution-assertion-id")
    p.add_argument("--reason", required=True)
    add_actor(p)
    p.set_defaults(func=cmd_question_close)

    p = sub.add_parser("demo", help="initialize and seed the lantern multiple-world demonstration")
    p.add_argument("cube")
    p.set_defaults(func=cmd_demo)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except LacunaError as exc:
        operation_index = None
        if exc.details and isinstance(exc.details.get("operation_index"), int):
            operation_index = exc.details["operation_index"]
        print(pretty_json(exc.receipt(operation_index=operation_index)), file=sys.stderr)
        return 2
    except ValueError as exc:
        error = LacunaError("invalid-input", str(exc))
        print(pretty_json(error.receipt()), file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print(pretty_json(LacunaError("interrupted", "operation interrupted").receipt()), file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
