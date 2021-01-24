"""
Adds zettel IDs to files, based on their creation date.
Prevents the creation of duplicate IDs.

To see documentation, run `$ python add_zettel_ids.py --help`
"""

import argparse
import re
from pathlib import Path
from typing import Union, Optional
import datetime

from util import get_note_paths, get_id_from_path


def has_zettel_id(path: Path, id_pattern) -> Union[str, bool]:
    """Checks if a note already has a zettel ID.

    :return zettel ID if present; False otherwise
    """

    pattern = re.compile(id_pattern)
    match = pattern.match(get_id_from_path(path))
    if match is not None:
        return match.group()
    return False


def generate_zettel_id(path: Path, used_ids: set, id_pattern, id_format) -> Optional[str]:
    """Generates a zettel ID for a note

    :return generated zettel ID if the note did not have an ID already;
    None otherwise
    """

    # First check if note already has a zettel ID
    # If so, add it to the used IDs and terminate
    if has_zettel_id(path, id_pattern):
        used_ids.add(has_zettel_id(path, id_pattern))
        return

    # Extract creation time
    ctime = datetime.datetime.fromtimestamp(path.stat().st_birthtime)

    # Create zettel ID from creation time
    zettel_id = ctime.strftime(id_format)

    # If the zettel ID already exists, keep adding a minute to the creation
    # time until we found an unused ID
    while zettel_id in used_ids:
        ctime += datetime.timedelta(minutes=1)
        zettel_id = ctime.strftime(id_format)

    used_ids.add(zettel_id)
    return zettel_id


def add_id_to_note(path, zettel_id, dry_run=False):
    """Adds a zettel ID to a note.

    :param path: path to the note to which the zettel ID should be added
    :param zettel_id: the zettel ID to add to the note
    :param dry_run: if True, files on disk are not actually renamed

    :returns new path name

    """

    destination = path.with_stem('{} {}'.format(zettel_id, path.stem))

    if not destination.exists() and not dry_run:
        # print('normally I would now operate on disk')
        path.replace(destination)

    return destination


def main():
    parser = argparse.ArgumentParser(description='Add Zettel IDs to notes in a Zettelkasten library')
    parser.add_argument('directory', type=Path, metavar='path',
                        help='directory of the zettelkasten library')
    parser.add_argument('--id-format', type=str, default='%Y%m%d%H%M', metavar='format_code',
                        help='format code to generate a zettel ID (default: %(default)s)')
    parser.add_argument('--id-pattern', type=str, default=r'(\d{12})', metavar='regex',
                        help='regex to identify a zettel ID (default: %(default)s)')
    parser.add_argument('--extensions', type=str, nargs='+', default=['md', 'txt'], metavar='ext',
                        help='extensions to check (default: md, txt)')
    parser.add_argument('--dry-run', action='store_true', default=False,
                        help='do a dry run, without actually renaming files')
    args = parser.parse_args()

    # Get note filenames
    note_paths = get_note_paths(args.directory, args.extensions)

    if args.dry_run:
        print("Operating in dry run mode. Files are not actually renamed on disk.\n")

    used_ids = set()
    counter = 0
    for path in note_paths:
        generated_id = generate_zettel_id(path, used_ids, args.id_pattern, args.id_format)
        if generated_id is not None:
            destination = add_id_to_note(path, generated_id, args.dry_run)
            print("Renamed {} \n     to {}".format(path, destination))
            counter += 1

    if counter == 0:
        print("All files in '{}' with extensions {} have zettel IDs already.".format(args.directory, args.extensions))
    else:
        print("Renamed {} files.".format(counter))


if __name__ == '__main__':
    main()
