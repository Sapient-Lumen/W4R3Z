# Removable-media local fallback fixture

This fixture is intentionally tiny. It gives `tools/removable_media_local_fallback_harness.py` real bytes to capture, digest, detach from, and process through a post-detach worker simulation.

The fixture is not a filesystem image. The harness uses the directory as a mounted-tree stand-in so the cloudtainer can exercise the capture/detach/post-detach invariant without FreeBSD block-device privileges.
