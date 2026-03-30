from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

from src.graph_agent import REPORT_PATH, run_monitoring
from src.sample_data import load_profiles


st.set_page_config(page_title="Agente de Monitoramento de Crédito", page_icon="📉", layout="wide")

st.title("Agente de Monitoramento de Crédito")
st.caption(
    "MVP com LangGraph para monitorar deterioração de perfil de crédito, priorizar risco e orientar ação preventiva."
)

profiles = load_profiles()

with st.sidebar:
    st.subheader("Monitoramento")
    selected_customer = st.selectbox("Cliente", profiles["customer_id"].tolist())
    run_button = st.button("Rodar fluxo de monitoramento")

if run_button or not REPORT_PATH.exists():
    report = run_monitoring(selected_customer)
else:
    report = json.loads(Path(REPORT_PATH).read_text(encoding="utf-8"))

profile = profiles.loc[profiles["customer_id"] == report["customer_id"]].iloc[0].to_dict()

metrics = st.columns(4)
metrics[0].metric("Cliente", profile["name"])
metrics[1].metric("Score atual", int(profile["current_score"]))
metrics[2].metric("Delta do score", report["score_delta"])
metrics[3].metric("Nível de risco", report["risk_level"])

left, right = st.columns([1.15, 1.0])

with left:
    st.subheader("Resumo analítico")
    st.warning(report["analyst_summary"])
    st.markdown("**Mensagem sugerida ao cliente**")
    st.write(report["customer_message"])
    st.markdown("**Ação recomendada**")
    st.write(report["recommended_action"])

with right:
    st.subheader("Perfil monitorado")
    st.json(profile)
    st.subheader("Flags de monitoramento")
    for flag in report["monitoring_flags"]:
        st.write(f"- {flag}")

st.subheader("Topologia do grafo")
st.markdown(
    """
    - `load_customer`
    - `compute_deltas`
    - `assess_risk`
    - `high_risk` ou `medium_low_risk`
    - `customer_message`
    - `analyst_summary`
    """
)

st.subheader("Artefato persistido")
st.code(Path(REPORT_PATH).read_text(encoding="utf-8"), language="json")
