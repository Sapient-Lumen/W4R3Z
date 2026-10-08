from pathlib import Path

root = Path(__file__).resolve().parent

patched = [
    'README.md',
    'docs/00-status.md',
    'docs/10-resilio-sync-evaluation.md',
    'docs/30-interface-spec.md',
    'docs/31-daemon-api-spec.md',
    'docs/32-interface-flows.md',
    'docs/38-operator-workbench-interface-spec.md',
    'docs/39-interface-pattern-language.md',
    'docs/40-architecture-decisions.md',
    'docs/50-roadmap.md',
    'docs/64-critical-open-questions.md',
    'docs/89-observer-readonly-local-write-and-serve-rights-spec.md',
]

print('rev0076 patch set recorded for:')
for path in patched:
    print('-', path)
