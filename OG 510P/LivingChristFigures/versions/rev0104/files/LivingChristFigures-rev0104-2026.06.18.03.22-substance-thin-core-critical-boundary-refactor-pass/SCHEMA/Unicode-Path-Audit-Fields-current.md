# Unicode Path Audit Fields current

Field schema for the matching current table.

| field | required | allowed_values_or_pattern | meaning |
|---|---|---|---|
| `path_audit_id` | yes | ^unicode_path_[0-9]{3}$ | Stable audit row identifier. |
| `check` | yes | controlled check name | Name of the path-safety check. |
| `severity` | yes | info/medium/high | Finding severity. |
| `status` | yes | pass/review/fail | Check result. |
| `observed_count` | yes | integer | Count of affected paths or observations. |
| `affected_paths` | no | pipe-delimited package-relative paths | Representative affected paths for non-pass or inventory rows. |
| `detail` | yes | free text | Explanation of the check and result. |
