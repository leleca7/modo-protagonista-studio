from __future__ import annotations
import json
import re
import requests

def ollama_available(base_url: str = "http://localhost:11434", timeout: float = 2.0) -> bool:
    try:
        return requests.get(base_url.rstrip("/") + "/api/tags", timeout=timeout).ok
    except Exception:
        return False

def list_ollama_models(base_url: str = "http://localhost:11434") -> list[str]:
    try:
        r = requests.get(base_url.rstrip("/") + "/api/tags", timeout=3)
        r.raise_for_status()
        return [m.get("name") for m in r.json().get("models", []) if m.get("name")]
    except Exception:
        return []

def _extract_json(text: str) -> dict:
    text = text.strip()
    try:
        return json.loads(text)
    except Exception:
        m = re.search(r"\{.*\}", text, flags=re.S)
        if not m:
            raise ValueError("A resposta do modelo não contém JSON válido.")
        return json.loads(m.group(0))

def generate_with_ollama(prompt: str, model: str, base_url: str) -> dict:
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "format": "json",
        "options": {"temperature": 0.88, "top_p": 0.92},
    }
    r = requests.post(base_url.rstrip("/") + "/api/generate", json=payload, timeout=420)
    r.raise_for_status()
    return _extract_json(r.json().get("response", "{}"))

def fallback_package(theme: str, audience: str) -> dict:
    stems = [
        "Eu avanço com confiança em direção ao meu objetivo.",
        "Eu ajo com clareza e constância todos os dias.",
        "Eu reconheço oportunidades alinhadas com o que quero construir.",
        "Minha rotina favorece meu crescimento e meu bem-estar.",
        "Eu confio na minha capacidade de aprender, adaptar e evoluir.",
        "Eu transformo intenção em ações simples e consistentes.",
        "Eu me sinto preparada para novas possibilidades.",
        "Eu escolho hábitos coerentes com a vida que desejo construir.",
        "Eu percebo meu progresso e valorizo cada etapa.",
        "Eu mantenho foco no que está sob meu controle.",
    ]
    affirmations = []
    for block in range(6):
        for s in stems:
            affirmations.append(s.replace("meu objetivo", theme.lower()).replace(".", f" — fase {block + 1}."))
    return {
        "concept": f"Jornada em seis fases para {theme}, com foco em confiança, hábitos, percepção e constância.",
        "titles": [
            f"{theme} ✦ entre no modo protagonista",
            f"modo protagonista: {theme} | afirmações + relaxamento",
            f"uma nova fase: {theme} ✨",
            f"afirmações para {theme} | foco e constância",
            f"{theme} — sessão longa para relaxar e visualizar",
        ],
        "affirmations": affirmations,
        "blocks": [{"name": f"Fase {i+1}", "purpose": "progressão temática", "affirmation_indexes": [i*10+1, i*10+10]} for i in range(6)],
        "description": f"Sessão de afirmações do Modo Protagonista com foco em {theme}. Conteúdo de entretenimento, relaxamento e desenvolvimento pessoal; não garante resultados específicos.",
        "pinned_comment": "Qual tema você quer ver no próximo vídeo? ✨ Encomendas: [E-MAIL]",
        "keywords": [theme, "afirmações", "modo protagonista", "relaxamento", "visualização"],
        "visual_prompt": f"visual editorial e atmosférico inspirado em {theme}, movimento sutil, luz suave, composição 16:9, seamless loop, sem texto",
        "visual_variations": ["variação de luz", "variação de enquadramento", "variação de partículas/chuva"],
        "thumbnail_texts": ["ELA CONSEGUIU", "NOVA FASE", "MODO PROTAGONISTA", "É A SUA VEZ", "TUDO SE ALINHA"],
        "differentiators": ["seis blocos", "progressão", "visual específico", "paisagem sonora", "metadados próprios"],
        "source": "fallback-sem-IA",
    }
