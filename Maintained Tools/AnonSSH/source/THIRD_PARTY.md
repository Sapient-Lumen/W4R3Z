# Bundled Programs

The portable Linux `anonssh` executable carries six executable payloads from four
independent upstream projects. At runtime AnonSSH extracts and executes them as child
processes. They are not linked into AnonSSH's Rust program. Tor is itself statically
linked with six separately selected libraries, and AnonSSH also carries reseed
certificates sourced from Java I2P.

`default.nix` is authoritative for pinned build inputs. The generated release manifest,
SBOM, license inventory, and corresponding-source inventory record the exact outputs of
one release; this document explains their distribution obligations.

## Tor 0.4.9.14

- Project: The Tor Project, <https://www.torproject.org/>
- Exact source: <https://dist.torproject.org/tor-0.4.9.14.tar.gz>
- Source SHA-256 (SRI): `sha256-GCRJrByP9DJ42ie2mwIEDhHQPQMn222RJuQZDsYjXko=`
- License: BSD-3-Clause, with GPL-3.0-only code enabled for onion-service proof of work

Anyone distributing the binary must distribute the applicable license notices and make
the complete corresponding Tor source for this exact build available from the same
release location, as required by GPLv3. The upstream tarball is the build input, but an
upstream URL alone is not a substitute for a distributor's corresponding-source duty.

### Tor static link inputs

The selected Tor executable is statically linked with these exact package inputs:

| Component | Version | Declared license |
| --- | --- | --- |
| libevent | 2.1.13 | BSD-3-Clause |
| OpenSSL | 3.5.8 | Apache-2.0 |
| zlib | 1.3.2 | Zlib |
| XZ Utils | 5.8.4 | GPL-2.0-or-later and LGPL-2.1-or-later |
| zstd | 1.5.7 | BSD-3-Clause |
| scrypt | 1.3.3 | BSD-2-Clause |

These libraries are not separately extracted runtime payloads. Their exact source
inputs are nevertheless materialized in the corresponding-source archive, identified
in `sources.json`, and represented in the SPDX SBOM.

## i2pd 2.61.0

- Project: PurpleI2P i2pd, <https://github.com/PurpleI2P/i2pd>
- Exact source: <https://github.com/PurpleI2P/i2pd/releases/tag/2.61.0>
- License: BSD-3-Clause

Release publishers must preserve the upstream notices with distributed artifacts.

## Java I2P 2.13.0 certificate source

- Project: Java I2P, <https://geti2p.net/>
- Exact source: the `i2p` source input recorded by the pinned Nix package set
- License: upstream multi-license collection; see the included source tree

The reseed certificates embedded with i2pd come from the Java I2P package's
`certificates/` output, not from i2pd. No Java I2P router executable is embedded. The
release source archive carries the exact Java I2P source input as
`i2p-java-2.13.0/`, and the SPDX inventory records this data provenance separately.

## OpenSSH 10.5p1

- Project: OpenSSH, <https://www.openssh.com/>
- Exact source: the `openssh` source input recorded by the pinned Nix package set
- License: BSD-style OpenSSH license collection

The static `ssh` client, `sftp-server` subsystem, and legacy `scp` helper are embedded.
The release source archive carries the exact pinned upstream input and AnonSSH build
expression.

## Dropbear 2026.94

- Project: Dropbear SSH, <https://matt.ucc.asn.au/dropbear/dropbear.html>
- Exact source: the `dropbear` source input recorded by the pinned Nix package set
- License: MIT-style Dropbear license collection

Only the static `dropbear` server is embedded. AnonSSH's pinned patch lets Dropbear
select the validated content-addressed SFTP and scp helpers without consulting host
paths. The release source archive carries the exact pinned upstream input and AnonSSH
build expression.

## Operator Overrides

`ANONSSH_TOR_BIN`, `ANONSSH_I2PD_BIN`, `ANONSSH_I2PD_CERTS_DIR`, `ANONSSH_SSH_BIN`,
`ANONSSH_DROPBEAR_BIN`, `ANONSSH_SFTP_SERVER_BIN`, and `ANONSSH_SCP_BIN` select
operator-provided alternatives. This precedence is intentional and tested; it permits
an operator-selected system package or local build without changing the AnonSSH
executable.
Configuration v2 `external_tor_services` entries instead attach exact authenticated
SOCKS/control pairs owned by already-running local Tor daemons; healthy occupied i2pd
SAM endpoints are similarly borrowed. AnonSSH does not stop borrowed services.
