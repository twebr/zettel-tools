from collections import defaultdict
from pathlib import Path
from typing import List, Generator, Tuple


def list_duplicates(seq: List) -> Generator[Tuple, None, None]:
    """Helper function to list duplicates.

    See https://stackoverflow.com/a/5419576
    """

    tally = defaultdict(list)
    for idx, item in enumerate(seq):
        tally[item].append(idx)
    return ((key, locs) for key, locs in tally.items()
            if len(locs) > 1)


def get_note_paths(directory: str, extensions: List[str]) -> List[Path]:
    """Returns a list of all paths to notes in the given directory.
    Filters out results based on extension."""

    patterns = ['*.{}'.format(ext) for ext in extensions]
    note_paths = []
    for pattern in patterns:
        note_paths += Path(directory).rglob(pattern)

    remove_hidden_files(note_paths)

    return note_paths


def get_id_from_path(path: Path, separator: str = ' ') -> str:
    """Returns the zettel ID for a note path.

    This method assumes that IDs and note names are separated by a space.
    Optionally you can define a different separator"""

    return path.stem.split(separator)[0]


def line_prepender(path, lines):
    """Writes a lines to the start of the file at the specified path."""

    with path.open(mode='r+') as f:
        content = f.read()
        f.seek(0, 0)

        lines_flat = "\n".join(lines)

        f.write(lines_flat + '\n' + content)


def remove_hidden_files(paths: List[Path]):
    """Takes a list of paths, removes in-place the files that are hidden.

    Hidden means either:
    1. The file itself starts with a .
    2. The file is in a folder that starts with a .
    """

    # we need list() to iterate over a copy of the list; we cannot delete
    # elements from the list we are iterating over
    for path in list(paths):
        if any([part.startswith(".") for part in path.parts]):
            paths.remove(path)
