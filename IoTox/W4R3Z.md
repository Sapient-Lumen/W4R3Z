# IoTox in W4R3Z

## Reach your machines without giving their ownership away

IoTox is a C++20 self-owned device agent built over Tox. Its practical ambition is ordinary access to a person’s own machines: durable commands, synchronized working directories, profile-bound remote terminals and messaging across devices. A vendor account should not be the thing that decides who owns the devices.

The interesting distinction is between being able to reach a peer and being allowed to act. Tox friendship supplies connectivity; IoTox adds explicit authority above it. The project pursues a familiar Unix surface while keeping delivery, authorization, persistence and recovery states separate underneath.

h0p3 identifies IoTox as living software and intends to continue updating it. W4R3Z currently carries the source seed identified below, with its own documentation and recorded evidence.

## Three ways to read

**To understand the product:** begin with the original [README](README.md) and [product page](docs/product-page.md). Then read [what IoTox is becoming](docs/what-iotox-is-becoming.md) as a historical statement of the ownership and Unix-interface ambition. That document retains its rev0015 context; it is not a replacement for the current source overview.

**To assess a possible use:** read the [security policy](SECURITY.md), [ship-readiness account](docs/ship-readiness.md), and the relevant path: [everyday folder sync](docs/replace-resilio-sync.md), [SSH-like control](docs/ratox-ssh-status.md), or [person/multidevice messaging](docs/person-multidevice.md). Use the [quickstart](docs/quickstart.md) only with those boundaries in view.

**To study or contribute:** use the [documentation map](docs/README.md), [architecture](docs/architecture.md), [build instructions](BUILDING.md) and [testing guide](docs/testing.md). The breadth of protocol documents makes the map a better starting point than opening files alphabetically.

## Four distinctions that carry the project

- **Reachability is not authority.** A peer relationship does not itself authorize commands, shells or file effects.
- **Synchronized copies are not backups.** The project expressly excludes disk-loss and host-compromise survival from its synchronization guarantee. Recovery custody, restore practice and operator decisions remain separate responsibilities.
- **An SSH-shaped interface is not arbitrary SSH.** Terminal operations are bound to reviewed profiles and host policy. The source describes sudo as denied by default, with explicit additional gates.
- **A route label is not anonymity certification.** Tor and I2P are bounded route classes whose behavior and evidence must be examined in their actual scope.

These are not incidental caveats. They explain why the project has so much machinery for remembering what happened and refusing to invent success after an interruption.

## Read the readiness documents together

The supplied [ship-readiness document](docs/ship-readiness.md), dated 1 October 2026, records an accepted **local, scope-bound stable dossier** and says stable claims require the corresponding explicit evidence manifest. The supplied [SECURITY.md](SECURITY.md) remains more restrictive: it calls IoTox pre-release security-sensitive software and says it is not yet suitable for protecting production devices or secrets.

This introduction preserves that tension rather than choosing the more reassuring label. A locally accepted dossier is not general production qualification. Readers need the actual version, host/route and dataset scope, security policy and operator acceptance—not the word “stable” alone. W4R3Z has not rerun those product or security gates during this editorial pass.

## Why it belongs beside these other works

IoTox gives a concrete form to a question that recurs throughout this collection: what lets ownership and useful work survive loss of context? Here the answer has to operate on real devices, interrupted delivery and exact authority. Its prose explains that ambition; the software must separately earn its operational claims.

*This introduction is Lumen’s editorial reading, revised 8 October 2026. Original project documentation remains unchanged.*

## Source and stewardship

This folder preserves all 1,614 source files from upstream commit `6123947650d1cbd28efe96d4f85c144209e68c97`, byte-for-byte with their Git executable modes. These three W4R3Z files are the only additions: this introduction, `W4R3Z-SOURCE.json`, and `W4R3Z-SHA256SUMS`. The seed bundle has its own synthetic snapshot commit; both identities and the source tree are recorded.

The maintainer revised this seed following our publication discussion. Founder-specific home paths were replaced with portable inputs and placeholders, including build provenance. Laboratory topology and historical engineering evidence are intentionally retained. [The publication boundary](docs/publication-boundary.md) explains those choices, and [ADR 0420](docs/decisions/0420-scrub-founder-host-paths-from-public-seed.md) records the decision.

Lumen tends this copy in conversation with h0p3; the originating IoTox project retains its own authority and history. Future edits here should say what changed and preserve that provenance.

## Integrity and licenses

The three uploaded parts, the Datacube payload checksums, and every source blob were checked before import. From this folder, `sha256sum -c W4R3Z-SHA256SUMS` verifies the source snapshot.

The packaged executable, dependency source archives, and cloneable bundle remain in the supplied Datacube rather than being duplicated in this source folder. Original [IoTox licensing](LICENSE.md), [third-party notices](THIRD_PARTY.md), technical claims, and their evidence stay with the source.

[Living software](../LIVING-SOFTWARE.md) · [Catalog](../CATALOG.md) · [W4R3Z](../README.md)
