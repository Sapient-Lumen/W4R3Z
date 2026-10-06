#!/usr/bin/env python3
"""Guardrail for critical product-profile defaults.

Purpose:
  - keep the A–D compilation-target surface small and stable
  - prevent profile-B drift back into ambiguous host-app / ambient-authority posture

This is intentionally conservative and fast.
It does not try to validate every possible default knob; JSON Schema already covers shape.
Instead it enforces a few critical, design-level invariants that we have explicitly decided.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "spec" / "examples" / "product.profiles.json"

EXPECTED_RUNTIME = {
    "fleet_host": "microvm-first",
    "workstation": "appvm-first-with-host-ui-control-plane",
    "general_os": "jails-first-with-microvm-lanes",
    "appliance_factory": "sealed-workload-images",
}

EXPECTED_BACKUPS = {
    "fleet_host": "state-replication-with-restore-drills",
    "workstation": "exports-or-home-replication",
    "general_os": "user-choice",
    "appliance_factory": "replication-and-restore-drills",
}

EXPECTED_REMOVABLE_MEDIA = {
    "fleet_host": "deny-or-quarantine-only",
    "workstation": "quarantine-first-no-automount",
    "general_os": "quarantine-first-local-fallback",
    "appliance_factory": "offline-ingest-quarantine-first",
}

EXPECTED_USB_ISOLATION = {
    "fleet_host": "prefer-device-domain-no-host-automount",
    "workstation": "device-domain-required-when-supported",
    "general_os": "prefer-device-domain-fallback-to-local-policy",
    "appliance_factory": "device-domain-or-ingest-station",
}

EXPECTED_NETWORK_EGRESS = {
    "fleet_host": "brokered-policy-derived-noninteractive",
    "workstation": "brokered-consent-with-durable-policy-landing",
    "general_os": "brokered-by-default-explicit-adapter-fallback",
    "appliance_factory": "deny-by-default-offline-or-approved-brokered",
}

EXPECTED_DNS_RESOLUTION = {
    "fleet_host": "brokered-required-when-hostnames-appear",
    "workstation": "brokered-required",
    "general_os": "brokered-preferred-explicit-fallback",
    "appliance_factory": "brokered-or-none-fixed-policy",
}

EXPECTED_NETWORK_INGRESS = {
    "fleet_host": "brokered-service-classes-noninteractive",
    "workstation": "loopback-by-default-brokered-exceptions-with-lease",
    "general_os": "brokered-service-classes-explicit-adapter-fallback",
    "appliance_factory": "deny-by-default-offline-or-approved-brokered-service",
}

EXPECTED_NETWORKING = {
    "fleet_host": "activation-first-commit-confirmed-maintenance-leased",
    "workstation": "trusted-ui-local-first-commit-confirmed",
    "general_os": "derived-preferred-explicit-admin-fallback",
    "appliance_factory": "sealed-offline-windowed-commit-confirmed",
}

EXPECTED_REMOTE_ASSISTANCE = {
    "fleet_host": "brokered-tty-console-recorded-no-gui-control",
    "workstation": "visible-user-mediated-view-or-control-with-lease",
    "general_os": "brokered-explicit-lease-no-ambient-agent",
    "appliance_factory": "disabled-by-default-maintenance-only-recorded",
}


EXPECTED_PRIVATE_KEYS = {
    "fleet_host": "brokered-nonexportable-headless-policy-gated",
    "workstation": "brokered-nonexportable-user-presence-vault-preferred",
    "general_os": "brokered-preferred-explicit-file-key-adapter",
    "appliance_factory": "offline-or-hsm-quorum-nonexportable",
}

EXPECTED_HOME_IDENTITY = {
    "fleet_host": "host-operator-accounts-no-portable-home-default",
    "workstation": "portable-home-preferred-login-mounted-no-whole-home-appvm-default",
    "general_os": "host-accounts-default-portable-home-optional",
    "appliance_factory": "no-human-homes-in-production-maintenance-identities-separate",
}

EXPECTED_DATA_AT_REST = {
    "fleet_host": "encrypted-state-attested-or-brokered-unlock",
    "workstation": "lost-device-default-login-bound-user-state",
    "general_os": "encrypted-preferred-explicit-compatibility-fallback",
    "appliance_factory": "encrypted-production-state-attested-or-quorum-maintenance-unlock",
}

EXPECTED_EVIDENCE_EXPORTS = {
    "fleet_host": "brokered-ticketed-encrypted-external-two-person",
    "workstation": "user-mediated-redacted-recipient-visible-encrypted-external",
    "general_os": "brokered-preferred-ticketed-explicit-adapter-fallback",
    "appliance_factory": "minimal-redacted-encrypted-two-person-transparency-required",
}

EXPECTED_EVIDENCE = {
    "fleet_host": "always-on",
    "workstation": "exportable",
    "general_os": "local-retained-explicit-export",
    "appliance_factory": "bundled-and-redacted",
}

EXPECTED_FIRMWARE_UPDATES = {
    "fleet_host": "policy-gated",
    "workstation": "interactive-consent",
    "general_os": "user-choice",
    "appliance_factory": "offline-staged",
}

EXPECTED_UPDATES = {
    "fleet_host": "health-gated",
    "workstation": "health-gated",
    "general_os": "transactional",
    "appliance_factory": "offline-bundles",
}

EXPECTED_INSTALLATION_RECOVERY = {
    "fleet_host": "target-bound-additive-breakglass",
    "workstation": "guided-consent-encrypted-default",
    "general_os": "guided-choice-explicit-destructive",
    "appliance_factory": "target-bound-offline-resettable",
}

EXPECTED_DESTRUCTIVE_REPROVISION = {
    "fleet_host": "target-bound-digest-breakglass-or-maintenance",
    "workstation": "trusted-ui-target-confirm-digest-bound",
    "general_os": "explicit-admin-or-trusted-ui-digest-bound",
    "appliance_factory": "offline-signed-authority-plus-reset-marker",
}

EXPECTED_STORE_RETENTION = {
    "fleet_host": "rollback-floor-policy-gated",
    "workstation": "trusted-ui-visible-space-pressure-rollback-floor",
    "general_os": "pins-and-generations-explicit-admin",
    "appliance_factory": "offline-auditable-rollback-floor",
}

EXPECTED_FUZZING = {
    "fleet_host": "required-classes-uapi-parser-driver-zero-open-reproducible-cases-flake-triage",
    "workstation": "required-classes-importer-broker-parser-zero-open-reproducible-cases-flake-triage",
    "general_os": "required-shipped-host-and-importer-classes-advisory-elsewhere",
    "appliance_factory": "approved-target-set-zero-open-production-cases-retained-corpora",
}

EXPECTED_KERNEL_MUTATION = {
    "fleet_host": "activation-first-maintenance-leased",
    "workstation": "activation-first-trusted-ui-maintenance",
    "general_os": "derived-default-explicit-admin-fallback",
    "appliance_factory": "preload-only-lockdown-offline-maintenance",
}

EXPECTED_DEVICE_AUTHORITY = {
    "fleet_host": "compiled-minimal-maintenance-leased",
    "workstation": "portal-first-host-owned-trusted-ui-exceptions",
    "general_os": "compiled-minimal-preferred-explicit-compatibility-fallback",
    "appliance_factory": "compiled-minimal-sealed-offline-maintenance",
}

EXPECTED_HIGH_RISK_APPROVALS = {
    "fleet_host": "digest-bound-role-separated-quorum",
    "workstation": "trusted-ui-user-consent-first",
    "general_os": "single-principal-default-explicit-quorum-lane",
    "appliance_factory": "offline-oob-role-separated-quorum",
}

EXPECTED_OPERATOR_ACCESS = {
    "fleet_host": "brokered-jit-cert-role-shell-escalation-separate",
    "workstation": "local-user-presence-preferred-jit-remote-admin-exceptional",
    "general_os": "local-admin-default-jit-remote-preferred-explicit-static-key-adapter",
    "appliance_factory": "maintenance-window-jit-cert-quorum-no-standing-admin-keys",
}

EXPECTED_TIME_AUTHORITY = {
    "fleet_host": "authenticated-quorum-lkgt-required-noninteractive",
    "workstation": "authenticated-preferred-visible-degraded-state-sensitive-ops-gated",
    "general_os": "authenticated-preferred-explicit-fallback",
    "appliance_factory": "offline-bounded-bootstrap-signed-time-or-authenticated-quorum",
}

EXPECTED_TRUST_BUNDLES = {
    "fleet_host": "purpose-scoped-diff-gated-shadow-trust-blocking",
    "workstation": "system-visible-trusted-ui-extra-roots",
    "general_os": "system-preferred-explicit-local-override",
    "appliance_factory": "fixed-purpose-offline-quorum-bundles",
}

EXPECTED_PLATFORM_PROVENANCE = {
    "fleet_host": "measured-receipted-and-sensitive-gating",
    "workstation": "measured-exportable-user-visible",
    "general_os": "optional-exportable-explicit-gates",
    "appliance_factory": "measured-retained-and-production-gating",
}

EXPECTED_WORKLOAD_IDENTITY = {
    "fleet_host": "brokered-short-lived-digest-bound-headless",
    "workstation": "brokered-short-lived-appvm-preferred-user-identity-separate",
    "general_os": "brokered-preferred-explicit-static-token-adapter",
    "appliance_factory": "brokered-attested-short-lived-no-static-production-secrets",
}

WORKSTATION_FORBIDDEN = "General-purpose app execution on host outside trusted UI / broker set"
WORKSTATION_NO_AUTOMOUNT = "Automount of removable media into trusted host UI plane"
WORKSTATION_NO_AMBIENT_EGRESS = "Ambient direct-socket egress for general interactive apps"
WORKSTATION_NO_AMBIENT_INGRESS = "Ambient LAN/WAN listeners for general interactive apps"
WORKSTATION_NO_STEALTH_REMOTE = "Stealth remote view/control outside the trusted UI path"
WORKSTATION_NO_RAW_KEYS = "Raw exportable private-key files for general interactive apps by default"
WORKSTATION_NO_WHOLE_HOME = "Whole portable home mounted into general interactive AppVMs by default"
WORKSTATION_NO_AMBIENT_UNLOCK = "Image-baked or ambient file-backed unlock keys for ordinary user state"
WORKSTATION_NO_INVISIBLE_EXPORT = "Invisible remembered export/support upload authority outside trusted UI lease / policy paths"
WORKSTATION_NO_STANDING_REMOTE_ADMIN = "Standing remote shell admin for workstation management by default"
WORKSTATION_NO_SILENT_TIME_FALLBACK = "Invisible unauthenticated time fallback for expiry-sensitive operations"
WORKSTATION_NO_STATIC_APP_TOKENS = "Long-lived cloud/API tokens for general interactive apps by default"
WORKSTATION_NO_SILENT_FIRMWARE = "Silent unattended firmware or Secure Boot trust-root updates outside trusted UI consent / maintenance path"
WORKSTATION_NO_SILENT_HOST_UPDATE = "Silent unattended host-generation apply/reboot outside trusted UI policy / maintenance path"
WORKSTATION_NO_SILENT_KERNEL_MUTATION = "Silent background kernel-mutation writes or module loads outside trusted UI / maintenance path"
WORKSTATION_NO_WEAK_DISK_CONFIRM = "Destructive reinstall or repartition on the wrong disk via weak/no trusted-UI disk identity confirmation"
WORKSTATION_NO_RAW_DEVNODES = "Ambient raw host device nodes for general interactive apps outside portal or trusted-UI-mediated exception paths"
WORKSTATION_NO_AMBIENT_DIAGNOSTIC_UPLOAD = "Ambient background diagnostic upload or always-on high-detail support capture outside trusted UI / policy lanes"
WORKSTATION_NO_SILENT_TOPOLOGY = "Silent host-topology mutation that can strand the machine or silently broaden exposure outside trusted UI / confirm window"
WORKSTATION_NO_SILENT_ROOT_INJECTION = "Silent enterprise / custom trust-root injection outside trusted UI / review path"
WORKSTATION_NO_SHADOW_TRUST = "App-shipped shadow trust stores for general interactive apps by default"
APPLIANCE_NO_LIVE_TRUST_ROOT = "Live production trust-root injection or ad-hoc CA edits outside approved offline bundle / quorum lane"
FLEET_NO_SHADOW_TRUST = "Embedded or per-app trust stores in official fleet lanes that bypass governed trust bundles"
APPLIANCE_NO_ADHOC_TOPOLOGY = "Ad-hoc live production topology mutation outside approved maintenance window / rollback path"
FLEET_NO_UNCONFIRMED_TOPOLOGY = "Unconfirmed live host-topology mutation that can strand remote nodes or silently broaden exposure"
GENERAL_OS_NO_AMBIENT_DIAGNOSTIC_DEP = "Ambient off-box diagnostic collection or support-agent dependency by default"
APPLIANCE_NO_LIVE_DIAGNOSTIC_STREAMING = "Ambient live production diagnostic streaming or open-ended vendor telemetry in shipped/factory images"
FLEET_NO_UNBOUNDED_DIAGNOSTICS = "Unbounded or unreceipted always-on diagnostic capture outside compiled budget / policy lanes"


def _load() -> dict:
    return json.loads(SRC.read_text(encoding="utf-8"))


def main() -> int:
    obj = _load()
    profiles = obj.get("profiles") or {}
    errors: list[str] = []

    for pid, expected in EXPECTED_RUNTIME.items():
        defaults = (profiles.get(pid) or {}).get("defaults") or {}
        got = defaults.get("runtime")
        if got != expected:
            errors.append(f"{pid}.defaults.runtime expected {expected!r}, found {got!r}")

        backups = defaults.get("backups")
        expected_backups = EXPECTED_BACKUPS[pid]
        if backups != expected_backups:
            errors.append(
                f"{pid}.defaults.backups expected {expected_backups!r}, found {backups!r}"
            )

        removable_media = defaults.get("removable_media")
        expected_rm = EXPECTED_REMOVABLE_MEDIA[pid]
        if removable_media != expected_rm:
            errors.append(
                f"{pid}.defaults.removable_media expected {expected_rm!r}, found {removable_media!r}"
            )

        usb_isolation = defaults.get("usb_isolation")
        expected_usb = EXPECTED_USB_ISOLATION[pid]
        if usb_isolation != expected_usb:
            errors.append(
                f"{pid}.defaults.usb_isolation expected {expected_usb!r}, found {usb_isolation!r}"
            )

        network_egress = defaults.get("network_egress")
        expected_egress = EXPECTED_NETWORK_EGRESS[pid]
        if network_egress != expected_egress:
            errors.append(
                f"{pid}.defaults.network_egress expected {expected_egress!r}, found {network_egress!r}"
            )

        dns_resolution = defaults.get("dns_resolution")
        expected_dns = EXPECTED_DNS_RESOLUTION[pid]
        if dns_resolution != expected_dns:
            errors.append(
                f"{pid}.defaults.dns_resolution expected {expected_dns!r}, found {dns_resolution!r}"
            )

        network_ingress = defaults.get("network_ingress")
        expected_ingress = EXPECTED_NETWORK_INGRESS[pid]
        if network_ingress != expected_ingress:
            errors.append(
                f"{pid}.defaults.network_ingress expected {expected_ingress!r}, found {network_ingress!r}"
            )

        networking = defaults.get("networking")
        expected_networking = EXPECTED_NETWORKING[pid]
        if networking != expected_networking:
            errors.append(
                f"{pid}.defaults.networking expected {expected_networking!r}, found {networking!r}"
            )

        remote_assistance = defaults.get("remote_assistance")
        expected_remote = EXPECTED_REMOTE_ASSISTANCE[pid]
        if remote_assistance != expected_remote:
            errors.append(
                f"{pid}.defaults.remote_assistance expected {expected_remote!r}, found {remote_assistance!r}"
            )

        private_keys = defaults.get("private_keys")
        expected_private_keys = EXPECTED_PRIVATE_KEYS[pid]
        if private_keys != expected_private_keys:
            errors.append(
                f"{pid}.defaults.private_keys expected {expected_private_keys!r}, found {private_keys!r}"
            )

        home_identity = defaults.get("home_identity")
        expected_home_identity = EXPECTED_HOME_IDENTITY[pid]
        if home_identity != expected_home_identity:
            errors.append(
                f"{pid}.defaults.home_identity expected {expected_home_identity!r}, found {home_identity!r}"
            )

        data_at_rest = defaults.get("data_at_rest")
        expected_data_at_rest = EXPECTED_DATA_AT_REST[pid]
        if data_at_rest != expected_data_at_rest:
            errors.append(
                f"{pid}.defaults.data_at_rest expected {expected_data_at_rest!r}, found {data_at_rest!r}"
            )

        evidence = defaults.get("evidence")
        expected_evidence = EXPECTED_EVIDENCE[pid]
        if evidence != expected_evidence:
            errors.append(
                f"{pid}.defaults.evidence expected {expected_evidence!r}, found {evidence!r}"
            )

        evidence_exports = defaults.get("evidence_exports")
        expected_evidence_exports = EXPECTED_EVIDENCE_EXPORTS[pid]
        if evidence_exports != expected_evidence_exports:
            errors.append(
                f"{pid}.defaults.evidence_exports expected {expected_evidence_exports!r}, found {evidence_exports!r}"
            )

        firmware_updates = defaults.get("firmware_updates")
        expected_firmware_updates = EXPECTED_FIRMWARE_UPDATES[pid]
        if firmware_updates != expected_firmware_updates:
            errors.append(
                f"{pid}.defaults.firmware_updates expected {expected_firmware_updates!r}, found {firmware_updates!r}"
            )

        updates = defaults.get("updates")
        expected_updates = EXPECTED_UPDATES[pid]
        if updates != expected_updates:
            errors.append(
                f"{pid}.defaults.updates expected {expected_updates!r}, found {updates!r}"
            )

        store_retention = defaults.get("store_retention")
        expected_store_retention = EXPECTED_STORE_RETENTION[pid]
        if store_retention != expected_store_retention:
            errors.append(
                f"{pid}.defaults.store_retention expected {expected_store_retention!r}, found {store_retention!r}"
            )

        installation_recovery = defaults.get("installation_recovery")
        expected_installation_recovery = EXPECTED_INSTALLATION_RECOVERY[pid]
        if installation_recovery != expected_installation_recovery:
            errors.append(
                f"{pid}.defaults.installation_recovery expected {expected_installation_recovery!r}, found {installation_recovery!r}"
            )

        destructive_reprovision = defaults.get("destructive_reprovision")
        expected_destructive_reprovision = EXPECTED_DESTRUCTIVE_REPROVISION[pid]
        if destructive_reprovision != expected_destructive_reprovision:
            errors.append(
                f"{pid}.defaults.destructive_reprovision expected {expected_destructive_reprovision!r}, found {destructive_reprovision!r}"
            )

        kernel_mutation = defaults.get("kernel_mutation")
        expected_kernel_mutation = EXPECTED_KERNEL_MUTATION[pid]
        if kernel_mutation != expected_kernel_mutation:
            errors.append(
                f"{pid}.defaults.kernel_mutation expected {expected_kernel_mutation!r}, found {kernel_mutation!r}"
            )

        device_authority = defaults.get("device_authority")
        expected_device_authority = EXPECTED_DEVICE_AUTHORITY[pid]
        if device_authority != expected_device_authority:
            errors.append(
                f"{pid}.defaults.device_authority expected {expected_device_authority!r}, found {device_authority!r}"
            )

        high_risk_approvals = defaults.get("high_risk_approvals")
        expected_high_risk_approvals = EXPECTED_HIGH_RISK_APPROVALS[pid]
        if high_risk_approvals != expected_high_risk_approvals:
            errors.append(
                f"{pid}.defaults.high_risk_approvals expected {expected_high_risk_approvals!r}, found {high_risk_approvals!r}"
            )

        operator_access = defaults.get("operator_access")
        expected_operator_access = EXPECTED_OPERATOR_ACCESS[pid]
        if operator_access != expected_operator_access:
            errors.append(
                f"{pid}.defaults.operator_access expected {expected_operator_access!r}, found {operator_access!r}"
            )

        time_authority = defaults.get("time_authority")
        expected_time_authority = EXPECTED_TIME_AUTHORITY[pid]
        if time_authority != expected_time_authority:
            errors.append(
                f"{pid}.defaults.time_authority expected {expected_time_authority!r}, found {time_authority!r}"
            )

        trust_bundles = defaults.get("trust_bundles")
        expected_trust_bundles = EXPECTED_TRUST_BUNDLES[pid]
        if trust_bundles != expected_trust_bundles:
            errors.append(
                f"{pid}.defaults.trust_bundles expected {expected_trust_bundles!r}, found {trust_bundles!r}"
            )

        platform_provenance = defaults.get("platform_provenance")
        expected_platform_provenance = EXPECTED_PLATFORM_PROVENANCE[pid]
        if platform_provenance != expected_platform_provenance:
            errors.append(
                f"{pid}.defaults.platform_provenance expected {expected_platform_provenance!r}, found {platform_provenance!r}"
            )

        workload_identity = defaults.get("workload_identity")
        expected_workload_identity = EXPECTED_WORKLOAD_IDENTITY[pid]
        if workload_identity != expected_workload_identity:
            errors.append(
                f"{pid}.defaults.workload_identity expected {expected_workload_identity!r}, found {workload_identity!r}"
            )

    fleet_host = profiles.get("fleet_host") or {}
    fleet_notes = fleet_host.get("notes") or []
    if not any("replaceable" in x.lower() and "replication" in x.lower() for x in fleet_notes):
        errors.append("fleet_host.notes must mention replaceable hosts + replication-backed recovery")
    if not any("firmware" in x.lower() and ("policy" in x.lower() or "maintenance" in x.lower()) for x in fleet_notes):
        errors.append("fleet_host.notes must mention policy-gated / maintenance-shaped firmware posture")
    if not any(("install" in x.lower() or "recovery" in x.lower() or "disk" in x.lower()) and ("target-device" in x.lower() or "target device" in x.lower() or "breakglass" in x.lower() or "maintenance" in x.lower()) for x in fleet_notes):
        errors.append("fleet_host.notes must mention target-device-bound / breakglass-shaped install-recovery posture")
    if not any(("approval" in x.lower() or "approvals" in x.lower() or "quorum" in x.lower()) and ("digest" in x.lower() or "distinct principal" in x.lower() or "self-approval" in x.lower() or "self approval" in x.lower()) for x in fleet_notes):
        errors.append("fleet_host.notes must mention digest-bound/distinct-principal quorum posture for high-risk shared-trust mutations")
    if not any(("kernel mutation" in x.lower() or "sysctl" in x.lower() or "kmod" in x.lower() or "module" in x.lower()) and ("activation-first" in x.lower() or "maintenance lease" in x.lower() or "maintenance leases" in x.lower() or "preload" in x.lower()) for x in fleet_notes):
        errors.append("fleet_host.notes must mention activation-first / maintenance-leased kernel-mutation posture")
    fleet_invariants = fleet_host.get("required_invariants") or []
    if not any("restore drill" in x.lower() or "replication" in x.lower() for x in fleet_invariants):
        errors.append("fleet_host.required_invariants must mention replication / restore drills")
    if not any(("encrypted" in x.lower() or "state remains encrypted" in x.lower()) and ("attested" in x.lower() or "brokered" in x.lower()) for x in fleet_invariants):
        errors.append("fleet_host.required_invariants must mention encrypted state + attested/brokered unlock posture")
    if not any("export" in x.lower() and "ticket" in x.lower() and "encrypt" in x.lower() for x in fleet_invariants):
        errors.append("fleet_host.required_invariants must mention brokered/ticketed/encrypted evidence export posture")
    if not any(("operator access" in x.lower() or "escalation" in x.lower()) and ("jit" in x.lower() or "leased" in x.lower() or "revocable" in x.lower()) for x in fleet_invariants):
        errors.append("fleet_host.required_invariants must mention JIT/leased operator access posture")
    if not any(("authenticated time" in x.lower() or "time" in x.lower()) and ("lkgt" in x.lower() or "quorum" in x.lower()) and ("degraded" in x.lower() or "non-interactive" in x.lower() or "noninteractive" in x.lower()) for x in fleet_invariants):
        errors.append("fleet_host.required_invariants must mention authenticated time + quorum/LKGT + non-interactive degraded posture")
    if not any(("measured" in x.lower() or "attestation" in x.lower() or "platform posture" in x.lower()) and ("admission" in x.lower() or "identity" in x.lower() or "secret" in x.lower() or "rollout" in x.lower()) for x in fleet_invariants):
        errors.append("fleet_host.required_invariants must mention receipted measured posture gating sensitive admissions")
    if not any(("firmware" in x.lower() or "uefi" in x.lower()) and ("maintenance" in x.lower() or "policy" in x.lower()) and ("receipt" in x.lower() or "gate" in x.lower() or "post-reboot" in x.lower() or "postreboot" in x.lower() or "stage" in x.lower()) for x in fleet_invariants):
        errors.append("fleet_host.required_invariants must mention maintenance/policy-gated firmware posture with post-reboot receipts/gates")
    if not any(("evidence" in x.lower() or "diagnostic" in x.lower() or "flight recorder" in x.lower()) and "always-on" in x.lower() and "bounded" in x.lower() and ("receipted" in x.lower() or "policy" in x.lower()) for x in fleet_invariants):
        errors.append("fleet_host.required_invariants must mention always-on bounded evidence collection posture with explicit/policy-shaped expansion")
    if not any(("gc" in x.lower() or "rollback floor" in x.lower() or "retention" in x.lower()) and ("bootable" in x.lower() or "rollback" in x.lower()) and ("silent" in x.lower() or "bytes" in x.lower() or "cohort" in x.lower()) for x in fleet_invariants):
        errors.append("fleet_host.required_invariants must mention rollback-floor GC posture")
    if not any(("network topology" in x.lower() or "links/addresses/routes" in x.lower() or "pf root" in x.lower() or "topology" in x.lower()) and ("activation-first" in x.lower() or "commit-confirmed" in x.lower() or "commit confirmed" in x.lower()) and ("maintenance lease" in x.lower() or "rollback" in x.lower() or "remote-brick" in x.lower() or "remote brick" in x.lower()) for x in fleet_invariants):
        errors.append("fleet_host.required_invariants must mention activation-first commit-confirmed network-topology posture with maintenance leases / rollback")
    if not any(("update" in x.lower()) and ("health-gated" in x.lower() or "rollout" in x.lower()) and ("receipt" in x.lower() or "channel" in x.lower() or "health" in x.lower() or "promotion" in x.lower()) for x in fleet_invariants):
        errors.append("fleet_host.required_invariants must mention health-gated rollout-shaped update posture with signed-channel/health-gate receipts")
    if not any(("install" in x.lower() or "recovery" in x.lower() or "disk" in x.lower()) and ("target-device" in x.lower() or "target device" in x.lower()) and ("breakglass" in x.lower() or "maintenance" in x.lower() or "recovery media" in x.lower() or "verifiable" in x.lower()) for x in fleet_invariants):
        errors.append("fleet_host.required_invariants must mention target-device-bound/additive install-recovery posture with breakglass and verified recovery media")
    if not any(("approval" in x.lower() or "approvals" in x.lower() or "quorum" in x.lower()) and ("digest" in x.lower() or "role-separated" in x.lower() or "role separated" in x.lower() or "distinct principal" in x.lower()) and ("publish" in x.lower() or "trust-root" in x.lower() or "breakglass" in x.lower() or "receipt" in x.lower()) for x in fleet_invariants):
        errors.append("fleet_host.required_invariants must mention digest-bound role-separated approval posture for publish/trust-root/breakglass mutations")
    if not any(("kernel mutation" in x.lower() or "sysctl" in x.lower() or "module" in x.lower() or "kmod" in x.lower()) and ("activation-first" in x.lower() or "generation-bound" in x.lower() or "generation bound" in x.lower()) and ("maintenance lease" in x.lower() or "receipt" in x.lower() or "preload" in x.lower() or "lockdown" in x.lower()) for x in fleet_invariants):
        errors.append("fleet_host.required_invariants must mention activation-first kernel-mutation posture with generation-bound tunables, maintenance-leased runtime writes, and preload/lockdown")

    if not any(("device authority" in x.lower() or "device-node" in x.lower() or "device node" in x.lower() or "/dev" in x.lower()) and ("compiled-minimal" in x.lower() or "compiled minimal" in x.lower() or "lease" in x.lower()) and ("raw block" in x.lower() or "input" in x.lower() or "capture" in x.lower() or "packet" in x.lower() or "receipt" in x.lower()) for x in fleet_invariants):
        errors.append("fleet_host.required_invariants must mention compiled-minimal/lease-shaped device authority posture with no ambient raw device authority")

    general_os = profiles.get("general_os") or {}
    general_notes = general_os.get("notes") or []
    if not any("backup" in x.lower() and ("choice" in x.lower() or "tool" in x.lower()) for x in general_notes):
        errors.append("general_os.notes must mention explicit backup-tool choice")
    if not any("encrypt" in x.lower() and ("preferred" in x.lower() or "compatibility" in x.lower()) for x in general_notes):
        errors.append("general_os.notes must mention encryption-preferred / explicit-compatibility posture")
    if not any(("support" in x.lower() or "upload" in x.lower() or "export" in x.lower()) and "adapter" in x.lower() for x in general_notes):
        errors.append("general_os.notes must mention explicit support/upload adapter fallback posture")
    if not any(("remote admin" in x.lower() or "static-key" in x.lower() or "static key" in x.lower()) and ("adapter" in x.lower() or "jit" in x.lower() or "leased" in x.lower()) for x in general_notes):
        errors.append("general_os.notes must mention JIT-remote / static-key-adapter operator-access posture")
    if not any(("authenticated time" in x.lower() or "time" in x.lower()) and ("preferred" in x.lower() or "easy" in x.lower()) and ("fallback" in x.lower() or "compatibility" in x.lower()) for x in general_notes):
        errors.append("general_os.notes must mention authenticated-time preferred / explicit-fallback posture")
    if not any(("measured" in x.lower() or "attestation" in x.lower()) and ("optional" in x.lower() or "explicit" in x.lower()) and ("exportable" in x.lower() or "export" in x.lower()) for x in general_notes):
        errors.append("general_os.notes must mention optional/exportable attestation posture")
    if not any(("single-principal" in x.lower() or "single principal" in x.lower() or "local admin" in x.lower()) and ("quorum" in x.lower() or "separation-of-duties" in x.lower() or "separation of duties" in x.lower()) and ("optional" in x.lower() or "explicit" in x.lower() or "prerequisite" in x.lower()) for x in general_notes):
        errors.append("general_os.notes must mention single-principal viability with explicit optional quorum lane")
    if not any(("workload identity" in x.lower()) and ("preferred" in x.lower()) and ("static-token" in x.lower() or "file-credential" in x.lower() or "adapter" in x.lower()) for x in general_notes):
        errors.append("general_os.notes must mention preferred workload identity posture with explicit static-token/file-credential adapter fallback")
    if not any("firmware" in x.lower() and ("user choice" in x.lower() or "adapter" in x.lower() or "fwupd" in x.lower()) for x in general_notes):
        errors.append("general_os.notes must mention user-choice firmware posture with explicit adapter fallback")
    if not any(("install" in x.lower() or "recovery" in x.lower()) and ("classic-installer" in x.lower() or "classic installer" in x.lower() or "guided" in x.lower()) and ("destructive" in x.lower() or "encrypt" in x.lower() or "preferred" in x.lower()) for x in general_notes):
        errors.append("general_os.notes must mention guided/classic install choice with explicit destructive/encryption posture")
    if not any(("transactional" in x.lower() or "update" in x.lower()) and ("rollout" in x.lower() or "health-gate" in x.lower() or "health gate" in x.lower() or "offline bundle" in x.lower()) and ("explicit" in x.lower() or "choice" in x.lower() or "hidden" in x.lower() or "prerequisite" in x.lower()) for x in general_notes):
        errors.append("general_os.notes must mention transactional baseline with rollout/health-gate/offline-bundle lanes remaining explicit choices")
    if not any(("kernel mutation" in x.lower() or "sysctl" in x.lower() or "module" in x.lower() or "kmod" in x.lower()) and ("derived" in x.lower() or "derive-managed" in x.lower() or "derive managed" in x.lower()) and ("local-admin fallback" in x.lower() or "local admin fallback" in x.lower() or "explicit" in x.lower()) for x in general_notes):
        errors.append("general_os.notes must mention derive-managed kernel mutation with explicit local-admin fallback")
    general_invariants = general_os.get("required_invariants") or []
    if not any(("attestation" in x.lower() or "measured" in x.lower()) and ("explicit" in x.lower() or "reviewable" in x.lower()) and ("tpm" in x.lower() or "verifier" in x.lower() or "default installs" in x.lower() or "compatibility" in x.lower()) for x in general_invariants):
        errors.append("general_os.required_invariants must mention explicit/reviewable attestation gates without silent TPM/verifier dependency")
    if not any(("workload identity" in x.lower()) and ("preferred" in x.lower()) and ("static-token" in x.lower() or "file-credential" in x.lower() or "adapter" in x.lower()) for x in general_invariants):
        errors.append("general_os.required_invariants must mention preferred workload identity posture with explicit static-token/file-credential adapter fallback")
    if not any(("firmware" in x.lower()) and ("receipt" in x.lower() or "planned" in x.lower() or "receipted" in x.lower()) and ("adapter" in x.lower() or "vendor" in x.lower() or "ambient" in x.lower()) for x in general_invariants):
        errors.append("general_os.required_invariants must mention receipted firmware posture with explicit adapter/vendortool fallback")
    if not any(("transactional" in x.lower() or "update" in x.lower()) and ("rollout" in x.lower() or "health-gate" in x.lower() or "health gate" in x.lower() or "offline-bundle" in x.lower() or "offline bundle" in x.lower()) and ("explicit" in x.lower() or "killable" in x.lower() or "coordinator" in x.lower()) for x in general_invariants):
        errors.append("general_os.required_invariants must mention standalone transactional update viability and explicit rollout/health-gate/offline-bundle lanes")
    if not any(("install" in x.lower() or "recovery" in x.lower()) and ("guided" in x.lower() or "compatibility" in x.lower() or "classic" in x.lower()) and ("destructive" in x.lower() or "encrypt" in x.lower() or "fallback" in x.lower()) for x in general_invariants):
        errors.append("general_os.required_invariants must mention explicit guided/compatibility install-recovery posture with visible destructive path and encryption fallback")

    if not any(("evidence" in x.lower() or "diagnostic" in x.lower() or "support agent" in x.lower() or "collector" in x.lower()) and ("local-retained" in x.lower() or "local retained" in x.lower()) and ("explicit-export" in x.lower() or "explicit export" in x.lower() or "optional" in x.lower() or "killable" in x.lower()) for x in general_invariants):
        errors.append("general_os.required_invariants must mention local-retained explicit-export evidence posture with optional/killable remote collectors")
    if not any(("gc" in x.lower() or "pins" in x.lower() or "generations" in x.lower()) and ("explicit" in x.lower() or "queryable" in x.lower()) and ("admin" in x.lower() or "surprise" in x.lower()) for x in general_invariants):
        errors.append("general_os.required_invariants must mention explicit/queryable GC posture with local-admin cleanup choice")

    if not any(("network topology" in x.lower() or "links/addresses/routes" in x.lower() or "topology" in x.lower()) and ("derived" in x.lower() or "plan" in x.lower() or "receipt" in x.lower()) and ("local-admin fallback" in x.lower() or "local admin fallback" in x.lower() or "compatibility" in x.lower() or "reviewable" in x.lower()) for x in general_invariants):
        errors.append("general_os.required_invariants must mention derived-preferred network-topology posture with explicit local-admin fallback")

    if not any(("local admin" in x.lower() or "install" in x.lower() or "update" in x.lower()) and ("approver" in x.lower() or "quorum" in x.lower() or "separation-of-duties" in x.lower() or "separation of duties" in x.lower()) and ("optional" in x.lower() or "explicit" in x.lower() or "reachability" in x.lower() or "without" in x.lower()) for x in general_invariants):
        errors.append("general_os.required_invariants must mention no central approver dependency for ordinary local flows and explicit optional quorum lane")
    if not any(("kernel mutation" in x.lower() or "sysctl" in x.lower() or "module" in x.lower() or "kmod" in x.lower()) and ("derive-managed" in x.lower() or "derive managed" in x.lower() or "default" in x.lower()) and ("local-admin fallback" in x.lower() or "local admin fallback" in x.lower() or "explicit" in x.lower()) and ("reviewable" in x.lower() or "receipted" in x.lower() or "ambient" in x.lower()) for x in general_invariants):
        errors.append("general_os.required_invariants must mention derive-managed default kernel-mutation posture with explicit local-admin fallback and no ambient service authority")

    if not any(("device authority" in x.lower() or "device-node" in x.lower() or "device node" in x.lower() or "/dev" in x.lower()) and ("compiled-minimal" in x.lower() or "compiled minimal" in x.lower() or "mediated" in x.lower() or "portal" in x.lower()) and ("compatibility" in x.lower() or "fallback" in x.lower() or "explicit" in x.lower() or "ambient" in x.lower()) for x in general_invariants):
        errors.append("general_os.required_invariants must mention compiled-minimal/mediated preferred device authority with explicit compatibility fallback")

    appliance_factory = profiles.get("appliance_factory") or {}
    appliance_invariants = appliance_factory.get("required_invariants") or []
    if not any("restore drill" in x.lower() for x in appliance_invariants):
        errors.append("appliance_factory.required_invariants must mention recurring restore drills")
    if not any(("encrypted" in x.lower() or "state remains encrypted" in x.lower()) and ("attested" in x.lower() or "quorum" in x.lower() or "brokered" in x.lower()) for x in appliance_invariants):
        errors.append("appliance_factory.required_invariants must mention encrypted production state + attested/quorum/brokered unlock posture")
    if not any(("export" in x.lower() or "sharing" in x.lower()) and "redacted" in x.lower() and "encrypt" in x.lower() for x in appliance_invariants):
        errors.append("appliance_factory.required_invariants must mention minimal/redacted/encrypted evidence export posture")
    if not any(("maintenance" in x.lower() or "operator access" in x.lower()) and ("jit" in x.lower() or "quorum" in x.lower() or "standing" in x.lower()) for x in appliance_invariants):
        errors.append("appliance_factory.required_invariants must mention maintenance-window / JIT / no-standing-admin-key posture")
    if not any(("offline" in x.lower() or "bootstrap" in x.lower() or "signed time" in x.lower() or "authenticated quorum" in x.lower()) and ("expiry" in x.lower() or "freshness" in x.lower() or "evidentiary" in x.lower()) for x in appliance_invariants):
        errors.append("appliance_factory.required_invariants must mention bounded offline/bootstrap time with signed/authenticated evidence posture")
    if not any(("measured" in x.lower() or "attestation" in x.lower() or "platform posture" in x.lower()) and ("retain" in x.lower() or "retained" in x.lower()) and ("production" in x.lower() or "maintenance" in x.lower() or "secret" in x.lower() or "enrollment" in x.lower()) for x in appliance_invariants):
        errors.append("appliance_factory.required_invariants must mention retained measured posture gating production/maintenance-sensitive admissions")
    if not any(("production" in x.lower() or "service authentication" in x.lower() or "workload" in x.lower()) and ("short-lived" in x.lower() or "issued identities" in x.lower() or "identity" in x.lower()) and ("static shared secrets" in x.lower() or "out of bounds" in x.lower() or "brokered" in x.lower()) for x in appliance_invariants):
        errors.append("appliance_factory.required_invariants must mention short-lived production identities and no shipped static shared secrets posture")
    if not any(("firmware" in x.lower() or "uefi" in x.lower()) and ("offline" in x.lower() or "staged" in x.lower() or "bundle" in x.lower() or "mirror" in x.lower()) and ("receipt" in x.lower() or "approval" in x.lower() or "review" in x.lower()) for x in appliance_invariants):
        errors.append("appliance_factory.required_invariants must mention offline-staged firmware posture with retained receipts/approval")
    if not any(("update" in x.lower()) and ("offline" in x.lower() or "bundle" in x.lower() or "mirror kit" in x.lower() or "mirror-kit" in x.lower()) and ("quarantine" in x.lower() or "promote" in x.lower() or "approval" in x.lower() or "receipt" in x.lower()) for x in appliance_invariants):
        errors.append("appliance_factory.required_invariants must mention offline-bundle/mirror-kit update delivery with quarantine→promote and retained approval/receipts")
    if not any(("install" in x.lower() or "recovery" in x.lower() or "reprovision" in x.lower() or "reset" in x.lower()) and ("target-device" in x.lower() or "target device" in x.lower() or "offline" in x.lower()) and ("signed" in x.lower() or "receipt" in x.lower() or "approval" in x.lower() or "recovery media" in x.lower()) for x in appliance_invariants):
        errors.append("appliance_factory.required_invariants must mention target-device-bound/offline install-recovery posture with signed reset authority and verified recovery media")
    if not any(("publish" in x.lower() or "trust-root" in x.lower() or "reset" in x.lower() or "exposure" in x.lower()) and ("digest" in x.lower() or "role-separated" in x.lower() or "role separated" in x.lower()) and ("quorum" in x.lower() or "offline" in x.lower() or "oob" in x.lower() or "out-of-band" in x.lower()) for x in appliance_invariants):
        errors.append("appliance_factory.required_invariants must mention digest-bound role-separated offline/OOB quorum posture for production mutations")
    if not any(("kernel mutation" in x.lower() or "sysctl" in x.lower() or "module" in x.lower() or "kmod" in x.lower()) and ("preload-only" in x.lower() or "preload only" in x.lower() or "lockdown" in x.lower()) and ("offline" in x.lower() or "maintenance" in x.lower() or "receipt" in x.lower()) for x in appliance_invariants):
        errors.append("appliance_factory.required_invariants must mention preload-only/lockdown kernel-mutation posture with offline or strongly approved maintenance workflows")

    if not any(("evidence" in x.lower() or "diagnostic" in x.lower() or "bundle" in x.lower() or "telemetry" in x.lower()) and ("bundle-oriented" in x.lower() or "bundle oriented" in x.lower() or "bundled" in x.lower()) and "redacted" in x.lower() and ("retention" in x.lower() or "streaming" in x.lower() or "production" in x.lower()) for x in appliance_invariants):
        errors.append("appliance_factory.required_invariants must mention bundle-oriented minimal/redacted evidence posture and no ambient production streaming")
    if not any(("gc" in x.lower() or "rollback" in x.lower() or "audit" in x.lower()) and ("offline" in x.lower() or "maintenance" in x.lower()) and ("receipt" in x.lower() or "coverage" in x.lower() or "floor" in x.lower()) for x in appliance_invariants):
        errors.append("appliance_factory.required_invariants must mention offline/auditable rollback-floor GC posture")

    if not any(("device authority" in x.lower() or "device-node" in x.lower() or "device node" in x.lower() or "/dev" in x.lower()) and ("compiled-minimal" in x.lower() or "compiled minimal" in x.lower() or "sealed" in x.lower()) and ("offline" in x.lower() or "approved" in x.lower() or "receipt" in x.lower() or "debug" in x.lower()) for x in appliance_invariants):
        errors.append("appliance_factory.required_invariants must mention compiled-minimal sealed device authority posture with offline/approved expansion")
    if not any(("topology" in x.lower() or "links/addresses/routes" in x.lower() or "pf root" in x.lower()) and ("sealed" in x.lower() or "maintenance-window" in x.lower() or "maintenance window" in x.lower()) and ("rollback" in x.lower() or "receipt" in x.lower() or "approved" in x.lower()) for x in appliance_invariants):
        errors.append("appliance_factory.required_invariants must mention sealed maintenance-window-shaped network-topology posture with rollback/receipts")

    workstation = profiles.get("workstation") or {}
    forbidden = workstation.get("forbidden_by_default") or []
    if WORKSTATION_FORBIDDEN not in forbidden:
        errors.append(
            "workstation.forbidden_by_default missing "
            f"{WORKSTATION_FORBIDDEN!r}"
        )
    if WORKSTATION_NO_AUTOMOUNT not in forbidden:
        errors.append(
            "workstation.forbidden_by_default missing "
            f"{WORKSTATION_NO_AUTOMOUNT!r}"
        )
    if WORKSTATION_NO_AMBIENT_EGRESS not in forbidden:
        errors.append(
            "workstation.forbidden_by_default missing "
            f"{WORKSTATION_NO_AMBIENT_EGRESS!r}"
        )
    if WORKSTATION_NO_AMBIENT_INGRESS not in forbidden:
        errors.append(
            "workstation.forbidden_by_default missing "
            f"{WORKSTATION_NO_AMBIENT_INGRESS!r}"
        )
    if WORKSTATION_NO_STEALTH_REMOTE not in forbidden:
        errors.append(
            "workstation.forbidden_by_default missing "
            f"{WORKSTATION_NO_STEALTH_REMOTE!r}"
        )

    if WORKSTATION_NO_RAW_KEYS not in forbidden:
        errors.append(
            "workstation.forbidden_by_default missing "
            f"{WORKSTATION_NO_RAW_KEYS!r}"
        )
    if WORKSTATION_NO_WHOLE_HOME not in forbidden:
        errors.append(
            "workstation.forbidden_by_default missing "
            f"{WORKSTATION_NO_WHOLE_HOME!r}"
        )
    if WORKSTATION_NO_AMBIENT_UNLOCK not in forbidden:
        errors.append(
            "workstation.forbidden_by_default missing "
            f"{WORKSTATION_NO_AMBIENT_UNLOCK!r}"
        )
    if WORKSTATION_NO_INVISIBLE_EXPORT not in forbidden:
        errors.append(
            "workstation.forbidden_by_default missing "
            f"{WORKSTATION_NO_INVISIBLE_EXPORT!r}"
        )
    if WORKSTATION_NO_STANDING_REMOTE_ADMIN not in forbidden:
        errors.append(
            "workstation.forbidden_by_default missing "
            f"{WORKSTATION_NO_STANDING_REMOTE_ADMIN!r}"
        )
    if WORKSTATION_NO_SILENT_TIME_FALLBACK not in forbidden:
        errors.append(
            "workstation.forbidden_by_default missing "
            f"{WORKSTATION_NO_SILENT_TIME_FALLBACK!r}"
        )
    if WORKSTATION_NO_STATIC_APP_TOKENS not in forbidden:
        errors.append(
            "workstation.forbidden_by_default missing "
            f"{WORKSTATION_NO_STATIC_APP_TOKENS!r}"
        )
    if WORKSTATION_NO_SILENT_FIRMWARE not in forbidden:
        errors.append(
            "workstation.forbidden_by_default missing "
            f"{WORKSTATION_NO_SILENT_FIRMWARE!r}"
        )
    if WORKSTATION_NO_SILENT_HOST_UPDATE not in forbidden:
        errors.append(
            "workstation.forbidden_by_default missing "
            f"{WORKSTATION_NO_SILENT_HOST_UPDATE!r}"
        )
    if WORKSTATION_NO_SILENT_KERNEL_MUTATION not in forbidden:
        errors.append(
            "workstation.forbidden_by_default missing "
            f"{WORKSTATION_NO_SILENT_KERNEL_MUTATION!r}"
        )
    if WORKSTATION_NO_WEAK_DISK_CONFIRM not in forbidden:
        errors.append(
            "workstation.forbidden_by_default missing "
            f"{WORKSTATION_NO_WEAK_DISK_CONFIRM!r}"
        )
    if WORKSTATION_NO_RAW_DEVNODES not in forbidden:
        errors.append(
            "workstation.forbidden_by_default missing "
            f"{WORKSTATION_NO_RAW_DEVNODES!r}"
        )
    if WORKSTATION_NO_AMBIENT_DIAGNOSTIC_UPLOAD not in forbidden:
        errors.append(
            "workstation.forbidden_by_default missing "
            f"{WORKSTATION_NO_AMBIENT_DIAGNOSTIC_UPLOAD!r}"
        )
    if WORKSTATION_NO_SILENT_TOPOLOGY not in forbidden:
        errors.append(
            "workstation.forbidden_by_default missing "
            f"{WORKSTATION_NO_SILENT_TOPOLOGY!r}"
        )

    notes = workstation.get("notes") or []
    if not any("firmware" in x.lower() and ("trusted ui" in x.lower() or "consent" in x.lower() or "silent" in x.lower()) for x in notes):
        errors.append("workstation.notes must mention trusted-UI/consent-first firmware posture")
    if not any(("install" in x.lower() or "recovery" in x.lower()) and ("trusted-ui" in x.lower() or "trusted ui" in x.lower() or "disk confirmation" in x.lower() or "encrypted-root" in x.lower()) for x in notes):
        errors.append("workstation.notes must mention trusted-UI-guided install-recovery posture with disk confirmation/encrypted default")
    if not any(("trusted-ui" in x.lower() or "trusted ui" in x.lower() or "user-consent" in x.lower() or "user consent" in x.lower()) and ("shared-trust" in x.lower() or "org-wide" in x.lower() or "admin lane" in x.lower() or "ordinary prompts" in x.lower()) for x in notes):
        errors.append("workstation.notes must mention trusted-UI user-consent-first posture and separate admin lane for shared-trust mutations")
    if not any(("kernel mutation" in x.lower() or "sysctl" in x.lower() or "module" in x.lower() or "kmod" in x.lower()) and ("activation-first" in x.lower() or "trusted-ui" in x.lower() or "trusted ui" in x.lower()) and ("maintenance" in x.lower() or "background" in x.lower() or "visible" in x.lower()) for x in notes):
        errors.append("workstation.notes must mention activation-first trusted-UI-mediated kernel-mutation posture")
    if not any(("cleanup" in x.lower() or "space pressure" in x.lower() or "rollback" in x.lower()) and ("trusted-ui" in x.lower() or "trusted ui" in x.lower() or "human" in x.lower()) for x in notes):
        errors.append("workstation.notes must mention trusted-UI-visible cleanup posture under space pressure")

    invariants = workstation.get("required_invariants") or []
    if not any("trusted UI boundary" in x or "secure attention" in x for x in invariants):
        errors.append("workstation.required_invariants must mention trusted UI / secure attention")
    if not any("Portal-mediated" in x or "portal-mediated" in x for x in invariants):
        errors.append("workstation.required_invariants must mention portal-mediated access")
    if not any(("export" in x.lower() or "replication" in x.lower()) and "recovery" in x.lower() for x in invariants):
        errors.append("workstation.required_invariants must mention explicit export/replication recovery posture")
    if not any("lease" in x.lower() or "policy edit" in x.lower() or "exceptions" in x.lower() for x in invariants):
        errors.append("workstation.required_invariants must mention lease/policy landing for network prompts")
    if not any("lan/wan listeners" in x.lower() or ("sharing/support" in x.lower() and "timebox" in x.lower()) for x in invariants):
        errors.append("workstation.required_invariants must mention no ambient ingress / timeboxed sharing")
    if not any("remote assistance" in x.lower() and ("secure-attention" in x.lower() or "lease" in x.lower() or "revocable" in x.lower()) for x in invariants):
        errors.append("workstation.required_invariants must mention visible/leased remote assistance posture")

    if not any(("user-presence" in x.lower() or "user presence" in x.lower()) and ("raw key bytes" in x.lower() or "crypto operations" in x.lower()) for x in invariants):
        errors.append("workstation.required_invariants must mention user-presence-gated crypto / no raw key bytes posture")
    if not any(("unlocks on login" in x.lower() or "login" in x.lower()) and ("relock" in x.lower() or "unmount" in x.lower()) for x in invariants):
        errors.append("workstation.required_invariants must mention login-bounded home unlock / relock posture")
    if not any(("lost-device" in x.lower() or "lost/stolen-device" in x.lower() or "login-bounded" in x.lower()) and ("user state" in x.lower() or "boot-available" in x.lower() or "private user state" in x.lower()) for x in invariants):
        errors.append("workstation.required_invariants must mention lost-device/login-bounded user-state posture")
    if not any(("whole-home" in x.lower() or "whole home" in x.lower()) and ("lease" in x.lower() or "explicit" in x.lower()) for x in invariants):
        errors.append("workstation.required_invariants must mention no default whole-home AppVM sharing / explicit lease posture")
    if not any(("evidence sharing" in x.lower() or "support" in x.lower() or "export" in x.lower()) and ("recipient" in x.lower() or "redaction" in x.lower()) and ("lease" in x.lower() or "policy" in x.lower()) for x in invariants):
        errors.append("workstation.required_invariants must mention recipient-visible / leased evidence export posture")
    if not any(("local admin" in x.lower() or "elevation" in x.lower()) and ("presence" in x.lower() or "secure-attention" in x.lower() or "secure attention" in x.lower()) for x in invariants):
        errors.append("workstation.required_invariants must mention local presence / secure-attention admin posture")
    if not any(("remote shell admin" in x.lower() or "remote admin" in x.lower()) and ("exceptional" in x.lower() or "leased" in x.lower() or "standing" in x.lower()) for x in invariants):
        errors.append("workstation.required_invariants must mention exceptional/leased remote admin posture")
    if not any(("time health" in x.lower() or "degraded time" in x.lower() or "authenticated time" in x.lower()) and ("visible" in x.lower() or "human" in x.lower()) and ("gate" in x.lower() or "sensitive" in x.lower()) for x in invariants):
        errors.append("workstation.required_invariants must mention visible degraded time / authenticated-time gating posture")
    if not any(("measured" in x.lower() or "attestation" in x.lower() or "platform posture" in x.lower()) and ("visible" in x.lower() or "exportable" in x.lower()) and ("sensitive" in x.lower() or "ordinary local use" in x.lower() or "local use" in x.lower()) for x in invariants):
        errors.append("workstation.required_invariants must mention visible/exportable measured posture and no surprise hard dependency for ordinary local use")
    if not any(("workload identity" in x.lower() or "appvm" in x.lower() or "dev services" in x.lower()) and ("human login" in x.lower() or "account authority" in x.lower() or "user" in x.lower()) and ("token" in x.lower() or "static" in x.lower()) for x in invariants):
        errors.append("workstation.required_invariants must mention separate workload identity vs human authority and no static app-token sprawl posture")
    if not any(("firmware" in x.lower() or "secure boot" in x.lower()) and ("trusted-ui" in x.lower() or "trusted ui" in x.lower() or "consent" in x.lower()) and ("receipt" in x.lower() or "power" in x.lower() or "stage" in x.lower()) for x in invariants):
        errors.append("workstation.required_invariants must mention trusted-UI-visible/consented firmware posture with receipts and safety checks")
    if not any(("install" in x.lower() or "recovery" in x.lower() or "disk" in x.lower()) and ("trusted-ui" in x.lower() or "trusted ui" in x.lower() or "disk identity" in x.lower() or "disk confirmation" in x.lower()) and ("encrypt" in x.lower() or "recovery path" in x.lower() or "local recovery" in x.lower()) for x in invariants):
        errors.append("workstation.required_invariants must mention trusted-UI-guided install-recovery posture with explicit disk identity, encryption default, and local recovery path")
    if not any(("user-consent" in x.lower() or "user consent" in x.lower() or "trusted-ui" in x.lower() or "trusted ui" in x.lower()) and ("shared-trust" in x.lower() or "org-wide" in x.lower() or "admin lane" in x.lower()) and ("prompt" in x.lower() or "surface" in x.lower() or "enabled" in x.lower()) for x in invariants):
        errors.append("workstation.required_invariants must mention user-consent-first personal-risk posture and separate admin lane for shared-trust mutations")
    if not any(("kernel mutation" in x.lower() or "sysctl" in x.lower() or "module" in x.lower() or "kmod" in x.lower()) and ("activation-first" in x.lower() or "generation-bound" in x.lower() or "generation bound" in x.lower()) and ("trusted-ui" in x.lower() or "trusted ui" in x.lower() or "visible" in x.lower() or "silent background" in x.lower()) for x in invariants):
        errors.append("workstation.required_invariants must mention activation-first trusted-UI-mediated kernel-mutation posture and no silent background host mutation")
    if not any(("gc" in x.lower() or "rollback" in x.lower() or "space-aware" in x.lower() or "space aware" in x.lower()) and ("trusted-ui" in x.lower() or "trusted ui" in x.lower() or "human" in x.lower()) and ("pin" in x.lower() or "cleanup" in x.lower() or "rollback points" in x.lower()) for x in invariants):
        errors.append("workstation.required_invariants must mention trusted-UI-visible rollback-protecting GC posture")

    if errors:
        print("Product profile check failed:\n")
        for e in errors:
            print(f"- {e}")
        return 1

    print("Product profile check OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
