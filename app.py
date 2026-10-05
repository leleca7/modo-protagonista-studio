from __future__ import annotations
import json
from pathlib import Path
import streamlit as st

from core.config import ROOT, load_config, save_config
from core.db import recent_projects, get_project, update_project
from core.ai import ollama_available, list_ollama_models
from core.renderer import ffmpeg_available
from core.tts_windows import windows_sapi_available
from core.library import backgrounds, ambient_sounds, ensure_asset_folders
from core.pipeline import create_project, generate_voice, generate_thumbnail, render_project
from core.policy import check_policy_changes
from core.youtube_upload import upload_video, youtube_credentials_ready
from core.preflight import system_preflight

st.set_page_config(page_title="Modo Protagonista Studio", page_icon="✨", layout="wide")

st.markdown("""
<style>
.block-container { padding-top: 1.4rem; max-width: 1500px; }
[data-testid="stSidebar"] { background: #FAF3EA; }
.mp-hero {padding:22px 26px;border-radius:24px;background:linear-gradient(115deg,#1A1420,#5B284C);color:#fff;margin-bottom:18px;}
.mp-hero h1{margin:0;font-size:2.1rem}.mp-hero p{margin:.35rem 0 0;opacity:.85}
.mp-pill{display:inline-block;padding:5px 10px;border-radius:99px;background:#D6FF52;color:#1A1420;font-weight:700;font-size:.8rem;margin-right:6px}
</style>
<div class="mp-hero">
<span class="mp-pill">LOCAL</span><span class="mp-pill">FREE-FIRST</span>
<h1>✨ Modo Protagonista Studio</h1>
<p>Roteiro, voz, visual, render, thumbnail, compliance e publicação em um único painel.</p>
</div>
""", unsafe_allow_html=True)

cfg = load_config()
ensure_asset_folders()
preflight = system_preflight(cfg, ROOT)

if "project" not in st.session_state:
    st.session_state.project = None
if "policy_status" not in st.session_state:
    st.session_state.policy_status = None

with st.sidebar:
    st.subheader("Sistema")
    st.write("**IA local:**", "🟢 Ollama online" if ollama_available(cfg["ollama_url"]) else "⚪ modo sem IA")
    st.write("**FFmpeg:**", "🟢 pronto" if ffmpeg_available(cfg["ffmpeg_path"]) else "🔴 ausente")
    st.write("**Voz local:**", "🟢 Windows SAPI" if windows_sapi_available() else "🟠 indisponível neste sistema")
    st.write("**YouTube:**", "🟢 credencial encontrada" if youtube_credentials_ready(ROOT / cfg["youtube_client_secret"]) else "⚪ não configurado")
    st.write("**Disco livre:**", f"{preflight['free_gb']} GB" + (" ⚠️" if preflight["disk_warning"] else ""))
    st.divider()
    st.caption("Chaves, tokens, banco, renders e biblioteca de mídia ficam locais e fora do Git.")

new_tab, library_tab, history_tab, rules_tab, settings_tab = st.tabs([
    "✨ Novo vídeo", "🗂 Biblioteca", "📚 Histórico", "🛡 Regras", "⚙️ Configurações"
])

