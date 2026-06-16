#!/usr/bin/env python3
import argparse
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_DIR = os.path.split(os.path.dirname(os.path.abspath(__file__)))[0]
VALIDATE_SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "validate.py")
NETWORKS = ("mainnet", "testnet")

_COLOR = (sys.stdout.isatty() or bool(os.environ.get("GITHUB_ACTIONS"))) and not os.environ.get("NO_COLOR")

def _c(code):
    return code if _COLOR else ""

RESET   = _c("\033[0m")
BOLD    = _c("\033[1m")
DIM     = _c("\033[2m")
# Monad brand palette (24-bit)
PURPLE  = _c("\033[38;2;110;84;255m")    # #6E54FF — primary
LPURPLE = _c("\033[38;2;221;215;254m")   # #DDD7FE — light purple
CYAN    = _c("\033[38;2;133;230;255m")   # #85E6FF
PINK    = _c("\033[38;2;255;142;228m")   # #FF8EE4
ORANGE  = _c("\033[38;2;255;174;69m")    # #FFAE45
WHITE   = _c("\033[97m")


def get_all_files(network):
    folder = os.path.join(BASE_DIR, network)
    return [
        (network, f, os.path.join(folder, f))
        for f in sorted(os.listdir(folder))
        if f.endswith(".json") and "validators" not in f
    ]


def resolve_files(args):
    if args.paths:
        files = []
        for path in args.paths:
            parts = path.replace("\\", "/").strip("/").split("/")
            network = next((p for p in parts if p in NETWORKS), None)
            if not network:
                print(f"{ORANGE}⚠  Cannot determine network from path: {path}{RESET}", file=sys.stderr)
                continue
            filename = parts[-1]
            if not filename.endswith(".json"):
                filename += ".json"
            files.append((network, filename, os.path.join(BASE_DIR, network, filename)))
        return files

    if args.network:
        return get_all_files(args.network)
    return get_all_files("mainnet") + get_all_files("testnet")


def main():
    parser = argparse.ArgumentParser(description="Run validate.py on multiple validator files")
    parser.add_argument("paths", nargs="*", help="Full paths like mainnet/foo.json or testnet/bar.json")
    parser.add_argument("--network", "-n", type=str, default=None, choices=["mainnet", "testnet"])
    parser.add_argument("--verbose", "-v", action="store_true")
    parser.add_argument("--workers", "-w", type=int, default=20)
    args = parser.parse_args()

    files = resolve_files(args)
    total = len(files)

    counts = {}
    for network, _, _ in files:
        counts[network] = counts.get(network, 0) + 1

    sep = f"{PURPLE}{'─' * 48}{RESET}"
    print(f"\n{sep}")
    print(f"  {BOLD}{WHITE}◆ monad{RESET}  {DIM}validator check{RESET}")
    print(sep)
    for network, count in sorted(counts.items()):
        dot = "◆" if _COLOR else "-"
        dot_color = PURPLE if network == "mainnet" else CYAN
        print(f"  {dot_color}{dot}{RESET}  {WHITE}{network:<12}{RESET}{LPURPLE}{count} validators{RESET}")
    print(f"  {DIM}{'─' * 28}{RESET}")
    print(f"  {'':>3}{DIM}total        {RESET}{BOLD}{WHITE}{total}{RESET}")
    print(f"{sep}\n")

    failures = []

    def validate(network, filename, filepath):
        result = subprocess.run(
            [sys.executable, VALIDATE_SCRIPT, filepath],
            capture_output=True,
            text=True,
        )
        return network, filename, result

    done = 0
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {executor.submit(validate, *f): f for f in files}
        for future in as_completed(futures):
            network, filename, result = future.result()
            done += 1
            pct = int(done / total * 100)
            bar = int(pct / 5)
            if _COLOR:
                bar_str = f"{PURPLE}{'█' * bar}{DIM}{'░' * (20 - bar)}{RESET}"
            else:
                bar_str = f"[{'#' * bar}{' ' * (20 - bar)}]"
            if result.returncode != 0:
                status = f"{PINK}✗{RESET}"
                label = f"{PINK}{network}/{filename}{RESET}"
                failures.append((network, filename, result))
            else:
                status = f"{CYAN}✓{RESET}"
                label = f"{DIM}{network}/{filename}{RESET}"
            print(f"  {bar_str} {DIM}{pct:3d}%{RESET}  {status}  {label}")
            if result.returncode == 0 and args.verbose:
                print(result.stdout)

    print()
    if failures:
        print(f"{PINK}{'─' * 48}{RESET}")
        print(f"  {BOLD}{PINK}✗  {len(failures)} file(s) failed{RESET}")
        print(f"{PINK}{'─' * 48}{RESET}\n")
        for network, filename, result in failures:
            print(f"  {BOLD}{WHITE}{network}/{filename}{RESET}")
            print(f"{DIM}{'─' * 40}{RESET}")
            print(result.stdout)
            if result.stderr:
                print(f"{ORANGE}{result.stderr}{RESET}")
        sys.exit(1)
    else:
        print(f"  {BOLD}{CYAN}✓  All {total} validators passed!{RESET}\n")


if __name__ == "__main__":
    main()
