SHELL := /usr/bin/env bash
.DEFAULT_GOAL := help

CARGO_TARGET_DIR ?= /tmp/anonssh-build
ARTIFACTS_DIR ?= artifacts
PACKAGE_PATH_FILE := $(ARTIFACTS_DIR)/package-path.txt
PACKAGE_LINK := $(ARTIFACTS_DIR)/package
STATIC_PACKAGE_PATH_FILE := $(ARTIFACTS_DIR)/static-package-path.txt
STATIC_PACKAGE_LINK := $(ARTIFACTS_DIR)/static-package
STATIC_RELEASE_DIR := $(ARTIFACTS_DIR)/release
STATIC_RELEASE_BINARY := $(STATIC_RELEASE_DIR)/anonssh
PUBLICATION_DIR := $(ARTIFACTS_DIR)/publication
MONSTERNIX_PACKAGE_DIR := $(ARTIFACTS_DIR)/monsternix-package
MONSTERNIX_PACKAGE_LINK := $(MONSTERNIX_PACKAGE_DIR)/package
MONSTERNIX_PACKAGE_PATH_FILE := $(MONSTERNIX_PACKAGE_DIR)/package-path.txt
I2P_BOOTSTRAP_LEDGER := bootstrap/i2p-observations.json
I2P_BOOTSTRAP_SOURCES := /var/lib/anonssh-i2pd /var/lib/anonssh-i2pd-release
I2P_BOOTSTRAP_MINIMUM_OBSERVATION_DAYS ?= 3
I2P_BOOTSTRAP_MINIMUM_OBSERVATION_SPAN_DAYS ?= 7
BOND_SOAK_ROUNDS ?= 4
BOND_ENDURANCE_DURATION_SECONDS ?= 86400
BOND_ENDURANCE_SLOTS_PER_PROVIDER ?= 16
BOND_ENDURANCE_PAYLOAD_MIB ?= 32
BOND_ENDURANCE_QUIET_SECONDS ?= 120
BOND_ENDURANCE_MAX_DISK_GIB ?= 2
CARGO_ENV := env TZ=UTC LC_ALL=C CARGO_TARGET_DIR=$(CARGO_TARGET_DIR)
DEV_SHELL := nix-shell default.nix --arg devShell true --run

.PHONY: help doctor fmt fmt-fix lock lock-online check clippy test test-bond test-quick test-fuzz build check-i2p-bootstrap status-i2p-bootstrap status-i2p-sources observe-i2p-bootstrap curate-i2p-bootstrap promote-i2p-bootstrap package package-monsternix package-static package-static-reproducible package-publication sign-release test-package-consumer smoke test-service-lifecycle live-tor live-i2p live-i2p-fresh live-i2p-pool live-bond live-bond-scale live-bond-soak live-bond-endurance live-bond-forward live-bond-native live-bond-ssh live-bond-tools live-adaptive-bond-ssh live-bond-tor-ssh live-bond-i2p-ssh live-auto-fallback live-auto-topology live-concurrent-bond-ssh live-pool-recovery live-process-restart gate clean-package clean-live-state reset-bond-endurance clean

help:
	@printf '%s\n' \
	  'make doctor      Check the deterministic development environment' \
	  'make fmt-fix     Apply Rust formatting' \
	  'make lock        Refresh Cargo.lock without network access' \
	  'make lock-online Refresh Cargo.lock when intentionally adding dependencies' \
	  'make test-bond   Run the deterministic bonded-transport tests' \
	  'make test-quick  Format-check, lint, and run all workspace tests' \
	  'make test-fuzz   Run shipped deterministic parser mutation campaigns' \
	  'make build       Build the locked release binary' \
	  'make check-i2p-bootstrap  Validate the public I2P corpus and longevity evidence' \
	  'make status-i2p-bootstrap  Report longitudinal I2P evidence without mutation' \
	  'make status-i2p-sources  Inspect current mature-router evidence without mutation' \
	  'make observe-i2p-bootstrap  Record one daily observation from both mature routers' \
	  'make curate-i2p-bootstrap  Stage all currently qualified long-lived routers' \
	  'make promote-i2p-bootstrap  Promote the reviewed staged I2P corpus' \
	  'make package     Build the wrapped Nix package' \
	  'make package-monsternix  Prove the Nix-integrated package without embedded programs' \
	  'make package-static  Build and prove the portable static Linux binary' \
	  'make package-static-reproducible  Rebuild and compare the static artifact' \
	  'make package-publication  Build and verify the source-plus-binary publication ZIP' \
	  'make sign-release  Sign SHA256SUMS with an explicit publisher SSH key' \
	  'make test-package-consumer  Prove external pkgs.callPackage consumption' \
	  'make smoke       Exercise the wrapped binary without live routes' \
	  'make test-service-lifecycle  Prove packaged user-service lifecycle in isolation' \
	  'make live-tor    Run packaged Tor and SSH end to end' \
	  'make live-i2p    Run packaged I2P and SSH end to end' \
	  'make live-i2p-fresh  Run E2E with a fresh managed i2pd' \
	  'make live-i2p-pool  Run striping through two owned i2pd routers' \
	  'make live-bond   Run authenticated live Tor-plus-I2P striping' \
	  'make live-bond-scale  Measure live 1+1 through 8+8 uni/bidirectional scaling' \
	  'make live-bond-soak  Run the explicit 1+1 through 16+16 extended campaign' \
	  'make live-bond-endurance  Run bounded persistent-state adaptive endurance' \
	  'make live-bond-forward  Prove named local TCP forwarding over the mixed bond' \
	  'make live-bond-native  Prove ALP native bulk and real-time streams over one mixed bond' \
	  'make live-bond-ssh  Run the default bonded SSH product path' \
	  'make live-bond-tools  Prove stock rsync, Git, Borg, scp/SFTP, and SSHFS compatibility' \
	  'make live-adaptive-bond-ssh  Prove load-driven expansion and drain over SSH' \
	  'make live-bond-tor-ssh  Run four-router Tor-only bonded SSH' \
	  'make live-bond-i2p-ssh  Run four-router I2P-only bonded SSH' \
	  'make live-auto-fallback  Prove a default bond server accepts direct auto recovery' \
	  'make live-auto-topology  Prove auto selects mixed and homogeneous bonds' \
	  'make live-concurrent-bond-ssh  Prove concurrent clients share one resident pool' \
	  'make live-pool-recovery  Prove 8+8 striping and retained lane repair' \
	  'make live-process-restart  Crash and recover the bonded product processes' \
	  'make gate        Run all review gates' \
	  'make clean-package  Release the packaged-runtime GC root' \
	  'make clean-live-state  Remove dead owned live-test state from temp/runtime roots' \
	  'make reset-bond-endurance  Delete inactive endurance state and evidence' \
	  'make clean       Release package root and remove disposable Cargo output'

doctor:
	@command -v nix-shell >/dev/null
	@command -v nix-build >/dev/null
	@$(DEV_SHELL) 'rustc --version; cargo --version; rustfmt --version; cargo clippy --version; cargo metadata --locked --no-deps --format-version 1 >/dev/null'
	@printf '%s\n' 'doctor: ok'

fmt:
	@$(DEV_SHELL) '$(CARGO_ENV) cargo fmt --all -- --check'

fmt-fix:
	@$(DEV_SHELL) '$(CARGO_ENV) cargo fmt --all'

lock:
	@$(DEV_SHELL) '$(CARGO_ENV) cargo update --workspace --offline'

lock-online:
	@$(DEV_SHELL) '$(CARGO_ENV) cargo update --workspace'

check:
	@$(DEV_SHELL) '$(CARGO_ENV) cargo check --workspace --all-targets --locked'

clippy:
	@$(DEV_SHELL) '$(CARGO_ENV) cargo clippy --workspace --all-targets --locked -- -D warnings'

test:
	@$(DEV_SHELL) '$(CARGO_ENV) cargo test --workspace --all-targets --locked'

