"""
Adds a zettel ID from the filename to a specified property in the YAML frontmatter of the note.
"""

import argparse
from pathlib import Path

import frontmatter

from util import get_note_paths, has_zettel_id


def add_id_to_frontmatter(path: Path, property_name: str, zettel_id: str) -> frontmatter.Post:
    """Adds specified zettel ID to the existing frontmatter of a note.
    :param path: Path to the note.
    :param property_name: Name of the frontmatter property to write the zettel ID to.
    :param zettel_id: ID of the zettel that should be added to the frontmatter.
    :return: Frontmatter post object to which the zettel ID is added.
    """
    post = frontmatter.load(path)
    post[property_name] = zettel_id

    return post


def main():
    parser = argparse.ArgumentParser(description='Add zettel ID from the filename to the YAML frontmatter')
    parser.add_argument('input_directory', type=Path, metavar='path',
                        help='directory of the zettelkasten library')
    parser.add_argument('--id-pattern', type=str, default=r'(\d{12})', metavar='regex',
                        help='regex to identify a zettel ID (default: %(default)s)')
    parser.add_argument('--property-name', type=str, default='note_id',
                        help='Name of the frontmatter property to write the note ID to')
    parser.add_argument('--extensions', type=str, nargs='+', default=['md', 'txt'], metavar='ext',
                        help='extensions to check (default: md, txt)')
    parser.add_argument("--dry-run", action="store_true",
                        help="Perform a dry run without changing files on disk")
    args = parser.parse_args()

    if args.dry_run:
        print("Running in dry mode.\n")

    # Get note filenames
    note_paths = get_note_paths(args.input_directory, args.extensions)

    success_counter = 0
    skip_counter = 0
    for path in note_paths:
        if zettel_id := has_zettel_id(path, args.id_pattern):
            post = add_id_to_frontmatter(path, args.property_name, zettel_id)

            if not args.dry_run:
                # Write the modified file to disk (this overwrites the original file)
                frontmatter.dump(post, path)
            print(f"Added zettel ID '{zettel_id}' to '{path}'")
            success_counter += 1
        else:
            print(f"No zettel ID found for '{path}'")
            skip_counter += 1

    if success_counter == 0:
        print("No files to modify")
    else:
        print(f"\nAdded zettel IDs to the property '{args.property_name}' in {success_counter} files.")
        print(f"Skipped {skip_counter} files.")
        print(f"Processed {success_counter + skip_counter} files in total.")


if __name__ == '__main__':
    main()
