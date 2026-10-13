#!/usr/bin/env python3
"""CLI wrapper for validating sources.yaml.

Usage:
    python validate_sources.py [path/to/sources.yaml]
"""
import sys
from aoia.registry import validate_registry_file

def main():
    target = sys.argv[1] if len(sys.argv) > 1 else "configs/sources.yaml"
    errs = validate_registry_file(target)
    if errs:
        print(f"Validation failed with {len(errs)} error(s):")
        for e in errs:
            print(f"  - {e}")
        sys.exit(1)
    print("Validation passed (0 errors).")
    sys.exit(0)

if __name__ == "__main__":
    main()