with new_tab:
    st.subheader("1. Briefing")
    c1, c2, c3 = st.columns(3)
    with c1:
        theme = st.text_input("Objetivo específico", "Passar na faculdade que desejo")
        audience = st.selectbox("Público", ["Feminino", "Unissex", "Masculino"])
        voice_style = st.selectbox("Estilo da voz", [
            "calma, íntima e natural",
            "sussurrada e lenta",
            "suave e confiante",
            "neutra e relaxante",
        ])
    with c2:
        duration_label = st.selectbox(
            "Duração final",
            ["1 minuto (teste)", "11 minutos", "60 minutos", "8 horas", "11 horas"],
            index=0,
        )
        duration_map = {
            "1 minuto (teste)": 1,
            "11 minutos": 11,
            "60 minutos": 60,
            "8 horas": 480,
            "11 horas": 660,
        }
        frequency = st.selectbox(
            "Frequência opcional",
            [0, 211, 222, 432, 528],
            index=2,
            format_func=lambda x: "Sem frequência" if x == 0 else f"{x} Hz",
        )
        ambient_name = st.selectbox("Atmosfera", ["Chuva", "Mar", "Vento", "Silêncio", "Arquivo/Biblioteca"])
    with c3:
        visual_style = st.text_area(
            "Direção visual",
            "noturno, rosa suave, editorial, sonhador, movimento discreto",
            height=106,
        )
        st.caption("Se nenhum fundo for enviado, o sistema cria um visual procedural local.")

    bgs = backgrounds()
    ambs = ambient_sounds()
    c4, c5 = st.columns(2)
    with c4:
        bg_choice = st.selectbox("Fundo da biblioteca", ["— automático —"] + [p.name for p in bgs])
        background_upload = st.file_uploader(
            "Ou enviar fundo",
            type=["png", "jpg", "jpeg", "webp", "mp4", "mov", "mkv", "webm"],
            key="bg_upload",
        )
    with c5:
        amb_choice = st.selectbox("Som da biblioteca", ["— nenhum —"] + [p.name for p in ambs])
        ambient_upload = st.file_uploader(
            "Ou enviar som ambiente",
            type=["wav", "mp3", "m4a", "aac", "ogg", "flac"],
            key="amb_upload",
        )

    meta = {
        "theme": theme.strip(),
        "audience": audience,
        "duration_minutes": duration_map[duration_label],
        "visual_style": visual_style.strip(),
        "ambient": ambient_name,
        "frequency": int(frequency),
        "voice_style": voice_style,
    }

    auto_long_ok = True
    if meta["duration_minutes"] > 60:
        auto_long_ok = st.checkbox(
            "Entendo que renderizar 8h/11h pode levar bastante tempo e ocupar muito espaço no computador."
        )

    create_col, all_col = st.columns(2)
    with create_col:
        create_clicked = st.button("✨ CRIAR PROJETO", type="primary", use_container_width=True)
    with all_col:
        all_clicked = st.button(
            "⚡ GERAR TUDO",
            use_container_width=True,
            disabled=(meta["duration_minutes"] > 60 and not auto_long_ok),
            help="Cria pacote, voz, thumbnail e vídeo final em sequência.",
        )

    if create_clicked or all_clicked:
        if not theme.strip():
            st.error("Digite um objetivo específico.")
        elif all_clicked and not preflight["ffmpeg_ok"]:
            st.error("FFmpeg não foi encontrado. Rode INSTALAR.bat antes de usar GERAR TUDO.")
        elif all_clicked and not preflight["tts_ok"]:
            st.error("A voz local gratuita depende do Windows PowerShell/SAPI. Rode o Studio no Windows.")
        else:
            lib_bg = next((p for p in bgs if p.name == bg_choice), None)
            lib_amb = next((p for p in ambs if p.name == amb_choice), None)
            try:
                with st.status("Produzindo projeto...", expanded=True) as status:
                    st.write("1/4 Criando conceito, afirmações e metadados...")
                    project = create_project(meta, cfg, background_upload, ambient_upload, lib_bg, lib_amb)
                    st.session_state.project = project

                    if all_clicked:
                        st.write("2/4 Gerando voz local...")
                        generate_voice(project, cfg)

                        st.write("3/4 Gerando thumbnail...")
                        thumb_options = project["package"].get("thumbnail_texts") or [theme]
                        generate_thumbnail(project, thumb_options[0])

                        st.write("4/4 Renderizando vídeo final com FFmpeg...")
                        render_project(project, cfg)
                        status.update(label="Projeto completo gerado.", state="complete", expanded=False)
                    else:
                        status.update(label="Pacote criativo pronto para revisão.", state="complete", expanded=False)

                sim = project["similarity"]
                if sim["risk"] == "alto":
                    st.warning(
                        f"Similaridade ainda alta: {sim['percent']}% com projeto #{sim['closest_project_id']}. "
                        "Revise antes de publicar."
                    )
                elif all_clicked:
                    st.success(f"Projeto #{project['id']} completo. Faça a revisão abaixo antes de publicar.")
                else:
                    st.success(
                        f"Projeto #{project['id']} criado. Similaridade máxima recente: "
                        f"{sim['percent']}% ({sim['risk']})."
                    )
            except Exception as e:
                st.error(f"A produção parou nesta etapa: {e}")

    project = st.session_state.project
    if project:
        st.divider()
        st.subheader("2. Revisão criativa")
        pkg = project["package"]
        out = Path(project["out_dir"])

        a, b = st.columns([1.2, 1])
        with a:
            st.markdown(f"**Conceito:** {pkg.get('concept', '')}")
            titles = pkg.get("titles") or [project["meta"]["theme"]]
            chosen_title = st.selectbox("Título do YouTube", titles, key=f"title_{project['id']}")
            description = st.text_area(
                "Descrição", pkg.get("description", ""), height=190, key=f"desc_{project['id']}"
            )
            if st.button("💾 Salvar título e descrição"):
                update_project(project["id"], selected_title=chosen_title, description=description)
                st.success("Metadados salvos.")
        with b:
            sim = pkg.get("similarity", {})
            st.metric("Similaridade recente", f"{sim.get('percent', 0)}%")
            st.write("**Origem do texto:**", pkg.get("source", ""))
            st.write("**Diferenciais:**")
            for d in pkg.get("differentiators", [])[:5]:
                st.write("•", d)

        with st.expander("📝 Ver as afirmações"):
            st.write("\n\n".join(pkg.get("affirmations", [])))

        with st.expander("🎨 Prompt visual e variações"):
            st.code(pkg.get("visual_prompt", ""), language=None)
            for v in pkg.get("visual_variations", []):
                st.write("•", v)

        st.subheader("3. Produção")
        p1, p2, p3 = st.columns(3)
        with p1:
            if st.button("🎙 GERAR VOZ LOCAL", use_container_width=True):
                try:
                    with st.spinner("Gerando voice.wav..."):
                        voice = generate_voice(project, cfg)
                    st.success(f"Voz pronta: {voice.name}")
                except Exception as e:
                    st.error(str(e))

        with p2:
            thumb_texts = pkg.get("thumbnail_texts") or ["MODO PROTAGONISTA"]
            thumb_text = st.selectbox("Texto da thumbnail", thumb_texts, key=f"thumbtext_{project['id']}")
            if st.button("🖼 GERAR THUMBNAIL", use_container_width=True):
                try:
                    thumb = generate_thumbnail(project, thumb_text)
                    st.success("Thumbnail pronta.")
                    st.image(str(thumb), use_container_width=True)
                except Exception as e:
                    st.error(str(e))

        with p3:
            if st.button("🎬 RENDERIZAR", use_container_width=True):
                try:
                    with st.spinner("Renderizando localmente com FFmpeg..."):
                        video = render_project(project, cfg)
                    st.success("Vídeo final pronto.")
                    st.video(str(video))
                except Exception as e:
                    st.error(str(e))

        latest = get_project(project["id"]) or {}
        thumb_path = Path(latest.get("thumbnail_path") or out / "thumbnail.jpg")
        video_path = Path(latest.get("video_path") or out / "video_final.mp4")

        prev1, prev2 = st.columns(2)
        with prev1:
            if thumb_path.exists():
                st.image(str(thumb_path), caption="Thumbnail atual", use_container_width=True)
        with prev2:
            if video_path.exists():
                st.video(str(video_path))

        st.subheader("4. Publicação")
        privacy = st.selectbox("Privacidade no envio", ["private", "unlisted", "public"], index=0)
        ack = st.checkbox(
            "Revisei áudio, visual, direitos dos arquivos usados, título, descrição e possíveis mudanças nas políticas do YouTube."
        )

        if st.button("🚀 ENVIAR AO YOUTUBE", use_container_width=True, disabled=not ack):
            try:
                if not video_path.exists():
                    raise FileNotFoundError("Renderize o vídeo antes de publicar.")
                with st.spinner("Enviando ao YouTube..."):
                    vid = upload_video(
                        video_path,
                        chosen_title,
                        description,
                        ROOT / cfg["youtube_client_secret"],
                        ROOT / cfg["youtube_token"],
                        privacy,
                        pkg.get("keywords", []),
                    )
                update_project(
                    project["id"],
                    youtube_video_id=vid,
                    status="publicado_" + privacy,
                    selected_title=chosen_title,
                    description=description,
                )
                st.success(f"Upload concluído. ID do vídeo: {vid}")
            except Exception as e:
                st.error(str(e))

        st.caption(f"Pasta do projeto: {out}")

