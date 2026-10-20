# 0004: Expose an SSH-compatible remote-shell contract

Status: implemented

## Context

Many valuable programs do not need an SSH implementation. They need a remote-shell
executable with the conventional `ssh [options] destination [command ...]` invocation,
stdio, terminal, signal, and exit-status behavior. Rsync, Git, Borg, scp, and similar
tools construct that invocation themselves. Requiring `anonssh rsync` or a wrapper for
each program would duplicate parsers, hide upstream features, and make AnonSSH less
composable.

The original direct form accepted only one bare `user@machine-id`, rejected positional
remote commands, and converted nonzero OpenSSH status into a generic AnonSSH error. The
implemented parser and process adapter now provide the bounded contract below.

## Decision

AnonSSH will implement a documented, fail-closed subset of the OpenSSH client
invocation contract:

```text
anonssh [safe-ssh-options] [user@]machine-id [--] [command [argument ...]]
anonssh -l user [safe-ssh-options] machine-id [--] [command [argument ...]]
```

Named AnonSSH commands retain precedence when the first command token is a known
subcommand. Otherwise a dedicated remote-shell parser, not a heuristic insertion of
`connect`, separates client options, destination, and remote command. The parser consumes
`-l` into the recovery target. It forwards only options whose semantics do not replace
AnonSSH's route, identity, host trust, destination, port, configuration, or proxy. `--`
ends client-option parsing and permits an option-like first remote-command argument.
Unknown or ambiguous options fail before password entry.

Remote command arguments are appended after the generated OpenSSH destination in their
original operating-system string form. AnonSSH does not join, quote, parse, allowlist, or
execute the command itself. OpenSSH retains its normal remote-shell semantics, including
the fact that the destination login shell interprets the resulting command. This is the
only behavior compatible with existing SSH tooling; callers remain responsible for the
same quoting they require with `ssh`.

The identity prompt reads from the controlling terminal. Remote-command stdin and
stdout remain byte-pure, and all AnonSSH progress remains on stderr. The adapter
preserves OpenSSH's PTY defaults, explicit terminal and subsystem requests, half-close,
signals, and final exit status. Parser and local setup failures that occur before
OpenSSH starts retain explicit AnonSSH diagnostics; after launch, exit behavior follows
OpenSSH, including its conventional status 255 for connection failure.

Compatibility claims are evidence-based:

- remote-shell tools such as rsync, Git, and Borg are eligible once their real command
  forms and exit behavior pass packaged end-to-end tests;
- modern scp and `sftp` use the stock OpenSSH clients through `-S anonssh`; AnonSSH
  embeds the server-side SFTP subsystem and legacy scp helper rather than adding
  file-transfer subcommands;
- a tool-specific remote executable remains a destination dependency, just as it is
  with ordinary SSH, unless AnonSSH separately embeds and configures it; and
- arbitrary OpenSSH configuration compatibility is not a goal when it can override the
  recovery route or trust model.

## Consequences

The intended rsync interface is the ordinary upstream interface:

```sh
rsync -a --info=progress2 -e anonssh ./data/ alice@home:/srv/data/
```

Git can use `GIT_SSH_COMMAND=anonssh`, and other programs can select `anonssh` wherever
they select an SSH executable. Stock `scp -S anonssh` and `sftp -S anonssh` need no
AnonSSH-specific protocol; Borg uses `BORG_RSH`, and SSHFS uses `ssh_command`. The
packaged `make live-bond-tools` campaign proves rsync push/pull/resume, Git
push/clone/fetch, Borg create/check/extract, modern scp and SFTP, legacy scp, SSHFS
read/write/rename/unmount, exact remote stdio and status, clean missing-tool failure,
and independent SSH streams reusing one bond session.

This interface adds no ABP wire behavior. Each command still receives an independent
SSH connection and therefore an independent `Interactive` BondedStream on a reusable
destination session. Sustained large encrypted writes continue to use adaptive bulk
scheduling inside that stream, while small writes retain low-latency treatment.