test-bond: fmt
	@$(DEV_SHELL) '$(CARGO_ENV) cargo test -p anonssh-bond -p anonssh-bond-tokio --all-targets --locked'

test-quick: fmt clippy test

test-fuzz: build
	@rm -rf "$(ARTIFACTS_DIR)/fuzz"
	@mkdir -p "$(ARTIFACTS_DIR)/fuzz"
	@set -eu; \
	  temporary="$(ARTIFACTS_DIR)/fuzz/report.json.tmp"; \
	  "$(CARGO_TARGET_DIR)/release/anonssh" test --fuzz --json > "$$temporary"; \
	  grep -Fq '"schema": "anonssh.embedded-parser-fuzz.v1"' "$$temporary"; \
	  grep -Fq '"status": "ok"' "$$temporary"; \
	  mv "$$temporary" "$(ARTIFACTS_DIR)/fuzz/report.json"
	@printf '%s\n' 'test-fuzz: ok (artifacts/fuzz/report.json)'

build:
	@$(DEV_SHELL) '$(CARGO_ENV) cargo build --release --workspace --locked'

check-i2p-bootstrap: build
	@mkdir -p "$(ARTIFACTS_DIR)"
	@"$(CARGO_TARGET_DIR)/release/anonssh" check-i2p-bootstrap \
	  --corpus "$(CURDIR)/bootstrap/i2p" \
	  > "$(ARTIFACTS_DIR)/i2p-bootstrap-validation.json"
	@printf '%s\n' 'check-i2p-bootstrap: ok'

status-i2p-bootstrap: build
	@mkdir -p "$(ARTIFACTS_DIR)"
	@"$(CARGO_TARGET_DIR)/release/anonssh" status-i2p-bootstrap \
	  --ledger "$(I2P_BOOTSTRAP_LEDGER)" \
	  --minimum-observation-days "$(I2P_BOOTSTRAP_MINIMUM_OBSERVATION_DAYS)" \
	  --minimum-observation-span-days "$(I2P_BOOTSTRAP_MINIMUM_OBSERVATION_SPAN_DAYS)" \
	  > "$(ARTIFACTS_DIR)/i2p-bootstrap-status.json"
	@printf '%s\n' 'status-i2p-bootstrap: ok (artifacts/i2p-bootstrap-status.json)'

status-i2p-sources: build
	@mkdir -p "$(ARTIFACTS_DIR)"
	@set -eu; \
	  temporary="$(ARTIFACTS_DIR)/i2p-bootstrap-source-status.json.tmp"; \
	  rm -f "$$temporary"; \
	  sudo -n "$(CARGO_TARGET_DIR)/release/anonssh" status-i2p-sources \
	    --source $(I2P_BOOTSTRAP_SOURCES) > "$$temporary"; \
	  mv "$$temporary" "$(ARTIFACTS_DIR)/i2p-bootstrap-source-status.json"
	@printf '%s\n' 'status-i2p-sources: ok (artifacts/i2p-bootstrap-source-status.json)'

observe-i2p-bootstrap: build
	@mkdir -p bootstrap "$(ARTIFACTS_DIR)"
	@sudo -n "$(CARGO_TARGET_DIR)/release/anonssh" observe-i2p-bootstrap \
	  --source $(I2P_BOOTSTRAP_SOURCES) \
	  --ledger "$(CURDIR)/$(I2P_BOOTSTRAP_LEDGER)" \
	  > "$(ARTIFACTS_DIR)/i2p-bootstrap-observation.json"
	@sudo -n chown "$$(id -u):$$(id -g)" "$(I2P_BOOTSTRAP_LEDGER)"
	@printf '%s\n' 'observe-i2p-bootstrap: ok'

curate-i2p-bootstrap: build
	@test ! -e bootstrap/i2p.next || { printf '%s\n' 'bootstrap/i2p.next already exists; inspect it before retrying' >&2; exit 1; }
	@mkdir -p bootstrap "$(ARTIFACTS_DIR)"
	@sudo -n "$(CARGO_TARGET_DIR)/release/anonssh" curate-i2p-bootstrap \
	  --source $(I2P_BOOTSTRAP_SOURCES) \
	  --ledger "$(CURDIR)/$(I2P_BOOTSTRAP_LEDGER)" \
	  --output "$(CURDIR)/bootstrap/i2p.next" \
	  --minimum-observation-days "$(I2P_BOOTSTRAP_MINIMUM_OBSERVATION_DAYS)" \
	  --minimum-observation-span-days "$(I2P_BOOTSTRAP_MINIMUM_OBSERVATION_SPAN_DAYS)" \
	  > "$(ARTIFACTS_DIR)/i2p-bootstrap-curation.json"
	@sudo -n chown -R "$$(id -u):$$(id -g)" bootstrap/i2p.next
	@"$(CARGO_TARGET_DIR)/release/anonssh" check-i2p-bootstrap \
	  --corpus "$(CURDIR)/bootstrap/i2p.next" \
	  > "$(ARTIFACTS_DIR)/i2p-bootstrap-staged-validation.json"
	@status=0; diff -ru bootstrap/i2p bootstrap/i2p.next \
	  > "$(ARTIFACTS_DIR)/i2p-bootstrap.diff" || status=$$?; test "$$status" -le 1
	@printf '%s\n' 'curate-i2p-bootstrap: staged bootstrap/i2p.next; review artifacts/i2p-bootstrap.diff'

promote-i2p-bootstrap: build
	@test -d bootstrap/i2p.next || { printf '%s\n' 'bootstrap/i2p.next is not staged' >&2; exit 1; }
	@mkdir -p "$(ARTIFACTS_DIR)"
	@"$(CARGO_TARGET_DIR)/release/anonssh" check-i2p-bootstrap \
	  --corpus "$(CURDIR)/bootstrap/i2p.next" \
	  > "$(ARTIFACTS_DIR)/i2p-bootstrap-staged-validation.json"
	@rm -rf bootstrap/i2p.previous
	@if [[ -e bootstrap/i2p ]]; then mv bootstrap/i2p bootstrap/i2p.previous; fi
	@mv bootstrap/i2p.next bootstrap/i2p || { mv bootstrap/i2p.previous bootstrap/i2p; exit 1; }
	@rm -rf bootstrap/i2p.previous
	@printf '%s\n' 'promote-i2p-bootstrap: ok'

package: check-i2p-bootstrap
	@mkdir -p "$(ARTIFACTS_DIR)"
	@set -eu; package="$$(nix-build default.nix --out-link "$(PACKAGE_LINK)")"; \
	  printf '%s\n' "$$package" > "$(PACKAGE_PATH_FILE)"; \
	  printf '%s\n' "$$package"

