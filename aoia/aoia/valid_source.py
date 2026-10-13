"""Registry validation module matching validate_sources.py."""
import sys
from .registry import validate_registry_file

def main(p="configs/sources.yaml"):
    errs = validate_registry_file(p)
    if errs:
        print(f"errors={len(errs)}")
        for e in errs:
            print(" -", e)
        return 1
    print("sources valid, 0 errors")
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "configs/sources.yaml"))