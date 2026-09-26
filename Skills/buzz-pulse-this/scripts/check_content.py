#!/usr/bin/env python3
"""Pre-publish content checker for the buzz-pulse-this skill.

Runs the content-shape gate (and, with --card-1, the Card 1 field checks) on
the exact text that is about to be passed to `buzz social publish --content`,
after printing it between sentinels so the agent can confirm intent.

This script never publishes anything and never reads credentials. Content can
be passed with --content, read from a file with --file, or piped from stdin
with `--content -`; the stdin convention is safe here precisely because this
script is not the publish boundary.

Exit codes: 0 = safe to publish, 1 = rejected, 2 = usage error.
"""

import argparse
import re
import sys

CARD_1_FIELDS = (
    "Owner",
    "Asked",
    "Deliverable(s)",
    "Links",
    "Dates",
    "Current",
    "Waiting on",
)

DRIVE_OR_UNC_PATH = re.compile(r"^(?:\\\\|[A-Za-z]:[\\/])")


def shape_error(content):
    """The content-shape gate: reject the four malformed shapes outright."""
    stripped = content.strip()
    if stripped == "":
        return "content is empty or whitespace-only"
    if stripped == "-":
        return (
            "content is a bare '-' -- buzz social publish has no stdin "
            "convention, so the dash would be published literally as the "
            "whole note (the 2026-08-28 failure)"
        )
    if len(stripped) == 1 and not stripped.isalnum():
        return "content is a single punctuation character"
    return None


def card_1_errors(content):
    """Field checks for the Card 1 work-log template."""
    errors = []
    lines = [line.strip() for line in content.strip().splitlines()]
    for field in CARD_1_FIELDS:
        prefix = field + ":"
        if not any(line.startswith(prefix) for line in lines):
            errors.append("Card 1 missing field: " + field)
    if any(line.lower().startswith("last update") for line in lines):
        errors.append(
            "Card 1 must not carry a 'Last update' field -- each reply's "
            "relay timestamp supplies it"
        )
    links_line = next(
        (line for line in lines if line.startswith("Links:")), None
    )
    if links_line is not None:
        for token in links_line[len("Links:"):].split():
            token = token.strip(",;()[]")
            if token.startswith("/") or DRIVE_OR_UNC_PATH.match(token):
                errors.append(
                    "Card 1 Links value is an absolute path: " + token
                    + " -- use workspace-relative paths or URLs only"
                )
    return errors


def show(content, from_stdin_dash=False):
    print("=" * 20 + " CONTENT TO BE PUBLISHED " + "=" * 20)
    print(content)
    print("=" * 20 + " END CONTENT " + "=" * 28)
    print("Length: {} characters.".format(len(content)))
    if from_stdin_dash:
        print(
            "Reminder: content arrived via '--content -' reading stdin. "
            "buzz social publish has NO stdin convention -- publish this "
            "checked text as a literal or a shell variable, never as a "
            "bare '-' which would be published literally."
        )
    print(
        "Confirm this is the intended post before publishing. "
        "A Pulse note cannot be edited or deleted by anyone."
    )


def run_checks(content, card_1):
    problems = []
    error = shape_error(content)
    if error:
        problems.append(error)
    if card_1:
        problems.extend(card_1_errors(content))
    return problems


def self_test():
    """Deterministic acceptance matrix for the pre-publish check."""
    rejects = {
        "empty": "",
        "whitespace-only": "   \n\t  \n",
        "single punctuation (period)": ".",
        "bare dash": "-",
    }
    accepts = {
        "Card 0 sample": (
            "Investigated the relay latency spike. Root cause was a "
            "config reload, not load. Monitoring will confirm overnight."
        ),
        "Card 1 sample": (
            "Owner: Tunde (via Uzo)\n"
            "Asked: verify the backup schedule against the relay config\n"
            "Deliverable(s): in-chat answer\n"
            "Links: Archive/Live/Plans/Buzz/1.) Example.md\n"
            "Dates: Started 2026-09-11\n"
            "Current: in progress\n"
            "Waiting on: nobody"
        ),
    }
    failures = 0
    for label, sample in rejects.items():
        if shape_error(sample) is None:
            print("SELF-TEST FAIL: should reject but passed: " + label)
            failures += 1
        else:
            print("self-test: rejected as expected: " + label)
    for label, sample in accepts.items():
        problems = run_checks(sample, card_1=label.startswith("Card 1"))
        if problems:
            print("SELF-TEST FAIL: should accept but rejected: " + label)
            for problem in problems:
                print("  - " + problem)
            failures += 1
        else:
            print("self-test: accepted as expected: " + label)
    if failures:
        print("{} self-test failure(s).".format(failures))
        return 1
    print("Self-test passed: all four malformed shapes rejected, both well-formed samples accepted.")
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Pre-publish check for buzz social publish content."
    )
    parser.add_argument(
        "--content",
        help="the exact content about to be published; '-' reads stdin",
    )
    parser.add_argument(
        "--file",
        help="read the content from this file instead",
    )
    parser.add_argument(
        "--card-1",
        action="store_true",
        help="also run the Card 1 work-log field checks",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="run the deterministic acceptance matrix and exit",
    )
    args = parser.parse_args()

    if args.self_test:
        sys.exit(self_test())

    from_stdin_dash = args.content == "-"
    if args.file is not None:
        with open(args.file, "r", encoding="utf-8") as handle:
            content = handle.read()
    elif from_stdin_dash:
        content = sys.stdin.read()
    elif args.content is not None:
        content = args.content
    else:
        parser.error("provide --content, --content - (stdin), or --file")
        sys.exit(2)

    show(content, from_stdin_dash=from_stdin_dash)
    problems = run_checks(content, args.card_1)
    if problems:
        print("REJECTED -- do not publish. Fix and re-check:")
        for problem in problems:
            print("  - " + problem)
        sys.exit(1)
    print("PASS -- content passed the pre-publish check.")
    sys.exit(0)


if __name__ == "__main__":
    main()
