"""
Retuning `settings.env` for the length of a `with` block, and putting it back.

The suite changes settings rather than working around them: a test that needs a
smaller token budget or a lower ceiling edits the real file, because the server
re-reading it is itself one of the things under test.
"""

from contextlib import contextmanager
from typing import Dict

from .paths import SETTINGS_FILE


_write_counter = 0


@contextmanager
def settings(**overrides):
    """
    Retune `settings.env` for the length of a `with` block, then put it back.

    The server re-reads the file whenever its timestamp *or size* moves, so this
    guarantees the size moves: a bind-mounted Windows directory can report
    timestamps too coarse to tell two writes apart, and a same-size rewrite
    inside one tick would leave the old values cached with nothing to show for
    it. Restoring writes the original text back byte for byte, so the file the
    reader edits is never left with a test's numbers in it.
    """
    global _write_counter
    original = SETTINGS_FILE.read_text(encoding="utf-8")

    _write_counter += 1
    marked = _with_overrides(original, overrides) + f"\n# test override {'-' * _write_counter}\n"
    while len(marked.encode("utf-8")) == len(original.encode("utf-8")):
        marked += "-"

    try:
        SETTINGS_FILE.write_text(marked, encoding="utf-8")
        yield
    finally:
        SETTINGS_FILE.write_text(original, encoding="utf-8")


def _with_overrides(text: str, overrides: Dict[str, object]) -> str:
    """Replace the settings named, and append the ones the file doesn't carry."""
    lines = text.splitlines()
    remaining = dict(overrides)

    for index, line in enumerate(lines):
        name = line.split("=", 1)[0].strip()
        if name in remaining:
            lines[index] = f"{name}={remaining.pop(name)}"

    lines += [f"{name}={value}" for name, value in remaining.items()]
    return "\n".join(lines) + "\n"