package-monsternix: check-i2p-bootstrap
	@rm -rf "$(MONSTERNIX_PACKAGE_DIR)"
	@mkdir -p "$(MONSTERNIX_PACKAGE_DIR)"
	@set -euo pipefail; \
	  test_parent="$${XDG_RUNTIME_DIR:-$$HOME}"; \
	  test_root="$$(mktemp -d "$$test_parent/.anonssh-monsternix-package.XXXXXXXX")"; \
	  trap 'rm -rf "$$test_root"' EXIT; \
	  install -d -m 0700 "$$test_root/cache" "$$test_root/runtime"; \
	  nixpkgs="$$(nix-instantiate --find-file nixpkgs)"; \
	  package="$$(nix-build --out-link "$(MONSTERNIX_PACKAGE_LINK)" --expr \
	    "let pkgs = import $$nixpkgs {}; in import $(CURDIR)/nix/monsternix.nix { inherit pkgs; }")"; \
	  binary="$$package/bin/anonssh"; \
	  wrapped="$$package/bin/.anonssh-wrapped"; \
	  test -x "$$binary" -a -x "$$wrapped"; \
	  printf '%s\n' "$$package" > "$(MONSTERNIX_PACKAGE_PATH_FILE)"; \
	  export XDG_CACHE_HOME="$$test_root/cache"; \
	  export XDG_RUNTIME_DIR="$$test_root/runtime"; \
	  "$$binary" --version > "$(MONSTERNIX_PACKAGE_DIR)/version.txt"; \
	  "$$binary" test --json > "$(MONSTERNIX_PACKAGE_DIR)/self-test.json"; \
	  "$$binary" doctor --json > "$(MONSTERNIX_PACKAGE_DIR)/doctor.json"; \
	  grep -Fq '"status": "ok"' "$(MONSTERNIX_PACKAGE_DIR)/self-test.json"; \
	  for field in tor_version i2pd_version openssh_version dropbear_version sftp_server_version scp_version; do \
	    grep -Fq "\"$$field\": null" "$(MONSTERNIX_PACKAGE_DIR)/doctor.json"; \
	  done; \
	  test "$$(grep -c '"path": "/nix/store/' "$(MONSTERNIX_PACKAGE_DIR)/doctor.json")" -eq 8; \
	  test ! -e "$$test_root/cache/anonssh/runtime"; \
	  digest="$$(sha256sum "$$wrapped" | cut -d' ' -f1)"; \
	  bytes="$$(stat -c '%s' "$$wrapped")"; \
	  version="$$(cat "$(MONSTERNIX_PACKAGE_DIR)/version.txt")"; \
	  printf '{"schema":"anonssh.monsternix-package.v1","status":"ok","package":"%s","nixpkgs":"%s","version":"%s","rust_binary":{"sha256":"%s","bytes":%s},"executable_payloads_embedded":false,"runtime_dependencies":"nix-store","embedded_runtime_cache_created":false}\n' \
	    "$$package" "$$nixpkgs" "$$version" "$$digest" "$$bytes" \
	    > "$(MONSTERNIX_PACKAGE_DIR)/report.json"; \
	  rm -rf "$$test_root"; \
	  trap - EXIT
	@printf '%s\n' 'package-monsternix: ok (artifacts/monsternix-package/report.json)'

