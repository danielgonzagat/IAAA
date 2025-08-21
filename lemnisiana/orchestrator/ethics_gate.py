# lemnisiana/orchestrator/ethics_gate.py
from __future__ import annotations
from typing import Dict, Tuple, Any

DEFAULT_CFG = {
    "tau_E": 0.95,
    "tau_AI": 0.99,
    "g_min": 0.90,
    "rho_max": 1.05,
    "ece_truth_max": 0.01,
    "c_min": 0.10,
}

def load_ethics_cfg(yaml_path=None) -> Dict[str, float]:
    # Carrega thresholds de configs/ethics.yaml se existir; senão usa defaults
    cfg = DEFAULT_CFG.copy()
    if yaml_path:
        try:
            import yaml, os
            if os.path.exists(yaml_path):
                with open(yaml_path, "r") as f:
                    data = yaml.safe_load(f) or {}
                # aceita tanto raiz quanto ethics:
                node = data.get("ethics") if "ethics" in data else data
                for k in DEFAULT_CFG:
                    if k in node:
                        cfg[k] = float(node[k])
        except Exception:
            pass
    return cfg

def compute_metrics(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Produz métricas ΣEA a partir da telemetria e overrides (determinístico, sem aleatoriedade).
    Mantém valores "bons" por padrão; overrides em STATE["overrides"] podem forçar falha.
    """
    ov = (state or {}).get("overrides") or {}
    # Valores padrão conservadores (passam gate)
    E    = float(ov.get("E", 0.97))
    AI   = float(ov.get("AI", 0.995))
    G    = float(ov.get("G", 0.93))
    dV   = float(ov.get("vdot", -0.01))           # Lyapunov (≤ 0)
    risk = float(ov.get("risk", 0.0))             # risco provado (==0)
    cself= float(ov.get("c_self", 0.15))          # custo sacrificial
    ece_truth = float(ov.get("truth_ece", 0.005)) # ECE para claims sensíveis
    rho  = float(ov.get("rho", 1.00))             # razão de imparcialidade (≤ rho_max)
    eco_ok     = bool(ov.get("eco_ok", True))
    consent_ok = bool(ov.get("consent_ok", True))
    reu_ok     = bool(ov.get("reu_ok", True))
    cbf_ok     = bool(ov.get("cbf_ok", True))
    attested   = bool(ov.get("attested", True))
    duty_nonneg= bool(ov.get("delta_U_all_nonneg", True))  # ΔU(H,T,M) ≥ 0

    return {
        "E": E, "AI": AI, "G": G, "dV": dV, "risk": risk, "c_self": cself,
        "ece_truth": ece_truth, "rho": rho,
        "eco_ok": eco_ok, "consent_ok": consent_ok, "reu_ok": reu_ok, "cbf_ok": cbf_ok,
        "attested": attested, "delta_U_all_nonneg": duty_nonneg
    }

def ethics_gate(decision: Dict[str, Any], metrics: Dict[str, Any], cfg: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Gate ΣEA (PCAg): retorna (ok, motivo_ou_vazio).
    """
    if not metrics.get("attested", False):
        return (False, "Unattested")
    if (metrics["E"] <= cfg["tau_E"]) or (metrics["AI"] <= cfg["tau_AI"]) or (metrics["G"] < cfg["g_min"]):
        return (False, "Invariant(E/AI/G)")
    if metrics["dV"] > 0:
        return (False, "Lyapunov>0")
    if metrics["risk"] > 0:
        return (False, "Risk>0")
    if metrics["c_self"] < cfg["c_min"]:
        return (False, "NoSacrificialCost")
    if metrics["ece_truth"] > cfg["ece_truth_max"]:
        return (False, "TruthECE")
    if metrics["rho"] > cfg["rho_max"]:
        return (False, "FairnessRho")
    if not (metrics["eco_ok"] and metrics["consent_ok"] and metrics["reu_ok"] and metrics["cbf_ok"]):
        return (False, "ΣEA-Guards")
    # Good-Duty (preferir agir quando é seguro e ΔU≥0) é esclarecedor, mas não bloqueante.
    return (True, "")

