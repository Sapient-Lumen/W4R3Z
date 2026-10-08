# Bundle materialization

`vhk materialize-bundle <bundle.zip> <out_dir>` verifies and safely extracts one
reviewed VHK bundle into a target directory.

Why this exists:

- release and native-install flows already produce reviewable bundle payloads
- service/session flows need one shared way to turn that payload back into a
  runnable project tree
- ad-hoc `unzip` habits are the wrong place to hide integrity and path-safety
  assumptions

What the command guarantees:

- it can verify the embedded VHK bundle manifest before extraction
- it rejects absolute-path and `..`-escaping archive members
- it writes `.vhk_bundle_materialized.json` with the extracted project root and
  bundle metadata so follow-on scripts do not have to guess where the payload
  landed

This is not a sandbox boundary or a substitute for host review. It is the
reviewed-payload bridge that lets native install, package, and user-service
lanes all inherit the same bundle truth.
