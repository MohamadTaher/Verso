"""
Settings, in the two kinds this app has.

`.env` holds the API key. A key is a secret, it is set once, and reading it
again would never give a different answer, so it is read here at import and kept
as a plain constant.

`settings.env` holds everything someone retunes while the server is running.
Those are read from `env_file` at the moment they are asked for, never cached:
see `pacing` for the ones the CLI and the server share, and `server/settings.py`
for the limits that are the server's alone.

Importing this package is what loads `.env`, so `GEMINI_API_KEY` below is the
only supported way to reach the key. Reading `os.environ` for it elsewhere works
only for as long as that module happens to import this one first.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Read .env from the project root rather than the working directory, so the key
# is found no matter where the CLI or the server is started from. Real
# environment variables already set win, which is how deployment secrets
# override the local file.
load_dotenv(PROJECT_ROOT / ".env")

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

__all__ = ["GEMINI_API_KEY", "PROJECT_ROOT"]
