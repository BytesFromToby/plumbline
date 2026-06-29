"""Command-line entry point for mdtoc.

``python -m mdtoc <file>`` prints the generated TOC to stdout. With
``--insert`` the TOC is written back into the file (wired in Slice 5).
"""
import argparse
import sys

from mdtoc.core import extract_headings, insert_toc, render_toc


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="mdtoc",
        description="Generate a table of contents from a Markdown file's headings.",
    )
    parser.add_argument("file", help="path to the Markdown file")
    parser.add_argument(
        "--insert",
        action="store_true",
        help="write the TOC back into the file between marker comments",
    )
    args = parser.parse_args()

    try:
        with open(args.file, encoding="utf-8") as f:
            text = f.read()
    except OSError as exc:
        print(f"mdtoc: cannot read {args.file}: {exc}", file=sys.stderr)
        return 1

    toc = render_toc(extract_headings(text))

    if args.insert:
        new_text = insert_toc(text, toc)
        try:
            with open(args.file, "w", encoding="utf-8") as f:
                f.write(new_text)
        except OSError as exc:
            print(f"mdtoc: cannot write {args.file}: {exc}", file=sys.stderr)
            return 1
        return 0

    sys.stdout.write(toc)
    return 0


if __name__ == "__main__":
    sys.exit(main())
