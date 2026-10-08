# Micromax revision 0961

## Outcome

Rev0961 closes the highest-risk unfinished plugin journey. In a restricted
workspace, explicit approval now captures the exact bounded package generation
that will execute. Initial load, reload, lifecycle source, and deferred
package-local reads consume that immutable snapshot rather than returning to
live files after a separate check.

## Product changes

- Kept restricted startup metadata-only; plugin commands remain absent until an
  interactive user approves the package.
- Made `plugin load NAME` capture a content-bound session snapshot. An unloaded
  candidate activates from those bytes; a loaded candidate receives a pending
  replacement approval without changing or disabling the committed generation.
- Made disk drift unable to alter a running callback. The callback continues to
  use the committed snapshot, while `plugin reload NAME` refuses unapproved live
  changes and commits only the retained approved replacement.
- Closed a post-approval symlink retarget escape: package-local classification is
  now lexical against the frozen snapshot, so a captured member cannot be made
  to fall through to live outside bytes.
- Invalidated retained revoked or superseded grant objects before they can
  recapture disk, consume a newer approval, reload, or evaluate source.
- Kept visible origin through command inspection and failure messages.
- Made `plugin revoke NAME` decisive: host-owned transactional cleanup removes
  managed runtime without invoking the plugin's `deinit` word, then revokes the
  grant. `plugin unload NAME` remains the explicit graceful lifecycle path.
- Kept failed cleanup honest: the live generation and grant remain unchanged and
  retained cleanup diagnostics stay inspectable.

## Audit/refactor changes

- Added `plugin_package.py` as the single owner of bounded package membership,
  digesting, exact bytes, source resolution, and worker serialization.
- Split `plugin_meta.parse_plugin_meta()` from filesystem I/O so metadata and
  entry validation can operate on the same captured bytes as evaluation.
- Removed live package walks, hashes, and worker creation from ordinary plugin
  callbacks; callback authorization is now an in-memory identity/grant check.
- Added an aggregate retained-snapshot byte budget and deduplicated identical
  live/approved snapshot objects.
- Made loaded-plugin authority object-identity-safe so stale retired records
  cannot recover access by name/digest resemblance.
- Refactored worker result handling to drain a potentially multi-megabyte
  `multiprocessing.Queue` payload before joining the child, and to terminate the
  child plus close queue resources when result receive or join fails.
- Made completion/prompt grant rows use in-memory state; explicit grant inventory
  performs the bounded live verification.
- Kept the established forkserver/spawn-first worker policy after auditing and
  rejecting an unrelated fork-first shortcut that would weaken threaded-process
  safety.
- Fixed flattened screen and curses-coordinate consumers that treated numeric
  zero as absence, restoring cursor-at-origin evidence in viewport, display,
  full-screen, and terminal rendering paths.

## Honest boundary

The capture is exact but not an atomic filesystem transaction across every file:
a hostile concurrent mutator can make the captured package a mixture of moments.
The grant nevertheless binds exactly that captured mixture, and no later
unchecked file is substituted. Plugins still execute in one Python process;
this is application policy and lifecycle hygiene, not hostile-code isolation,
publisher identity, signing, or a durable permission store.
