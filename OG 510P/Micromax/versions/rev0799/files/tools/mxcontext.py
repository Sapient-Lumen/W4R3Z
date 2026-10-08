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
    "docs/549-mkrevzip-scratch-tree-hygiene.md",
    "docs/550-showhook-root-summary.md",
    "docs/551-showkeymode-root-summary.md",
    "docs/552-showoption-root-summary.md",
    "docs/553-showcmd-root-summary.md",
    "docs/554-showaction-root-summary.md",
    "docs/555-showword-root-summary.md",
    "docs/556-showkey-root-summary.md",
    "docs/557-showbuffer-root-summary.md",
    "docs/558-showmark-root-summary.md",
    "docs/559-showjump-root-summary.md",
    "docs/560-showrecent-root-summary.md",
    "docs/561-showrecentdir-root-summary.md",
    "docs/562-showdoc-root-summary.md",
    "docs/563-showtopic-root-summary.md",
    "docs/564-showhelpheading-command-preview.md",
    "docs/565-showhelplink-command-preview.md",
    "docs/566-helpfollow-command-preview.md",
    "docs/567-helplinkcopy-command-preview.md",
    "docs/568-helpcopylink-command-preview.md",
    "docs/569-helpback-command-preview.md",
    "docs/570-helpforward-command-preview.md",
    "docs/571-helpresume-command-preview.md",
    "docs/572-helpprune-command-preview.md",
    "docs/573-helphistory-command-preview.md",
    "docs/574-helpnavpick-command-preview.md",
    "docs/575-helpoutlinepick-command-preview.md",
    "docs/576-showhelpnav-command-preview.md",
    "docs/577-helpjump-command-preview.md",
    "docs/578-helplinkpick-command-preview.md",
    "docs/579-url-command-preview.md",
    "docs/580-buffers-marks-command-preview.md",
    "docs/581-buffer-mark-root-summaries.md",
    "docs/582-buffer-mark-pickers-command-preview.md",
    "docs/583-revision-package-bullet-guard.md",
    "docs/584-todo-history-package-bullet-guard.md",
    "docs/585-todo-handoff-trail-guard.md",
    "docs/586-macro-root-summary.md",
    "docs/587-macro-alias-completion-parity.md",
    "docs/588-macro-runtime-feedback-aliases.md",
    "docs/589-macro-playback-blockers.md",
    "docs/590-macro-slot-blocker-preview.md",
    "docs/591-macro-count-preview.md",
    "docs/592-macro-arity-guards.md",
    "docs/593-macro-unknown-subcommand-preview.md",
    "docs/594-macro-count-menu-blockers.md",
    "docs/595-macro-slot-menu-blockers.md",
    "docs/596-macro-root-alias-syntax.md",
    "docs/597-macro-play-recording-guard.md",
    "docs/598-macro-count-blocker-precedence.md",
    "docs/599-macro-play-hostcall-playback-guard.md",
    "docs/600-macro-direct-hostcall-blockers.md",
    "docs/601-macro-get-missing-slot-truth.md",
    "docs/602-macro-empty-slot-inventory-truth.md",
    "docs/603-macro-set-recording-ownership-guard.md",
    "docs/604-showmacro-exact-inspection.md",
    "docs/605-showmacro-last-empty-default-slot.md",
    "docs/606-showmacro-root-default-slot-summary.md",
    "docs/607-showmacro-idle-default-slot-summary.md",
    "docs/608-showmacro-last-first-completion.md",
    "docs/609-macro-default-slot-last-first-menus.md",
    "docs/610-macro-play-root-default-slot-summary.md",
    "docs/611-macro-play-last-default-badge.md",
    "docs/612-macro-play-last-default-action-text.md",
    "docs/613-macro-status-default-slot-summary.md",
    "docs/614-macro-root-default-slot-summary.md",
    "docs/615-macro-list-default-badge.md",
    "docs/616-macro-preview-list-default-badge.md",
    "docs/617-macro-record-last-default-action-text.md",
    "docs/618-macro-record-last-default-badge.md",
    "docs/619-macro-default-badge-helper.md",
    "docs/620-macro-record-root-default-slot-steps.md",
    "docs/621-macro-play-last-empty-default-slot.md",
    "docs/622-macro-play-root-default-action-summary.md",
    "docs/623-macro-record-root-default-action-summary.md",
    "docs/624-macro-doc-dialect-normalization.md",
    "docs/625-macro-default-slot-steps-helper.md",
    "docs/626-macro-default-slot-action-helpers.md",
    "docs/627-macro-default-slot-empty-runtime-helper.md",
    "docs/628-macro-missing-runtime-helper.md",
    "docs/629-macro-invalid-count-runtime-helper.md",
    "docs/630-macro-invalid-count-type-runtime-helper.md",
    "docs/631-macro-count-row-validation-precedence.md",
    "docs/632-macro-main-doc-sync.md",
    "docs/633-macro-root-live-action-summary.md",
    "docs/634-showmacro-root-live-action-summary.md",
    "docs/635-macro-guide-sync.md",
    "docs/636-macro-root-sample-dedup.md",
    "docs/637-macro-status-sample-dedup.md",
    "docs/638-macro-preview-sample-helper.md",
    "docs/639-showmacro-read-only-while-recording.md",
    "docs/640-show-commands-read-only-while-recording.md",
    "docs/641-command-recording-success-only.md",
    "docs/642-action-recording-success-only.md",
    "docs/643-macro-recordability-helpers.md",
    "docs/644-jumps-read-only-while-recording.md",
    "docs/645-pwd-helphistory-read-only-recording.md",
    "docs/646-help-apropos-read-only-recording.md",
    "docs/647-macro-recordability-constants.md",
    "docs/648-picker-commands-read-only-recording.md",
    "docs/649-macro-recordability-pattern-constants.md",
    "docs/650-help-family-read-only-recording.md",
    "docs/651-whichkey-read-only-recording.md",
    "docs/652-prefixmode-read-only-recording.md",
    "docs/653-macro-recordability-kind-helper.md",
    "docs/654-test-suite-portability-runway.md",
    "docs/655-host-test-hygiene-runway.md",
    "docs/656-command-parse-error-hygiene.md",
    "docs/657-macro-replay-atomicity-trust.md",
    "docs/658-macro-replay-history-hygiene.md",
    "docs/659-macro-replay-undo-history-hygiene.md",
    "docs/660-qreplace-zero-width-hygiene.md",
    "docs/661-replace-family-flag-hygiene.md",
    "docs/662-replace-zero-width-hygiene.md",
    "docs/663-replace-template-error-hygiene.md",
    "docs/664-replace-template-backslash-hygiene.md",
    "docs/665-replace-template-parser-hygiene.md",
    "docs/666-replace-template-brace-hygiene.md",
    "docs/667-replace-template-leading-zero-hygiene.md",
    "docs/668-replace-template-unclosed-brace-hygiene.md",
    "docs/669-regex-hostcall-unmatched-capture-hygiene.md",
    "docs/670-regex-hostcall-flag-hygiene.md",
    "docs/671-regex-hostcall-start-hygiene.md",
    "docs/672-regex-hostcall-sub-zero-width-hygiene.md",
    "docs/673-regex-hostcall-replacement-error-hygiene.md",
    "docs/674-editor-replacement-no-match-template-hygiene.md",
    "docs/675-regex-hostcall-out-of-range-start-hygiene.md",
    "docs/676-regex-hostcall-sentinel-flag-hygiene.md",
    "docs/677-regex-hostcall-start-sentinel-hygiene.md",
    "docs/678-string-hostcall-integer-sentinel-hygiene.md",
    "docs/679-string-replace-empty-needle-hygiene.md",
    "docs/680-string-format-boolean-data-hygiene.md",
    "docs/681-string-format-boolean-repr-hygiene.md",
    "docs/682-string-format-boolean-key-hygiene.md",
    "docs/683-string-format-argument-underflow-hygiene.md",
    "docs/684-string-format-plan-preflight-hygiene.md",
    "docs/685-string-format-data-preflight-hygiene.md",
    "docs/686-string-join-preflight-hygiene.md",
    "docs/687-string-replace-preflight-hygiene.md",
    "docs/688-string-split-preflight-hygiene.md",
    "docs/689-stdlib-package-resource-trust.md",
    "docs/690-test-runway-chunked-runner.md",
    "docs/691-datacube-index-seed.md",
    "docs/692-replace-preview-plan.md",
    "docs/693-mxtest-resumable-manifest.md",
    "docs/694-mxtest-segment-duration-scheduler.md",
    "docs/695-mxtest-all-chunks-resume.md",
    "docs/696-mxtest-history-diff-recommend.md",
    "docs/697-mxtest-source-attestation.md",
    "docs/698-mxtest-current-source-verify.md",
    "docs/699-mxtest-environment-attestation.md",
    "docs/700-mxtest-resume-environment-gate.md",
    "docs/701-mxtest-current-manifest-audit.md",
    "docs/702-mxtest-manifest-summary.md",
    "docs/703-cloudtainer-audit-docscan-cachefix.md",
    "docs/704-docs-index-doctor-entrypoints.md",
    "docs/705-prompt-seams-pathquote-cache.md",
    "docs/706-action-seams-plugin-reload-macroinput.md",
    "docs/707-plugin-reload-transactional-stage.md",
    "docs/708-plugin-unload-runtime-boundary.md",
    "docs/709-saveas-transactional-write-boundary.md",
    "docs/710-atomic-save-external-freshness.md",
    "docs/711-save-conflict-recovery-statcheap.md",
    "docs/712-script-filecaps-structured-recovery.md",
    "docs/713-mxtest-verbosity-empty-selection-safety.md",
    "docs/714-mxtest-heartbeat-timeout-checkpoint.md",
    "docs/715-diskstate-caprows-capboundary.md",
    "docs/716-script-filecaps-final-containment.md",
    "docs/717-mxtest-processgroup-fileisolated-doctor.md",
    "docs/718-dirfd-save-parent-swap.md",
    "docs/719-fs-hostcalls-finalcontain-openread.md",
    "docs/720-mxtest-interrupt-plugin-dictionary-pycache.md",
    "docs/721-mkparents-require-capboundary.md",
    "docs/722-capmutation-persistio-boundary.md",
    "docs/723-script-code-load-deferred-boundary.md",
    "docs/724-deferred-keybinding-macro-authority.md",
    "docs/725-plugin-callback-wordlist-context.md",
    "docs/726-plugin-callback-failure-rollback.md",
    "docs/727-plugin-group-provenance-guard.md",
    "docs/728-script-option-policy-hostknobs.md",
    "docs/729-script-dirty-autosave-taint.md",
    "docs/730-readonly-hostcall-edit-boundary.md",
    "docs/731-plugin-callback-generation-token.md",
    "docs/732-hostcall-url-boundary.md",
    "docs/733-runtime-registration-chdir-bufferdiscard.md",
    "docs/734-macro-registry-recording-authority.md",
    "docs/735-transient-input-directedit-undo.md",
    "docs/736-direct-save-fd-hostcall-preflight.md",
    "docs/737-prompt-origin-delayed-submit.md",
    "docs/738-directsave-digest-editpreflight.md",
    "docs/739-active-keymode-authority.md",
    "docs/740-direct-fsync-selection-boundary.md",
    "docs/741-withundo-runtimepreflight-doctorbatch.md",
    "docs/742-withundo-marks-scopepreflight.md",
    "docs/743-cursorstate-message-timer-boundary.md",
    "docs/744-runtime-transaction-scope-boundaries.md",
    "docs/745-bridge-popfree-markonly-transaction.md",
    "docs/746-value-snapshot-mutable-rollback.md",
    "docs/747-mark-authority-plugin-rollback.md",
    "docs/748-help-docs-contained-paths.md",
    "docs/749-selection-stack-authority.md",
    "docs/750-jumplist-authority-boundary.md",
    "docs/751-recent-register-authority.md",
    "docs/752-help-message-register-authority.md",
    "docs/752-message-log-authority-boundary.md",
    "docs/752-state-history-clear-capability.md",
    "docs/753-history-clear-capability-wiring.md",
    "docs/754-helphistory-replay-cap-boundary.md",
    "docs/755-undo-redo-authority-boundary.md",
    "docs/756-persisted-history-provenance.md",
    "docs/757-clipboard-register-authority.md",
    "docs/revision-index.json",
]

