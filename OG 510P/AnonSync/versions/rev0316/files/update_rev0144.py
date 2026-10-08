from pathlib import Path

print('rev0144 is a documentation revision packaged from rev0143.')
print('Primary additions:')
for name in [
    '237-control-channel-certificate-bootstrap-and-browser-trust-exception-interface-spec.md',
    '238-browser-handoff-registration-and-manual-intake-fallback-interface-spec.md',
    '239-effective-rate-policy-lan-exception-and-scheduled-throttle-interface-spec.md',
    '240-installation-trust-gate-firewall-consent-and-first-run-attestation-interface-spec.md',
]:
    print(' -', name)
