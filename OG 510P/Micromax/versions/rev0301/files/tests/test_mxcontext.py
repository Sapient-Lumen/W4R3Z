from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]



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
    assert 'Rev: 300' in proc.stdout
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
    assert payload['rev'] == 300
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