CODE = [
    "pyproject.toml",
    "Makefile",
    "src/micromax/vm.py",
    "src/micromax/core.py",
    "src/micromax/portability_suite.py",
    "src/micromax/stdlib/core.mx",
    "src/micromax_editor/editor.py",
    "src/micromax_editor/undo.py",
    "src/micromax_editor/actions_default.py",
    "src/micromax_editor/options_default.py",
    "src/micromax_editor/capabilities.py",
    "src/micromax_editor/option_policy.py",
    "src/micromax_editor/edit_boundary.py",
    "src/micromax_editor/hostcall_boundary.py",
    "src/micromax_editor/hostcall_transactions.py",
    "src/micromax_editor/url_policy.py",
    "src/micromax_editor/runtime_policy.py",
    "src/micromax_editor/macro_policy.py",
    "src/micromax_editor/buffer_scriptops.py",
    "src/micromax_editor/docs_index.py",
    "src/micromax_editor/prompt_rank.py",
    "src/micromax_editor/prompt_rows.py",
    "src/micromax_editor/prompt_completion.py",
    "src/micromax_editor/prompt_model.py",
    "src/micromax_editor/plugins.py",
    "src/micromax_editor/plugin_runtime.py",
    "src/micromax_editor/file_write.py",
    "src/micromax_editor/file_access.py",
    "src/micromax_editor/file_recovery.py",
    "src/micromax_editor/file_scriptops.py",
    "src/micromax_editor/file_hostcalls.py",
    "src/micromax_editor/fs_hostcalls.py",
    "src/micromax_editor/vm_load_policy.py",
    "src/micromax_editor/command_dispatcher.py",
    "src/micromax_editor/keymap.py",
    "src/micromax_editor/timers.py",
    "src/micromax_editor/replace_plan.py",
    "src/micromax_editor/cmdline.py",
    "src/micromax_editor/micromax_bridge.py",
    "src/micromax_editor/__main__.py",
    "tests/test_editor_undo_authority.py",
    "tests/test_editor_prompt_history_authority.py",
    "tests/test_editor_clipboard_authority.py",
    "scripts/test.sh",
    "tools/mkrevzip.py",
    "tools/mxcontext.py",
    "tools/mxdoctor.py",
    "tools/mxformat.py",
    "tools/mxlint.py",
    "tools/mxtest.py",
    "portability/kernel_cases.json",
]
RUN_COMMANDS = [
    "make test",
    "make test-plan",
    "make test-chunk CHUNK=1/8",
    "make test-all-chunks",
    "make doctor",
    "make doctor-full",
    "make doctor-chunked",
    "python tools/mxtest.py --run-chunks 8 --strategy segment --isolate-files --resume --json .artifacts/mxtest-all.json",
    "python tools/mxtest.py --run-chunks 8 --strategy segment --chunk-timeout 180 --heartbeat 30 --json .artifacts/mxtest-all.json",
    "python tools/mxtest.py --verify-manifest .artifacts/mxtest-all.json",
    "python tools/mxtest.py --verify-current-source .artifacts/mxtest-all.json",
    "python tools/mxtest.py --verify-current-environment .artifacts/mxtest-all.json",
    "python tools/mxtest.py --verify-current .artifacts/mxtest-all.json",
    "python tools/mxtest.py --manifest-summary .artifacts/mxtest-all.json",
    "python tools/mxtest.py --plan --chunks 8 --strategy duration --history .artifacts/mxtest-chunk-1.json",
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



def _todo_section_entries() -> list[dict[str, Any]]:
    """Return parsed ``# TODO (revN)`` blocks in top-to-bottom order.

    Each checklist block is part of the archive's handoff trail. Surface the
    heading rev plus any explicit ``package rev...`` bullet so repo checks can
    spot stale packaged-rev claims in older recent sections too, not just the
    newest block.
    """

    lines = _read_text("TODO.md").splitlines()
    entries: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    current_lines: list[str] = []

    def finish() -> None:
        nonlocal current, current_lines
        if current is None:
            return
        entry = dict(current)
        entry["lines"] = list(current_lines)
        entry.setdefault("package_rev", None)
        entry.setdefault("package_line", "")
        entries.append(entry)
        current = None
        current_lines = []

    for line in lines:
        stripped = line.strip()
        if stripped.startswith('# TODO'):
            finish()
            current = {
                "heading": stripped,
                "section_rev": _extract_rev(stripped),
            }
            continue
        if current is None:
            continue
        if stripped.startswith('# '):
            finish()
            continue
        current_lines.append(line)
        if not stripped.startswith('- ['):
            continue
        if 'package rev' not in stripped.lower():
            continue
        pkg_rev = _extract_rev(stripped)
        if pkg_rev is not None:
            current["package_rev"] = pkg_rev
            current["package_line"] = stripped
        elif not current.get("package_line"):
            current["package_line"] = stripped
    finish()
    return entries



def _current_todo_section_lines() -> tuple[int | None, list[str]]:
    """Return the newest ``# TODO (revN)`` block as ``(rev, lines)``.

    The top checklist block is the closest thing this archive has to an explicit
    handoff contract for the next packaging loop. Keeping that block parseable
    lets ``mxcontext --check`` notice stale checklist bullets before they get
    baked into another release zip.
    """

    entries = _todo_section_entries()
    if not entries:
        return None, []
    first = entries[0]
    return first.get("section_rev"), list(first.get("lines") or [])



def _todo_current_section_package_rev() -> tuple[int | None, str]:
    """Return the packaged-rev checklist bullet from the newest TODO block."""

    entries = _todo_section_entries()
    if not entries:
        return None, ''
    first = entries[0]
    pkg_rev = first.get("package_rev")
    if isinstance(pkg_rev, int):
        return pkg_rev, str(first.get("package_line") or '')
    return None, str(first.get("package_line") or '')



def _todo_package_section_mismatches() -> list[dict[str, Any]]:
    """Return TODO sections whose explicit package bullet drifts from the heading rev."""

    mismatches: list[dict[str, Any]] = []
    for entry in _todo_section_entries():
        section_rev = entry.get("section_rev")
        package_rev = entry.get("package_rev")
        if not isinstance(section_rev, int) or not isinstance(package_rev, int):
            continue
        if section_rev == package_rev:
            continue
        mismatches.append(
            {
                "section_rev": section_rev,
                "package_rev": package_rev,
                "package_line": str(entry.get("package_line") or ''),
                "heading": str(entry.get("heading") or ''),
            }
        )
    return mismatches






def _todo_recent_handoff_blocks() -> list[dict[str, Any]]:
    """Return recent TODO handoff blocks from the checklist-era trail.

    The newest part of ``TODO.md`` uses a repeated pattern of:
    ``RevN note`` → ``Latest tiny landing (revN)`` → ``# TODO (revN)``.
    Future humans/LLMs rely on that top trail as the archive's most legible
    handoff lane, so ``mxcontext --check`` should notice orphaned or mismatched
    preambles there too, not just stale package bullets inside checklist blocks.
    """

    lines = _read_text("TODO.md").splitlines()
    heading_re = re.compile(r'^# TODO \(rev(\d+)\)$')
    note_re = re.compile(r'^Rev(\d+) note:')
    landing_re = re.compile(r'^Latest tiny landing \(rev(\d+)\):')
    blocks: list[dict[str, Any]] = []
    outside_lines: list[str] = []
    in_recent_section = False
    recent_started = False

    for line in lines:
        heading_match = heading_re.match(line)
        if heading_match:
            heading_rev = int(heading_match.group(1))
            if heading_rev <= 600:
                break
            recent_started = True
            note_revs = [int(m.group(1)) for m in map(note_re.match, outside_lines) if m]
            landing_revs = [int(m.group(1)) for m in map(landing_re.match, outside_lines) if m]
            blocks.append(
                {
                    'heading_rev': heading_rev,
                    'note_revs': note_revs,
                    'landing_revs': landing_revs,
                    'last_note_rev': note_revs[-1] if note_revs else None,
                    'last_landing_rev': landing_revs[-1] if landing_revs else None,
                    'preamble_lines': [line for line in outside_lines if line.strip()],
                }
            )
            outside_lines = []
            in_recent_section = True
            continue
        if not recent_started:
            outside_lines.append(line)
            continue
        if in_recent_section:
            if note_re.match(line) or landing_re.match(line):
                in_recent_section = False
                outside_lines = [line]
            continue
        outside_lines.append(line)
    return blocks



def _todo_recent_handoff_mismatches() -> list[dict[str, Any]]:
    """Return recent handoff-block mismatches from the TODO checklist trail."""

    mismatches: list[dict[str, Any]] = []
    for block in _todo_recent_handoff_blocks():
        heading_rev = block['heading_rev']
        note_revs = list(block.get('note_revs') or [])
        landing_revs = list(block.get('landing_revs') or [])
        extra_revs = sorted((set(note_revs) | set(landing_revs)) - {heading_rev}, reverse=True)
        if block.get('last_note_rev') != heading_rev or block.get('last_landing_rev') != heading_rev or extra_revs:
            mismatches.append(
                {
                    'heading_rev': heading_rev,
                    'last_note_rev': block.get('last_note_rev'),
                    'last_landing_rev': block.get('last_landing_rev'),
                    'extra_revs': extra_revs,
                }
            )
    return mismatches
def revision_sources() -> dict[str, Any]:
    todo_lines = _read_text("TODO.md").splitlines()
    todo_first_line = todo_lines[0].strip() if todo_lines else ""
    readme_note = latest_note() or ""
    todo_first_rev = _extract_rev(todo_first_line)
    todo_heading_rev = _todo_heading_rev()
    todo_section_rev, _todo_section_lines = _current_todo_section_lines()
    todo_package_rev, todo_package_line = _todo_current_section_package_rev()
    todo_package_section_mismatches = _todo_package_section_mismatches()
    todo_recent_handoff_mismatches = _todo_recent_handoff_mismatches()
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
        if todo_section_rev is not None and todo_section_rev != current_rev:
            warnings.append(
                f"TODO.md current-section rev {todo_section_rev} does not match current rev {current_rev}"
            )
        for mismatch in todo_package_section_mismatches:
            section_rev = mismatch.get("section_rev")
            package_rev = mismatch.get("package_rev")
            warnings.append(
                f"TODO.md section rev {section_rev} has package bullet rev {package_rev}"
            )
        for mismatch in todo_recent_handoff_mismatches:
            heading_rev = mismatch.get("heading_rev")
            last_note_rev = mismatch.get("last_note_rev")
            last_landing_rev = mismatch.get("last_landing_rev")
            extra_revs = mismatch.get("extra_revs") or []
            if last_note_rev != heading_rev:
                warnings.append(
                    f"TODO.md handoff block before rev {heading_rev} has note rev {last_note_rev}"
                )
            if last_landing_rev != heading_rev:
                warnings.append(
                    f"TODO.md handoff block before rev {heading_rev} has landing rev {last_landing_rev}"
                )
            if extra_revs:
                extras = ', '.join(f"rev{rev}" for rev in extra_revs)
                warnings.append(
                    f"TODO.md handoff block before rev {heading_rev} contains orphan rev block(s): {extras}"
                )
    return {
        "current_rev": current_rev,
        "todo_first_line": todo_first_line,
        "todo_first_line_rev": todo_first_rev,
        "todo_heading_rev": todo_heading_rev,
        "todo_current_section_rev": todo_section_rev,
        "todo_current_section_package_rev": todo_package_rev,
        "todo_current_section_package_line": todo_package_line,
        "todo_package_section_mismatches": todo_package_section_mismatches,
        "todo_recent_handoff_mismatches": todo_recent_handoff_mismatches,
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



def startup_snapshot() -> dict[str, object]:
    from micromax import VM

    vm = VM(strict_stdlib=True)
    return {
        "stdlib": vm.stdlib_health(),
        "diagnostics": list(vm.startup_diagnostics),
        "has_finally": vm.find_word("finally") is not None,
        "has_2drop": vm.find_word("2drop") is not None,
    }


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
        "startup": startup_snapshot(),
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
    startup = data.get("startup")
    if isinstance(startup, dict):
        stdlib = startup.get("stdlib")
        if isinstance(stdlib, dict):
            print("Startup snapshot:")
            print(
                "  - stdlib: "
                f"{stdlib.get('state', 'unknown')} "
                f"({stdlib.get('resource', 'unknown')})"
            )
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
