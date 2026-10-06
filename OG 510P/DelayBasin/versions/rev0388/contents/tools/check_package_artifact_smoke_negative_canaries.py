from package_preflight_lib import package_artifact_negative_canary_results

results = package_artifact_negative_canary_results()
failures = [row for row in results if row.get("status") != "pass"]
if failures:
    preview = "; ".join(f"{row['id']}: {row.get('observed_failure')!r}" for row in failures[:3])
    raise SystemExit("package artifact smoke negative canary failure: " + preview)
print(f"check_package_artifact_smoke_negative_canaries: OK ({len(results)} mutation canaries)")
