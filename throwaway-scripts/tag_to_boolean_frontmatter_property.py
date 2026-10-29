#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "ruamel.yaml>=0.18,<1",
# ]
# ///

"""Set a boolean frontmatter property based on tag presence in an Obsidian vault."""

from __future__ import annotations

import argparse
import io
import re
import shutil
import sys
import tempfile
import warnings
from pathlib import Path

from ruamel.yaml import YAML
from ruamel.yaml.error import YAMLError


FENCE_RE = re.compile(r"^\s{0,3}(`{3,}|~{3,})")


def normalize_tag(tag: str) -> str:
    tag = tag.strip()
    if tag.startswith("#"):
        tag = tag[1:]
    if not tag or any(c.isspace() for c in tag):
        raise argparse.ArgumentTypeError(
            "Tag must be a single tag name, optionally prefixed with '#'."
        )
    return tag


def remove_inline_code(line: str) -> str:
    """Mask inline code spans before searching for tags."""
    result = list(line)
    i = 0

    while i < len(line):
        if line[i] != "`":
            i += 1
            continue

        j = i
        while j < len(line) and line[j] == "`":
            j += 1

        marker = line[i:j]
        end = line.find(marker, j)

        if end == -1:
            i = j
            continue

        for k in range(i, end + len(marker)):
            if result[k] not in "\r\n":
                result[k] = " "

        i = end + len(marker)

    return "".join(result)


def tag_pattern(tag: str) -> re.Pattern[str]:
    return re.compile(rf"(?<![\w/#-])#{re.escape(tag)}(?![\w/-])")


def remove_body_tags(body: str, tag: str) -> tuple[str, bool]:
    """Remove matching tags from Markdown, excluding code blocks."""
    pattern = tag_pattern(tag)
    output = []
    changed = False
    in_fence = None

    for line in body.splitlines(keepends=True):
        fence_match = FENCE_RE.match(line)

        if in_fence is not None:
            output.append(line)
            if fence_match:
                marker = fence_match.group(1)
                if marker[0] == in_fence[0] and len(marker) >= len(in_fence):
                    in_fence = None
            continue

        if fence_match:
            in_fence = fence_match.group(1)
            output.append(line)
            continue

        ending = ""
        content = line

        if content.endswith("\r\n"):
            content, ending = content[:-2], "\r\n"
        elif content.endswith(("\n", "\r")):
            content, ending = content[:-1], content[-1]

        searchable = remove_inline_code(content)
        matches = list(pattern.finditer(searchable))

        if not matches:
            output.append(line)
            continue

        for match in reversed(matches):
            start, end = match.span()
            content = content[:start] + content[end:]

        content = re.sub(r"[ \t]{2,}", " ", content)
        content = re.sub(r"[ \t]+$", "", content)
        output.append(content + ending)
        changed = True

    return "".join(output), changed


def split_frontmatter(text: str) -> tuple[str | None, str]:
    lines = text.splitlines(keepends=True)

    if not lines or lines[0].strip() != "---":
        return None, text

    for i in range(1, len(lines)):
        if lines[i].strip() in ("---", "..."):
            return "".join(lines[1:i]), "".join(lines[i + 1:])

    return None, text


def is_target_tag(value: object, tag: str) -> bool:
    return (
        isinstance(value, str)
        and value.strip().removeprefix("#") == tag
    )


def remove_frontmatter_tag(metadata: dict, tag: str) -> bool:
    """Remove the target from YAML tags while retaining other tags."""
    tags = metadata.get("tags")

    if isinstance(tags, list):
        cleaned = [item for item in tags if not is_target_tag(item, tag)]
        changed = len(cleaned) != len(tags)

        if changed:
            if cleaned:
                metadata["tags"] = cleaned
            else:
                del metadata["tags"]

        return changed

    if is_target_tag(tags, tag):
        del metadata["tags"]
        return True

    return False


