from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class OptionSpec:
    name: str
    default: Any
    kind: str  # 'bool' | 'int' | 'str' | 'enum'
    enum: list[str] | None = None
    doc: str = ""
    alias_for: str | None = None


class Options:
    """Option registry + global values.

    We keep this small and explicit. Buffer-local overrides are stored per
    EditorBuffer.
    """

    def __init__(self) -> None:
        self.specs: dict[str, OptionSpec] = {}
        self.values: dict[str, Any] = {}
        self.aliases: dict[str, str] = {}

    def register(
        self,
        name: str,
        default: Any,
        *,
        kind: str,
        enum: list[str] | None = None,
        doc: str = "",
    ) -> None:
        self.specs[name] = OptionSpec(name=name, default=default, kind=kind, enum=enum, doc=doc)
        self.values.setdefault(name, default)

    def register_alias(self, alias: str, target: str, *, doc: str = "") -> None:
        target_name = self.resolve_name(target)
        if target_name not in self.specs:
            raise KeyError(target)
        spec = self.specs[target_name]
        self.aliases[alias] = target_name
        self.specs[alias] = OptionSpec(
            name=alias,
            default=spec.default,
            kind=spec.kind,
            enum=list(spec.enum) if spec.enum is not None else None,
            doc=doc or spec.doc,
            alias_for=target_name,
        )

    def resolve_name(self, name: str) -> str:
        seen: set[str] = set()
        cur = str(name)
        while cur in self.aliases and cur not in seen:
            seen.add(cur)
            cur = self.aliases[cur]
        return cur

    def spec(self, name: str) -> OptionSpec | None:
        return self.specs.get(str(name))

    def canonical_spec(self, name: str) -> OptionSpec | None:
        return self.specs.get(self.resolve_name(str(name)))

    def _convert(self, spec: OptionSpec, raw: str) -> Any:
        if spec.kind == "bool":
            v = raw.strip().lower()
            if v in ("1", "true", "on", "yes"):
                return True
            if v in ("0", "false", "off", "no"):
                return False
            raise ValueError(f"invalid bool: {raw}")
        if spec.kind == "int":
            return int(raw, 10)
        if spec.kind == "enum":
            v = str(raw).strip()
            if spec.enum and v not in spec.enum:
                raise ValueError(f"invalid {spec.name}: {v} (expected one of {spec.enum})")
            return v
        return str(raw)

    def get(self, name: str, *, local: dict[str, Any] | None = None) -> Any:
        key = self.resolve_name(str(name))
        if local is not None and key in local:
            return local[key]
        if key in self.values:
            return self.values[key]
        raise KeyError(name)

    def set(self, name: str, raw: str, *, local: dict[str, Any] | None = None) -> Any:
        alias_name = str(name)
        key = self.resolve_name(alias_name)
        spec = self.canonical_spec(alias_name)
        if spec is None:
            raise KeyError(name)
        val = self._convert(spec, raw)
        if local is not None:
            local[key] = val
        else:
            self.values[key] = val
        return val

    def toggle(self, name: str, *, local: dict[str, Any] | None = None) -> Any:
        alias_name = str(name)
        key = self.resolve_name(alias_name)
        spec = self.canonical_spec(alias_name)
        if spec is None:
            raise KeyError(name)
        if spec.kind != "bool":
            raise TypeError("toggle only supports bool options")
        cur = bool(self.get(alias_name, local=local))
        new = not cur
        if local is not None:
            local[key] = new
        else:
            self.values[key] = new
        return new

    def aliases_for(self, name: str) -> list[str]:
        target = self.resolve_name(str(name))
        return sorted(
            [alias for alias, resolved in self.aliases.items() if str(resolved) == target],
        )

    def list_specs(self, *, include_aliases: bool = False) -> list[OptionSpec]:
        if include_aliases:
            keys = sorted(self.specs.keys())
        else:
            keys = sorted([k for k, spec in self.specs.items() if spec.alias_for is None])
        return [self.specs[k] for k in keys]
