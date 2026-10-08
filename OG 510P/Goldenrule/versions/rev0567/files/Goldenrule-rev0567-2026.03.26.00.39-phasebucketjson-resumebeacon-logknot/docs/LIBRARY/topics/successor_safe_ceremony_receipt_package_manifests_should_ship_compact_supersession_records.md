# Successor-safe ceremony receipt packages should ship compact supersession records

Once the archive has a compact package manifest, the next easy failure mode is **replacement ambiguity**.

A future steward should not have to infer which package manifest replaced an older one by diffing timestamps, browsing neighboring files, or reconstructing review history from chat. The archive should keep one further tiny artifact: a **package supersession record**.

For any current successor-safe ceremony receipt package that replaces an earlier package root, the supersession record should:

1. cite the prior and current package manifests by path and fixity;
2. say whether the active receipt locator stayed the same or rotated;
3. list which authoritative component roles were replaced;
4. state the compact reason codes behind the replacement; and
5. tell future stewards which manifest is now authoritative for downstream citation.

Data on the Web Best Practices says good versioning helps consumers understand whether a newer version is available and how versions differ. DCMI says one resource can explicitly replace or be replaced by another. A compact package supersession record translates those pressures into archive practice without keeping bulky duplicate package prose.
