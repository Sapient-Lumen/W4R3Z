from pathlib import Path

print('rev0143 is a documentation revision packaged from rev0142.')
print('Primary additions:')
for name in [
    '233-approval-memory-scope-recall-and-one-time-trust-interface-spec.md',
    '234-disconnected-offline-visibility-return-and-removal-scope-interface-spec.md',
    '235-web-credential-reset-state-preservation-and-no-duplicate-seat-interface-spec.md',
    '236-local-fault-recovery-ladder-and-copy-safety-interface-spec.md',
]:
    print(' -', name)
