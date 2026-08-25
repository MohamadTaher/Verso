"""What passed, what failed, what is only worrying, and how it is printed."""

import json
import sys
import time
import traceback
from pathlib import Path
from typing import Callable, Dict, List

from .paths import RESULTS_DIR


class Report:
    """
    What passed, what failed, and what is only worrying.

    A soft check is one whose answer comes from the model rather than from the
    code — whether it honoured a glossary term, say. Those are worth watching
    and not worth failing a build over, so they are counted apart.
    """

    def __init__(self, title: str):
        self.title = title
        self.entries: List[Dict] = []
        self.started = time.time()
        print(f"\n{'=' * 78}\n{title}\n{'=' * 78}")

    def section(self, name: str):
        print(f"\n-- {name} " + "-" * max(0, 72 - len(name)))

    def check(self, name: str, passed: bool, detail: str = "") -> bool:
        return self._record("PASS" if passed else "FAIL", name, detail)

    def soft(self, name: str, passed: bool, detail: str = "") -> bool:
        return self._record("PASS" if passed else "WARN", name, detail)

    def note(self, name: str, detail: str = ""):
        self._record("INFO", name, detail)

    def broke(self, name: str, error: BaseException):
        self._record("FAIL", name, f"{type(error).__name__}: {error}")
        traceback.print_exc()

    def _record(self, outcome: str, name: str, detail: str) -> bool:
        self.entries.append({'outcome': outcome, 'name': name, 'detail': detail})
        print(f"  [{outcome}] {name}" + (f"  -- {detail}" if detail else ""))
        return outcome == "PASS"

    def counts(self) -> Dict[str, int]:
        tally = {'PASS': 0, 'FAIL': 0, 'WARN': 0, 'INFO': 0}
        for entry in self.entries:
            tally[entry['outcome']] += 1
        return tally

    def summary(self) -> int:
        tally = self.counts()
        elapsed = time.time() - self.started
        print(f"\n{'=' * 78}")
        print(f"{self.title}: {tally['PASS']} passed, {tally['FAIL']} failed, "
              f"{tally['WARN']} warnings, in {elapsed:.0f}s")

        for entry in self.entries:
            if entry['outcome'] in ("FAIL", "WARN"):
                print(f"  [{entry['outcome']}] {entry['name']}"
                      + (f"  -- {entry['detail']}" if entry['detail'] else ""))
        print("=" * 78)

        return tally['FAIL']

    def save(self, name: str) -> Path:
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        path = RESULTS_DIR / name
        path.write_text(json.dumps({
            'title': self.title,
            'at': time.strftime("%Y-%m-%d %H:%M:%S"),
            'seconds': round(time.time() - self.started, 1),
            'counts': self.counts(),
            'entries': self.entries,
        }, indent=2, ensure_ascii=False), encoding="utf-8")
        return path


def run_tests(report: Report, tests: List[Callable], *arguments) -> None:
    """
    Run each test, and let a failing one fail alone.

    A test that raises has still told us something, and the ones after it are
    usually about something else entirely — so the traceback is recorded as a
    failure and the suite carries on.
    """
    for test in tests:
        try:
            test(*arguments)
        except Exception as error:
            report.broke(f"{test.__name__} raised", error)
        sys.stdout.flush()
