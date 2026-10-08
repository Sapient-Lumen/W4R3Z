from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]



def _expected_rev() -> int:
    first = (ROOT / "TODO.md").read_text(encoding="utf-8").splitlines()[0]
    match = re.search(r"rev\s*(\d+)", first, flags=re.IGNORECASE)
    assert match is not None
    return int(match.group(1))



def test_mxcontext_cli_human_output_includes_rev_and_priorities() -> None:
    proc = subprocess.run(
        [sys.executable, str(ROOT / 'tools' / 'mxcontext.py')],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert proc.returncode == 0
    assert 'micromax repo context' in proc.stdout
    assert f"Rev: {_expected_rev()}" in proc.stdout
    assert 'Current priorities:' in proc.stdout
    assert 'make context-json' in proc.stdout
    assert 'make context-check' in proc.stdout



def test_mxcontext_cli_can_emit_json_and_check_referenced_paths() -> None:
    proc = subprocess.run(
        [sys.executable, str(ROOT / 'tools' / 'mxcontext.py'), '--json', '--check'],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert proc.returncode == 0
    payload = json.loads(proc.stdout)
    assert payload['project'] == 'micromax'
    assert payload['rev'] == _expected_rev()
    assert payload['checks']['ok'] is True
    assert payload['checks']['missing_paths'] == []
    assert 'docs/170-context-cli-json.md' in payload['docs']
    assert 'docs/171-rust-vm-spike.md' in payload['docs']
    assert 'docs/176-docs-cues-link-metadata.md' in payload['docs']
    assert 'docs/177-docs-cues-image-metadata.md' in payload['docs']
    assert 'docs/178-docs-cues-code-metadata.md' in payload['docs']
    assert 'docs/179-docs-cues-inline-markup-metadata.md' in payload['docs']
    assert 'docs/180-docs-cues-literal-source-metadata.md' in payload['docs']
    assert 'docs/202-docs-cues-structure-metadata.md' in payload['docs']
    assert 'docs/203-docs-cues-table-metadata.md' in payload['docs']
    assert 'docs/204-docs-cues-heading-metadata.md' in payload['docs']
    assert 'docs/205-docs-cues-definition-metadata.md' in payload['docs']
    assert 'docs/206-docs-cues-block-metadata.md' in payload['docs']
    assert 'docs/207-docs-cues-section-metadata.md' in payload['docs']
    assert 'docs/208-helpoutline-section-groups.md' in payload['docs']
    assert 'docs/209-recentdirpick.md' in payload['docs']
    assert 'docs/446-showrecentdir-sample-truth.md' in payload['docs']
    assert 'docs/210-helpnav-heading-breadcrumbs.md' in payload['docs']
    assert 'docs/211-help-breadcrumb-query-matching.md' in payload['docs']
    assert 'docs/212-helplink-heading-query-matching.md' in payload['docs']
    assert 'docs/213-help-heading-fragment-query-matching.md' in payload['docs']
    assert 'docs/214-helplink-target-title-query-matching.md' in payload['docs']
    assert 'docs/215-portability-cleanup-error-precedence.md' in payload['docs']
    assert 'docs/216-portability-try-handler-error-precedence.md' in payload['docs']
    assert 'docs/217-portability-stdlib-manifest-cli.md' in payload['docs']
    assert 'docs/218-portability-stdlib-source-inventory.md' in payload['docs']
    assert 'docs/219-portability-stdlib-dependency-inventory.md' in payload['docs']
    assert 'docs/220-portability-stdlib-closure-inventory.md' in payload['docs']
    assert 'docs/344-help-navigation-model.md' in payload['docs']
    assert 'docs/350-help-navigation-blocked-targets.md' in payload['docs']
    assert 'docs/357-help-navigation-missingdoc-command-honesty.md' in payload['docs']
    assert 'docs/362-macro-inventory-rows.md' in payload['docs']
    assert 'docs/363-recent-inventory-rows.md' in payload['docs']
    assert 'docs/364-plugin-inventory-rows.md' in payload['docs']
    assert 'docs/365-binding-inventory-rows.md' in payload['docs']
    assert 'docs/221-portability-stdlib-user-inventory.md' in payload['docs']
    assert 'docs/222-portability-stdlib-impact-map.md' in payload['docs']
    assert 'docs/223-portability-selected-retest-command.md' in payload['docs']
    assert 'docs/224-portability-impact-inventory.md' in payload['docs']
    assert 'docs/225-portability-impact-groups.md' in payload['docs']
    assert 'docs/226-portability-impact-group-retest-metadata.md' in payload['docs']
    assert 'docs/227-portability-impact-stages.md' in payload['docs']
    assert 'docs/228-portability-impact-slice-filters.md' in payload['docs']
    assert 'docs/229-portability-impact-case-filters.md' in payload['docs']
    assert 'docs/230-portability-impact-filter-options.md' in payload['docs']
    assert 'docs/231-portability-impact-semantic-filter-options.md' in payload['docs']
    assert 'docs/232-portability-impact-filter-suffixes.md' in payload['docs']
    assert 'docs/233-portability-impact-filter-commands.md' in payload['docs']
    assert 'docs/234-portability-impact-filter-family-modes.md' in payload['docs']
    assert 'docs/235-portability-impact-filter-previews.md' in payload['docs']
    assert 'docs/236-portability-impact-preview-effects.md' in payload['docs']
    assert 'docs/237-portability-impact-filter-recommendations.md' in payload['docs']
    assert 'docs/238-portability-impact-equivalent-cuts.md' in payload['docs']
    assert 'docs/239-portability-impact-distinct-recommendations.md' in payload['docs']
    assert 'docs/240-portability-impact-distinct-groups.md' in payload['docs']
    assert 'docs/241-portability-impact-representative-reasons.md' in payload['docs']
    assert 'docs/242-portability-impact-recommendation-ranks.md' in payload['docs']
    assert 'docs/243-portability-impact-primary-recommendation.md' in payload['docs']
    assert 'docs/244-context-portability-snapshot.md' in payload['docs']
    assert 'docs/245-archive-context-manifest.md' in payload['docs']
    assert 'docs/246-docs-cues-task-metadata.md' in payload['docs']
    assert 'docs/247-docs-cues-blockquote-break-metadata.md' in payload['docs']
    assert 'docs/248-docs-cues-list-metadata.md' in payload['docs']
    assert 'docs/249-docs-cues-link-target-metadata.md' in payload['docs']
    assert 'docs/250-docs-cues-image-target-metadata.md' in payload['docs']
    assert 'docs/251-docs-cues-table-kind-metadata.md' in payload['docs']
    assert 'docs/252-docs-cues-block-kind-metadata.md' in payload['docs']
    assert 'docs/253-docs-cues-markup-kind-metadata.md' in payload['docs']
    assert 'docs/254-docs-cues-literal-kind-metadata.md' in payload['docs']
    assert 'docs/255-docs-cues-definition-kind-metadata.md' in payload['docs']
    assert 'docs/256-docs-cues-heading-kind-metadata.md' in payload['docs']
    assert 'docs/257-docs-cues-link-source-kind-metadata.md' in payload['docs']
    assert 'docs/258-docs-cues-image-source-kind-metadata.md' in payload['docs']
    assert 'docs/259-docs-cues-reference-form-metadata.md' in payload['docs']
    assert 'docs/260-docs-cues-markup-delimiter-metadata.md' in payload['docs']
    assert 'docs/261-docs-cues-code-delimiter-metadata.md' in payload['docs']
    assert 'docs/262-docs-cues-fenced-code-source-metadata.md' in payload['docs']
    assert 'docs/263-docs-cues-table-alignment-metadata.md' in payload['docs']
    assert 'docs/264-docs-cues-blockquote-alert-kind-metadata.md' in payload['docs']
    assert 'docs/265-docs-cues-heading-level-metadata.md' in payload['docs']
    assert 'docs/266-docs-cues-heading-fragment-source-metadata.md' in payload['docs']
    assert 'docs/267-docs-cues-task-list-kind-metadata.md' in payload['docs']
    assert 'docs/268-docs-cues-task-state-metadata.md' in payload['docs']
    assert 'src/micromax/portability_suite.py' in payload['code']
    assert 'portability/kernel_cases.json' in payload['code']
    assert 'docs/181-portability-pick-roll-cases.md' in payload['docs']
    assert 'docs/182-portability-pick-roll-indexing.md' in payload['docs']
    assert 'docs/183-portability-pick-roll-four-item.md' in payload['docs']
    assert 'docs/184-portability-pick-roll-five-item.md' in payload['docs']
    assert 'docs/185-portability-pick-roll-errors.md' in payload['docs']
    assert 'docs/186-portability-qdup.md' in payload['docs']
    assert 'docs/187-portability-negate-abs-zero-less.md' in payload['docs']
    assert 'docs/188-portability-min-max.md' in payload['docs']
    assert 'docs/189-portability-oneplus-oneminus-zeropreds.md' in payload['docs']
    assert 'docs/190-portability-twostar-twoslash.md' in payload['docs']
    assert 'docs/191-portability-2over-2swap.md' in payload['docs']
    assert 'docs/192-portability-2rot.md' in payload['docs']
    assert 'docs/193-portability-2returnstack-pairs.md' in payload['docs']
    assert 'docs/194-portability-2nip-2tuck.md' in payload['docs']
    assert 'docs/195-portability-2rdrop.md' in payload['docs']
    assert 'docs/196-portability-not-equals.md' in payload['docs']
    assert 'docs/197-portability-basic-stack-pairs.md' in payload['docs']
    assert 'docs/198-portability-keep.md' in payload['docs']
    assert 'docs/199-portability-recovery-error-stacks.md' in payload['docs']
    assert 'docs/200-portability-assert.md' in payload['docs']
    assert 'docs/201-portability-stdlib-coverage-audit.md' in payload['docs']
    assert payload['current_priorities']
    assert any('Rust VM spike' in item or 'Rust' in item for item in payload['current_priorities']) is False
    revisions = payload['revision_sources']
    assert revisions['ok'] is True
    assert revisions['warnings'] == []
    assert revisions['current_rev'] == _expected_rev()
    assert revisions['todo_first_line_rev'] == _expected_rev()
    assert revisions['todo_heading_rev'] == _expected_rev()
    assert revisions['readme_latest_rev'] == _expected_rev()
    assert payload['checks']['revision_warnings'] == []
    portability = payload['portability']
    assert portability['kernel_cases_path'] == 'portability/kernel_cases.json'
    assert portability['case_count'] >= 150
    assert portability['category_counts']['kernel'] > 0
    assert portability['category_counts']['stdlib'] > 0
    assert portability['boot_stdlib_manifest']['all_cases_present'] is True
    assert portability['boot_stdlib_manifest']['word_count'] > 0
    assert portability['boot_stdlib_source']['source_path'] == 'src/micromax/stdlib/core.mx'
    assert portability['boot_stdlib_source']['word_count'] >= portability['boot_stdlib_manifest']['word_count']
    assert portability['boot_stdlib_source']['alias_count'] >= 0
