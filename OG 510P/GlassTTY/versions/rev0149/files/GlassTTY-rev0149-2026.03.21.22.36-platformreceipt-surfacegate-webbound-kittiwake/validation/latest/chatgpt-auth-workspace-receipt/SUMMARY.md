# ChatGPT auth/workspace receipt

- generated_at: `2026-03-21T22:05:01Z`
- target support tier: `provisional`

## Auth/workspace axes

- auth-posture: logged-out and logged-in proof should remain distinct in the support story
- workspace-kind: guest, personal, business, enterprise, and edu scopes should stay explicit instead of being assumed from sparse cues
- history-boundary: logged-out one-conversation/no-saved-history behavior should remain distinct from signed-in chat history and search
- workspace-switching: multi-workspace switching cues should travel with signed-in evidence so personal-vs-business review stays auditable

## Auth/workspace readiness states

- provisional-auth-envelope: repeated text-only proof windows justify only a provisional guest-or-workspace-bound session envelope
- experimental-auth-envelope: current evidence can justify only an experimental guest-or-workspace-bound session envelope
- hold-for-auth-clarification: proof exists, but auth posture, workspace kind, or logged-out history limits are still too fuzzy to phrase honestly
- investigated-only: planning or thin proof artifacts exist, but they do not yet justify a live auth/workspace envelope
- planning-only: the receipt still describes session-boundary discipline rather than current live evidence
- stop: the supplied proof windows mix incompatible auth or workspace envelopes and should be split into separate evidence lanes
