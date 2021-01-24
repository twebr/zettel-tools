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
    return note_paths


def get_id_from_path(path: Path, separator: str = ' ') -> str:
    """Returns the zettel ID for a note path.

    This method assumes that IDs and note names are separated by a space.
    Optionally you can define a different separator"""

    return path.stem.split(separator)[0]