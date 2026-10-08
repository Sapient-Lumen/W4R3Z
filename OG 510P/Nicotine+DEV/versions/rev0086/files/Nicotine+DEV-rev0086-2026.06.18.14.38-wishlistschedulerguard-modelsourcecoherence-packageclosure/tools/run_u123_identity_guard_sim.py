"""Run the U-123 fixed-behavior regression with an identity-aware deactivation monkeypatch.

This does not claim to be the final upstream patch. It only demonstrates that the
regression target is reachable with a narrow object-identity guard that prevents
an older Transfer timeout from deleting a newer active username+token mapping.
"""

from __future__ import annotations

import importlib.util
import pathlib
import sys
import unittest


def load_test_module(path: pathlib.Path):
    spec = importlib.util.spec_from_file_location("u123_fixed_regression", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def install_identity_guard():
    import pynicotine.transfers as transfers_mod

    def identity_checked_deactivate(self, transfer):
        username = transfer.username
        token = transfer.token

        if token is None:
            return False

        active_for_user = self.active_users.get(username, {})
        active_transfer = active_for_user.get(token)
        removed_active_slot = False

        if active_transfer is transfer:
            del active_for_user[token]
            if not active_for_user:
                del self.active_users[username]
            removed_active_slot = True
        elif active_transfer is not None:
            # The username+token slot belongs to a newer session. Leave it intact.
            pass
        else:
            # No active slot exists. Continue with transfer-local cleanup so stale
            # request timers/tokens are not left on the object being aborted.
            pass

        if transfer.speed > 0:
            self.total_bandwidth = max(0, self.total_bandwidth - transfer.speed)

        if transfer.request_timer_id is not None:
            transfers_mod.events.cancel_scheduled(transfer.request_timer_id)
            transfer.request_timer_id = None

        transfer.speed = transfer.avg_speed
        transfer.sock = None
        transfer.token = None
        return removed_active_slot

    transfers_mod.Transfers._deactivate_transfer = identity_checked_deactivate


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: run_u123_identity_guard_sim.py /path/to/test_downloads_duplicate_transfer_token_fixed_regression.py")
    test_module = load_test_module(pathlib.Path(sys.argv[1]))
    install_identity_guard()
    suite = unittest.defaultTestLoader.loadTestsFromModule(test_module)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    raise SystemExit(0 if result.wasSuccessful() else 1)


if __name__ == "__main__":
    main()
