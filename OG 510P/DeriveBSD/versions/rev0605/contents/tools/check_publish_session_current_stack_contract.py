#!/usr/bin/env python3
import sys
from pathlib import Path

REQUIRED = {
    'README.md': ['ADR-0194', 'current-stack map', 'session_version stays `0.33`'],
    'CHANGELOG.md': ['ADR-0194', 'current-stack map', 'session_version stays `0.33`'],
    'docs/00-index.md': ['ADR-0194', 'current-stack map'],
    'docs/98-archive-hygiene.md': ['check_publish_session_current_stack_contract.py', 'docs/604-publish-session-current-contract-stack-and-stale-entrypoint-firewall.md'],
    'docs/99-llm-runbook.md': ['check_publish_session_current_stack_contract.py', 'docs/604-publish-session-current-contract-stack-and-stale-entrypoint-firewall.md'],
    'docs/110-juicy-os-lessons.md': ['current-stack map', 'docs/604-publish-session-current-contract-stack-and-stale-entrypoint-firewall.md'],
    'docs/266-open-questions-and-risk-register.md': ['ADR-0194', 'docs/604-publish-session-current-contract-stack-and-stale-entrypoint-firewall.md'],
    'docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md': ['current-stack map', 'docs/604-publish-session-current-contract-stack-and-stale-entrypoint-firewall.md'],
    'docs/564-publish-session-end-conditions-and-no-auto-resume-posture-boundary.md': ['current-stack map', 'docs/604-publish-session-current-contract-stack-and-stale-entrypoint-firewall.md'],
    'docs/593-publish-session-organization-user-shares-stay-organization-scoped.md': ['current-stack map', 'docs/604-publish-session-current-contract-stack-and-stale-entrypoint-firewall.md'],
    'docs/594-publish-session-published-endpoint-surface-stays-lease-frozen.md': ['current-stack map', 'docs/604-publish-session-current-contract-stack-and-stale-entrypoint-firewall.md'],
    'docs/595-publish-session-diagnostic-artifacts-stay-off-baseline-envelope.md': ['current-stack map', 'docs/604-publish-session-current-contract-stack-and-stale-entrypoint-firewall.md'],
    'docs/596-publish-session-notes-stay-off-baseline-envelope.md': ['current-stack map', 'docs/604-publish-session-current-contract-stack-and-stale-entrypoint-firewall.md'],
    'docs/597-publish-session-visible-indicators-stay-durable-until-ended.md': ['current-stack map', 'docs/604-publish-session-current-contract-stack-and-stale-entrypoint-firewall.md'],
    'docs/598-publish-session-post-end-access-stays-fail-closed.md': ['current-stack map', 'docs/604-publish-session-current-contract-stack-and-stale-entrypoint-firewall.md'],
    'docs/599-publish-session-revocation-affordances-stay-same-surface-durable.md': ['current-stack map', 'docs/604-publish-session-current-contract-stack-and-stale-entrypoint-firewall.md'],
    'docs/600-publish-session-return-paths-stay-trusted-ui-persistent.md': ['current-stack map', 'docs/604-publish-session-current-contract-stack-and-stale-entrypoint-firewall.md'],
    'docs/601-publish-session-management-return-paths-stay-lease-exact.md': ['current-stack map', 'docs/604-publish-session-current-contract-stack-and-stale-entrypoint-firewall.md'],
    'docs/602-publish-session-post-end-management-return-stays-lease-exact-ended.md': ['current-stack map', 'docs/604-publish-session-current-contract-stack-and-stale-entrypoint-firewall.md'],
    'docs/603-publish-session-ended-states-stay-terminal-cause-exact.md': ['current-stack map', 'docs/604-publish-session-current-contract-stack-and-stale-entrypoint-firewall.md'],
}

CANONICAL_DOC = 'docs/604-publish-session-current-contract-stack-and-stale-entrypoint-firewall.md'
CANONICAL_MEMBERS = [f'docs/{n}-' for n in range(593, 604)]

ok = True
for path, toks in REQUIRED.items():
    text = Path(path).read_text()
    for tok in toks:
        if tok not in text:
            print(f'{path} missing required publish-session current-stack token: {tok}')
            ok = False

text = Path(CANONICAL_DOC).read_text()
for prefix in CANONICAL_MEMBERS:
    if prefix not in text:
        print(f'{CANONICAL_DOC} missing current-stack entry prefix: {prefix}')
        ok = False

if not ok:
    sys.exit(1)
print('publish-session current-stack contract OK')
