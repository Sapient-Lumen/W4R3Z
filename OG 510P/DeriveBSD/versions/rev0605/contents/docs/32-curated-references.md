# Curated references (minimal, high signal)

This file is a pointer map. We do not copy external text into the archive.

## FreeBSD / BSD primitives

- FreeBSD securelevel(7): https://man.freebsd.org/cgi/man.cgi?query=securelevel&sektion=7
- OpenBSD securelevel(7): https://man.openbsd.org/securelevel.7
- FreeBSD kld(4) (kernel module interface): https://man.freebsd.org/cgi/man.cgi?query=kld&sektion=4
- FreeBSD kldload(8): https://man.freebsd.org/kldload
- FreeBSD kldstat(8): https://man.freebsd.org/kldstat
- FreeBSD kldunload(8): https://man.freebsd.org/kldunload
- FreeBSD kldconfig(8): https://man.freebsd.org/kldconfig
- FreeBSD sysctl(8): https://man.freebsd.org/cgi/man.cgi?query=sysctl&sektion=8
- FreeBSD sysctl.conf(5): https://man.freebsd.org/cgi/man.cgi?query=sysctl.conf&sektion=5
- FreeBSD Handbook security chapter (current securelevel overview): https://docs.freebsd.org/en/books/handbook/security/
- FreeBSD loader.conf(5): https://man.freebsd.org/cgi/man.cgi?query=loader.conf&sektion=5
- FreeBSD kenv(1): https://man.freebsd.org/cgi/man.cgi?query=kenv&sektion=1
- FreeBSD Secure Boot wiki: https://wiki.freebsd.org/SecureBoot
- FreeBSD Foundation: UEFI Secure Boot (overview/how-to): https://freebsdfoundation.org/freebsd-uefi-secure-boot/
- FreeBSD boot process security slides (libsecureboot/loader verification): https://papers.freebsd.org/2019/BSDCan/stanek-Improving_Security_of_the_FreeBSD_Boot_Process.files/stanek-Improving_Security_of_the_FreeBSD_Boot_Process-slides.pdf
- Adding verification to FreeBSD loader (BSDCan 2018): https://papers.freebsd.org/2018/bsdcan/gerraty-Adding_verification_to_FreeBSD_loader.files/gerraty-Adding_verification_to_FreeBSD_loader.pdf

- FreeBSD 15.0 release announcement (packaged base / pkgbase): https://www.freebsd.org/releases/15.0R/announce/
- pkgbase (FreeBSD wiki): https://wiki.freebsd.org/pkgbase
- FreeBSD etcupdate(8) (disciplined /etc merge during base upgrades): https://man.freebsd.org/cgi/man.cgi?query=etcupdate&sektion=8
- FreeBSD `freebsd-base(7)` / pkgbase(7) manpage: https://man.freebsd.org/cgi/man.cgi?query=pkgbase
- FreeBSD `build(7)` (building base-package repositories from source): https://man.freebsd.org/build
- FreeBSD `arch(7)` (cross-build `TARGET` / `TARGET_ARCH` scope and meaning): https://man.freebsd.org/arch%287%29
- Nix cross-compilation tutorial (`buildPlatform`, `hostPlatform`, `targetPlatform`): https://nix.dev/tutorials/cross-compilation.html
- Nixpkgs manual cross-platform dependency roles and config-string caveats: https://nixos.org/manual/nixpkgs/stable/
- Clang user manual (`--target=` target triples): https://clang.llvm.org/docs/UsersManual.html

- FreeBSD Handbook (Virtualization / bhyve host): https://docs.freebsd.org/en/books/handbook/virtualization/
- bhyve(8) man page: https://man.freebsd.org/bhyve
- bectl(8) man page (ZFS boot environments): https://man.freebsd.org/cgi/man.cgi?query=bectl&sektion=8
- libbe(3) (boot environment library): https://man.freebsd.org/cgi/man.cgi?query=libbe&sektion=3

- OpenZFS encryption properties (zfsprops): https://openzfs.github.io/openzfs-docs/man/master/7/zfsprops.7.html
- OpenZFS key management (zfs-load-key / zfs-change-key): https://openzfs.github.io/openzfs-docs/man/master/8/zfs-load-key.8.html
- FreeBSD zfs(8) (dataset encryption flags are documented in zfsprops): https://man.freebsd.org/cgi/man.cgi?query=zfs&sektion=8

- OpenZFS zfs-send(8) (streams, bookmarks, resume tokens): https://openzfs.github.io/openzfs-docs/man/master/8/zfs-send.8.html
- OpenZFS `zfs-hold(8)` (held snapshots cannot be destroyed): https://openzfs.github.io/openzfs-docs/man/master/8/zfs-hold.8.html
- OpenZFS `zfs-bookmark(8)` (lightweight replication continuity after snapshot deletion): https://openzfs.github.io/openzfs-docs/man/v2.2/8/zfs-bookmark.8.html
- OpenZFS zfs-recv(8) (resumable receive -s, abort -A, raw-send constraints): https://openzfs.github.io/openzfs-docs/man/master/8/zfs-recv.8.html
- FreeBSD Handbook: ZFS scrubbing / self-healing / `zpool status`: https://docs.freebsd.org/en/books/handbook/zfs/
- OpenZFS `zpool-status(8)` (current scrub / resilver / health surface): https://openzfs.github.io/openzfs-docs/man/master/8/zpool-status.8.html
- FreeBSD zfs-send(8) man page: https://man.freebsd.org/zfs-send%288%29

- ZFS boot environments overview (libbe/bectl mental model): https://wiki.freebsd.org/BootEnvironments
## Health-gated updates / boot assessment / rollback

- systemd Automatic Boot Assessment (bless/fallback discipline): https://systemd.io/AUTOMATIC_BOOT_ASSESSMENT/
- systemd-bless-boot.service(8): https://www.freedesktop.org/software/systemd/man/systemd-bless-boot.service.html
- Android A/B updates (slot lifecycle; bootloader fallback): https://source.android.com/docs/core/ota/ab
- update_engine README (A/B lifecycle and rollback note): https://chromium.googlesource.com/aosp/platform/system/update_engine/+/HEAD/README.md
- Fedora IoT/CoreOS auto-updates + rollback overview: https://docs.fedoraproject.org/en-US/fedora-coreos/auto-updates/
- greenboot (health checks + reboot/rollback framework): https://github.com/fedora-iot/greenboot
- Red Hat MicroShift docs (current greenboot health-check behavior): https://docs.redhat.com/en/documentation/red_hat_build_of_microshift/4.21/html/getting_ready_to_install_microshift/microshift-greenboot
- Greenboot in practice (Red Hat article): https://developers.redhat.com/articles/2024/08/12/greenboot-automate-rollbacks-atomically-updated-systems
- SUSE transactional-update man page (snapshot update + rollback): https://kubic.opensuse.org/documentation/man-pages/transactional-update.8.html

- FreeBSD Handbook (Network configuration): https://docs.freebsd.org/en/books/handbook/network/
- FreeBSD rc.conf(5) (network/service configuration): https://man.freebsd.org/rc.conf
- FreeBSD Handbook (Advanced networking / routing): https://docs.freebsd.org/en/books/handbook/advanced-networking/
- FreeBSD Handbook (Firewalls / PF): https://docs.freebsd.org/en/books/handbook/firewalls/
- pf.conf(5) anchors: https://man.freebsd.org/cgi/man.cgi?query=pf.conf&sektion=5
- Casper (capability-mode broker services): https://man.freebsd.org/cgi/man.cgi?query=libcasper&sektion=3
- cap_dns(3) (Casper DNS service client): https://man.freebsd.org/cgi/man.cgi?query=cap_dns&sektion=3

- netgraph(4) (kernel graph networking framework): https://man.freebsd.org/cgi/man.cgi?query=netgraph&sektion=4
- ngctl(8) (netgraph control tool): https://man.freebsd.org/cgi/man.cgi?query=ngctl&sektion=8
- ng_bridge(4) (netgraph bridge node): https://man.freebsd.org/cgi/man.cgi?query=ng_bridge&sektion=4
- ng_nat(4) (netgraph NAT node): https://man.freebsd.org/cgi/man.cgi?query=ng_nat&sektion=4
- FreeBSD Handbook mention (netgraph for host↔jail wiring): https://docs.freebsd.org/en/books/handbook/book/
- FreeBSD Foundation: “Netgraph for the Rest of Us” (overview + examples): https://freebsdfoundation.org/our-work/journal/browser-based-edition/networking-3/netgraph-for-the-rest-of-us
- netmap(4) (fast packet I/O framework): https://man.freebsd.org/cgi/man.cgi?query=netmap&sektion=4
- VALE man page (netmap virtual switch): https://manpages.ubuntu.com/manpages/jammy/man4/vale.4freebsd.html
- bpf(4) (raw packet capture interface): https://man.freebsd.org/cgi/man.cgi?query=bpf&sektion=4
- tcpdump(1) (capture through `/dev/bpf*`; packet files are an explicit artifact, not a policy boundary): https://man.freebsd.org/cgi/man.cgi?query=tcpdump&sektion=1
- pcap-filter(7) (capture-filter grammar for libpcap/tcpdump-family tooling; useful implementation substrate, but not the DeriveBSD review surface): https://man.freebsd.org/cgi/man.cgi?query=pcap-filter
- Wireshark libpcap notes (capture-filter strings are passed to libpcap and available syntax depends on the installed version): https://wiki.wireshark.org/libpcap
- Zeek `conn.log` (compact connection-level transaction summaries from observed traffic): https://docs.zeek.org/en/current/logs/conn.html
- Arkime sessions/SPI pages (session-first review over stored packet traffic, with explicit PCAP export as a separate action): https://arkime.com/
- Wireshark User's Guide (pcapng can carry comments and decryption-secret blocks, so capture files may contain more than packet payloads alone): https://www.wireshark.org/docs/wsug_html/
- Wireshark `editcap(1)` (can inject Decryption Secrets Blocks and can also discard embedded secrets when normalizing captures): https://www.wireshark.org/docs/man-pages/editcap.html
- Wireshark `capinfos(1)` (reports capture-file properties including decryption-secret counts): https://www.wireshark.org/docs/man-pages/capinfos.html
- IETF OPSAWG pcapng draft (official block taxonomy; includes Name Resolution Block and Decryption Secrets Block, which is why DeriveBSD keeps capture-file sideband metadata out of the authoritative review/export surface): https://datatracker.ietf.org/doc/draft-ietf-opsawg-pcapng/

- FreeBSD jail(8) (jail parameters, hierarchical jails): https://man.freebsd.org/jail
- FreeBSD `fts(3)` (physical tree walks; `FTS_PHYSICAL`, `FTS_NOCHDIR`): https://man.freebsd.org/fts%283%29
- FreeBSD `openat(2)` (`O_NOFOLLOW`, `O_DIRECTORY`, `O_RESOLVE_BENEATH`): https://man.freebsd.org/cgi/man.cgi?manpath=FreeBSD+12.3-RELEASE+and+Ports&query=openat&sektion=2
- FreeBSD `umount(8)` (busy mounts, open files, current working directory): https://man.freebsd.org/cgi/man.cgi?query=umount&sektion=8
- FreeBSD `fuser(1)` (which processes keep a filesystem busy; includes cwd/root/jail-root use): https://man.freebsd.org/cgi/man.cgi?query=fuser
- FreeBSD `procstat(1)` (inspect process file descriptors and working directories): https://man.freebsd.org/procstat%281%29
- FreeBSD `chflags(1)` (set `uchg`/`schg` immutable flags; useful as an implementation hardening option for preserving an exact captured file without inventing a new evidence store): https://man.freebsd.org/cgi/man.cgi?query=chflags&sektion=1
- FreeBSD `ls(1)` (`-o` shows file flags, including immutable flags, in long listings): https://man.freebsd.org/cgi/man.cgi?query=ls&sektion=1
- FreeBSD jail(2) (privilege + errors; jail_set/jail_attach semantics): https://man.freebsd.org/cgi/man.cgi?query=jail&sektion=2
- FreeBSD Architecture Handbook, Jails chapter (socket restrictions + BPF/devfs note): https://docs.freebsd.org/en/books/arch-handbook/jail/
- FreeBSD security advisory SA-05:17.devfs (why devfs exposure undermines isolation claims): https://www.freebsd.org/security/advisories/FreeBSD-SA-05%3A17.devfs.asc

## Declarative host networking (drift control lessons)

- FreeBSD Handbook: network interface configuration (ifconfig + rc.conf persistence): https://docs.freebsd.org/en/books/handbook/network/
- systemd.network(5) (.network files): https://www.freedesktop.org/software/systemd/man/systemd.network.html
- systemd.netdev(5) (.netdev files): https://www.freedesktop.org/software/systemd/man/systemd.netdev.html
- Junos OS: commit / commit confirmed / automatic rollback: https://www.juniper.net/documentation/us/en/software/junos/cli/topics/topic-map/junos-configuration-commit.html
- OpenWrt UCI backend apply with automatic rollback unless confirmed: https://openwrt.org/docs/techref/uci
- NixOS Wiki: Networking (declarative posture): https://wiki.nixos.org/wiki/Networking

## Network egress control / per-application firewalls (UX lessons)

- Little Snitch (macOS per-app outbound firewall): https://www.obdev.at/products/littlesnitch
- OpenSnitch (Linux interactive application firewall): https://github.com/evilsocket/opensnitch
- Qubes OS firewall docs (per-qube outbound policy; DNS-name caveat and updates-proxy distinction): https://doc.qubes-os.org/en/latest/user/security-in-qubes/firewall.html
- Qubes software install docs (temporary network enablement and updates-proxy posture): https://doc.qubes-os.org/en/latest/user/how-to-guides/how-to-install-software.html
- Little Snitch profiles / profile-specific rules: https://help.obdev.at/littlesnitch4/adv-profiles
- OpenSnitch getting started (temporary rules → durable least-privilege rules): https://github.com/evilsocket/opensnitch/wiki/Getting-started
- OpenSnitch configuration reference (default action, reject/deny caveats, checksums): https://github.com/evilsocket/opensnitch/wiki/Configurations
- Qubes OS firewall docs (per-qube outbound policy; DNS-name caveat and updates-proxy distinction): https://doc.qubes-os.org/en/latest/user/security-in-qubes/firewall.html
- Qubes software install docs (temporary network enablement and updates-proxy posture): https://doc.qubes-os.org/en/latest/user/how-to-guides/how-to-install-software.html
- Little Snitch profiles / profile-specific rules: https://help.obdev.at/littlesnitch4/adv-profiles
- OpenSnitch getting started (temporary rules → durable least-privilege rules): https://github.com/evilsocket/opensnitch/wiki/Getting-started
- OpenSnitch configuration reference (default action, reject/deny caveats, checksums): https://github.com/evilsocket/opensnitch/wiki/Configurations
- Cilium: policy audit mode / policy creation docs (observe flows while allowing; not recommended as steady-state production posture): https://docs.cilium.io/en/latest/security/policy-creation.html
- Kubescape: network policy generation + “NetworkNeighborhood” workload traffic summary object: https://kubescape.io/docs/operator/network-policy-generation/
- Calico: staged network policies / preview traffic impact before enforcement: https://docs.tigera.io/calico/latest/network-policy/staged-network-policies
- Capsicum (capsicum(4) + wiki): https://man.freebsd.org/capsicum%284%29 , https://wiki.freebsd.org/Capsicum
- Capsicum paper (TrustedBSD): https://papers.freebsd.org/2010/rwatson-capsicum/

## Workload identity / mTLS (SPIFFE-style)

- SPIFFE overview: https://spiffe.io/docs/latest/spiffe-about/overview/
- SPIFFE concepts (IDs + trust domain basics): https://spiffe.io/docs/latest/spiffe-about/spiffe-concepts/
- SPIFFE ID standard: https://github.com/spiffe/spiffe/blob/main/standards/SPIFFE-ID.md
- X.509-SVID standard: https://github.com/spiffe/spiffe/blob/main/standards/X509-SVID.md
- JWT-SVID standard: https://github.com/spiffe/spiffe/blob/main/standards/JWT-SVID.md
- SPIRE (reference implementation): https://spiffe.io/spire/
- SPIFFE Trust Domain and Bundle spec: https://github.com/spiffe/spiffe/blob/main/standards/SPIFFE_Trust_Domain_and_Bundle.md
- SPIFFE Federation (bundle retrieval): https://spiffe.io/docs/latest/spiffe-specs/spiffe_federation/
- SPIRE concepts (node/workload attestation and issuance): https://spiffe.io/docs/latest/spire-about/spire-concepts/
- Working with SVIDs (SPIFFE Workload API + X.509-SVIDs): https://spiffe.io/docs/latest/deploying/svids/
- SPIFFE Trust Domain and Bundle spec (current doc-site form): https://spiffe.io/docs/latest/spiffe-specs/spiffe_trust_domain_and_bundle/
- Kubernetes service account administration (TokenRequest-bound short-lived tokens): https://kubernetes.io/docs/reference/access-authn-authz/service-accounts-admin/
- Kubernetes projected service-account tokens: https://kubernetes.io/docs/concepts/storage/projected-volumes/
- Vault database secrets engine (dynamic credentials): https://developer.hashicorp.com/vault/docs/secrets/databases
- Vault Agent tutorial (additional unwrap attempts on an already-unwrapped token return an error): https://developer.hashicorp.com/vault/tutorials/vault-agent/agent-aws
- Use temporary credentials with AWS resources (calls fail after temporary credentials expire and a new set must be generated): https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_temp_use-resources.html

## PKI / trust stores (trust drift control)

