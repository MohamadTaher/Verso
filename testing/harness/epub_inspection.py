"""
Opening a finished book and reading what is actually in it.

Deliberately avoids `verso`. Checking the writer's output with the reader that
produced it would agree with itself no matter what went wrong, so a downloaded
book is opened here as a plain zip and its text counted character by character.
"""

import io
import re
import zipfile
from pathlib import Path
from typing import Dict, List
from urllib.parse import unquote

from bs4 import BeautifulSoup

# Unicode ranges, restated here rather than imported, so a book that comes back
# untranslated cannot be declared translated by the same table that misjudged it.
SCRIPTS = {
    'chinese': [(0x4E00, 0x9FFF), (0x3400, 0x4DBF)],
    'arabic': [(0x0600, 0x06FF)],
    'latin': [(0x0041, 0x005A), (0x0061, 0x007A)],
}


def epub_documents(path) -> Dict[str, str]:
    """Every XHTML document in the archive, by the name it is stored under."""
    with zipfile.ZipFile(path) as archive:
        return {
            name: archive.read(name).decode("utf-8", "replace")
            for name in archive.namelist()
            if name.lower().endswith((".xhtml", ".html", ".htm"))
        }


def epub_members(path) -> List[str]:
    """Every member, duplicates included — which is the point of asking."""
    with zipfile.ZipFile(path) as archive:
        return [info.filename for info in archive.infolist()]


def duplicate_members(path) -> List[str]:
    """
    Names stored more than once.

    A zip may hold two members under one name and most readers show the first,
    so a book that duplicates its nav document looks fine until something strict
    opens it. `EpubWriter._ensure_navigation` exists to prevent exactly this.
    """
    seen, duplicates = set(), []
    for name in epub_members(path):
        if name in seen:
            duplicates.append(name)
        seen.add(name)
    return duplicates


def opf_metadata(path) -> Dict[str, List[str]]:
    """
    The titles and languages the package document declares, in the order it
    declares them.

    Lists rather than single values, because an EPUB may carry several of each
    and a reader shows the first — so "what language is this book in" is
    answered by position, not by whether the right value is in there somewhere.
    """
    with zipfile.ZipFile(path) as archive:
        opf_name = next((n for n in archive.namelist() if n.lower().endswith(".opf")), None)
        if not opf_name:
            return {'titles': [], 'languages': []}
        opf = archive.read(opf_name).decode("utf-8", "replace")

    def field(tag: str) -> List[str]:
        return [value.strip()
                for value in re.findall(rf"<dc:{tag}[^>]*>(.*?)</dc:{tag}>", opf, re.S)]

    return {'titles': field("title"), 'languages': field("language")}


def is_epub(content: bytes) -> bool:
    """Whether these bytes are an archive that opens."""
    try:
        with zipfile.ZipFile(io.BytesIO(content)) as archive:
            return archive.testzip() is None
    except (zipfile.BadZipFile, OSError):
        return False


def download_filename(response) -> str:
    """
    The name a browser would save a download under.

    Starlette percent-encodes the name into `filename*=utf-8''…` as soon as it
    holds anything that needs quoting — a space and a bracket are enough — so
    the header has to be decoded before it can be read.
    """
    disposition = response.headers.get("content-disposition", "")
    match = re.search(r"filename\*=utf-8''([^;]+)", disposition) or \
        re.search(r'filename="([^"]+)"', disposition)
    return unquote(match.group(1)) if match else ""


def visible_text(html: str) -> str:
    """The words a reader would see, with the markup taken out."""
    soup = BeautifulSoup(html, "html.parser")
    return (soup.body or soup).get_text(" ", strip=True)


def script_ratio(text: str, script: str) -> float:
    """
    Share of the letters in `text` that belong to `script`.

    Counted here rather than imported: this is the measure a translated chapter
    is judged by, so it has to be independent of the code that decided the
    chapter was translated.
    """
    ranges = SCRIPTS[script]
    letters = [character for character in text if character.isalpha()]
    if not letters:
        return 0.0

    inside = sum(1 for character in letters
                 if any(low <= ord(character) <= high for low, high in ranges))
    return inside / len(letters)


def chapter_texts(path) -> Dict[str, str]:
    """
    Every document in the book that carries words, by member name.

    The cover page and the navigation are dropped: neither is a chapter, and
    both would drag a script ratio towards whichever language wrote the markup.
    """
    texts = {}
    for name, html in epub_documents(path).items():
        if "nav" in Path(name).name.lower() or "cover" in Path(name).name.lower():
            continue
        text = visible_text(html)
        if text:
            texts[name] = text
    return texts

