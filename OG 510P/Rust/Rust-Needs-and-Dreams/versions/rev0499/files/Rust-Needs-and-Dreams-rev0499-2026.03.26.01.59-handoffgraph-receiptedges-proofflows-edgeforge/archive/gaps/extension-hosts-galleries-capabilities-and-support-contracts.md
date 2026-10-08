# Gap: Extension hosts, galleries, capabilities, and support contracts

Rust already has serious extension ingredients:
- Zed extensions are Git repositories with an `extension.toml` manifest, can provide languages/debuggers/themes/snippets/slash commands/MCP servers, and compile procedural Rust parts to WebAssembly.
- Nushell plugins are separately installed executables speaking a versioned `nu-plugin` protocol, with explicit register/search/update lifecycle.
- Tauri plugins are first-class product units composed of a Cargo crate plus optional NPM/mobile packages, can hook lifecycle, expose commands, and ship named permissions/capabilities.
- Extism treats a plug-in system as a host-defined interface, gives plug-ins a manifest carrying runtime constraints, and allows hosts to inject custom host functions as explicit capability surfaces.
- The WebAssembly Component Model plus Rust’s 2026 Wasm Components push make WIT-described, cross-language, component-shaped extension runtimes more mainstream, not less niche.

What Rust still lacks is the **portable boring boundary above those ingredients**.

Today, serious extension-enabled products still publish their support story as a tangle of:
- host version caveats,
- plugin protocol versions,
- manifest snippets,
- capability/permission files,
- gallery/install instructions,
- update and downgrade folklore,
- runtime-kind assumptions,
- and support notes scattered across READMEs, blog posts, and issue threads.

That leaves the ecosystem unable to answer routine product questions cleanly:
- Which host versions and extension runtimes are actually supported?
- Which capabilities are merely available, which are granted by default, and which are user- or app-activated?
- Is an extension a Git repo, a registry package, a wasm/component bundle, an executable, a native dylib, or all of the above?
- What breaks on host upgrade: protocol version, capability names, runtime imports, package layout, or support policy?
- Which install/update/downgrade paths are real and tested versus only mentioned in docs?

The missing contribution is therefore **not** another plugin SDK, gallery wrapper, marketplace scraper, or Wasm-only abstraction.
It is a **productization/evidence stack** that keeps:
- host/plugin surface truth,
- runtime-kind and capability truth,
- extension package/install/update truth,
- compatibility and migration truth,
- and shipped/support truth

separate while still letting them compose.

## Why this matters
Extension ecosystems now cut across multiple archive territories:
- **Plugin Surface Kit** already covers extension points, lifecycle, manifests, and compatibility posture.
- **Runtime Capability Kit** already covers permission/capability/least-privilege truth.
- **Wasm Component Kit** already covers WIT/package/composition/publication truth for the component-model lane.
- **Host Package Kit** already covers foreign-consumer package identity and shipped package truth.
- **Distribution Contract** and **Support Envelope** already cover install/update/verification/support promises.

Without a synthesis layer, real extension products remain a seam where all of those truths get flattened into “has plugins”, “supports extensions”, or “uses Wasm”.

## Contribution shape that would count as worthy
A worthy contribution would:
1. define a thin importable artifact family for extension-enabled products;
2. keep host identity, extension package identity, runtime-kind truth, and capability activation distinct;
3. make host-upgrade, extension-upgrade, downgrade, and unsupported-lane stories explicit;
4. give release/support/gallery/policy/atlas consumers something durable to import;
5. work across editor, shell, desktop-app, agent-host, and embedded-host lanes without pretending they are identical.

## Archive direction
This gap should now be treated as an explicit **Extension Productization Stack** opportunity rather than scattered follow-on work under Plugin Surface, Wasm Components, Runtime Capability, or host-package notes.