package-static: check-i2p-bootstrap
	@rm -rf "$(STATIC_RELEASE_DIR)"
	@mkdir -p "$(STATIC_RELEASE_DIR)"
	@set -euo pipefail; \
	  package="$$(nix-build default.nix --arg static true --out-link "$(STATIC_PACKAGE_LINK)")"; \
	  binary="$$package/bin/anonssh"; \
	  printf '%s\n' "$$package" > "$(STATIC_PACKAGE_PATH_FILE)"; \
	  if readelf -l "$$binary" | grep -q INTERP; then \
	    printf '%s\n' 'static binary has an ELF interpreter' >&2; exit 1; \
	  fi; \
	  if readelf -d "$$binary" | grep -q NEEDED; then \
	    printf '%s\n' 'static binary needs a shared library' >&2; exit 1; \
	  fi; \
	  install -m 0755 "$$binary" "$(STATIC_RELEASE_BINARY)"; \
	  "$(STATIC_RELEASE_BINARY)" --version > "$(STATIC_RELEASE_DIR)/version.txt"; \
	  "$(STATIC_RELEASE_BINARY)" --help > "$(STATIC_RELEASE_DIR)/help.txt"; \
	  grep -Fq 'anonssh [SAFE-SSH-OPTIONS] <USER@MACHINE-ID>' "$(STATIC_RELEASE_DIR)/help.txt"; \
	  runtime_cache="$(CURDIR)/$(STATIC_RELEASE_DIR)/runtime-cache"; \
	  mkdir -p "$$runtime_cache/tmp"; \
	  USER="$$(id -un)" XDG_CACHE_HOME="$$runtime_cache" TMPDIR="$$runtime_cache/tmp" \
	  PATH=/nonexistent \
	    "$(STATIC_RELEASE_BINARY)" test --json \
	      > "$(STATIC_RELEASE_DIR)/embedded-test.json"; \
	  grep -Fq '"ssh_runtime": "embedded-openssh-to-embedded-dropbear"' \
	    "$(STATIC_RELEASE_DIR)/embedded-test.json"; \
	  PATH=/nonexistent \
	    "$(STATIC_RELEASE_BINARY)" test --fuzz --json \
	      > "$(STATIC_RELEASE_DIR)/embedded-fuzz.json"; \
	  grep -Fq '"schema": "anonssh.embedded-parser-fuzz.v1"' \
	    "$(STATIC_RELEASE_DIR)/embedded-fuzz.json"; \
	  grep -Fq '"status": "ok"' "$(STATIC_RELEASE_DIR)/embedded-fuzz.json"; \
	  XDG_CACHE_HOME="$$runtime_cache" \
	  PATH=/nonexistent \
	    "$(STATIC_RELEASE_BINARY)" doctor --json \
	      > "$(STATIC_RELEASE_DIR)/doctor.json"; \
	  grep -Fq '"tor_version": "0.4.9.14"' "$(STATIC_RELEASE_DIR)/doctor.json"; \
	  grep -Fq '"i2pd_version": "2.61.0"' "$(STATIC_RELEASE_DIR)/doctor.json"; \
	  grep -Fq '"openssh_version": "10.5p1"' "$(STATIC_RELEASE_DIR)/doctor.json"; \
	  grep -Fq '"dropbear_version": "2026.94"' "$(STATIC_RELEASE_DIR)/doctor.json"; \
	  grep -Fq '"sftp_server_version": "10.5p1"' "$(STATIC_RELEASE_DIR)/doctor.json"; \
	  grep -Fq '"scp_version": "10.5p1"' "$(STATIC_RELEASE_DIR)/doctor.json"; \
	  grep -Fq "$$runtime_cache/anonssh/runtime/tor-0.4.9.14-" "$(STATIC_RELEASE_DIR)/doctor.json"; \
	  grep -Fq "$$runtime_cache/anonssh/runtime/i2pd-2.61.0-" "$(STATIC_RELEASE_DIR)/doctor.json"; \
	  grep -Fq "$$runtime_cache/anonssh/runtime/ssh-10.5p1-" "$(STATIC_RELEASE_DIR)/doctor.json"; \
	  grep -Fq "$$runtime_cache/anonssh/runtime/dropbear-2026.94-" "$(STATIC_RELEASE_DIR)/doctor.json"; \
	  grep -Fq "$$runtime_cache/anonssh/runtime/sftp-server-10.5p1-" "$(STATIC_RELEASE_DIR)/doctor.json"; \
	  grep -Fq "$$runtime_cache/anonssh/runtime/scp-10.5p1-" "$(STATIC_RELEASE_DIR)/doctor.json"; \
	  tor="$$(find "$$runtime_cache" -type f -path '*/bin/tor' -print -quit)"; \
	  i2pd="$$(find "$$runtime_cache" -type f -path '*/bin/i2pd' -print -quit)"; \
	  ssh="$$(find "$$runtime_cache" -type f -path '*/bin/ssh' -print -quit)"; \
	  dropbear="$$(find "$$runtime_cache" -type f -path '*/bin/dropbear' -print -quit)"; \
	  sftp_server="$$(find "$$runtime_cache" -type f -path '*/bin/sftp-server' -print -quit)"; \
	  scp="$$(find "$$runtime_cache" -type f -path '*/bin/scp' -print -quit)"; \
	  test -n "$$tor" -a -n "$$i2pd" -a -n "$$ssh" -a -n "$$dropbear" \
	    -a -n "$$sftp_server" -a -n "$$scp"; \
	  for program in "$$tor" "$$i2pd" "$$ssh" "$$dropbear" "$$sftp_server" "$$scp"; do \
	    test "$$(stat -c '%a' "$$program")" = 500; \
	    if readelf -l "$$program" | grep -q INTERP || readelf -d "$$program" | grep -q NEEDED; then \
	      printf 'embedded program is not static: %s\n' "$$program" >&2; exit 1; \
	    fi; \
	  done; \
	  digest="$$(sha256sum "$(STATIC_RELEASE_BINARY)" | cut -d' ' -f1)"; \
	  bytes="$$(stat -c '%s' "$(STATIC_RELEASE_BINARY)")"; \
	  sources="$$(nix-build default.nix --arg releaseSources true --no-out-link)"; \
	  cp "$$sources/anonssh-sources.tar.gz" "$$sources/sources.json" "$(STATIC_RELEASE_DIR)/"; \
	  source_archive="$(STATIC_RELEASE_DIR)/anonssh-sources.tar.gz"; \
	  source_inventory="$(STATIC_RELEASE_DIR)/sources.json"; \
	  grep -Fq "\"schema\":\"anonssh.corresponding-sources.v2\"" "$$source_inventory"; \
	  grep -Fq "\"materialized\":true" "$$source_inventory"; \
	  grep -Fq '"symlinks":0' "$$source_inventory"; \
	  source_listing="$(STATIC_RELEASE_DIR)/sources.list.tmp"; \
	  source_details="$(STATIC_RELEASE_DIR)/sources.details.tmp"; \
	  tar -tzf "$$source_archive" > "$$source_listing"; \
	  tar -tvzf "$$source_archive" > "$$source_details"; \
	  test "$$(awk 'substr($$1, 1, 1) == "l" { count++ } END { print count + 0 }' "$$source_details")" -eq 0; \
	  for component in \
	    libevent-2.1.13 openssl-3.5.8 zlib-1.3.2 xz-5.8.4 zstd-1.5.7 scrypt-1.3.3 \
	    i2p-java-2.13.0; do \
	      grep -Fq "anonssh-sources/$$component/" "$$source_listing"; \
	  done; \
	  rm "$$source_listing" "$$source_details"; \
	  source_digest="$$(sha256sum "$$source_archive" | cut -d' ' -f1)"; \
	  grep -Fq "\"sha256\":\"$$source_digest\"" "$$source_inventory"; \
	  cp LICENSE THIRD_PARTY.md "$(STATIC_RELEASE_DIR)/"; \
	  printf '{"schema":"anonssh.static-release.v4","status":"ok","target":"x86_64-linux-musl","native_execution":true,"sha256":"%s","bytes":%s,"embedded_bootstrap":true,"embedded_programs":{"tor":"0.4.9.14","i2pd":"2.61.0","openssh":"10.5p1","dropbear":"2026.94","sftp-server":"10.5p1","scp":"10.5p1"},"linked_libraries":{"tor":{"libevent":"2.1.13","openssl":"3.5.8","zlib":"1.3.2","xz":"5.8.4","zstd":"1.5.7","scrypt":"1.3.3"}},"data_sources":{"i2p_reseed_certificates":{"project":"java-i2p","version":"2.13.0"}},"corresponding_sources":{"schema":"anonssh.corresponding-sources.v2","materialized":true,"symlinks":0},"dynamic_libraries":0,"signed":false}\n' \
	    "$$digest" "$$bytes" > "$(STATIC_RELEASE_DIR)/report.json"; \
	  printf '{"spdxVersion":"SPDX-2.3","dataLicense":"CC0-1.0","SPDXID":"SPDXRef-DOCUMENT","name":"anonssh-x86_64-linux-musl","documentNamespace":"https://anonssh.invalid/spdx/%s","creationInfo":{"created":"1970-01-01T00:00:00Z","creators":["Tool: AnonSSH-Makefile"]},"packages":[{"name":"AnonSSH","SPDXID":"SPDXRef-AnonSSH","versionInfo":"0.2.0","downloadLocation":"NOASSERTION","licenseConcluded":"MIT","checksums":[{"algorithm":"SHA256","checksumValue":"%s"}]},{"name":"Tor","SPDXID":"SPDXRef-Tor","versionInfo":"0.4.9.14","downloadLocation":"https://dist.torproject.org/tor-0.4.9.14.tar.gz","licenseConcluded":"BSD-3-Clause AND GPL-3.0-only"},{"name":"i2pd","SPDXID":"SPDXRef-i2pd","versionInfo":"2.61.0","downloadLocation":"https://github.com/PurpleI2P/i2pd/releases/tag/2.61.0","licenseConcluded":"BSD-3-Clause"},{"name":"OpenSSH","SPDXID":"SPDXRef-OpenSSH","versionInfo":"10.5p1","downloadLocation":"https://www.openssh.com/","licenseConcluded":"SSH-OpenSSH"},{"name":"Dropbear","SPDXID":"SPDXRef-Dropbear","versionInfo":"2026.94","downloadLocation":"https://matt.ucc.asn.au/dropbear/dropbear.html","licenseConcluded":"MIT"},{"name":"libevent","SPDXID":"SPDXRef-libevent","versionInfo":"2.1.13","downloadLocation":"NOASSERTION","licenseConcluded":"BSD-3-Clause"},{"name":"OpenSSL","SPDXID":"SPDXRef-OpenSSL","versionInfo":"3.5.8","downloadLocation":"NOASSERTION","licenseConcluded":"Apache-2.0"},{"name":"zlib","SPDXID":"SPDXRef-zlib","versionInfo":"1.3.2","downloadLocation":"NOASSERTION","licenseConcluded":"Zlib"},{"name":"XZ-Utils","SPDXID":"SPDXRef-xz","versionInfo":"5.8.4","downloadLocation":"NOASSERTION","licenseConcluded":"NOASSERTION","licenseDeclared":"GPL-2.0-or-later AND LGPL-2.1-or-later"},{"name":"zstd","SPDXID":"SPDXRef-zstd","versionInfo":"1.5.7","downloadLocation":"NOASSERTION","licenseConcluded":"BSD-3-Clause"},{"name":"scrypt","SPDXID":"SPDXRef-scrypt","versionInfo":"1.3.3","downloadLocation":"NOASSERTION","licenseConcluded":"BSD-2-Clause"},{"name":"Java I2P reseed certificate source","SPDXID":"SPDXRef-JavaI2P","versionInfo":"2.13.0","downloadLocation":"https://geti2p.net/","licenseConcluded":"NOASSERTION"}]}\n' \
	    "$$digest" "$$digest" > "$(STATIC_RELEASE_DIR)/sbom.spdx.json"; \
	  printf '{"schema":"anonssh.release-manifest.v2","status":"ok","target":"x86_64-linux-musl","binary":{"path":"anonssh","sha256":"%s","bytes":%s},"corresponding_sources":{"path":"anonssh-sources.tar.gz","sha256":"%s","inventory":"sources.json","materialized":true,"symlinks":0},"programs":{"tor":"0.4.9.14","i2pd":"2.61.0","openssh":"10.5p1","dropbear":"2026.94","sftp-server":"10.5p1","scp":"10.5p1"},"linked_libraries":{"tor":{"libevent":"2.1.13","openssl":"3.5.8","zlib":"1.3.2","xz":"5.8.4","zstd":"1.5.7","scrypt":"1.3.3"}},"data_sources":{"i2p_reseed_certificates":{"project":"java-i2p","version":"2.13.0"}},"integrity":"SHA256SUMS","signature":"optional-explicit-publisher-key"}\n' \
	    "$$digest" "$$bytes" "$$source_digest" > "$(STATIC_RELEASE_DIR)/manifest.json"; \
	  (cd "$(STATIC_RELEASE_DIR)" && sha256sum \
	    LICENSE THIRD_PARTY.md anonssh anonssh-sources.tar.gz doctor.json \
	    embedded-fuzz.json embedded-test.json help.txt manifest.json report.json sbom.spdx.json \
	    sources.json version.txt > SHA256SUMS); \
	  rm -rf "$$runtime_cache"
	@printf '%s\n' 'package-static: ok ($(STATIC_RELEASE_BINARY))'

package-static-reproducible: package-static
	@set -eu; \
	  before="$$(sha256sum "$(STATIC_RELEASE_BINARY)" | cut -d' ' -f1)"; \
	  nix-build default.nix --arg static true --check --no-out-link >/dev/null; \
	  after="$$(sha256sum "$(STATIC_RELEASE_BINARY)" | cut -d' ' -f1)"; \
	  test "$$before" = "$$after"; \
	  printf '{"schema":"anonssh.reproducibility.v1","status":"ok","target":"x86_64-linux-musl","first_sha256":"%s","second_sha256":"%s"}\n' \
	    "$$before" "$$after" > "$(STATIC_RELEASE_DIR)/reproducibility.json"
	@printf '%s\n' 'package-static-reproducible: ok'

