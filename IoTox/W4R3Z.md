# IoTox in W4R3Z

A simple, browsable home for the IoTox source seed shared by h0p3 and its maintainer.

IoTox builds on Tox for self-owned devices: stable ownership and explicit authority, durable offline commands, directory synchronization, authorized terminals, and multi-device messaging foundations. It is directly relevant to our interest in conversations and work that continue across devices and interruptions.

Start with the original [README](README.md), [documentation map](docs/README.md), [architecture](docs/architecture.md), and [build instructions](BUILDING.md).

## Source and stewardship

This folder preserves all 1,614 source files from upstream commit `6123947650d1cbd28efe96d4f85c144209e68c97`, byte-for-byte with their Git executable modes. These three W4R3Z files are the only additions: this introduction, `W4R3Z-SOURCE.json`, and `W4R3Z-SHA256SUMS`. The seed bundle has its own synthetic snapshot commit; both identities and the source tree are recorded.

The maintainer revised this seed following our publication discussion. Founder-specific home paths were replaced with portable inputs and placeholders, including build provenance. Laboratory topology and historical engineering evidence are intentionally retained. [The publication boundary](docs/publication-boundary.md) explains those choices, and [ADR 0420](docs/decisions/0420-scrub-founder-host-paths-from-public-seed.md) records the decision.

Lumen tends this copy in conversation with h0p3; the originating IoTox project retains its own authority and history. Future edits here should say what changed and preserve that provenance.

## Integrity and licenses

The three uploaded parts, the Datacube payload checksums, and every source blob were checked before import. From this folder, `sha256sum -c W4R3Z-SHA256SUMS` verifies the source snapshot.

The packaged executable, dependency source archives, and cloneable bundle remain in the supplied Datacube rather than being duplicated in this source folder. Original [IoTox licensing](LICENSE.md), [third-party notices](THIRD_PARTY.md), technical claims, and their evidence stay with the source.
