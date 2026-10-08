#!/usr/bin/env python3
"""Execute wishlist scheduler scenarios against a supplied Nicotine+ source tree."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from unittest.mock import patch


def build(search_cls, request_cls, items):
    instance = search_cls.__new__(search_cls)
    instance.wishlist = {}
    for token, (term, enabled) in enumerate(items, start=1):
        instance.wishlist[term] = request_cls(
            token=token,
            term=term,
            term_sanitized=term,
            term_transmitted=term,
            included_words=[term],
            excluded_words=[],
            auto_search=enabled,
        )
    return instance


def run_scenario(search_cls, request_cls, items, ticks):
    instance = build(search_cls, request_cls, items)
    selected = []
    with patch.object(search_cls, "_do_wishlist_search", autospec=True) as sender:
        for _ in range(ticks):
            before = sender.call_count
            search_cls._do_next_wishlist_search(instance)
            if sender.call_count == before:
                selected.append(None)
            else:
                selected.append(sender.call_args.args[1].term)
    return {
        "selected": selected,
        "order": list(instance.wishlist),
        "ignored": {term: wish.is_ignored for term, wish in instance.wishlist.items()},
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", required=True)
    args = parser.parse_args()
    source_root = Path(args.source_root).resolve()
    sys.path.insert(0, str(source_root))
    from pynicotine.search import Search, WishSearchRequest

    scenarios = {
        "empty": ([], 1),
        "single_disabled": ([("disabled", False)], 1),
        "all_disabled": ([("a", False), ("b", False), ("c", False)], 4),
        "disabled_then_enabled": ([("off-a", False), ("on-b", True)], 2),
        "enabled_then_disabled": ([("on-a", True), ("off-b", False)], 2),
        "all_enabled": ([("a", True), ("b", True), ("c", True)], 6),
        "mixed": ([("off-a", False), ("on-b", True), ("off-c", False), ("on-d", True)], 4),
    }
    result = {
        name: run_scenario(Search, WishSearchRequest, items, ticks)
        for name, (items, ticks) in scenarios.items()
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