with library_tab:
    st.subheader("Biblioteca local")
    st.write("Coloque arquivos reutilizáveis nestas pastas. Eles não são enviados ao GitHub automaticamente.")
    st.code(str(ROOT / "assets" / "backgrounds"), language=None)
    st.code(str(ROOT / "assets" / "ambient"), language=None)
    st.write(f"**Fundos encontrados:** {len(backgrounds())}")
    for p in backgrounds()[:20]:
        st.write("•", p.name)
    st.write(f"**Sons encontrados:** {len(ambient_sounds())}")
    for p in ambient_sounds()[:20]:
        st.write("•", p.name)

with history_tab:
    st.subheader("Histórico de projetos")
    rows = recent_projects(50)
    if rows:
        st.dataframe(
            [
                {k: r.get(k) for k in [
                    "id", "created_at", "theme", "audience", "duration_minutes",
                    "status", "similarity_score", "youtube_video_id"
                ]}
                for r in rows
            ],
            use_container_width=True,
            hide_index=True,
        )
        selected_id = st.number_input("Abrir projeto pelo ID", min_value=1, step=1)
        if st.button("Abrir registro"):
            row = get_project(int(selected_id))
            if row:
                st.json({k: v for k, v in row.items() if k != "package_json"})
                try:
                    st.json(json.loads(row.get("package_json") or "{}"))
                except Exception:
                    pass
            else:
                st.warning("Projeto não encontrado.")
    else:
        st.info("Ainda não há projetos.")

