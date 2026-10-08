# Benchmark interoperability should separate partner, environment, and institution generalization

Recent cooperative-agent benchmark work suggests that one blended “generalization” score is too coarse for Concord.

Three distinctions matter:

1. **Partner generalization**: can a policy cooperate with unfamiliar counterparts when the world/institution is held fixed?
2. **Environment generalization**: can it retain cooperative competence when the task layout or ecology changes?
3. **Institution generalization**: can it preserve the intended reciprocity story when rematch, search, role-assignment, or persistence rules change?

This is now well-motivated in the external benchmark literature.

- `RS-GR-036` (OGC) explicitly treats novel partners and novel levels as separate parts of zero-shot cooperation rather than as a single leaderboard story.
- `RS-GR-037` (CEC) finds that training across many environments can induce cooperative norms that transfer to unfamiliar partners and even to human collaborators.
- `RS-GR-038` (SocialJax) shows that sequential social-dilemma evaluation can be made fast enough to support broader test coverage without turning every benchmark pass into an expensive archive-widening event.

For Concord, the practical implication is compact rather than expansive.

The first interoperability lane should not mint a new family of wide benchmark reports. Instead, it should publish one small three-axis benchmark summary inside the retained benchmark artifact or its nearest compact receipt:

- partner-novelty result,
- environment-novelty result,
- institution-novelty result.

That summary can stay scalar-and-interval based: contender set, winner/margin status, and any materiality or equivalence flag already required by the standing compact decision bundle.

This keeps the archive small while making a stronger scientific claim. A policy that only survives one axis of novelty is not yet an inheritor-grade “Golden Rule survives contact with the world” result.