package-publication: package-static
	@$(DEV_SHELL) 'set -euo pipefail; \
	  export TZ=UTC LC_ALL=C; \
	  test -z "$$(git status --porcelain --untracked-files=normal)" || { \
	    printf "%s\n" "publication requires a clean committed tree" >&2; exit 1; \
	  }; \
	  for evidence in \
	    "$(ARTIFACTS_DIR)/live/bond-tools.json" \
	    "$(ARTIFACTS_DIR)/fuzz/report.json" \
	    "$(ARTIFACTS_DIR)/package-consumer/report.json" \
	    "$(ARTIFACTS_DIR)/service-lifecycle/report.json"; do \
	      test -f "$$evidence" || { printf "missing evidence: %s\n" "$$evidence" >&2; exit 1; }; \
	      grep -Eq "\"status\"[[:space:]]*:[[:space:]]*\"ok\"" "$$evidence" || { \
	        printf "evidence is not successful: %s\n" "$$evidence" >&2; exit 1; \
	      }; \
	  done; \
	  version="$$(cut -d" " -f2 "$(STATIC_RELEASE_DIR)/version.txt")"; \
	  test -n "$$version"; \
	  revision="$$(git rev-parse HEAD)"; \
	  short="$$(git rev-parse --short=12 HEAD)"; \
	  epoch="$$(git show -s --format=%ct HEAD)"; \
	  base="AnonSSH-$$version-$$short"; \
	  work="$(PUBLICATION_DIR)/work"; \
	  verify="$(PUBLICATION_DIR)/verify"; \
	  root="$$work/$$base"; \
	  archive="$(CURDIR)/$(PUBLICATION_DIR)/$$base-publication.zip"; \
	  rm -rf "$(PUBLICATION_DIR)"; \
	  mkdir -p "$$root/source" "$$root/release/x86_64-linux" "$$root/evidence"; \
	  git archive --format=tar HEAD | tar -xf - -C "$$root/source"; \
	  cp -a "$(STATIC_RELEASE_DIR)/." "$$root/release/x86_64-linux/"; \
	  cp "$(ARTIFACTS_DIR)/live/bond-tools.json" "$$root/evidence/live-bond-tools.json"; \
	  cp "$(ARTIFACTS_DIR)/fuzz/report.json" "$$root/evidence/fuzz.json"; \
	  cp "$(ARTIFACTS_DIR)/package-consumer/report.json" "$$root/evidence/package-consumer.json"; \
	  cp "$(ARTIFACTS_DIR)/service-lifecycle/report.json" "$$root/evidence/service-lifecycle.json"; \
	  cp PUBLISHING.md "$$root/START-HERE.md"; \
	  printf "%s\n" "$$revision" > "$$root/REVISION"; \
	  printf '"'"'{"schema":"anonssh.publication-handoff.v1","status":"ok","project":"AnonSSH","version":"%s","revision":"%s","history_included":false,"source":"source","release":"release/x86_64-linux","evidence":"evidence","binary_target":"x86_64-linux-musl","binary_signed":false}\n'"'"' \
	    "$$version" "$$revision" > "$$root/HANDOFF.json"; \
	  (cd "$$root" && find . -type f ! -name HANDOFF-SHA256SUMS -print0 | \
	    LC_ALL=C sort -z | xargs -0 sha256sum > HANDOFF-SHA256SUMS); \
	  find "$$root" -exec touch -h -d "@$$epoch" {} +; \
	  (cd "$$work" && find "$$base" -print | LC_ALL=C sort | \
	    zip -X -q "$$archive" -@); \
	  unzip -tqq "$$archive"; \
	  mkdir -p "$$verify"; \
	  unzip -q "$$archive" -d "$$verify"; \
	  test -f "$$verify/$$base/source/Cargo.toml"; \
	  test -f "$$verify/$$base/source/default.nix"; \
	  test -f "$$verify/$$base/source/PUBLISHING.md"; \
	  (cd "$$verify/$$base" && sha256sum -c HANDOFF-SHA256SUMS >/dev/null); \
	  (cd "$$verify/$$base/release/x86_64-linux" && sha256sum -c SHA256SUMS >/dev/null); \
	  source_archive="$$verify/$$base/release/x86_64-linux/anonssh-sources.tar.gz"; \
	  source_inventory="$$verify/$$base/release/x86_64-linux/sources.json"; \
	  grep -Fq "\"schema\":\"anonssh.corresponding-sources.v2\"" "$$source_inventory"; \
	  grep -Fq "\"materialized\":true" "$$source_inventory"; \
	  source_details="$$verify/sources.details"; \
	  tar -tvzf "$$source_archive" > "$$source_details"; \
	  if grep -q "^l" "$$source_details"; then \
	    printf "%s\n" "corresponding source archive contains a symlink" >&2; exit 1; \
	  fi; \
	  rm "$$source_details"; \
	  runtime="$$verify/runtime"; \
	  mkdir -p "$$runtime/cache" "$$runtime/tmp"; \
	  USER="$$(id -un)" XDG_CACHE_HOME="$$runtime/cache" TMPDIR="$$runtime/tmp" PATH=/nonexistent \
	    "$$verify/$$base/release/x86_64-linux/anonssh" test --json \
	      > "$$verify/extracted-binary-test.json"; \
	  grep -Fq '"'"'"status": "ok"'"'"' "$$verify/extracted-binary-test.json"; \
	  rm -rf "$$work" "$$verify"; \
	  (cd "$(PUBLICATION_DIR)" && sha256sum "$${base}-publication.zip" \
	    > "$${base}-publication.zip.sha256"); \
	  printf "package-publication: ok (%s)\n" "$$archive"'

sign-release:
	@test -n "$(RELEASE_SIGNING_KEY)" || { printf '%s\n' 'set RELEASE_SIGNING_KEY to a publisher-controlled SSH private key' >&2; exit 1; }
	@test -f "$(STATIC_RELEASE_DIR)/SHA256SUMS" || { printf '%s\n' 'run make package-static first' >&2; exit 1; }
	@set -eu; \
	  public="$$(ssh-keygen -y -f "$(RELEASE_SIGNING_KEY)")"; \
	  printf 'anonssh %s\n' "$$public" > "$(STATIC_RELEASE_DIR)/allowed_signer"; \
	  ssh-keygen -Y sign -f "$(RELEASE_SIGNING_KEY)" -n anonssh-release \
	    "$(STATIC_RELEASE_DIR)/SHA256SUMS" >/dev/null; \
	  mv "$(STATIC_RELEASE_DIR)/SHA256SUMS.sig" "$(STATIC_RELEASE_DIR)/SHA256SUMS.sshsig"; \
	  ssh-keygen -Y verify -f "$(STATIC_RELEASE_DIR)/allowed_signer" -I anonssh \
	    -n anonssh-release -s "$(STATIC_RELEASE_DIR)/SHA256SUMS.sshsig" \
	    < "$(STATIC_RELEASE_DIR)/SHA256SUMS" >/dev/null; \
	  fingerprint="$$(printf '%s\n' "$$public" | ssh-keygen -lf - | awk '{print $$2}')"; \
	  rm "$(STATIC_RELEASE_DIR)/allowed_signer"; \
	  printf '{"schema":"anonssh.release-signature.v1","status":"verified","namespace":"anonssh-release","identity":"anonssh","fingerprint":"%s"}\n' \
	    "$$fingerprint" > "$(STATIC_RELEASE_DIR)/signature.json"
	@printf '%s\n' 'sign-release: ok'

