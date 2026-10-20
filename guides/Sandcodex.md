# Sandcodex

## Give an agent a place to do the work

Sandcodex turns a selected Linux project into a sustained human–agent working environment. Codex can edit the repository, run builds, use a real browser, operate a native desktop and return to the project's sessions. The purpose is not to make the agent merely suggest changes from outside. It is to give it enough practical capability to carry an engineering task through, while making the difference between that project's authority and the rest of the host explicit.

The supplied **0.88.0** artifact is one file containing the launcher, pinned dependency graph, operator handbook, embedded controllers and diagnostic fixtures. [Read its opening Field Handbook](../Maintained%20Tools/sandcodex#L18-L54) for the design in its own terms. The [source receipt](../updates/2026-10-20.json) identifies this supplied copy more precisely than its version number alone.

## A project boundary that permits consequential work

Consider a web application that needs a fix. The agent needs to inspect its source, change files, install or build dependencies, start the application and check the result in a browser. A room that prevents those ordinary actions is not much of a development environment. Conversely, granting the project does not require silently donating the user's whole home directory or letting project configuration become credential-bearing frontend policy.

Sandcodex's default arrangement separates these concerns. The selected project is writable; system paths and the Nix store are projected read-only; the command room uses private process, mount and network namespaces while sharing the host kernel. The [outer boundary implementation](../Maintained%20Tools/sandcodex#L120864-L120970) constructs those mounts and launch arguments explicitly. Ordinary project work can still delete files or damage uncommitted changes. That is real working authority, not a promise that every operation will be individually approved.

A further distinction matters inside the room. Codex's frontend needs authentication and session state; ordinary model-issued commands do not need to inherit all of that state. The launcher keeps trusted control material outside the mutable project and generates frontend configuration there. By default, a repository's executable `.codex` configuration, hooks and MCP declarations are not automatically loaded with frontend authority. Reading ordinary project instructions is a different activity from trusting executable project policy. The [authentication and configuration section](../Maintained%20Tools/sandcodex#L466-L486) explains that separation and its explicit override.

## The room includes ways to see what was built

The browser and desktop are different facilities, not two names for a screenshot tool. The browser provides persistent Chromium and Playwright MCP for web applications, downloads and browser interaction. The desktop is a separate Linux workstation with native application control. Its Wayland and X11 lanes serve different uses, including headless native work and a shared headful Xephyr workstation.

This lets the workflow continue beyond compilation: inspect a page, exercise its controls, open a native application, or review an exported result. Human viewers normally begin hidden; revealing a viewer need not create a different work environment or stop the controlled application. The [visual-work section](../Maintained%20Tools/sandcodex#L368-L393) also makes a crucial collaboration fact explicit: human input does not automatically suspend the agent. Fresh observations and mutation fences matter because the two participants can act on a changing scene.

Application access is handled separately again. A declared TCP publication maps a host listener to an exact application port inside the room. That can make a development server reachable, but a TCP relay is not application authentication or TLS. A local listener test and an actual remote client's successful request establish different facts. This distinction helps the operator diagnose the real missing step instead of treating “the port is open” as “the application works.” See [ingress and its checks](../Maintained%20Tools/sandcodex#L395-L427).

## Keep continuation and parallel work distinct

A long task may need more than one turn, and a large task may benefit from separate workers. Sandcodex gives those needs different mechanisms.

**Loop** continues one project and session lineage sequentially. A detached safe-mode loop can live under the user systemd manager rather than depend on an open terminal. Its controller handles classified transient failures and disk-growth stops. Requesting another turn does not enlarge the launch's outer authority. This is continuity of an ongoing working session, not a claim that every additional turn improves the project.

**Campaign** creates staged parallel work from an exact clean Git commit. A worker gets an independent clone; collection returns committed work as a Git bundle with a digest receipt. Collection does not merge or adopt it. That boundary makes a useful difference: a proposal can be inspected as a concrete change before it becomes the foreground project's state. The primary agent remains responsible for integration and tests.

The [continuation and delegation chapter](../Maintained%20Tools/sandcodex#L429-L464) also describes provider-specific lifetimes and native subagents. Those are not all the same form of independence. A worker's usable provider connection and the foreground room's continued existence can have different dependencies. The design therefore uses explicit lifecycle status rather than inferring that silence means a worker started or finished.

## A smaller boundary for a smaller action

Not every command deserves the full project's authority. The inner jail lets a delegator specify a narrower workspace, inputs, tools, network access, resource ceilings and expected result evidence for a suspect or tightly bounded operation. The delegated action supplies its arguments; it does not choose its own grant. Nested grants narrow rather than expand.

This is different from the default outer room, which is meant for ordinary engineering, and different again from an operator service: a reviewed application declaration launched in a credentialless sibling boundary with its own supervised ingress. [The authority postures](../Maintained%20Tools/sandcodex#L285-L325) explain where each belongs. Bare-metal mode is a separate, deliberate removal of outer containment, potentially including host sudo authority; it is not a fallback for an unsuccessful safe launch.

## Carry the environment's design, preserve its working state deliberately

The single-file form means the implementation and the explanation of its arrangement travel together. The [implementation atlas](../Maintained%20Tools/sandcodex#L571-L595) maps the embedded components to their distinct trust domains. It is a substantial source artifact, not merely a small command that downloads an undisclosed launcher from elsewhere. Pinned dependencies still have to be realized; portable source is not an offline bundle of every dependency or an export of runtime sessions.

Runtime continuity has its own layout. Disposable project-local work is separated from trusted authentication, sessions, locks and lifecycle records. Cleanup distinguishes caches from sessions, downloads and persistent visual-work state. State import and export are transactional and schema-checked; copying a live working-state tree is not the documented backup method. [The process/data map](../Maintained%20Tools/sandcodex#L327-L366) and [recovery chapter](../Maintained%20Tools/sandcodex#L488-L512) explain how a later occupant can recover a working situation rather than merely find a directory full of files.

## Choose the host and posture deliberately

The ordinary host contract is non-root Linux on x86-64 or ARM64, Bash, Nix with flakes, unprivileged user namespaces, cgroup v2 and a functioning systemd user manager. Explicit degradation flags change that contract. The default proxy permits broad HTTP/HTTPS/SOCKS access, including LAN destinations; restricted networking is a separate choice. Project isolation is therefore not a data-loss-prevention policy, and sharing the host kernel is not a VM boundary.

[Sandpi](Sandpi.md) instead places the Pi coding agent inside a persistent NixOS VM with its own kernel. These are different working environments, not a universal ranking of safety or capability. In either case, granting a live writable project grants consequential access to it.

If sharing Codex OAuth credentials with Sandpi, avoid overlapping refresh windows: the current reconciliation path can promote a stale frontend copy over newer canonical state. See the [source-level compatibility finding](review/Sandcodex-2026-10-20.md).

Read the original handbook before selecting a posture or following its commands. Original attribution and license/dependency notices remain in the supplied artifact. [Supplied-source review](review/Sandcodex-2026-10-20.md) · [Source receipt](../updates/2026-10-20.json).

[Maintained Tools](../Maintained%20Tools/README.md) · [Catalog](../CATALOG.md) · [W4R3Z](../README.md)
