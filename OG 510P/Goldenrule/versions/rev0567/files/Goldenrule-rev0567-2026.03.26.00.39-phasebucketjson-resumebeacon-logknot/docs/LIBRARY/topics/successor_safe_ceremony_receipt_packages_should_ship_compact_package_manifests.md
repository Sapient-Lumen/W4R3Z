# Successor-safe ceremony receipt packages should ship compact package manifests

Once the archive already has a compact successor-safe ceremony receipt plus locator, assessment, disposition, remediation plan, authorization, promotion record, review watch, review verdict, and citation advisory, the next easy failure mode is **package scatter**.

A future steward should not have to rediscover which files currently constitute the authoritative package by browsing neighboring snapshots, timestamps, or changelog prose. The archive should keep one further tiny artifact: a **package manifest**.

For any current successor-safe ceremony receipt package, the manifest should:

1. cite the active receipt locator and current claim status;
2. name the current package-state decisions (authorization, promotion, review, advisory);
3. list the authoritative component roles and exact file paths for the package root;
4. attach one file-level SHA-256 digest and byte count for each component; and
5. keep the summary small enough that downstream notes can point at the manifest when they need package membership rather than ceremony prose.

BagIt says a bag should carry just enough structure to enclose payload plus metadata for reliable storage and transfer. RO-Crate says a crate should have one root metadata document that describes the dataset and its contents. PROV says provenance information about entities and activities supports judgments about quality, reliability, and trustworthiness. A compact package manifest translates those pressures into archive practice without widening the retained evidence body.