with rules_tab:
    st.subheader("Monitor de políticas")
    st.write(
        "O monitor registra mudanças nas páginas oficiais. Uma mudança de hash é um alerta para revisão, "
        "não uma interpretação automática da regra."
    )
    if st.button("🛡 VERIFICAR PÁGINAS OFICIAIS AGORA", type="primary"):
        with st.spinner("Consultando páginas oficiais do YouTube..."):
            st.session_state.policy_status = check_policy_changes()

    if st.session_state.policy_status:
        for key, item in st.session_state.policy_status.items():
            if item.get("ok"):
                icon = "🟠" if item.get("changed") else "🟢"
                st.write(
                    f"{icon} **{key}** — "
                    f"{'mudou desde a última captura' if item.get('changed') else 'sem mudança detectada'}"
                )
                st.caption(item.get("url"))
            else:
                st.write(f"🔴 **{key}** — não foi possível verificar")
                st.caption(item.get("error", ""))

with settings_tab:
    st.subheader("Configurações locais")
    c1, c2 = st.columns(2)
    with c1:
        models = list_ollama_models(cfg["ollama_url"])
        model = st.text_input("Modelo Ollama", cfg.get("ollama_model", "qwen3:4b"))
        ollama_url = st.text_input("Endereço Ollama", cfg.get("ollama_url", "http://localhost:11434"))
        ffmpeg_path = st.text_input("FFmpeg", cfg.get("ffmpeg_path", "ffmpeg"))
        if models:
            st.caption("Modelos detectados: " + ", ".join(models))
    with c2:
        voice_rate = st.slider("Velocidade da voz Windows", -10, 10, int(cfg.get("default_voice_rate", -1)))
        voice_volume = st.slider("Volume da voz", 0.01, 1.0, float(cfg.get("voice_volume", 0.10)), 0.01)
        ambient_volume = st.slider("Volume ambiente", 0.0, 1.0, float(cfg.get("ambient_volume", 0.62)), 0.01)
        tone_volume = st.slider("Volume Hz", 0.0, 0.30, float(cfg.get("tone_volume", 0.035)), 0.005)
        threshold = st.slider(
            "Limite de similaridade para regenerar",
            0.50, 0.95,
            float(cfg.get("similarity_regenerate_threshold", 0.78)),
            0.01,
        )

    if st.button("💾 SALVAR CONFIGURAÇÕES", type="primary"):
        cfg.update({
            "ollama_model": model.strip(),
            "ollama_url": ollama_url.strip(),
            "ffmpeg_path": ffmpeg_path.strip(),
            "default_voice_rate": voice_rate,
            "voice_volume": voice_volume,
            "ambient_volume": ambient_volume,
            "tone_volume": tone_volume,
            "similarity_regenerate_threshold": threshold,
        })
        save_config(cfg)
        st.success("Configurações salvas.")

st.divider()
st.caption("Modo Protagonista Studio v0.3 • processamento local • free-first • revisão humana antes da publicação")