test-package-consumer: check-i2p-bootstrap
	@mkdir -p "$(ARTIFACTS_DIR)/package-consumer"
	@set -eu; \
	  nixpkgs="$$(nix-instantiate --find-file nixpkgs)"; \
	  package="$$(nix-build --no-out-link --expr \
	    "let pkgs = import $$nixpkgs {}; in pkgs.callPackage $(CURDIR)/default.nix {}")"; \
	  version="$$($$package/bin/anonssh --version)"; \
	  "$$package/bin/anonssh" doctor --json \
	    > "$(ARTIFACTS_DIR)/package-consumer/doctor.json"; \
	  printf '{"schema":"anonssh.package-consumer.v1","status":"ok","package":"%s","nixpkgs":"%s","version":"%s"}\n' \
	    "$$package" "$$nixpkgs" "$$version" \
	    > "$(ARTIFACTS_DIR)/package-consumer/report.json"
	@printf '%s\n' 'test-package-consumer: ok'

smoke: package
	@mkdir -p "$(ARTIFACTS_DIR)/smoke"
	@rm -f "$(ARTIFACTS_DIR)/smoke/embedded-test.txt"
	@set -eu; package="$$(cat "$(PACKAGE_PATH_FILE)")"; \
	  "$$package/bin/anonssh" --version > "$(ARTIFACTS_DIR)/smoke/version.txt"; \
	  "$$package/bin/anonssh" test --json > "$(ARTIFACTS_DIR)/smoke/embedded-test.json"; \
	  "$$package/bin/anonssh" doctor --json > "$(ARTIFACTS_DIR)/smoke/doctor.json"
	@printf '%s\n' 'smoke: ok'

test-service-lifecycle: package
	@rm -rf "$(ARTIFACTS_DIR)/service-lifecycle"
	@mkdir -p \
	  "$(ARTIFACTS_DIR)/service-lifecycle/root/cache" \
	  "$(ARTIFACTS_DIR)/service-lifecycle/root/config" \
	  "$(ARTIFACTS_DIR)/service-lifecycle/root/data" \
	  "$(ARTIFACTS_DIR)/service-lifecycle/root/runtime" \
	  "$(ARTIFACTS_DIR)/service-lifecycle/root/state"
	@set -eu; \
	  artifact="$(CURDIR)/$(ARTIFACTS_DIR)/service-lifecycle"; \
	  root="$$artifact/root"; \
	  package="$$(cat "$(PACKAGE_PATH_FILE)")"; \
	  controller="$$(type -P true)"; \
	  export XDG_CACHE_HOME="$$root/cache"; \
	  export XDG_CONFIG_HOME="$$root/config"; \
	  export XDG_DATA_HOME="$$root/data"; \
	  export XDG_RUNTIME_DIR="$$root/runtime"; \
	  export XDG_STATE_HOME="$$root/state"; \
	  export ANONSSH_CLIENT_TOR_POOL_SOCKS_ADDRS="127.0.0.1:30050,127.0.0.1:30051,127.0.0.1:30052,127.0.0.1:30053,127.0.0.1:30054,127.0.0.1:30055,127.0.0.1:30056,127.0.0.1:30057"; \
	  export ANONSSH_CLIENT_TOR_POOL_CONTROL_ADDRS="127.0.0.1:30150,127.0.0.1:30151,127.0.0.1:30152,127.0.0.1:30153,127.0.0.1:30154,127.0.0.1:30155,127.0.0.1:30156,127.0.0.1:30157"; \
	  export ANONSSH_CLIENT_TOR_RESERVE_SOCKS_ADDRS="127.0.0.1:30250,127.0.0.1:30251,127.0.0.1:30252,127.0.0.1:30253,127.0.0.1:30254,127.0.0.1:30255,127.0.0.1:30256,127.0.0.1:30257"; \
	  export ANONSSH_CLIENT_TOR_RESERVE_CONTROL_ADDRS="127.0.0.1:30350,127.0.0.1:30351,127.0.0.1:30352,127.0.0.1:30353,127.0.0.1:30354,127.0.0.1:30355,127.0.0.1:30356,127.0.0.1:30357"; \
	  export ANONSSH_CLIENT_I2P_POOL_ADDRS="127.0.0.1:30656,127.0.0.1:30657,127.0.0.1:30658,127.0.0.1:30659,127.0.0.1:30660,127.0.0.1:30661,127.0.0.1:30662,127.0.0.1:30663"; \
	  export ANONSSH_SYSTEMCTL_BIN="$$controller"; \
	  export ANONSSH_SERVICE_EXECUTABLE="$$package/bin/anonssh"; \
	  "$$package/bin/anonssh" broker start > "$$artifact/broker-start.txt"; \
	  "$$package/bin/anonssh" broker status --json > "$$artifact/broker-running.json"; \
	  grep -q '"resident": true' "$$artifact/broker-running.json"; \
	  "$$package/bin/anonssh" broker start > "$$artifact/broker-start-again.txt"; \
	  grep -q 'already running' "$$artifact/broker-start-again.txt"; \
	  "$$package/bin/anonssh" broker stop > "$$artifact/broker-stop.txt"; \
	  sleep 1; \
	  "$$package/bin/anonssh" broker status --json > "$$artifact/broker-stopped.json"; \
	  grep -q '"running": false' "$$artifact/broker-stopped.json"; \
	  "$$package/bin/anonssh" service install --machine-id lifecycle-test \
	    > "$$artifact/install.json"; \
	  test "$$(stat -c '%a' "$$root/config/anonssh/service/install.json")" = 600; \
	  test "$$(stat -c '%a' "$$root/config/anonssh/service/config.json")" = 600; \
	  test "$$(stat -c '%a' "$$root/config/systemd/user/anonssh-server.service")" = 644; \
	  cp "$$root/config/systemd/user/anonssh-broker.service" "$$artifact/broker.service"; \
	  cp "$$root/config/systemd/user/anonssh-server.service" "$$artifact/server.service"; \
	  "$$package/bin/anonssh" service status --json > "$$artifact/locked.json"; \
	  grep -q '"credential_state": "locked"' "$$artifact/locked.json"; \
	  ANONSSH_PASSPHRASE='anonssh isolated lifecycle proof' \
	    "$$package/bin/anonssh" service unlock > "$$artifact/unlock.json"; \
	  "$$package/bin/anonssh" service start > "$$artifact/start.json"; \
	  "$$package/bin/anonssh" service stop > "$$artifact/stop.json"; \
	  test ! -e "$$root/runtime/anonssh/service/identity-password"; \
	  "$$package/bin/anonssh" service stop > "$$artifact/stop-again.json"; \
	  if analyzer="$$(type -P systemd-analyze)"; then \
	    "$$analyzer" verify "$$artifact/broker.service" "$$artifact/server.service" \
	      > "$$artifact/systemd-verify.txt" 2>&1; \
	    test ! -s "$$artifact/systemd-verify.txt"; \
	  else \
	    printf '%s\n' 'systemd-analyze unavailable; syntax verification skipped' \
	      > "$$artifact/systemd-verify.txt"; \
	  fi; \
	  "$$package/bin/anonssh" service uninstall > "$$artifact/uninstall.json"; \
	  "$$package/bin/anonssh" service uninstall > "$$artifact/uninstall-again.json"; \
	  "$$package/bin/anonssh" service status --json > "$$artifact/uninstalled.json"; \
	  grep -q '"installed": false' "$$artifact/uninstalled.json"; \
	  printf '%s\n' '{"schema":"anonssh.service-lifecycle.v1","status":"ok","host_manager_modified":false}' \
	    > "$$artifact/report.json"
	@printf '%s\n' 'test-service-lifecycle: ok'

live-tor: package
	@mkdir -p "$(ARTIFACTS_DIR)/live"
	@package="$$(cat "$(PACKAGE_PATH_FILE)")"; \
	  "$$package/bin/anonssh" test --live tor > "$(ARTIFACTS_DIR)/live/tor.txt" 2>&1
	@cat "$(ARTIFACTS_DIR)/live/tor.txt"

