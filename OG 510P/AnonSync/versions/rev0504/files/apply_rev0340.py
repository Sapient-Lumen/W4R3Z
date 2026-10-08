#!/usr/bin/env python3
from pathlib import Path

def main() -> None:
    root = Path(__file__).resolve().parent
    print("rev0340 is a documentation revision. Files are already materialized under:", root)
    print("New tranche: 1180-1185 plus spine-doc updates.")

if __name__ == "__main__":
    main()
