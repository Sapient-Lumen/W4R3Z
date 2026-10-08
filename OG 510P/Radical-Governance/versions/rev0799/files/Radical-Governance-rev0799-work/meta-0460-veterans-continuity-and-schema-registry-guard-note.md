# rev0759 meta — veterans continuity and common-matrix schema registry guard

Revision: `rev0759`  
Timestamp: `2026-06-13 08:25 UTC`  
Codename: `veteranscontinuity-noveteransupportbyclaimrow-schemaregistryguard`

This revision adds a veterans benefits / care / support continuity packet under **no veteran support by claim row** and adds a small lint refactor: common test-matrix schema files must now agree with the registry on their schema filename and metadata `schema` const.

The refactor is intentionally narrow. It prevents another copy-forward schema identity drift without turning the session into a general schema migration.
