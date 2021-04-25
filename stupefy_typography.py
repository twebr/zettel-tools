"""
Reverses the smart typography applied by tools such as SmartyPants or
smart quotes in MS Word.

TAKE CARE! The transformation is done in-place.

This script reads the files and converts the following:
- curly quotes to straight quotes
- em dashes to ---
- en dashes to --
- ellipsis to ...

To see documentation, run `$ python stupefy_typography.py --help`
"""

import argparse
from pathlib import Path

from util import get_note_paths

replacements = {
    "“": '"',
    "”": '"',
    "‘": "'",
    "’": "'",
    "–": "--",
    "—": "---",
    "…": "..."
}


def stupefy_typography(path: Path, dry_run: bool) -> bool:
    """Adds title (based on filename) to the start of the note.

    :return True if changes were made, False otherwise
    """

    # Read in the file
    with open(path, "r") as file:
        contents = file.read()

    # Replace the target string
    new_contents = replace_all(contents, replacements)

    # Check if there were changes; if none, return
    if contents == new_contents:
        print("No changes needed to file {}".format(path))
        return False

    # print(new_contents)

    # Write the file out again
    print("Stupefying file {}".format(path))
    if not dry_run:
        with open(path, "w") as file:
            file.write(new_contents)

    return True


def replace_all(text: str, text_replacements: dict) -> str:
    for old, new in text_replacements.items():
        text = text.replace(old, new)
    return text


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path, metavar="path",
                        help="directory of the zettelkasten library")
    parser.add_argument("--extensions", type=str, nargs="+", default=["md", "txt"], metavar="ext",
                        help="extensions to check (default: md, txt)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Perform a dry run without changing files on disk")
    args = parser.parse_args()

    if args.dry_run:
        print("Running in dry mode.\n")

    # Get note filenames
    note_paths = get_note_paths(args.directory, args.extensions)

    counter = 0
    for path in note_paths:
        if stupefy_typography(path, args.dry_run):
            counter += 1

    if counter == 0:
        print("No files to modify")
    else:
        print("\nStupefied typography in {} files.".format(counter))


if __name__ == '__main__':
    main()
