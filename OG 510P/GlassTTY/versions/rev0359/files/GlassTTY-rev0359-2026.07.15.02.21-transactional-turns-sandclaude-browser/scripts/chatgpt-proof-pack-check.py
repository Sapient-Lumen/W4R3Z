#!/usr/bin/env python3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from chatgpt_proof_pack_check import main

if __name__ == '__main__':
    raise SystemExit(main())
