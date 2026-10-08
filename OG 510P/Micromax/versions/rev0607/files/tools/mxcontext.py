#!/usr/bin/env python3
"""mxcontext.py

Emit a short, stable repo-context snapshot for humans and LLMs.

Usage:
  python tools/mxcontext.py
  python tools/mxcontext.py --json
  python tools/mxcontext.py --check
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

DOCS = [
    "TODO.md",
    "docs/43-worklist.md",
    "docs/00-vision.md",
    "docs/01-llm-start-here.md",
    "docs/42-portability-ledger.md",
    "docs/23-data-model.md",
    "docs/22-two-tier-execution.md",
    "docs/24-bytecode-format.md",
    "docs/25-inline-caching.md",
    "docs/27-bytecode-serialization.md",
    "docs/31-host-api.md",
    "docs/50-editor-behaviors.md",
    "docs/57-editor-multicursor.md",
    "docs/61-editor-cursorstate.md",
    "docs/63-editor-jumplist.md",
    "docs/64-editor-prompt-completion.md",
    "docs/65-debugging-spans.md",
    "docs/66-editor-micromax-commands.md",
    "docs/67-editor-keybinding-provenance.md",
    "docs/68-hook-provenance.md",
    "docs/69-editor-statusline-model.md",
    "docs/73-hook-groups.md",
    "docs/74-editor-registration-groups.md",
    "docs/75-editor-keymap-modes.md",
    "docs/76-editor-transient-keymodes.md",
    "docs/77-editor-keymap-discovery.md",
    "docs/78-editor-binding-descriptions.md",
    "docs/79-editor-prefix-maps.md",
    "docs/80-editor-mode-prefix-maps.md",
    "docs/146-keymenu.md",
    "docs/147-infobar.md",
    "docs/148-statusline-row-policy.md",
    "docs/149-constantshow.md",
    "docs/150-capture-prompts.md",
    "docs/151-capture-status-model.md",
    "docs/152-interaction-status-model.md",
    "docs/153-bottom-rows-model.md",
    "docs/154-statusline-layout-model.md",
    "docs/155-keymenu-infobar-models.md",
    "docs/156-interaction-row-model.md",
    "docs/157-screen-layout-model.md",
    "docs/158-edit-window-model.md",
    "docs/159-screen-model.md",
    "docs/160-prompt-panel-model.md",
    "docs/161-gutter-model.md",
    "docs/162-viewport-rows-model.md",
    "docs/163-screen-rows-model.md",
    "docs/164-search-rows-model.md",
    "docs/165-showchars-rows-model.md",
    "docs/166-display-rows-model.md",
    "docs/167-viewport-cues-model.md",
    "docs/168-docs-cues-model.md",
    "docs/169-headless-screen-dump-cli.md",
    "docs/170-context-cli-json.md",
    "docs/171-rust-vm-spike.md",
    "docs/176-docs-cues-link-metadata.md",
    "docs/177-docs-cues-image-metadata.md",
    "docs/178-docs-cues-code-metadata.md",
    "docs/179-docs-cues-inline-markup-metadata.md",
    "docs/180-docs-cues-literal-source-metadata.md",
    "docs/202-docs-cues-structure-metadata.md",
    "docs/203-docs-cues-table-metadata.md",
    "docs/204-docs-cues-heading-metadata.md",
    "docs/205-docs-cues-definition-metadata.md",
    "docs/206-docs-cues-block-metadata.md",
    "docs/207-docs-cues-section-metadata.md",
    "docs/208-helpoutline-section-groups.md",
    "docs/209-recentdirpick.md",
    "docs/210-helpnav-heading-breadcrumbs.md",
    "docs/211-help-breadcrumb-query-matching.md",
    "docs/212-helplink-heading-query-matching.md",
    "docs/213-help-heading-fragment-query-matching.md",
    "docs/214-helplink-target-title-query-matching.md",
    "docs/215-portability-cleanup-error-precedence.md",
    "docs/216-portability-try-handler-error-precedence.md",
    "docs/217-portability-stdlib-manifest-cli.md",
    "docs/218-portability-stdlib-source-inventory.md",
    "docs/219-portability-stdlib-dependency-inventory.md",
    "docs/220-portability-stdlib-closure-inventory.md",
    "docs/221-portability-stdlib-user-inventory.md",
    "docs/222-portability-stdlib-impact-map.md",
    "docs/223-portability-selected-retest-command.md",
    "docs/224-portability-impact-inventory.md",
    "docs/225-portability-impact-groups.md",
    "docs/226-portability-impact-group-retest-metadata.md",
    "docs/227-portability-impact-stages.md",
    "docs/228-portability-impact-slice-filters.md",
    "docs/229-portability-impact-case-filters.md",
    "docs/230-portability-impact-filter-options.md",
    "docs/231-portability-impact-semantic-filter-options.md",
    "docs/232-portability-impact-filter-suffixes.md",
    "docs/233-portability-impact-filter-commands.md",
    "docs/234-portability-impact-filter-family-modes.md",
    "docs/235-portability-impact-filter-previews.md",
    "docs/236-portability-impact-preview-effects.md",
    "docs/237-portability-impact-filter-recommendations.md",
    "docs/238-portability-impact-equivalent-cuts.md",
    "docs/239-portability-impact-distinct-recommendations.md",
    "docs/240-portability-impact-distinct-groups.md",
    "docs/241-portability-impact-representative-reasons.md",
    "docs/242-portability-impact-recommendation-ranks.md",
    "docs/243-portability-impact-primary-recommendation.md",
    "docs/244-context-portability-snapshot.md",
    "docs/245-archive-context-manifest.md",
    "docs/246-docs-cues-task-metadata.md",
    "docs/247-docs-cues-blockquote-break-metadata.md",
    "docs/248-docs-cues-list-metadata.md",
    "docs/249-docs-cues-link-target-metadata.md",
    "docs/250-docs-cues-image-target-metadata.md",
    "docs/251-docs-cues-table-kind-metadata.md",
    "docs/252-docs-cues-block-kind-metadata.md",
    "docs/253-docs-cues-markup-kind-metadata.md",
    "docs/254-docs-cues-literal-kind-metadata.md",
    "docs/255-docs-cues-definition-kind-metadata.md",
    "docs/256-docs-cues-heading-kind-metadata.md",
    "docs/257-docs-cues-link-source-kind-metadata.md",
    "docs/258-docs-cues-image-source-kind-metadata.md",
    "docs/259-docs-cues-reference-form-metadata.md",
    "docs/260-docs-cues-markup-delimiter-metadata.md",
    "docs/261-docs-cues-code-delimiter-metadata.md",
    "docs/262-docs-cues-fenced-code-source-metadata.md",
    "docs/263-docs-cues-table-alignment-metadata.md",
    "docs/264-docs-cues-blockquote-alert-kind-metadata.md",
    "docs/265-docs-cues-heading-level-metadata.md",
    "docs/266-docs-cues-heading-fragment-source-metadata.md",
    "docs/267-docs-cues-task-list-kind-metadata.md",
    "docs/268-docs-cues-task-state-metadata.md",
    "docs/181-portability-pick-roll-cases.md",
    "docs/182-portability-pick-roll-indexing.md",
    "docs/183-portability-pick-roll-four-item.md",
    "docs/184-portability-pick-roll-five-item.md",
    "docs/185-portability-pick-roll-errors.md",
    "docs/186-portability-qdup.md",
    "docs/187-portability-negate-abs-zero-less.md",
    "docs/188-portability-min-max.md",
    "docs/189-portability-oneplus-oneminus-zeropreds.md",
    "docs/190-portability-twostar-twoslash.md",
    "docs/191-portability-2over-2swap.md",
    "docs/192-portability-2rot.md",
    "docs/193-portability-2returnstack-pairs.md",
    "docs/194-portability-2nip-2tuck.md",
    "docs/195-portability-2rdrop.md",
    "docs/196-portability-not-equals.md",
    "docs/197-portability-basic-stack-pairs.md",
    "docs/198-portability-keep.md",
    "docs/199-portability-recovery-error-stacks.md",
    "docs/200-portability-assert.md",
    "docs/201-portability-stdlib-coverage-audit.md",
    "docs/71-cookbook.md",
    "docs/72-hacking-by-hand.md",
    "docs/315-showcmd-showword-miss-feedback.md",
    "docs/316-keybinding-miss-feedback.md",
    "docs/317-core-introspection-miss-feedback.md",
    "docs/318-picker-fallback-section-labels.md",
    "docs/319-buffer-command-miss-feedback.md",
    "docs/320-showhook-not-hook-feedback.md",
    "docs/321-markjump-miss-feedback.md",
    "docs/322-unknown-command-feedback.md",
    "docs/323-headless-repl-unknown-command-feedback.md",
    "docs/324-help-miss-feedback.md",
    "docs/325-macro-subcommand-miss-feedback.md",
    "docs/326-macro-play-miss-feedback.md",
    "docs/327-unbind-success-feedback.md",
    "docs/328-bind-success-feedback.md",
    "docs/329-close-success-feedback.md",
    "docs/330-command-runtime-error-feedback.md",
    "docs/331-help-doc-navigation-miss-feedback.md",
    "docs/332-plugin-no-manager-feedback.md",
    "docs/333-bulk-close-error-feedback.md",
    "docs/334-mx-command-error-feedback.md",
    "docs/335-hook-runtime-error-feedback.md",
    "docs/336-binddoc-success-feedback.md",
    "docs/337-url-command-feedback.md",
    "docs/338-option-command-feedback.md",
    "docs/339-help-link-action-feedback.md",
    "docs/340-helpfollow-miss-feedback.md",
    "docs/341-helpback-feedback.md",
    "docs/342-helpdocs-open-feedback.md",
    "docs/343-helpjump-fragment-miss-feedback.md",
    "docs/344-help-navigation-model.md",
    "docs/345-helpforward-session-history.md",
    "docs/346-helpfragment-local-history.md",
    "docs/347-help-history-register.md",
    "docs/348-helpresume-dormant-session.md",
    "docs/349-help-navigation-action-cues.md",
    "docs/350-help-navigation-blocked-targets.md",
    "docs/351-help-navigation-prune.md",
    "docs/352-help-dormant-branch-continuity.md",
    "docs/353-help-dormant-replay-continuity.md",
    "docs/354-help-dormant-same-topic-reopen.md",
    "docs/355-helpresume-active-actionability.md",
    "docs/356-helpresume-active-command-honesty.md",
    "docs/357-help-navigation-missingdoc-command-honesty.md",
    "docs/358-help-navigation-adjacent-reuse.md",
    "docs/359-jump-history-register.md",
    "docs/360-mark-inventory-rows.md",
    "docs/361-buffer-inventory-rows.md",
    "docs/362-macro-inventory-rows.md",
    "docs/363-recent-inventory-rows.md",
    "docs/364-plugin-inventory-rows.md",
    "docs/365-binding-inventory-rows.md",
    "docs/366-option-inventory-rows.md",
    "docs/367-hook-inventory-rows.md",
    "docs/368-keymode-inventory-rows.md",
    "docs/369-word-detail-row.md",
    "docs/370-command-action-detail-rows.md",
    "docs/371-binding-detail-row.md",
    "docs/372-doc-summary-after-heading.md",
    "docs/373-doc-detail-row.md",
    "docs/374-generic-help-doc-topics.md",
    "docs/375-help-heading-detail-row.md",
    "docs/376-help-link-detail-row.md",
    "docs/377-help-current-heading-detail-row.md",
    "docs/378-macro-status-rows.md",
    "docs/379-topic-detail-row.md",
    "docs/380-topic-doc-section-summary-rows.md",
    "docs/381-plugin-section-summary-rows.md",
    "docs/382-hook-summary-rows.md",
    "docs/383-helpnav-section-summary-rows.md",
    "docs/384-keymode-detail-row.md",
    "docs/385-binding-section-summary-rows.md",
    "docs/386-option-detail-row.md",
    "docs/387-option-section-summary-rows.md",
    "docs/388-command-palette-section-summary-rows.md",
    "docs/389-buffer-section-summary-rows.md",
    "docs/390-recent-section-summary-rows.md",
    "docs/391-recent-dir-section-summary-rows.md",
    "docs/392-buffer-detail-row.md",
    "docs/393-recent-detail-row.md",
    "docs/394-mark-detail-row.md",
    "docs/395-mark-section-summary-rows.md",
    "docs/396-recent-dir-detail-row.md",
    "docs/397-jump-detail-row.md",
    "docs/398-plugin-detail-row.md",
    "docs/399-replace-command-identity.md",
    "docs/400-hook-detail-row.md",
    "docs/401-keymode-completion-detail.md",
    "docs/402-showkey-completion-detail.md",
    "docs/403-buffer-completion-detail.md",
    "docs/404-mark-completion-detail.md",
    "docs/405-helpjump-completion-detail.md",
    "docs/406-showgroupcompletion-sectionsummaryprompt.md",
    "docs/407-showpalettegroups-completion-summaryprompt.md",
    "docs/408-showhelpnav-completion-summaryprompt.md",
    "docs/409-option-plugin-group-completion-summaryprompt.md",
    "docs/410-showbindingmodes-completion-summaryprompt.md",
    "docs/411-showdocs-completion-summaryprompt.md",
    "docs/412-showtopics-completion-summaryprompt.md",
    "docs/413-showhooks-completion-summaryprompt.md",
    "docs/414-showcmd-completion-detail.md",
    "docs/415-topic-command-detail-prompt.md",
    "docs/416-apropos-command-detail-prompt.md",
    "docs/417-word-topic-prompt-provenance.md",
    "docs/418-doc-topic-prompt-provenance.md",
    "docs/419-action-detail-provenance.md",
    "docs/420-commandpick-detail-prompt.md",
    "docs/421-command-palette-recent-detail.md",
    "docs/422-command-palette-openpath-context.md",
    "docs/423-command-palette-opendir-context.md",
    "docs/424-command-palette-open-row-context.md",
    "docs/425-command-palette-directory-drilldown-cue.md",
    "docs/426-command-palette-open-file-action-cue.md",
    "docs/427-command-palette-open-unsaved-file-truth.md",
    "docs/428-command-palette-parsecursor-dir-drilldown.md",
    "docs/429-command-palette-parsecursor-file-goto-cue.md",
    "docs/430-command-palette-parsecursor-relative-open-row.md",
    "docs/431-command-palette-parsecursor-extensionless-open-row.md",
    "docs/432-command-palette-parsecursor-completion-suffix.md",
    "docs/433-command-palette-parsecursor-file-cursor-request-cue.md",
    "docs/434-command-palette-parsecursor-new-file-empty-buffer-cue.md",
    "docs/435-command-palette-parsecursor-directory-completion-suffix.md",
    "docs/436-command-palette-parsecursor-partial-extensionless-completion.md",
    "docs/437-command-palette-parsecursor-known-path-completion.md",
    "docs/438-command-palette-known-missing-file-truth.md",
    "docs/439-command-palette-recent-missing-file-truth.md",
    "docs/440-command-palette-recent-missing-action-truth.md",
    "docs/441-command-palette-recent-live-action-truth.md",
    "docs/442-command-palette-recent-existing-file-truth.md",
    "docs/443-showrecent-detail-truth.md",
    "docs/444-recentpick-row-truth.md",
    "docs/445-recentpick-project-menu-truth.md",
    "docs/446-showrecentdir-sample-truth.md",
    "docs/447-command-palette-location-truth.md",
    "docs/448-recent-location-dedupe.md",
    "docs/449-showrecentdir-location-dedupe.md",
    "docs/450-recent-group-summary-row-truth.md",
    "docs/451-project-root-summary-filename-dedupe.md",
    "docs/452-showrecent-completion-section-dedupe.md",
    "docs/453-recent-inventory-truth.md",
    "docs/454-recent-command-completion.md",
    "docs/455-recent-clear-count-feedback.md",
    "docs/456-recent-slot-feedback.md",
    "docs/457-recent-picker-submit-feedback.md",
    "docs/458-recent-picker-slot-feedback.md",
    "docs/459-recent-picker-selected-slot-truth.md",
    "docs/460-recent-picker-query-completion.md",
    "docs/461-recent-clear-count-hostcall.md",
    "docs/462-recent-picker-row-hostcalls.md",
    "docs/463-showrecent-slot-detail.md",
    "docs/464-recent-slot-hash-dialect.md",
    "docs/465-showrecentdir-slot-detail.md",
    "docs/466-showjump-hash-dialect.md",
    "docs/467-jump-section-summary-rows.md",
    "docs/468-jumppick-hash-dialect.md",
    "docs/469-jumppick-command-completion.md",
    "docs/470-jumppick-exact-miss.md",
    "docs/471-jumppick-submit-slot-feedback.md",
    "docs/472-jump-navigation-slot-feedback.md",
    "docs/473-jump-navigation-status-model.md",
    "docs/474-jump-navigation-command-preview.md",
    "docs/475-jumps-command-preview.md",
    "docs/476-showjumpgroups-command-preview.md",
    "docs/477-showjump-command-preview.md",
    "docs/478-jumppick-command-preview.md",
    "docs/479-showstatus-command-preview.md",
    "docs/480-showrecent-command-preview.md",
    "docs/481-showrecentdir-command-preview.md",
    "docs/482-showrecentgroups-command-preview.md",
    "docs/483-showrecentdirgroups-command-preview.md",
    "docs/484-recentpick-command-preview.md",
    "docs/485-recentdirpick-command-preview.md",
    "docs/486-recent-command-preview.md",
    "docs/487-recentpick-exact-slot-miss.md",
    "docs/488-showrecentdir-exact-slot-miss.md",
    "docs/489-showrecent-exact-path-miss.md",
    "docs/490-showrecentdir-exact-path-miss.md",
    "docs/491-recent-group-zero-summary-preview.md",
    "docs/492-recent-picker-zero-summary-preview.md",
    "docs/493-recent-command-exact-slot-miss.md",
    "docs/494-recent-command-hash-doc.md",
    "docs/495-save-saveas-command-preview.md",
    "docs/496-group-summary-command-preview.md",
    "docs/497-close-family-command-preview.md",
    "docs/498-quit-command-preview.md",
    "docs/499-undo-redo-command-preview.md",
    "docs/500-close-force-command-preview.md",
    "docs/501-showkeymodes-command-preview.md",
    "docs/502-showhooks-command-preview.md",
    "docs/503-plugin-list-command-preview.md",
    "docs/504-macro-subcommand-preview.md",
    "docs/505-plugin-subcommand-preview.md",
    "docs/506-macro-slot-command-preview.md",
    "docs/507-macro-action-command-preview.md",
    "docs/508-plugin-target-command-preview.md",
    "docs/509-showplugin-missing-command-preview.md",
    "docs/510-showhook-missing-command-preview.md",
    "docs/511-exact-inspection-missing-command-preview.md",
    "docs/512-exact-editor-state-missing-command-preview.md",
    "docs/513-showbindings-mode-command-preview.md",
    "docs/514-showbindings-command-preview.md",
    "docs/515-whichkey-command-preview.md",
    "docs/516-group-summary-sample-truth.md",
    "docs/517-group-summary-command-preview-wording.md",
    "docs/518-recent-group-preview-neutral-wording.md",
    "docs/519-showjumpgroups-sample-preview.md",
    "docs/520-showhooks-empty-sample-preview.md",
    "docs/521-showkeymodes-empty-sample-preview.md",
    "docs/522-active-binding-empty-witness.md",
    "docs/523-plugin-manager-unavailable-previews.md",
    "docs/524-pluginpick-no-manager-feedback.md",
    "docs/525-pluginpick-compact-menu-dialect.md",
    "docs/526-pluginpick-command-preview.md",
    "docs/527-plugin-root-command-preview.md",
    "docs/528-showplugin-command-preview.md",
    "docs/529-plugin-subcommand-empty-subset-witness.md",
    "docs/530-plugin-reload-target-detail-preview.md",
    "docs/531-plugin-info-target-state-fallback.md",
    "docs/532-plugin-exact-multierror-preview.md",
    "docs/533-plugin-reload-available-candidate-witness.md",
    "docs/534-plugin-errors-available-state-witness.md",
    "docs/535-plugin-runtime-zeroerror-state-witness.md",
    "docs/536-plugin-info-available-notloaded-preview.md",
    "docs/537-showplugin-runtime-available-witness.md",
    "docs/538-showplugin-runtime-multierror-summary.md",
    "docs/539-plugin-reload-runtime-broken-detail.md",
    "docs/540-plugin-runtime-filterederror-detail.md",
    "docs/541-plugin-runtime-singleerror-dedup.md",
    "docs/542-showplugin-runtime-loaded-state-witness.md",
    "docs/543-plugin-errors-runtime-emptywitness.md",
    "docs/544-plugin-info-runtime-loaded-witness.md",
    "docs/546-plugin-runtime-no-manager-distinction.md",
    "docs/547-plugin-runtime-root-summary.md",
    "docs/548-showplugin-runtime-root-summary.md",
]

CODE = [
    "src/micromax/vm.py",
    "src/micromax/core.py",
    "src/micromax/portability_suite.py",
    "src/micromax/stdlib/core.mx",
    "src/micromax_editor/editor.py",
    "src/micromax_editor/micromax_bridge.py",
    "src/micromax_editor/__main__.py",
    "tools/mkrevzip.py",
    "tools/mxcontext.py",
    "portability/kernel_cases.json",
]

RUN_COMMANDS = [
    "make test",
    "make context",
    "make context-json",
    "make context-check",
    "python tools/mxcontext.py --json",
    "python tools/mxcontext.py --check",
    "python tools/mxportable.py --json",
    "python tools/mxportable.py --stdlib-manifest --json",
    "python tools/mxportable.py --stdlib-manifest --show-source --json",
    "python -m micromax_editor --help-doc docs/70-tutorial.md --dump-screen 24 80",
]



def _read_text(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8", errors="replace")



def _extract_rev(line: str) -> int | None:
    match = re.search(r"rev\s*(\d+)", line, flags=re.IGNORECASE)
    if match:
        return int(match.group(1))
    return None



def _todo_heading_rev() -> int | None:
    for line in _read_text("TODO.md").splitlines():
        stripped = line.strip()
        if stripped.startswith("# TODO"):
            return _extract_rev(stripped)
    return None



def revision_sources() -> dict[str, Any]:
    todo_lines = _read_text("TODO.md").splitlines()
    todo_first_line = todo_lines[0].strip() if todo_lines else ""
    readme_note = latest_note() or ""
    todo_first_rev = _extract_rev(todo_first_line)
    todo_heading_rev = _todo_heading_rev()
    readme_latest_rev = _extract_rev(readme_note)
    revisions = [rev for rev in (todo_first_rev, todo_heading_rev, readme_latest_rev) if rev is not None]
    current_rev = max(revisions) if revisions else None
    warnings: list[str] = []
    if current_rev is None:
        warnings.append("could not infer current revision from TODO.md or README.md")
    if todo_first_rev is None:
        warnings.append("TODO.md first line is missing a revision note")
    if todo_heading_rev is None:
        warnings.append("TODO.md heading is missing a revision")
    if readme_latest_rev is None:
        warnings.append("README.md is missing a latest revision note")
    if current_rev is not None:
        if todo_first_rev is not None and todo_first_rev != current_rev:
            warnings.append(
                f"TODO.md first-line rev {todo_first_rev} does not match current rev {current_rev}"
            )
        if todo_heading_rev is not None and todo_heading_rev != current_rev:
            warnings.append(
                f"TODO.md heading rev {todo_heading_rev} does not match current rev {current_rev}"
            )
        if readme_latest_rev is not None and readme_latest_rev != current_rev:
            warnings.append(
                f"README.md latest note rev {readme_latest_rev} does not match current rev {current_rev}"
            )
    return {
        "current_rev": current_rev,
        "todo_first_line": todo_first_line,
        "todo_first_line_rev": todo_first_rev,
        "todo_heading_rev": todo_heading_rev,
        "readme_latest_note": readme_note,
        "readme_latest_rev": readme_latest_rev,
        "warnings": warnings,
        "ok": len(warnings) == 0,
    }



def infer_rev() -> int:
    info = revision_sources()
    current_rev = info.get("current_rev")
    if isinstance(current_rev, int):
        return current_rev
    raise SystemExit("could not infer rev from TODO.md or README.md")


def latest_note() -> str | None:
    for line in _read_text("README.md").splitlines():
        stripped = line.strip()
        if stripped.startswith("Rev") and " note:" in stripped:
            return stripped
    return None



def current_priorities() -> list[str]:
    lines = _read_text("TODO.md").splitlines()
    in_section = False
    priorities: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped.lower() == "## next up (high leverage)":
            in_section = True
            continue
        if in_section and stripped.startswith("## "):
            break
        if not in_section:
            continue
        match = re.match(r"\d+\.\s+(.*)$", stripped)
        if match:
            text = re.sub(r"\*\*", "", match.group(1)).strip()
            priorities.append(text)
    return priorities



def missing_paths() -> list[str]:
    missing: list[str] = []
    for rel in DOCS + CODE:
        if not (ROOT / rel).exists():
            missing.append(rel)
    return missing



def _load_portability_cases() -> list[dict[str, object]]:
    path = ROOT / "portability" / "kernel_cases.json"
    return json.loads(path.read_text(encoding="utf-8"))



def portability_snapshot() -> dict[str, object]:
    from micromax.portability_suite import boot_stdlib_manifest_inventory, boot_stdlib_word_specs

    cases = _load_portability_cases()
    category_counts = Counter(str(case.get("category") or "") for case in cases if str(case.get("category") or ""))
    tag_counts: Counter[str] = Counter()
    host_feature_counts: Counter[str] = Counter()
    for case in cases:
        tag_counts.update(str(tag) for tag in (case.get("tags") or []) if str(tag))
        host_feature_counts.update(str(feat) for feat in (case.get("host_features") or []) if str(feat))
    manifest = boot_stdlib_manifest_inventory(cases)
    specs = boot_stdlib_word_specs()
    alias_words = sorted(word for word, spec in specs.items() if str(spec.get("alias_of") or ""))
    max_depth = max((int(spec.get("stdlib_depth") or 0) for spec in specs.values()), default=0)
    return {
        "kernel_cases_path": "portability/kernel_cases.json",
        "case_count": len(cases),
        "category_counts": {name: int(category_counts[name]) for name in sorted(category_counts)},
        "tag_counts": {name: int(tag_counts[name]) for name in sorted(tag_counts)},
        "host_feature_counts": {name: int(host_feature_counts[name]) for name in sorted(host_feature_counts)},
        "boot_stdlib_manifest": {
            "word_count": int(manifest.get("word_count") or 0),
            "manifest_case_count": int(manifest.get("manifest_case_count") or 0),
            "all_cases_present": bool(manifest.get("all_cases_present")),
            "missing_words": [str(word) for word in (manifest.get("missing_words") or [])],
        },
        "boot_stdlib_source": {
            "source_path": "src/micromax/stdlib/core.mx",
            "word_count": len(specs),
            "alias_count": len(alias_words),
            "alias_words": alias_words,
            "max_dependency_depth": max_depth,
        },
    }



def payload() -> dict[str, object]:
    missing = missing_paths()
    revisions = revision_sources()
    return {
        "project": "micromax",
        "rev": infer_rev(),
        "latest_note": latest_note(),
        "current_priorities": current_priorities(),
        "docs": DOCS,
        "code": CODE,
        "run_commands": RUN_COMMANDS,
        "top_level": sorted(x.name for x in ROOT.iterdir() if not x.name.startswith('.')),
        "revision_sources": revisions,
        "checks": {
            "missing_paths": missing,
            "revision_warnings": list(revisions.get("warnings") or []),
            "ok": len(missing) == 0 and bool(revisions.get("ok")),
        },
        "portability": portability_snapshot(),
    }



def print_human(data: dict[str, object]) -> None:
    print("micromax repo context")
    print("====================")
    print()
    print(f"Rev: {data['rev']}")
    note = data.get("latest_note")
    if isinstance(note, str) and note:
        print(f"Latest note: {note}")
        print()
    priorities = data.get("current_priorities")
    if isinstance(priorities, list) and priorities:
        print("Current priorities:")
        for i, item in enumerate(priorities, start=1):
            print(f"  {i}. {item}")
        print()
    revisions = data.get("revision_sources")
    if isinstance(revisions, dict) and not revisions.get("ok", True):
        print("Revision warnings:")
        for warning in revisions.get("warnings") or []:
            print(f"  - {warning}")
        print()
    portability = data.get("portability")
    if isinstance(portability, dict):
        print("Portability snapshot:")
        print(f"  - cases: {portability.get('case_count', 0)}")
        categories = portability.get("category_counts")
        if isinstance(categories, dict) and categories:
            joined = ", ".join(f"{name}={categories[name]}" for name in sorted(categories))
            print(f"  - categories: {joined}")
        manifest = portability.get("boot_stdlib_manifest")
        if isinstance(manifest, dict):
            status = "all manifest cases present" if manifest.get("all_cases_present") else f"missing words: {', '.join(manifest.get('missing_words') or []) or '(unknown)'}"
            print(
                "  - stdlib manifest: "
                f"{manifest.get('word_count', 0)} words / {manifest.get('manifest_case_count', 0)} case refs ({status})"
            )
        source = portability.get("boot_stdlib_source")
        if isinstance(source, dict):
            print(
                "  - stdlib source: "
                f"{source.get('word_count', 0)} defs, {source.get('alias_count', 0)} aliases, depth<= {source.get('max_dependency_depth', 0)}"
            )
        print()
    print("Key entrypoints:")
    for p in data["docs"]:
        print(f"  - {p}")
    print()
    print("Key code:")
    for p in data["code"]:
        print(f"  - {p}")
    print()
    print("Useful commands:")
    for cmd in data["run_commands"]:
        print(f"  - {cmd}")
    print()
    print("Repo tree (top-level):")
    for p in data["top_level"]:
        print(f"  - {p}")



def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true", help="emit machine-readable repo context JSON")
    ap.add_argument("--check", action="store_true", help="fail if referenced docs/code paths are missing")
    args = ap.parse_args(argv)

    data = payload()
    if args.json:
        print(json.dumps(data, indent=2, sort_keys=True))
    else:
        print_human(data)

    if args.check:
        checks = data["checks"]
        missing = list(checks["missing_paths"])
        warnings = list(checks.get("revision_warnings") or [])
        if missing or warnings:
            if not args.json:
                if missing:
                    print()
                    print("Missing referenced paths:")
                    for rel in missing:
                        print(f"  - {rel}")
                if warnings:
                    print()
                    print("Revision warnings:")
                    for warning in warnings:
                        print(f"  - {warning}")
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
