#!/usr/bin/env python3
import argparse
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_DIR = os.path.split(os.path.dirname(os.path.abspath(__file__)))[0]
VALIDATE_SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "validate.py")


def get_all_filenames(network):
    network_folder = os.path.join(BASE_DIR, network)
    filenames = sorted(os.listdir(network_folder))
    return [x for x in filenames if x.endswith(".json") and "validators" not in x]


def main():
    parser = argparse.ArgumentParser(description="Run validate.py on multiple validator files")
    parser.add_argument("--filenames", "-f", type=str, nargs="+")
    parser.add_argument("--network", "-n", type=str, default="mainnet")
    parser.add_argument("--verbose", "-v", action="store_true")
    parser.add_argument("--workers", "-w", type=int, default=10)
    args = parser.parse_args()
    network = args.network
    verbose = args.verbose
    workers = args.workers

    if args.filenames is None:
        filenames = get_all_filenames(network)
    else:
        filenames = args.filenames
        filenames = [f + ".json" if not f.endswith(".json") else f for f in filenames]

    problems = []

    def validate(filename):
        filepath = os.path.join(BASE_DIR, network, filename)
        result = subprocess.run(
            [sys.executable, VALIDATE_SCRIPT, filepath],
            capture_output=True,
            text=True,
        )
        return filename, result

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(validate, f): f for f in filenames}
        for future in as_completed(futures):
            filename, result = future.result()
            print(f"checking {filename}")
            if result.returncode != 0:
                problems.append(filename)
                print(result.stdout)
                if result.stderr:
                    print(result.stderr)
            elif verbose:
                print(result.stdout)

    if problems:
        raise Exception(f"❌ Validation failed for {len(problems)} files: {' '.join(problems)}")
    else:
        print("✅ Validation successful!")


if __name__ == "__main__":
    main()
