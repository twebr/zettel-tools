"""
Adds a zettel ID from the filename to the YAML frontmatter of the note.
"""

import argparse
from pathlib import Path

import frontmatter

from util import get_note_paths, get_id_from_path


def get_id_from_filename(path: Path) -> str:
    """Gets ID from filenname. Returns False if none found."""

    zettel_id = get_id_from_path(path)
    return zettel_id


def add_id_to_frontmatter(path: Path, zettel_id: str) -> frontmatter.Post:
    """Adds specified zettel ID to the existing frontmatter of a note."""

    post = frontmatter.load(path)
    post['id'] = zettel_id

    return post

    # print("Adding {} to file {}".format(lines, path))
    # line_prepender(path, lines)


def main():
    parser = argparse.ArgumentParser(description='Add zettel ID from the filename to the YAML frontmatter')
    parser.add_argument('input_directory', type=Path, metavar='path',
                        help='directory of the zettelkasten library')
    # parser.add_argument('output_directory', type=Path, metavar='path',
    #                     help='directory to write the result to')
    # parser.add_argument('--tags', type=str, nargs='+', metavar='ext',
    #                     help='tags to add')
    parser.add_argument('--extensions', type=str, nargs='+', default=['md', 'txt'], metavar='ext',
                        help='extensions to check (default: md, txt)')
    args = parser.parse_args()

    # Get note filenames
    note_paths = get_note_paths(args.input_directory, args.extensions)

    counter = 0
    for path in note_paths:
        zettel_id = get_id_from_filename(path)
        post = add_id_to_frontmatter(path, zettel_id)

        frontmatter.dump(post, path)
        # with path.open(mode='w') as f:
        #     frontmatter.dump(post, f)

        counter += 1

    if counter == 0:
        print("No files to modify")
    else:
        print("Added tags to {} files.".format(counter))


if __name__ == '__main__':
    main()
