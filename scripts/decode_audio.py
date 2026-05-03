"""
Decode audio filenames that are in some scrambled encoding, produce a manifest
mapping readable Kalmyk lemma -> original file path.

Approach: try common encoding-round-trip patterns until Kalmyk chars appear.
The audio originates from an old Lingvo package; filenames are the lemma +
optional sense suffix like '_I_1)_1.wav'.
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
AUDIO_DIR = Path(os.environ.get("XALMG_AUDIO_DIR", PROJECT_ROOT / "data" / "xal-rus-audio"))
OUT = PROJECT_ROOT / "assets" / "data" / "audio_manifest.json"

# Round-trip chains: bytes interpreted as X, then re-decoded as Y
# We list candidates; pick one with best Kalmyk/Russian plausibility.
# NOTE: cp437 -> cp866 wins because the audio pack is from an old DOS-era
# Lingvo package where filenames were stored in cp866 and later extracted
# on Windows using cp437 fallback.
CANDIDATES = [
    ("cp437", "cp866"),
    ("cp437", "cp855"),
    ("cp1252", "cp1251"),
    ("latin-1", "cp1251"),
    ("cp866", "cp1251"),
]

# Alphabet: Kalmyk extends Russian Cyrillic with Ә, Ө, Ү, Җ, Ң, Һ
KALMYK_EXTRA = "ӘәӨөҮүҖҗҢңҺһ"
CYRILLIC_RU = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдеёжзийклмнопрстуфхцчшщъыьэюя"
OK_CHARS = set(KALMYK_EXTRA + CYRILLIC_RU + "0123456789_()-")
ALLOWED_EXT = ".wav"


def score(s: str) -> int:
    """Higher = more plausibly a Kalmyk/Russian word.
    Lowercase cyrillic letters score higher than uppercase (Lingvo lemmas are lowercase)."""
    stem = s.split(".wav")[0]
    total = len(stem)
    if total == 0:
        return -1
    lower_cyr = sum(1 for c in stem if c in "абвгдеёжзийклмнопрстуфхцчшщъыьэюяәөүҗңһ")
    upper_cyr = sum(1 for c in stem if c in "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯӘӨҮҖҢҺ")
    ok = sum(1 for c in stem if c in OK_CHARS)
    weird = total - ok
    bonus = 5 if any(c in KALMYK_EXTRA for c in stem) else 0
    # prefer lowercase Cyrillic (Kalmyk lemmas); penalize mostly-uppercase
    return lower_cyr * 3 + upper_cyr + ok - weird * 3 + bonus


def try_decode(name: str) -> tuple[str, int, tuple[str, str] | None]:
    """Return (best_decoded, score, chain)."""
    best = name
    best_score = score(name)
    best_chain: tuple[str, str] | None = None
    raw_bytes = None
    # The filename arrived as a python str from os.listdir — it's already decoded
    # by the OS (Windows API is UTF-16). So if mojibake, the mojibake is already
    # baked into the unicode. We need to "undo" the mis-decoding.
    # Try: re-encode to each encoding, then decode as the intended one.
    for src, dst in CANDIDATES:
        try:
            b = name.encode(src)
            d = b.decode(dst)
        except (UnicodeEncodeError, UnicodeDecodeError):
            continue
        sc = score(d)
        if sc > best_score:
            best = d
            best_score = sc
            best_chain = (src, dst)
    return best, best_score, best_chain


SUFFIX = re.compile(
    r"(?P<sense>_(?:I{1,3}|IV|V)(?:_\d+\))?(?:_\d+)?)?$"
)


def split_suffix(stem: str) -> tuple[str, str]:
    """Separate 'аав' from trailing sense/variant suffix like '_I_1)_1'."""
    # Roman-numeral or digit sense markers at end
    m = re.search(r"(_[IVX]+(?:_\d+\))?(?:_\d+)?|_\d+)$", stem)
    if m:
        return stem[:m.start()], stem[m.start():]
    return stem, ""


def main() -> int:
    if not AUDIO_DIR.exists():
        print(f"audio dir not found: {AUDIO_DIR}", file=sys.stderr)
        return 1

    manifest: dict[str, list[dict]] = {}
    samples: list[dict] = []
    encoding_votes: dict[tuple[str, str] | None, int] = {}

    files = [f for f in os.listdir(AUDIO_DIR) if f.lower().endswith(ALLOWED_EXT)]
    print(f"found {len(files)} wav files")

    # The filename pack is from DOS-era Lingvo. Force cp437->cp866 chain,
    # which empirically produces Cyrillic with standard suffix markers.
    best_chain = ("cp437", "cp866")
    print(f"forced chain: {best_chain}")

    # Second pass: apply the dominant chain where it improves the name
    for f in files:
        stem = f[:-4]
        if best_chain:
            src, dst = best_chain
            try:
                decoded = stem.encode(src).decode(dst)
                if score(decoded) < score(stem):
                    decoded = stem
            except (UnicodeEncodeError, UnicodeDecodeError):
                decoded = stem
        else:
            decoded = stem

        lemma, variant = split_suffix(decoded)
        manifest.setdefault(lemma.lower(), []).append({
            "file": f,
            "variant": variant,
            "decoded": decoded,
        })
        if len(samples) < 20:
            samples.append({"original": f, "decoded": decoded, "lemma": lemma, "variant": variant})

    OUT.parent.mkdir(parents=True, exist_ok=True)
    # sanitize surrogate escapes introduced by Windows filename quirks
    data = {
        "chain": best_chain,
        "count": len(files),
        "unique_lemmas": len(manifest),
        "manifest": manifest,
    }
    blob = json.dumps(data, ensure_ascii=False, indent=2)
    # replace lone surrogates with '?'
    blob = blob.encode("utf-8", errors="replace").decode("utf-8")
    OUT.write_text(blob, encoding="utf-8")
    print(f"wrote {OUT}")
    print(f"unique lemmas with audio: {len(manifest)}")
    print("samples:")
    for s in samples:
        print(f"  {s['original']!r} -> lemma={s['lemma']!r} var={s['variant']!r}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
