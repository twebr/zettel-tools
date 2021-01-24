"""
Checks integrity of a zettelkasten library at the specified path.
To see documentation, run `$ python check_integrity.py --help`

Loosely based on https://github.com/crelder/zettelkasten
"""

import argparse
import re
from pathlib import Path
from typing import List, Tuple

from util import list_duplicates, get_note_paths, get_id_from_path


def get_ids_with_incorrect_format(note_paths: List[Path], id_pattern: str) -> List[Tuple[str, Path]]:
    """Check if IDs have the correct format"""

    zettel_ids = [get_id_from_path(path) for path in note_paths]

    return [(zettel_id, note_paths[loc])
            for loc, zettel_id in enumerate(zettel_ids)
            if not re.match(id_pattern, zettel_id)]


def get_duplicate_ids(note_paths: List[Path], id_pattern: str) -> List[Tuple[str, List[Path]]]:
    """Checks for duplicate IDs

    This method assumes the IDs are in the correct format.

    :return List of 2-tuples of the form (id, List[Path]) for each ID that
    occurs more than once
    """

    ids = [get_id_from_path(path) for path in note_paths if re.match(id_pattern, get_id_from_path(path))]

    duplicates = []
    for zettel_id, locs in sorted(list_duplicates(ids)):
        duplicates.append((zettel_id, [note_paths[loc] for loc in locs]))
    return duplicates


def get_broken_links(note_paths: List[Path], id_pattern: str) -> List[Tuple[str, Path]]:
    """Checks for broken links (links that do not point to an existing ID)

    Checks for the wikilink styles [[ZETTEL_ID]] and [[ZETTEL_ID Optional text]]
    """

    ids = [get_id_from_path(path) for path in note_paths]
    pattern = re.compile(r"\[{2}" + id_pattern + r"[^]\n]*]{2}")
    broken_links = []

    for path in note_paths:
        for match in pattern.finditer(path.read_text()):
            # print('Found {}'.format(match.group(1)))
            if match.group(1) not in ids:
                broken_links.append((match.group(1), path))

    return broken_links


def main():
    parser = argparse.ArgumentParser(description='Check integrity of a zettelkasten library')
    parser.add_argument('directory', type=Path, metavar='path',
                        help='directory of the zettelkasten library')
    parser.add_argument('--id-pattern', type=str, default=r'(\d{12})', metavar='regex',
                        help='regex to identify a zettel ID (default: (\\d{12}))')
    parser.add_argument('--extensions', type=str, nargs='+', default=['md', 'txt'], metavar='ext',
                        help='extensions to check (default: md, txt)')
    args = parser.parse_args()

    # Get note filenames
    note_paths = get_note_paths(args.directory, args.extensions)

    # Check if zettel IDs have the correct format
    incorrect_ids = get_ids_with_incorrect_format(note_paths, args.id_pattern)
    if incorrect_ids:
        print("The following IDs have a wrong format:")
        for zettel_id, path in incorrect_ids:
            print('- {}, for the file {}'.format(zettel_id, path))
    else:
        print("All IDs have the correct format.")
    print("-"*80)

    # Check for duplicate zettel IDs
    duplicate_ids = get_duplicate_ids(note_paths, args.id_pattern)
    if duplicate_ids:
        print("The following IDs are not unique:")
        for zettel_id, paths in duplicate_ids:
            print("- {}, for the files: ".format(zettel_id))
            for path in paths:
                print('    - {}'.format(path))
    else:
        print("All IDs are unique.")
    print("-"*80)

    # Check for broken links
    broken_links = get_broken_links(note_paths, args.id_pattern)
    if broken_links:
        print("Broken links:")
        for broken_link, path in broken_links:
            print("- {}, in the file {}".format(broken_link, path))
    else:
        print("All links point to an existing ID.")
    print("-" * 80)

    exit()


if __name__ == '__main__':
    main()
