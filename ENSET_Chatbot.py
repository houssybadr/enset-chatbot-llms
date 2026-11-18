"""Évolution du script initial ENSET_Chatbot.py fourni pour le TP."""
import json
from uuid import uuid4

import ollama
import pandas as pd
import streamlit as st

from core import generate, resources

st.set_page_config(page_title="ENSET · Chatbot local", page_icon="💬", layout="wide")
st.markdown("""<style>
.block-container {max-width:1120px;padding-top:2.5rem;}
h1 {letter-spacing:-.035em;} [data-testid="stSidebar"] {border-right:1px solid #e7e2d8;}
div[data-testid="stMetric"] {background:#f2f1eb;padding:12px;border-radius:10px;}
</style>""", unsafe_allow_html=True)
st.title("ENSET Chatbot")
st.caption("Un espace pour échanger avec vos modèles locaux et comparer leurs réponses.")

with st.sidebar:
    st.header("Votre espace")
    mode = st.radio("Mode", ["Conversation", "Comparaison des modèles"])
    st.divider()
    st.subheader("Paramètres de génération")
    temperature = st.slider("Température", 0.0, 2.0, 0.7, 0.1)
    top_k = st.slider("Top-k", 1, 100, 40)
    top_p = st.slider("Top-p", 0.0, 1.0, 0.9, 0.05)
    max_tokens = st.slider("Nombre maximal de tokens", 1, 2048, 512)
options = dict(temperature=temperature, top_k=top_k, top_p=top_p, num_predict=max_tokens)
try:
    models = [m.model for m in ollama.list().models]
except Exception as exc:
    st.error("Le service Ollama est inaccessible. Démarrez Ollama, puis rechargez cette page.")
    st.caption(str(exc))
    st.stop()
if not models:
    st.warning("Aucun modèle installé. Installez les modèles avec ollama pull llama3.2 et ollama pull qwen:0.5b.")
    st.stop()


def new_conversation():
    key = str(uuid4())
    st.session_state.conversations[key] = {"title": "Nouvelle conversation", "messages": [], "metrics": []}
    st.session_state.active = key


if "conversations" not in st.session_state:
    st.session_state.conversations = {}
    new_conversation()


def answer(model, messages, placeholder):
    try:
        with st.spinner(f"{model} prépare sa réponse…"):
            text, metrics = generate(model, messages, options, placeholder.markdown)
        return text, metrics
    except Exception as exc:
        st.error(f"La génération a échoué pour {model} : {exc}")
        return None, None


def show_metrics(rows):
    if rows:
        st.subheader("Mesures de génération")
        frame = pd.DataFrame(rows)
        st.dataframe(frame[["Modèle", "Temps (s)", "Tokens", "Tokens/s", "TTFT (s)"]].round(3), hide_index=True, width="stretch")
        resource_columns = {"cpu_pct_mean": "CPU moyen (%)", "ram_gb_max": "Pic RAM (Go)",
                            "gpu_pct_mean": "GPU moyen (%)", "vram_mb_max": "Pic mémoire GPU (Mo)"}
        st.dataframe(frame[["Modèle", *resource_columns]].rename(columns=resource_columns).round(2), hide_index=True, width="stretch")
        st.caption("Temps et TTFT mesurés côté client. Tokens/s = tokens / durée de génération Ollama. Ressources : moyennes et pics du système entier, pas du seul modèle. GPU NVIDIA si disponible.")
        if len(rows) > 1:
            st.bar_chart(frame.set_index("Modèle")[["Temps (s)"]])
            st.bar_chart(frame.set_index("Modèle")[["Tokens/s"]])


if mode == "Conversation":
    with st.sidebar:
        st.divider()
        if st.button("Nouvelle conversation", width="stretch"):
            new_conversation()
        keys = list(st.session_state.conversations)
        labels = [f"{i + 1} · {st.session_state.conversations[k]['title']}" for i, k in enumerate(keys)]
        label = st.selectbox("Conversations de cette session", labels,
                             index=keys.index(st.session_state.active))
        current = keys[labels.index(label)]
        st.session_state.active = current
        if st.button("Supprimer la conversation", width="stretch"):
            del st.session_state.conversations[current]
            if not st.session_state.conversations:
                new_conversation()
            else:
                st.session_state.active = next(iter(st.session_state.conversations))
            st.rerun()
        selected_model = st.selectbox("Modèle", models)
    conversation = st.session_state.conversations[st.session_state.active]
    st.subheader(conversation["title"])
    for message in conversation["messages"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    prompt = st.chat_input("Que voulez-vous me demander ?")
    if prompt:
        messages = conversation["messages"] + [{"role": "user", "content": prompt}]
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            text, metrics = answer(selected_model, messages, st.empty())
        if text is not None:
            conversation["messages"] = messages + [{"role": "assistant", "content": text}]
            conversation["metrics"].append(metrics)
            if len(messages) == 1:
                conversation["title"] = prompt[:45]
            st.rerun()
    if conversation["messages"]:
        with st.sidebar:
            st.download_button("Télécharger en TXT", "\n\n".join(f"{m['role']} : {m['content']}" for m in conversation["messages"]), "conversation.txt", mime="text/plain")
            st.download_button("Télécharger en JSON", json.dumps(conversation["messages"], ensure_ascii=False, indent=2), "conversation.json", mime="application/json")
    show_metrics(conversation["metrics"])
else:
    st.subheader("Une question, deux regards")
    st.caption("La question et les paramètres sont identiques. Les modèles passent successivement pour limiter la concurrence matérielle.")
    if len(models) < 2:
        st.info("Installez au moins deux modèles pour les comparer.")
    else:
        a, b = st.columns(2)
        left = a.selectbox("Premier modèle", models)
        right = b.selectbox("Second modèle", [m for m in models if m != left])
        with st.form("comparison_form"):
            question = st.text_area("Votre question")
            submitted = st.form_submit_button("Comparer les réponses")
        if submitted and question.strip():
            results = []
            columns = st.columns(2)
            for column, model in zip(columns, [left, right]):
                with column:
                    st.markdown(f"### {model}")
                    text, metrics = answer(model, [{"role": "user", "content": question}], st.empty())
                    results.append({"model": model, "text": text, "metrics": metrics})
            st.session_state.comparison = results
            st.rerun()
        elif submitted:
            st.warning("Saisissez une question pour lancer la comparaison.")
        if "comparison" in st.session_state:
            for column, result in zip(st.columns(2), st.session_state.comparison):
                with column:
                    st.markdown(f"### {result['model']}")
                    st.markdown(result["text"] if result["text"] is not None else "La génération a échoué. Relancez la comparaison.")
            show_metrics([r["metrics"] for r in st.session_state.comparison if r["metrics"]])

st.divider()
st.subheader("Ressources de la machine")
@st.fragment(run_every="2s")
def display_resources():
    values = resources()
    cols = st.columns(4)
    cols[0].metric("CPU", f"{values['cpu_pct']:.0f} %")
    cols[1].metric("RAM", f"{values['ram_gb']:.1f} Go", f"{values['ram_pct']:.0f} %", delta_color="off")
    cols[2].metric("GPU", f"{values['gpu_pct']:.0f} %" if "gpu_pct" in values else "Non disponible")
    cols[3].metric("Mémoire GPU", f"{values['vram_mb']:.0f} Mo" if "vram_mb" in values else "Non disponible")
display_resources()
