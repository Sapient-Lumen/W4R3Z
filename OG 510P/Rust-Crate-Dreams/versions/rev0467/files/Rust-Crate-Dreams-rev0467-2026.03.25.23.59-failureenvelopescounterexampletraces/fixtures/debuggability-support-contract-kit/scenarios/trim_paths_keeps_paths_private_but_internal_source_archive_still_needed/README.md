# trim_paths_keeps_paths_private_but_internal_source_archive_still_needed

Scenario intent:
A release can use path trimming or remapping to reduce path disclosure while still needing an internal source archive or sysroot source pack for practical lookup.

The point is to keep **source-lookup impact** separate from **source-material availability and share posture**.
