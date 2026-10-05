from __future__ import annotations
import json
import re
from collections import Counter

STOP = {
    "a", "o", "e", "de", "do", "da", "dos", "das", "em", "um", "uma", "para", "por", "com",
    "eu", "meu", "minha", "meus", "minhas", "que", "se", "na", "no", "nas", "nos", "ao", "aos"
}

def _tokens(text: str) -> list[str]:
    words = re.findall(r"[a-záàâãéêíóôõúç0-9]+", (text or "").lower())
    return [w for w in words if len(w) > 2 and w not in STOP]

def _cosine(a: str, b: str) -> float:
    ca, cb = Counter(_tokens(a)), Counter(_tokens(b))
    if not ca or not cb:
        return 0.0
    common = set(ca) & set(cb)
    dot = sum(ca[x] * cb[x] for x in common)
    na = sum(v * v for v in ca.values()) ** 0.5
    nb = sum(v * v for v in cb.values()) ** 0.5
    return dot / (na * nb) if na and nb else 0.0

def package_text(package: dict) -> str:
    return "\n".join([
        str(package.get("concept", "")),
        "\n".join(package.get("affirmations", []) or []),
        "\n".join(package.get("titles", []) or []),
        str(package.get("description", "")),
        str(package.get("visual_prompt", "")),
    ])

def compare_to_history(package: dict, history: list[dict]) -> dict:
    current = package_text(package)
    best_score = 0.0
    best_project = None
    for row in history:
        try:
            old_pkg = json.loads(row.get("package_json") or "{}")
        except Exception:
            old_pkg = {}
        score = _cosine(current, package_text(old_pkg))
        if score > best_score:
            best_score = score
            best_project = row.get("id")
    return {
        "score": round(best_score, 3),
        "percent": round(best_score * 100, 1),
        "closest_project_id": best_project,
        "risk": "alto" if best_score >= 0.78 else "medio" if best_score >= 0.62 else "baixo",
    }
