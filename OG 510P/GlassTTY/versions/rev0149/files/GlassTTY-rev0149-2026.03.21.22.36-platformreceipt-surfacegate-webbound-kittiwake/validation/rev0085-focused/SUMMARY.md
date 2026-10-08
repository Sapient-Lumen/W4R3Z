# rev0085 focused validation

- baseline: `GlassTTY-rev0084-2026.03.17.08.51-playwrightmarker-stalesurvival-cacheproof-lapwing.zip`
- focus: preserve raw versus prepared Playwright cache truth so foreign-only retained installs and current-package link gaps stay visible instead of being silently healed
- targeted pytest: passed individually (`test_playwright_install_list_raw_reports_missing_links_without_mutating_cache`, `test_audit_playwright_cache_reports_foreign_only_current_link_gap`, `test_plan_playwright_cache_repair_reports_current_link_gap`, `test_repair_playwright_cache_aligns_shadow_install_and_prunes_broken_link`, `test_repair_playwright_cache_writes_missing_installation_marker`, `test_install_archive_registers_cache_for_raw_playwright_install_list`, `test_doctor_script_reports_manifest_and_wrapper`, `test_doctor_script_reports_profile_launch_metadata`)
- extension typecheck/build: passed
- real temp-root proof: raw `playwright install --list` can now be recorded without mutating the cache, and a foreign-owner cache root remains visibly foreign-owned until prepared mode or repair explicitly links the current Playwright package
- packaged zip verification: PASS (`verify-package.json`)
- honest gap: still no live Chromium/native-host/browser round-trip or successful online Playwright browser download in this container
