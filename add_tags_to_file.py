import argparse
from pathlib import Path

from util import get_note_paths, line_prepender


def add_tags(path, tags):
    """Adds specified tags to the start of the note."""

    # file = path.write_text()
    lines = ['---',
             'tags: [' + ', '.join(['{}'.format(tag) for tag in tags]) + ']',
             '---',
             '']

    print("Adding {} to file {}".format(lines, path))
    line_prepender(path, lines)


def main():
    parser = argparse.ArgumentParser(description='Add tags to file')
    parser.add_argument('directory', type=Path, metavar='path',
                        help='directory of the zettelkasten library')
    parser.add_argument('--tags', type=str, nargs='+', metavar='ext',
                        help='tags to add')
    parser.add_argument('--extensions', type=str, nargs='+', default=['md', 'txt'], metavar='ext',
                        help='extensions to check (default: md, txt)')
    args = parser.parse_args()

    # Get note filenames
    note_paths = get_note_paths(args.directory, args.extensions)

    counter = 0
    for path in note_paths:
        add_tags(path, args.tags)
        counter += 1

    if counter == 0:
        print("No files to modify")
    else:
        print("Added tags to {} files.".format(counter))


if __name__ == '__main__':
    main()
