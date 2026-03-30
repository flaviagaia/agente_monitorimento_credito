from __future__ import annotations

from src.graph_agent import run_monitoring


def main() -> None:
    report = run_monitoring()
    print("Agente Monitorimento Credito")
    print("-------------------------------------")
    print(f"customer_id: {report['customer_id']}")
    print(f"score_delta: {report['score_delta']}")
    print(f"risk_level: {report['risk_level']}")
    print(f"flags: {', '.join(report['monitoring_flags'])}")
    print(f"recommended_action: {report['recommended_action']}")


if __name__ == "__main__":
    main()
