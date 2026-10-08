"""Provider-plane surface audit and supersession helpers.

The baby cube intentionally shipped both ``providerpoison`` and
``provider_poison`` while tests were pinning behavior.  That helped iteration,
but it is now an audit risk: near-duplicate names make wake-from-amnesia work
harder.  This module does not delete history.  It records the active surface,
identifies shared public names, and gives future refactors a testable target.
"""
from __future__ import annotations

from dataclasses import dataclass
from importlib import import_module
from types import ModuleType


@dataclass(frozen=True)
class ProviderSurfaceAudit:
    canonical_module: str
    legacy_module: str
    canonical_public_count: int
    legacy_public_count: int
    shared_public_names: tuple[str, ...]
    canonical_only_names: tuple[str, ...]
    legacy_only_names: tuple[str, ...]
    decision: str

    @property
    def has_overlap(self) -> bool:
        return bool(self.shared_public_names)

    @property
    def should_keep_legacy_for_now(self) -> bool:
        return self.decision == "keep_legacy_until_callers_are_migrated"


def _public_names(module: ModuleType) -> set[str]:
    return {name for name in dir(module) if not name.startswith("_") and name not in {"annotations"}}


def audit_provider_surfaces(*, canonical: str = "i2p_dht_lab.provider_poison", legacy: str = "i2p_dht_lab.providerpoison") -> ProviderSurfaceAudit:
    canonical_module = import_module(canonical)
    legacy_module = import_module(legacy)
    canonical_public = _public_names(canonical_module)
    legacy_public = _public_names(legacy_module)
    shared = tuple(sorted(canonical_public & legacy_public))
    canonical_only = tuple(sorted(canonical_public - legacy_public))
    legacy_only = tuple(sorted(legacy_public - canonical_public))
    decision = "keep_legacy_until_callers_are_migrated" if legacy_only else "legacy_can_be_compat_wrapper"
    return ProviderSurfaceAudit(
        canonical_module=canonical,
        legacy_module=legacy,
        canonical_public_count=len(canonical_public),
        legacy_public_count=len(legacy_public),
        shared_public_names=shared,
        canonical_only_names=canonical_only,
        legacy_only_names=legacy_only,
        decision=decision,
    )


@dataclass(frozen=True)
class ProviderLegacyImport:
    path: str
    line_number: int
    line: str
    historical: bool = False


@dataclass(frozen=True)
class ProviderMigrationPlan:
    audit: ProviderSurfaceAudit
    legacy_imports: tuple[ProviderLegacyImport, ...]
    wrapper_ready: bool
    recommendation: str

    @property
    def legacy_import_count(self) -> int:
        return len(self.legacy_imports)

    @property
    def historical_legacy_import_count(self) -> int:
        return sum(1 for item in self.legacy_imports if item.historical)

    @property
    def active_legacy_import_count(self) -> int:
        return sum(1 for item in self.legacy_imports if not item.historical)


def find_provider_legacy_imports(root: str, *, legacy_module: str = "i2p_dht_lab.providerpoison") -> tuple[ProviderLegacyImport, ...]:
    """Find remaining source/test imports of the legacy providerpoison surface.

    This is intentionally lexical.  It is an audit/refactor tripwire, not a
    Python import graph.  The goal is to make the remaining historical callers
    visible before turning ``providerpoison.py`` into a pure compatibility shim.

    rev0017 classifies rev0011's old behavior-pinning test as historical rather
    than active code.  The old import still counts, but future migration can now
    distinguish "kept to preserve evidence" from "new caller accidentally used
    the shadow surface."
    """
    from pathlib import Path

    root_path = Path(root)
    findings: list[ProviderLegacyImport] = []
    needles = (f"from {legacy_module} import", f"import {legacy_module}")
    for path in sorted(list((root_path / "src").rglob("*.py")) + list((root_path / "tests").rglob("*.py"))):
        if path.name == "provider_refactor.py":
            continue
        text = path.read_text(encoding="utf-8")
        for idx, line in enumerate(text.splitlines(), start=1):
            if any(needle in line for needle in needles):
                rel = str(path.relative_to(root_path))
                historical = rel.startswith("tests/test_rev0011_providerpoison_gardenrefusal.py")
                findings.append(ProviderLegacyImport(rel, idx, line.strip(), historical))
    return tuple(findings)


def plan_provider_surface_migration(root: str, *, canonical: str = "i2p_dht_lab.provider_poison", legacy: str = "i2p_dht_lab.providerpoison") -> ProviderMigrationPlan:
    audit = audit_provider_surfaces(canonical=canonical, legacy=legacy)
    imports = find_provider_legacy_imports(root, legacy_module=legacy)
    active_imports = tuple(item for item in imports if not item.historical)
    wrapper_ready = audit.has_overlap and len(active_imports) == 0 and not audit.legacy_only_names
    if active_imports:
        recommendation = "migrate_active_legacy_callers_before_wrapper"
    elif imports:
        recommendation = "historical_imports_only_preserve_until_compat_surface"
    elif audit.legacy_only_names:
        recommendation = "preserve_legacy_names_or_add_adapters_before_wrapper"
    else:
        recommendation = "legacy_can_be_compat_wrapper"
    return ProviderMigrationPlan(audit, imports, wrapper_ready, recommendation)