- p11-kit trust module (shared system trust policy via PKCS#11): https://p11-glue.github.io/p11-glue/trust-module.html
- p11-kit trust module manual: https://p11-glue.github.io/p11-glue/p11-kit/manual/trust-module.html
- update-ca-trust(8) (consolidated CA extraction + PKCS#11 trust module hook): https://man.archlinux.org/man/update-ca-trust.8
- Fedora shared system certificates (p11-kit extracts PEM/dirhash/Java cacerts, etc): https://fedoraproject.org/wiki/Features/SharedSystemCertificates
- curl SSL CA certs overview (client trust store expectations): https://curl.se/docs/sslcerts.html
- NSS shared DB background (cert8.db/cert9.db, key3.db/key4.db): https://wiki.mozilla.org/NSS_Shared_DB
- FreeBSD libfetch CA path footgun example (historic bug): https://bugs.freebsd.org/193871
- FreeBSD `certctl(8)` (OpenSSL trust-store management): https://man.freebsd.org/certctl
- cert-manager trust-manager (bundle distribution / composition): https://cert-manager.io/docs/trust/trust-manager/
- cert-manager trust-manager ClusterBundle transition announcement (distribution API churn reminder): https://cert-manager.io/announcements/2025/09/05/trust-manager-clusterbundle-future/
- cert-manager Certificate renewal behavior (`duration`, `renewBefore`, `status.RenewalTime`): https://cert-manager.io/docs/usage/certificate/

## Temporary service sharing / relay publish adapters

- RFC 3986: URI Generic Syntax (generic URI grammar and authority/path components): https://www.rfc-editor.org/rfc/rfc3986.html
- RFC 6943: Issues in Identifier Comparison for Security Purposes (comparison ladders and security pitfalls when different components normalize identifiers differently): https://www.rfc-editor.org/rfc/rfc6943
- RFC 9110: HTTP Semantics (`https` URI scheme, default port 443, and deprecation of userinfo in http(s) URIs): https://www.rfc-editor.org/rfc/rfc9110
- RFC 6761: Special-Use Domain Names (`localhost.` and names under `.localhost.` are special and resolve to loopback): https://www.rfc-editor.org/rfc/rfc6761.html
- RFC 2606: Reserved Top Level DNS Names (`.example`, `.invalid`, `.localhost`, and `.test` stay reserved for documentation/testing and non-real-name examples): https://www.rfc-editor.org/rfc/rfc2606.html
- WHATWG URL Standard (living parser/serializer model for URL authoring and validation): https://url.spec.whatwg.org/
- Cloudflare Tunnel overview (outbound-only tunnel; no inbound ports required): https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/
- Cloudflare Tunnel connectivity requirements (explicit outbound firewall requirements): https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/configure-tunnels/tunnel-with-firewall/
- Tailscale Funnel (share a local service on the internet through a relay path): https://tailscale.com/docs/features/tailscale-funnel
- `tailscale funnel` CLI reference: https://tailscale.com/docs/reference/tailscale-cli/funnel
- Tailscale Serve (private-network sharing distinct from public Funnel): https://tailscale.com/docs/features/tailscale-serve
- ngrok secure tunnels (share localhost without opening inbound ports): https://ngrok.com/docs/guides/share-localhost/tunnels
- ngrok OAuth action (auth-gated publish endpoints rather than anonymous public by default): https://ngrok.com/docs/traffic-policy/actions/oauth
- Cloudflare Quick Tunnels (explicitly testing/development only temporary publish mode): https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/do-more-with-tunnels/trycloudflare/
- Cloudflare Tunnel FAQ (named tunnels can be attached to apex/custom DNS, showing the durable-naming side of the relay spectrum): https://developers.cloudflare.com/cloudflare-one/faq/cloudflare-tunnels-faq/
- ngrok Domains (dev domains, reserved domains, wildcard/custom domain support): https://ngrok.com/docs/universal-gateway/domains
- ngrok static dev domains blog (account-bound domains that persist across restarts and can front long-lived endpoints): https://ngrok.com/blog/free-static-domains-ngrok-users
- Cloudflare locally managed tunnels as a service (shows how relay tooling can become persistent service config if the platform does not draw a tighter boundary): https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/do-more-with-tunnels/local-management/as-a-service/linux/
- Tailscale Funnel reset/status (temporary internet sharing that still has explicit on/off and reset semantics): https://tailscale.com/docs/reference/tailscale-cli/funnel
- Tailscale Services / Serve config file and reset semantics (illustrates the config-persistence cliff for local service publication): https://tailscale.com/docs/features/tailscale-services
- Cloudflare Access policies (identity-bound access to published applications): https://developers.cloudflare.com/cloudflare-one/access-controls/policies/
- Cloudflare published application protocols (public hostname routes split HTTP/HTTPS from TCP/SSH/RDP/SMB service types): https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/routing-to-tunnel/protocols/
- GitHub validating webhook deliveries (explicit shared-secret signature verification for webhook callbacks): https://docs.github.com/en/webhooks/using-webhooks/validating-webhook-deliveries
- Stripe webhook signature verification (explicit receiver-side verification of callback signatures): https://docs.stripe.com/webhooks/signature
- Cloudflare Access JWT validation (receiver-side validation of signed identity assertions): https://developers.cloudflare.com/cloudflare-one/access-controls/applications/http-apps/authorization-cookie/validating-json/
- ngrok secure your applications with OAuth 2.0 (email/domain allowlist examples for preview sharing): https://ngrok.com/docs/guides/identity-aware-proxy/securing-with-oauth
- ngrok TCP Agent Endpoints (TCP endpoints use protocol-shaped remote URLs distinct from HTTP/S endpoint URLs): https://ngrok.com/docs/universal-gateway/tcp
- Chrome Remote Desktop support codes (one-time support code, explicit disconnect ends the session): https://support.google.com/chrome/answer/1649523
- TeamViewer Remote Support sessions (explicit support session creation/sharing flow): https://www.teamviewer.com/en/documents/
- OpenBSD `sshd_config(5)` (`GatewayPorts`, remote forwarding exposure control): https://man.openbsd.org/sshd_config

## Operator access / SSH certificates (JIT access)

- OpenSSH certificate format (PROTOCOL.certkeys): https://web.mit.edu/qrlg/openssh/PROTOCOL.certkeys
- OpenBSD sshd_config(5) (TrustedUserCAKeys / AuthorizedPrincipalsFile): https://man.openbsd.org/sshd_config
- IETF Internet-Draft: SSH Certificate Format (OpenSSH): https://www.ietf.org/archive/id/draft-miller-ssh-cert-05.html
- Smallstep SSH docs (short-lived cert workflows): https://smallstep.com/docs/ssh/
- Teleport authentication (short-lived certificates): https://goteleport.com/docs/reference/architecture/authentication/
- Teleport session recording (audit + replay model): https://goteleport.com/docs/reference/architecture/session-recording/
- OpenBSD doas(1): https://man.openbsd.org/doas.1
- OpenBSD doas.conf(5): https://man.openbsd.org/doas.conf
- HashiCorp Boundary session recording: https://developer.hashicorp.com/boundary/docs/session-recording
- Vault control groups (multi-party authorization with per-request approvals and TTL-wrapped tokens): https://developer.hashicorp.com/vault/docs/enterprise/control-groups
- Vault control-group API (authorize pending requests): https://developer.hashicorp.com/vault/api-docs/system/control-group
- GitHub Actions environments / required reviewers / prevent self-review: https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/manage-environments
- GitHub deployments and environments reference (required reviewers + protected secrets): https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments

## Pledge/unveil ergonomics (promise-based confinement)

- OpenBSD pledge(2): https://man.openbsd.org/pledge.2
- OpenBSD unveil(2): https://man.openbsd.org/unveil.2

## “Complain mode” learning loops (log→policy ergonomics)

- AppArmor command line profiling (aa-genprof / aa-logprof): https://documentation.suse.com/sles/15-SP7/html/SLES-all/cha-apparmor-commandline.html
- aa-logprof(8) man page (interactive review of AppArmor denial logs into profile edits): https://manpages.ubuntu.com/manpages/focal/man8/aa-logprof.8.html
- Ubuntu AppArmor docs (aa-logprof): https://documentation.ubuntu.com/server/how-to/security/apparmor/
- SELinux audit2allow (generate candidate allow rules from denial logs): https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/6/html/security-enhanced_linux/sect-security-enhanced_linux-fixing_problems-allowing_access_audit2allow
- OCI seccomp tracing hook (generate seccomp profiles by tracing syscalls): https://github.com/containers/oci-seccomp-bpf-hook
- Apple Sandbox/Seatbelt guide (SBPL profiling concepts; historical but good ergonomics lessons): https://reverse.put.as/wp-content/uploads/2011/09/Apple-Sandbox-Guide-v1.0.pdf
- Collection of macOS Seatbelt profiles (examples of profile structure and iteration): https://github.com/s7ephen/OSX-Sandbox--Seatbelt--Profiles

## Deterministic concurrency (reproducible multithreading for debug/test)

- DMP: Deterministic Shared Memory Multiprocessing (Devietti et al., ASPLOS 2009): https://homes.cs.washington.edu/~luisceze/publications/asplos004-devietti.pdf
- Dthreads: Efficient Deterministic Multithreading (Liu et al., SOSP 2011): https://people.cs.umass.edu/~emery/pubs/dthreads-sosp11.pdf

## Unikernels and library OSes (explicit manifests + tiny runtime contracts)

- Solo5 architecture (tender + manifest): https://github.com/Solo5/solo5/blob/main/docs/architecture.md
- MirageOS (typed unikernel ecosystem): https://mirage.io/
- Hillingar: MirageOS unikernels on NixOS (reproducible unikernel builds): https://tarides.com/blog/2022-12-14-hillingar-mirageos-unikernels-on-nixos/

## CHERI / capability hardware / temporal safety

- CHERI overview (Cambridge CTSRD): https://www.cl.cam.ac.uk/research/security/ctsrd/cheri/
- CheriBSD project: https://www.cheribsd.org/
- CheriBSD temporal safety (runtime revocation notes): https://ctsrd-cheri.github.io/cheribsd-getting-started/features/temporal.html
- CHERIvoke paper (Micro 2019): https://www.cl.cam.ac.uk/research/security/ctsrd/pdfs/201910micro-cheri-temporal-safety.pdf
- Cornucopia (Oakland 2020): https://www.cl.cam.ac.uk/research/security/ctsrd/pdfs/2020oakland-cornucopia.pdf

## Verified execution / file integrity

- NetBSD Veriexec guide chapter: https://www.netbsd.org/docs/guide/en/chap-veriexec.html
- NetBSD veriexec(4): https://man.netbsd.org/veriexec.4
- FreeBSD MAC/veriexec review trail: https://reviews.freebsd.org/D8554
- FreeBSD verifying loader for mac_veriexec: https://reviews.freebsd.org/D16575
- Linux fs-verity docs (Merkle-tree per-file authenticity): https://docs.kernel.org/filesystems/fsverity.html
- fsverity-utils (signing workflow notes): https://github.com/ebiggers/fsverity-utils
- rctl(8) man page (resource limits): https://man.freebsd.org/cgi/man.cgi?query=rctl&sektion=8
- rctl.conf(5) (persistent rctl rules): https://man.freebsd.org/cgi/man.cgi?query=rctl.conf&sektion=5
- FreeBSD Handbook: resource limits (rctl overview): https://docs.freebsd.org/en/books/handbook/security/#security-resourcelimits
- FreeBSD status: racct (resource accounting): https://www.freebsd.org/status/report-2021-04-2021-06/racct/
- FreeBSD hierarchical resource limits (background): https://wiki.freebsd.org/Hierarchical_Resource_Limits

## Resource governance / quotas / pressure

- Solaris/illumos rctl (resource controls): https://docs.oracle.com/cd/E36784_01/html/E36849/resource-ctrls-6.html
- Linux cgroup v2 (conceptual reference): https://docs.kernel.org/admin-guide/cgroup-v2.html
- systemd resource control (soft vs hard limits; MemoryHigh/MemoryMax patterns): https://www.freedesktop.org/software/systemd/man/systemd.resource-control.html
- Kubernetes Vertical Pod Autoscaler (observed usage → recommendations): https://kubernetes.io/docs/concepts/workloads/autoscaling/vertical-pod-autoscale/
- Linux PSI (pressure stall information): https://docs.kernel.org/accounting/psi.html

## Fault management / hardware health

- Solaris fault management overview (FMA): https://docs.oracle.com/cd/E36784_01/html/E48546/gliqg.html
- Joyent RFD 0006 (FMA background / `fmd`): https://github.com/joyent/rfd/blob/master/rfd/0006/README.md
- Oxide RFD 26 (illumos FMA notes): https://26.rfd.oxide.computer/
- OpenZFS events: https://openzfs.github.io/openzfs-docs/man/v2.0/5/zfs-events.5.html

## Secure time (NTS / Roughtime)

- RFC 8915 — Network Time Security (NTS) for NTP: https://www.rfc-editor.org/info/rfc8915
- Cloudflare Time Services overview (NTP / NTS / Roughtime): https://developers.cloudflare.com/time-services/
- Cloudflare NTS overview (operator-friendly): https://developers.cloudflare.com/time-services/nts/
- Cloudflare Roughtime overview: https://developers.cloudflare.com/time-services/roughtime/
- Cloudflare Roughtime usage (server address + public key): https://developers.cloudflare.com/time-services/roughtime/usage/
- chrony NTS config manual (`server ... nts`, current docs): https://chrony-project.org/doc/4.8/chrony.conf.html
- chrony vs other implementations (includes NTS support matrix and isolated-network notes): https://chrony-project.org/comparison.html
- NTPsec NTS quick start: https://docs.ntpsec.org/latest/NTS-QuickStart.html

## Confidential computing / TEEs (SEV-SNP / TDX / Arm CCA)

- AMD SEV-SNP attestation overview (report flow + cert chain): https://www.amd.com/content/dam/amd/en/documents/developer/lss-snp-attestation.pdf
- Linux kernel TDX doc (attestation steps; TDREPORT + quote): https://docs.kernel.org/arch/x86/tdx.html
- Intel TDX documentation hub (architecture + attestation pointers): https://www.intel.com/content/www/us/en/developer/tools/trust-domain-extensions/documentation.html
- Confidential Containers: Get Attestation (security considerations): https://confidentialcontainers.org/docs/features/get-attestation/
- Confidential Containers design overview (AA/KBS patterns): https://confidentialcontainers.org/docs/architecture/design-overview/
- CoCo attestation-service repo (evidence payload shape): https://github.com/confidential-containers/attestation-service
- Red Hat overview: confidential containers attestation flow: https://www.redhat.com/en/blog/understanding-confidential-containers-attestation-flow
- AWS doc: SEV-SNP attestation report and launch measurement explanation: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/snp-attestation.html

- ntpd-rs (memory-safe NTP+NTS implementation): https://github.com/pendulum-project/ntpd-rs
- FreeBSD NTS notes (chrony/ntpsec options): https://joshua.hu/encrypted-ntp-nts-chronyd-freebsd
- IETF Roughtime draft: https://datatracker.ietf.org/doc/draft-ietf-ntp-roughtime/
- Google Roughtime protocol (reference implementation/spec): https://roughtime.googlesource.com/roughtime/+/HEAD/PROTOCOL.md

## Structured event logs / journaling

- ETW overview (provider/consumer tracing sessions): https://learn.microsoft.com/en-us/windows/win32/etw/about-event-tracing
- systemd journal file format (binary + indexed logs): https://www.freedesktop.org/wiki/Software/systemd/journal-files/
- systemd journal file format (systemd.io canonical doc; includes sealing fields): https://systemd.io/JOURNAL_FILE_FORMAT/
- journald.conf Seal= (Forward Secure Sealing controls): https://www.freedesktop.org/software/systemd/man/journald.conf.html
- journalctl --setup-keys / sealing verification (FSS): https://www.freedesktop.org/software/systemd/man/journalctl.html
- AWS CloudTrail digest file structure (hashes + chained signatures): https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-log-file-validation-digest-file-structure.html
- AWS CloudTrail log file integrity validation overview: https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-log-file-validation-intro.html
- Security analysis of journald forward-secure sealing (IACR ePrint 2023/867): https://eprint.iacr.org/2023/867.pdf
- OpenTelemetry logs data model (timestamps, severities, attributes): https://opentelemetry.io/docs/specs/otel/logs/data-model/
- OpenTelemetry security: handling sensitive data (current guidance on minimization / redaction): https://opentelemetry.io/docs/security/handling-sensitive-data/
- systemd-journald service (structured, indexed journal behavior): https://www.freedesktop.org/software/systemd/man/systemd-journald.service.html
- Fuchsia diagnostics overview (Archivist + attributed logs/Inspect): https://fuchsia.dev/fuchsia-src/concepts/components/diagnostics
- Fuchsia Inspect overview (structured component diagnostics): https://fuchsia.dev/fuchsia-src/development/diagnostics/inspect

## Incident bundles / crash reporting / diagnostic collections

- Red Hat: generating sos reports for technical support (`sos report`, current RHEL 10 guide): https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/10/html/getting_the_most_from_your_support_experience/generating-an-sos-report-for-technical-support
- Red Hat KB: what an `sos report` collects and why it is used: https://access.redhat.com/solutions/3592
- Ubuntu Apport (crash reporting; sensitive-data warning): https://wiki.ubuntu.com/Apport
- Plaso / log2timeline (forensic “super timelines” from heterogeneous artifacts): https://plaso.readthedocs.io/
- Timesketch (collaborative timeline analysis; annotations/tags over timelines): https://github.com/google/timesketch
- NIST SP 800-86, *Guide to Integrating Forensic Techniques into Incident Response* (evidence integrity + chain-of-custody guidance for incident handling): https://csrc.nist.gov/pubs/sp/800/86/final

## Support bundles / diagnostic collection

- RHEL sos reports (support bundle collection): https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/8/html-single/generating_sos_reports_for_technical_support/index
- sosreport upstream repository (support bundle tool): https://github.com/sosreport/sos
- Fedora Magazine deep dive on sosreport layout (practical bundle contents): https://fedoramagazine.org/%F0%9F%94%A7-deep-dive-into-sosreport-understanding-the-data-pack-layout-in-fedora-rhel/
- OpenShift support / remote health monitoring (connected + restricted network support workflows): https://docs.redhat.com/en/documentation/openshift_container_platform/4.19/html-single/support/index
- Red Hat Ansible Automation Platform containerized troubleshooting (`clean` / `upload` support-bundle parameters): https://docs.redhat.com/en/documentation/red_hat_ansible_automation_platform/2.6/html-single/containerized_installation/index

- Fedora ABRT (Automatic Bug Reporting Tool): https://fedoraproject.org/wiki/Automatic_Bug_Reporting_Tool
- systemd-coredump (core dumps as objects + metadata): https://www.freedesktop.org/software/systemd/man/systemd-coredump.html
- coredumpctl (retrieve/process core-dump metadata and dumps): https://www.freedesktop.org/software/systemd/man/coredumpctl.html

## Ticketing / support system attachment APIs (export transports)

- Jira Cloud: add issue attachment via REST API: https://support.atlassian.com/jira/kb/how-to-add-an-attachment-to-a-jira-cloud-issue-using-rest-api/
- Jira Data Center: add issue attachment via REST API: https://support.atlassian.com/jira/kb/how-to-add-an-attachment-to-a-jira-issue-using-rest-api/
- Jira Data Center REST API (attachment group): https://developer.atlassian.com/server/jira/platform/rest/v10002/api-group-attachment/
- ServiceNow Attachment API: https://www.servicenow.com/docs/r/api-reference/rest-apis/c_AttachmentAPI.html

## Secrets / credentials (brokered, optionally TPM-bound)

- systemd credentials design notes: https://systemd.io/CREDENTIALS/
- systemd-creds(1) man page (encrypt/decrypt credentials): https://www.freedesktop.org/software/systemd/man/systemd-creds.html
- systemd-cryptenroll(1) (TPM2 enrollment into LUKS2): https://www.freedesktop.org/software/systemd/man/systemd-cryptenroll.html
- systemd-pcrphase.service(8) (boot phase measurements into PCRs): https://www.freedesktop.org/software/systemd/man/systemd-pcrphase.service.html
- TPM2 sealing/unsealing tools (tpm2-tools): https://tpm2-tools.readthedocs.io/en/latest/man/tpm2_create.1/ , https://tpm2-tools.readthedocs.io/en/latest/man/tpm2_unseal.1/ , https://tpm2-tools.readthedocs.io/en/latest/man/tpm2_policypcr.1/
- TPM2 policy-authorize (evolvable PCR policies): https://tpm2-tools.readthedocs.io/en/latest/man/tpm2_policyauthorize.1/
- TPM2 createpolicy (simple PCR policy creation): https://tpm2-tools.readthedocs.io/en/latest/man/tpm2_createpolicy.1/
- Vault Agent templating (render secrets to files/env for legacy apps): https://developer.hashicorp.com/vault/docs/agent-and-proxy/agent/template
- Vault leases (TTL/renew/revoke model): https://developer.hashicorp.com/vault/docs/concepts/lease
- Vault lease renew command: https://developer.hashicorp.com/vault/docs/commands/lease/renew
- Vault lease revoke command: https://developer.hashicorp.com/vault/docs/commands/lease/revoke
- Vault lease troubleshooting (manual revoke should follow a valid snapshot in recovery scenarios): https://developer.hashicorp.com/vault/docs/troubleshoot/lease-issues

## Crypto operations / split-key brokers (non-exportable keys)

- Qubes Split GPG ("smart card as a VM" pattern): https://doc.qubes-os.org/en/latest/user/security-in-qubes/split-gpg.html
- Qubes Split GPG-2 (updated split-gpg tooling): https://doc.qubes-os.org/en/latest/user/security-in-qubes/split-gpg-2.html
- Qubes qrexec socket-based services (RPC handled by a long-running server in a VM): https://doc.qubes-os.org/en/latest/developer/services/qrexec-socket-services.html
- Qubes Split SSH app/scripts (agent socket bridged to a vault VM): https://github.com/henn/qubes-app-split-ssh
- Qubes qrexec framework (cross-domain RPC): https://doc.qubes-os.org/en/latest/developer/services/qrexec.html
- Qubes RPC policy system (who may call what): https://doc.qubes-os.org/en/latest/user/advanced-topics/rpc-policy.html
- OpenSSH release notes (agent forwarding / PKCS#11 provider loading caveat): https://www.openssh.com/releasenotes.html
- OpenBSD `sshd_config(5)` (`AllowAgentForwarding` caveat; disabling forwarding alone is not a complete boundary if users still get a shell): https://man.openbsd.org/sshd_config
- GnuPG agent forwarding notes (legacy forwarding exists, so DeriveBSD must bound it instead of pretending it does not): https://wiki.gnupg.org/AgentForwarding
- Apple: Protecting keys with the Secure Enclave: https://developer.apple.com/documentation/security/protecting-keys-with-the-secure-enclave
- Apple Platform Security: The Secure Enclave: https://support.apple.com/guide/security/the-secure-enclave-sec59b0b31ff/web
- Apple Platform Security: Keychain data protection: https://support.apple.com/guide/security/keychain-data-protection-secb0694df1a/web
- Android hardware-backed keystore (KeyMint/Keymaster): https://source.android.com/docs/security/features/keystore
- Android key and ID attestation (hardware-backed constraints + attestable properties): https://source.android.com/docs/security/features/keystore/attestation


## Crypto agility / misuse-resistant libraries

- Google Tink (misuse-resistant crypto APIs): https://developers.google.com/tink
- libsodium documentation (high-level safe APIs): https://doc.libsodium.org/
- rustls (memory-safe TLS stack): https://github.com/rustls/rustls
- BoringSSL (TLS/crypto library with strong API opinions): https://boringssl.googlesource.com/boringssl/

## Interactive authorization / consent agents (GUI + TTY + portals)

- polkit agent docs (how GUI auth agents work): https://www.freedesktop.org/software/polkit/docs/latest/polkit-agents.html
- polkit overview (client/mechanism model): https://manpages.ubuntu.com/manpages/focal/man8/polkit.8.html
- systemd password agents spec: https://systemd.io/PASSWORD_AGENTS/
- systemd-tty-ask-password-agent(1): https://man7.org/linux/man-pages/man1/systemd-tty-ask-password-agent.1.html
- XDG Desktop Portal Request: https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.portal.Request.html
- XDG Desktop Portal PermissionStore: https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.impl.portal.PermissionStore.html
- XDG Desktop Portal RemoteDesktop: https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.portal.RemoteDesktop.html
- XDG Desktop Portal ScreenCast: https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.portal.ScreenCast.html
- XDG Desktop Portal wiki: The Permission Store (storage model notes): https://github.com/flatpak/xdg-desktop-portal/wiki/The-Permission-Store

## Spec/policy authoring frontends (compile-to-IR)

- CUE data validation use case (schema+values; validate then render): https://cuelang.org/docs/concept/data-validation-use-case/
- CUE JSON workflows (read/write/validate JSON): https://cuelang.org/docs/concept/how-cue-works-with-json/
- CUE export command reference: https://cuelang.org/docs/reference/command/cue-help-export/
- CUE file embedding reference (`@embed`): https://cuelang.org/docs/reference/command/cue-help-embed/
- CUE modules reference: https://cuelang.org/docs/reference/modules/
- Pkl language site/docs: https://pkl-lang.org/
- Pkl CLI docs (`--format json` and output control): https://pkl-lang.org/main/current/pkl-cli/index.html
- Pkl evaluator settings (root dir / HTTP / external readers): https://pkl-lang.org/package-docs/pkl/current/EvaluatorSettings/index.html
- Pkl external readers docs: https://pkl-lang.org/go/current/external-readers.html
- Pkl air-gapped package guidance: https://pkl-lang.org/blog/using-packages-in-air-gapped-environments.html
- Starlark language overview (deterministic / hermetic posture): https://starlark-lang.org/
- Starlark specification: https://starlark-lang.org/spec.html
- Nickel manual (intro): https://nickel-lang.org/user-manual/introduction/
- Nickel repo: https://github.com/nickel-lang/nickel
- Tweag: Nickel↔Nix interop notes: https://tweag.io/blog/2023-01-24-nix-with-with-nickel/
- HuJSON / JWCC reference implementation: https://github.com/tailscale/hujson

## Declarative / restricted build pipelines

- apko file format (YAML declarative image definition; no arbitrary `RUN`): https://github.com/chainguard-dev/apko/blob/main/docs/apko_file.md
- apko repo (reproducible-by-default image builder): https://github.com/chainguard-dev/apko
- melange repo (pipeline-oriented package builds): https://github.com/chainguard-dev/melange
- melange build command docs: https://github.com/chainguard-dev/melange/blob/main/docs/md/melange_build.md
- melange compile command docs: https://github.com/chainguard-dev/melange/blob/main/docs/md/melange_compile.md
- Wolfi overview: https://edu.chainguard.dev/open-source/wolfi/overview/

## Filesystem metadata + attribute queries (Haiku/BeOS BFS lessons)

- Haiku: Mastering queries (practical attribute/query workflows): https://www.haikuinsider.org/mastering-queries
- Ars Technica: BeOS/BFS retrospective (query UX): https://arstechnica.com/information-technology/2018/07/the-beos-filesystem/
- Dominic Giampaolo: Practical File System Design with the Be File System (attributes/indexing/query model): https://nobius.org/~dbg/practical-file-system-design.pdf

## Separation of duties / quorum approvals

- TUF spec (threshold signatures; root keys offline): https://theupdateframework.github.io/specification/latest/
- “four-eyes” / two-person rule (governance control pattern): https://www.flagsmith.com/blog/what-is-the-four-eyes-principle

## MicroVM config injection patterns

- cloud-init NoCloud datasource (config via ISO/VFAT, no network required): https://cloudinit.readthedocs.io/en/latest/reference/datasources/nocloud.html
- vm-bhyve cloud-init support (practical FreeBSD-hosted pattern): https://github.com/churchers/vm-bhyve
- Firecracker MMDS (metadata service; optional backend reference): https://github.com/firecracker-microvm/firecracker/blob/main/docs/mmds/mmds-user-guide.md

## ABI compatibility layers (Linuxulator / WSL / userspace kernels)

- FreeBSD Handbook: Linux Binary Compatibility (Linuxulator): https://docs.freebsd.org/en/books/handbook/linuxemu/
- FreeBSD `linux(4)` man page (Linux ABI module): https://man.freebsd.org/cgi/man.cgi?linux%284%29=
- FreeBSD wiki: Linuxulator (status notes): https://wiki.freebsd.org/Linuxulator
- Microsoft: Comparing WSL 1 and WSL 2 (compat layer vs real kernel): https://learn.microsoft.com/en-us/windows/wsl/compare-versions
- Ubuntu docs: Comparing WSL versions (same distinction): https://documentation.ubuntu.com/wsl/latest/explanation/compare-wsl-versions/
- gVisor docs (userspace “application kernel” isolation model): https://gvisor.dev/docs/

## Supply-chain / attestations / SBOM

- Go sumdb design (checksum transparency): https://go.googlesource.com/proposal/+/master/design/25530-sumdb.md
- Filippo Valsorda: transparent keyserver w/ tlog: https://words.filippo.io/keyserver-tlog/
- Google Key Transparency design (auditable key directory): https://github.com/google/keytransparency/blob/master/docs/design.md
- Rootless containers (user namespaces; UX reference): https://www.redhat.com/en/blog/rootless-podman-user-namespace-modes

- SLSA Provenance spec (v1.0): https://slsa.dev/spec/v1.0/provenance
- in-toto Attestation Framework (Statement/Envelope): https://in-toto.io/docs/specs/  (and Statement/Envelope v1 under in-toto/attestation)
- DSSE spec (v1): https://github.com/secure-systems-lab/dsse
- sigstore cosign attestations: https://docs.sigstore.dev/cosign/verifying/attestation/
- Cosign signing overview (keyless): https://docs.sigstore.dev/cosign/signing/overview/
- Cosign quickstart: https://docs.sigstore.dev/quickstart/quickstart-cosign/
- Cosign installation / TUF environment notes (trusted root distribution): https://docs.sigstore.dev/cosign/system_config/installation/
- Cosign verification guide (identity flags + bundle verification examples): https://docs.sigstore.dev/cosign/verifying/verify/
- Sigstore threat model (identity monitoring + TUF-distributed trust roots): https://docs.sigstore.dev/about/threat-model/
- Sigstore timestamp verification notes (Rekor integrated time / TSA): https://docs.sigstore.dev/cosign/verifying/timestamps/
- Sigstore BYO TUF / custom trust roots: https://blog.sigstore.dev/sigstore-bring-your-own-stuf-with-tuf-40febfd2badd/
- Sigstore blog: verifying bundles as an end user (Instance / IdP / identities): https://blog.sigstore.dev/cosign-verify-end-user/

- Sigstore bundle format (DSSE binding): https://docs.sigstore.dev/about/bundle/
- Sigstore overview (components + trust model): https://docs.sigstore.dev/about/overview/
- Fulcio overview (short-lived certs bound to OIDC): https://docs.sigstore.dev/certificate_authority/overview/
- Sigstore Rekor logging overview (monitoring notes): https://docs.sigstore.dev/logging/overview/
- Rekor monitor (sigstore/rekor-monitor): https://github.com/sigstore/rekor-monitor
- Sigstore blog: using rekor-monitor: https://blog.sigstore.dev/using-rekor-monitor/
- Trail of Bits: rekor-monitor production hardening (case study): https://blog.trailofbits.com/2025/12/12/catching-malicious-package-releases-using-a-transparency-log/
- transparency.dev: witness network explainer: https://blog.transparency.dev/can-i-get-a-witness-network
- Witness cosigning paper (Syta et al., “Witness cosigning”): https://dedis.cs.yale.edu/dissent/papers/witness.pdf
- Sigsum docs (witnessing + monitoring): https://www.sigsum.org/docs/
- Sigsum getting started (trust policy + offline verification walkthrough): https://www.sigsum.org/getting-started/
- transparency-dev witness implementation: https://github.com/transparency-dev/witness
- witness-network participation (operational profiles): https://witness-network.org/participate/
- TUF spec + security model (freeze/rollback): https://theupdateframework.github.io/specification/latest/ , https://theupdateframework.io/docs/security/
- TUF FAQ (delegations / role separation intuition): https://theupdateframework.io/docs/faq/
- SPDX spec: https://spdx.dev/specifications/
- SPDX 3.0.1 spec (HTML): https://spdx.github.io/spdx-spec/v3.0.1/
- CycloneDX spec: https://cyclonedx.org/specification/overview/
- CycloneDX standard (ECMA-424): https://ecma-international.org/publications-and-standards/standards/ecma-424/
- CycloneDX VEX capability (exploitability context): https://cyclonedx.org/capabilities/vex/
- CISA: minimum requirements for VEX: https://www.cisa.gov/sites/default/files/2023-04/minimum-requirements-for-vex-508c.pdf
- OpenVEX spec (minimal VEX format; designed for attestation embedding): https://github.com/openvex/spec
- OpenVEX attesting notes (in-toto embedding): https://github.com/openvex/spec/blob/main/ATTESTING.md
- GUAC (Graph for Understanding Artifact Composition) overview: https://guac.sh/guac/
- GUAC “known and unknown” (why metadata needs a graph): https://docs.guac.sh/guac/known-and-unknown/
- OpenSSF blog: GUAC joins OpenSSF as an incubating project: https://openssf.org/blog/2024/03/07/guac-joins-openssf-as-incubating-project/

## Software Heritage / SWHID (long-term source availability)

- SWHID spec (intrinsic identifiers for software artifacts): https://www.swhid.org/specification/
- SWHID spec v1.0 introduction: https://www.swhid.org/specification/v1.0/0.Introduction/
- Software Heritage SWHID overview: https://www.softwareheritage.org/software-hash-identifier-swhid/
- Software Heritage persistent identifiers docs: https://docs.softwareheritage.org/devel/swh-model/persistent-identifiers.html
- Software Heritage Vault (bundles) + API: https://docs.softwareheritage.org/devel/swh-vault/index.html and https://docs.softwareheritage.org/devel/swh-vault/api.html
- Software Heritage API getting started: https://docs.softwareheritage.org/devel/getting-started/api.html
- Guix blog: long-term source availability via Software Heritage: https://guix.gnu.org/en/blog/2019/connecting-reproducible-deployment-to-a-long-term-source-code-archive/
- Software Heritage note on Nix/Guix origins: https://docs.softwareheritage.org/user/software-origins/nixguix.html


## Store views / sandboxfs (performance)

- Bazel sandboxing (sandboxfs rationale): https://bazel.build/docs/sandboxing
- sandboxfs (FUSE virtual view FS): https://github.com/bazelbuild/sandboxfs
- FreeBSD port of sandboxfs (FreshPorts): https://www.freshports.org/filesystems/sandboxfs/

## Build farms / jobsets (Hydra lessons)

- Hydra repo docs (projects + jobsets): https://github.com/NixOS/hydra
- NixOS wiki: Hydra overview: https://wiki.nixos.org/wiki/Hydra
- Hydra paper (Dolstra): https://edolstra.github.io/pubs/hydra-scp-submitted.pdf

## Remote cache security (action-cache poisoning)

- Bazel remote caching: https://bazel.build/remote/caching
- Bazel remote execution overview: https://bazel.build/remote/rbe
- Deep dive on remote caching threats: https://blogsystem5.substack.com/p/bazel-remote-caching

## Observability / telemetry (capability-gated)

- OpenTelemetry spec overview (traces/metrics/logs semantics): https://opentelemetry.io/docs/specs/otel/overview/
- OpenTelemetry security guidance: handling sensitive data (processors/filtering/redaction): https://opentelemetry.io/docs/security/handling-sensitive-data/

## WebAssembly Component Model / WIT (interface contracts)

- WIT reference (Bytecode Alliance): https://component-model.bytecodealliance.org/design/wit.html
- WIT draft spec (WebAssembly/component-model): https://github.com/WebAssembly/component-model/blob/main/design/mvp/WIT.md
- Fuchsia diagnostics model (logs/Inspect mediated by archivist): https://fuchsia.dev/fuchsia-src/concepts/components/diagnostics

## Debugging / record-replay (time-travel)

## Userspace kernel development / driver testing (rump kernels)

- “Kernel Development in Userspace — The Rump Approach” (BSDCan 2009): https://www.bsdcan.org/2009/schedule/attachments/104_rumpdevel.pdf
- “Rump File Systems: Kernel Code Reborn” (USENIX 2009): https://www.usenix.org/event/usenix09/tech/full_papers/kantee/kantee.pdf
- “The rump kernel: A tool for driver development and a toolkit …” (AsiaBSDCon 2015): https://www.netbsd.org/gallery/presentations/justin/2015_AsiaBSDCon/justincormack-abc2015.pdf


## Kernel UAPI / ABI surface discipline

- LWN: “Specifying the kernel ABI” (syscalls + ioctls + vDSO framing): https://lwn.net/Articles/726021/
- Linux: ABI stability levels (`/Documentation/ABI/` habit): https://docs.kernel.org/admin-guide/abi-stable.html
- Linux: ABI testing documentation (examples of ioctl-based UAPI docs + expectations): https://www.kernel.org/doc/html/next/admin-guide/abi-testing.html
- Linux: ABI README (levels + expectations): https://github.com/torvalds/linux/blob/master/Documentation/ABI/README
- Qualcomm: UAPI compatibility checking automation (detect userspace breakage): https://www.qualcomm.com/developer/blog/2024/01/uapi-compatibility-checker-automated-tooling-detect-userspace-breakage-linux-kernel

## Programmable kernel hooks (BPF/eBPF) threat model

- Linux Foundation: eBPF Security Threat Model (attack trees + mitigations): https://www.linuxfoundation.org/hubfs/eBPF/ControlPlane%20%E2%80%94%20eBPF%20Security%20Threat%20Model.pdf
- SoK: Challenges and Paths Toward Memory Safety for eBPF (Oakland' 25): https://nebelwelt.net/files/25Oakland.pdf
- Verifying the Verifier: eBPF range analysis verification (CAV' 23): https://people.cs.rutgers.edu/~sn624/papers/agni-cav23.pdf
- Overview: The eBPF runtime in the Linux kernel (survey-style): https://arxiv.org/html/2410.00026v1

 + user-mode drivers

- Fuchsia: Drivers concept overview (drivers as user-space components): https://fuchsia.dev/fuchsia-src/concepts/drivers
- Fuchsia: Driver framework (DFv2) overview: https://fuchsia.dev/fuchsia-src/concepts/drivers/driver_framework
- Windows: User-Mode Driver Framework (UMDF) overview: https://learn.microsoft.com/en-us/windows-hardware/drivers/wdf/overview-of-the-umdf
- Linux kernel docs: Rust in the kernel: https://docs.kernel.org/rust/index.html
- Rust for Linux project hub: https://rust-for-linux.com/

## Userspace filesystems (puffs/FUSE style)

- NetBSD: puffs overview (pass-to-userspace framework): https://www.netbsd.org/docs/puffs/
- NetBSD man page: puffs(4): https://man.netbsd.org/puffs.4
- ReFUSE paper (FUSE reimplementation on puffs): https://www.netbsd.org/docs/puffs/refuse.pdf

## Live kernel patching / rebootless patching

- kpatch: dynamic kernel patching infrastructure: https://github.com/dynup/kpatch
- RHEL live patching docs (operational framing + limits): https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/8/html/managing_monitoring_and_updating_the_kernel/applying-patches-with-kernel-live-patching_managing-monitoring-and-updating-the-kernel
- Oracle Ksplice overview: https://www.oracle.com/linux/technologies/updating-system-with-ksplice.html


- rr project (record/replay + reverse debugging): https://rr-project.org/
- rr repository: https://github.com/rr-debugger/rr
- Pernosco (rr traces processed into a web time-travel debugger): https://pernos.co/
- Windows Time Travel Debugging (TTD) overview: https://learn.microsoft.com/en-us/windows-hardware/drivers/debuggercmds/time-travel-debugging-overview
- ReproZip docs (pack an execution + dependencies): https://docs.reprozip.org/en/latest/

## Remote assistance + session recording (consent + replayable artifacts)

- Microsoft: Windows Remote Assistance overview: https://support.microsoft.com/en-us/windows/solve-pc-problems-remotely-with-remote-assistance-cf384ff4-6269-d86e-bcfe-92d72ed55922
- Microsoft Remote Assistance policy CSP `SessionLogging` (device policy for session log generation): https://learn.microsoft.com/en-us/windows/client-management/mdm/policy-csp-remoteassistance
- AWS Systems Manager Session Manager logging session activity (session metadata/history and audit trail): https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager-auditing.html
- Qubes OS 4.1 release notes (strictly opt-in remote support, no ports open by default): https://doc.qubes-os.org/en/latest/developer/releases/4_1/release-notes.html
- tlog project (terminal I/O recording + playback): https://scribery.github.io/tlog/
- Red Hat docs: Recording sessions (tlog): https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/8/html-single/recording_sessions/index
- Red Hat docs: tlog playback tool (tlog-play): https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/8/html/recording_sessions/playing-back-a-recorded-session-getting-started-with-session-recording

## Breakglass / emergency access / recovery

- Microsoft Entra emergency access accounts (operational guidance + monitoring expectations): https://learn.microsoft.com/en-us/entra/identity/role-based-access-control/security-emergency-access
- AWS Well-Architected emergency access process (audit and monitoring expectations): https://docs.aws.amazon.com/wellarchitected/latest/framework/sec_permissions_emergency_process.html
- NixOS specialisations (alternate boot/recovery entry pattern): https://nixos.wiki/wiki/Specialisation
- OpenBSD `bsd.rd` ramdisk kernel (install/upgrade/recovery lane): https://www.openbsd.org/faq/faq4.html
- systemd rescue/emergency targets (recovery lane reference): https://www.freedesktop.org/software/systemd/man/systemd.special.html

## OS integration testing frameworks (VM/installer/boot as tests)

- NixOS VM tests overview (multi-VM orchestration + interactive driver): https://wiki.nixos.org/wiki/NixOS_VM_tests
- Nix.dev tutorial: integration testing with NixOS VMs: https://nix.dev/tutorials/nixos/integration-testing-using-virtual-machines.html
- openQA docs (OS installation/boot/GUI testing with screenshots/video): https://open.qa/docs/
- Kyua man page (BSD test execution/reporting): https://man.freebsd.org/cgi/man.cgi?query=kyua
- FreeBSD TestSuite notes (ATF/Kyua): https://wiki.freebsd.org/TestSuite
- ATF project (test authoring libraries): https://github.com/freebsd/atf
- ATF intro man page (BSD test authoring): https://man.freebsd.org/cgi/man.cgi?query=atf&sektion=7

## Fuzzing + regression localization (continuous security ROI)

- syzkaller docs (crash reproduction): https://github.com/google/syzkaller/blob/master/docs/reproducing_crashes.md
- syzkaller docs (coverage collection): https://github.com/google/syzkaller/blob/master/docs/coverage.md
- OSS-Fuzz docs (coverage reports as guidance): https://google.github.io/oss-fuzz/advanced-topics/code-coverage/
- OSS-Fuzz docs (Fuzz Introspector reachability/coverage guidance): https://google.github.io/oss-fuzz/advanced-topics/fuzz-introspector/
- syzkaller docs (syscall descriptions/syzlang): https://github.com/google/syzkaller/blob/master/docs/syscall_descriptions.md
- syzkaller docs (internals: corpus, minimization, VM orchestration): https://github.com/google/syzkaller/blob/master/docs/internals.md
- syzbot docs (continuous kernel fuzzing + reporting system): https://github.com/google/syzkaller/blob/master/docs/syzbot.md
- SyzDescribe paper (automating syscall description generation): https://www.shitong.me/pdfs/oakland23_syzdescribe.pdf
- ChromeOS security review HOWTO (explicit fuzzing requirement for non-trivial untrusted data): https://www.chromium.org/chromium-os/developer-library/guides/security/security-review-howto/
- Chromium Mojo IPC security notes (IPC methods are untrusted structured inputs): https://chromium.googlesource.com/chromium/src/+/main/docs/security/mojo.md
- Chromium IPC reviews guide (review discipline for new IPC surfaces): https://chromium.googlesource.com/chromium/src/+/HEAD/docs/security/ipc-reviews.md
- Project Zero: Fuzzing ImageIO (why image parsers are high-value attack surface): https://projectzero.google/2020/04/fuzzing-imageio.html
- Google Threat Intelligence: Fuzzing image parsing in Windows (harness + corpus notes): https://cloud.google.com/blog/topics/threat-intelligence/fuzzing-image-parsing-in-windows-color-profiles
- Microsoft SDL eBook (attack surface + untrusted parsing is high priority): https://download.microsoft.com/download/8/1/6/816C597A-5592-4867-A0A6-A0181703CD59/Microsoft_Press_eBook_TheSecurityDevelopmentLifecycle_PDF.pdf
- FreeBSD Foundation slides: Kernel Fuzzing with syzkaller (good mental model for corpora/crash DB): https://freebsdfoundation.org/wp-content/uploads/2021/01/Kernel-Fuzzing.pdf
- Delta Debugging (Zeller 2002, “ddmin” concept): https://www.st.cs.uni-saarland.de/publications/files/zeller-tse-2002.pdf
- Git bisect reference (binary search over badness): https://git-scm.com/docs/git-bisect
- Git `update-ref` documentation (safe ref updates with old-object verification / transaction semantics): https://git-scm.com/docs/git-update-ref

## Threat modeling / trust boundaries

- Microsoft Threat Modeling Tool getting started (DFDs + trust boundaries + STRIDE framing): https://learn.microsoft.com/en-us/azure/security/develop/threat-modeling-tool-getting-started
- Microsoft training module: create a threat model using DFD elements: https://learn.microsoft.com/en-us/training/modules/tm-create-a-threat-model-using-foundational-data-flow-diagram-elements/
- OWASP Threat Modeling Process (DFDs + STRIDE): https://owasp.org/www-community/Threat_Modeling_Process

## Information flow control (DIFC) / labels + declassification

- HiStar paper (labels + explicit info-flow enforcement): https://www.scs.stanford.edu/~nickolai/papers/zeldovich-histar.pdf
- Asbestos paper (labels + event processes + declassification): https://www.scs.stanford.edu/~dm/home/papers/efstathopoulos:asbestos.pdf
- Flume paper (DIFC on standard OS abstractions): https://pdos.csail.mit.edu/papers/flume-sosp07.pdf
- Laminar paper (practical DIFC across OS resources + heap objects): https://www.cs.utexas.edu/~mckinley/papers/laminar-pldi-2009.pdf

## Sandboxed file access (persistable grants)

- Apple: accessing files from the macOS App Sandbox (security-scoped bookmarks): https://developer.apple.com/documentation/security/accessing-files-from-the-macos-app-sandbox
- Apple: startAccessingSecurityScopedResource(): https://developer.apple.com/documentation/Foundation/URL/startAccessingSecurityScopedResource%28%29
- XDG Desktop Portal documentation index (portal family overview and cross-link surface): https://flatpak.github.io/xdg-desktop-portal/docs/
- XDG Desktop Portal: Documents portal (restricted exported view): https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.portal.Documents.html
- XDG Desktop Portal: FileChooser portal (user-mediated import/export): https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.portal.FileChooser.html
- XDG Desktop Portal: FileTransfer portal (brokered drag&drop/copy-paste export): https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.portal.FileTransfer.html
- XDG Desktop Portal: OpenURI portal (user-controlled URI opening; `file://` excluded from `OpenURI`): https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.portal.OpenURI.html
- Wayland data-control protocol (clipboard manager surface; note deprecation and privileged nature): https://wayland.app/protocols/wlr-data-control-unstable-v1
- XDG Desktop Portal: Clipboard portal: https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.portal.Clipboard.html
- XDG Desktop Portal: Notification portal: https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.portal.Notification.html
- XDG Desktop Portal: Lockdown backend interface (disable portal families for hardened environments): https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.impl.portal.Lockdown.html
- XDG Desktop Portal: Inhibit portal (session transitions): https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.portal.Inhibit.html
- XDG Desktop Portal: InputCapture portal (brokered input capture): https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.portal.InputCapture.html
- Qubes OS: device handling security warning (USB input devices): https://doc.qubes-os.org/en/latest/user/security-in-qubes/device-handling-security.html
- Microsoft: secure logon trusted path note (CTRL+ALT+DEL): https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/security-policy-settings/interactive-logon-do-not-require-ctrl-alt-del

## Intent routing / plumbing

- Plan 9 plumbing design notes: https://9p.io/sys/doc/plumb.html
- plumb(7) rules and ports: https://9fans.github.io/plan9port/man/man7/plumb.html
- Android intents and intent filters: https://developer.android.com/guide/components/intents-filters
- Android RoleManager API reference (browser/home/SMS and other host-managed roles): https://developer.android.com/reference/android/app/role/RoleManager
- Android Enterprise managed configurations (IT admins remotely specify app settings): https://developer.android.com/work/managed-configurations
- Android Enterprise dedicated devices overview (fully managed devices for a specific purpose): https://developer.android.com/work/dpc/dedicated-devices
- Microsoft ApplicationDefaults policy CSP (admins set default file/protocol associations through policy): https://learn.microsoft.com/en-us/windows/client-management/mdm/policy-csp-applicationdefaults
- Windows default application association XML import/export guidance: https://learn.microsoft.com/en-us/windows-hardware/manufacture/desktop/export-or-import-default-application-associations?view=windows-11
- Kubernetes admission controllers (mutating/validating policy stays distinct from the requesting client): https://kubernetes.io/docs/reference/access-authn-authz/admission-controllers/
- Kubernetes Validating Admission Policy (declarative in-process validation rules): https://kubernetes.io/docs/reference/access-authn-authz/validating-admission-policy/
- Kubernetes Mutating Admission Policy (mutations can be defined as apply configuration or JSON patch): https://kubernetes.io/docs/reference/access-authn-authz/mutating-admission-policy/
- Kubernetes admission request schema (`object` and `oldObject` on admission requests): https://kubernetes.io/docs/reference/config-api/apiserver-admission.v1/
- kube-apiserver Admission (v1) (`uid` distinguishes otherwise identical request/response pairs): https://kubernetes.io/docs/reference/config-api/apiserver-admission.v1/
- Vault response wrapping (single-use wrapping tokens with separate TTL): https://developer.hashicorp.com/vault/docs/concepts/response-wrapping; Response wrapping keeps single-use delivery tokens on a separate TTL-bound lane
- AWS S3 presigned URLs (URL-carried capability with explicit expiration): https://docs.aws.amazon.com/AmazonS3/latest/userguide/using-presigned-url.html; You can use the presigned URL multiple times, up to the expiration date and time
- Temporary security credentials in IAM (short-lived and unusable after expiry): https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_temp.html
- etcd transactions (`If`/`Then`/`Else` compare-and-swap primitive): https://etcd.io/docs/v3.4/learning/api/
- XDG Desktop Portal AppChooser backend (chooser from a provided app list): https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.impl.portal.AppChooser.html
- XDG Desktop Portal Settings backend (read-only; not for general purpose settings): https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.impl.portal.Settings.html
- Qubes OS disposables guide (OpenURL/OpenInVM into isolated compartments): https://doc.qubes-os.org/en/latest/user/how-to-guides/how-to-use-disposables.html

## Namespaces and filesystem views (Plan 9 + union directories)

- Plan 9 — the use of namespaces (per-process views; union directory model): https://9p.io/sys/doc/names.html
- Plan 9 `bind(1)` (union mount semantics): https://9p.io/magic/man2html/1/bind
- LWN — Union file systems (Plan 9/BSD/Linux comparisons): https://lwn.net/Articles/325369/

## Multi-origin userlands / meta-distribution layering

- Bedrock Linux concepts (strata terminology; explicit layering): https://bedrocklinux.org/0.7/concepts-and-terminology.html

## Resource delegation mindset

## Build feature flags / conditional dependencies

- Gentoo Development Manual — USE flags: https://devmanual.gentoo.org/general-concepts/use-flags/index.html

## Project input graphs / lockfiles (flakes lessons)

- nix.dev — Flakes concepts: https://nix.dev/concepts/flakes.html
- Nix reference manual — `nix flake lock`: https://nix.dev/manual/nix/2.18/command-ref/new-cli/nix3-flake-lock
- NixOS Wiki — Flakes overview: https://wiki.nixos.org/wiki/Flakes

## Controlled impurity (explicitly marked waivers)

- Nix reference manual — experimental feature `impure-derivations` (explicitly marking non-fixed outputs): https://nix.dev/manual/nix/2.21/contributing/experimental-features#impure-derivations

## Profiles and user environment generations (atomic switch UX)

- Nix manual — Profiles (user environment generations + atomic symlink flip): https://nix.dev/manual/nix/2.33/package-management/profiles.html
- Nix Pills — User environments + profile generations: https://nixos.org/guides/nix-pills/03-enter-environment.html
- Nix reference manual — `nix-env --switch-profile` (profile semantics): https://nix.dev/manual/nix/2.23/command-ref/nix-env/switch-profile

## Garbage collection, roots, and retention

- Nix manual — Garbage collection: https://nix.dev/manual/nix/2.26/package-management/garbage-collection
- Nix manual — Garbage Collector Roots: https://nix.dev/manual/nix/2.25/package-management/garbage-collector-roots
- Nix Pills — The Garbage Collector: https://nixos.org/guides/nix-pills/11-garbage-collector.html

## Closures and deployment diffs ("what new code exists now?")

- Nix reference manual — `nix-store --query --requisites` (closure / requisites): https://nix.dev/manual/nix/2.26/command-ref/nix-store/query
- rpm-ostree admin handbook (deployment model overview): https://coreos.github.io/rpm-ostree/administrator-handbook/
- RHEL for Edge docs — `rpm-ostree db diff` (diff package sets between commits): https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/9/html/composing_installing_and_managing_rhel_for_edge_images/edge-terminology-and-commands_composing-installing-managing-rhel-for-edge-images
- OSTree man page — `ostree admin config-diff` (diff /etc vs default): https://ostreedev.github.io/ostree/man/ostree-admin-config-diff.html

## Stateless roots / explicit persistence sets (impermanence)

- NixOS “impermanence” module (explicit persistence lists + discardable root): https://github.com/nix-community/impermanence
- “Erase your darlings” (practical stateless roots on ZFS): https://grahamc.com/blog/erase-your-darlings
- systemd-tmpfiles (declare volatile/persistent paths; lifecycle rules): https://www.freedesktop.org/software/systemd/man/latest/systemd-tmpfiles.html

## Portable service bundles (host attach/detach pattern)

- systemd — Portable Services: https://systemd.io/PORTABLE_SERVICES/
- systemd-portabled.service(8): https://man7.org/linux/man-pages/man8/systemd-portabled.service.8.html
- portablectl(1): https://manpages.debian.org/experimental/systemd-container/portablectl.1.en.html

## Document sanitization (disposable sandbox workflows)

- Dangerzone overview (render-to-pixels to neutralize active content): https://dangerzone.rocks/
- Dangerzone repo + design notes: https://github.com/freedomofpress/dangerzone
- Dangerzone Qubes integration (sanitization VM pattern): https://github.com/freedomofpress/dangerzone/wiki/Qubes-OS-Integration

## AppVMs, disposables, and portalized desktop apps

- Qubes OS inter-qube clipboard guide (explicit plain-text copy/paste; clears on delivery): https://doc.qubes-os.org/en/latest/user/how-to-guides/how-to-copy-and-paste-text.html
- Qubes GUI virtualization (window origin markers; clipboard mediation): https://doc.qubes-os.org/en/latest/developer/system/gui.html
- Qubes GUI domain (separate GUI-domain deployment option; trust-boundary consequences): https://doc.qubes-os.org/en/latest/user/advanced-topics/gui-domain.html
- Mesa VirGL (virtual 3D GPU architecture): https://docs.mesa3d.org/drivers/virgl.html
- Mesa Virtio-GPU Venus (virtio-GPU Vulkan protocol): https://docs.mesa3d.org/drivers/venus.html
- Qubes “how to use disposables” (stateless qubes; sanitize use-case): https://doc.qubes-os.org/en/latest/user/how-to-guides/how-to-use-disposables.html
- Qubes VM interface / OpenInVM/OpenURL service notes: https://doc.qubes-os.org/en/latest/developer/debugging/vm-interface.html
- Qubes disposable implementation (preloaded disposables mechanics): https://doc.qubes-os.org/en/latest/developer/services/disposablevm-implementation.html
- Qubes template implementation (private + volatile disks; read-only root): https://doc.qubes-os.org/en/latest/developer/system/template-implementation.html
- Qubes templates overview (centralized updates; per-VM private storage): https://doc.qubes-os.org/en/latest/user/templates/templates.html
- Flatpak sandbox permissions (default isolation + portal approach): https://docs.flatpak.org/en/latest/sandbox-permissions.html
- Flatpak manifests (how permissions/finish-args are expressed): https://docs.flatpak.org/en/latest/manifests.html
- Flathub linter (permission-smell rules that block submissions): https://docs.flathub.org/docs/for-app-authors/linter
- systemd-analyze security (generated sandbox exposure summary for units): https://www.freedesktop.org/software/systemd/man/systemd-analyze.html
- Microsoft Office Protected View (downloaded/untrusted files open read-only first): https://support.microsoft.com/en-us/office/what-is-protected-view-d6f09ac7-e6b9-4495-8e43-2bbcdbcb6653
- Microsoft File Explorer preview disabled by default for Mark-of-the-Web files: https://support.microsoft.com/en-us/topic/file-explorer-automatically-disables-the-preview-feature-for-files-downloaded-from-the-internet-56d55920-6187-4aae-a4f6-102454ef61fb
- Microsoft SharePoint check out/check in/discard changes (explicit check-in/version boundary): https://support.microsoft.com/en-us/office/check-out-check-in-or-discard-changes-to-files-in-a-sharepoint-library-7e2c12a9-a874-4393-9511-1378a700f6de
- Google Drive Manage versions / Upload new version: https://support.google.com/drive/answer/2409045?co=GENIE.Platform%3DDesktop&hl=en

## Portable homes / embedded user records (roaming users)

- systemd “Home Directories” (systemd-homed overview): https://systemd.io/HOME_DIRECTORY/
- systemd user record format (embedded JSON metadata): https://github.com/systemd/systemd/blob/main/docs/USER_RECORD.md
- homectl(1) (management interface): https://www.freedesktop.org/software/systemd/man/homectl.html
- Android file-based encryption / Direct Boot (credential-encrypted vs device-encrypted storage): https://source.android.com/docs/security/features/encryption/file-based
- FreeBSD Handbook: ZFS delegation + per-dataset permissions: https://docs.freebsd.org/en/books/handbook/zfs/
- FreeBSD Foundation: ZFS native encryption overview (keys load/unload): https://freebsdfoundation.org/our-work/journal/browser-based-edition/storage-and-filesystems/protecting-data-with-zfs-native-encryption
- Qubes OS FAQ (default full-disk encryption except `/boot`): https://doc.qubes-os.org/en/latest/introduction/faq.html

## Appendix: concrete links (authoritative where possible)

### FreeBSD / bhyve / networking
- bhyve(8) man page (virtio-console listed): https://man.freebsd.org/bhyve
- FreeBSD Handbook — bhyve graphical UEFI framebuffer / VNC (`fbuf`): https://docs.freebsd.org/en/books/handbook/virtualization/
- FreeBSD `virtio_gpu(4)` man page (2D virtio-gpu guest support): https://man.freebsd.org/cgi/man.cgi?query=virtio_gpu&sektion=4&manpath=FreeBSD+14.4-RELEASE+and+Ports
- FreeBSD src commit adding `virtio_gpu` 2D driver: https://cgit.freebsd.org/src/commit/?id=02f2706606e1a4364d10a313dade29a9d4cfffe1
- bhyvectl(8) control utility (destroy/force-poweroff/snapshots): https://man.freebsd.org/cgi/man.cgi?query=bhyvectl&sektion=8
- FreeBSD bhyve wiki (guest notes, examples): https://wiki.freebsd.org/bhyve
- nmdm(4) null-modem device (serial console plumbing): https://man.freebsd.org/nmdm%284%29
- pf.conf(5) anchors: https://man.freebsd.org/cgi/man.cgi?query=pf.conf&sektion=5
- Casper (capability-mode broker services): https://man.freebsd.org/cgi/man.cgi?query=libcasper&sektion=3
- cap_dns(3) (Casper DNS service client): https://man.freebsd.org/cgi/man.cgi?query=cap_dns&sektion=3

### Network egress control / per-application firewalls (UX lessons)

- Little Snitch (macOS per-app outbound firewall): https://www.obdev.at/products/littlesnitch
- OpenSnitch (Linux interactive application firewall): https://github.com/evilsocket/opensnitch
- Cilium: policy audit mode / policy creation docs (observe flows while allowing; not recommended as steady-state production posture): https://docs.cilium.io/en/latest/security/policy-creation.html
- Kubescape: network policy generation + “NetworkNeighborhood” workload traffic summary object: https://kubescape.io/docs/operator/network-policy-generation/
- Calico: staged network policies / preview traffic impact before enforcement: https://docs.tigera.io/calico/latest/network-policy/staged-network-policies
- bectl(8) boot environments: https://man.freebsd.org/cgi/man.cgi?query=bectl&sektion=8
- vmm(4) device (bhyve virtualization interface): https://man.freebsd.org/cgi/man.cgi?query=vmm&sektion=4
- devfs.rules(5) (device node permissions / jails / services): https://man.freebsd.org/cgi/man.cgi?query=devfs.rules&sektion=5
- FreeBSD Status Report: VirtIO Sockets / AF_VSOCK: https://www.freebsd.org/status/report-2024-07-2024-09/vsock/
- Linux vsock(7) man page (AF_VSOCK address format and semantics): https://man7.org/linux/man-pages/man7/vsock.7.html
- Cloud Hypervisor vsock notes (well-known CID values, design pointers): https://github.com/cloud-hypervisor/cloud-hypervisor/blob/main/docs/vsock.md
- QEMU virtio-vsock feature notes: https://wiki.qemu.org/Features/VirtioVsock

### bhyve inside jails (defense in depth)
- FreeBSD 12.0 release notes (`security.jail.vmm_allowed`): https://www.freebsd.org/releases/12.0R/relnotes/
- FreeBSD Handbook: virtualization notes re bhyve in jails + devfs naming collisions: https://docs.freebsd.org/en/books/handbook/virtualization/
- jail(8) warnings about devfs exposure: https://man.freebsd.org/jail
- Jailed bhyve walkthrough (developer write-up): https://github.com/lattera/articles/blob/master/freebsd/2018-10-27_jailed_bhyve/article.md
- Example regression report (bug): https://bugs.freebsd.org/bugzilla/show_bug.cgi?id=273557

### virtio-9p (VirtFS) and FreeBSD guest support
- bhyve(8) lists virtio-9p device: https://man.freebsd.org/bhyve%288%29
- FreeBSD review trail: virtio-9p/VirtFS in bhyve (D10335): https://reviews.freebsd.org/D10335
- FreeBSD guest filesystem: p9fs(4): https://cocalc.com/github/freebsd/freebsd-src/blob/main/share/man/man4/p9fs.4
- Guest caveat thread (vm-bhyve issue): https://github.com/churchers/vm-bhyve/issues/552

### “first boot provisioning” (Ignition pattern)
- Fedora CoreOS docs: producing Ignition config: https://docs.fedoraproject.org/en-US/fedora-coreos/producing-ign/
- Ignition overview: https://coreos.github.io/ignition/
- Ignition configuration spec (example v3.4.0): https://coreos.github.io/ignition/configuration-v3_4/

### Immutable base + optional extensions (systemd-sysext pattern)
- systemd-sysext(8): https://www.freedesktop.org/software/systemd/man/systemd-sysext.html

### Per-compartment hardening knobs (HardenedBSD secadm mindset)
- HardenedBSD feature comparison (ASLR, SEGVGUARD, W^X): https://hardenedbsd.org/content/easy-feature-comparison
- secadm README (rules + toggles): https://hardenedbsd.org/sites/default/files/README.txt
- secadm repo (design notes): https://github.com/HardenedBSD/secadm

### MicroVM containers (Kata lessons)
- Firecracker API actions (SendCtrlAltDel for orderly shutdown): https://github.com/firecracker-microvm/firecracker/blob/main/docs/api_requests/actions.md
- Kata design doc: virtualization mapping: https://github.com/kata-containers/kata-containers/blob/main/docs/design/virtualization.md
- AWS blog: Kata Containers isolation overview: https://aws.amazon.com/blogs/containers/enhancing-kubernetes-workload-isolation-and-security-using-kata-containers/
- Kata blog: microVM + vsock agent notes: https://katacontainers.io/blog/deploying-microvm-on-top-of-kubernetes/

### Practical ecosystem notes
- vm-bhyve virtio-9p guest caveats (issue): https://github.com/churchers/vm-bhyve/issues/552

### Canonicalization / digests
- RFC 8785 (JCS): https://www.rfc-editor.org/rfc/rfc8785
- JCS reference implementation + test vectors (cyberphone): https://github.com/cyberphone/json-canonicalization
- Pure-Python RFC 8785 implementation (Trail of Bits): https://github.com/trailofbits/rfc8785.py
- Python JCS package (Anders Rundgren): https://pypi.org/project/jcs/
- Rust canonical JSON (RFC 8785) formatter (containers/canon-json-rs): https://github.com/containers/canon-json-rs
- Rust JCS implementation (serde_json_canonicalizer): https://crates.io/crates/serde_json_canonicalizer
- Unicode Standard Annex #15: Unicode Normalization Forms: https://unicode.org/reports/tr15/
- Apple Developer Forums: APFS FAQ (normalization-preserving, normalization-insensitive lookup behavior): https://developer.apple.com/forums/thread/731600
- RFC 9530 (HTTP Content-Digest / Repr-Digest): https://www.rfc-editor.org/rfc/rfc9530
- RFC 9530 (HTTP Content-Digest / Repr-Digest): https://www.rfc-editor.org/rfc/rfc9530

- RFC 9110 (HTTP 202 Accepted is intentionally noncommittal; useful reminder that send success is not the same thing as later acceptance): https://www.rfc-editor.org/rfc/rfc9110
- RFC 3798 (Message Disposition Notification; useful prior art for correlating original and final recipient identities on a per-recipient basis): https://www.rfc-editor.org/rfc/rfc3798
- RFC 4130 (AS2 signed receipt / MDN with Received-content-MIC; useful prior art for separating transport response from stronger receipt evidence): https://www.rfc-editor.org/rfc/rfc4130
- RFC 9110 (HTTP HEAD and validators; useful prior art for metadata-first reverification without body transfer): https://datatracker.ietf.org/doc/html/rfc9110
- Amazon S3 `HeadObject` (metadata lookup without returning object bytes): https://docs.aws.amazon.com/AmazonS3/latest/API/API_HeadObject.html
- Google Cloud Storage objects.get metadata / HEAD guidance (metadata-first lookup rather than downloading full object contents): https://docs.cloud.google.com/storage/docs/json_api/v1/objects/get
- AWS S3 Object Lock (retention periods + legal holds for object versions): https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock.html
- Azure immutable blob storage (WORM posture via time-based retention policies + legal holds): https://learn.microsoft.com/en-us/azure/storage/blobs/immutable-storage-overview
- Azure immutable blob version immutability / legal hold (version-scoped hold/immutability posture): https://learn.microsoft.com/en-us/azure/storage/blobs/immutable-policy-configure-version-scope
- Amazon S3 `GetObject` (specific object versions via `versionId`): https://docs.aws.amazon.com/AmazonS3/latest/API/API_GetObject.html
- Azure `Get Blob Properties` (HEAD + `versionid` for metadata on a specific blob version): https://learn.microsoft.com/en-us/rest/api/storageservices/get-blob-properties
- Google Cloud Storage Object Retention Lock (object-scoped retention configuration / lock): https://docs.cloud.google.com/storage/docs/object-lock
- Google Cloud Storage Bucket Lock / retention lock (locked retention policies prevent early removal): https://docs.cloud.google.com/storage/docs/bucket-lock

### Attestations
- in-toto specs index: https://in-toto.io/docs/specs/
- in-toto spec (layout + link model): https://github.com/in-toto/docs/blob/master/in-toto-spec.md
- in-toto getting started (layout explanation): https://in-toto.io/docs/getting-started/
- in-toto paper (USENIX Security 2019): https://www.usenix.org/system/files/sec19-torres-arias.pdf
- in-toto Statement v1 spec: https://github.com/in-toto/attestation/blob/main/spec/v1/statement.md
- in-toto Envelope (DSSE) v1 spec: https://github.com/in-toto/attestation/blob/main/spec/v1/envelope.md
- SLSA blog: in-toto and SLSA: https://slsa.dev/blog/2023/05/in-toto-and-slsa
- SLSA specification v1.2: https://slsa.dev/spec/v1.2/
- SLSA Build Provenance (predicate): https://slsa.dev/spec/v1.2/build-provenance
- SLSA verifying artifacts (attestations need verifier expectations): https://slsa.dev/spec/v1.0/verifying-artifacts
- SLSA Verification Summary Attestation (VSA): https://slsa.dev/verification_summary/

## Sigstore/Cosign (optional adapter lane)

- Cosign repo: https://github.com/sigstore/cosign
- Cosign keyless signing overview: https://docs.sigstore.dev/cosign/signing/overview/
- Cosign in-toto attestation verification: https://docs.sigstore.dev/cosign/verifying/attestation/

## bhyve configuration

- bhyve(8): https://man.freebsd.org/bhyve
- bhyve_config(5) (network backends incl. tap / netgraph / netmap / slirp): https://man.freebsd.org/cgi/man.cgi?query=bhyve_config&sektion=5

## Secure Boot

- FreeBSD UEFI Secure Boot (Foundation): https://freebsdfoundation.org/freebsd-uefi-secure-boot/
- FreeBSD SecureBoot wiki: https://wiki.freebsd.org/SecureBoot
- UEFI spec: Secure Boot and Driver Signing: https://uefi.org/specs/UEFI/2.9_A/32_Secure_Boot_and_Driver_Signing.html
- boot1.efi(8): https://man.freebsd.org/cgi/man.cgi?query=boot1.efi&sektion=8
- SBAT (generation-based revocation) in shim: https://github.com/rhboot/shim/blob/main/SBAT.md
- GRUB manual on SBAT: https://www.gnu.org/software/grub/manual/grub/html_node/Secure-Boot-Advanced-Targeting.html
- Microsoft Secure Boot certificate expiration + CA updates (2011→2023): https://support.microsoft.com/en-us/topic/windows-secure-boot-certificate-expiration-and-ca-updates-7ff40d33-95dc-4c3c-8725-a9b95457578e
- Microsoft support: When Secure Boot certificates expire on Windows devices (customer/device remediation guidance): https://support.microsoft.com/en-us/topic/when-secure-boot-certificates-expire-on-windows-devices-c83b6afd-a2b6-43c6-938e-57046c80c1c2
- Microsoft IT Pro blog: Act now — Secure Boot certificates expire in June 2026: https://techcommunity.microsoft.com/blog/windows-itpro-blog/act-now-secure-boot-certificates-expire-in-june-2026/4426856
- Microsoft Windows Server blog: Prepare your servers for Secure Boot certificate updates (server rollout guidance): https://www.microsoft.com/en-us/windows-server/blog/2026/02/23/prepare-your-servers-for-secure-boot-certificate-updates/
- Red Hat: Secure Boot certificate changes in 2026 (Linux operator guidance): https://access.redhat.com/articles/7128933
- Dell Secure Boot transition FAQ (2011→2023 CA split for bootloaders/Option ROMs): https://www.dell.com/support/kbdoc/en-bb/000390990/secure-boot-transition-faq
- LWN: Linux and Secure Boot certificate expiration (shim key expiry context): https://lwn.net/Articles/1029767/

## TPM / measured boot (optional)

- Microsoft DICE (Device Identifier Composition Engine) overview: https://www.microsoft.com/en-us/research/project/dice-device-identifier-composition-engine/
- IETF RATS Architecture (RFC 9334): https://datatracker.ietf.org/doc/rfc9334/
- TPM2 tooling (quote): https://tpm2-tools.readthedocs.io/en/latest/man/tpm2_quote.1/
- TPM2 tooling (verify quote): https://tpm2-tools.readthedocs.io/en/latest/man/tpm2_checkquote.1/
- TPM2 tooling (event log parser + PCR replay helper): https://tpm2-tools.readthedocs.io/en/latest/man/tpm2_eventlog.1/
- TCG Canonical Event Log (CEL) format (draft; verifier trust guidance): https://trustedcomputinggroup.org/wp-content/uploads/TCG_IWG_CEL_v1_r0p41_pub.pdf
- TCG PC Client Platform Firmware Profile v1.06 (event log + integrity hooks): https://trustedcomputinggroup.org/wp-content/uploads/TCG-PC-Client-Platform-Firmware-Profile-Version-1.06-Revision-52_pub-3.pdf
- TCG Guidance on Integrity Measurements and Event Log Processing v1.0 (verifier guidance; log trust pitfalls): https://trustedcomputinggroup.org/wp-content/uploads/TCG-Guidance-Integrity-Measurements-Event-Log-Processing_V1.0_R131_PUB.pdf
- Keylime security design notes: https://keylime.readthedocs.io/en/latest/design/security.html
- IMA concepts (runtime integrity vocabulary): https://ima-doc.readthedocs.io/en/latest/ima-concepts.html
- RATS conceptual message wrapper draft (Evidence/Results containers): https://datatracker.ietf.org/doc/html/draft-ietf-rats-msg-wrap
- EAT media types (RATS payload conveyance): https://www.rfc-editor.org/rfc/rfc9782.pdf
- Keylime measured boot guide: https://keylime.readthedocs.io/en/latest/user_guide/use_measured_boot.html
- Keylime policy tool (current measured-boot policy/reference-state authoring CLI): https://keylime.readthedocs.io/en/latest/user_guide/keylime_policy.html
- Keylime “durable attestation” framing (attestation as audit/time series): https://next.redhat.com/2023/04/25/keylimes-durable-attestation-makes-security-auditable/
- Red Hat blog (PCR vs TPM event log intuition): https://www.redhat.com/en/blog/attestation-confidential-computing
- Google go-tpm-tools (event log parsing + attestation verification libs): https://github.com/google/go-tpm-tools
- Google go-eventlog (event-log replay/verification helpers): https://github.com/google/go-eventlog
- Microsoft MU “TPM replay event log” schema docs (alternate canonicalization reference): https://microsoft.github.io/mu/dyn/mu_plus/TpmTestingPkg/TpmReplayPei/Tool/TpmReplaySchema/
- systemd-measure (PCR pre-calculation for UKI): https://www.freedesktop.org/software/systemd/man/systemd-measure.html
- systemd-pcrlock (variant-aware PCR policy authoring / prediction): https://www.freedesktop.org/software/systemd/man/latest/systemd-pcrlock.html
- UAPI Group: Unified Kernel Image (UKI) specification (canonical section measurement semantics): https://uapi-group.org/specifications/specs/unified_kernel_image/
- UAPI Group: Linux TPM PCR Registry (published semantics for what measures into which PCR): https://github.com/uapi-group/specifications/blob/main/specs/linux_tpm_pcr_registry.md
- Keylime architecture overview (agent/verifier/registrar components; practical workflow): https://keylime.dev/blog/2024/02/07/remote-attestation-blog-part1.html
- RHEL 9 security hardening: Keylime integration guide (ops framing + actions): https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/9/html/security_hardening/assembly_ensuring-system-integrity-with-keylime_security-hardening
- SUSE Micro Keylime guide (workload/verifier/registrar deployment notes): https://documentation.suse.com/sle-micro/6.0/html/Micro-keylime/index.html
- systemd-stub TPM PCR notes (UKI measurement details): https://man7.org/linux/man-pages/man7/systemd-stub.7.html
- systemd phase markers (pcrphase): https://www.freedesktop.org/software/systemd/man/systemd-pcrphase.service.html
- systemd doc: TPM2 PCR measurements overview: https://systemd.io/TPM2_PCR_MEASUREMENTS/
- TCG TPM2 Library Part 1 (policy/PCR primitives): https://trustedcomputinggroup.org/wp-content/uploads/Trusted-Platform-Module-2.0-Library-Part-1-Architecture-Version-184-rc2_20Dec24.pdf
- BSDCan 2019 talk: improving security of the FreeBSD boot process (TPM/measured boot): https://papers.freebsd.org/2019/bsdcan/stanek-improving_security_of_the_freebsd_boot_process/

## Firmware updates (UEFI capsules / LVFS / fwupd)

- UEFI spec: Firmware Update and Reporting (capsules + ESRT): https://uefi.org/specs/UEFI/2.11/23_Firmware_Update_and_Reporting.html
- LVFS intro (why a firmware service exists): https://lvfs.readthedocs.io/en/latest/intro.html
- fwupd overview: https://fwupd.org/
- fwupdmgr docs (notes `--json` output exists, terminal output not stable): https://fwupd.github.io/libfwupdplugin/fwupdmgr.html
- fwupd UEFI capsule plugin notes (ESRT + UpdateCapsule constraints): https://fwupd.github.io/libfwupdplugin/uefi-capsule-README.html
- LVFS download guidance (client metadata + server-side gating to avoid bad updates): https://lvfs.readthedocs.io/en/latest/download.html
- NIST SP 800-193 (protect / detect / recover framing for platform firmware resiliency): https://csrc.nist.gov/pubs/sp/800/193/final
- Windows UEFI firmware update platform (UpdateCapsule guidance): https://learn.microsoft.com/en-us/windows-hardware/drivers/bringup/windows-uefi-firmware-update-platform
- Microsoft Secure Boot overview + 2026 certificate expiry note: https://learn.microsoft.com/en-us/windows-hardware/design/device-experiences/oem-secure-boot
- Microsoft Secure Boot status report (fleet readiness surface): https://learn.microsoft.com/en-us/windows/deployment/windows-autopatch/monitor/secure-boot-status-report
- Microsoft Windows Server blog: Prepare your servers for Secure Boot certificate updates (server rollout guidance): https://www.microsoft.com/en-us/windows-server/blog/2026/02/23/prepare-your-servers-for-secure-boot-certificate-updates/
- Microsoft support: When Secure Boot certificates expire on Windows devices (customer/device remediation guidance): https://support.microsoft.com/en-us/topic/when-secure-boot-certificates-expire-on-windows-devices-c83b6afd-a2b6-43c6-938e-57046c80c1c2
- LVFS: signing and vendor separation notes (security model): https://blogs.gnome.org/hughsie/2019/12/11/improving-the-security-model-of-the-lvfs/

- FreeBSD fwget(8) (driver firmware packages; firmware(9) lane): https://man.freebsd.org/cgi/man.cgi?fwget%288%29=
- FreeBSD efivar(8) (manage UEFI environment variables): https://man.freebsd.org/efivar

## Hardware inventory / device topology

- FreeBSD devinfo(8): https://man.freebsd.org/devinfo%288%29
- FreeBSD pciconf(8): https://man.freebsd.org/pciconf%288%29
- FreeBSD usbconfig(8) (`ugenX.Y` addressing plus current descriptor/summary/interface-driver inspection): https://man.freebsd.org/usbconfig%288%29
- FreeBSD devmatch(8) (unattached-device / module-match inspection): https://man.freebsd.org/devmatch%288%29
- systemd hwdb(7) (modalias-like hardware database): https://www.freedesktop.org/software/systemd/man/hwdb.html
- fwupd `hwids` command docs (stable machine hardware IDs / GUIDs): https://fwupd.github.io/libfwupdplugin/fwupdmgr.html
- NixOS: nixos-generate-config (hardware-configuration.nix as a declarative hardware snapshot): https://wiki.nixos.org/wiki/Nixos-generate-config
- Fuchsia driver binding (device topology + match/bind programs): https://fuchsia.dev/fuchsia-src/concepts/drivers/driver_binding
- Ubuntu Certified hardware catalog (published supported-device catalog): https://ubuntu.com/certified
- Ubuntu Desktop Certified Hardware Programme guide (systems remain certified for the life cycle of the Ubuntu release against which they were certified): https://certification.canonical.com/docs/programmes/desktop/Desktop_Programme_Guide/
- Ubuntu Server Hardware Certification Overview (certification is tied to the Ubuntu Server LTS version against which the server was certified): https://certification.canonical.com/docs/programmes/server/Programme_Guide/
- Ubuntu IoT and device services (continuous testing of certified devices across updates/security patches): https://ubuntu.com/pricing/devices
- Ubuntu Stable Release Updates: special types / hardware enablement criteria (new hardware support on stable/LTS trains needs explicit criteria): https://documentation.ubuntu.com/project/SRU/reference/special/
- Android Compatibility Definition Document (per-release compatibility policy / hardware requirements): https://source.android.com/docs/compatibility/cdd
- Android Compatibility program overview (CDD + CTS + self-test framing): https://source.android.com/docs/compatibility/overview
- Android Compatibility Test Suite (CTS) overview (official compatibility test suite): https://source.android.com/docs/compatibility/cts
- Android Vendor Test Suite (VTS) and infrastructure (kernel/HAL-oriented compatibility suite): https://source.android.com/docs/core/tests/vts
- Red Hat hardware certification intro (official compatibility/certification program): https://docs.redhat.com/en/documentation/red_hat_hardware_certification/2025/html/red_hat_hardware_certification_quick_start_guide/con_introduction-to-red-hat-hardware-certification_hw-quick-start
- Red Hat hardware certification policies (model-specific test plans + published supported-feature statuses): https://docs.redhat.com/en/documentation/red_hat_hardware_certification/2025/html/red_hat_hardware_certification_program_policy_guide/assembly_hardware-certification-policies_hw-pol-cert-process-overview
- Red Hat Hardware Certification Program Policy Guide (certification is specific to a RHEL major version and architecture): https://docs.redhat.com/en/documentation/red_hat_hardware_certification/2026/html-single/red_hat_hardware_certification_program_policy_guide/index
- Red Hat Hardware Certification Test Suite User Guide (official methodology + results-evaluation guide): https://docs.redhat.com/en/documentation/red_hat_hardware_certification/2025/html/red_hat_hardware_certification_test_suite_user_guide/index
- Windows Hardware Lab Kit (HLK) overview: https://learn.microsoft.com/en-us/windows-hardware/test/hlk/
- Windows HLK compatibility-playlist notes: https://learn.microsoft.com/en-us/windows-hardware/test/hlk/what-s-new-in-the-hardware-lab-kit
- Windows HLK Step 6 / official playlist version matching: https://learn.microsoft.com/en-us/windows-hardware/test/hlk/getstarted/step-6-select-and-run-tests
- osquery PCI inventory table docs: https://fleetdm.com/tables/pci_devices
- osquery USB inventory table docs: https://fleetdm.com/tables/usb_devices

- osquery documentation (tables, flags, extensions): https://osquery.readthedocs.io/
- Introducing osquery (Facebook Engineering): https://engineering.fb.com/2014/10/29/security/introducing-osquery/
- GraphQL introduction (query ergonomics inspiration): https://graphql.org/learn/introduction/

## Boot assessment / try-counters

- UAPI Boot Loader Specification (tries-left/tries-done): https://uapi-group.org/specifications/specs/boot_loader_specification/
- systemd Automatic Boot Assessment (implementation notes on BLS counters): https://systemd.io/AUTOMATIC_BOOT_ASSESSMENT/
- U-Boot Boot Count Limit (bootcount/bootlimit): https://docs.u-boot.org/en/latest/api/bootcount.html

## Declarative disk layouts + atomic deployments (install/recovery inspirations)

- systemd-repart(8) (declarative GPT partitioning; additive apply semantics): https://www.freedesktop.org/software/systemd/man/systemd-repart.html
- Lennart Poettering: "Discoverable GPT disk images" (layout conventions + repart usage): https://0pointer.net/blog/the-wondrous-world-of-discoverable-gpt-disk-images.html
- Nix disko (disk layout as code): https://github.com/nix-community/disko
- OSTree atomic upgrades (multi-deployment, power-loss safe transitions): https://ostreedev.github.io/ostree/atomic-upgrades/
- OSTree deployments (deployment layout + booting exactly one deployment): https://ostreedev.github.io/ostree/deployment/
- ZFSBootMenu (recovery shell UX around boot environments; tooling image as a product): https://zfsbootmenu.org/
- LinuxBoot (boot payloads as artifacts): https://book.linuxboot.org/
- LWN: replacing x86 firmware with Linux and Go (LinuxBoot context): https://lwn.net/Articles/738649/
- u-root releases (one-binary initramfs userspace): https://github.com/u-root/u-root/releases
- u-root (one-binary initramfs userspace): https://github.com/u-root/u-root


## Fetch stack (FreeBSD)

- fetch(1): https://man.freebsd.org/cgi/man.cgi?query=fetch&sektion=1
- fetch(3): https://man.freebsd.org/fetch%283%29
- verify(1): https://man.freebsd.org/cgi/man.cgi?query=verify&sektion=1

## Capsicum/Casper

- capsicum(4): https://man.freebsd.org/cgi/man.cgi?query=capsicum&sektion=4
- cap_enter(2): https://man.freebsd.org/cgi/man.cgi?query=cap_enter&sektion=2
- cap_rights_limit(2): https://man.freebsd.org/cgi/man.cgi?query=cap_rights_limit&sektion=2
- cap_rights_init(3): https://man.freebsd.org/cgi/man.cgi?query=cap_rights_init&sektion=3
- open(2): https://man.freebsd.org/cgi/man.cgi?query=open&sektion=2
- chflags(2): https://man.freebsd.org/cgi/man.cgi?query=chflags&sektion=2
- rights(4): https://man.freebsd.org/cgi/man.cgi?query=rights&sektion=4
- closefrom(2): https://man.freebsd.org/cgi/man.cgi?query=closefrom&sektion=2
- posix_spawn_file_actions_addclosefrom_np(3): https://man.freebsd.org/cgi/man.cgi?query=posix_spawn_file_actions_addclosefrom_np&sektion=3
- fexecve(2): https://man.freebsd.org/cgi/man.cgi?query=fexecve&sektion=2
- libcasper(3): https://man.freebsd.org/cgi/man.cgi?query=libcasper&sektion=3
- Capsicum and Casper paper (PDF): https://people.freebsd.org/~pjd/pubs/Capsicum_and_Casper.pdf


## DNS privacy / mediated resolution

- RFC 9076 DNS Privacy Considerations: https://www.rfc-editor.org/rfc/rfc9076.html
- RFC 9156 DNS Query Name Minimisation to Improve Privacy: https://www.rfc-editor.org/rfc/rfc9156.html

## Portals / powerbox (mediated capability acquisition)

These references help anchor the workstation transfer split used in `docs/671-workstation-ordinary-datatransfer-baseline-stays-frozen-and-richer-lanes-are-rfc-first.md` and `docs/672-workstation-richer-datatransfer-lanes-mint-distinct-artifact-families.md`: narrow ordinary picker/transfer lanes should stay visibly separate from broader mediated document/provider lanes.

- Towards oblivious sandboxing with Capsicum (powerbox concept): https://www.engr.mun.ca/~anderson/publications/2017/towards-oblivious-sandboxing.pdf
- vBSDCon slides variant (Capsh/libpreopen concept): https://papers.freebsd.org/2017/vbsdcon/anderson-Towards_Oblivious_SandBoxing.files/anderson-Towards_Oblivious_SandBoxing.pdf
- XDG Desktop Portal overview: https://flatpak.github.io/xdg-desktop-portal/
- Android Photo Picker (official docs): https://developer.android.com/training/data-storage/shared/photopicker
- Android Storage Access Framework / document provider (official docs): https://developer.android.com/guide/topics/providers/document-provider
- Android shared-storage documents/files guide (`ACTION_OPEN_DOCUMENT_TREE` directory-tree access behavior): https://developer.android.com/training/data-storage/shared/documents-files
- Android shared-storage documents/files guide (`ACTION_CREATE_DOCUMENT` cannot overwrite an existing file; same-name save appends a numeric suffix): https://developer.android.com/training/data-storage/shared/documents-files
- WICG File System Access / showDirectoryPicker (directory handle permission model): https://wicg.github.io/file-system-access/
- POSIX ar utility (historical archive member naming; final pathname component unless using non-portable extensions): https://pubs.opengroup.org/onlinepubs/9699919799/utilities/ar.html
- GNU tar manual: multiple members with the same name (duplicate member names can overwrite earlier extraction results): https://www.gnu.org/software/tar/manual/html_node/multiple.html
- GNU tar manual: Restoring Intermediate Directories (extracting nested members can recreate intermediate directories with default metadata unless directory entries are present): https://www.gnu.org/software/tar/manual/html_node/intermediate-directories.html
- Python changelog: ZIP files created by distutils will now include entries for directories: https://docs.python.org/3.9/whatsnew/changelog.html
- Flatpak portal model (sandbox permissions): https://docs.flatpak.org/en/latest/sandbox-permissions.html
- xdg-desktop-portal repo (DBus interfaces under org.freedesktop.portal.Desktop): https://github.com/flatpak/xdg-desktop-portal

## Attenuating delegation tokens (Macaroons / Biscuit)

- Macaroons paper (NDSS 2014, PDF): https://theory.stanford.edu/~ataly/Papers/macaroons.pdf
- NDSS page (Macaroons abstract): https://www.ndss-symposium.org/ndss2014/ndss-2014-programme/macaroons-cookies-contextual-caveats-decentralized-authorization-cloud/
- Biscuit docs: introduction (offline attenuation): https://doc.biscuitsec.org/getting-started/introduction.html
- Biscuit blog: third-party blocks (delegation patterns): https://www.biscuitsec.org/blog/third-party-blocks-why-how-when-who/

## Capability-centric sandboxing ergonomics (pledge/unveil)

- OpenBSD pledge(2): https://man.openbsd.org/pledge.2
- OpenBSD unveil(2): https://man.openbsd.org/unveil.2
- Pledge/Unveil paper (BSDCan 2018): https://www.openbsd.org/papers/BeckPledgeUnveilBSDCan2018.pdf

## Capability routing / explicit grants (Fuchsia lessons)

- Fuchsia capabilities (concepts): https://fuchsia.dev/fuchsia-src/concepts/components/v2/capabilities
- Fuchsia component manifest (.cml) reference (source → compiled manifest): https://fuchsia.dev/reference/cml
- Fuchsia component manifests overview (CML and compilation): https://fuchsia.dev/fuchsia-src/concepts/components/v2/component_manifests
- Fuchsia RFC-0093 — component manifest design principles (human source vs backend format): https://fuchsia.dev/fuchsia-src/contribute/governance/rfcs/0093_component_manifest_design_principles
- Fuchsia principles (capability routing as access control): https://fuchsia.dev/fuchsia-src/contribute/contributing-to-cf/original_principles
- Fuchsia Realm Builder (build test topologies in code): https://fuchsia.dev/fuchsia-src/development/testing/components/realm_builder
- Fuchsia integration testing topologies (realm builder vs static manifests): https://fuchsia.dev/fuchsia-src/development/testing/components/integration_testing
- Fuchsia components intro (sandboxed modules + capabilities): https://fuchsia.dev/fuchsia-src/get-started/learn/intro/components

## Capability routing / component frameworks (Genode lessons)

- Genode Foundations documentation index: https://genode.org/documentation/genode-foundations/25.05/index.html
- Genode init component (policy-driven component tree): https://genode.org/documentation/genode-foundations/21.05/system_configuration/The_init_component.html
- Genode capability-based security overview: https://genode.org/documentation/genode-foundations/20.05/architecture/Capability-based_security.html

## Type-safe kernels (Tock) / syscall boundary lessons

- Tock syscall model documentation (subscribe/allow/command): https://book.tockos.org/doc/syscalls
- Weisblat thesis: syscall-boundary safety in a type-safe OS (Tock case study): https://www.ll.mit.edu/sites/default/files/publication/doc/improving-security-system-call-boundary-type-safe-weisblat-thesis-weisblat.pdf

## Verified execution (MAC/veriexec)

- FreeBSD Handbook: Mandatory Access Control (MAC) framework: https://docs.freebsd.org/en/books/handbook/mac/
- FreeBSD review: MAC/veriexec (verified execution): https://reviews.freebsd.org/D8554
- FreeBSD review: verifying loader for mac_veriexec: https://reviews.freebsd.org/D16575
- mac_bsdextended(4) (filesystem access controls): https://man.freebsd.org/cgi/man.cgi?query=mac_bsdextended
- HardenedBSD Integriforce (hash-enforced exec allowlisting): https://hardenedbsd.org/content/projects
- HardenedBSD Integriforce article / call for testing: https://hardenedbsd.org/article/shawn-webb/2015-03-11/call-testing-secadm-integriforce
- rc.subr(8) mentions mac_veriexec integration points: https://man.freebsd.org/rc.subr%288%29

## Verified execution (NetBSD Veriexec)

- NetBSD guide chapter: Veriexec subsystem: https://www.netbsd.org/docs/guide/en/chap-veriexec.html
- veriexec(8) man page: https://man.netbsd.org/veriexec.8

## Auditing (OpenBSM)

- FreeBSD Handbook: Auditing: https://docs.freebsd.org/en/books/handbook/audit/
- auditd(8): https://man.freebsd.org/cgi/man.cgi?query=auditd&sektion=8
- auditreduce(1): https://man.freebsd.org/cgi/man.cgi?query=auditreduce&sektion=1
- praudit(1): https://man.freebsd.org/cgi/man.cgi?query=praudit&sektion=1
- OpenBSM overview (TrustedBSD): https://www.trustedbsd.org/openbsm.html

## Observability

- FreeBSD Handbook: DTrace: https://docs.freebsd.org/en/books/handbook/dtrace/
- FreeBSD dtrace(1): https://man.freebsd.org/cgi/man.cgi?query=dtrace&sektion=1
- Oracle Solaris Dynamic Tracing Guide: https://docs.oracle.com/cd/E19253-01/817-6223/index.html

## Reproducible builds (FreeBSD)

- FreeBSD wiki (Ports reproducibility): https://wiki.freebsd.org/ReproducibleBuilds/Ports
- poudriere issue re SOURCE_DATE_EPOCH: https://github.com/freebsd/poudriere/issues/1287

## Reproducible builds (build records / `.buildinfo`)

- Debian buildinfo files (what is recorded): https://wiki.debian.org/ReproducibleBuilds/BuildinfoFiles
- Reproducible Builds, “Variations in the build environment” (filesystem ordering, locale, and other environment-dependent nondeterminism): https://reproducible-builds.org/docs/env-variations/
- Reproducible Builds, “Stable order for outputs” (stable sorting and locale-independent ordering guidance): https://reproducible-builds.org/docs/stable-outputs/
- reproduce.debian.net (attempts rebuilds using `.buildinfo`): https://reproduce.debian.net/
- Debian reproducible builds overview (project status + guidance): https://wiki.debian.org/ReproducibleBuilds
- Reproducible Builds project tools overview: https://reproducible-builds.org/tools/
- diffoscope (deep recursive diffs): https://diffoscope.org/
- Reproducible Builds: SOURCE_DATE_EPOCH (time normalization convention): https://reproducible-builds.org/docs/source-date-epoch/
- Debian strip-nondeterminism project (targeted metadata normalization): https://salsa.debian.org/reproducible-builds/strip-nondeterminism
- OSS-Rebuild stabilizers (normalization helpers for functional equivalence testing): https://docs.oss-rebuild.dev/stabilizers/


## Zig toolchain wedge (cross-compilation helper)

- Zig project home: https://ziglang.org/
- Zig overview (language + toolchain model): https://ziglang.org/learn/overview/
- Zig release notes (0.15.1): https://ziglang.org/download/0.15.1/release-notes.html
- Andrew Kelley: zig cc as a drop-in C/C++ compiler frontend: https://andrewkelley.me/post/zig-cc-powerful-drop-in-replacement-gcc-clang.html


## Ports collection

- FreeBSD Handbook: Packages and Ports: https://docs.freebsd.org/en/books/handbook/ports/

## Repository signing inspiration

- pkg-repo(8): https://man.freebsd.org/pkg-repo%288%29
- OpenBSD signify(1) (small signatures, no GPG): https://man.openbsd.org/signify
- pkg-audit(8): https://man.freebsd.org/pkg-audit
- Porters Handbook: Security / VuXML: https://docs.freebsd.org/en/books/porters-handbook/security/
- VuXML site: https://vuxml.freebsd.org/

## Vulnerability intelligence + update security

- OSV schema: https://ossf.github.io/osv-schema/
- OSV database: https://osv.dev/
- OSV API docs (query by version/commit; batch queries): https://google.github.io/osv.dev/api/
- TUF specification: https://theupdateframework.github.io/specification/latest/
- TUF specification (official latest): https://theupdateframework.io/specification/latest/
- TUF docs: roles and metadata: https://theupdateframework.io/docs/metadata/
- TUF roles and metadata (official docs): https://theupdateframework.io/docs/metadata/
- OSTree static deltas for offline updates (self-contained delta files): https://ostreedev.github.io/ostree/copying-deltas/
- RAUC update bundles (signed offline artifacts): https://rauc.readthedocs.io/en/latest/basic.html

## Hashing

- BLAKE3 specs repo: https://github.com/BLAKE3-team/BLAKE3-specs

## Transparency logs

- Sigstore Bundle Format: https://docs.sigstore.dev/about/bundle/
- sigstore Rekor overview: https://docs.sigstore.dev/logging/overview/
- Rekor repo: https://github.com/sigstore/rekor
- Trillian transparent logging guide (general purpose append-only logs): https://google.github.io/trillian/docs/TransparentLogging.html
- transparency.dev (logs as a verifiable transport layer): https://transparency.dev/articles/logs-a-verifiable-transport-layer/
- Sigsum overview (lightweight key-usage transparency): https://www.sigsum.org/
- Sigsum design notes: https://git.sigsum.org/sigsum/tree/doc/design.md
- Filippo Valsorda: Building a Transparent Keyserver (tlog pattern): https://words.filippo.io/keyserver-tlog/
- Go sumdb transparency log proposal/design: https://go.googlesource.com/proposal/+/master/design/25530-sumdb.md
- Go `tlog` package (CT-compatible proofs): https://pkg.go.dev/golang.org/x/mod/sumdb/tlog
- Trail of Bits: Catching malicious package releases using a transparency log (monitor ergonomics): https://blog.trailofbits.com/2025/12/12/catching-malicious-package-releases-using-a-transparency-log/

## Supply-chain transparency registries (SCITT)

- IETF SCITT WG (about/charter): https://datatracker.ietf.org/group/scitt/about/
- SCITT architecture draft (Datatracker): https://datatracker.ietf.org/doc/draft-ietf-scitt-architecture/
- SCITT COSE receipts with CCF profile draft: https://datatracker.ietf.org/doc/draft-ietf-scitt-receipts-ccf-profile/

## Update rollout + cohorting

- Chromium Omaha protocol (v4) doc: https://chromium.googlesource.com/chromium/src/+/refs/tags/135.0.7020.1/docs/updater/protocol_4.md
- google/omaha repo (updater engine): https://github.com/google/omaha

- Zincati auto-updates overview (phased rollouts, wariness): https://coreos.github.io/zincati/usage/auto-updates/
- Cincinnati protocol (update graph DAG): https://coreos.github.io/zincati/development/cincinnati/protocol/
- OpenShift Update Service (built on Cincinnati): https://www.redhat.com/en/blog/openshift-update-service-update-manager-for-your-cluster

- Bottlerocket Update Operator (Brupop) docs: https://bottlerocket.dev/en/brupop/
- Brupop repo: https://github.com/bottlerocket-os/bottlerocket-update-operator
- Bottlerocket updates + waves (TUF + wave schedules talk): https://d1.awsstatic.com/events/reinvent/2020/Securing_Bottlerocket_updates_with_TUF_and_Rust_OPN401.pdf

- Uptane deployment best practices (Director decisions): https://uptane.org/docs/latest/deployment/best-practices
- Uptane Standard for Design and Implementation (v2.1.0): https://uptane.org/docs/2.1.0/standard/uptane-standard
- Android virtual A/B overview (OTA mechanics): https://source.android.com/docs/core/ota/virtual_ab

## PF anchors + socket activation (inbound/outbound policy)

- OpenBSD PF anchors FAQ: https://www.openbsd.org/faq/pf/anchors.html
- OpenBSD pf.conf(5): ANCHORS: https://man.openbsd.org/pf.conf
- FreeBSD pfctl(8): anchors (-a): https://man.freebsd.org/pfctl
- FreeBSD pf.conf(5): https://man.freebsd.org/cgi/man.cgi?query=pf.conf&sektion=5

- systemd socket activation overview (developer note): https://0pointer.de/blog/projects/socket-activation.html
- systemd.socket(5) (socket unit semantics): https://www.freedesktop.org/software/systemd/man/systemd.socket.html
- systemd-socket-activate(1) (test/CLI wrapper): https://www.freedesktop.org/software/systemd/man/systemd-socket-activate.html
- OpenBSD authpf FAQ (authenticated, session-bound PF anchor loading): https://www.openbsd.org/faq/pf/authpf.html
- Qubes OS 4.1 release notes (remote support remains opt-in; no new ports/connections open by default): https://doc.qubes-os.org/en/latest/developer/releases/4_1/release-notes.html
- FreeBSD inetd(8) “super-server”: https://man.freebsd.org/cgi/man.cgi?query=inetd&sektion=8

## Device nodes and jails (FreeBSD devfs rulesets)

- FreeBSD jail(8): note on limiting device nodes in per-jail devfs: https://man.freebsd.org/cgi/man.cgi?query=jail&sektion=8
- devfs(8): device filesystem administration: https://man.freebsd.org/cgi/man.cgi?query=devfs&sektion=8
- devfs.rules(5): ruleset configuration format: https://man.freebsd.org/cgi/man.cgi?query=devfs.rules&sektion=5
- devd(8): device state change daemon: https://man.freebsd.org/cgi/man.cgi?devd%288%29=
- devd.conf(5): attach/detach event rules and actions, plus VFS mount/unmount notifications: https://man.freebsd.org/cgi/man.cgi?query=devd.conf&sektion=5&manpath=FreeBSD+15.0-RELEASE+and+Ports.quarterly
- automountd(8): autofs mount-request daemon (useful reminder that host automount is an existing convenience surface that DeriveBSD is intentionally not treating as baseline removable-media authority): https://man.freebsd.org/cgi/man.cgi?query=automountd&sektion=8&manpath=FreeBSD+15.0-RELEASE+and+Ports.quarterly
- FreeBSD Handbook: Jails chapter (current operational context for jails + devfs): https://docs.freebsd.org/en/books/handbook/jails/
- FreeBSD `fstyp(8)` (machine-parsable probe; recognizes multiple filesystem families and runs sandboxed using Capsicum): https://man.freebsd.org/fstyp%288%29
- FreeBSD `mount(8)` (generic mount flags including `noexec`, `nosuid`, `nosymfollow`, and `untrusted`; useful as the host-side hardening vocabulary for the local removable-media fallback): https://man.freebsd.org/cgi/man.cgi?mount%288%29=
- FreeBSD `umount(8)` (host-side unmount/cleanup vocabulary; useful when the removable-medium session should end immediately after verified capture rather than after later processing): https://man.freebsd.org/cgi/man.cgi?query=umount&sektion=8
- FreeBSD Handbook: Other File Systems (current FAT / exFAT / NTFS / HFS+ operational notes): https://docs.freebsd.org/en/books/handbook/filesystems/
- FreeBSD `mount_msdosfs(8)` (MS-DOS/FAT mount helper; `-u` / `-g` / `-m` / `-M` show how ownership and permission ceilings are mount-rendered rather than source-truth): https://man.freebsd.org/mount_msdosfs%288%29
- FreeBSD `mount.exfat-fuse(8)` (exFAT helper; `uid` / `gid` / `umask` / `dmask` / `fmask` show how owner/mode semantics are receiver-local mount choices here too): https://man.freebsd.org/mount.exfat-fuse
- FreeBSD `mount_cd9660(8)` (ISO-9660 helper; Joliet / Rock Ridge / version-handling knobs matter for naming semantics, and `-U` / `-G` / `-m` show how owner/group/mask defaults can be synthesized): https://man.freebsd.org/cgi/man.cgi?format=html&query=mount_cd9660&sektion=8
- FreeBSD `mount_nullfs(8)` (project a mounted subtree elsewhere in the namespace): https://man.freebsd.org/mount_nullfs
- FreeBSD `file(1)` (classify one selected file and emit MIME/type strings; useful reminder that file classification is not the same thing as reviewed tree semantics): https://man.freebsd.org/file%281%29
- FreeBSD `bsdtar(1)` (security notes cover absolute paths, `..`, and symlink-altered target directories during extraction; useful reminder that archive/tree semantics are their own lane): https://man.freebsd.org/cgi/man.cgi?format=html&query=bsdtar&sektion=1
- FreeBSD `camcontrol(8)` (SCSI inquiry surface can print device serial numbers; useful as current-device evidence but not a reason to auto-resume authority on reattach): https://man.freebsd.org/cgi/man.cgi?query=camcontrol
- FreeBSD `diskinfo(8)` (`-s` returns the disk ident, usually the serial number; useful as an operator hint rather than a durable trust root for the first removable-media fallback): https://man.freebsd.org/diskinfo%288%29

## USB quarantine domains (Qubes USB qubes)

- How to use USB devices (sys-usb workflow): https://doc.qubes-os.org/en/latest/user/how-to-guides/how-to-use-usb-devices.html
- Device handling security (USB stack and HID warning): https://doc.qubes-os.org/en/latest/user/security-in-qubes/device-handling-security.html
- Qubes architecture (USB stacks/drivers sandboxed): https://doc.qubes-os.org/en/latest/developer/system/architecture.html
- How to use devices (overview of device attach): https://doc.qubes-os.org/en/latest/user/how-to-guides/how-to-use-devices.html
- USBGuard home (explicit USB device authorization framework): https://usbguard.github.io/
- USBGuard rule language (allow/block/reject; implicit default block): https://usbguard.github.io/documentation/rule-language

## Quarantine metadata + origin labels (macOS/Windows)

- Apple: LSFileQuarantineEnabled (File Quarantine opt-in): https://developer.apple.com/documentation/bundleresources/information-property-list/lsfilequarantineenabled
- Apple: quarantineProperties (remove quarantine by setting nil): https://developer.apple.com/documentation/foundation/urlresourcevalues/quarantineproperties
- Microsoft: Zone.Identifier stream name (Mark-of-the-Web): https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-fscc/6e3f7352-d11c-4d76-8c39-2516a9df36e8
- FreeBSD: extattr(2) (VFS extended attributes): https://man.freebsd.org/extattr
- Microsoft: AttachmentManager policy CSP (preserve zone information in file attachments): https://learn.microsoft.com/en-us/windows/client-management/mdm/policy-csp-attachmentmanager
- FreeBSD: extattr(9) (named extended-attribute semantics): https://man.freebsd.org/extattr%289%29

## Formal methods (TLA+)

- TLA+ home (Lamport): https://lamport.azurewebsites.net/tla/tla.html
- TLA+ overview (Lamport): https://lamport.azurewebsites.net/tla/high-level-view.html
- TLA+ tools page (TLC/TLAPS): https://lamport.azurewebsites.net/tla/tools.html
- TLA+ tools / Toolbox repo: https://github.com/tlaplus/tlaplus
- TLA+ wiki (getting started): https://docs.tlapl.us/
- TLC model checker start: https://docs.tlapl.us/using:tlc:start
- Learn TLA+ (invariants): https://learntla.com/core/invariants.html
- Alloy (lightweight relational modeling): https://alloytools.org/

## Formal verification (seL4 proofs as artifacts)

- seL4 overview: https://sel4.systems/
- EverParse (formally proven message parsers; high-assurance parser wedge): https://www.microsoft.com/en-us/research/blog/everparse-hardening-critical-attack-surfaces-with-formally-proven-message-parsers/
- seL4 whitepaper: https://sel4.systems/About/seL4-whitepaper.pdf
- “Comprehensive formal verification of an OS microkernel” (Klein et al., 2014): https://sel4.systems/Research/pdfs/comprehensive-formal-verification-os-microkernel.pdf
- seL4 verification project background: https://trustworthy.systems/projects/OLD/seL4-verification/

## Bootable host images over OCI (bootc)

- bootc project site: https://bootc-dev.github.io/bootc/
- CNCF project page (context/status): https://www.cncf.io/projects/bootc/
- Fedora bootc docs (getting started): https://docs.fedoraproject.org/en-US/bootc/getting-started/
- Update-size optimization note (layer isolation): https://developers.redhat.com/articles/2025/11/03/reduce-bootc-system-update-size
- OCI Image Specification (manifest/index + digest model): https://github.com/opencontainers/image-spec/blob/main/spec.md

## Lazy-pulling + mountable verified image trees

- casync repo: https://github.com/systemd/casync
- casync design notes: https://0pointer.net/blog/casync-a-tool-for-distributing-file-system-images.html
- CernVM-FS docs root: https://cvmfs.readthedocs.io/
- composefs project repo: https://github.com/composefs/composefs
- composefs state-of-the-union (Larsson): https://blogs.gnome.org/alexl/2023/07/11/composefs-state-of-the-union/
- mkcomposefs(1) (Arch manpage): https://man.archlinux.org/man/mkcomposefs.1.en

- stargz-snapshotter overview (containerd): https://github.com/containerd/stargz-snapshotter/blob/main/docs/overview.md
- buildkit lazy-pulling guide (eStargz): https://crazymax.dev/buildkit/user-guides/lazy-pulling/

- Nydus docs: https://nydus.dev/
- Nydus repo (DragonflyOSS): https://github.com/dragonflyoss/nydus
- nydus-snapshotter (containerd integration): https://github.com/containerd/nydus-snapshotter

- CernVM-FS overview (on-demand metadata/files over HTTP caches): https://cvmfs.readthedocs.io/en/stable/cpt-overview.html
- CernVM-FS implementation notes (catalog/TTL details): https://cvmfs.readthedocs.io/en/stable/cpt-details.html

## P2P distribution (fleet-scale artifact delivery)

- Dragonfly (d7y) docs: https://d7y.io/docs/
- Dragonfly repo: https://github.com/dragonflyoss/dragonfly
- CNCF blog (Dragonfly overview + multi-cluster use): https://www.cncf.io/blog/2023/09/01/using-dragonfly-to-distribute-images-and-files-for-multi-cluster-kuberenetes/

## Structured diagnostics trees (Inspect-style)

- Fuchsia Inspect overview (concepts + tooling): https://fuchsia.dev/fuchsia-src/development/diagnostics/inspect
- Fuchsia diagnostics concept (Archivist + ArchiveAccessor): https://fuchsia.dev/fuchsia-src/concepts/components/diagnostics
- Inspect discovery and hosting details: https://fuchsia.dev/fuchsia-src/reference/diagnostics/inspect/tree
- fuchsia.diagnostics protocol reference (ArchiveAccessor and friends): https://fuchsia.dev/reference/fidl/fuchsia.diagnostics
- RFC-0168 (Inspect exposure via InspectSink): https://fuchsia.dev/fuchsia-src/contribute/governance/rfcs/0168_exposing_inspect_through_inspectsink

## Flight recorder tracing (circular buffers)

- Microsoft: ETW logging sessions (in-memory buffers, kernel-managed): https://learn.microsoft.com/en-us/windows-hardware/test/wpt/sessions

## Plan 9 archival snapshots (Fossil/Venti)

- Fossil paper (archival file server): https://p9f.org/sys/doc/fossil.pdf
- Fossil docs source (9p.io): https://9p.io/sources/plan9/sys/doc/fossil.ms
- Venti (FAST'02 paper): https://www.usenix.org/conference/fast-02/venti-new-approach-archival-data-storage

## Inferno (distributed namespaces, Styx/9P)

- Inferno OS (project site): https://inferno-os.org/inferno/
- “The Inferno Operating System” (Ritchie et al., Bell Labs Technical Journal, 1997): https://www.mrynet.com/FTP/os/inferno/paper01.pdf

## Singularity (manifests + contract-based channels)

- Singularity project (overview): https://www.microsoft.com/en-us/research/project/singularity/
- “An Overview of the Singularity Project” (MSR TR-2005-135): https://www.microsoft.com/en-us/research/wp-content/uploads/2005/10/tr-2005-135.pdf
- “Singularity: Rethinking the Software Stack” (OSR 2007): https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/osr2007_rethinkingsoftwarestack.pdf

## Solaris/illumos Doors (FD-based lightweight RPC)

- Oracle Solaris 11.4 “Doors Overview”: https://docs.oracle.com/en/operating-systems/solaris/oracle-solaris/11.4/prog-interfaces/doors-overview.html
- illumos man page `door_call(3C)` (SmartOS mirror): https://smartos.org/man/3C/door_call

## MINIX 3 reliability + self-healing (reincarnation server)

- “A Lightweight Method for Building Reliable Operating Systems” (Herder et al.): https://www.minix3.org/doc/reliable-os.pdf
- “MINIX 3: Status Report and Current Research” (Tanenbaum, ;login: 2010): https://www.usenix.org/system/files/login/articles/61781-tanenbaum.pdf
- MINIX 3 OSR 2006 paper: https://minix3.org/doc/OSR-2006.pdf

## Capability kernels (KeyKOS/EROS)

- KeyKOS OSR paper (architecture overview): https://pdos.csail.mit.edu/6.828/2008/readings/keykos-osr.pdf
- Mark S. Miller et al., “Capability Myths Demolished” (attenuation, membranes, confinement): https://classpages.cselabs.umn.edu/Fall-2021/csci5271/papers/SRL2003-02.pdf
- Joe Duffy, “Objects as Secure Capabilities” (Midori lessons): https://joeduffyblog.com/2015/11/10/objects-as-secure-capabilities/
- “EROS: A fast capability system” (Shapiro et al.): https://flint.cs.yale.edu/cs428/doc/eros.pdf
- “Verifying the EROS confinement mechanism” (Shapiro et al.): https://flint.cs.yale.edu/cs428/doc/eros-verify.pdf

## Orthogonal persistence / single-level stores (EROS/CapROS/Grasshopper)

- CapROS overview (orthogonal persistence + capabilities): https://www.capros.org/overview.html
- "Design Evolution of the EROS Single-Level Store" (Shapiro, 2002): https://rcs.uwaterloo.ca/papers/sls.pdf
- "Grasshopper: An orthogonally persistent operating system" (Dearle et al.): https://archive.cs.st-andrews.ac.uk/gh/pub/gh-03.pdf

## Amoeba (immutable files + capability directories)

- "Amoeba: a distributed operating system for the 1990s" (Mullender et al.): https://www.cs.cornell.edu/home/rvr/papers/Amoeba1990s.pdf
- "The Amoeba Distributed Operating System – A Status Report" (Tanenbaum): https://www.cs.vu.nl/~ast/Publications/Papers/compcom-1991.pdf

## Nemesis (QoS firewalling + resource accounting)

- Nemesis project archive (overview): https://www.cl.cam.ac.uk/research/srg/netos/projects/archive/nemesis/
- "Self-Paging in the Nemesis Operating System" (Hand et al., OSDI 1999): https://www.usenix.org/events/osdi99/full_papers/hand/hand.pdf


## ZFS snapshot access pitfalls (permission changes)

- FreeBSD forum discussion: snapshots may remain readable after permissions change if snapshot dirs are exposed: https://forums.freebsd.org/threads/security-issues-with-snapshots-for-longer-term-backups.91178/

## Policy tracing / replay (OPA-shaped ergonomics)

- OPA tracing builtin (`trace()` / query explanations): https://www.openpolicyagent.org/docs/policy-reference/builtins/tracing
- OPA decision logs (audit + offline debugging): https://openpolicyagent.org/docs/management-decision-logs
- OPA policy testing framework: https://openpolicyagent.org/docs/policy-testing
- Cedar analysis toolkit (automated reasoning over auth policies): https://aws.amazon.com/blogs/opensource/introducing-cedar-analysis-open-source-tools-for-verifying-authorization-policies/
- Cedar language reference: https://docs.cedarpolicy.com/
- Qubes OS qrexec RPC policy (cross-domain comms governed by policy): https://doc.qubes-os.org/en/latest/user/advanced-topics/rpc-policy.html
- Qubes OS qrexec overview (secure inter-domain command/RPC mechanism): https://doc.qubes-os.org/en/latest/developer/services/qrexec.html
- Mutation testing of access-control policies (fault models/operators): https://dl.acm.org/doi/10.1145/1242572.1242663
- Conftest (OPA-based tests for structured config): https://openpolicyagent.org/ecosystem/entry/conftest

## Idempotent mutation / retry semantics

- IETF HTTPAPI Idempotency-Key draft (server lifecycle, expiry, duplicate handling, fingerprint/mismatch semantics): https://datatracker.ietf.org/doc/html/draft-ietf-httpapi-idempotency-key-header-07
- Stripe idempotent requests (same key returns first result; parameter mismatch with reused key is an error): https://docs.stripe.com/api/idempotent_requests
- Stripe low-level error handling (safe retries repeat the same request until outcome is clear; new parameters require a new key): https://docs.stripe.com/error-low-level
- RFC 6920 (Naming Things with Hashes): https://www.rfc-editor.org/rfc/rfc6920.html
- OCI image-spec descriptor digest rules (digest as content identifier; verify retrieved content against it): https://github.com/opencontainers/image-spec/blob/main/descriptor.md
- AWS Well-Architected REL04-BP04 (same request token should yield the same response, making retries operationally transparent): https://docs.aws.amazon.com/wellarchitected/2023-04-10/framework/rel_prevent_interaction_failure_idempotent.html
- AWS Well-Architected REL04-BP04 (latest path; same token should yield the same response, making retries operationally transparent): https://docs.aws.amazon.com/wellarchitected/latest/framework/rel_prevent_interaction_failure_idempotent.html

## Backups, replication, and restore drills

- CISA StopRansomware Guide (offline/encrypted backups + regular restore testing): https://www.cisa.gov/stopransomware/ransomware-guide
- NIST SP 800-184, Guide for Cybersecurity Event Recovery (recovery planning + checked backups): https://nvlpubs.nist.gov/nistpubs/specialpublications/nist.sp.800-184.pdf
- restic (content-addressed backups, snapshots): https://restic.net/
- restic restore documentation: https://restic.readthedocs.io/en/stable/050_restore.html
- BorgBackup (deduplicating backups): https://www.borgbackup.org/
- Tarsnap (encrypted, content-addressed backups): https://www.tarsnap.com/
- zrepl (ZFS replication + pruning automation): https://zrepl.github.io/
- Qubes OS backup/restore guide (explicit restore workflow and verify-only restore path): https://doc.qubes-os.org/en/latest/user/how-to-guides/how-to-back-up-restore-and-migrate.html
- Qubes OS emergency backup recovery (portable disaster-recovery format): https://doc.qubes-os.org/en/latest/user/how-to-guides/backup-emergency-restore-v4.html
- OpenZFS wiki: zrepl overview: https://openzfs.org/wiki/Zrepl
- sanoid/syncoid (ZFS snapshotting + replication): https://github.com/jimsalterjrs/sanoid

## Firmware updates (capsules) + UEFI variable tooling

- UEFI spec: Firmware Update and Reporting (capsules, UpdateCapsule, ESP delivery): https://uefi.org/specs/UEFI/2.11/23_Firmware_Update_and_Reporting.html
- UEFI 2.11 Secure Boot and Driver Signing chapter: https://uefi.org/specs/UEFI/2.11/32_Secure_Boot_and_Driver_Signing.html
- fwupd UEFI capsule plugin notes (how capsule updates are staged/applied): https://fwupd.github.io/libfwupdplugin/uefi-capsule-README.html
- LVFS docs intro (fwupd architecture + policy posture): https://lvfs.readthedocs.io/en/latest/intro.html
- FreeBSD: efivar(8) (manage UEFI variables): https://man.freebsd.org/efivar
- Microsoft overview: Windows UEFI firmware update platform (capsule delivery model): https://learn.microsoft.com/en-us/windows-hardware/drivers/bringup/windows-uefi-firmware-update-platform
- Microsoft Secure Boot overview + 2026 certificate expiry note: https://learn.microsoft.com/en-us/windows-hardware/design/device-experiences/oem-secure-boot
- Microsoft Secure Boot status report (fleet readiness surface): https://learn.microsoft.com/en-us/windows/deployment/windows-autopatch/monitor/secure-boot-status-report
## Supervision trees + crash-only recovery discipline

- Erlang/OTP design principles: Supervisor Behaviour: https://www.erlang.org/doc/system/sup_princ.html
- Erlang/OTP stdlib: supervisor module docs: https://www.erlang.org/doc/apps/stdlib/supervisor.html
- Crash-Only Software (Candea/Fox): https://dslab.epfl.ch/pubs/crashonly.pdf
- ROC draft (Brown et al.): https://roc.cs.berkeley.edu/papers/hpts01-draft.pdf
- ROC overview (Microsoft Research): https://www.microsoft.com/en-us/research/publication/recovery-oriented-computing-motivation-definition-principles-and-examples/

## Networked object capabilities (CapTP / OCapN)

- CapTP overview (E rights): https://erights.org/elib/distrib/captp/index.html
- OCapN group site: https://ocapn.org/
- CapTP draft specification (OCapN repo): https://github.com/ocapn/ocapn/blob/main/draft-specifications/CapTP%20Specification.md
- OCapN test suite (interop focus): https://github.com/ocapn/ocapn-test-suite
- Sandstorm “containerize data, not services” (Cap’n Proto / ocap lineage): https://sandstorm.io/how-it-works

## API/contract evolution + compatibility gates (registries, diffs, policies)

- Fuchsia platform API evolution guidelines: https://fuchsia.dev/fuchsia-src/development/api/evolution
- Fuchsia API levels (platform surface snapshots): https://fuchsia.dev/fuchsia-src/concepts/versioning/api_levels
- Google AIP-180 (backwards compatibility guidance): https://google.aip.dev/180
- Protocol Buffers overview (safe evolution motivation + pointers): https://protobuf.dev/overview/
- gRPC core versioning guide: https://grpc.github.io/grpc/core/md_doc_versioning.html

- Kubernetes API deprecation policy (explicit lifecycle expectations): https://kubernetes.io/docs/reference/using-api/deprecation-policy/
- Stoplight: Deprecating API endpoints (practical guidance): https://blog.stoplight.io/deprecating-api-endpoints

## Policy-as-code / gate engines (implementation choices)

- Open Policy Agent (OPA) (policy-as-code engine): https://www.openpolicyagent.org/
- Kubernetes ValidatingAdmissionPolicy (admission-style policy patterns): https://kubernetes.io/docs/reference/access-authn-authz/validating-admission-policy/

## Permission review dashboards (revoke, expire, explain)

- Android runtime permission auto-reset (unused apps): https://developer.android.com/about/versions/11/privacy/permissions
- Apple App Privacy Report (network domains + sensor access visibility): https://support.apple.com/en-us/102188
- Firefox Permission Manager docs (central per-origin permission store): https://firefox-source-docs.mozilla.org/permissions/manager.html
- Qubes RPC policy basics (cross-domain calls are policy files): https://doc.qubes-os.org/en/latest/user/advanced-topics/rpc-policy.html

## CHERI capability hardware + memory safety lanes

- Cambridge CTSRD CHERI overview: https://www.cl.cam.ac.uk/research/security/ctsrd/cheri/
- FreeBSD Foundation: FreeBSD for Research: CHERI/Morello: https://freebsdfoundation.org/blog/freebsd-for-research-cheri-morello/
- FreeBSD status report: CheriBSD project update: https://www.freebsd.org/status/report-2022-10-2022-12/cheribsd/

## Remote attestation (Keylime-shaped)

- Red Hat Enterprise Linux 10: Ensuring system integrity with Keylime: https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/10/html/security_hardening/ensuring-system-integrity-with-keylime
- Microsoft Device Health Attestation: https://learn.microsoft.com/en-us/windows-server/security/device-health-attestation
- Microsoft Intune endpoint note on DHA -> Azure Attestation migration for Windows 11 compliance checks: https://learn.microsoft.com/en-us/intune/intune-service/fundamentals/intune-endpoints
- Azure Trusted Launch for Azure VMs: https://learn.microsoft.com/en-us/azure/virtual-machines/trusted-launch
- Keylime docs: Attestation security (design notes): https://keylime.readthedocs.io/en/latest/design/security.html
- SUSE docs: Remote attestation using Keylime (practical PCR/event-log angle): https://documentation.suse.com/sle-micro/5.5/html/SLE-Micro-all/cha-security-attestation.html

## Measured launch / DRTM (TrenchBoot-shaped)

- TrenchBoot dev docs: Late Launch overview (DRTM background): https://trenchboot.org/dev-docs/Late_Launch_Overview/
- TrenchBoot documentation quickstart (project posture): https://github.com/TrenchBoot/documentation/blob/master/QUICKSTART.md
- Qubes OS: TrenchBoot Anti Evil Maid (deployment motivation): https://www.qubes-os.org/news/2023/01/31/trenchboot-aem-for-qubes-os/

## Chaos engineering / failure injection discipline

- IBM: What is Chaos Engineering? (history + framing): https://www.ibm.com/think/topics/chaos-engineering
- Chaos Mesh overview (fault taxonomy inspiration): https://chaos-mesh.org/blog/chaos_mesh_your_chaos_engineering_solution/

## Adapter/migration patterns (interop without forever-legacy)

- Strangler Fig Application (Martin Fowler): https://martinfowler.com/bliki/StranglerFigApplication.html
- Original Strangler Fig Application (Fowler, 2004): https://martinfowler.com/bliki/OriginalStranglerFigApplication.html
- Strangler fig pattern (Azure Architecture Center): https://learn.microsoft.com/en-us/azure/architecture/patterns/strangler-fig
- Strangler fig pattern (Wikipedia overview): https://en.wikipedia.org/wiki/Strangler_fig_pattern
- Anti-Corruption Layer (microservices.io pattern index): https://microservices.io/patterns/refactoring/anti-corruption-layer.html
- “Legacy Displacement” patterns (Martin Fowler): https://martinfowler.com/articles/patterns-legacy-displacement/

## Documentation + navigation tooling (amnesia-resistant archives)

- OpenAPI specification (API description → generated docs; discovery surfaces): https://spec.openapis.org/oas/latest.html
- Kubernetes API conventions (mechanical consistency enabling tooling + discovery): https://github.com/kubernetes/community/blob/master/contributors/devel/sig-architecture/api-conventions.md
- Diátaxis (documentation architecture framework; keeps “how-to vs reference vs explanation” clean): https://diataxis.fr/
- Universal Ctags (code navigation indexes; tags as a lightweight catalog primitive): https://github.com/universal-ctags/ctags
- ripgrep (fast repo-wide search, respects ignore rules): https://github.com/BurntSushi/ripgrep

## Machine-readable error envelopes / stable reason codes (design cues)

- RFC 9457: Problem Details for HTTP APIs (structured, machine-readable error details; obsoletes RFC 7807): https://www.rfc-editor.org/rfc/rfc9457.html
- FreeBSD sysexits(3) (stable symbolic failure codes for programs; reason-code vocabulary inspiration): https://man.freebsd.org/cgi/man.cgi?query=sysexits&sektion=3
- gRPC status codes (small, stable machine-readable result vocabulary; design cue): https://grpc.io/docs/guides/status-codes/
- systemd.service exit-status names (symbolic exit-status vocabulary; design cue): https://www.freedesktop.org/software/systemd/man/systemd.service.html

- Chromium OS firmware boot and recovery design (recovery code path, explicit recovery mode, verified boot assumptions): https://www.chromium.org/chromium-os/chromiumos-design-docs/firmware-boot-and-recovery/
- Chromium OS developer mode design (physical presence, mode-transition wipe, recovery behavior): https://www.chromium.org/chromium-os/chromiumos-design-docs/developer-mode/

- RFC 9110 (`If-Match` and strong validators prevent the lost-update problem): https://www.rfc-editor.org/rfc/rfc9110
- RFC 7232 (strong validators change whenever the representation data changes; useful validator-pinning prior art): https://www.rfc-editor.org/rfc/rfc7232
- Kubernetes optimistic concurrency via `resourceVersion` (only one concurrent update succeeds): https://kubernetes.io/docs/concepts/cluster-administration/coordinated-leader-election/

## Breakglass / remote-presence adapters

- DMTF Redfish `VirtualMedia` schema index: https://redfish.dmtf.org/redfish/schema_index
- DMTF Redfish Resource and Schema Guide (`ComputerSystem.BootSourceOverrideTarget`, manager `SerialInterfaces`): https://redfish.dmtf.org/schemas/v1/DSP2046_2025.2.html
- DMTF Redfish Property Guide (`ConsoleEntryCommand`, `HotKeySequenceDisplay`, `VirtualMedia`, `VirtualMediaConfig`): https://redfish.dmtf.org/schemas/Redfish_Release_History.pdf
- DMTF Redfish Release History (`ConsoleEntryCommand`, `HotKeySequenceDisplay`, `SerialConsole`, `GraphicalConsole`, `VirtualMediaConfig`, `VirtualMedia`): https://redfish.dmtf.org/schemas/Redfish_Release_History.pdf
- Intel® Server System OpenBMC Redfish API specification (`WebSocketEndpoint` as virtual-media endpoint socket name/location): https://www.intel.com/content/dam/support/us/en/documents/server-products/intel-server-obmc-redfish-interface.pdf
- OpenBMC virtual-media design (proxy vs legacy modes; browser path vs BMC-managed remote image mounting): https://github.com/openbmc/docs/blob/master/designs/virtual-media.md
- Dell iDRAC virtual console / next boot menu (select next boot, then reboot/reset): https://www.dell.com/support/kbdoc/en-us/000176919/using-virtual-console-idrac7
- Dell iDRAC virtual media (with or without virtual console): https://www.dell.com/support/manuals/en-us/poweredge-r570/idrac10_1.20.xx_ug/accessing-virtual-media?guid=guid-4fecffb2-11ac-48e8-950c-6bd6def97338&lang=en-us
- Dell iDRAC virtual-console / virtual-media security guidance (separate encryption / redirection posture): https://www.dell.com/support/manuals/en-us/idrac9-lifecycle-controller-v5.x-series/idrac9_security_configuration_guide/virtual-console-and-virtual-media-security?guid=guid-fb3786a6-81eb-47b7-8a39-d69d5df1fcb1&lang=en-us
- DMTF Redfish Property Guide PDF (`GraphicalConsole`, `SerialConsole`, `CommandShell`, `VirtualMedia`, console-related properties): https://redfish.dmtf.org/schemas/v1/DSP2053_2025.2.pdf
- DMTF Redfish Serial Console Enhancements whitepaper (serial console capability/UX context): https://www.dmtf.org/sites/default/files/Redfish_Serial_Console_Enhancements_05-2020_WIP.pdf
- Dell iDRAC9 HTML5 virtual console usage guide (current console launch / behavior details): https://www.dell.com/support/manuals/en-us/idrac9-lifecycle-controller-v4.x-series/idrac9_4.00.00.00_ug_new/configuring-and-using-virtual-console?guid=guid-1607d2bc-0ed1-4487-84e1-272357a474ae&lang=en-us
- Dell iDRAC9 HTML5-based virtual console guide (session/viewer behavior details): https://www.dell.com/support/manuals/en-us/idrac9-lifecycle-controller-v5.x-series/idrac9_5.00.00.00_ug/html5-based-virtual-console?guid=guid-d7844cc4-f163-49e5-93f4-1e7f9e926857&lang=en-us
- HPE iLO one-time boot status (sets the next boot target for the next server reset): https://support.hpe.com/hpesc/public/docDisplay?docId=sd00005342en_us&docLocale=en_US&page=one-time-boot-options.html
- Intel Serial-over-LAN setup guide: https://www.intel.com/content/www/us/en/support/articles/000059471/server-products.html
- Supermicro BMC remote-presence feature overview: https://www.supermicro.com/en/solutions/management-software/bmc-resources

Last updated: 2026-05-18r493
