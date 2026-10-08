# macos_direct_download_release_missing_dsym_handoff

This scenario exists to keep **direct-download shipping** separate from **post-release diagnosability**.

A macOS app can be bundled and even notarized successfully while still leaving support unable to symbolicate crashes if the `.dSYM` handoff path is missing.
