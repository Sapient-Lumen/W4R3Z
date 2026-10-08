# rev0985 audit

Rev0985 extends one existing immutable SQLite backup owner across the five database roles selected by a deployment manifest. It preserves the released no-role replica behavior and binds each explicit role to its exact schema, deployment role, application ID, cutpoint, bounded canonical image, source bracket, private artifact, and detached reinspection.

The adjacent refactor separates filename-free forensic read-only SQLite images from named forensic files. Native `sqlite3_db_readonly()` remains mandatory for named files; detached immutable images retain unnamed/query-only/MEMORY-journal constraints plus behavioral write-denial proof. File-effect and folder-catalog inspection now share bounded root-cold observers rather than opening unavailable synchronized roots or maintaining divergent implementations.

Executable proof includes the existing 598-check backup/recovery/replacement process oracle and a new 699-check five-role oracle. Supporting lexical audits passed 28/28 original-backup, 31/31 role-bound-backup, 39/39 TLS-profile, and 412/412 structural checks. Those scans are supporting hygiene, not semantic proof.
