# Prompt profiles

VHK now keeps a small project-local store of remembered prompt answers at:

```
<project>/.vhk/prompt_profiles.json
```

This store serves two related use cases:

- **last-used answers**: the next run pre-fills the most recent non-secret values
- **named prompt profiles**: `--prompt-profile NAME` and `--save-prompt-profile NAME`
  let repeated flows reuse a saved parameter profile

## Safety

- password fields are never persisted
- fields may opt out with `remember: false`
- authors may override the derived key with `profile_key:` when multiple prompts
  should share the same saved values

## CLI

```bash
vhk run /path/to/project deploy --preset prod --prompt-profile release
vhk run /path/to/project deploy --preset prod --save-prompt-profile hotfix
vhk palette /path/to/project --prompt-profile release
vhk list-prompt-profiles /path/to/project
vhk delete-prompt-profile /path/to/project macro:deploy:preset:prod release
```

## Format notes

A prompt profile is not part of the shared project spec itself; it is local state.
That keeps reusable project files clean while still giving Linux users the fast,
iterative launcher-and-dialog workflow they expect. Prompted presets may also
surface saved profiles directly in `vhk palette` as actions like `macro@preset#profile`.
