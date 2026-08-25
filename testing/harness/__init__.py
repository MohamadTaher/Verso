"""
What every test in this folder is built out of.

One module per job, rather than the four this used to be in one file:

    paths.py               the repo, `settings.env`, and where reports are written
    api_client.py          `Api`: the endpoints, called the way the browser calls them
    settings_override.py   `settings(...)`: retune settings.env for a `with` block
    epub_inspection.py     opening a finished book and reading what is in it
    expected_packing.py    the packing rule restated, to check request counts against
    report.py              the tally, and what it prints at the end

Everything is re-exported here, so a suite writes `from harness import Api,
Report, settings` and never has to know which module a helper came from.
"""

from .api_client import BASE_URL, Api, wait_for
from .epub_inspection import (SCRIPTS, chapter_texts, download_filename, duplicate_members,
                              epub_documents, epub_members, is_epub, opf_metadata,
                              script_ratio, visible_text)
from .expected_packing import CHAPTER_SEPARATOR_TOKENS, PATCH_OVERHEAD_TOKENS, patches_by_rule
from .paths import RESULTS_DIR, ROOT, SETTINGS_FILE
from .report import Report, run_tests
from .settings_override import settings

__all__ = [
    "Api", "BASE_URL", "CHAPTER_SEPARATOR_TOKENS", "PATCH_OVERHEAD_TOKENS", "RESULTS_DIR",
    "ROOT", "SCRIPTS", "SETTINGS_FILE", "Report", "chapter_texts", "download_filename",
    "duplicate_members", "epub_documents", "epub_members", "is_epub", "opf_metadata",
    "patches_by_rule", "run_tests", "script_ratio", "settings", "visible_text", "wait_for",
]
