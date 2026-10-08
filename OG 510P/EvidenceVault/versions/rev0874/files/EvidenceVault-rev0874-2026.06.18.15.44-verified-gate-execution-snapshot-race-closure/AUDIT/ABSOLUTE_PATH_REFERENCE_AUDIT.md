# Absolute path reference audit

This audit inventories cloud/container absolute paths embedded inside text payloads. It complements filesystem path validation: the shipped file names can be safe while the file contents still contain stale `/mnt/data/...` or `/home/oai/...` references.

- Status: `no_cloud_container_absolute_paths_found`
- UTF-8 text files scanned: **4229**
- Files with cloud/container absolute path references: **0**
- Total matching references: **0**
- Families/areas with references: **0**

## By family/area

| Family/area | Files | References |
| --- | ---: | ---: |

## Highest-impact interpretation

These references are not necessarily secrets and do not prove data loss. They do prove that some evidence payloads still carry build-host coordinates. For portability, replay, and publication, normalize references to shipped relative paths when the target exists in the archive; otherwise keep an explicit historical-external-path ledger so readers know the path is provenance context rather than an expected local file.

## Files with references

| Path | Matches | Unique | Sample |
| --- | ---: | ---: | --- |
