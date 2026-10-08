#!/usr/bin/env python3
from __future__ import annotations

import os
from datetime import datetime, timezone


def generated_at_utc() -> str:
    """Return a reproducible generation timestamp when requested.

    Precedence:
    1. RG_GENERATED_AT_UTC or RG_GENERATED_AT: explicit ISO timestamp. A trailing Z is normalized to +00:00.
    2. SOURCE_DATE_EPOCH: standard reproducible-build epoch seconds.
    3. current UTC wall clock, microseconds stripped.

    Archive generators import the wrapper in ``archive_meta``; that wrapper
    uses the release timestamp by default and calls this function only for
    explicit overrides. Direct callers retain the wall-clock fallback.
    """
    explicit = os.environ.get("RG_GENERATED_AT_UTC", "").strip() or os.environ.get("RG_GENERATED_AT", "").strip()
    if explicit:
        if explicit.endswith("Z"):
            explicit = explicit[:-1] + "+00:00"
        dt = datetime.fromisoformat(explicit)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc).replace(microsecond=0).isoformat()

    epoch = os.environ.get("SOURCE_DATE_EPOCH", "").strip()
    if epoch:
        return datetime.fromtimestamp(int(epoch), tz=timezone.utc).replace(microsecond=0).isoformat()

    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
