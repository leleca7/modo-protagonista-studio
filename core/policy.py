from __future__ import annotations
import hashlib
import json
import re
from datetime import datetime
import requests
from .config import ROOT

POLICIES = {
    "monetization": "https://support.google.com/youtube/answer/1311392?hl=pt-BR",
    "spam": "https://support.google.com/youtube/answer/2801973?hl=pt-BR",
    "synthetic": "https://support.google.com/youtube/answer/14328491?hl=pt-BR",
    "copyright_audio": "https://support.google.com/youtube/answer/3376882?hl=pt-BR",
}

def _clean_html(html: str) -> str:
    html = re.sub(r"<script.*?</script>", " ", html, flags=re.I | re.S)
    html = re.sub(r"<style.*?</style>", " ", html, flags=re.I | re.S)
    text = re.sub(r"<[^>]+>", " ", html)
    return re.sub(r"\s+", " ", text).strip()

def check_policy_changes() -> dict:
    folder = ROOT / "data" / "policies"
    folder.mkdir(parents=True, exist_ok=True)
    results = {}
    for key, url in POLICIES.items():
        try:
            r = requests.get(url, timeout=20, headers={"User-Agent": "ModoProtagonistaStudio/0.3"})
            r.raise_for_status()
            text = _clean_html(r.text)
            digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
            meta_path = folder / f"{key}.json"
            old = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}
            changed = bool(old.get("sha256")) and old.get("sha256") != digest
            (folder / f"{key}.txt").write_text(text, encoding="utf-8")
            now = datetime.now().isoformat(timespec="seconds")
            meta_path.write_text(json.dumps({"url": url, "checked_at": now, "sha256": digest}, ensure_ascii=False, indent=2), encoding="utf-8")
            results[key] = {"ok": True, "changed": changed, "url": url, "checked_at": now}
        except Exception as e:
            results[key] = {"ok": False, "changed": False, "url": url, "error": str(e)}
    return results
