# 310. Voter-facing public-answer surfaces family map and promotion rules

**Track:** Shared

This document treats the voter-facing public-answer surfaces named in `artifacts/tables/voter-facing-public-answer-surfaces.csv` as a **single bounded family**.
The goal is **not** to add yet another public surface. The goal is to keep the family **navigable, non-overlapping, and growth-disciplined** as the archive accumulates.

It exists to make five things easier:

1. deciding **which existing surface** should carry a given voter-facing fact,
2. deciding when a proposed new surface is **actually distinct** rather than a synonym for an existing one,
3. keeping `308` (calendar synthesis), `305` (contact routing), and `307` (problem/escalation routing) from swallowing every other surface,
4. giving maintainers a compact map of the **canonical voter questions** already covered, and
5. keeping future additions **payload-shaped** (docs + template + checklist), rather than allowing the archive to drift into a sprawling FAQ anthology.

It composes with:
- `docs/195-rumor-control-and-status-boards-as-verifiable-public-surfaces.md`
- `docs/203-official-channel-directory-as-evidence.md`
- `docs/205-cache-and-freshness-controls-for-public-surfaces.md`
- `docs/215-election-lifecycle-evidence-map.md`
- `docs/227-refactor-and-growth-protocol.md`
- `docs/229-experiment-to-spec-promotion-protocol.md`
- `docs/242-audience-reading-paths-and-what-to-ignore.md`
- `docs/262-jurisdictional-policy-surface-registry.md`
- `docs/292-polling-place-directory-and-change-notices-as-evidence-surfaces.md` through `docs/328-college-student-voting-campus-residence-and-home-address-choice-as-evidence-surfaces.md`
- `docs/335-guardianship-conservatorship-and-court-determined-voting-capacity-as-evidence-surfaces.md`
- `docs/336-tribal-community-voting-tribal-ids-reservation-addresses-and-tribal-government-ballot-access-paths-as-evidence-surfaces.md`
- `docs/337-disaster-displacement-evacuation-and-temporary-relocation-voting-paths-as-evidence-surfaces.md`
- `docs/338-new-citizen-and-newly-naturalized-voter-registration-timing-proof-and-post-ceremony-fallback-paths-as-evidence-surfaces.md`
- `docs/339-signature-alternatives-mark-witness-stamp-and-accessible-signature-cure-paths-as-evidence-surfaces.md`
- `docs/340-youth-voter-preregistration-activation-timing-and-primary-before-general-eligibility-as-evidence-surfaces.md`
- `docs/341-voter-assistance-person-of-choice-interpreter-rules-and-restricted-helper-boundaries-as-evidence-surfaces.md`
- `docs/342-ballot-return-by-another-person-designated-agent-or-bearer-rules-and-ballot-handoff-boundaries-as-evidence-surfaces.md`
- `docs/343-challenged-voter-oaths-affidavits-witnesses-and-fail-safe-ballot-rights-as-evidence-surfaces.md`
- `artifacts/tables/voter-facing-public-answer-surfaces.csv`
- `docs/329-voter-facing-public-answer-surface-registry-and-duplicate-firewall.md`
- `docs/330-voter-facing-public-answer-surface-triplet-coherence-and-orphan-control.md`
- `docs/331-special-case-voter-facing-surfaces-subfamily-and-authority-anchor-minimums.md`
- `docs/332-special-case-voter-facing-surface-nonoverlap-declarations-and-misrouting-firewall.md`
- `docs/333-special-case-voter-facing-surface-safe-fallback-and-escalation-boundaries.md`
- `docs/334-special-case-voter-facing-surface-temporal-volatility-freshness-and-no-cross-jurisdiction-inference.md`
- `docs/355-special-case-voter-facing-surface-control-stack-reference-closure-and-navigation-firewall.md`
- `docs/366-official-voter-information-broadcast-alerts-social-posts-and-linkback-discipline.md`
- `docs/369-official-voter-information-videos-livestreams-and-clip-context-discipline.md`
- `docs/370-official-voter-information-emails-newsletters-reminders-and-forward-context-discipline.md`
- `docs/371-official-voter-information-community-partner-distribution-co-branding-and-relay-boundary-discipline.md`
- `docs/372-official-voter-information-site-signage-wayfinding-and-stale-posting-removal-discipline.md`
- `docs/373-official-voter-information-forms-applications-affidavits-and-version-acceptance-discipline.md`
- `docs/374-official-voter-information-routers-state-selectors-and-decision-path-trace-discipline.md`
- `docs/375-official-voter-information-site-search-autocomplete-and-result-ranking-discipline.md`
- `docs/376-official-voter-information-map-embeds-geolocation-and-directions-discipline.md`
- `docs/377-official-voter-information-language-selectors-locale-fallback-and-machine-translation-boundary-discipline.md`
- `docs/378-official-voter-information-document-downloads-embedded-viewers-and-file-delivery-boundary-discipline.md`
- `docs/379-official-voter-information-redirects-expired-pages-and-stale-link-recovery-discipline.md`
- `docs/380-official-voter-information-site-alerts-banners-and-interstitial-discipline.md`
- `docs/381-official-voter-information-qr-codes-short-urls-and-printed-to-digital-handoff-discipline.md`
- `docs/382-official-voter-information-search-result-presentation-title-links-snippets-and-canonical-discipline.md`
- `docs/383-official-voter-information-social-profiles-bio-links-and-pinned-post-discipline.md`
- `docs/384-official-voter-information-mobile-apps-app-store-listings-and-download-boundary-discipline.md`
- `docs/385-official-voter-information-platform-place-cards-office-listings-and-hours-contact-discipline.md`
- `docs/386-official-voter-information-off-platform-ai-answer-surfaces-citation-handoff-and-authority-boundary-discipline.md`
- `docs/387-official-voter-information-voice-search-voice-assistant-answers-and-spoken-handoff-discipline.md`
- `docs/388-official-voter-information-shared-link-previews-unfurls-and-preview-cache-discipline.md`
- `docs/389-official-voter-information-calendar-subscriptions-ics-downloads-and-reminder-handoff-discipline.md`
- `docs/390-official-voter-information-public-apis-data-feeds-and-widget-consumption-discipline.md`
- `docs/391-official-voter-information-crawlability-indexability-canonical-discovery-and-sitemap-discipline.md`
- `docs/392-official-voter-information-organization-structured-data-site-names-favicons-and-entity-identity-discipline.md`
- `docs/393-official-voter-information-breadcrumb-faq-and-search-appearance-structured-data-discipline.md`
- `docs/394-official-voter-information-search-removals-noindex-and-recrawl-discipline.md`
- `docs/395-official-voter-information-snippet-preview-controls-and-ai-excerpt-discipline.md`
- `docs/396-official-voter-information-publication-dates-last-updated-cues-and-byline-discipline.md`
- `docs/397-official-voter-information-alternate-language-discovery-hreflang-x-default-and-locale-adaptive-crawl-discipline.md`
- `docs/398-official-voter-information-site-moves-domain-migrations-gov-transitions-and-hostname-continuity-discipline.md`
- `docs/399-official-voter-information-search-console-property-coverage-ownership-continuity-and-emergency-control-plane-discipline.md`
- `docs/400-official-voter-information-search-performance-monitoring-query-loss-detection-and-anomaly-triage-discipline.md`
- `docs/401-official-voter-information-url-inspection-live-test-and-page-state-diagnosis-discipline.md`
- `docs/402-official-voter-information-page-performance-core-web-vitals-and-mobile-readiness-discipline.md`
- `docs/403-official-voter-information-progressive-enhancement-javascript-dependency-and-degraded-client-recovery-discipline.md`
- `docs/404-official-voter-information-cache-freshness-service-worker-updates-and-stale-answer-eviction-discipline.md`
- `docs/405-official-voter-information-anti-bot-challenges-captcha-waf-and-human-verification-fail-open-discipline.md`
- `docs/406-official-voter-information-request-context-variance-personalization-and-experiment-boundary-discipline.md`
- `docs/407-official-voter-information-secure-transport-browser-security-warnings-and-unsafe-page-recovery-discipline.md`
- `docs/408-official-voter-information-temporary-overload-queue-pages-rate-limiting-and-degraded-answer-continuity-discipline.md`
- `docs/409-official-voter-information-public-read-access-sign-in-boundaries-and-session-expiry-recovery-discipline.md`
- `docs/410-official-voter-information-third-party-dependencies-embeds-and-external-origin-fail-open-discipline.md`
- `docs/411-official-voter-information-cookie-consent-walls-privacy-overlays-and-first-load-answer-lane-visibility-discipline.md`
- `docs/412-official-voter-information-browser-permission-prompts-geolocation-notifications-and-device-capability-fail-open-discipline.md`
- `docs/413-official-voter-information-external-destinations-non-federal-handoffs-and-new-context-fail-open-discipline.md`
- `docs/414-official-voter-information-embedded-browsers-webviews-and-constrained-container-fail-open-discipline.md`
- `docs/415-official-voter-information-low-connectivity-intermittent-network-and-reduced-data-fail-open-discipline.md`
- `docs/416-official-voter-information-reflow-text-scaling-and-small-viewport-fail-open-discipline.md`
- `docs/417-official-voter-information-keyboard-navigation-focus-visibility-and-logical-order-fail-open-discipline.md`
- `docs/418-official-voter-information-screen-reader-semantics-landmarks-labels-and-live-update-fail-open-discipline.md`
- `docs/419-official-voter-information-color-contrast-non-color-cues-and-meaningful-state-fail-open-discipline.md`
- `docs/420-official-voter-information-motion-animation-auto-advancing-content-and-interruption-safe-fail-open-discipline.md`
- `docs/421-official-voter-information-touch-target-size-hover-revealed-content-and-pointer-operability-fail-open-discipline.md`
- `docs/422-official-voter-information-field-entry-hints-autofill-and-input-error-recovery-fail-open-discipline.md`
- `docs/423-official-voter-information-date-entry-calendar-widgets-and-typed-date-fallback-fail-open-discipline.md`
- `docs/424-official-voter-information-address-entry-autocomplete-suggestions-unit-details-and-manual-override-fail-open-discipline.md`
- `docs/425-official-voter-information-name-entry-personal-name-structure-and-match-recovery-fail-open-discipline.md`
- `docs/426-official-voter-information-fixed-format-identifier-entry-leading-zeros-and-exact-string-fail-open-discipline.md`
- `docs/427-official-voter-information-phone-email-entry-delivery-targets-and-verification-code-fail-open-discipline.md`
- `docs/428-official-voter-information-document-upload-file-types-size-limits-camera-capture-and-manual-fallback-fail-open-discipline.md`
- `docs/429-official-voter-information-multi-step-progress-review-and-state-preservation-fail-open-discipline.md`
- `docs/430-official-voter-information-submission-confirmation-reference-numbers-record-keeping-and-safe-retry-fail-open-discipline.md`
- `docs/431-official-voter-information-inactivity-timeouts-advance-warnings-and-lossless-expiry-recovery-fail-open-discipline.md`
- `docs/432-official-voter-information-long-running-processing-wait-states-and-in-session-pending-response-fail-open-discipline.md`
- `docs/433-official-voter-information-post-submit-pending-review-status-follow-up-and-escalation-fail-open-discipline.md`
- `docs/434-official-voter-information-unsuccessful-outcomes-rejection-reasons-and-reapply-or-help-fail-open-discipline.md`
- `docs/435-official-voter-information-service-unavailable-maintenance-windows-and-degraded-mode-fail-open-discipline.md`
- `docs/436-official-voter-information-sign-out-shared-device-and-local-data-clearing-fail-open-discipline.md`
- `docs/437-official-voter-information-portable-records-print-save-to-pdf-and-off-screen-fidelity-fail-open-discipline.md`
- `docs/438-official-voter-information-bookmarking-shared-link-revisit-continuity-and-share-safe-url-discipline.md`
- `docs/439-official-voter-information-history-restore-hidden-return-and-parallel-tab-state-freshness-discipline.md`
- `docs/440-official-voter-information-reader-mode-simplified-view-and-main-content-extraction-discipline.md`
- `docs/441-official-voter-information-page-titles-browser-tab-identity-and-history-entry-disambiguation-discipline.md`
- `docs/442-official-voter-information-section-anchors-in-page-navigation-and-fragment-target-continuity-discipline.md`
- `docs/443-official-voter-information-accordions-disclosures-and-collapsed-answer-reveal-discipline.md`
- `docs/444-official-voter-information-sticky-headers-fixed-chrome-and-unobscured-target-landing-discipline.md`
- `docs/445-official-voter-information-tabs-active-panel-continuity-and-hidden-panel-findability-discipline.md`
- `docs/446-official-voter-information-data-tables-responsive-overflow-sort-state-and-row-findability-discipline.md`
- `docs/447-official-voter-information-cards-collections-and-answer-tile-disambiguation-discipline.md`
- `docs/448-official-voter-information-source-order-visual-order-and-focus-order-continuity-discipline.md`
- `docs/449-official-voter-information-bypass-blocks-skip-links-and-first-answer-reachability-discipline.md`
- `docs/450-official-voter-information-pagination-current-page-indication-and-result-set-continuity-discipline.md`
- `docs/451-official-voter-information-load-more-infinite-scroll-and-result-refindability-discipline.md`
- `docs/452-official-voter-information-filters-facets-active-scope-and-subset-reset-discipline.md`
- `docs/453-official-voter-information-comboboxes-suggestion-popups-and-explicit-commit-discipline.md`
- `docs/454-official-voter-information-breadcrumb-trails-current-location-legibility-and-parent-path-continuity-discipline.md`
- `docs/455-official-voter-information-zero-results-empty-states-and-recovery-route-continuity-discipline.md`
- `docs/456-official-voter-information-sort-controls-default-order-and-order-change-legibility-discipline.md`
- `docs/457-official-voter-information-horizontal-rails-carousels-and-offscreen-answer-discoverability-discipline.md`
- `docs/458-official-voter-information-view-switchers-list-map-calendar-toggles-and-cross-view-continuity-discipline.md`
- `docs/459-official-voter-information-answer-overlays-dialogs-drawers-and-route-continuity-discipline.md`
- `docs/460-official-voter-information-navigation-menus-fly-outs-and-destination-continuity-discipline.md`
- `docs/461-official-voter-information-buttons-links-and-action-destination-truthfulness-discipline.md`
- `docs/462-official-voter-information-disabled-controls-unavailable-actions-and-unlock-path-legibility-discipline.md`
- `docs/463-official-voter-information-tooltips-popovers-hover-help-and-essential-answer-visibility-discipline.md`
- `docs/464-official-voter-information-transient-toasts-snackbars-status-messages-and-durable-outcome-visibility-discipline.md`
- `docs/465-official-voter-information-browser-history-entry-mutation-push-replace-semantics-and-back-stack-truthfulness-discipline.md`
- `docs/466-official-voter-information-missing-fragment-targets-unresolved-section-anchors-and-fail-open-refinding-discipline.md`
- `docs/467-official-voter-information-mutable-live-pages-point-in-time-citation-snapshots-and-current-vs-citation-head-discipline.md`
- `docs/468-official-voter-information-citation-head-registers-unique-head-warnings-and-public-handoff-discipline.md`
- `docs/469-official-voter-information-local-only-saves-queued-background-sync-and-office-acknowledged-state-truthfulness-discipline.md`
- `docs/470-official-voter-information-mid-flow-version-drift-expected-head-review-and-resumed-state-honesty-discipline.md`
- `docs/471-official-voter-information-copy-share-controls-clipboard-write-truthfulness-and-native-share-handoff-discipline.md`
- `docs/472-official-voter-information-installable-web-apps-home-screen-launches-and-standalone-identity-discipline.md`
- `docs/473-official-voter-information-text-fragment-deep-links-quoted-text-highlights-and-excerpt-anchor-truthfulness-discipline.md`
- `docs/474-official-voter-information-browser-find-in-page-hidden-until-found-and-first-match-truthfulness-discipline.md`
- `docs/475-official-voter-information-web-push-notifications-subscription-lifecycle-and-stale-notification-withdrawal-discipline.md`
- `docs/476-official-voter-information-leave-page-warnings-unsaved-changes-dialogs-and-loss-prevention-truthfulness-discipline.md`
- `docs/477-official-voter-information-post-submit-redirects-browser-repost-prompts-and-refresh-safe-confirmation-discipline.md`
- `docs/478-official-voter-information-text-assistance-layers-autocorrect-autocapitalize-spellcheck-and-ime-composition-discipline.md`
- `docs/479-official-voter-information-speculative-loading-prefetch-prerender-and-pre-activation-freshness-discipline.md`
- `docs/480-official-voter-information-private-browsing-ephemeral-storage-and-storage-denied-fallback-discipline.md`
- `docs/481-official-voter-information-browser-native-constraint-validation-validation-messages-and-durable-error-recovery-discipline.md`
- `docs/482-official-voter-information-virtual-keyboards-visual-viewport-shrink-and-obscured-control-recovery-discipline.md`
- `docs/483-official-voter-information-user-overridden-text-spacing-clipped-or-overlapped-content-and-readability-recovery-discipline.md`
- `docs/484-official-voter-information-forced-colors-high-contrast-system-palettes-and-user-color-override-discipline.md`
- `docs/485-official-voter-information-light-dark-theme-variants-browser-chrome-and-color-scheme-coherence-discipline.md`
- `docs/486-official-voter-information-browser-integrated-page-summaries-page-context-ai-sidebars-and-authority-boundary-discipline.md`
- `docs/487-official-voter-information-browser-integrated-page-translation-selected-text-translation-and-authority-boundary-discipline.md`
- `docs/488-official-voter-information-browser-integrated-ocr-image-text-extraction-scanned-pdf-text-layers-and-transcription-boundary-discipline.md`
- `docs/489-official-voter-information-browser-integrated-read-aloud-listen-to-page-and-page-audio-narration-boundary-discipline.md`
- `docs/490-official-voter-information-browser-managed-reading-lists-offline-saved-pages-and-web-archive-authority-boundary-discipline.md`
- `docs/491-official-voter-information-browser-integrated-image-descriptions-unlabeled-image-inference-and-authority-boundary-discipline.md`
- `docs/492-official-voter-information-browser-integrated-live-captions-subtitle-translation-and-transcript-boundary-discipline.md`
- `docs/493-official-voter-information-platform-transcript-panes-searchable-transcripts-and-clip-jump-authority-boundary-discipline.md`
- `docs/494-official-voter-information-platform-chapter-markers-key-moments-and-shareable-chapter-list-authority-boundary-discipline.md`
- `docs/495-official-voter-information-platform-clips-highlights-and-shareable-segment-authority-boundary-discipline.md`
- `docs/496-official-voter-information-platform-autoplay-end-screens-cards-and-play-next-authority-boundary-discipline.md`
- `docs/497-official-voter-information-platform-watch-later-saved-playlists-offline-downloads-and-smart-download-authority-boundary-discipline.md`
- `docs/498-official-voter-information-platform-follows-subscriptions-and-live-event-reminder-authority-boundary-discipline.md`
- `docs/499-official-voter-information-platform-ai-video-summaries-ask-this-video-and-answer-module-authority-boundary-discipline.md`
- `docs/500-official-voter-information-platform-comments-live-chat-qa-polls-and-reactions-authority-boundary-discipline.md`
- `docs/501-official-voter-information-platform-alternate-audio-tracks-dubbed-audio-and-audio-description-authority-boundary-discipline.md`
- `docs/502-official-voter-information-platform-popout-playback-picture-in-picture-and-background-play-authority-boundary-discipline.md`
- `docs/503-official-voter-information-platform-remote-playback-casting-and-second-screen-authority-boundary-discipline.md`
- `docs/504-official-voter-information-platform-fullscreen-theater-mode-and-immersive-player-authority-boundary-discipline.md`
- `docs/505-official-voter-information-platform-playback-speed-scrubbing-skipping-and-seek-authority-boundary-discipline.md`
- `docs/506-official-voter-information-platform-watch-history-continue-watching-recent-videos-and-resume-state-authority-boundary-discipline.md`
- `docs/507-official-voter-information-platform-channel-home-featured-videos-playlists-and-collection-pages-authority-boundary-discipline.md`
- `docs/508-official-voter-information-platform-upcoming-event-pages-premiere-watch-pages-and-pre-live-countdown-authority-boundary-discipline.md`
- `docs/509-official-voter-information-platform-post-live-archive-replay-and-ended-event-surface-authority-boundary-discipline.md`
- `docs/510-official-voter-information-platform-search-results-homepage-recommendations-and-browse-feed-authority-boundary-discipline.md`
- `docs/511-official-voter-information-platform-share-panels-copy-links-timestamp-links-and-embed-export-authority-boundary-discipline.md`
- `docs/512-official-voter-information-platform-unavailable-private-age-gated-region-blocked-and-playback-restricted-surface-authority-boundary-discipline.md`
- `docs/513-official-voter-information-platform-playback-quality-adaptive-bitrate-resolution-selectors-and-data-saver-authority-boundary-discipline.md`
- `docs/514-official-voter-information-platform-titles-descriptions-thumbnails-posters-and-metadata-wrapper-authority-boundary-discipline.md`
- `docs/515-official-voter-information-platform-processing-pending-optimization-and-not-yet-fully-ready-media-surface-authority-boundary-discipline.md`
- `docs/516-official-voter-information-platform-live-edge-behind-live-state-latency-and-watch-live-recovery-authority-boundary-discipline.md`
- `docs/517-official-voter-information-platform-simulcast-mirrors-multi-route-live-events-and-redirect-chain-authority-boundary-discipline.md`
- `docs/518-official-voter-information-platform-registration-forms-invite-only-join-links-and-audience-gated-media-authority-boundary-discipline.md`
- `docs/519-official-voter-information-platform-view-counts-concurrent-viewers-likes-and-audience-metrics-wrapper-authority-boundary-discipline.md`
- `docs/520-official-voter-information-platform-channel-bylines-profile-names-handles-verification-badges-and-source-identity-wrapper-authority-boundary-discipline.md`
- `docs/521-official-voter-information-platform-information-panels-context-boxes-disclosure-labels-and-policy-wrapper-authority-boundary-discipline.md`
- `docs/522-official-voter-information-platform-event-theming-branded-player-chrome-and-live-status-label-authority-boundary-discipline.md`
- `docs/523-official-voter-information-platform-media-boundary-quickmap-and-duplicate-firewall.md`
- `docs/583-official-voter-information-platform-media-stacked-authenticity-cues-identity-context-provenance-ordering-and-non-collapse-firewall.md`
- `docs/584-official-voter-information-platform-media-provenance-signals-content-credentials-and-non-substitutive-authenticity-discipline.md`
- `docs/585-official-voter-information-platform-media-authenticity-cue-transport-cross-route-divergence-and-absence-non-inference-firewall.md`
- `docs/586-official-voter-information-platform-media-authenticity-cue-tension-aspect-separation-and-non-cancellation-firewall.md`
- `docs/587-official-voter-information-platform-media-authenticity-cue-lifecycle-timing-drift-and-non-retroactive-inference-firewall.md`
- `docs/588-official-voter-information-platform-media-authenticity-cue-attachment-points-scope-boundaries-and-non-inheritance-firewall.md`
- `docs/589-official-voter-information-platform-media-authenticity-cue-inspection-gates-expanded-details-and-non-ambient-visibility-firewall.md`
- `docs/590-official-voter-information-platform-media-authenticity-cue-viewer-state-variance-eligibility-conditions-and-non-universality-firewall.md`
- `docs/591-official-voter-information-platform-media-authenticity-cue-observation-assembly-cross-state-composites-and-no-faux-single-state-firewall.md`
- `docs/592-official-voter-information-platform-media-authenticity-cue-preview-shells-open-target-separation-and-noninheritance-firewall.md`
- `docs/593-official-voter-information-platform-media-authenticity-cue-player-state-occlusion-reduced-context-suppression-and-non-absence-inference-firewall.md`
- `docs/594-official-voter-information-platform-media-authenticity-cue-observation-windows-clipped-captures-and-non-totality-firewall.md`
- `docs/595-official-voter-information-platform-media-authenticity-cue-text-extracts-transcript-caption-ocr-derivatives-and-non-carried-cue-firewall.md`
- `docs/596-official-voter-information-platform-media-authenticity-cue-audio-extracts-track-downloads-and-detached-spoken-derivatives-and-non-carried-cue-firewall.md`
- `docs/597-official-voter-information-platform-media-authenticity-cue-still-image-extracts-frame-grabs-poster-exports-and-non-carried-cue-firewall.md`
- `docs/598-official-voter-information-platform-media-authenticity-cue-metadata-extracts-title-description-chapter-list-derivatives-and-non-carried-cue-firewall.md`
- `docs/599-official-voter-information-platform-media-authenticity-cue-locator-derivatives-shared-links-timestamp-links-and-non-carried-cue-firewall.md`
- `docs/600-official-voter-information-platform-media-authenticity-cue-detached-derivative-family-quickmap-mixed-packets-and-anti-fragmentation-firewall.md`
- `docs/524-official-voter-information-platform-media-route-state-lexicon-badge-normalization-and-capture-order-discipline.md
- `docs/525-official-voter-information-platform-media-mutation-classes-first-contact-evidence-pack-and-snapshot-minimization-discipline.md`
- `docs/526-official-voter-information-platform-media-re-anchor-ladder-canonical-recovery-targets-and-wrapper-exit-discipline.md`
- `docs/527-official-voter-information-platform-media-control-tuple-one-line-normalization-contract-and-packet-comparison-discipline.md`
- `docs/528-official-voter-information-platform-media-same-object-transition-chains-packet-stitching-and-resnapshot-threshold-discipline.md`
- `docs/529-official-voter-information-platform-media-chain-heads-current-control-and-closeout-discipline.md`
- `docs/530-official-voter-information-platform-media-chain-citations-head-first-reference-and-historical-leg-scoping-discipline.md`
- `docs/531-official-voter-information-platform-media-head-supersession-notes-trigger-codes-and-demotion-discipline.md`
- `docs/532-official-voter-information-platform-media-head-volatility-labels-provisional-current-notes-and-review-window-discipline.md`
- `docs/533-official-voter-information-platform-media-no-public-head-states-headless-chain-notes-and-fallback-anchor-discipline.md`
- `docs/534-official-voter-information-platform-media-co-current-aliases-sibling-routes-and-canonical-head-with-alias-discipline.md`
- `docs/535-official-voter-information-platform-media-audience-scoped-current-aliases-scope-labels-and-public-default-retention-discipline.md`
- `docs/536-official-voter-information-platform-media-route-scope-transitions-widening-narrowing-and-alias-rebucketing-discipline.md`
- `docs/537-official-voter-information-platform-media-capability-bearing-current-aliases-link-secret-routes-and-redaction-default-discipline.md`
- `docs/538-official-voter-information-platform-media-player-host-render-aliases-direct-embed-routes-and-watch-page-default-discipline.md`
- `docs/539-official-voter-information-platform-media-entrypoint-offset-aliases-current-time-start-at-routes-and-full-object-default-discipline.md`
- `docs/540-official-voter-information-platform-media-notification-carriers-reminder-pointers-and-route-carrier-separation-discipline.md`
- `docs/541-official-voter-information-platform-media-carrier-target-drift-late-delivery-retargeting-and-stale-pointer-non-supersession-discipline.md`
- `docs/542-official-voter-information-platform-media-app-launch-aliases-open-in-app-deep-links-and-browser-default-retention-discipline.md`
- `docs/543-official-voter-information-platform-media-remembered-resume-aliases-history-reentry-and-full-object-default-discipline.md`
- `docs/544-official-voter-information-platform-media-in-player-moment-jump-aliases-transcript-chapter-picks-and-route-stability-retention-discipline.md`
- `docs/545-official-voter-information-platform-media-text-track-selection-states-caption-subtitle-language-picks-and-head-default-retention-discipline.md`
- `docs/546-official-voter-information-platform-media-player-view-state-aliases-detached-immersive-containers-and-source-page-default-retention-discipline.md`
- `docs/547-official-voter-information-platform-media-rendition-selection-states-adaptive-quality-picks-and-head-default-retention-discipline.md`
- `docs/548-official-voter-information-platform-media-playback-rate-selection-states-accelerated-slowed-and-scan-posture-head-default-retention-discipline.md`
- `docs/549-official-voter-information-platform-media-audio-output-selection-states-mute-volume-posture-and-head-default-retention-discipline.md`
- `docs/550-official-voter-information-platform-media-remote-playback-target-states-cast-controller-splits-and-sender-default-retention-discipline.md`
- `docs/551-official-voter-information-platform-media-successor-object-handoffs-autoplay-queue-progression-and-head-noninheritance-discipline.md`
- `docs/552-official-voter-information-platform-media-spoken-audio-track-selection-states-dubbed-language-picks-and-head-default-retention-discipline.md`
- `docs/556-official-voter-information-platform-media-loop-repeat-retention-states-same-object-replay-cycling-and-head-default-retention-discipline.md`
- `docs/557-official-voter-information-platform-media-transcript-pane-states-search-focus-and-head-default-retention-discipline.md`
- `docs/558-official-voter-information-platform-media-interaction-pane-states-social-tab-focus-and-head-default-retention-discipline.md`
- `docs/559-official-voter-information-platform-media-live-position-states-behind-live-recovery-and-head-default-retention-discipline.md`
- `docs/560-official-voter-information-platform-media-next-item-queue-states-up-next-foreground-and-head-default-retention-discipline.md`
- `docs/561-official-voter-information-platform-media-derivative-readiness-states-processing-lag-and-head-default-retention-discipline.md`
- `docs/553-official-voter-information-platform-media-saved-shelf-reentry-aliases-watch-later-playlist-offline-reopen-and-head-default-retention-discipline.md`

## Why this exists (bounded)

Current official guidance already treats voter information as a family of authoritative answer surfaces rather than one generic webpage. EAC’s current **Voter FAQs** page says election administration is highly decentralized and that the best practical source of registration and voting information is the local elections office. EAC’s current **Register and Vote in Your State** tool routes voters to state election office sites, local office directories, registration/update/status information, and ballot-casting options. EAC’s current **Best Practices: FAQs for Election Officials** page explicitly encourages election officials to build website FAQ surfaces and promote them as a trusted source of information. NASS’s current **Can I Vote** service and **#TrustedInfo2026** initiative reinforce the same posture by sending voters to state election websites and election-official materials instead of pretending one national answer page can safely compress every jurisdiction’s rules. (xref: `eac_voter_faqs_page`; xref: `eac_register_and_vote_in_your_state_page`; xref: `eac_best_practices_faqs_election_officials_page`; xref: `nass_can_i_vote_page`; xref: `nass_trustedinfo_2026_page`)

That is exactly why this archive should treat these surfaces as a **family**. The decentralized reality does **not** justify a giant undifferentiated FAQ chapter. It justifies a small set of bounded surface types with explicit supersession, parity, accessibility, and help-path rules.

## Family boundary

A voter-facing public-answer surface belongs in this family when **all** of the following are true:

- the question is one a voter, helper, journalist, or poll worker can reasonably ask in plain language;
- the answer changes **what action the voter should take next**;
- the answer is expected to appear on official public channels (webpage, interactive router, PDF, hotline script, directory, sample ballot page, signed notice, print artifact, site signage, partner-distributed official material, fillable/downloadable form packet, or status surface);
- silent edits or split-view delivery would matter later in a dispute;
- the answer can be represented by a **small payload + explicit help path + supersession chain**;
- the archive can support it with a **doc + template + checklist** rather than a jurisdiction-by-jurisdiction law treatise.

A proposed surface does **not** belong in this family if it is mainly:

- a general civics explainer,
- an internal operations runbook,
- a fifty-state legal digest,
- a generic “contact us” page with no action-changing semantics,
- a duplicate of an existing surface with only wording changes, or
- a question that should be handled as a cross-cutting correction/advisory on an existing surface.

## The family, grouped by the voter question it answers

The current family has four practical buckets.

### A. Locate the right place, channel, or schedule

These surfaces answer **where / when / which channel** questions.

- `292` — polling-place directory and change notices
- `297` — early-voting site hours and change notices
- `298` — ballot-drop-box directories, hours, and change notices
- `299` — polling-place live status, queue advisories, and reroute notices
- `305` — election-office contact directories, office hours, and change notices
- `308` — election calendars, key dates, and change notices
- `320` — vote-center, countywide-voting, and assigned-location rules

Canonical user questions:
- Where do I go?
- When is it open?
- Is the route still valid right now?
- Which office is authoritative if the answer changed?
- Which date or deadline now controls what I can still do?
- Can I vote at any county site, any assigned center, or only one designated location for this phase?

### B. Confirm eligibility, prerequisites, or accommodations

These surfaces answer **can I do this / what do I need / what support exists** questions.

- `294` — voter-registration-status lookups and correction notices
- `315` — precinct, district, and jurisdiction lookups and assignment change notices
- `300` — voter-identification requirements, alternatives, and change notices
- `301` — accessible voting accommodations, curbside, and change notices
- `302` — language assistance, translated materials, and change notices
- `303` — same-day registration locations, proof requirements, and change notices
- `309` — primary-election participation, party affiliation, and change notices
- `312` — runoff and special-election participation, district scope, and change notices
- `318` — voter-registration updates, address/name/party changes, and move-close-to-election notices
- `319` — inactive/removed registration states and reactivation notices
- `323` — felony-conviction voting eligibility, restoration, and re-registration help
- `324` — no-fixed-address, homelessness, residence, and ballot-delivery help
- `325` — confidential voter registration, address confidentiality, and protected ballot paths
- `326` — in-custody eligible voting, jail/detention, and civil-commitment ballot access
- `327` — long-term care, assisted living, residential facility, and facility-assisted voting
- `328` — college-student voting, campus residence, and home-address choice
- `335` — guardianship, conservatorship, and court-determined voting capacity
- `336` — tribal-community voting, tribal IDs, reservation addresses, and tribal-government ballot-access paths
- `337` — disaster displacement, evacuation, and temporary-relocation voting paths
- `338` — new-citizen and newly naturalized voter registration timing, proof, and post-ceremony fallback paths
- `339` — signature alternatives, mark/witness, stamp, and accessible signature-cure paths
- `340` — youth-voter preregistration, activation timing, and primary-before-general eligibility
- `341` — voter assistance by person of choice, interpreter rules, and restricted-helper boundaries

For the highest-risk special-case cluster — the rows tagged `special_case_high_risk` in `artifacts/tables/voter-facing-public-answer-surfaces.csv` (currently `317–328` and `335–343`) — maintainers should treat `docs/331-*`, `docs/332-*`, `docs/333-*`, `docs/334-*`, and the canonical current control-stack map in `docs/355-*` as the companion firewall set. In substance that means a surface should be well-anchored in repeated official-public sources, carry direct jurisdiction-specific governing examples rather than only national routing material, stay explicit about adjacent numbered surfaces and `305` / `307` lane changes, stay explicit that the rule is jurisdiction-specific and unsafe to port by analogy, make current-official routing and superseding-notice discipline visible, stop on unresolved official conflict, expose a concrete official help/contact path, identify the responsible office, name an official secure channel, say how to verify operability right now, keep the latest triplet/checklist/payload backstops synchronized, and keep overview docs inheriting the current stack from one canonical map instead of freezing stale local tail lists.

Canonical user questions:
- Am I registered or do I need to fix something?
- Which precinct, districts, or local election jurisdiction apply to me right now?
- What do I need to bring?
- What accessible or language-support path exists for me?
- Can I still register or update on site?
- Can I participate in this primary, and under which ballot-eligibility semantics?
- Is there a runoff or special election for my district, and do any carry-forward rules control my participation?
- I moved or changed my name, address, or party affiliation; how do I update my record, by what deadline, and what late-change fallback applies?
- My record says inactive or removed; can I still vote, and what official reactivation or restoration path applies now?
- Can I vote with this conviction right now, and if not, what restoration or re-registration path controls?
- I do not have a fixed address; what can I use as residence, where will my ballot go, and what fallback exists if mail delivery fails?
- I need to vote without exposing my address; what confidential-registration, substitute-address, or protected ballot path applies?
- I am in jail, detention, or civil commitment but may still be eligible; what address, ballot-request path, and facility handoff control how I vote from here?
- I live in a nursing home, assisted-living facility, treatment center, veterans home, group home, shelter, or similar residential facility; what proof, assistance team, or supervised/agent ballot path applies where I live?
- I am a college student; should I vote from campus or from home, does student housing count as residence, what campus proof or mailing rule applies, and when should I use absentee voting from the other address instead?
- I am under guardianship or conservatorship, or someone says a court found me unable to vote; can I still register or vote, who decides, and what help path applies?
- I have been evacuated or temporarily displaced by a disaster; should I keep my home address, use a temporary mailing address, and what ballot fallback controls if delivery or site access is disrupted?
- I just became a U.S. citizen or will naturalize close to the election; when may I register, what proof or in-person rule applies, and what fallback exists if the ordinary online or deadline path does not fit?

### C. Understand ballot content or navigate the ballot path

These surfaces answer **what is on my ballot / what changed in a race / what does this measure mean / how do I get or return the ballot / what happened to it** questions.

- `293` — ballot-style lookups and sample ballots
- `313` — ballot-measure explanatory texts, official voter guides, and voters’ pamphlets
- `314` — candidate withdrawal, death, disqualification, and replacement notices
- `304` — mail-ballot request methods, deadlines, and change notices
- `317` — mail-ballot replacement, spoilage, nonreceipt, and surrender-fallback
- `322` — emergency absentee ballots, hospitalized/incapacitated voters, and late-emergency delivery paths
- `311` — mail-ballot return instructions, envelope requirements, and deadline semantics
- `342` — ballot return by another person, designated-agent or bearer rules, and ballot-handoff boundaries
- `343` — challenged-voter oaths, affidavits, witnesses, and fail-safe ballot rights
- `295` — mail-ballot status lookups and cure notices
- `296` — provisional-ballot status lookups and reason notices
- `306` — military and overseas voting paths, FPCA/FWAB, and change notices
- `321` — provisional-ballot issuance reasons, partial-count rules, and voter instructions
- `316` — voter history and participation-record lookups and correction notices

Canonical user questions:
- What is on my ballot?
- What does this measure mean, where is the authoritative explanatory guide or pamphlet, and which version controlled that explanation?
- Did the candidate field for this race change, does stale material still exist, and which official notice now controls?
- How do I request or receive the right ballot path?
- My ballot is lost, spoiled, damaged, or missing a usable envelope; how do I get a replacement or switch to another lawful voting path?
- A late emergency or hospitalization now prevents ordinary voting; which emergency ballot, representative-delivery, or clerk-delivery path still remains lawful?
- How do I return this ballot correctly, and what deadline basis controls?
- May someone else pick up, carry, drop off, or return ballot materials for me, and what authorization or agent/bearer rule controls that handoff?
- Someone is challenging my right to vote right now; what oath, affidavit, witness, or fail-safe ballot path controls?
- Why am I being asked to vote provisionally, what does that mean right now, and what immediate instructions or alternate-location choices control that decision?
- What happened to my returned ballot?
- If my ballot is provisional, what was the reason and what can I do now?
- Does the official participation record now show that I voted in this election, and what should I do if it does not?
- If I am military or overseas, which specialized federal/jurisdictional path applies?

### D. Report problems and escalate safely

This surface answers **the ordinary answer path failed; where do I go now** questions.

- `307` — voting-issue reporting, civil-rights escalation, and change notices

Canonical user questions:
- Who should I contact for ordinary voting help?
- Which lane is the formal complaint path?
- Which lane is civil-rights escalation?
- Which lane is emergency safety / intimidation / law-enforcement routing?

## Automated assistants and site-search layers are delivery layers, not a fifth family bucket

A public search assistant, FAQ bot, chatbot, LLM helper, or on-site search/autocomplete surface can sit **in front of** the existing voter-facing answer surfaces, but it does not create a new canonical voter-question bucket by itself.

If a jurisdiction uses one of these layers, the controlling question is still one of the underlying surfaces already modeled here: where to vote (`292`, `297`, `298`, `299`), which office controls (`305`), how to escalate (`307`), how to request/return/track a ballot (`304`, `311`, `295`, `296`, `317`, `321`, `322`), or which special-case eligibility/accommodation path applies (`323–343`).

So the safe maintenance rule is simple: **promote new canonical surfaces only for distinct voter questions, not for new delivery modalities.** The following docs govern those delivery layers without creating a fifth family bucket:

- `docs/363-*` — automated assistants and chat helpers, including first-contact warning labels, approved-source hierarchies, wizard-handoff rules, operating-bounds disclosure, official-directory/discovery binding, explicit lifecycle-state and dependency honesty, and feedback-fed review.
- `docs/364-*` — official voter-help hotlines and call-center script packets.
- `docs/365-*` — official FAQ/help pages and knowledge-base entries.
- `docs/366-*` — short-form alerts, social posts, texts, and app notifications.
- `docs/367-*` — press releases, media advisories, and spokesperson/public statements.
- `docs/368-*` — printable handouts, postcards, brochures, infographics, and downloadable PDFs.
- `docs/369-*` — videos, livestreams, webinars, replays, and republished clips.
- `docs/370-*` — emails, newsletters, reminders, and similar public-help inbox messages.
- `docs/371-*` — community-partner redistribution and co-branded relay lanes.
- `docs/372-*` — physical site signage, wayfinding, curbside, and reroute signs.
- `docs/374-*` — interactive state selectors, map-backed routers, dropdown tools, and decision-tree path finders.
- `docs/375-*` — official site-search boxes, autocomplete/query-suggestion layers, and result pages.
- `docs/376-*` — official maps, pin layers, optional geolocation helpers, and directions-link surfaces.
- `docs/377-*` — official language selectors, multilingual landing paths, locale fallback logic, and machine-translation boundary surfaces.
- `docs/378-*` — official download links, non-HTML file handoffs, embedded document/PDF viewers, and alternate-format fallback surfaces.
- `docs/379-*` — redirects, expired-election pages, stale file links, and help-rich 404 / unavailable recovery surfaces.
- `docs/380-*` — sitewide alerts, page-scoped banners, homepage notice modules, and bounded modal/interstitial surfaces.
- `docs/381-*` — QR codes, short URLs, vanity paths, and resolver-backed printed-to-digital handoff surfaces.
- `docs/382-*` — external search-result title links, snippets, site-name/favicon identity cues, and canonical result-presentation surfaces.
- `docs/383-*` — official social handles, profile bios, bio links, pinned posts, featured profile media, and legacy-profile recovery surfaces.
- `docs/384-*` — official mobile-app listings, install/download handoffs, store disclosures, and stale-version recovery surfaces.
- `docs/385-*` — search/maps office cards, platform office listings, hours/contact state, and official-domain recovery surfaces.
- `docs/386-*` — off-platform AI overviews, cited answer cards, synthesized answer handoffs, and recovery from partial or stale AI summaries.
- `docs/387-*` — voice search, smart-speaker / assistant spoken answers, office-card-fed hours/navigation responses, and recovery from partial or stale spoken first-contact layers.
- `docs/388-*` — shared-link preview cards, unfurls, chat/social card caches, and recovery from stale or decontextualized pasted-link first-contact layers.
- `docs/389-*` — subscription calendars, `.ics` downloads, add-to-calendar handoffs, timezone/all-day/recurrence semantics, and recovery from stale or rollover-surviving reminder artifacts.
- `docs/390-*` — public APIs, structured data feeds, widget backends, election-scope/freshness semantics, and safe recovery from partial, stale, ambiguous, or no-data machine-readable public answers.
- `docs/391-*` — crawlable official paths, sitemap/discovery posture, canonical representative URLs, locale-variant discovery, and safe retirement of stale pages before search/AI/voice layers form.
- `docs/392-*` — organization structured data, site names, favicons, official contact cues, and host-scope identity continuity so search/listing/AI layers can recognize the current official source rather than a stale or ambiguous shell.
- `docs/393-*` — breadcrumb trails, government-FAQ structured-data eligibility, visible-answer discipline, and validation after template/navigation changes so search previews do not quietly preserve invented hierarchy or stale FAQ answer shells.
- `docs/394-*` — temporary search removals, crawl-visible durable `noindex` / `X-Robots-Tag` state, non-HTML file retirement, URL-variation coverage, and recrawl acceleration so stale official pages/files stop recirculating after the current official answer already changed.
- `docs/395-*` — `nosnippet`, `max-snippet`, `data-nosnippet`, large-image-preview posture, and structured-data / AI-excerpt boundary checks so search and AI surfaces do not quietly quote volatile official text out of context.
- `docs/396-*` — visible freshness labels, structured date cues, timezone-aware update precision, page-versus-event date separation, and archive posture so official voter-information pages look current for the right reason instead of because of ambiguous date signals.
- `docs/397-*` — stable locale URLs, reciprocal `hreflang` clusters, generic-language / `x-default` fallbacks, non-HTML alternate declarations, and locale-adaptive crawl hazard controls so search can reach the right current translated official page instead of a selector or wrong-language shell.
- `docs/398-*` — whole-site domain/subdomain moves, `.gov` transitions, legacy-host retention, search-side move signaling, canonical/alternate-language migration, and emergency replacement-host controls so the official source host itself stays legible while the hostname changes.
- `docs/399-*` — Search Console property-scope coverage, verified-owner continuity, stale-token retirement, migration verification survival, and emergency search-side recovery operability so the office is not locked out when public search recovery is needed.
- `docs/400-*` — critical query/page cluster monitoring, page/country/device/search-appearance triage, preliminary-data windows, anomaly checks, and AI-feature measurement discipline so discoverability loss is separated from reporting artifacts.
- `docs/401-*` — page-level indexed-vs-live-state separation, canonical diagnosis, Googlebot-visible render/preview-control checks, and request-indexing operability so narrow current-page failures can be diagnosed before broader content churn.
- `docs/402-*` — critical-page performance budgets, mobile-first review, field-vs-preflight separation, hydration/fallback boundaries, and release-governance so current official pages remain usable before deadline-sensitive actions fail.
- `docs/403-*` — answer-first progressive-enhancement review, crawlable critical routing, widget-optional boundaries, and degraded-client recovery so current official answers do not disappear behind script-only shells.
- `docs/404-*` — mutable-answer cache classification, revalidation-first posture, service-worker navigation/update control, and stale-answer eviction/rollback so current official pages do not keep replaying an obsolete client-side state.
- `docs/405-*` — anti-bot challenge-scope separation, accessible CAPTCHA fallback/help recovery, wanted-crawler verification/allow posture, and non-`200` temporary interstitial discipline so current official pages do not disappear behind challenge walls.
- `docs/406-*` — request-context variant inventory, explicit-vs-ambient boundary discipline, no-cookie authoritative-first-contact posture, and experiment/personalization limits so the same official URL does not quietly tell different voters different things.
- `docs/407-*` — HTTPS-only critical-route posture, certificate/HSTS review, mixed-content zero tolerance, and unsafe-page recovery/help discipline so current official pages do not train voters to bypass browser warnings.
- `docs/408-*` — temporary-unavailable posture, queue/waitroom quality, client-vs-sitewide throttling distinction, and lightweight help-rich degraded-answer continuity so current official pages do not disappear behind opaque overload states.
- `docs/409-*` — anonymous-public-read classification, auth-required route separation, visible no-auth explanation/help recovery, and session-expiry / re-authentication continuity so current official pages do not quietly turn into account walls.
- `docs/410-*` — first-party core-answer preservation, non-primary embed boundaries, tag-manager/vendor-scope review, and blocked/slow external-origin fail-open recovery so current official pages do not become “wait for the vendor widget” shells.
- `docs/411-*` — optional-consent boundary discipline, bounded/dismissible administrative first-load overlays, focus/mobile non-obscuration review, and overlay-component fail-open recovery so current official pages do not make a policy wall the price of reading the answer.
- `docs/412-*` — user-initiated browser/device permission timing, no-capability-required public read, visible manual fallbacks, notification opt-in separation, and denied/unsupported fail-open recovery so current official pages do not make a browser prompt the price of reading the answer.
- `docs/413-*` — intentional outbound handoff labeling, direct-destination discipline, real-link-vs-fake-trigger boundaries, new-tab/popup/application-launch notice, and first-party recovery so current official pages do not strand voters behind opaque off-site jumps.
- `docs/414-*` — embedded-browser/container assumptions, open-in-browser or copy-link escape hatches, weak-browser-chrome recovery, and container-specific download/deeplink/new-context fail-open posture so current official pages do not become unreadable just because they opened inside an app shell.
- `docs/415-*` — low-connectivity / reduced-data first-contact survivability, text-first answer-lane visibility before heavy media/widgets, reduced-data handling without answer drift, and manual fallback/help continuity so current official pages do not require a good connection just to reveal the answer.
- `docs/416-*` — small-viewport / text-resize / zoom first-contact survivability, no-disabled-zoom posture, reflow-first ordinary reading, bounded two-dimensional exceptions with parallel readable fallbacks, and control-visibility discipline so current official pages do not require horizontal panning or clipped controls just to reveal the answer.
- `docs/417-*` — keyboard-only reachability, visible focus, logical task-order traversal, real interactive semantics, no-trap posture, and dynamic-update continuity so current official pages do not require pointer input or invisible focus just to reveal the answer.
- `docs/418-*` — nonvisual answer-lane survivability, with landmark/heading structure, usable control names, preserved relationships/instructions, and meaningful result/status announcements so current official pages do not depend on visual layout alone to expose the authoritative answer.
- `docs/419-*` — visible-reading answer-lane survivability, with practical text contrast, distinguishable controls/states, redundant non-color cues for warnings/required/selected/current states, and readable action/help affordances so current official pages do not depend on hue alone or ideal viewing conditions to expose the authoritative answer.
- `docs/420-*` — still-reading answer-lane survivability, with reduced-motion handling, pause/stop/manual control for auto-moving content, non-essential interaction-triggered animation limits, and interruption-safe live/update behavior so current official pages do not depend on carousels, countdown motion, shimmer loaders, or rotating notices to expose the authoritative answer.
- `docs/421-*` — touch/coarse-pointer answer-lane survivability, with adequately sized or separated activation areas, no-hover equivalents for hover-revealed meaning, simple non-gesture alternatives for swipe/drag-heavy controls, and precision-independent access to the authoritative answer so current official pages do not depend on tiny hit targets, hover-only disclosures, or map-pixel hunting.
- `docs/422-*` — typed-entry answer-lane survivability, with task-accurate field labels, sensible keyboard/input hints, paste/autofill survivability, constrained-format-helper discipline, and value-preserving correction paths so current official pages do not depend on brittle masks, ambiguous field purpose, or clear-on-error retry loops to reveal the authoritative answer.
- `docs/423-*` — date-entry answer-lane survivability, with explicit date purpose, visible format cues, manual typed-date fallback, widget-optional calendars, correction-friendly segmented date entry, and visible date-window bounds so current official pages do not depend on brittle pickers, hidden min/max rules, or locale/format guesswork to reveal the authoritative answer.
- `docs/424-*` — address-entry answer-lane survivability, with explicit address-role clarity, reviewable autocomplete/geocoder suggestions, preserved apartment/unit and other secondary detail, repeated-address disambiguation, and manual edit/override so current official pages do not depend on a silent “best match” guess to reveal the authoritative answer.
- `docs/425-*` — name-entry answer-lane survivability, with justified full-name-vs-split-field choice, support for diacritics/spaces/hyphens/suffixes/single-name cases, clear registration-record naming cues, and value-preserving mismatch recovery so current official pages do not depend on Western-only parsing assumptions or brittle exact-match dead ends to reveal the authoritative answer.
- `docs/426-*` — fixed-format identifier-entry answer-lane survivability, with explicit token-kind cues, exact-string-vs-number posture, preserved leading zeros and meaningful letters/separators, mask-safe paste/correction, and value-preserving retry help so current official pages do not depend on silent numeric coercion or brittle fixed-format parsing to reveal the authoritative answer.
- `docs/427-*` — contact-target and verification-code answer-lane survivability, with explicit phone-vs-email semantics, visible SMS-capable/U.S.-number requirements when relevant, ordinary paste/autofill support, predictable code-entry behavior, and delivery-failure/help recovery so current official pages do not depend on brittle contact verification or surprise code choreography to reveal the authoritative answer.
- `docs/428-*` — document-upload answer-lane survivability, with explicit accepted file/count/size expectations, clear camera-vs-existing-file posture, actionable upload errors, safe retry-state preservation, and visible alternate/help recovery so current official pages do not depend on hidden attachment assumptions or capture-only flows to reveal the authoritative answer.
- `docs/429-*` — multi-step process answer-lane survivability, with visible current-step/process-shape cues, optional-step posture, warned invalidation of later work, explicit save/resume-or-non-persistence posture, and review-before-submit recovery so current official pages do not depend on opaque wizard behavior or silent step loss to reveal the authoritative answer.
- `docs/430-*` — post-submit answer-lane survivability, with explicit submitted-vs-pending-vs-needs-action outcome cues, durable confirmation-state visibility, reference-number/keep-a-record posture, next-step timing, and duplicate-safe retry/help recovery so current official pages do not depend on ambiguous success states or blind resubmission to reveal what happened.
- `docs/431-*` — pre-completion timeout / expiry survivability, with early inactivity-limit disclosure, accessible extend-or-preserve posture, context restoration through re-authentication when feasible, and expired-state restart/help clarity so current official pages do not depend on hidden timers or surprise work loss.
- `docs/432-*` — in-session processing / wait-state survivability, with explicit working-vs-waiting-vs-queued state cues, truthful determinate-or-indeterminate progress posture, duplicate-action prevention while a request remains in flight, and long-wait help/recovery so current official pages do not depend on spinner-only uncertainty between action and outcome.
- `docs/433-*` — after-confirmation pending-state survivability, with longer-lived unresolved-state vocabulary, ordinary check-back windows, authoritative later-status paths, reference-number reuse posture, and silence-escalation clarity so current official pages do not depend on content-free “pending” states once the first confirmation moment has passed.
- `docs/434-*` — unsuccessful-outcome survivability, with plain-language negative-result meaning, fixable-vs-final-vs-wrong-route distinctions, preserved retry/help context, and authoritative next-step visibility so current official pages do not depend on opaque “unable to process,” “rejected,” or “no match found” states once the route has actually resolved unsuccessfully.
- `docs/435-*` — service-unavailable / maintenance / degraded-mode survivability, with plain-language temporary-unavailable meaning, affected-function specificity, authoritative fallback/help visibility, retry/check-back posture, and semantically honest temporary-error signaling so current official pages do not depend on generic outage pages, blank shells, or content-free “try again later” ambiguity when the service itself is down.
- `docs/436-*` — session-end / shared-device survivability, with visible sign-out or safe-exit posture, explicit shared-device/public-device risk cues, honest logout-vs-local-clearing boundaries, save/resume privacy limits, and accessible exit guidance so personalized official routes do not depend on private-device assumptions or hidden browser-clearing folklore once the voter has reached a sensitive answer lane.
- `docs/437-*` — portable-record / print-save-to-PDF off-screen fidelity, with must-survive fields, reviewed print/save output modes, HTML-vs-PDF authority clarity, and mobile-safe record-keeping cues so official answers do not evaporate once the live page is gone.
- `docs/438-*` — bookmark/share/revisit URL survivability, with public-share-safe vs same-user-only state classes, browser-history alignment, secret-free URL posture, and substitute reference/help routing so official answers do not evaporate or leak when the current URL itself is kept or forwarded.
- `docs/439-*` — already-open route return-state survivability, with Back/Forward, hidden-return, restore, and parallel-tab freshness/recovery posture so official answers do not silently persist as stale or contradictory state after the user comes back.
- `docs/440-*` — reader-mode / simplified-view main-content extraction, with must-survive facts, bounded reader-safe-vs-summary-only posture, and visible full-view/help boundaries so critical official meaning does not vanish when the browser strips surrounding chrome.
- `docs/441-*` — page-title / browser-tab / history-entry disambiguation, with task-first title patterns, office/jurisdiction context, dynamic title updates, and title-heading-breadcrumb alignment so the right official route stays findable in browser/app chrome.
- `docs/442-*` — section-anchor / in-page-navigation / fragment-target continuity, with targetable answer sections, heading-and-jump-link alignment, fragment continuity across ordinary revisions, and hidden-section boundary review so long official pages do not turn the right answer into a generic scroll hunt.
- `docs/443-*` — accordion / disclosure / collapsed-answer reveal continuity, with meaningful panel labels, default-open-vs-explicit-reveal posture, direct-target reveal behavior, and degraded-script answer visibility so the right official answer does not remain technically present but practically concealed behind closed panels.
- `docs/444-*` — sticky-header / fixed-chrome / unobscured-target landing, with persistent-chrome inventory, fragment-and-scripted-scroll landing checks, mobile/zoom/banner offset review, and answer-bearing top-line visibility so the right official target does not look broken or incomplete underneath persistent UI.
- `docs/445-*` — tabs / active-panel continuity / hidden-panel findability, with meaningful tab labels, default-visible-vs-selected panel review, focus-vs-selection posture, hidden-panel reveal continuity, and overview/help escape so the right official answer does not remain stranded behind the wrong visible panel.
- `docs/446-*` — data tables / responsive overflow / sort-state / row-findability, with header/context preservation, narrow-screen and stacked-row review, visible sort/filter posture, row/cell re-findability, and help/overview escape so the right official answer does not dissolve into clipped columns, ambiguous cells, or silent table state.
- `docs/447-*` — cards / collections / answer-tile disambiguation, with grouped-item structure, distinct headings and CTA purpose, badge/status semantics, responsive scan-order review, and help/overview escape so the right official answer does not dissolve into lookalike tiles or ambiguous card destinations.
- `docs/448-*` — source-order / visual-order / focus-order continuity, with sequence-sensitive route inventory, featured-block promotion review, source-vs-visual order coherence, and responsive restacking checks so the right official answer does not imply different sequences to mouse, keyboard, speech, or magnifier users.
- `docs/449-*` — bypass-blocks / skip-links / first-answer reachability, with repeated-block inventory, skip-target review, mobile header/banner checks, and bounded evidence that the right official answer remains directly reachable past repeated government/site chrome.
- `docs/450-*` — pagination / current-page indication / result-set continuity, with page-boundary review, explicit current-page semantics, more-pages/end-of-set cues, compact/mobile pagination checks, and bounded evidence that the right official answer does not disappear behind a silent page-1 cliff.
- `docs/451-*` — load-more / infinite-scroll / result-refindability, with continuation-mode review, item identity/position cues, loading/end-of-set announcements, compact/mobile continuation checks, and bounded evidence that the right official answer does not disappear into silent autoload or virtualization drift.
- `docs/452-*` — filters / facets / active-scope / subset-reset, with group-label and selection-model review, visible active-scope posture, bounded result-change announcements, compact/mobile active-filter continuity, and bounded evidence that the right official answer does not disappear behind hidden subset state or a missing clear/reset path.
- `docs/453-*` — comboboxes / suggestion-popups / explicit-commit, with official-set label clarity, typed-vs-highlighted-vs-committed state review, back-out/recovery posture, bounded answer-lane update announcements, compact/mobile continuity, and bounded evidence that the right official answer does not silently change on suggestion highlight or blur.
- `docs/454-*` — visible breadcrumb trails / current-location legibility / parent-path continuity, with hierarchy-truth review, singular current-page marking, title-heading alignment, compact/mobile breadcrumb reduction, and bounded evidence that deep-linked voters can still move up to the right parent official section without browser-history guesswork.
- `docs/455-*` — zero-results states / empty-state / recovery-route continuity, with visible query/scope persistence, truthful clear/broaden/help recovery options, bounded status-message review, recurring no-result signal review, and bounded evidence that a retrieval miss does not masquerade as a governing official negative.
- `docs/456-*` — sort controls / default order / order-change legibility, with explicit default-order labeling, visible current-order posture, promoted-vs-ordinary lane separation, bounded dynamic order-change announcements, and bounded evidence that “top” or “first” does not silently masquerade as a substantive official priority claim on non-table result routes.
- `docs/457-*` — horizontal rails / carousels / offscreen-answer discoverability, with visible continuation cues, labeled next/previous or equivalent controls, pause/manual control for any auto-rotation, compact/mobile and keyboard continuity, and bounded evidence that the right official answer does not remain silently offscreen in a lateral swipe-only lane.
- `docs/458-*` — view switchers / list-map-calendar toggles / cross-view continuity, with explicit active-view state, deliberate activation posture, visible parity/carryover boundaries across views, compact/mobile continuity, and bounded evidence that the right official answer does not disappear behind a silently different current view.
- `docs/459-*` — answer overlays / dialogs / drawers / route continuity, with explicit user-trigger posture, stable item identity, close-and-return recovery, durable detail-route/share posture, compact/mobile continuity, and bounded evidence that the right official answer does not disappear into a transient UI layer.
- `docs/460-*` — navigation menus / fly-outs / destination continuity, with deliberate menu-trigger posture, truthful submenu-versus-link cues, parent-page fallback, compact/mobile hierarchy continuity, and bounded evidence that the right official destination does not disappear behind hover-fragile or semantically misleading navigation.
- `docs/461-*` — buttons / links / action-destination truthfulness, with honest navigation-versus-action posture, clear control-label/destination continuity, primary-versus-secondary action separation, grouped-control review, compact/mobile continuity, and bounded evidence that the next official step does not hide behind mixed link/button semantics or vague CTA wording.
- `docs/462-*` — disabled controls / unavailable actions / unlock-path legibility, with unavailable-reason visibility, explicit unlock-condition review, disabled-versus-`aria-disabled` posture review, same-page recovery versus fallback/help routing, compact/mobile continuity, and bounded evidence that a visible greyed-out control does not masquerade as a final official dead end.
- `docs/463-*` — tooltips / popovers / hover-help / essential-answer visibility, with supplemental-versus-critical-meaning review, trigger discoverability, dismissible-hoverable-persistent behavior, tooltip-versus-popover semantic honesty, durable visible alternatives for controlling rules, and bounded evidence that the official answer does not live only inside a transient help bubble.
- `docs/464-*` — transient toasts / snackbars / status messages / durable-outcome visibility, with severity-role truthfulness, auto-dismiss and replacement review, live-region/focus discipline, durable visible equivalents for governing meaning, and bounded evidence that the official answer does not hide in a vanishing toast.
- `docs/465-*` — browser-history entry mutation / `pushState()`-`replaceState()` semantics / back-stack truthfulness, with meaningful-answer-step versus canonicalization boundaries, consistent push-vs-replace review, overlay/subview Back semantics, repair-loop avoidance, recovery-point preservation, and bounded evidence that same-document routing keeps telling the truth about which official state each history step represents.
- `docs/466-*` — missing fragment targets / unresolved section anchors / fail-open refinding, with truthful miss signaling, preserved target identity, bounded refinding aids, hidden/collapsed target recovery, and bounded evidence that unresolved same-page references do not strand voters at a generic shell.
- `docs/467-*` — mutable live pages / point-in-time citation snapshots / current-vs-citation-head discipline, with live-versus-citation-head separation, preview/queue boundary honesty, superseding-head legibility, and bounded evidence that exact citation claims do not silently rest on a moving live page.
- `docs/468-*` — citation-head registers / unique-head warnings / public handoff discipline, with one tiny reviewed register for mutable route lineages, explicit operational-head versus citation-head naming, ambiguity/warning publication when no unique citation-safe head exists, and bounded evidence that downstream handoff users do not have to infer head truth from scattered pages or captures.
- `docs/469-*` — local-only saves / queued background sync / office-acknowledged-state truthfulness, with explicit local-versus-queued-versus-office receipt classes, restart/return continuity review, retry guidance that changes with the real state class, and bounded evidence that device-local memory or repair queues do not masquerade as official submission receipt.
- `docs/470-*` — mid-flow version drift / expected-head review / resumed-state honesty, with explicit earlier-basis versus current-basis separation, material-change re-review/restart/help posture, resumed-state expected-head cues, and bounded evidence that continuity of state does not masquerade as continuity of governing authority.
- `docs/471-*` — copy/share controls / clipboard-write truthfulness / native-share handoff posture, with explicit artifact-class labeling, success-versus-cancel-versus-unsupported honesty, share-safe substitution when the current route is not safely forwardable, and bounded evidence that office-offered handoff controls do not quietly mint misleading portable pointers.
- `docs/472-*` — installable web apps / home-screen launches / standalone-identity posture, with optional-install truthfulness, visible official identity when browser chrome is reduced, safe launch-entry and `start_url` / scope posture, browser/open-on-web recovery, and bounded evidence that installed web-app shells do not quietly impersonate standalone authoritative apps.
- `docs/473-*` — text-fragment deep links / quoted-text highlights / excerpt-anchor truthfulness posture, with visible surrounding official context, durable-anchor preference over brittle quote matches when needed, no-match/unsupported fail-open recovery, quote-observability humility, and bounded evidence that highlighted excerpts do not quietly masquerade as standalone official rulings.
- `docs/474-*` — browser find-in-page / hidden-until-found / first-match truthfulness posture, with high-stakes keyword-class review, duplicate-keyword/chrome boundary control, heading/freshness/help context around matched phrases, humility about hidden-state reveal guarantees, and bounded evidence that manual on-page keyword search does not quietly elevate decontextualized first hits into standalone official answers.
- `docs/475-*` — web push notifications / subscription lifecycle / stale-notification withdrawal posture, with explicit optionality, current-route landing review, unsubscribe/expiry/revocation recovery, delayed-or-rate-limited delivery honesty, superseding/withdrawal posture for stale alerts, and bounded evidence that browser-origin push remains subordinate to the controlling official page/help lane.
- `docs/476-*` — leave-page warnings / unsaved-changes dialogs / loss-prevention truthfulness posture, with route-level leave-risk classification, generic-browser-dialog humility, explicit unsaved-versus-local-versus-office-received state boundaries, custom-confirmation clarity, mobile/app-switch caution, and bounded evidence that leave warnings do not quietly masquerade as durable save or submission receipt.
- `docs/477-*` — post-submit redirects / browser repost prompts / refresh-safe confirmation posture, with reviewed post-submit destination classes, `303`-style retrieval honesty, explicit humility about generic browser repost prompts, duplicate-retry boundary control, and bounded evidence that official retry guidance does not quietly depend on redirect folklore or replay ambiguity.
- `docs/478-*` — text-assistance layers / autocorrect-autocapitalize / spellcheck / IME-composition posture, with decisive-field-class review, form-level inheritance review, composition-vs-commit boundaries, spellcheck/writing-suggestions privacy posture, and bounded evidence that browser/device text help does not quietly decide the authoritative entered value.
- `docs/479-*` — speculative loading / prefetch-prerender / pre-activation-freshness posture, with safe-target selection, GET-side-effect review, activation-gated prerender behavior, stale-speculation eviction, support-variance humility, and bounded evidence that browser-side future-navigation acceleration does not quietly outrun freshness or explicit user arrival.
- `docs/480-*` — private-browsing / ephemeral-storage / storage-denied-fallback posture, with no-storage first-contact review, private-session ephemerality honesty, storage-denial error handling, embedded third-party state fallback, local-truth-boundary clarity, and bounded evidence that privacy-hardened browsing does not quietly erase the route’s usability or authority story.
- `docs/481-*` — browser-native constraint validation / validation-messages / durable-error-recovery posture, with submit-path review, durable field- and page-level correction text, localized-validation-message humility, explicit pre-submit-versus-server-rejection boundaries, and bounded evidence that transient user-agent blocking does not quietly become the office’s only public explanation of why a route will not proceed.
- `docs/482-*` — virtual keyboards / visual-viewport shrink / obscured-control-recovery posture, with keyboard-open route-class review, visible continuation/help controls while typing, dismiss-and-resume recovery, correction visibility under keyboard-open conditions, support-variance humility around keyboard APIs, and bounded evidence that the current answer/help lane does not quietly vanish beneath the on-screen keyboard.
- `docs/483-*` — user-overridden text spacing / clipped-or-overlapped-content / readability-recovery posture, with reviewed spacing bounds, fixed-height/overflow/positioning risk review, short-label resilience, language/script applicability humility, and bounded evidence that the current answer/help lane does not quietly break once voters increase line, paragraph, word, or letter spacing.
- `docs/484-*` — forced-colors / high-contrast-system-palette / user-color-override posture, with reviewed forced-colors routes, custom-control/icon survivability, focus/state visibility under system palettes, rare-and-justified `forced-color-adjust` exceptions, and bounded evidence that the current answer/help lane does not quietly depend on the authored palette being preserved.
- `docs/485-*` — light/dark-theme-variant / browser-chrome / color-scheme coherence posture, with reviewed scheme parity, theme-sensitive browser UI and `theme-color` hints, embedded SVG/iframe inheritance review, manual-toggle humility, and bounded evidence that supported light/dark variants do not quietly become competing official visual stories.
- `docs/486-*` — browser-integrated page-summary / page-context-AI posture, with same-page authority-boundary review, selected-text qualifier-loss review, optional/blocked-feature honesty, and bounded evidence that browser-generated summaries of the already-open official page do not quietly become a second controlling answer surface.
- `docs/487-*` — browser-integrated page-translation / selected-text-translation posture, with reviewed official-translation-vs-convenience-translation boundaries, original-language recovery, auto-translate-persistence honesty, and bounded evidence that browser-translated renderings of the already-open official page do not quietly become a shadow multilingual publication.
- `docs/488-*` — browser-integrated OCR / image-text-extraction / scanned-PDF-text-layer posture, with text-equivalent-vs-extracted-text boundaries, layout-dependency warnings, downstream transform subordination, and bounded evidence that inferred text from the already-open official artifact does not quietly become a shadow transcript or action surface.
- `docs/489-*` — browser-integrated read-aloud / listen-to-page / page-audio posture, with serial-audio qualifier review, conversational/AI-playback boundaries, background-playback recovery, and bounded evidence that narration of the already-open official page does not quietly become a shadow official briefing.
- `docs/490-*` — browser-managed Reading List / offline-saved-page / web-archive posture, with in-page freshness and scope cues that survive capture, explicit live-route recovery for volatile topics, portable-edition distinction from office-issued artifacts, and bounded evidence that reopened browser-kept copies of the already-open official page do not quietly become a shadow current edition.
- `docs/491-*` — browser-generated image-description / unlabeled-image-inference posture, with generated-caption subordination, high-risk-image review, authored-text-equivalence backstops, support-variance honesty, and bounded evidence that inferred descriptions of images on the already-open official page do not quietly become a shadow explanatory surface.
- `docs/492-*` — browser-integrated live-captions / subtitle-translation posture, with generated-text subordination, translation-boundary review, portable-record honesty, privacy/retention variance notes, and bounded evidence that captions over already-open official media do not quietly become a shadow transcript or translated publication.
- `docs/493-*` — platform transcript-pane / searchable-transcript / clip-jump posture, with transcript-provenance review, jump-context control, searchability and portable-record honesty, and bounded evidence that transcript panes over already-open official media do not quietly become a shadow portable text edition or decontextualized rule surface.
- `docs/494-*` — platform chapter-marker / key-moment / shareable-chapter-list posture, with chapter-provenance review, heading-overstatement control, discovery-boundary review, share/copy boundary honesty, and bounded evidence that titled navigation surfaces over already-open official media do not quietly become a shadow answer map or portable excerpt surface.
- `docs/495-*` — platform clips / highlights / shareable-segment posture, with excerpt-provenance review, qualifier-loss control, publicity/discovery honesty, and bounded evidence that portable excerpts over already-open official media do not quietly become a shadow stand-alone answer surface.
- `docs/496-*` — platform autoplay / end-screen / card / play-next posture, with next-step provenance review, silent-continuity control, external-pivot honesty, and bounded evidence that player-driven continuations over already-open official media do not quietly become a shadow authority lift into an adjacent route.
- `docs/497-*` — platform Watch Later / saved-playlist / offline-download posture, with saved-media provenance review, offline-freshness boundaries, mixed-library adjacency control, and bounded evidence that platform-managed saved-media shelves over already-open official media do not quietly become a shadow private library of still-current official answers.
- `docs/498-*` — platform follow / subscription / live-event-reminder posture, with delivery-humility review, ranked-feed and inbox adjacency control, calendar-export boundary honesty, and bounded evidence that platform-managed relationship/reminder state over official media does not quietly become a shadow standing notice lane for still-current voter instructions.
- `docs/499-*` — platform AI video-summary / ask-this-video / answer-module posture, with answer-provenance review, transcript/language dependence review, jump-link portability control, and bounded evidence that player-native generated answers over already-open official media do not quietly become a shadow official briefing.
- `docs/500-*` — platform comments / live-chat / Q&A / poll / reaction posture, with elevated-interaction review, replay/copy portability control, moderation-boundary honesty, and bounded evidence that interaction layers over already-open official media do not quietly become a shadow help desk, correction lane, or stand-alone instruction surface.
- `docs/501-*` — platform alternate-audio / dubbed-audio / audio-description posture, with track-provenance review, language-switch honesty, written-route recovery, and bounded evidence that alternate spoken tracks over already-open official media do not quietly become a shadow spoken edition or translated current-answer lane.
- `docs/502-*` — platform popout-playback / picture-in-picture / background-play posture, with source-page-recovery review, context-loss honesty, detached-caption/audio continuity review, and bounded evidence that detached playback modes over already-open official media do not quietly become a stripped-down stand-alone official answer surface.
- `docs/503-*` — platform remote-playback / casting / second-screen posture, with queue/controller split review, remote-screen recovery review, automatic-handoff honesty, and bounded evidence that second-screen routes over already-open official media do not quietly become a stripped-down stand-alone official answer surface.
- `docs/504-*` — platform fullscreen / theater-mode / immersive-player posture, with context-loss review, availability-variance honesty, source-page-recovery review, and bounded evidence that enlarged same-device player layouts over already-open official media do not quietly become a stripped-down stand-alone official answer surface.
- `docs/505-*` — platform playback-speed / scrubbing / skipping / seek posture, with qualifier-loss review, live catch-up/currentness recovery, availability-variance honesty, and bounded evidence that fragmentary scan behavior over already-open official media does not quietly become a compressed stand-alone official answer surface.
- `docs/506-*` — platform watch-history / continue-watching / recent-videos / resume-state posture, with re-entry-memory review, remembered-position honesty, cross-device sync variance notes, and bounded evidence that history-driven resurfacing over already-open official media does not quietly become a shadow still-current return path.
- `docs/507-*` — platform channel-home / featured-video / playlist / collection-page posture, with featured-order review, mixed-scope aging honesty, shared/embed portability review, and bounded evidence that office-curated media collections over official recordings do not quietly become a shadow FAQ, router, or current-answer map.
- `docs/508-*` — platform upcoming-event page / Premiere watch-page / pre-live countdown posture, with discoverability-before-start review, countdown/trailer truthfulness, delay/reschedule honesty, and bounded evidence that public pre-start event shells over official media do not quietly become the apparent current-answer page before the briefing begins.
- `docs/509-*` — platform post-live archive / replay-page / ended-event-shell posture, with archive-identity review, redirect/playlist continuity review, archived-interaction boundary review, and bounded evidence that public post-live replay shells over official media do not quietly become the default current-answer or return path after the event ends.
- `docs/510-*` — platform search-result / homepage recommendation + browse-feed posture, with ranking/personalization review, mixed-source adjacency control, and bounded evidence that upstream platform discovery over official media does not quietly become the practical current-answer router before the media page is even opened.
- `docs/511-*` — platform share-panel / copy-link / timestamp-link + embed-export posture, with portable-wrapper review, current-time overclaim control, and bounded evidence that copied links and embedded official media do not quietly become shadow current-answer objects outside the original watch context.
- `docs/512-*` — platform unavailable / private / age-gated / region-blocked + playback-restriction posture, with restriction-state review, recovery-lane continuity, and bounded evidence that “video unavailable” or permission-denied shells over official media do not quietly become shadow answers about what the public can currently rely on.
- `docs/513-*` — platform playback-quality / adaptive-bitrate / resolution-selector + data-saver posture, with fidelity-state review, embed-quality review, and bounded evidence that lower-detail renditions of official media do not quietly become stand-alone answer surfaces for detail-heavy instructions.
- `docs/514-*` — platform titles / descriptions / thumbnails / posters + metadata-wrapper posture, with wrapper-state review, container-local metadata-drift review, and bounded evidence that mutable labels around the same official media do not quietly become the controlling currentness or scope summary.
- `docs/515-*` — platform processing / pending-optimization + not-yet-fully-ready media posture, with readiness-state review, delayed-derivative review, and bounded evidence that publicly reachable but still-processing official media does not quietly look like a settled stand-alone answer surface before the current written/help lane should yield.
- `docs/516-*` — platform live-edge / behind-live-state + latency/Watch-Live-recovery posture, with mixed-currentness review, delayed-slice recovery, and bounded evidence that still-live official media does not quietly treat materially behind-live viewing as interchangeable with the true live current answer.
- `docs/517-*` — platform simulcast-mirror / multi-route-live-event + redirect-chain posture, with primary-vs-mirror review, route-set variance review, redirect-legibility review, and bounded evidence that same-event official route sets do not quietly act like several interchangeable live answers.
- `docs/518-*` — platform registration-form / invite-only-join-link + audience-gated-media posture, with gate-type review, gated-discovery review, non-admitted-viewer recovery review, and bounded evidence that pre-access audience-selection shells do not quietly become the office’s whole public answer about availability or next steps.
- `docs/519-*` — platform view-count / concurrent-viewer / like-count + audience-metrics-wrapper posture, with metric-definition review, live-vs-replay/report distinction review, and bounded evidence that audience metrics over official media do not quietly become proof that a route is the controlling current answer.
- `docs/520-*` — platform channel-byline / profile-name / handle / verification-badge + source-identity-wrapper posture, with directory-binding review, cross-wrapper identity-cue review, and bounded evidence that bylines, badges, handles, uploader cards, and similar source cues around official media do not quietly become the whole proof that a route is official and current.
- `docs/521-*` — platform information-panel / disclosure-label / policy-wrapper posture, with wrapper-provenance review, cross-route wrapper-visibility review, and bounded evidence that context panels, ratings, sensitivity cues, protection banners, and similar wrapper signals around official media do not quietly become the office's whole explanation of currentness, authority, or legal effect.
- `docs/522-*` — platform event-theming / branded-player-chrome + live-status-label posture, with route-state-legibility review, cross-view chrome review, and bounded evidence that organizer-controlled banners, logos, colors, trailers, layout modes, latest-video substitutions, and hidden live-status cues around official media do not quietly become proof that a route is current, live, or newly authoritative.
- `docs/583-*` — platform-media stacked-authenticity-cues / identity-context-provenance ordering posture, with same-route cue coexistence review, governing-cue selection review, and bounded evidence that a byline/badge + context/policy wrapper + provenance bundle around one official media route does not quietly become a compound proof object.
- `docs/584-*` — platform-media provenance-signal / Content-Credentials posture, with presence-vs-absence honesty review, derivative-preservation review, verification-handoff review, and bounded evidence that origin/history signals around official media do not quietly become the whole proof that a route is current, authoritative, or action-safe.
- `docs/585-*` — platform-media authenticity-cue-transport / cross-route-divergence posture, with native-vs-embed-vs-mirror cue-transport review, absence-non-inference review, file-borne-vs-route-local classification, and bounded evidence that supportive authenticity-adjacent cues around one official media object do not quietly become proof that the underlying answer changed just because those cues traveled unevenly.
- `docs/586-*` — platform-media authenticity-cue-tension / aspect-separation posture, with same-route non-cancellation review, identity-vs-context-vs-provenance aspect-split review, and bounded evidence that supportive authenticity-adjacent cues around one official media route do not quietly collapse into a positive/negative authenticity score or a one-cue override.
- `docs/587-*` — platform-media authenticity-cue-lifecycle / non-retroactive-inference posture, with same-route cue timing review for badges, panels, and provenance disclosures that later appear, disappear, expire, or are backfilled, plus bounded evidence that one observed cue state does not quietly rewrite the route’s whole authenticity history.
- `docs/588-*` — platform-media authenticity-cue-attachment / scope-boundary posture, with channel-vs-route-vs-object attachment review, noninheritance review for siblings and derivatives, and bounded evidence that visually adjacent supportive cues do not quietly transfer to the wrong object or wrapper scope.
- `docs/589-*` — platform-media authenticity-cue-discoverability / inspection-gate posture, with expanded-description, click/tap-handoff, and hover/details-only review, plus bounded evidence that same-route cues do not quietly become either ambient proof or route-level absence just because later readers captured one visibility state.
- `docs/590-*` — platform-media authenticity-cue viewer-state-variance / eligibility-conditions posture, with country-or-region, language, app-or-device, and organization-setting conditionality review, plus bounded evidence that one viewer's same-route cue state does not quietly become the route's universal authenticity posture.
- `docs/591-*` — platform-media authenticity-cue observation-assembly / no-faux-single-state posture, with cross-route, cross-time, cross-viewer, and cross-interaction composite review, plus bounded evidence that later packets or screenshots do not quietly compress several observations into one simultaneously witnessed page posture.
- `docs/592-*` — platform-media authenticity-cue preview-shells / open-target-separation posture, with shell-versus-target cue inheritance review for search cards, playlist rows, queue slots, end-screen/info-card targets, library/file tiles, and similar preview-bearing shells, plus bounded evidence that shell-level cue posture does not quietly transfer to the opened target or vice versa.
- `docs/593-*` — platform-media authenticity-cue player-state-occlusion / reduced-context-suppression posture, with fullscreen/theater/miniplayer/PiP/popout hiddenness review, same-object reduced-context visibility review, and bounded evidence that surrounding cue disappearance inside a reduced-context player state does not quietly become route-level absence or withdrawal.
- `docs/594-*` — platform-media authenticity-cue observation-windows / clipped-captures / non-totality posture, with player-only-screenshot, partial-viewport, narrow-embed, and deck-crop review, plus bounded evidence that a truthful but narrow capture of the same route does not quietly become proof of the route's whole authenticity-cue posture.
- `docs/595-*` — platform-media authenticity-cue text-extracts / transcript-caption-OCR-derivatives / non-carried-cue posture, with copied-transcript, downloaded-text, subtitle-quote, and OCR-excerpt review, plus bounded evidence that extracted text from the same route does not quietly carry — or disprove — the route's surrounding authenticity-cue posture.
- `docs/596-*` — platform-media authenticity-cue audio-extracts / track-downloads / detached-spoken-derivatives / non-carried-cue posture, with downloaded-track, audio-only-export, detached-spoken-excerpt, and heard-layer-forward review, plus bounded evidence that extracted spoken audio from the same route does not quietly carry — or disprove — the route's surrounding authenticity-cue posture.
- `docs/597-*` — platform-media authenticity-cue still-image-extracts / frame-grabs / poster-exports / non-carried-cue posture, with frame-grab, poster-export, thumbnail-like-still, and frozen-visual-slice review, plus bounded evidence that detached still images from the same route do not quietly carry — or disprove — the route's surrounding authenticity-cue posture.
- `docs/598-*` — platform-media authenticity-cue metadata-extracts / title-description-chapter-list-derivatives / non-carried-cue posture, with copied-title, description-block, chapter-list, playlist-label, and metadata-sidecar review, plus bounded evidence that stripped metadata labels from the same route do not quietly carry — or disprove — the route's surrounding authenticity-cue posture.
- `docs/599-*` — platform-media authenticity-cue locator-derivatives / shared-links-timestamp-links / non-carried-cue posture, with copied-watch-URL, short-share-link, timestamp-link, and embed/player-URL review, plus bounded evidence that stripped pointers to the same route do not quietly carry — or disprove — the route's surrounding authenticity-cue posture.
- `docs/600-*` — platform-media authenticity-cue detached-derivative family quickmap / mixed-packets routing / anti-fragmentation posture, with dominant-derivative review, carrier-wrapper-nonpromotion discipline for slide/PDF/chat-export/saved-page bundles, mixed detached-derivative packet compression, saved-page-and-web-archive baseline routing, and a growth stop that keeps `595–599` acting like one bounded subfamily rather than a springboard for fresh detached-derivative siblings.
- `docs/523-*` — platform-media boundary quickmap + duplicate firewall, with fast primary-surface selection across the `493–522` media stack plus bounded provenance-signal controls `583–618`, mixed-incident routing discipline, and an anti-bloat promotion test for future adjacent media additions.
- `docs/601-*` — platform-media wrapper-label hygiene for filenames / subject lines / slide titles / memo headings, so short later packet labels stay descriptive rather than becoming copied-source or governing-member substitutes.
- `docs/602-*` — platform-media wrapper-summary hygiene for forwarding comments / share messages / speaker notes / memo-body synopsis prose, so longer later packet summaries stay descriptive rather than becoming copied-source or governing-member substitutes.
- `docs/603-*` — platform-media wrapper-markup hygiene for highlight boxes / arrows / circles / underlines / comment anchors / zoom callouts / ink, so later packet emphasis stays descriptive rather than becoming source-native or governing-member proof.
- `docs/604-*` — platform-media wrapper-concealment hygiene for redactions / crop-hide regions / hidden slides / hidden objects, so later packet suppression stays descriptive rather than becoming source-absence or governing-member proof.
- `docs/605-*` — platform-media wrapper-ordering hygiene for slide order / PDF page sequence / packet section order, so later packet arrangement stays descriptive rather than becoming source-chronology or governing-member proof.
- `docs/606-*` — platform-media wrapper-membership hygiene for imported slides / selected PDF merges / chosen attachments, so later packet composition stays descriptive rather than becoming source-native completeness, source-native scope, or governing-member proof.
- `docs/607-*` — platform-media wrapper-repetition hygiene for duplicate slides / repeated pages / repeated excerpts / repeated attachments, so later packet multiplicity stays descriptive rather than becoming independent corroboration, source-native multiplicity, or governing-member proof.
- `docs/608-*` — platform-media wrapper-layout hygiene for side-by-side placement / inset-over-main layout / gallery rows / split-screen comparison frames, so later packet positioning stays descriptive rather than becoming source-native adjacency, source-native simultaneity, source priority, or governing-member proof.
- `docs/609-*` — platform-media wrapper-prominence hygiene for enlarged hero panels / thumbnail demotion / resized excerpt blocks, so later packet size weighting stays descriptive rather than becoming source-native emphasis, source-native priority, or governing-member proof.
- `docs/610-*` — platform-media wrapper-styling hygiene for warning palettes / official-looking themes / font-background restyling, so later packet visual tone stays descriptive rather than becoming source-native urgency, source-native officiality, or governing-member proof.
- `docs/611-*` — platform-media wrapper-timing hygiene for object animations / build order / autoplay / delayed reveal, so later packet motion stays descriptive rather than becoming source-native chronology, source-native urgency, or governing-member proof.
- `docs/612-*` — platform-media wrapper-navigation hygiene for hyperlinks / action buttons / hotspots / internal jumps, so later packet click paths stay descriptive rather than becoming source-native navigation, source-native hierarchy, source-native endorsement, or governing-member proof.
- `docs/613-*` — platform-media wrapper-view-state hygiene for initial-view settings / open-page-open-slide choices / zoom / fit modes, so later packet opening posture stays descriptive rather than becoming source-native focus, source-native default posture, source-native priority, or governing-member proof.
- `docs/614-*` — platform-media wrapper-query-state hygiene for search terms / find-hit lists / highlighted matches / result panes, so later packet query posture stays descriptive rather than becoming source-native emphasis, source-native completeness, or governing-member proof.
- `docs/615-*` — platform-media wrapper-selection-state hygiene for selected thumbnails / selected objects / selected text ranges / active sidebar items, so later packet active focus stays descriptive rather than becoming source-native emphasis, source-native scope, or governing-member proof.
- `docs/616-*` — platform-media wrapper-review-discourse hygiene for comment threads / replies / action-item review notes / note sidebars, so later packet attached discussion stays descriptive rather than becoming source wording, source endorsement, source resolution, or governing-member proof.
- `docs/617-*` — platform-media wrapper-revision-state hygiene for tracked changes / suggestions / redlines / replace-text proposal layers, so later packet proposal posture stays descriptive rather than becoming adopted source text, adopted source revision, or governing-member proof.
- `docs/618-*` — platform-media wrapper-history-state hygiene for version-history panes / named versions / restore candidates / prior-version comparisons, so later packet prior-version posture stays descriptive rather than becoming current source text, adopted source chronology, restored source state, or governing-member proof.
- `docs/619-*` — platform-media wrapper-access-state hygiene for share dialogs / link-access scopes / role matrices / manage-access posture, so later packet permissions posture stays descriptive rather than becoming source-route publicness, endorsed audience scope, or governing-member proof.
- `docs/620-*` — platform-media wrapper-event-state hygiene for notification cards / activity feeds / alert emails / shared-with-you posture, so later packet workflow-event posture stays descriptive rather than becoming official publication, current source change, endorsed distribution, or governing-member proof.
- `docs/621-*` — platform-media wrapper-lifecycle-state hygiene for Trash / Recycle Bin / deleted queue / restore confirmation posture, so later packet deletion-recovery posture stays descriptive rather than becoming official retraction, current public absence, restored publication, or governing-member proof.
- `docs/622-*` — platform-media wrapper-sync-state hygiene for available-offline / local-availability / sync-pending / sync-conflict posture, so later packet offline-sync posture stays descriptive rather than becoming official publication, office acknowledgment, current source stability, or governing-member proof.
- `docs/623-*` — platform-media wrapper-organization-state hygiene for starred state / recent-file listings / pinned recents / shortcut-favorite placement / moved-location posture, so later packet organization posture stays descriptive rather than becoming official prominence, currentness, endorsed retention, or governing-member proof.
- `docs/624-*` — platform-media wrapper-information-state hygiene for details panes / info cards / properties dialogs / owner-location-size-type fields, so later packet file-information posture stays descriptive rather than becoming source-native metadata, official control, canonical location, or governing-member proof.
- `docs/625-*` — platform-media wrapper-listing-state hygiene for file lists / sort order / filters / group headers / shown-hidden columns, so later packet collection posture stays descriptive rather than becoming official chronology, official completeness, official categorization, or governing-member proof.
- `docs/626-*` — platform-media wrapper-action-state hygiene for command bars / context menus / quick actions / disabled commands / more-actions sheets, so later packet affordance posture stays descriptive rather than becoming official permission, official capability, source-native control, or governing-member proof.
- `docs/627-*` — platform-media wrapper-preview-state hygiene for thumbnail tiles / preview panes / same-tab previews / partial-full preview shells, so later packet preview posture stays descriptive rather than becoming source-native frames, source-native default render state, settled content state, or governing-member proof.
- `docs/628-*` — platform-media wrapper-launch-state hygiene for "Open with" / "Open in app" / browser-desktop-defaults, so later packet open-target and handler posture stays descriptive rather than becoming source-native format requirements, official route choice, canonical render environment, required software, or governing-member proof.
- `docs/629-*` — platform-media wrapper-participation-state hygiene for collaborator avatars / anonymous-viewers / cursors / participants, so later packet presence posture stays descriptive rather than becoming source authorship, official approval, current office attention, governing participation, or governing-member proof.
- `docs/630-*` — platform-media wrapper-account-state hygiene for signed-in accounts / profile-switchers / work-or-school or personal-business shells, so later packet account posture stays descriptive rather than becoming source ownership, official control, official affiliation, governing identity, or governing-member proof.
- `docs/631-*` — platform-media wrapper-classification-state hygiene for classification labels / sensitivity-retention labels / policy tips / message-bar labels, so later packet classification posture stays descriptive rather than becoming source-native classification, official endorsement, legal handling duty, final retention posture, or governing-member proof.
- `docs/632-*` — platform-media wrapper-security-state hygiene for suspicious-file warnings / blocked-file markers / protected-view shells / trust-gated security dialogs, so later packet security posture stays descriptive rather than becoming source inauthenticity, official withdrawal, source-native danger classification, or governing-member proof.
- `docs/633-*` — platform-media wrapper-signature-state hygiene for signature lines / validation badges / signer-certificate details / eSignature status panels / audit-trail pages, so later packet signature posture stays descriptive rather than becoming source-route official publication, source-route authorship, office adoption, legal finality, or governing-member proof.
- `docs/634-*` — platform-media wrapper-workflow-state hygiene for submit-for-approval posture / pending-approved-rejected badges / approval sidebars / approved-version controls, so later packet workflow disposition stays descriptive rather than becoming source-route official publication, source-route authorship, office adoption, legal finality, or governing-member proof.
- `docs/635-*` — platform-media wrapper-rights-state hygiene for no-download / no-print / no-copy / no-forward / review-only / read-only / expiring-rights posture, so later packet usage-restriction posture stays descriptive rather than becoming source-route official publication, source-route authorship, office adoption, legal finality, or governing-member proof.
- `docs/636-*` — platform-media wrapper-watermark-state hygiene for visible watermarks / confidentiality overlays / viewer-email burn-ins / playback-time watermark posture, so later packet watermark/deterrence posture stays descriptive rather than becoming source-route official publication, source-route authorship, source-native classification, office adoption, legal finality, or governing-member proof.
- `docs/637-*` — platform-media wrapper-proofing-state hygiene for visible spelling underlines / grammar marks / autocorrect replacements / proofing-language badges / dictionary-ignore posture, so later packet proofing posture stays descriptive rather than becoming source-native error, source-native correction, official terminology rulings, source language, office adoption, or governing-member proof.
- `docs/638-*` — platform-media wrapper-translation-state hygiene for translated renderings / selected-text translation popups / show-original posture / language-pair badges / auto-translate indicators, so later packet translation posture stays descriptive rather than becoming a reviewed official translation, source-native language, office adoption, or governing-member proof.
- `docs/639-*` — platform-media wrapper-reader-state hygiene for Reader View / Reading mode / Show Reader / Immersive Reader / stripped-chrome posture / simplified article extraction / line-focus posture, so later packet reader posture stays descriptive rather than becoming source-native layout, source-native omission, office-curated simplification, or governing-member proof.
- `docs/640-*` — platform-media wrapper-outline-state hygiene for document outlines / bookmark panels / heading-navigation panes / table-of-contents sidebars, so later packet structure-map posture stays descriptive rather than becoming source-native hierarchy, source-native completeness, office-curated priority ordering, or governing-member proof.
- `docs/641-*` — platform-media wrapper-transcript-state hygiene for transcript panes / current-line highlights / transcript search / transcript-language-timestamp toggles / return-to-current-time posture, so later packet transcript posture stays descriptive rather than becoming a reviewed official transcript edition, source-native emphasis, source-native chronology, official translation, or governing-member proof.
- `docs/642-*` — platform-media wrapper-rendition-state hygiene for `Auto` / `Data saver` / visible resolution picks / quality-settings panes / embed-default quality posture, so later packet rendition posture stays descriptive rather than becoming source-native blur, source-native unreadability, source-native omission of fine detail, official preferred fidelity, or governing-member proof.
- `docs/643-*` — platform-media wrapper-caption-state hygiene for CC on/off posture / selected caption language / auto-generated-caption inclusion / caption appearance customization / default-on embed captions, so later packet caption posture stays descriptive rather than becoming burned-in source text, a reviewed official translation, source-native line breaking or emphasis, source-native accessibility styling, or governing-member proof.
- `docs/644-*` — platform-media wrapper-playback-rate-state hygiene for visible `1.25x` / `1.5x` / `2x` / `0.8x` selections / temporary hold-to-scan posture / remembered speed defaults / speed-menu state, so later packet playback-rate posture stays descriptive rather than becoming source-native brevity, source-native pacing, an officially summarized edition, office-preferred review tempo, or governing-member proof.
- `docs/645-*` — platform-media wrapper-audio-output-state hygiene for mute toggles / low-volume posture / restored audibility / visible volume-slider state, so later packet audibility posture stays descriptive rather than becoming source-native silence, source-native incompleteness, office-preferred audio redaction, an officially republished quiet edition, or governing-member proof.
- `docs/646-*` — platform-media wrapper-player-state hygiene for fullscreen / theater mode / miniplayer / picture-in-picture / popout posture, so later packet reduced-context player posture stays descriptive rather than becoming source-native framing, source-native omission of surrounding route context, office-preferred presentation, an officially republished immersive edition, or governing-member proof.
- `docs/647-*` — platform-media wrapper-audio-track-state hygiene for original-audio selection / dubbed-language posture / automatic-dub selection / audio-description selection / commentary-track posture, so later packet spoken-audio-track posture stays descriptive rather than becoming source-native language, a reviewed official translation, an officially adopted accessibility/commentary edition, or governing-member proof.
- `docs/651-*` — platform-media wrapper-repeat-state hygiene for loop-on controls / repeat-one indicators / replay-after-end posture / continuous replay cycling / embed-loop settings, so later packet repeat-state posture stays descriptive rather than becoming source-native repetition, official continuous rebroadcast, office-preferred replay posture, source-native chronology, or governing-member proof.
- `docs/650-*` — platform-media wrapper-chapter-state hygiene for chapter markers / active chapter highlights / chapter-list panes / chapter-title previews, so later packet chapter-state posture stays descriptive rather than becoming source-native structure, an officially endorsed excerpt boundary, a governing quoted section, or governing-member proof.
- `docs/524-*` — platform-media route-state lexicon + badge-normalization / capture-order discipline, with one compact vocabulary for pre-start, live, behind-live, replay/archive, processing, and state-obscured-by-chrome notes so adjacent event-state docs stay comparable instead of badge-by-badge divergent.
- `docs/525-*` — platform-media mutation classes + first-contact evidence-pack / snapshot-minimization discipline, with a five-part capture budget that starts at the outermost route, records one normalized state cue, then preserves only the decisive wrapper delta and re-anchor path so multi-wrapper incidents stay explainable without bloated screenshot packs.
- `docs/526-*` — platform-media re-anchor ladder + canonical-recovery-target / wrapper-exit discipline, with one compact precedence rule for choosing the winning office-controlled recovery target after a mixed-wrapper incident so adjacent packets do not drift across embeds, replay shells, lagged live slices, or other lower-authority exits.
- `docs/527-*` — platform-media control tuple + one-line normalization contract / packet-comparison discipline, with one canonical summary line for the `523–526` decisions plus one optional canonicalized `companions=` header plus one optional `companions_overflow=` spillway for **additional companion docs only** plus one optional single-tag `companions_detail=` line for one extra same-doc residue fact from one already-carried companion doc, so adjacent packets can record boundary, state, mutation, cue, recovery target, and compact subordinate chain facts without prose drift, silent-negation drift when a later header omits a tag, fake diffs caused by ad hoc non-doc-native companion tokens, overreading same-doc token replacement as full supersession, duplicating one companion doc across header and overflow, or leaving same-doc residue to loose prose instead of a bounded canonical detail line chosen by doc-declared detail-pick order when available, while keeping header-vs-overflow selection under the archive's deterministic budget rule (`540–561` first, then `562,570,581,572,575,576,573,563,580,577,579,578,571,565,567,564,566,574,568,569`).
- `docs/528-*` — platform-media same-object transition chains + packet-stitching / resnapshot-threshold discipline, with one compact continuity test and append/fork/split rule so adjacent observations of the same official event can accumulate across time without turning into disconnected duplicate packets, treating header omission as a clearance event by itself, or treating companion-token replacement as a split when the controlling tuple stayed stable.
- `docs/529-*` — platform-media chain heads + current-control / closeout discipline, with one compact governance rule for naming the active packet inside a same-object chain, demoting older packets to historical-leg status, and keeping companion-only later appends from churning the general-purpose head unless a controlling field actually moved.
- `docs/530-*` — platform-media chain citations + head-first-reference / historical-leg-scoping discipline, with one compact downstream rule for citing the current head by default, scoping earlier-leg references explicitly, and avoiding negation or head-change claims that are supported only by missing later companion tags or by companion-only latest-packet drift.
- `docs/531-*` — platform-media head-supersession notes + trigger-codes / demotion discipline, with one compact governance note for recording when a new head displaced the old one, what bounded trigger caused that change, and why later summaries should treat the prior head as historical rather than reconstructing the demotion from scattered packet prose.
- `docs/532-*` — platform-media head-volatility-labels + provisional-current-notes / review-window discipline, with one compact forward-looking note for marking a valid current head as still provisional, naming the next expected control-changing trigger, and telling later summaries when an open chain should be revisited before it is allowed to sound settled.
- `docs/533-*` — platform-media no-public-head states + headless-chain-notes / fallback-anchor discipline, with one compact absence-governance note for when a same-object chain still exists historically but no public media packet should remain current, so present-tense guidance moves to the best fallback anchor instead of leaving an old replay or live leg sounding current.
- `docs/534-*` — platform-media co-current aliases + sibling-routes / canonical-head-with-alias discipline, with one compact same-answer multi-route note for when more than one public route is still current for the same controlling event or recording, so the archive can keep one canonical head while naming other sibling routes as aliases instead of forcing false supersession or false historical-leg labeling.
- `docs/535-*` — platform-media audience-scoped current aliases + scope-labels / public-default-retention discipline, with one compact subset-route note for when a current public head coexists with a still-current attendee-, registrant-, or invitee-scoped route, so later summaries can preserve the ordinary-public default while still recording audience-specific delivery paths honestly.
- `docs/536-*` — platform-media route-scope transitions + widening/narrowing / alias re-bucketing discipline, with one compact scope-drift note for when the same route or answer family moves between ordinary-public, public-alias, audience-scoped, and headless-chain buckets over time, so later summaries can reclassify that route without inventing a new object or a false supersession.
- `docs/537-*` — platform-media capability-bearing current aliases + link-secret routes / redaction-default discipline, with one compact bearer-route note for when a same-object chain still has a current unlisted, privacy-hash, or other token-bearing path, so later summaries can classify the route honestly without promoting it into the ordinary-public default or reproducing more of the route than the archive needs.
- `docs/538-*` — platform-media player-host render aliases + direct-embed routes / watch-page-default discipline, with one compact render-path note for when a same-object chain still has a direct player-host or embed-render route, so later summaries can preserve that host-path fact without mistaking the render shell for an ordinary watch-page alias, a new current head, or a bearer-style secret route.
- `docs/539-*` — platform-media entrypoint-offset aliases + current-time/start-at routes / full-object-default discipline, with one compact landing-point note for when a same-object chain still has a `Start at`, current-time, or similar offset route, so later summaries can preserve that arrival-point fact without mistaking it for a new current head, a true clip surface, or a replacement for the full-object default.
- `docs/540-*` — platform-media notification carriers + reminder pointers / route-carrier separation discipline, with one compact delivery-wrapper note for when a same-object chain also has a reminder, notification, inbox entry, or delivery email, so later summaries can preserve what recipients received without mistaking the carrier itself for the current route, alias, or head.
- `docs/541-*` — platform-media carrier-target drift + late-delivery retargeting / stale-pointer non-supersession discipline, with one compact delivered-target note for when a real reminder, notification, inbox entry, or delivery email points at a route that no longer controls, so later summaries can preserve what recipients opened without inferring false supersession or letting stale carrier targets outrank the head-first citation rule.
- `docs/542-*` — platform-media app-launch aliases + open-in-app deep links / browser-default-retention discipline, with one compact app-container note for when a same-object chain launches through an installed app, open-in-app prompt, universal link, or other app-preferred handoff, so later summaries can preserve the app path honestly without letting it outrank the citation-safe browser/public default.
- `docs/543-*` — platform-media remembered-resume aliases + history re-entry / full-object-default discipline, with one compact re-entry note for when a same-object chain comes back through history, Continue Watching, recents, or remembered progress, so later summaries can preserve that memory-shaped return honestly without letting it outrank the citation-safe browser/public default or blur into an explicit offset alias.
- `docs/623-*` — packet-starred / recents / shortcuts / favorites + wrapper-organization-state firewall, with one compact organization-state note for when a later packet preserves starred status, recent-file placement, pinned recent entries, shortcut/favorite placement, or moved-location posture around same-route detached derivatives, so later summaries can preserve that curation layer honestly without letting it outrank the current head, packet governance, or citation-safe source control.
- `docs/624-*` — packet-details-panes / properties / owner-location + wrapper-information-state firewall, with one compact information-state note for when a later packet preserves a details pane, info card, properties dialog, or owner/location/size/type block around same-route detached derivatives, so later summaries can preserve that file-information layer honestly without letting it rewrite source-native metadata, official control, canonical location, packet governance, or citation-safe source control.
- `docs/625-*` — packet-file-lists / sort-filters-groups + wrapper-listing-state firewall, with one compact listing-state note for when a later packet preserves a file list, saved view, sort order, filter subset, grouped header, shown/hidden columns, or similar visible collection-level posture around same-route detached derivatives, so the archive preserves that wrapper-added listing state honestly without quietly treating it as official chronology, official completeness, official categorization, or the packet's governing member.
- `docs/626-*` — packet-command-bars / context-menus + wrapper-action-state firewall, with one compact action-state note for when a later packet preserves a command bar, context menu, quick-action row, disabled command, or similar visible affordance layer around same-route detached derivatives, so the archive preserves that wrapper-added action state honestly without quietly treating it as official permission, official capability, source-native control, or the packet's governing member.
- `docs/627-*` — packet-thumbnails / preview-panes + wrapper-preview-state firewall, with one compact preview-state note for when a later packet preserves thumbnail tiles, preview panes, same-tab previews, or partial/full preview shells around same-route detached derivatives, so the archive preserves that wrapper-added preview state honestly without quietly treating it as source-native frames, source-native default render state, settled content state, or the packet's governing member.
- `docs/628-*` — packet-open-with / open-in-app / browser-desktop-defaults + wrapper-launch-state firewall, with one compact launch-state note for when a later packet preserves "Open with" menus, "Open in app" choices, browser-versus-desktop preferences, default handlers, or auto-open posture around same-route detached derivatives, so the archive preserves that wrapper-added launch state honestly without quietly treating it as source-native format requirements, official route choice, canonical render environment, required software, or the packet's governing member.
- `docs/629-*` — packet-presence / avatars / cursors / participants + wrapper-participation-state firewall, with one compact participation-state note for when a later packet preserves collaborator avatars, anonymous-viewer chips, presence cursors, participant lists, or review-status badges around same-route detached derivatives, so the archive preserves that wrapper-added participation state honestly without quietly treating it as source authorship, official approval, current office attention, governing participation, or the packet's governing member.
- `docs/630-*` — packet-accounts / profiles / tenants + wrapper-account-state firewall, with one compact account-state note for when a later packet preserves signed-in account chips, profile switchers, personal-versus-business or work-or-school selections, tenant badges, or multi-account shells around same-route detached derivatives, so the archive preserves that wrapper-added account state honestly without quietly treating it as source ownership, official control, official affiliation, governing identity, or the packet's governing member.
- `docs/631-*` — packet-classification-labels / sensitivity-retention + wrapper-classification-state firewall, with one compact classification-state note for when a later packet preserves classification labels, sensitivity labels, retention labels, policy-tip recommendations, message-bar labels, or similar visible protection posture around same-route detached derivatives, so the archive preserves that wrapper-added classification state honestly without quietly treating it as source-native classification, official endorsement, legal handling duty, final retention posture, or the packet's governing member.
- `docs/632-*` — packet-suspicious-file-warnings / blocked-file-status / protected-view + wrapper-security-state firewall, with one compact security-state note for when a later packet preserves suspicious-file warnings, blocked-file markers, protected-view shells, read-only sandboxes, security dialogs, or similar visible warning/block posture around same-route detached derivatives, so the archive preserves that wrapper-added security state honestly without quietly treating it as source inauthenticity, official withdrawal, source-native danger classification, or the packet's governing member.
- `docs/633-*` — packet-signature-status / signer-certificates / eSignature-audit-trails + wrapper-signature-state firewall, with one compact signature-state note for when a later packet preserves signature lines, validation badges, signer-certificate details, eSignature status panels, audit-trail pages, certified-document markers, or similar visible signature posture around same-route detached derivatives, so the archive preserves that wrapper-added signature state honestly without quietly treating it as source-route official publication, source-route authorship, office adoption, legal finality, or the packet's governing member.
- `docs/634-*` — packet-approval-status / pending-approved-rejected + wrapper-workflow-state firewall, with one compact workflow-state note for when a later packet preserves submit-for-approval posture, pending/approved/rejected badges, approval sidebars, review-approvals controls, approved versions, or similar visible workflow disposition around same-route detached derivatives, so the archive preserves that wrapper-added workflow state honestly without quietly treating it as source-route official publication, source-route authorship, office adoption, legal finality, or the packet's governing member.
- `docs/635-*` — packet-download-print-copy-forward-edit-restrictions + wrapper-rights-state firewall, with one compact rights-state note for when a later packet preserves visible no-download, no-print, no-copy, no-forward, read-only, review-only, expiring-rights, or similar usage-restriction posture around same-route detached derivatives, so the archive preserves that wrapper-added rights state honestly without quietly treating it as source-route official publication, source-route authorship, office adoption, legal finality, or the packet's governing member.
- `docs/636-*` — packet-watermarks-confidentiality-overlays-viewer-email-burn-ins + wrapper-watermark-state firewall, with one compact watermark-state note for when a later packet preserves visible watermarks, confidentiality overlays, viewer-email burn-ins, playback-time watermark posture, or similar deterrence/ownership overlays around same-route detached derivatives, so the archive preserves that wrapper-added watermark state honestly without quietly treating it as source-route official publication, source-route authorship, source-native classification, office adoption, legal finality, or the packet's governing member.
- `docs/637-*` — packet-spelling-grammar-autocorrect-proofing-language + wrapper-proofing-state firewall, with one compact proofing-state note for when a later packet preserves visible spelling underlines, grammar marks, autocorrect replacements, proofing-language badges, dictionary-ignore posture, or similar proofing layers around same-route detached derivatives, so the archive preserves that wrapper-added proofing state honestly without quietly treating it as source-native error, source-native correction, official terminology rulings, source language, office adoption, or the packet's governing member.
- `docs/638-*` — packet-translated-renderings-show-original + wrapper-translation-state firewall, with one compact translation-state note for when a later packet preserves translated renderings, selected-text translation popups, show-original posture, language-pair badges, auto-translate indicators, or similar visible translation layers around same-route detached derivatives, so the archive preserves that wrapper-added translation state honestly without quietly treating it as a reviewed official translation, source-native language, office adoption, or the packet's governing member.
- `docs/639-*` — packet-reader-mode-simplified-views-immersive-reader + wrapper-reader-state firewall, with one compact reader-state note for when a later packet preserves Reader View, Reading mode, Show Reader, Immersive Reader, stripped-chrome posture, simplified article extraction, line-focus posture, or similar visible reader layers around same-route detached derivatives, so the archive preserves that wrapper-added reader state honestly without quietly treating it as source-native layout, source-native omission, office-curated simplification, or the packet's governing member.
- `docs/640-*` — packet-document-outlines-bookmarks-navigation-panes + wrapper-outline-state firewall, with one compact outline-state note for when a later packet preserves document outlines, bookmark panels, heading-navigation panes, table-of-contents sidebars, or similar visible structure maps around same-route detached derivatives, so the archive preserves that wrapper-added outline state honestly without quietly treating it as source-native hierarchy, source-native completeness, office-curated priority ordering, or the packet's governing member.
- `docs/641-*` — packet-transcript-panes-current-line-highlights-search + wrapper-transcript-state firewall, with one compact transcript-state note for when a later packet preserves transcript panes, current-line highlights, transcript search, transcript-language/timestamp toggles, return-to-current-time posture, or similar visible transcript layers around same-route detached derivatives, so the archive preserves that wrapper-added transcript state honestly without quietly treating it as a reviewed official transcript edition, source-native emphasis, source-native chronology, official translation, or the packet's governing member.
- `docs/642-*` — packet-auto-quality-data-saver-resolution-picks + wrapper-rendition-state firewall, with one compact rendition-state note for when a later packet preserves `Auto`, `Data saver`, visible resolution picks, quality-settings panes, embed-default quality posture, or similar fidelity selectors around same-route detached derivatives, so the archive preserves that wrapper-added rendition state honestly without quietly treating it as source-native blur, source-native unreadability, source-native omission of fine detail, official preferred fidelity, or the packet's governing member.
- `docs/643-*` — packet-cc-on-off-caption-language-appearance + wrapper-caption-state firewall, with one compact caption-state note for when a later packet preserves captions-on posture, captions-off state, selected caption language, auto-generated-caption inclusion, caption appearance customizations, default-on embed captions, caption-menu state, or similar visible caption layers around same-route detached derivatives, so the archive preserves that wrapper-added caption state honestly without quietly treating it as burned-in source text, a reviewed official translation, source-native line breaking or emphasis, source-native accessibility styling, or the packet's governing member.
- `docs/644-*` — packet-playback-rate-selections-accelerated-slowed-scan-posture + wrapper-playback-rate-state firewall, with one compact playback-rate-state note for when a later packet preserves visible `1.25x`, `1.5x`, `2x`, `0.8x`, temporary hold-to-scan posture, remembered speed defaults, speed-menu state, or similar playback-rate layers around same-route detached derivatives, so the archive preserves that wrapper-added playback-rate state honestly without quietly treating it as source-native brevity, source-native pacing, an officially summarized edition, office-preferred review tempo, or the packet's governing member.
- `docs/645-*` — packet-mute-volume-restored-audibility + wrapper-audio-output-state firewall, with one compact audio-output-state note for when a later packet preserves mute toggles, low-volume posture, restored audibility, visible volume-slider state, or similar audio-output layers around same-route detached derivatives, so the archive preserves that wrapper-added audibility state honestly without quietly treating it as source-native silence, source-native incompleteness, office-preferred audio redaction, an officially republished quiet edition, or the packet's governing member.
- `docs/646-*` — packet-fullscreen-theater-mode-miniplayer-picture-in-picture-popout + wrapper-player-state firewall, with one compact player-state note for when a later packet preserves fullscreen, theater mode, miniplayer, picture-in-picture, popout, or similar reduced-context player posture around same-route detached derivatives, so the archive preserves that wrapper-added player-state honestly without quietly treating it as source-native framing, source-native omission of surrounding route context, office-preferred presentation, an officially republished immersive edition, or the packet's governing member.
- `docs/647-*` — packet-audio-track-language-dub-audio-description-commentary + wrapper-audio-track-state firewall, with one compact audio-track-state note for when a later packet preserves original-audio selection, dubbed-language posture, automatic-dub selection, audio-description selection, commentary-track posture, or similar spoken-audio-track layers around same-route detached derivatives, so the archive preserves that wrapper-added spoken-track state honestly without quietly treating it as source-native language, a reviewed official translation, an officially adopted accessibility/commentary edition, or the packet's governing member.
- `docs/648-*` — packet-cast-target-AirPlay-mirroring-second-screen + wrapper-remote-playback-state firewall, with one compact remote-playback-state note for when a later packet preserves cast-target chips, AirPlay destination posture, screen mirroring, wireless-display projection, remote-playback-session indicators, or similar visible second-screen layers around same-route detached derivatives, so the archive preserves that wrapper-added remote-playback state honestly without quietly treating it as source-native viewing environment, official second-screen publication, office-preferred display context, or the packet's governing member.
- `docs/649-*` — packet-up-next-queue-autoplay-next-playlist-progression + wrapper-successor-state firewall, with one compact successor-state note for when a later packet preserves up-next rows, queue slots, autoplay-next countdowns, playlist-side next-item previews, showcase-next posture, TV-queue successor state, or similar visible next-object layers around same-route detached derivatives, so the archive preserves that wrapper-added successor-state honestly without quietly treating it as official continuation, official endorsement of the next object, source-native chronology, or the packet's governing member.
- `docs/650-*` — packet-chapter-markers-active-chapter-lists + wrapper-chapter-state firewall, with one compact chapter-state note for when a later packet preserves chapter markers, active chapter highlights, chapter-list panes, chapter-title previews, or similar visible chapter-state layers around same-route detached derivatives, so the archive preserves that wrapper-added chapter-state honestly without quietly treating it as source-native structure, an officially endorsed excerpt boundary, a governing quoted section, or the packet's governing member.
- `docs/651-*` — packet-loop-repeat-replay-cycling + wrapper-repeat-state firewall, with one compact repeat-state note for when a later packet preserves loop-on controls, repeat-one indicators, replay-after-end posture, continuous replay cycling, embed-loop settings, or similar visible repeat-state layers around same-route detached derivatives, so the archive preserves that wrapper-added repeat-state honestly without quietly treating it as source-native repetition, official continuous rebroadcast, office-preferred replay posture, source-native chronology, or the packet's governing member.
- `docs/544-*` — platform-media in-player moment-jump aliases + transcript/chapter picks / route-stability-retention discipline, with one compact player-navigation note for when a same-object chain stays current but playback jumps through transcript clicks, chapter picks, or other player-internal selections, so later summaries can preserve that moment-selection fact honestly without mistaking it for a new route, a new head, or an explicit offset alias.
- `docs/545-*` — platform-media text-track selection states + caption/subtitle-language picks / head-default-retention discipline, with one compact text-layer note for when a same-object chain stays current but captions/subtitles are toggled, a text-track language is selected, or an embed defaults a text track, so later summaries can preserve that visible-text-layer fact honestly without mistaking it for a new route, a reviewed translated edition, or the citation-safe current head.
- `docs/546-*` — platform-media player-view-state aliases + detached/immersive containers / source-page-default-retention discipline, with one compact player-container note for when a same-object chain stays current but the viewer enters fullscreen, theater mode, miniplayer, picture-in-picture, popout, or another player container state, so later summaries can preserve that framing fact honestly without mistaking it for a new route, a new head, or the citation-safe public default.
- `docs/547-*` — platform-media rendition-selection states + adaptive-quality picks / head-default-retention discipline, with one compact fidelity-state note for when a same-object chain stays current but playback runs in `Auto`, `Data saver`, a selected quality, or another rendition-selection state, so later summaries can preserve that detail-floor fact honestly without mistaking it for a new route, a reviewed edition, or the citation-safe current head.
- `docs/548-*` — platform-media playback-rate selection states + accelerated/slowed scan-posture / head-default-retention discipline, with one compact timing-state note for when a same-object chain stays current but playback runs at 1.25x, 1.5x, 2x, 0.8x, a temporary hold-to-scan posture, or another playback-rate state, so later summaries can preserve that timing/comprehension fact honestly without mistaking it for a new route, a reviewed edition, or the citation-safe current head.
- `docs/549-*` — platform-media audio-output selection states + mute-volume posture / head-default-retention discipline, with one compact audibility-state note for when a same-object chain stays current but playback is muted, effectively low-volume, or later restored to audible volume, so later summaries can preserve that practical-hearing fact honestly without mistaking it for a new route, a reviewed edition, or the citation-safe current head.
- `docs/550-*` — platform-media remote-playback target states + cast-controller splits / sender-default-retention discipline, with one compact second-screen note for when a same-object chain stays current but playback moves onto a cast target, AirPlay destination, mirrored display, or other remote screen/controller split, so later summaries can preserve that sender-target fact honestly without mistaking it for a new route, a new head, or the citation-safe current default.
- `docs/551-*` — platform-media successor-object handoffs + autoplay/queue progression / head-noninheritance discipline, with one compact cross-object note for when autoplay, queue order, playlist progression, or another play-next mechanic carries viewers into a different media object, so later summaries can preserve that transition honestly without appending it into the earlier same-object chain or letting the later object inherit the earlier head.
- `docs/552-*` — platform-media spoken-audio-track selection states + dubbed-language picks / head-default-retention discipline, with one compact heard-audio note for when a same-object chain stays current but the viewer hears original audio, a dubbed language, descriptive audio, commentary, or another selected spoken track, so later summaries can preserve that heard-layer fact honestly without mistaking it for a new route, a reviewed translated edition, or the citation-safe current head.
- `docs/553-*` — platform-media saved-shelf re-entry aliases + Watch Later/playlist/offline reopen / head-default-retention discipline, with one compact saved-media-reopen note for when a same-object chain comes back through Watch Later, a saved playlist entry, an offline library item, or another saved shelf, so later summaries can preserve that saved/offline return honestly without mistaking it for the citation-safe current head, a reviewed portable edition, or generic history memory.
- `docs/554-*` — platform-media metadata-wrapper drift + playlist-local relabeling / head-default-retention discipline, with one compact wrapper-state note for when a same-object chain stays current but a title, description, thumbnail, poster, or playlist-local display label changes around that same object, so later summaries can preserve that first-contact wrapper fact honestly without mistaking it for a new route, a reviewed edition, or the citation-safe current head.
- `docs/555-*` — platform-media collection-context aliases + playlist/showcase/list-view routes / source-object-default-retention discipline, with one compact collection-context note for when a same-object chain stays current but the same object is opened inside playlist/showcase/list-view context, so later summaries can preserve that collection-bearing shell honestly without mistaking it for a new route, a different object, or the citation-safe current head.
- `docs/556-*` — platform-media loop/repeat-retention states + same-object replay cycling / head-default-retention discipline, with one compact replay-cycle note for when a same-object chain stays current but the player loops, repeats, or restarts that same object after the endpoint, so later summaries can preserve that replay-cycle fact honestly without mistaking it for a new route, a fresher leg, or a successor-object handoff.
- `docs/557-*` — platform-media transcript-pane states + search focus / head-default-retention discipline, with one compact transcript-pane-state note for when a same-object chain stays current but the transcript pane is opened, searched, or left highlighting one line, so later summaries can preserve that transcript-foregrounding fact honestly without mistaking it for a new route, a reviewed text edition, or the citation-safe current head.
- `docs/558-*` — platform-media interaction-pane states + social-tab focus / head-default-retention discipline, with one compact interaction-pane-state note for when a same-object chain stays current but comments, live chat, Q&A, polls, or another interaction pane is merely opened, tab-switched, feed-switched, or left foregrounding one item, so later summaries can preserve that social-foregrounding fact honestly without mistaking it for a new route, a reviewed official answer, or the citation-safe current head.
- `docs/559-*` — platform-media live-position states + behind-live recovery / head-default-retention discipline, with one compact live-position-state note for when a same still-live object stays current but the viewer is paused live, behind live, recovered to live, or watching from an earlier shown-live point, so later summaries can preserve that live-position fact honestly without mistaking it for a fresher head, a new route, or the citation-safe current head.
- `docs/560-*` — platform-media next-item queue states + up-next foreground / head-default-retention discipline, with one compact pending-next note for when a same current media object still controls but a queue, up-next slot, TV queue, or playlist-side pending item is foregrounded beside it, so later summaries can preserve that staged-next fact honestly without mistaking the upcoming item for the current head, a completed successor handoff, or the citation-safe present default.
- `docs/561-*` — platform-media derivative-readiness states + processing lag / head-default-retention discipline, with one compact derivative-readiness note for when a same current media object already controls but higher qualities, captions/transcripts, chapter/key-moment layers, replay derivatives, AI-answer prerequisites, or other ordinary layers are still settling, so later summaries can preserve that half-ready or later-settled derivative fact honestly without mistaking it for a new route, a fresher head, or the citation-safe current edition.
- `docs/562-*` — platform-media AI-answer-pane states + summary focus / head-default-retention discipline, with one compact AI-pane-state note for when a same current media object already controls but an AI pane is merely open, a generated summary is foregrounded, a suggested question is selected, or an answer card is visible, so later summaries can preserve that generated-pane fact honestly without mistaking it for a new route, a reviewed official briefing, or the citation-safe current head; the doc now also declares one canonical header winner order for co-true AI-pane states and stays pane-state-only rather than duplicating prompt-origin or follow-up-thread semantics.
- `docs/563-*` — platform-media AI-question-thread states + follow-up carryover / prompt-history-minimization discipline, with one compact AI-thread-state note for when the same current media object and AI pane already exist but the visible answer is fresh, follow-up-conditioned, visibly reset, or materially tied to suggested-vs-typed prompt origin, so later summaries can preserve that conversational-state fact honestly without mistaking it for a new route, a reviewed official briefing, or a reason to retain long prompt histories.
- `docs/564-*` — platform-media AI-answer output-language states + translated-response-mode / head-default-retention discipline, with one compact AI-answer-language note for when the same current media object, AI pane, and AI thread already exist but the visible answer stays in the source language, appears in translated output, or mixes languages, so later summaries can preserve that linguistic rendering fact honestly without mistaking it for a new route, a reviewed multilingual office publication, or the citation-safe current head.
- `docs/565-*` — platform-media AI-answer grounding states + linked-moment-cue / head-default-retention discipline, with one compact AI-answer-grounding note for when the same current media object, AI pane, AI thread, and answer language already exist but the visible answer exposes linked grounding, weaker/nonlinked grounding, or no visible grounding, so later summaries can preserve that support-cue fact honestly without mistaking it for a reviewed citation lane, a new route, or the citation-safe current head.
- `docs/566-*` — platform-media AI-answer source-basis states + transcript-vs-web provenance / head-default-retention discipline, with one compact AI-answer-provenance note for when the same current media object, AI pane, AI thread, answer language, and grounding state already exist but the visible answer is documented as transcript-only, platform-and-web, or not clearly disclosed in basis, so later summaries can preserve that provenance fact honestly without mistaking it for a new authority object, a reviewed citation lane, or the citation-safe current head.
- `docs/567-*` — platform-media AI-answer outcome states + no-answer-fallthrough / head-default-retention discipline, with one compact AI-answer-outcome note for when the same current media object, AI pane, AI thread, answer language, grounding, and source-basis state already exist but one visible AI interaction returns a substantive answer, a scope-limited no-answer, a prerequisite-missing no-answer, or a retry/error no-answer state, so later summaries can preserve that answer-versus-no-answer fact honestly without mistaking it for a new route, a safer citation lane, or the citation-safe current head.
- `docs/568-*` — platform-media AI-answer qualification states + disclaimer-visibility / head-default-retention discipline, with one compact AI-answer-qualification note for when the same current media object, AI pane, AI thread, answer language, grounding, source-basis, and outcome state already exist but the visible answer also carries an informational-only warning, an inaccuracy warning, or an experimental/preview label, so later summaries can preserve that visible caution fact honestly without mistaking it for a reviewed office disclaimer, a new route, or the citation-safe current head.
- `docs/569-*` — platform-media AI-answer feedback states + helpfulness-votes/report-lane non-authority discipline, with one compact AI-answer-feedback note for when the same current media object, AI pane, AI thread, answer language, grounding, source-basis, outcome, and qualification state already exist but the visible answer also carries thumbs-up / thumbs-down controls, a visible feedback submission, or a legal/report lane, so later summaries can preserve that feedback/report fact honestly without mistaking it for endorsement, adjudication, live support, or the citation-safe current head.
- `docs/570-*` — platform-media AI-answer eligibility states + rollout-gating/captured-absence-scope discipline, with one compact AI-answer-eligibility note for when the same current media object already controls but the visible AI surface is present or absent only because of account scope, region/language limits, owner activation, plan/licensing, selective rollout, or client-environment requirements, so later summaries can preserve that capture-scoped exposure fact honestly without mistaking it for an object-wide route change or the citation-safe current head.
- `docs/571-*` — platform-media AI-interaction data-handling states + retention-windows/prompt-minimization discipline, with one compact AI-interaction-data-handling note for when the same current media object already controls but the platform also discloses how prompts/responses are stored, reviewed, retained, improved from, or excluded from model training, so later summaries can preserve that minimization/privacy fact honestly without preserving long prompts or treating privacy language like the citation-safe current head.
- `docs/572-*` — platform-media AI-answer input-sufficiency states + transcript-floors/content-fit discipline, with one compact AI-answer-input-sufficiency note for when the same current media object already controls and the AI surface may already be visible but the remaining ambiguity is whether the transcript/video cleared a published minimum length, word-count, or best-fit rule, so later summaries can preserve that floor/fit fact honestly without treating requirements copy like the citation-safe current head.
- `docs/573-*` — platform-media AI-answer governing-transcript states + original-transcript-precedence/displayed-translation noninheritance discipline, with one compact AI-answer-governing-transcript note for when the same current media object already controls but translated or alternate visible transcript variants coexist and the remaining ambiguity is which transcript variant actually governed the answer, so later summaries can preserve that precedence fact honestly without mistaking displayed translation, transcript-pane state, or answer-language mode for the citation-safe current head.
- `docs/574-*` — platform-media AI-answer in-video-basis states + scene/object/slide-scope discipline, with one compact AI-answer-in-video-basis note for when the same current media object already controls but the platform says the answer can use scenes, objects, slides, or other same-video material beyond transcript text, so later summaries can preserve that same-video-basis fact honestly without mistaking it for web augmentation or the citation-safe current head.
- `docs/575-*` — platform-media AI-answer transcript-language-alignment states + spoken-source-match discipline, with one compact AI-answer transcript-language-alignment note for when the same current media object already controls but the governing transcript language may match, mismatch, or be regenerated to match the spoken source, so later summaries can preserve that language-hygiene fact honestly without mistaking it for visible answer language, a reviewed translation lane, or the citation-safe current head.
- `docs/576-*` — platform-media AI-answer transcript-terminology-fidelity states + proper-name-repair discipline, with one compact AI-answer transcript-terminology-fidelity note for when the same current media object already controls but the governing transcript may still misrecognize names, acronyms, office titles, or domain terms, or later be repaired through bounded transcript correction or vocabulary help, so later summaries can preserve that term-fidelity fact honestly without mistaking it for transcript-language mismatch, a new head, or the citation-safe current control.
- `docs/577-*` — platform-media AI-question-scope states + current-video-bounds / related-content-allowance discipline, with one compact AI-question-scope note for when the same current media object already controls but the remaining ambiguity is whether the module was framed as about-this-video only, stay-on-topic around the video, or explicitly able to help with related content, so later summaries can preserve that topic-bounds posture honestly without mistaking it for source-basis drift, thread carryover, or a freestanding general-assistant lane.
- `docs/578-*` — platform-media AI-answer safety-control states + prompt/output filtering / sensitive-context-guardrail discipline, with one compact AI-answer safety-control note for when the same current media object already controls but the remaining ambiguity is what safety controls the product itself discloses — prompt filtering, sensitive-context blocking, offensive-output mitigation, bias/fairness controls, or no clearly disclosed controls — so later summaries can preserve that guardrail posture honestly without mistaking it for visible warning text, a report lane, or privacy-handling drift.
- `docs/579-*` — platform-media AI-answer task-mode states + prompt-guide-output-class discipline, with one compact AI-answer task-mode note for when the same current media object already controls but the remaining ambiguity is what output class the selected turn was producing — summary, notes/key information, action items/calls to action, outstanding issues, locate/timestamp help, recommendation, or ordinary Q&A — so later summaries can preserve that generated output-class posture honestly without mistaking it for pane state, reviewed minutes, or a task register.
- `docs/580-*` — platform-media AI-prompt-affordance states + suggested-question-inventory/non-agenda discipline, with one compact AI-prompt-affordance note for when the same current media object already controls but the remaining ambiguity is what prompt inventory the visible AI module offered — Prompt Guide categories, suggested prompts, pre-generated questions, or only a freeform ask box — so later summaries can preserve that guided-prompt posture honestly without mistaking it for pane state, actual prompt origin, selected task mode, or an official FAQ/public agenda.
- `docs/581-*` — platform-media AI-answer remediation-authority states + owner-admin-activation/transcript-repair dependence discipline, with one compact AI-answer remediation-authority note for when the same current media object already controls but the remaining ambiguity is who can actually enable or repair the same AI lane — owner/admin Ask AI toggles, editor/owner transcript generation or repair, viewer-must-contact-owner dependence, or no published self-service path — so later summaries can preserve that enablement/repair posture honestly without mistaking it for viewer gating, transcript-floor fit, language repair, or a live support/current-head lane.
- `docs/582-*` — platform-media AI-answer companion quickmap + composition-limits/anti-fragmentation firewall, with one compact maintainer map that gives higher-level docs `582`'s **top-line defaults** as a pair-level reference before another numbered AI-tail sibling is considered.

In every case, the modality is just a delivery layer over the same underlying voter-question family already captured in this document.

## Overlap rules (to keep the family from collapsing into one blob)

### `308` is a synthesis surface, not a substitute for every detailed rule page

`308` exists to answer: **which dates, windows, and deadline semantics control action right now?**
It SHOULD point outward to more detailed surfaces when needed.
It SHOULD NOT absorb the full semantics of:
- primary-ballot eligibility (`309`),
- ID requirements (`300`),
- same-day registration proof classes (`303`), or
- mail-ballot request methods (`304`), or
- mail-ballot return instructions (`311`), or
- ballot-measure explanatory materials and guide versions (`313`).

### `305` is the fallback/help directory, not the rulebook

`305` answers: **which office/help path is authoritative and reachable?**
It SHOULD help the voter recover when a more specific surface is missing, stale, or disputed.
It SHOULD NOT replace specific rule surfaces such as `300`, `303`, or `309`.

### `307` is the escalation lane, not the answer to every voter-information problem

`307` becomes authoritative when ordinary help has failed, rights are implicated, or the right escalation lane matters.
It SHOULD NOT be used as an excuse to avoid maintaining ordinary answer surfaces for locations, deadlines, or ballot status.

### `292` and `299` are different on purpose

- `292` answers: **what site/location did the jurisdiction designate?**
- `299` answers: **what was the live service state of that site or its replacement path at time `T`?**

Do not merge them. A correct directory with a wrong same-day service state still fails voters.

### `293` and `313` are adjacent but not interchangeable

- `293` answers: **what ballot style or sample ballot answer was in scope for this voter or address?**
- `313` answers: **what official explanatory guide, pamphlet text, fiscal-impact material, or statement bundle accompanied a measure, and which edition controlled at time `T`?**

Do not merge them. A jurisdiction can have an accurate sample ballot while the explanatory guide surface is stale, mistranslated, silently swapped, or broader than the voter’s actual ballot scope. The reverse can also happen.

### `293`, `313`, and `314` are adjacent but not interchangeable

- `293` answers: **what ballot style or sample-ballot answer was published for this voter or address?**
- `313` answers: **what explanatory guide, pamphlet, fiscal-impact text, or official statement package accompanied a measure, and which edition controlled at time `T`?**
- `314` answers: **did the candidate field for a race change, does stale public material still exist, and which superseding notice or replacement path now controls?**

Do not merge them. A jurisdiction can have an accurate sample-ballot lookup while the candidate list and correction notice about a withdrawn or replaced candidate are stale. It can also have a correct candidate-change notice while the older pamphlet or sample-ballot PDF remains in circulation and needs an explicit superseding explanation.

### `304`, `317`, `311`, `295`, and `296` are separate because the voter’s time horizon is different

- `304` = **before** the voter has the ballot in hand,
- `317` = **after issuance**, when the ballot is missing, spoiled, damaged, or only the return materials need replacement, but **before** the voter has completed a lawful return or committed to the final in-person fallback path,
- `311` = **after** the voter has a usable ballot in hand, but **before** the jurisdiction has spoken through the status/cure surface,
- `295` = **after** the voter has entered the mail-ballot return/status pipeline,
- `296` = **after** the voter has been shifted onto the provisional path.

Those are different public facts with different correction semantics.

### `321` and `296` are adjacent but not interchangeable

- `321` answers: **why the voter was asked to vote provisionally, what immediate instructions controlled that choice, and whether the ballot might be fully counted, partially counted, or rejected.**
- `296` answers: **what the official post-cast status/free-access surface later said happened to the provisional ballot.**

A jurisdiction can publish a correct status checker while still misdescribing the pre-cast issuance reasons or wrong-place consequences that drove the voter onto the provisional path. The reverse can also happen.

### `300`, `303`, `319`, and `321` are adjacent but not interchangeable

- `300` answers: **which ID documents or alternatives are accepted.**
- `303` answers: **which same-day or late-registration path still exists.**
- `319` answers: **what inactive or removed labels mean, and what restoration path applies.**
- `321` answers: **how those conditions translate into the immediate decision to issue a provisional ballot, and what the voter was told before casting it.**

A jurisdiction can publish accurate general ID, same-day-registration, or inactive-status guidance while still telling voters the wrong provisional-issuance consequence at the poll.

### `320` and `321` are adjacent but not interchangeable

- `320` answers: **whether the voter may use any site in scope, any vote center, an assigned subset, or one designated location for the phase.**
- `321` answers: **what the public surface said happens when the voter appears at a site or under conditions that trigger provisional voting, including whether going to the correct site remains the better path.**

A jurisdiction can publish the correct location-eligibility model while still failing to say what the provisional consequence is when a voter shows up at the wrong place. The reverse can also happen.

### `321`, `307`, and `343` are adjacent but not interchangeable

- `321` answers: **why the voter was being placed onto the provisional path, what immediate instructions controlled that choice, and what the provisional ballot might later count for.**
- `307` answers: **where the voter should report intimidation, rights violations, or other urgent failures safely.**
- `343` answers: **what the ordinary official challenge procedure itself said when a voter’s qualifications were challenged at the polls — who may challenge, what bases were allowed, whether an oath/affidavit or witness could preserve a regular ballot, and which fail-safe ballot path applied if not.**

Do not merge them. A jurisdiction can publish a correct provisional-ballot page while still failing to tell voters the immediate challenged-voter procedure that could keep them on a regular ballot. It can also publish a correct rights/escalation page while still leaving the ordinary challenge procedure unclear. The reverse can also happen.

### `295`, `296`, and `316` are adjacent but not interchangeable

- `295` answers: **what happened to my returned mail ballot, and what cure/help path exists right now?**
- `296` answers: **what happened to my provisional ballot, and why?**
- `316` answers: **does the official participation record now show that I voted in this election, and what correction/help path exists if it does not?**

Do not merge them. A jurisdiction can have an accurate live mail-ballot or provisional status surface while voter history is not yet posted, is temporarily unavailable during canvass, or is later corrected. It can also have a correct posted participation record while earlier ballot-status surfaces remain stale or have already aged out of their live-action role.

### `304`, `317`, and `311` are adjacent but not interchangeable

- `304` answers: **how do I request a mail ballot in the first place, and by what deadline?**
- `317` answers: **my ballot is lost, spoiled, damaged, never arrived, or missing a usable envelope; how do I get replacement materials or switch to another lawful voting path?**
- `311` answers: **I have a usable ballot in hand; exactly how do I return it correctly, and what deadline basis controls?**

Do not merge them. A jurisdiction can have a correct request page while its replacement-ballot or envelope-only rescue path is stale. It can also have a correct replacement/reissue page while the ordinary return instructions remain wrong, especially when office cutoffs, surrender rules, or provisional fallback semantics change late.

### `318`, `324`, `317`, and `337` are adjacent but not interchangeable

- `318` answers: **how does an ordinarily situated voter update name, address, or party information, by what method and deadline, and what late-change fallback applies?**
- `324` answers: **what residence and ballot-delivery rule applies when the voter lacks a fixed address or needs a nontraditional residence description?**
- `317` answers: **how does the voter replace a lost, spoiled, damaged, or never-received ballot packet after issuance?**
- `337` answers: **whether a voter displaced by disaster should keep the home address for districting, change only the mailing or delivery path, and use disaster-specific fallback when ordinary delivery or site access breaks.**

Do not merge them. A temporarily displaced voter can still have a fixed voting residence, can need more than a simple replacement packet, and can need disaster-specific instructions that are neither ordinary move/update guidance nor the homelessness/no-fixed-address rule.

### `309` and `312` are adjacent but not interchangeable

- `309` answers: **which standing primary model applies, and how do party affiliation or declaration rules usually control ballot eligibility?**
- `312` answers: **for a runoff or special election, what district scope and carry-forward participation semantics controlled action right now?**

Do not merge them. A jurisdiction can have accurate standing primary rules and still mislead voters about a partial-district special election or a party-specific runoff constraint.

### `311` and `298` are adjacent but not interchangeable

- `311` answers: **what return instructions, envelope steps, and deadline semantics controlled the voter’s act of return?**
- `298` answers: **which official drop-box locations existed, where, and during which availability windows?**

A perfect drop-box directory can still fail voters if the packet insert or website says the wrong envelope or deadline rule. A perfect return-instructions page can still fail voters if the drop-box directory is stale.

### `294`, `319`, and `323` are adjacent but not interchangeable

- `294` answers: **what does the registration-status surface currently say?**
- `319` answers: **what do inactive or removed labels mean inside the registration system, and how does the voter become active again?**
- `323` answers: **whether conviction-related rules still control eligibility or restoration before the ordinary registration-status semantics even apply.**

A jurisdiction can have a correct status checker and inactive-voter explanation while still giving the wrong public answer about whether a person with a conviction is eligible to register or vote. The reverse can also happen.

### `318` and `323` are adjacent but not interchangeable

- `318` answers: **how does an already-eligible voter update name, address, or party information?**
- `323` answers: **whether the voter is eligible after a conviction, whether rights restored automatically or only after additional steps, and whether re-registration is required.**

A correct update page does not answer whether the voter is legally eligible yet. A correct conviction-restoration page does not replace the ordinary update rules once the voter is eligible again.

### `294` and `303` are adjacent but not interchangeable

- `294` answers: **what does the registration/status surface currently say about me or my record?**
- `303` answers: **what official late-registration/update path still exists if ordinary registration timing has already failed?**

A jurisdiction can have a correct registration-status checker and still fail same-day-registration guidance, or vice versa.

### `294`, `300`, `303`, and `338` are adjacent but not interchangeable

- `294` answers: **what does the registration/status surface currently say about me or my voter record right now?**
- `300` answers: **which voter-identification documents or alternatives are accepted when voting.**
- `303` answers: **what same-day or late-registration path still exists generally when ordinary timing has already failed.**
- `338` answers: **whether a newly naturalized person may register now, whether pre-naturalization registration is forbidden, whether a special post-naturalization exception or same-day path controls, and what proof or in-person rule applies close to the election.**

Do not merge them. A jurisdiction can have a correct status checker, correct voter-ID page, and correct general same-day-registration page while still failing to tell a new citizen when the person first becomes eligible, whether a late-naturalization exception exists, or what certificate/proof must be shown. The reverse can also happen: a jurisdiction can publish good new-citizen guidance while ordinary status, voter-ID, or same-day-registration pages lag.

### `294`, `303`, `309`, and `340` are adjacent but not interchangeable

- `294` answers: **what does the registration/status surface currently say about me or my voter record right now?**
- `303` answers: **what same-day or late-registration path still exists generally when ordinary timing has already failed.**
- `309` answers: **which primary participation model and party-affiliation rule control ballot access.**
- `340` answers: **when a young voter may pre-register or register before 18, when that record becomes active, and whether a 17-year-old may vote in a primary because the general-election age threshold will be met in time.**

Do not merge them. A jurisdiction can have a correct status checker, correct same-day-registration page, and correct primary-party rules while still failing to tell a 16- or 17-year-old when the person may first enter the system, whether the record is merely future/pending, or whether age alone permits primary participation before the 18th birthday. The reverse can also happen.

### `301`, `302`, `307`, and `341` are adjacent but not interchangeable

- `301` answers: **which accessible voting accommodations, alternate formats, or alternate in-person paths exist generally.**
- `302` answers: **which translated materials, language hotlines, or language-access resources exist generally.**
- `307` answers: **where a voter should report a problem or escalate a rights issue safely.**
- `341` answers: **who may personally assist or interpret for a voter, what oath or form applies, and which restricted-helper rules bar a specific assistant.**

Do not merge them. A jurisdiction can publish correct accessibility options, correct translated-materials guidance, and a correct escalation page while still failing to tell a voter whether a specific helper or interpreter may assist right now, whether that person must sign an oath, or whether an employer/union restriction bars the helper. The reverse can also happen.

### `311`, `317`, `322`, `327`, `341`, and `342` are adjacent but not interchangeable

- `311` answers: **which return methods, envelope requirements, and deadline semantics control once the voter already has a usable ballot.**
- `317` answers: **how the voter gets a replacement or switches paths after spoilage, loss, damage, or nonreceipt.**
- `322` answers: **which emergency absentee or representative-delivery path still exists after a late emergency or hospitalization breaks the ordinary timeline.**
- `327` answers: **which long-term-care or facility-assisted workflow controls for residents of those institutions.**
- `341` answers: **who may personally assist or interpret for the voter and what oath or form applies to that personal assistance.**
- `342` answers: **whether another person may transport, deposit, or return ballot materials for the voter, and what authorization or restricted-helper rule controls that handoff.**

Do not merge them. A jurisdiction can publish correct ordinary return instructions, replacement-ballot rules, emergency representative procedures, facility workflows, and personal-assistance rules while still failing to tell a voter or helper whether another person may lawfully pick up, carry, drop off, or mail the ballot and what authorization section or separate agent/bearer form must be completed. The reverse can also happen.

### `301`, `311`, `295`, and `339` are adjacent but not interchangeable

- `301` answers: **which accessible voting accommodations, alternate in-person methods, or assistance options are offered generally.**
- `311` answers: **which post-issuance ballot-return instructions, envelope steps, and deadline semantics control.**
- `295` answers: **what the post-return ballot-status or cure surface says after a ballot is flagged.**
- `339` answers: **what substitute counts when the voter cannot provide an ordinary handwritten signature, whether witness/stamp/typed-digital options exist, and how the voter updates or cures the signature record.**

Do not merge them. A jurisdiction can publish correct accessibility guidance, correct return instructions, and correct post-return cure/status notices while still failing to tell a voter who cannot sign ordinarily what substitute counts on which step, whether a witness or assistant is required, or how to update the signature record safely. The reverse can also happen.

### `294`, `303`, and `318` are adjacent but not interchangeable

- `294` answers: **what does the registration/status surface currently say about me or my voter record right now?**
- `303` answers: **what same-day or late-registration/update path still exists when ordinary timing has already failed and the jurisdiction offers that path?**
- `318` answers: **how do I update an existing voter record, by which method and deadline, and what moved-close-to-election or other late-change fallback controls if I missed the ordinary path?**

Do not merge them. A jurisdiction can have a correct registration-status checker while publishing the wrong ordinary update deadline or the wrong late-move fallback instruction. It can also have a correct update page while the same-day-registration surface is stale or while the current status checker has not yet caught up.

### `309` and `318` are adjacent but not interchangeable

- `309` answers: **which primary model applies, and how do party affiliation or declaration rules control ballot eligibility?**
- `318` answers: **how does a voter change party affiliation, name, or address on the record, by what cutover date, and which late-change semantics apply?**

Do not merge them. Party-affiliation rules can remain accurate while the update path or party-change deadline is stale, and the reverse can also happen.

### `315` and `318` are adjacent but not interchangeable

- `315` answers: **which precinct, districts, and jurisdiction currently apply according to the public assignment surface?**
- `318` answers: **how should the voter change the record after moving or changing identifying information, and how will the public know when the update should propagate?**

A jurisdiction can publish a correct current assignment while the update path that should change future assignment is stale, and it can publish a current update path while downstream assignment surfaces lag or contradict it.

### `315`, `318`, and `324` are adjacent but not interchangeable

- `315` answers: **which precinct, districts, and jurisdiction currently apply according to the public assignment surface?**
- `318` answers: **how does an already-locatable voter ordinarily update name, address, or party information?**
- `324` answers: **what counts as voting residence or mailing address when the voter lacks a fixed address, and what ballot-delivery fallback applies?**

A jurisdiction can have a correct current assignment lookup and ordinary update page while still failing to tell voters without a fixed address what residence description to use or how to receive voting materials. The reverse can also happen: a special-circumstances page can be correct while the downstream assignment or ordinary update surfaces lag.

### `318`, `324`, and `325` are adjacent but not interchangeable

- `318` answers: **how does an ordinarily registered voter update name, address, or party information?**
- `324` answers: **what counts as voting residence or mailing address when the voter lacks a fixed address, and what ballot-delivery fallback applies?**
- `325` answers: **how does a voter protect a real residence or identity detail from public exposure, and which confidential-registration or protected ballot path applies instead of the ordinary one?**

A jurisdiction can publish an accurate ordinary update page and an accurate no-fixed-address page while still failing to tell a threatened voter how to register or vote without exposing a real residence. The reverse can also happen: a confidentiality-program page can be correct while ordinary update or no-fixed-address pages lag or contradict the safe routing instructions.

### `323`, `304`, `311`, and `326` are adjacent but not interchangeable

- `323` answers: **does conviction status still block eligibility or require restoration before any ordinary voter path applies?**
- `304` answers: **how does an ordinary voter request a mail ballot, and by what deadline?**
- `311` answers: **once the voter has a usable ballot in hand, how is it returned correctly and under which deadline semantics?**
- `326` answers: **for an otherwise eligible voter in jail, detention, or civil commitment, which address, request lane, facility handoff, and release-from-custody fallback control the custody-specific ballot path?**

A jurisdiction can publish a correct conviction-restoration page, ordinary request page, and ordinary return page while still failing to tell an eligible person in custody how to register, where the ballot should be sent, or how facility staff fit into the handoff chain. The reverse can also happen: a jail-voting guide can be correct while the conviction-eligibility or ordinary absentee surfaces lag.

### `324`, `325`, `326`, and `327` are adjacent but not interchangeable

- `324` answers: **what counts as voting residence or mailing address when the voter lacks a fixed address, and what ballot-delivery fallback applies?**
- `325` answers: **how does a voter protect a real residence or identity detail from public exposure, and which confidential-registration or protected ballot path applies instead of the ordinary one?**
- `326` answers: **how does an otherwise eligible voter act from custody when the facility may receive ballots, may not count as residence, and may impose a distinct handoff or release-transition workflow?**
- `327` answers: **for a voter living in a long-term-care or similar residential facility, which residence/proof rule, deputized or supervised assistance model, and ballot-handling workflow control the public answer?**

A jurisdiction can publish accurate homelessness, protected-address, and custody guidance while still failing to tell a long-term-care or assisted-living resident whether staff may vouch, whether deputies or a supervised team will visit, or whether ordinary absentee rules are enough. The reverse can also happen: a facility-voting handout can be current while homelessness, protected-address, or in-custody routing is stale.

### `300`, `324`, `292`, `320`, and `336` are adjacent but not interchangeable

- `300` answers: **which ID documents or alternatives are generally accepted once the voter is already on the ordinary path.**
- `324` answers: **what residence and ballot-delivery rule applies when the voter lacks a fixed address.**
- `292` answers: **what polling-place or voting-site directory entry was published.**
- `320` answers: **whether the voter may use any site, a vote center, or one assigned location.**
- `336` answers: **whether tribal IDs, reservation or nontraditional addresses, tribal-government buildings, or reservation-specific access routes change the public answer for a tribal-community voter.**

A jurisdiction can publish a correct general ID list, no-fixed-address rule, or ordinary location directory while still leaving tribal/reservation voters to infer whether tribal documents count, how a reservation address is handled, whether a tribal-government building may receive ballot mail, or whether an on-reservation equivalent service site exists. The reverse can also happen.

### `303`, `304`, `318`, and `328` are adjacent but not interchangeable

- `303` answers: **how does same-day registration work at the late window, and what proof classes are accepted there?**
- `304` answers: **how does an ordinary voter request a mail ballot, and by what deadline?**
- `318` answers: **how does an ordinarily registered voter update address, name, or party information?**
- `328` answers: **for a college or university student, which campus-versus-home residence choice controls, does student housing count as residence, what campus proof or mailing rule applies, and when is absentee voting from the other address the right lawful path?**

A jurisdiction can publish correct same-day registration, ordinary absentee, and ordinary update pages while still failing to tell a student whether to register locally at campus, remain registered at home, or what campus-housing document proves residence. The reverse can also happen: a student-voting page can be current while the ordinary same-day, absentee, or update surfaces lag or contradict it.

### `294` and `315` are adjacent but not interchangeable

- `294` answers: **what does the registration/status surface currently say about me or my voter record?**
- `315` answers: **which precinct, districts, and local election jurisdiction did the public assignment surface say applied to me or this address?**

A jurisdiction can show that a voter is registered while still publishing the wrong precinct or district assignment, or vice versa.

### `292`, `293`, `312`, and `315` are adjacent but not interchangeable

- `292` answers: **where is the voter supposed to go?**
- `293` answers: **what ballot style or sample-ballot answer was published?**
- `312` answers: **whether a runoff or special election exists for the voter's district and which carry-forward rules matter.**
- `315` answers: **which precinct, districts, and jurisdiction the official assignment surface said applied in the first place.**

A correct assignment answer can still coexist with a stale polling-place page, stale sample ballot, or stale special-election scope page. The reverse can also happen.


### `294` and `319` are adjacent but not interchangeable

- `294` answers: **what does the registration/status surface currently say about me or my voter record?**
- `319` answers: **what do inactive or removed labels mean, can I still vote, and how do I become active again or restore the record?**

A status checker can correctly display “inactive” while the public explanation of what that means, or what reactivation path controls, is stale or contradictory. The reverse can also happen.

### `318` and `319` are adjacent but not interchangeable

- `318` answers: **how does a voter ordinarily update name/address/party information, by what method and deadline, and what late-change fallback applies?**
- `319` answers: **how does a voter recover from inactive or removed status, and when is a fresh registration required instead of an ordinary update?**

Do not merge them. An ordinary update page can be correct while the inactive/reactivation page is wrong, and an inactive/reactivation page can be correct while the ordinary update page still points voters to the wrong action.

### `300`, `296`, and `319` are adjacent but not interchangeable

- `300` answers: **which identification documents or alternatives are accepted?**
- `296` answers: **what happened to a provisional ballot and why?**
- `319` answers: **which ballot path or affirmation step applies because of the voter's inactive or removed status?**

A jurisdiction can have correct ID and provisional pages while the public inactive-voter explanation is wrong about whether the voter should expect a regular, challenged, or provisional ballot. The reverse can also happen.

### `292`, `297`, `315`, and `320` are adjacent but not interchangeable

- `292` answers: **which site or sites did the jurisdiction designate?**
- `297` answers: **when are early-voting sites open?**
- `315` answers: **which precinct, districts, and jurisdiction currently apply according to the public assignment surface?**
- `320` answers: **whether the voter may use any countywide site, any vote center, an assigned subset, or one designated site for the current phase.**

A jurisdiction can have a correct site list, correct hours, and correct precinct assignment while still failing to say whether the voter may lawfully use any site in scope or only one assigned location. The reverse can also happen.

## Promotion test for any future voter-facing surface

Before promoting a new `31x`-style voter-facing public-answer surface, maintainers SHOULD require a strong “yes” to all of these:

1. **Distinct action question:** does this answer a voter question that changes next action in a way not already covered?
2. **Distinct correction semantics:** would silent edits or contradictory official answers create a dispute that is materially different from adjacent surfaces?
3. **Distinct payload shape:** can the answer be represented by a small, coherent payload rather than by stuffing extra fields into `305`, `307`, or `308`?
4. **Distinct checklist:** can an operator actually run a short checklist for this surface?
5. **Authoritative public channel reality:** do official state/local election channels commonly publish this as a separate public answer surface in practice?
6. **Anti-bloat discipline:** will adding this surface reduce confusion more than it increases archive sprawl?

If the answer to any of these is “no,” prefer one of the following instead:
- expand an adjacent doc’s **overlap rules** section,
- add a row or note to `artifacts/tables/voter-facing-public-answer-surfaces.csv`,
- tighten the duplicate-firewall or registry wiring in `docs/329-voter-facing-public-answer-surface-registry-and-duplicate-firewall.md`,
- add a template/checklist refinement to an existing surface,
- tighten the special-case authority minimums in `docs/331-special-case-voter-facing-surfaces-subfamily-and-authority-anchor-minimums.md` when the proposal is really an edge-case `317–328 / 335–343`-style surface,
- or log the idea in `docs/207-research-agenda-and-revision-ledger.md` until a better boundary emerges.

## Current bounded queue (not yet promoted)

At this revision, the stronger near-term queue items should still remain unpromoted unless repeated official-publication patterns justify a distinct boundary. In particular, avoid promoting generic “candidate list,” “who can vote,” or “ballot tracking plus everything else” surfaces unless they clear the overlap test above.

The challenged-voter / challenge-form / challenge-oath crossover has now been promoted into `343` because current official-public sources repeatedly present it as a distinct voter-facing answer boundary rather than a mere sub-bullet of `321` or `307`. Use `343` for ordinary challenge-procedure capture; use `321` for provisional-ballot issuance semantics; use `307` when the problem crosses into intimidation, rights harm, or urgent escalation.

## Minimal archive artifact

Maintain the compact family registry at:
- `artifacts/tables/voter-facing-public-answer-surfaces.csv`
- `docs/329-voter-facing-public-answer-surface-registry-and-duplicate-firewall.md`
- `docs/330-voter-facing-public-answer-surface-triplet-coherence-and-orphan-control.md`
- `docs/331-special-case-voter-facing-surfaces-subfamily-and-authority-anchor-minimums.md`
- `docs/332-special-case-voter-facing-surface-nonoverlap-declarations-and-misrouting-firewall.md`
- `docs/333-special-case-voter-facing-surface-safe-fallback-and-escalation-boundaries.md`
- `docs/334-special-case-voter-facing-surface-temporal-volatility-freshness-and-no-cross-jurisdiction-inference.md`
- `docs/355-special-case-voter-facing-surface-control-stack-reference-closure-and-navigation-firewall.md`
- `docs/366-official-voter-information-broadcast-alerts-social-posts-and-linkback-discipline.md`
- `docs/369-official-voter-information-videos-livestreams-and-clip-context-discipline.md`
- `docs/370-official-voter-information-emails-newsletters-reminders-and-forward-context-discipline.md`
- `docs/371-official-voter-information-community-partner-distribution-co-branding-and-relay-boundary-discipline.md`
- `docs/372-official-voter-information-site-signage-wayfinding-and-stale-posting-removal-discipline.md`
- `docs/373-official-voter-information-forms-applications-affidavits-and-version-acceptance-discipline.md`
- `docs/382-official-voter-information-search-result-presentation-title-links-snippets-and-canonical-discipline.md`
- `docs/383-official-voter-information-social-profiles-bio-links-and-pinned-post-discipline.md`
- `docs/384-official-voter-information-mobile-apps-app-store-listings-and-download-boundary-discipline.md`
- `docs/385-official-voter-information-platform-place-cards-office-listings-and-hours-contact-discipline.md`
- `docs/386-official-voter-information-off-platform-ai-answer-surfaces-citation-handoff-and-authority-boundary-discipline.md`
- `docs/387-official-voter-information-voice-search-voice-assistant-answers-and-spoken-handoff-discipline.md`
- `docs/388-official-voter-information-shared-link-previews-unfurls-and-preview-cache-discipline.md`
- `docs/389-official-voter-information-calendar-subscriptions-ics-downloads-and-reminder-handoff-discipline.md`
- `docs/390-official-voter-information-public-apis-data-feeds-and-widget-consumption-discipline.md`
- `docs/391-official-voter-information-crawlability-indexability-canonical-discovery-and-sitemap-discipline.md`
- `docs/392-official-voter-information-organization-structured-data-site-names-favicons-and-entity-identity-discipline.md`
- `docs/393-official-voter-information-breadcrumb-faq-and-search-appearance-structured-data-discipline.md`
- `docs/394-official-voter-information-search-removals-noindex-and-recrawl-discipline.md`
- `docs/395-official-voter-information-snippet-preview-controls-and-ai-excerpt-discipline.md`
- `docs/396-*` — visible freshness labels, structured date cues, timezone-aware update precision, page-versus-event date separation, and archive posture so official voter-information pages look current for the right reason instead of because of ambiguous date signals.
- `docs/397-official-voter-information-alternate-language-discovery-hreflang-x-default-and-locale-adaptive-crawl-discipline.md`
- `docs/398-official-voter-information-site-moves-domain-migrations-gov-transitions-and-hostname-continuity-discipline.md`
- `docs/399-*` — Search Console property-scope coverage, verified-owner continuity, stale-token retirement, migration verification survival, and emergency search-side recovery operability so the office is not locked out when public search recovery is needed.
- `docs/400-*` — critical query/page cluster monitoring, page/country/device/search-appearance triage, preliminary-data windows, anomaly checks, and AI-feature measurement discipline so discoverability loss is separated from reporting artifacts.
- `docs/401-*` — page-level indexed-vs-live-state separation, canonical diagnosis, Googlebot-visible render/preview-control checks, and request-indexing operability so narrow current-page failures can be diagnosed before broader content churn.
- `docs/402-*` — critical-page performance budgets, mobile-first review, field-vs-preflight separation, hydration/fallback boundaries, and release-governance so current official pages remain usable before deadline-sensitive actions fail.
- `docs/403-*` — answer-first progressive-enhancement review, crawlable critical routing, widget-optional boundaries, and degraded-client recovery so current official answers do not disappear behind script-only shells.
- `docs/404-*` — mutable-answer cache classification, revalidation-first posture, service-worker navigation/update control, and stale-answer eviction/rollback so current official pages do not keep replaying an obsolete client-side state.
- `docs/405-*` — anti-bot challenge-scope separation, accessible CAPTCHA fallback/help recovery, wanted-crawler verification/allow posture, and non-`200` temporary interstitial discipline so current official pages do not disappear behind challenge walls.
- `docs/406-*` — request-context variant inventory, explicit-vs-ambient boundary discipline, no-cookie authoritative-first-contact posture, and experiment/personalization limits so the same official URL does not quietly tell different voters different things.
- `docs/409-*` — anonymous-public-read classification, auth-required route separation, visible no-auth explanation/help recovery, and session-expiry / re-authentication continuity so current official pages do not quietly turn into account walls.
- `docs/407-*` — HTTPS-only critical-route posture, certificate/HSTS review, mixed-content zero tolerance, and unsafe-page recovery/help discipline so current official pages do not train voters to bypass browser warnings.
- `docs/408-*` — temporary-unavailable posture, queue/waitroom quality, client-vs-sitewide throttling distinction, and lightweight help-rich degraded-answer continuity so current official pages do not disappear behind opaque overload states.
- `docs/410-*` — first-party core-answer preservation, non-primary embed boundaries, tag-manager/vendor-scope review, and blocked/slow external-origin fail-open recovery so current official pages do not become “wait for the vendor widget” shells.
- `docs/411-*` — optional-consent boundary discipline, bounded/dismissible administrative first-load overlays, focus/mobile non-obscuration review, and overlay-component fail-open recovery so current official pages do not make a policy wall the price of reading the answer.
- `docs/412-*` — user-initiated browser/device permission timing, no-capability-required public read, visible manual fallbacks, notification opt-in separation, and denied/unsupported fail-open recovery so current official pages do not make a browser prompt the price of reading the answer.
- `docs/413-*` — intentional outbound handoff labeling, direct-destination discipline, real-link-vs-fake-trigger boundaries, new-tab/popup/application-launch notice, and first-party recovery so current official pages do not strand voters behind opaque off-site jumps.
- EAC: Register and Vote in Your State (xref: `eac_register_and_vote_in_your_state_page`)
- EAC: Best Practices: FAQs for Election Officials (xref: `eac_best_practices_faqs_election_officials_page`)
- NASS: Can I Vote (xref: `nass_can_i_vote_page`)
- NASS: #TrustedInfo2026 (xref: `nass_trustedinfo_2026_page`)

## Family registry companion

`docs/329-*` and `docs/330-*` are the maintenance companions to this family map.
Use `310` to decide whether a surface is conceptually distinct; use `329` to make sure the family registry and anti-duplicate logic stay coherent; use `330` to make sure the accepted surface exists as a fully wired doc/template/checklist triplet with no orphan residue.
