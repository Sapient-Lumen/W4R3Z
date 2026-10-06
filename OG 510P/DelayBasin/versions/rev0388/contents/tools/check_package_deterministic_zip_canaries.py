from package_preflight_lib import package_determinism_canary_results

results = package_determinism_canary_results()
failures = [row for row in results if row.get("status") != "pass"]
if failures:
    preview = "; ".join(f"{row['id']}: {row.get('observed')!r}" for row in failures[:3])
    raise SystemExit("package deterministic zip canary failure: " + preview)
print(f"check_package_deterministic_zip_canaries: OK ({len(results)} writer canaries)")
