#!/usr/bin/env python3
import os, sys
import subprocess
import argparse
import re
from packaging import version

TEST_DIR = 'test'

MAUDE_MIN_VERSION = '2.7.1'
MAUDE = 'maude.linux64'
MAUDE_EXT = '.maude'
MAUDE_FLAGS = ['-no-advise', '-no-banner']

EXPECTED_RESULT = 'Bool: true'

SEP = '=' * 50

def print_color(color, *args):
    print(f"\033[{color}m", end='', flush=False)
    print(*args, end='', flush=False)
    print("\033[00m")

def print_warn(*args): print_color(93, *args)
def print_warn_bg(*args): print_color(43, *args)
def print_err(*args): print_color(31, *args)
def print_err_bg(*args): print_color(41, *args)
def print_ok(*args): print_color(32, *args)
def print_ok_bg(*args): print_color(42, *args)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', help="name of the test file in ./test/ (without extension)")
    parser.add_argument('--verbose', action='store_true')
    args = parser.parse_args()

    # Check version
    actual_version = subprocess.check_output([MAUDE, '--version']).decode().strip()
    if version.parse(actual_version) < version.Version(MAUDE_MIN_VERSION):
        print_err(f"Maude version {actual_version} is too low (expected {MAUDE_MIN_VERSION}).")
        sys.exit(1)

    files = [args.name + MAUDE_EXT] if args.name else os.listdir(TEST_DIR)

    for file in files:
        parse_error = False

        _, ext = os.path.splitext(file)
        if ext != MAUDE_EXT:
            continue

        path = os.path.join(TEST_DIR, file)

        # Invoke Maude on the file and get output
        cmd = [MAUDE] + MAUDE_FLAGS + [path]
        p = subprocess.Popen(cmd,
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        out_raw, err_raw = p.communicate(b"quit\n")
        out = out_raw.decode()
        err = err_raw.decode()

        # Parse unit tests (i.e., reduce and rewrite commands)
        command_matches = re.findall(r'^(reduce|rewrite) in .*: (\w+)', out, flags=re.MULTILINE)
        n_commands = len(command_matches)
        name_matches = [ name for (_, name) in command_matches ]
        names_unique = [
            f"{name}[{name_matches[:i].count(name)}]"
            for i, name in enumerate(name_matches)
        ] # elegant way to number tests that have the same name

        # Parse results
        res_matches = re.findall(r'^result (.+)', out, flags=re.MULTILINE)
        n_results = len(res_matches)
        n_tests_ok = res_matches.count(EXPECTED_RESULT)
        n_tests_failed = n_results - n_tests_ok

        if n_commands == 0 or n_commands != n_results:
            parse_error = True

        # Parse warnings
        warnings = re.findall(r'^Warning: ([^:]*):', err, flags=re.MULTILINE)

        # Print warnings and other information
        print(SEP)
        print(f"TESTS FOR {file}:")

        if args.verbose:
            print('$', ' '.join(cmd))
            print_warn(err)
            print(out)
        else:
            print_warn(err)

        # Print results
        for name, res in zip(names_unique, res_matches):
            print(name + ":", end=' ', flush=False)
            if res == EXPECTED_RESULT:
                print_ok_bg("passed")
            else:
                print_err_bg("failed")

        print(f"\nSUMMARY FOR {file}:")
        summary = f"{n_tests_ok} passed, {n_tests_failed} failed"
        if n_tests_failed == 0:
            print_ok_bg(summary)
        else:
            print_err_bg(summary)
        if warnings:
            print_warn_bg(len(warnings), "warning(s)")
        if parse_error:
            print_err_bg(f"Parse error: {n_commands} tests, {n_results} results")
        print(SEP)

    print("Use the --verbose flag to see the full output.")

if __name__ == "__main__":
    main()
