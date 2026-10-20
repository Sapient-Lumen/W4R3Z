# CLI registry and completion

Status: complete command-name registry and Bash/Zsh/Fish generation implemented by ADR 0317.

IoTox has one sorted typed registry for all 201 accepted command spellings. ADR 0317 established
the first 199; ADR 0319 added `sync-recovery-verify`; ADR 0360 added
`witness-service-checkpoint-custody` through the same gate. The registry records
which dispatcher owns each command and names the canonical target of every compatibility alias.
`iotox --help` ends with the generated index, so hidden parser-only command names are visible.

Generate completion for the current shell without contacting an Agent:

```sh
# Bash, current shell
source <(iotox completion bash)

# Zsh, one conventional per-user installation
mkdir -p "$HOME/.zfunc"
iotox completion zsh >"$HOME/.zfunc/_iotox"
# Ensure ~/.zfunc is in fpath before compinit in the user's zsh configuration.

# Fish, one conventional per-user installation
mkdir -p "$HOME/.config/fish/completions"
iotox completion fish >"$HOME/.config/fish/completions/iotox.fish"
```

Those writes are ordinary operator choices; IoTox itself only prints to standard output and never
modifies shell configuration. Package maintainers may generate the same files during a build.

The v1 generator completes stable command names and `--help`/`--version`. It deliberately does not
query live peers, aliases, sessions, namespaces, witness records, filesystem paths, or remote state.
It also does not pretend to validate positional arguments. Exact argument errors remain the
responsibility of IoTox's strict parser, and the detailed forms remain in `iotox --help` and the
owning protocol/operator documents.
