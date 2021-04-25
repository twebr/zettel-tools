# zettel-tools

A collection of Python scripts to manage a Zettelkasten library.

Tested with Python 3.9 on macOS 10.14.


## `add_tags_to_file.py`

Adds tags to the top of a note with the following formatting:

```
---
tags: [tag1, tag2]
---

rest of the file
```

Documentation:
```
usage: add_tags_to_file.py [-h] [--tags ext [ext ...]] [--extensions ext [ext ...]] path

Add tags to file

positional arguments:
  path                  directory of the zettelkasten library

optional arguments:
  -h, --help            show this help message and exit
  --tags ext [ext ...]  tags to add
  --extensions ext [ext ...]
                        extensions to check (default: md, txt)

```


## `add_title_to_file.py`

Adds title (based on filename) to the start of the note. Documentation:

```
usage: add_title_to_file.py [-h] [--extensions ext [ext ...]] path

Add markdown title to file based on filename

positional arguments:
  path                  directory of the zettelkasten library

optional arguments:
  -h, --help            show this help message and exit
  --extensions ext [ext ...]
                        extensions to check (default: md, txt)

```


## `add_zettel_ids.py`

Create Zettel IDs for a Zettelkasten library at the specified location. You can specify your own format code for generating the IDs, based on the file creation date. The script prevents the generation of duplicate IDs, and also checks if notes already have a valid ID (if so, these notes are skipped).

Documentation:

```
usage: add_zettel_ids.py [-h] [--id-format format_code] [--id-pattern regex] [--extensions ext [ext ...]] [--dry-run] path

Add Zettel IDs to notes in a Zettelkasten library

positional arguments:
  path                  directory of the zettelkasten library

optional arguments:
  -h, --help            show this help message and exit
  --id-format format_code
                        format code to generate a zettel ID (default: %Y%m%d%H%M)
  --id-pattern regex    regex to identify a zettel ID (default: (\d{12}))
  --extensions ext [ext ...]
                        extensions to check (default: md, txt)
  --dry-run             do a dry run, without actually renaming files

```


## `check_integrity.py`

Checks the integrity of a Zettelkasten library at the specified location. It checks for three things:

- Ill-formatted Zettel IDs
- Duplicate Zettel IDs
- Broken links between notes (assuming [[wikilinks]] style links)

Documentation:

```
usage: check_integrity.py [-h] [--id-pattern regex] [--extensions ext [ext ...]] path

Check integrity of a Zettelkasten library

positional arguments:
  path                  directory of the zettelkasten library

optional arguments:
  -h, --help            show this help message and exit
  --id-pattern regex    regex to identify a zettel ID (default: (\d{12}))
  --extensions ext [ext ...]
                        extensions to check (default: md, txt)


```

Sample output:

```
The following IDs have a wrong format:
- 20201016123, for the file data/small-testset/subfolder1/20201016123 abiogenetic nutlet.md
- 4definitey, for the file data/small-testset/4definitey abkhazian opcw.txt
--------------------------------------------------------------------------------
The following IDs are not unique:
- 202001011234, for the files: 
    - data/small-testset/202001011234 abducent common racoon.md
    - data/small-testset/subfolder1/202010161231 aberrant suspiciousness.md
- 202010161231, for the files: 
    - data/small-testset/subfolder1/20201016123 abiogenetic nutlet.md
    - data/small-testset/subfolder1/202010161231 aberrant xeranthemum annuum.md
--------------------------------------------------------------------------------
Broken links:
- 123456789012, in the file data/small-testset/202001011235 abducent port moresby.md
- 123456789012, in the file data/small-testset/202001011235 abducent port moresby.md
--------------------------------------------------------------------------------
```


## `stupefy_typography.py`

Reverses the smart typography applied by tools such as SmartyPants or smart quotes in MS Word. Documentation:

```
usage: stupefy_typography.py [-h] [--extensions ext [ext ...]] [--dry-run] path

Reverses the smart typography applied by tools such as SmartyPants or smart quotes in MS Word. TAKE CARE! The transformation is done in-place. This script reads the files and converts the
following: - curly quotes to straight quotes - em dashes to --- - en dashes to -- - ellipsis to ... To see documentation, run `$ python stupefy_typography.py --help`

positional arguments:
  path                  directory of the zettelkasten library

optional arguments:
  -h, --help            show this help message and exit
  --extensions ext [ext ...]
                        extensions to check (default: md, txt)
  --dry-run             Perform a dry run without changing files on disk

```


## Known limitations

- `add_zettel_ids.py`: While you can supply your own format code for generating Zettel IDs, the system for resolving duplicate IDs always increments the ID with 1 minute. If you choose a higher granularity (e.g. seconds), this may create larger gaps in Zettel IDs than strictly needed. If you choose a lower granularity (e.g. hours), the script may slow down because it will do many redundant checks.
- `add_zettel_ids.py`: This script does not check for duplicates in existing Zettel IDs, so the result is not guaranteed to be duplicate-free. To check integrity, you can of course use `check_integrity.py`.