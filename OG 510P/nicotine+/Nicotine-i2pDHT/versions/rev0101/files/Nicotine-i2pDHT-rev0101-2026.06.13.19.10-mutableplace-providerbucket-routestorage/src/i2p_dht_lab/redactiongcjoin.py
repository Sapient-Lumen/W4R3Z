"""rev0075 compatibility wrapper for the earlier redaction-GC-join branchlet.

The active folded surface is :mod:`i2p_dht_lab.redactiongc`.  This module keeps
historical branchlet imports readable during audit/surface-clean sweeps without
creating a second active protocol authority.
"""
from __future__ import annotations

from .redactiongc import *  # noqa: F401,F403