live-i2p: package
	@mkdir -p "$(ARTIFACTS_DIR)/live"
	@package="$$(cat "$(PACKAGE_PATH_FILE)")"; \
	  "$$package/bin/anonssh" test --live i2p > "$(ARTIFACTS_DIR)/live/i2p.txt" 2>&1
	@cat "$(ARTIFACTS_DIR)/live/i2p.txt"

live-i2p-fresh: package
	@mkdir -p "$(ARTIFACTS_DIR)/live"
	@package="$$(cat "$(PACKAGE_PATH_FILE)")"; \
	  "$$package/bin/anonssh" test --live i2p-fresh > "$(ARTIFACTS_DIR)/live/i2p-fresh.json" 2> "$(ARTIFACTS_DIR)/live/i2p-fresh.stderr"
	@cat "$(ARTIFACTS_DIR)/live/i2p-fresh.json"

live-bond: package
	@mkdir -p "$(ARTIFACTS_DIR)/live"
	@package="$$(cat "$(PACKAGE_PATH_FILE)")"; \
	  "$$package/bin/anonssh" test --live bond > "$(ARTIFACTS_DIR)/live/bond.json" 2> "$(ARTIFACTS_DIR)/live/bond.stderr"
	@cat "$(ARTIFACTS_DIR)/live/bond.json"

live-bond-scale: package
	@mkdir -p "$(ARTIFACTS_DIR)/live"
	@rm -f "$(ARTIFACTS_DIR)/live/bond-scale.checkpoint.json"
	@package="$$(cat "$(PACKAGE_PATH_FILE)")"; \
	  ANONSSH_INTERNAL_SCALE_CHECKPOINT="$(CURDIR)/$(ARTIFACTS_DIR)/live/bond-scale.checkpoint.json" \
	  "$$package/bin/anonssh" test --live bond-scale > "$(ARTIFACTS_DIR)/live/bond-scale.json" 2> "$(ARTIFACTS_DIR)/live/bond-scale.stderr"
	@cat "$(ARTIFACTS_DIR)/live/bond-scale.json"

live-bond-soak: package
	@mkdir -p "$(ARTIFACTS_DIR)/live"
	@rm -f "$(ARTIFACTS_DIR)/live/bond-soak.checkpoint.json"
	@package="$$(cat "$(PACKAGE_PATH_FILE)")"; \
	  ANONSSH_INTERNAL_SCALE_MAX_SLOTS_PER_PROVIDER=16 \
	  ANONSSH_INTERNAL_SCALE_ROUNDS_PER_TRIAL="$(BOND_SOAK_ROUNDS)" \
	  ANONSSH_INTERNAL_SCALE_CHECKPOINT="$(CURDIR)/$(ARTIFACTS_DIR)/live/bond-soak.checkpoint.json" \
	  "$$package/bin/anonssh" test --live bond-scale > "$(ARTIFACTS_DIR)/live/bond-soak.json" 2> "$(ARTIFACTS_DIR)/live/bond-soak.stderr"
	@cat "$(ARTIFACTS_DIR)/live/bond-soak.json"

live-bond-endurance: package
	@mkdir -p "$(ARTIFACTS_DIR)/live"
	@set -euo pipefail; \
	  package="$$(cat "$(PACKAGE_PATH_FILE)")"; \
	  final="$(ARTIFACTS_DIR)/live/bond-endurance.json"; \
	  temporary="$$final.tmp"; \
	  stderr="$(ARTIFACTS_DIR)/live/bond-endurance.stderr"; \
	  stderr_raw="$$stderr.raw.tmp"; \
	  stderr_temporary="$$stderr.tmp"; \
	  rm -f "$$temporary" "$$final" "$$stderr_raw" "$$stderr_temporary"; \
	  trap 'rm -f "$$temporary" "$$stderr_raw" "$$stderr_temporary"' EXIT; \
	  set +e; \
	  ANONSSH_INTERNAL_ENDURANCE_ROOT="$(CURDIR)/$(ARTIFACTS_DIR)/live/bond-endurance-state" \
	  ANONSSH_INTERNAL_ENDURANCE_CHECKPOINT="$(CURDIR)/$(ARTIFACTS_DIR)/live/bond-endurance.checkpoint.json" \
	  ANONSSH_INTERNAL_ENDURANCE_DURATION_SECONDS="$(BOND_ENDURANCE_DURATION_SECONDS)" \
	  ANONSSH_INTERNAL_ENDURANCE_SLOTS_PER_PROVIDER="$(BOND_ENDURANCE_SLOTS_PER_PROVIDER)" \
	  ANONSSH_INTERNAL_ENDURANCE_PAYLOAD_MIB="$(BOND_ENDURANCE_PAYLOAD_MIB)" \
	  ANONSSH_INTERNAL_ENDURANCE_QUIET_SECONDS="$(BOND_ENDURANCE_QUIET_SECONDS)" \
	  ANONSSH_INTERNAL_ENDURANCE_MAX_DISK_GIB="$(BOND_ENDURANCE_MAX_DISK_GIB)" \
	  "$$package/bin/anonssh" test --live bond-endurance > "$$temporary" 2> "$$stderr_raw"; \
	  status=$$?; \
	  set -e; \
	  tail -c 1048576 "$$stderr_raw" > "$$stderr_temporary"; \
	  mv "$$stderr_temporary" "$$stderr"; \
	  rm -f "$$stderr_raw"; \
	  if (( status != 0 )); then \
	    printf 'live-bond-endurance: failed status=%d checkpoint=%s stderr=%s\n' \
	      "$$status" "$(ARTIFACTS_DIR)/live/bond-endurance.checkpoint.json" "$$stderr" >&2; \
	    exit "$$status"; \
	  fi; \
	  mv "$$temporary" "$$final"; \
	  trap - EXIT; \
	  printf 'live-bond-endurance: ok artifact=%s checkpoint=%s stderr=%s\n' \
	    "$$final" "$(ARTIFACTS_DIR)/live/bond-endurance.checkpoint.json" "$$stderr"

live-i2p-pool: package
	@mkdir -p "$(ARTIFACTS_DIR)/live"
	@package="$$(cat "$(PACKAGE_PATH_FILE)")"; \
	  "$$package/bin/anonssh" test --live i2p-pool > "$(ARTIFACTS_DIR)/live/i2p-pool.json" 2> "$(ARTIFACTS_DIR)/live/i2p-pool.stderr"
	@cat "$(ARTIFACTS_DIR)/live/i2p-pool.json"

live-bond-ssh: package
	@mkdir -p "$(ARTIFACTS_DIR)/live"
	@package="$$(cat "$(PACKAGE_PATH_FILE)")"; \
	  "$$package/bin/anonssh" test --live bond-ssh > "$(ARTIFACTS_DIR)/live/bond-ssh.json" 2> "$(ARTIFACTS_DIR)/live/bond-ssh.stderr"
	@cat "$(ARTIFACTS_DIR)/live/bond-ssh.json"

live-bond-tools: package
	@mkdir -p "$(ARTIFACTS_DIR)/live"
	@$(DEV_SHELL) 'package="$$(cat "$(PACKAGE_PATH_FILE)")"; \
	  "$$package/bin/anonssh" test --live bond-tools \
	  > "$(ARTIFACTS_DIR)/live/bond-tools.json" \
	  2> "$(ARTIFACTS_DIR)/live/bond-tools.stderr"'
	@cat "$(ARTIFACTS_DIR)/live/bond-tools.json"

live-bond-forward: package
	@mkdir -p "$(ARTIFACTS_DIR)/live"
	@package="$$(cat "$(PACKAGE_PATH_FILE)")"; \
	  "$$package/bin/anonssh" test --live bond-forward > "$(ARTIFACTS_DIR)/live/bond-forward.json" 2> "$(ARTIFACTS_DIR)/live/bond-forward.stderr"
	@cat "$(ARTIFACTS_DIR)/live/bond-forward.json"

