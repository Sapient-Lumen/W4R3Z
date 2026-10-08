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


class Options:
    """Option registry + global values.

    We keep this small and explicit. Buffer-local overrides are stored per
    EditorBuffer.
    """

    def __init__(self) -> None:
        self.specs: dict[str, OptionSpec] = {}
        self.values: dict[str, Any] = {}

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
        if local is not None and name in local:
            return local[name]
        if name in self.values:
            return self.values[name]
        raise KeyError(name)

    def set(self, name: str, raw: str, *, local: dict[str, Any] | None = None) -> Any:
        if name not in self.specs:
            raise KeyError(name)
        spec = self.specs[name]
        val = self._convert(spec, raw)
        if local is not None:
            local[name] = val
        else:
            self.values[name] = val
        return val

    def toggle(self, name: str, *, local: dict[str, Any] | None = None) -> Any:
        if name not in self.specs:
            raise KeyError(name)
        spec = self.specs[name]
        if spec.kind != "bool":
            raise TypeError("toggle only supports bool options")
        cur = bool(self.get(name, local=local))
        new = not cur
        if local is not None:
            local[name] = new
        else:
            self.values[name] = new
        return new

    def list_specs(self) -> list[OptionSpec]:
        return [self.specs[k] for k in sorted(self.specs.keys())]
