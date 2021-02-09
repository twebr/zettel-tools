import argparse
from pathlib import Path

from util import get_note_paths, line_prepender


def add_title(path):
    """Adds title (based on filename) to the start of the note."""

    title = path.stem
    lines = ['# {}'.format(title)]

    print("Adding {} to file {}".format(lines, path))
    line_prepender(path, lines)


def main():
    parser = argparse.ArgumentParser(description='Add markdown title to file based on filename')
    parser.add_argument('directory', type=Path, metavar='path',
                        help='directory of the zettelkasten library')
    parser.add_argument('--extensions', type=str, nargs='+', default=['md', 'txt'], metavar='ext',
                        help='extensions to check (default: md, txt)')
    args = parser.parse_args()

    # Get note filenames
    note_paths = get_note_paths(args.directory, args.extensions)

    counter = 0
    for path in note_paths:
        add_title(path)
        counter += 1

    if counter == 0:
        print("No files to modify")
    else:
        print("Added titles to {} files.".format(counter))


if __name__ == '__main__':
    main()
