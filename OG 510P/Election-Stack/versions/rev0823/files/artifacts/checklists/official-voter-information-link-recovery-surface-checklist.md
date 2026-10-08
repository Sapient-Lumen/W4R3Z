# Official voter-information link-recovery surface checklist

- Inventory stale public entrypoints voters may still use: old bookmarks, shared links, printed shortlinks, QR destinations, search-engine results, old PDFs/file URLs, and prior-cycle campaign or help pages.
- Make the recovery role explicit: redirects, expired-page notices, and 404/help pages recover the voter to the current official destination; they do not become hidden rule sources by themselves.
- Decide per stale path whether it should stay current, recover through a scoped redirect, resolve through an explicit expired-page tombstone or superseding notice, or land on a help-rich not-found / unavailable recovery page.
- Use a moved-path recovery only when the old and new targets still represent the same practical voter question and scope.
- Do not redirect every stale deep link to the site homepage as a substitute for scoped recovery.
- Do not silently remap one election's stale page into a different election's answer without explicit expired-state context.
- Keep a current official help path visible on recovery pages, including search/help links and office-contact fallback where one exists.
- Keep expired-page or superseding notices explicit when a prior election page or file no longer controls.
- Recover retired file URLs to a current wrapper, current file, or explicit superseding notice rather than a dead download.
- Keep link-recovery behavior aligned with the current office/help route, FAQ/help entries, search layer, router layer, and file-delivery layer.
- Use a small result-state taxonomy so current, moved, expired, and missing/unavailable states stay distinguishable.
- Preserve a bounded link-recovery trace for action-changing stale-link states, including policy version, requested path or path class, status family, result-state class, target/help route, and timestamp.
- Do not retain detailed per-user stale-link click histories longer than the published policy requires.
- Re-check recovery behavior after election-cycle rollover, FAQ restructures, redesigns, file removals, CMS migrations, vanity-link changes, or superseding notices.
- When material recovery behavior changes, publish an explicit updated state instead of relying only on silent config edits.
