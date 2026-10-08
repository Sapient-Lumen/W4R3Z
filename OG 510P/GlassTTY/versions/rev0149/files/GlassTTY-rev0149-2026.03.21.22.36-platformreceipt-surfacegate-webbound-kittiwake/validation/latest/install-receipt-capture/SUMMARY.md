# Install receipt

- generated_at: 2026-03-21T22:05:01Z
- bootstrap_stage: native-host-registration-missing
- primary_blocker: install the required native-host targets: chromium
- manifest_exists: True
- host_wrapper_exists: True
- ready_targets: (none)
- missing_targets: chromium
- broker_socket_exists: False
- readiness_grade: blocked-by-validation

- suggested_install_command: `./scripts/install-native-host.sh --target chromium --extension-id afmmlmjnbbcapinmhhhhbcoanfckdbfh --host-exe /mnt/data/rev0149_work/GlassTTY-rev0149-2026.03.21.22.36-platformreceipt-surfacegate-webbound-kittiwake/scripts/native-host-wrapper.sh`
- primary_next_command: `python scripts/validate-release.py --out-dir validation/latest --resume`