live-bond-native: package
	@mkdir -p "$(ARTIFACTS_DIR)/live"
	@package="$$(cat "$(PACKAGE_PATH_FILE)")"; \
	  temporary="$(ARTIFACTS_DIR)/live/bond-native.json.tmp"; \
	  rm -f "$$temporary"; \
	  trap 'rm -f "$$temporary"' EXIT; \
	  "$$package/bin/anonssh" test --live bond-native > "$$temporary" 2> "$(ARTIFACTS_DIR)/live/bond-native.stderr"; \
	  mv "$$temporary" "$(ARTIFACTS_DIR)/live/bond-native.json"; \
	  trap - EXIT
	@cat "$(ARTIFACTS_DIR)/live/bond-native.json"

live-adaptive-bond-ssh: package
	@mkdir -p "$(ARTIFACTS_DIR)/live"
	@package="$$(cat "$(PACKAGE_PATH_FILE)")"; \
	  ANONSSH_INTERNAL_TEST_ADAPTIVE_LOAD=1 \
	  "$$package/bin/anonssh" test --live bond-ssh \
	  > "$(ARTIFACTS_DIR)/live/adaptive-bond-ssh.json" \
	  2> "$(ARTIFACTS_DIR)/live/adaptive-bond-ssh.stderr"
	@cat "$(ARTIFACTS_DIR)/live/adaptive-bond-ssh.json"

live-bond-tor-ssh: package
	@mkdir -p "$(ARTIFACTS_DIR)/live"
	@package="$$(cat "$(PACKAGE_PATH_FILE)")"; \
	  "$$package/bin/anonssh" test --live bond-tor-ssh > "$(ARTIFACTS_DIR)/live/bond-tor-ssh.json" 2> "$(ARTIFACTS_DIR)/live/bond-tor-ssh.stderr"
	@cat "$(ARTIFACTS_DIR)/live/bond-tor-ssh.json"

live-bond-i2p-ssh: package
	@mkdir -p "$(ARTIFACTS_DIR)/live"
	@package="$$(cat "$(PACKAGE_PATH_FILE)")"; \
	  "$$package/bin/anonssh" test --live bond-i2p-ssh > "$(ARTIFACTS_DIR)/live/bond-i2p-ssh.json" 2> "$(ARTIFACTS_DIR)/live/bond-i2p-ssh.stderr"
	@cat "$(ARTIFACTS_DIR)/live/bond-i2p-ssh.json"

live-auto-fallback: package
	@mkdir -p "$(ARTIFACTS_DIR)/live"
	@package="$$(cat "$(PACKAGE_PATH_FILE)")"; \
	  "$$package/bin/anonssh" test --live auto-fallback > "$(ARTIFACTS_DIR)/live/auto-fallback.json" 2> "$(ARTIFACTS_DIR)/live/auto-fallback.stderr"
	@cat "$(ARTIFACTS_DIR)/live/auto-fallback.json"

live-auto-topology: package
	@mkdir -p "$(ARTIFACTS_DIR)/live"
	@package="$$(cat "$(PACKAGE_PATH_FILE)")"; \
	  "$$package/bin/anonssh" test --live auto-topology > "$(ARTIFACTS_DIR)/live/auto-topology.json" 2> "$(ARTIFACTS_DIR)/live/auto-topology.stderr"
	@cat "$(ARTIFACTS_DIR)/live/auto-topology.json"

live-concurrent-bond-ssh: package
	@mkdir -p "$(ARTIFACTS_DIR)/live"
	@package="$$(cat "$(PACKAGE_PATH_FILE)")"; \
	  "$$package/bin/anonssh" test --live concurrent-bond-ssh > "$(ARTIFACTS_DIR)/live/concurrent-bond-ssh.json" 2> "$(ARTIFACTS_DIR)/live/concurrent-bond-ssh.stderr"
	@cat "$(ARTIFACTS_DIR)/live/concurrent-bond-ssh.json"

live-pool-recovery: package
	@mkdir -p "$(ARTIFACTS_DIR)/live"
	@package="$$(cat "$(PACKAGE_PATH_FILE)")"; \
	  "$$package/bin/anonssh" test --live pool-recovery > "$(ARTIFACTS_DIR)/live/pool-recovery.json" 2> "$(ARTIFACTS_DIR)/live/pool-recovery.stderr"
	@cat "$(ARTIFACTS_DIR)/live/pool-recovery.json"

live-process-restart: package
	@mkdir -p "$(ARTIFACTS_DIR)/live"
	@package="$$(cat "$(PACKAGE_PATH_FILE)")"; \
	  "$$package/bin/anonssh" test --live process-restart > "$(ARTIFACTS_DIR)/live/process-restart.json" 2> "$(ARTIFACTS_DIR)/live/process-restart.stderr"
	@cat "$(ARTIFACTS_DIR)/live/process-restart.json"

gate: test-quick test-fuzz package-static test-package-consumer package-monsternix smoke test-service-lifecycle

clean-package:
	@rm -f "$(PACKAGE_LINK)" "$(PACKAGE_PATH_FILE)" \
	  "$(STATIC_PACKAGE_LINK)" "$(STATIC_PACKAGE_PATH_FILE)" \
	  "$(MONSTERNIX_PACKAGE_LINK)" "$(MONSTERNIX_PACKAGE_PATH_FILE)"
	@if [[ -d "$(STATIC_RELEASE_DIR)" ]]; then find "$(STATIC_RELEASE_DIR)" -depth -delete; fi
	@if [[ -d "$(ARTIFACTS_DIR)/release-aarch64" ]]; then find "$(ARTIFACTS_DIR)/release-aarch64" -depth -delete; fi

clean-live-state:
	@set -euo pipefail; \
	  uid="$$(id -u)"; \
	  roots=("$${TMPDIR:-/tmp}"); \
	  runtime_root="$${XDG_RUNTIME_DIR:-/run/user/$$uid}"; \
	  if [[ -d "$$runtime_root" && "$$runtime_root" != "$${roots[0]}" ]]; then \
	    roots+=("$$runtime_root"); \
	  fi; \
	  removed=0; \
	  skipped=0; \
	  for root in "$${roots[@]}"; do \
	    while IFS= read -r -d '' path; do \
	      owner="$$(stat -c '%u' -- "$$path")"; \
	      pid="$${path##*-}"; \
	      if [[ "$$owner" != "$$uid" || ! "$$pid" =~ ^[0-9]+$$ ]] || kill -0 "$$pid" 2>/dev/null; then \
	        skipped=$$((skipped + 1)); \
	        continue; \
	      fi; \
	      find "$$path" -depth -delete; \
	      removed=$$((removed + 1)); \
	    done < <(find "$$root" -mindepth 1 -maxdepth 1 -type d -name 'anonssh-live-*' -print0); \
	  done; \
	  printf 'clean-live-state: removed=%d skipped=%d\n' "$$removed" "$$skipped"

reset-bond-endurance:
	@set -euo pipefail; \
	  root="$(ARTIFACTS_DIR)/live/bond-endurance-state"; \
	  if [[ -d "$$root/campaign.lease" ]]; then \
	    printf '%s\n' 'reset-bond-endurance: campaign lease is active; refusing cleanup' >&2; \
	    exit 1; \
	  fi; \
	  if [[ -d "$$root" ]]; then find "$$root" -depth -delete; fi; \
	  rm -f \
	    "$(ARTIFACTS_DIR)/live/bond-endurance.json" \
	    "$(ARTIFACTS_DIR)/live/bond-endurance.json.tmp" \
	    "$(ARTIFACTS_DIR)/live/bond-endurance.checkpoint.json" \
	    "$(ARTIFACTS_DIR)/live/bond-endurance.stderr" \
	    "$(ARTIFACTS_DIR)/live/bond-endurance.stderr.raw.tmp" \
	    "$(ARTIFACTS_DIR)/live/bond-endurance.stderr.tmp"; \
	  printf '%s\n' 'reset-bond-endurance: ok'

clean: clean-package
	@if [[ -d "$(CARGO_TARGET_DIR)" ]]; then find "$(CARGO_TARGET_DIR)" -depth -delete; fi
