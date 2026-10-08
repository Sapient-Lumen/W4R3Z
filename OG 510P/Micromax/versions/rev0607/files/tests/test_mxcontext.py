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
    assert 'docs/447-command-palette-location-truth.md' in payload['docs']
    assert 'docs/448-recent-location-dedupe.md' in payload['docs']
    assert 'docs/449-showrecentdir-location-dedupe.md' in payload['docs']
    assert 'docs/450-recent-group-summary-row-truth.md' in payload['docs']
    assert 'docs/451-project-root-summary-filename-dedupe.md' in payload['docs']
    assert 'docs/452-showrecent-completion-section-dedupe.md' in payload['docs']
    assert 'docs/453-recent-inventory-truth.md' in payload['docs']
    assert 'docs/454-recent-command-completion.md' in payload['docs']
    assert 'docs/459-recent-picker-selected-slot-truth.md' in payload['docs']
    assert 'docs/460-recent-picker-query-completion.md' in payload['docs']
    assert 'docs/461-recent-clear-count-hostcall.md' in payload['docs']
    assert 'docs/462-recent-picker-row-hostcalls.md' in payload['docs']
    assert 'docs/463-showrecent-slot-detail.md' in payload['docs']
    assert 'docs/465-showrecentdir-slot-detail.md' in payload['docs']
    assert 'docs/466-showjump-hash-dialect.md' in payload['docs']
    assert 'docs/467-jump-section-summary-rows.md' in payload['docs']
    assert 'docs/468-jumppick-hash-dialect.md' in payload['docs']
    assert 'docs/469-jumppick-command-completion.md' in payload['docs']
    assert 'docs/470-jumppick-exact-miss.md' in payload['docs']
    assert 'docs/471-jumppick-submit-slot-feedback.md' in payload['docs']
    assert 'docs/472-jump-navigation-slot-feedback.md' in payload['docs']
    assert 'docs/473-jump-navigation-status-model.md' in payload['docs']
    assert 'docs/474-jump-navigation-command-preview.md' in payload['docs']
    assert 'docs/475-jumps-command-preview.md' in payload['docs']
    assert 'docs/476-showjumpgroups-command-preview.md' in payload['docs']
    assert 'docs/477-showjump-command-preview.md' in payload['docs']
    assert 'docs/478-jumppick-command-preview.md' in payload['docs']
    assert 'docs/479-showstatus-command-preview.md' in payload['docs']
    assert 'docs/480-showrecent-command-preview.md' in payload['docs']
    assert 'docs/481-showrecentdir-command-preview.md' in payload['docs']
    assert 'docs/482-showrecentgroups-command-preview.md' in payload['docs']
    assert 'docs/483-showrecentdirgroups-command-preview.md' in payload['docs']
    assert 'docs/484-recentpick-command-preview.md' in payload['docs']
    assert 'docs/485-recentdirpick-command-preview.md' in payload['docs']
    assert 'docs/486-recent-command-preview.md' in payload['docs']
    assert 'docs/487-recentpick-exact-slot-miss.md' in payload['docs']
    assert 'docs/488-showrecentdir-exact-slot-miss.md' in payload['docs']
    assert 'docs/489-showrecent-exact-path-miss.md' in payload['docs']
    assert 'docs/490-showrecentdir-exact-path-miss.md' in payload['docs']
    assert 'docs/491-recent-group-zero-summary-preview.md' in payload['docs']
    assert 'docs/492-recent-picker-zero-summary-preview.md' in payload['docs']
    assert 'docs/493-recent-command-exact-slot-miss.md' in payload['docs']
    assert 'docs/494-recent-command-hash-doc.md' in payload['docs']
    assert 'docs/495-save-saveas-command-preview.md' in payload['docs']
    assert 'docs/496-group-summary-command-preview.md' in payload['docs']
    assert 'docs/497-close-family-command-preview.md' in payload['docs']
    assert 'docs/498-quit-command-preview.md' in payload['docs']
    assert 'docs/499-undo-redo-command-preview.md' in payload['docs']
    assert 'docs/500-close-force-command-preview.md' in payload['docs']
    assert 'docs/501-showkeymodes-command-preview.md' in payload['docs']
    assert 'docs/502-showhooks-command-preview.md' in payload['docs']
    assert 'docs/503-plugin-list-command-preview.md' in payload['docs']
    assert 'docs/504-macro-subcommand-preview.md' in payload['docs']
    assert 'docs/505-plugin-subcommand-preview.md' in payload['docs']
    assert 'docs/506-macro-slot-command-preview.md' in payload['docs']
    assert 'docs/507-macro-action-command-preview.md' in payload['docs']
    assert 'docs/508-plugin-target-command-preview.md' in payload['docs']
    assert 'docs/509-showplugin-missing-command-preview.md' in payload['docs']
    assert 'docs/510-showhook-missing-command-preview.md' in payload['docs']
    assert 'docs/511-exact-inspection-missing-command-preview.md' in payload['docs']
    assert 'docs/512-exact-editor-state-missing-command-preview.md' in payload['docs']
    assert 'docs/513-showbindings-mode-command-preview.md' in payload['docs']
    assert 'docs/514-showbindings-command-preview.md' in payload['docs']
    assert 'docs/515-whichkey-command-preview.md' in payload['docs']
    assert 'docs/516-group-summary-sample-truth.md' in payload['docs']
    assert 'docs/517-group-summary-command-preview-wording.md' in payload['docs']
    assert 'docs/518-recent-group-preview-neutral-wording.md' in payload['docs']
    assert 'docs/519-showjumpgroups-sample-preview.md' in payload['docs']
    assert 'docs/520-showhooks-empty-sample-preview.md' in payload['docs']
    assert 'docs/521-showkeymodes-empty-sample-preview.md' in payload['docs']
    assert 'docs/522-active-binding-empty-witness.md' in payload['docs']
    assert 'docs/523-plugin-manager-unavailable-previews.md' in payload['docs']
    assert 'docs/524-pluginpick-no-manager-feedback.md' in payload['docs']
    assert 'docs/525-pluginpick-compact-menu-dialect.md' in payload['docs']
    assert 'docs/526-pluginpick-command-preview.md' in payload['docs']
    assert 'docs/527-plugin-root-command-preview.md' in payload['docs']
    assert 'docs/528-showplugin-command-preview.md' in payload['docs']
    assert 'docs/529-plugin-subcommand-empty-subset-witness.md' in payload['docs']
    assert 'docs/530-plugin-reload-target-detail-preview.md' in payload['docs']
    assert 'docs/531-plugin-info-target-state-fallback.md' in payload['docs']
    assert 'docs/532-plugin-exact-multierror-preview.md' in payload['docs']
    assert 'docs/534-plugin-errors-available-state-witness.md' in payload['docs']
    assert 'docs/535-plugin-runtime-zeroerror-state-witness.md' in payload['docs']
    assert 'docs/536-plugin-info-available-notloaded-preview.md' in payload['docs']
    assert 'docs/537-showplugin-runtime-available-witness.md' in payload['docs']
    assert 'docs/538-showplugin-runtime-multierror-summary.md' in payload['docs']
    assert 'docs/539-plugin-reload-runtime-broken-detail.md' in payload['docs']
    assert 'docs/540-plugin-runtime-filterederror-detail.md' in payload['docs']
    assert 'docs/541-plugin-runtime-singleerror-dedup.md' in payload['docs']
    assert 'docs/542-showplugin-runtime-loaded-state-witness.md' in payload['docs']
    assert 'docs/543-plugin-errors-runtime-emptywitness.md' in payload['docs']
    assert 'docs/544-plugin-info-runtime-loaded-witness.md' in payload['docs']
    assert 'docs/546-plugin-runtime-no-manager-distinction.md' in payload['docs']
    assert 'docs/547-plugin-runtime-root-summary.md' in payload['docs']
    assert 'docs/548-showplugin-runtime-root-summary.md' in payload['docs']
    assert 'docs/540-plugin-runtime-filterederror-detail.md' in payload['docs']
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