def transform_note(
    text: str,
    yaml: YAML,
    tag: str,
    path: Path,
    legacy_status: bool = False,
) -> tuple[str, bool, bool]:
    """Set the tag-named property to true or false on every note."""
    frontmatter, body = split_frontmatter(text)
    has_frontmatter = frontmatter is not None
    metadata = {}

    if has_frontmatter:
        try:
            loaded = yaml.load(frontmatter)
        except YAMLError as exc:
            raise ValueError(f"Invalid YAML frontmatter: {exc}") from exc

        if loaded is None:
            metadata = {}
        elif isinstance(loaded, dict):
            metadata = loaded
        else:
            raise ValueError("Frontmatter must contain a YAML mapping.")

    # Check tag presence before removing it.
    tags = metadata.get("tags")
    frontmatter_has_tag = (
        any(is_target_tag(item, tag) for item in tags)
        if isinstance(tags, list)
        else is_target_tag(tags, tag)
    )

    new_body, body_has_tag = remove_body_tags(body, tag)
    legacy_match = (
            legacy_status
            and re.search(
        r"(?im)^[ \t]*Status::[ \t]*watched[ \t]*$",
        body,
    ) is not None
    )

    tag_present = frontmatter_has_tag or body_has_tag or legacy_match

    # Warn if the property already exists, even if its value is unchanged.
    if has_frontmatter and tag in metadata:
        warnings.warn(
            f"{path}: frontmatter already contains property "
            f"{tag!r}; overwriting it.",
            UserWarning,
            stacklevel=2,
        )

    # Remove the tag from YAML tags and the Markdown body.
    if has_frontmatter:
        remove_frontmatter_tag(metadata, tag)

    metadata[tag] = tag_present

    buffer = io.StringIO()
    yaml.dump(metadata, buffer)
    new_frontmatter = buffer.getvalue().rstrip("\r\n")

    newline = "\r\n" if "\r\n" in text else "\n"
    result = (
        "---" + newline
        + new_frontmatter + newline
        + "---" + newline
        + new_body
    )

    return result, result != text, tag_present


def process_vault(
    vault: Path, tag: str, dry_run: bool, legacy_status: bool = False
) -> int:
    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.allow_unicode = True

    updated = 0
    unchanged = 0
    errors = 0

    for path in sorted(vault.rglob("*.md")):
        relative = path.relative_to(vault)

        # Ignore hidden directories/notes at any depth.
        if any((part.startswith(".") or part.startswith("_")) for part in relative.parts):
            continue

        if path.is_symlink():
            continue

        try:
            original = path.read_bytes()
            has_bom = original.startswith(b"\xef\xbb\xbf")
            text = original.decode("utf-8-sig" if has_bom else "utf-8")

            new_text, changed, tag_present = transform_note(
                text, yaml, tag, path, legacy_status
            )

            value = "true" if tag_present else "false"
            action = f"set {tag}: {value}"

            if changed:
                print(f"{relative}: would {action}" if dry_run
                      else f"{relative}: {action}")

                if not dry_run:
                    encoded = new_text.encode("utf-8")
                    if has_bom:
                        encoded = b"\xef\xbb\xbf" + encoded

                    temp_path = None
                    try:
                        with tempfile.NamedTemporaryFile(
                            dir=path.parent,
                            prefix=f".{path.name}.",
                            suffix=".tmp",
                            delete=False,
                        ) as temp:
                            temp_path = Path(temp.name)
                            temp.write(encoded)

                        shutil.copystat(path, temp_path)
                        temp_path.replace(path)
                    finally:
                        if temp_path is not None:
                            temp_path.unlink(missing_ok=True)

                updated += 1
            else:
                print(f"{relative}: no changes needed")
                unchanged += 1

        except (OSError, UnicodeError, ValueError, YAMLError) as exc:
            print(f"ERROR: {path}: {exc}", file=sys.stderr)
            errors += 1

    action = "would be updated" if dry_run else "updated"
    print(
        f"\nDone: {updated} note(s) {action}, "
        f"{unchanged} unchanged, {errors} error(s)."
    )
    return 1 if errors else 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Set a boolean frontmatter property named after a tag "
            "based on whether each Obsidian note contains that tag."
        )
    )
    parser.add_argument("vault", type=Path, help="Path to the Obsidian vault")
    parser.add_argument(
        "--tag",
        type=normalize_tag,
        default="watched",
        help="Tag to check (default: watched; '#' prefix optional)",
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="Apply changes (default: dry run)",
    )
    parser.add_argument(
        "--legacy-status",
        action="store_true",
        help="Also treat 'Status:: watched' as a match for the tag.",
    )

    args = parser.parse_args()

    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_-]*", args.tag):
        parser.error(
            "--tag must also be a valid simple YAML property name: "
            "letters, digits, underscores, and hyphens, not starting "
            "with a digit or hyphen."
        )

    vault = args.vault.expanduser().resolve()
    if not vault.is_dir():
        parser.error(f"Vault directory does not exist: {vault}")

    return process_vault(
        vault,
        args.tag,
        dry_run=not args.write,
        legacy_status=args.legacy_status,
    )


if __name__ == "__main__":
    raise SystemExit(main())
