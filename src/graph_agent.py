from __future__ import annotations

import json
from pathlib import Path
from typing import Literal, TypedDict

from langgraph.graph import END, START, StateGraph

from .sample_data import load_profiles


PROCESSED_DIR = Path(__file__).resolve().parents[1] / "data" / "processed"
REPORT_PATH = PROCESSED_DIR / "credit_monitoring_report.json"


class MonitoringState(TypedDict, total=False):
    customer_id: str
    customer_profile: dict
    score_delta: int
    utilization_delta: int
    risk_level: str
    monitoring_flags: list[str]
    recommended_action: str
    customer_message: str
    analyst_summary: str


def load_customer_node(state: MonitoringState) -> MonitoringState:
    profiles = load_profiles()
    row = profiles.loc[profiles["customer_id"] == state["customer_id"]]
    if row.empty:
        raise ValueError(f"Customer {state['customer_id']} not found.")
    profile = row.iloc[0].to_dict()
    return {"customer_profile": profile}


def compute_deltas_node(state: MonitoringState) -> MonitoringState:
    profile = state["customer_profile"]
    return {
        "score_delta": int(profile["current_score"]) - int(profile["previous_score"]),
        "utilization_delta": int(profile["credit_utilization_pct"]) - int(profile["previous_utilization_pct"]),
    }


def assess_risk_node(state: MonitoringState) -> MonitoringState:
    profile = state["customer_profile"]
    score_delta = state["score_delta"]
    utilization = int(profile["credit_utilization_pct"])
    late_payments = int(profile["recent_late_payments"])
    negative_records = int(profile["negative_records"])

    flags: list[str] = []
    risk_points = 0

    if score_delta <= -40:
        flags.append("queda_relevante_de_score")
        risk_points += 3
    elif score_delta < 0:
        flags.append("queda_leve_de_score")
        risk_points += 1

    if utilization >= 80:
        flags.append("utilizacao_critica")
        risk_points += 3
    elif utilization >= 60:
        flags.append("utilizacao_alta")
        risk_points += 2

    if late_payments >= 3:
        flags.append("inadimplencia_recente_relevante")
        risk_points += 3
    elif late_payments > 0:
        flags.append("atrasos_recentes")
        risk_points += 1

    if negative_records > 0:
        flags.append("registro_negativo")
        risk_points += 2

    if risk_points >= 7:
        risk_level = "alto"
    elif risk_points >= 4:
        risk_level = "medio"
    else:
        risk_level = "baixo"

    return {"risk_level": risk_level, "monitoring_flags": flags}


def route_action(state: MonitoringState) -> Literal["high_risk", "medium_low_risk"]:
    return "high_risk" if state["risk_level"] == "alto" else "medium_low_risk"


def high_risk_action_node(state: MonitoringState) -> MonitoringState:
    profile = state["customer_profile"]
    return {
        "recommended_action": (
            f"Abertura imediata de monitoramento ativo para {profile['name']}, "
            "com contato preventivo, revisão de limite e avaliação da política de cobrança."
        )
    }


def medium_low_risk_action_node(state: MonitoringState) -> MonitoringState:
    profile = state["customer_profile"]
    return {
        "recommended_action": (
            f"Monitoramento assistido para {profile['name']}, com comunicação educativa e reavaliação no próximo ciclo."
        )
    }


def customer_message_node(state: MonitoringState) -> MonitoringState:
    profile = state["customer_profile"]
    score_delta = state["score_delta"]
    tone = (
        "Percebemos uma piora relevante no seu perfil recente."
        if state["risk_level"] == "alto"
        else "Identificamos sinais que merecem atenção no seu perfil."
    )
    message = (
        f"{tone} Seu score atual está em {int(profile['current_score'])}, "
        f"com variação de {score_delta} pontos em relação ao ciclo anterior. "
        f"Os principais fatores observados foram utilização de crédito em {int(profile['credit_utilization_pct'])}% "
        f"e {int(profile['recent_late_payments'])} atraso(s) recente(s). "
        "Nossa recomendação é revisar seu nível de utilização e manter os próximos pagamentos em dia."
    )
    return {"customer_message": message}


def analyst_summary_node(state: MonitoringState) -> MonitoringState:
    profile = state["customer_profile"]
    summary = (
        f"Cliente {profile['customer_id']} ({profile['name']}) no segmento {profile['segment']} "
        f"apresenta score {int(profile['current_score'])} com delta de {state['score_delta']} pontos. "
        f"Flags: {', '.join(state['monitoring_flags']) if state['monitoring_flags'] else 'nenhuma'}. "
        f"Nível de risco: {state['risk_level']}. "
        f"Ação recomendada: {state['recommended_action']}"
    )
    return {"analyst_summary": summary}


def build_monitoring_graph():
    graph = StateGraph(MonitoringState)
    graph.add_node("load_customer", load_customer_node)
    graph.add_node("compute_deltas", compute_deltas_node)
    graph.add_node("assess_risk", assess_risk_node)
    graph.add_node("high_risk", high_risk_action_node)
    graph.add_node("medium_low_risk", medium_low_risk_action_node)
    graph.add_node("customer_message", customer_message_node)
    graph.add_node("analyst_summary", analyst_summary_node)

    graph.add_edge(START, "load_customer")
    graph.add_edge("load_customer", "compute_deltas")
    graph.add_edge("compute_deltas", "assess_risk")
    graph.add_conditional_edges(
        "assess_risk",
        route_action,
        {
            "high_risk": "high_risk",
            "medium_low_risk": "medium_low_risk",
        },
    )
    graph.add_edge("high_risk", "customer_message")
    graph.add_edge("medium_low_risk", "customer_message")
    graph.add_edge("customer_message", "analyst_summary")
    graph.add_edge("analyst_summary", END)
    return graph.compile()


def run_monitoring(customer_id: str = "MON-1002") -> dict:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    graph = build_monitoring_graph()
    result = graph.invoke({"customer_id": customer_id})
    REPORT_PATH.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return result
