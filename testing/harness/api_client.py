"""
The endpoints, called the way the browser calls them.

One client per visitor: `ip` is sent as `X-Forwarded-For`, which is how a test
pretends to be a second reader when the cooldown is per visitor.
"""

import json
import os
import time
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

import requests

# Inside the app container this is uvicorn itself. From anywhere else, point it
# at the published port instead.
BASE_URL = os.environ.get("EPUB_TEST_BASE_URL", "http://localhost:7860")


class Api:
    """
    The endpoints, called the way the browser calls them.

    `ip` is sent as `X-Forwarded-For`, which is what `_client_ip` reads: that is
    how a test pretends to be a second visitor, since the cooldown is per
    address and every test otherwise arrives from the same one.
    """

    def __init__(self, base_url: str = BASE_URL, ip: str = "198.51.100.7",
                 headers: Optional[Dict[str, str]] = None):
        self.base_url = base_url.rstrip("/")
        self.ip = ip
        # Sent with every call. The one use is a `Host` header: the Vite dev
        # server answers 403 to a request that arrives under the container's own
        # hostname, so reaching it over the compose network means saying
        # localhost the way a browser would.
        self.headers = headers or {}

    def _call(self, method: str, path: str, **kwargs) -> requests.Response:
        headers = {'X-Forwarded-For': self.ip, **self.headers, **kwargs.pop('headers', {})}
        kwargs.setdefault('timeout', 60)
        return requests.request(method, f"{self.base_url}{path}", headers=headers, **kwargs)

    def status(self) -> requests.Response:
        return self._call("GET", "/api/status")

    def upload(self, path, source_lang: str = "auto", target_lang: str = "English",
               filename: Optional[str] = None) -> requests.Response:
        path = Path(path)
        with open(path, "rb") as handle:
            return self._call(
                "POST", "/api/jobs",
                files={'file': (filename or path.name, handle.read(), "application/epub+zip")},
                data={'source_lang': source_lang, 'target_lang': target_lang},
            )

    def job(self, job_id: str) -> requests.Response:
        return self._call("GET", f"/api/jobs/{job_id}")

    def preview(self, job_id: str, chapter_ids: Optional[List[str]] = None) -> requests.Response:
        return self._call("POST", f"/api/jobs/{job_id}/preview", json={'chapter_ids': chapter_ids})

    def start(self, job_id: str, chapter_ids: Optional[List[str]] = None) -> requests.Response:
        return self._call("POST", f"/api/jobs/{job_id}/start", json={'chapter_ids': chapter_ids})

    def cancel(self, job_id: str) -> requests.Response:
        return self._call("POST", f"/api/jobs/{job_id}/cancel")

    def cover(self, job_id: str) -> requests.Response:
        return self._call("GET", f"/api/jobs/{job_id}/cover")

    def download(self, job_id: str) -> requests.Response:
        return self._call("GET", f"/api/jobs/{job_id}/download")

    def get_glossary(self, job_id: str) -> requests.Response:
        return self._call("GET", f"/api/jobs/{job_id}/glossary")

    def put_glossary(self, job_id: str, terms: Dict) -> requests.Response:
        return self._call("PUT", f"/api/jobs/{job_id}/glossary", json={'terms': terms})

    def stream(self, job_id: str, on_event: Optional[Callable[[Dict], None]] = None,
               timeout: int = 900) -> Tuple[List[Dict], Optional[Dict]]:
        """
        Follow a job to its end, returning every event and the final snapshot.

        `on_event` runs on this thread, between two reads of the socket, which is
        what lets a test cancel a run or download the book mid-flight at a known
        point rather than after a guessed sleep.

        The stream is deliberately not reopened when it closes: the server ends
        it when the job is terminal, and a reconnect would replay the whole log
        and end again, forever. Tests that want the replay ask for it by calling
        this a second time.
        """
        events: List[Dict] = []
        final: Optional[Dict] = None
        deadline = time.time() + timeout
        name = None

        with self._call("GET", f"/api/jobs/{job_id}/events", stream=True,
                        timeout=(10, 60)) as response:
            response.raise_for_status()

            for line in response.iter_lines(decode_unicode=True):
                if time.time() > deadline:
                    raise TimeoutError(f"job {job_id} was still running after {timeout}s")
                if not line or line.startswith(":"):        # blank, or a keep-alive
                    continue
                if line.startswith("event:"):
                    name = line[len("event:"):].strip()
                    continue
                if not line.startswith("data:"):
                    continue

                payload = json.loads(line[len("data:"):].strip())
                if name == "end":
                    final = payload
                    break

                events.append(payload)
                if on_event:
                    on_event(payload)

        return events, final


def wait_for(condition: Callable[[], bool], timeout: float = 30, interval: float = 0.5) -> bool:
    """Poll until something becomes true, or give up and say so."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        if condition():
            return True
        time.sleep(interval)
    return condition()

