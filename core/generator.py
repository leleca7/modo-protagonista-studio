from __future__ import annotations
import json
import re
from .ai import generate_with_ollama, fallback_package, ollama_available
from .config import ROOT
from .similarity import compare_to_history

def slugify(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9áàâãéêíóôõúç]+", "-", value, flags=re.I)
    return value.strip("-") or "projeto"

def build_prompt(meta: dict, history: list[dict], variation_note: str = "") -> str:
    history_short = []
    for p in history[:8]:
        try:
            old_pkg = json.loads(p.get("package_json") or "{}")
        except Exception:
            old_pkg = {}
        history_short.append({
            "id": p.get("id"),
            "theme": p.get("theme"),
            "concept": old_pkg.get("concept", ""),
            "first_affirmations": (old_pkg.get("affirmations") or [])[:5],
            "visual_style": p.get("visual_style"),
            "ambient": p.get("ambient"),
        })
    return f"""
Você é a redatora, diretora criativa e editora do canal Modo Protagonista.
Crie um pacote ORIGINAL para um vídeo de afirmações/relaxamento. A diferença deve ser perceptível para a pessoa que assiste, e não apenas uma troca cosmética de palavras.

OBJETIVO: {meta['theme']}
PÚBLICO: {meta['audience']}
DURAÇÃO FINAL: {meta['duration_minutes']} minutos
ESTILO VISUAL: {meta['visual_style']}
AMBIENTE: {meta['ambient']}
FREQUÊNCIA OPCIONAL: {meta['frequency']} Hz
INTENSIDADE DA VOZ: {meta.get('voice_style', 'calma, íntima e natural')}

Histórico recente a evitar repetir:
{json.dumps(history_short, ensure_ascii=False)}

{variation_note}

REGRAS EDITORIAIS:
- Gere 60 afirmações em português brasileiro, divididas em 6 blocos com progressão clara.
- Misture estruturas: eu sou, eu sinto, eu percebo, eu consigo, minha rotina, é natural para mim, eu escolho.
- Não prometa resultado garantido, cura, riqueza instantânea, mudança corporal impossível ou aprovação certa.
- Em temas de aparência, use linguagem de autocuidado, percepção, hábitos e confiança; não faça alegações médicas.
- Em dinheiro, carreira e estudos, combine mentalidade com hábitos e ações concretas.
- Não atribua efeitos científicos comprovados a frequências Hz.
- Títulos podem ser fortes, mas não devem afirmar que ouvir garante um resultado.
- O conceito visual deve permitir loop contínuo, com movimento sutil e sem texto embutido.
- Crie também 3 microvariações visuais que possam ser alternadas ao longo de vídeos longos.

Responda SOMENTE JSON válido com estas chaves:
concept (string), titles (array com 5), affirmations (array com 60),
blocks (array com 6 objetos: name, purpose, affirmation_indexes),
description (string), pinned_comment (string), keywords (array), visual_prompt (string),
visual_variations (array com 3), thumbnail_texts (array com 5 textos de no máximo 5 palavras),
differentiators (array com 5), source (string "ollama-local").
""".strip()

def _normalize_package(package: dict, meta: dict) -> dict:
    package.setdefault("concept", f"Sessão focada em {meta['theme']}")
    package.setdefault("titles", [meta["theme"]])
    package.setdefault("affirmations", [])
    package.setdefault("blocks", [])
    package.setdefault("description", "")
    package.setdefault("pinned_comment", "")
    package.setdefault("keywords", [])
    package.setdefault("visual_prompt", "")
    package.setdefault("visual_variations", [])
    package.setdefault("thumbnail_texts", [meta["theme"]])
    package.setdefault("differentiators", [])
    return package

def generate_package(meta: dict, history: list[dict], cfg: dict) -> tuple[dict, dict]:
    if cfg.get("ai_provider") == "ollama" and ollama_available(cfg.get("ollama_url")):
        try:
            package = generate_with_ollama(build_prompt(meta, history), cfg.get("ollama_model"), cfg.get("ollama_url"))
            package["source"] = "ollama-local"
        except Exception as e:
            package = fallback_package(meta["theme"], meta["audience"])
            package["warning"] = f"Ollama falhou; usado modo sem IA: {e}"
    else:
        package = fallback_package(meta["theme"], meta["audience"])

    package = _normalize_package(package, meta)
    similarity = compare_to_history(package, history)
    threshold = float(cfg.get("similarity_regenerate_threshold", 0.78))
    if similarity["score"] >= threshold and package.get("source") == "ollama-local":
        try:
            note = (
                f"A primeira versão ficou {similarity['percent']}% semelhante ao projeto #{similarity['closest_project_id']}. "
                "Refaça o conceito do zero: mude progressão, vocabulário, metáforas, organização dos blocos, direção visual e títulos."
            )
            package = generate_with_ollama(build_prompt(meta, history, note), cfg.get("ollama_model"), cfg.get("ollama_url"))
            package["source"] = "ollama-local-regenerado"
            package = _normalize_package(package, meta)
            similarity = compare_to_history(package, history)
        except Exception:
            pass
    package["similarity"] = similarity
    return package, similarity

def write_project_files(meta: dict, package: dict):
    from datetime import datetime
    slug = slugify(meta["theme"])
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = ROOT / "output" / f"{stamp}_{slug}"
    out.mkdir(parents=True, exist_ok=True)
    (out / "project.json").write_text(json.dumps({"meta": meta, "package": package}, ensure_ascii=False, indent=2), encoding="utf-8")
    (out / "affirmations.txt").write_text("\n".join(package.get("affirmations", [])), encoding="utf-8")
    (out / "tts_script.txt").write_text(". ".join(package.get("affirmations", [])), encoding="utf-8")
    (out / "metadata.txt").write_text(
        "TÍTULOS\n" + "\n".join(package.get("titles", [])) + "\n\nDESCRIÇÃO\n" + package.get("description", "") +
        "\n\nCOMENTÁRIO FIXADO\n" + package.get("pinned_comment", "") + "\n\nPALAVRAS-CHAVE\n" + ", ".join(package.get("keywords", [])),
        encoding="utf-8",
    )
    (out / "visual_prompt.txt").write_text(package.get("visual_prompt", ""), encoding="utf-8")
    return out
