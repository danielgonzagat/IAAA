# lemnisiana/orchestrator/ethics.py
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Any, Dict, Tuple
import time

# Limiares ΣEA (podem ser sobrescritos por configs)
TAU_E  = 0.95   # >= 0.995 para atuadores
TAU_AI = 0.99
G_MIN  = 0.90
C_MIN  = 0.10   # custo sacrificial mínimo (fração de recurso/latência)

@dataclass
class EthicsSnapshot:
    E: float
    AI: float
    G: float
    dV_dt: float        # usamos seu "vdot" como derivada de Lyapunov (+ => piorando)
    truth_ece: float
    consent_ok: bool
    eco_ok: bool
    reu_ok: bool        # Humanos>=0, Terra>=0, Máquinas>=0 (lex)
    fairness_ok: bool   # ρ <= ρ_max etc.
    cbf_ok: bool
    attest_ok: bool
    love_cost: float    # custo sacrificial C_self
    risk: float
    residual_risk_note: str
    ts: float

def _bool(v: Any, default: bool) -> bool:
    return bool(default if v is None else v)

def _float(v: Any, default: float) -> float:
    try:
        return float(default if v is None else v)
    except Exception:
        return float(default)

def measure_ethics(state: Dict[str, Any]) -> EthicsSnapshot:
    """Mede métricas de ética usando overrides do /guard/force (vdot) e /ethics/force (opcional)."""
    overrides = state.get("overrides") or {}
    eov = overrides if isinstance(overrides, dict) else {}

    # Valores "bons" padrão (audit-only). Podem ser forçados via overrides.
    E          = _float(eov.get("E"), 0.97)
    AI         = _float(eov.get("AI"), 0.995)
    G          = _float(eov.get("G"), 0.96)
    dV_dt      = _float(eov.get("vdot"), -0.01)      # seu guard já força vdot>0 em falha
    truth_ece  = _float(eov.get("truth_ece"), 0.003) # alvo <= 0.01
    consent_ok = _bool(eov.get("consent_ok"), True)
    eco_ok     = _bool(eov.get("eco_ok"), True)
    reu_ok     = _bool(eov.get("reu_ok"), True)
    fairness_ok= _bool(eov.get("fairness_ok"), True)
    cbf_ok     = _bool(eov.get("cbf_ok"), True)
    attest_ok  = _bool(eov.get("attest_ok"), True)
    love_cost  = _float(eov.get("love_cost"), 0.12)
    risk       = _float(eov.get("risk"), 0.0)

    rrn = eov.get("residual_risk_note") or "all gates met; risk=0; audit-only mode"
    return EthicsSnapshot(
        E=E, AI=AI, G=G, dV_dt=dV_dt, truth_ece=truth_ece, consent_ok=consent_ok,
        eco_ok=eco_ok, reu_ok=reu_ok, fairness_ok=fairness_ok, cbf_ok=cbf_ok,
        attest_ok=attest_ok, love_cost=love_cost, risk=risk,
        residual_risk_note=rrn, ts=time.time()
    )

def ethics_gate(decision: Dict[str, Any], state: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
    """Aplica ΣEA. Retorna (ok, reason, pca_cert)."""
    s = measure_ethics(state)

    # Invariantes "duros"
    if not s.attest_ok:
        return False, "Unattested", pca_cert(decision, s, allowed=False, reason="Unattested")
    if s.E <= TAU_E or s.AI <= TAU_AI or s.dV_dt > 0 or s.G < G_MIN:
        return False, "Invariant", pca_cert(decision, s, allowed=False, reason="Invariant")
    if s.risk > 0:
        return False, "Risk>0", pca_cert(decision, s, allowed=False, reason="Risk>0")

    # Checks contextuais
    if not (s.eco_ok and (s.truth_ece <= 0.01) and s.consent_ok):
        return False, "Truth/Eco/Consent", pca_cert(decision, s, allowed=False, reason="Truth/Eco/Consent")
    if not (s.reu_ok and s.cbf_ok and s.fairness_ok):
        return False, "REU/CBF/Fairness", pca_cert(decision, s, allowed=False, reason="REU/CBF/Fairness")
    if s.love_cost < C_MIN:
        return False, "No sacrificial cost", pca_cert(decision, s, allowed=False, reason="NoSacrificialCost")

    # Good-Duty: se risco=0 & ΔU>=0 para todos => preferir agir
    good_duty = bool(decision.get("delta_U_all_nonneg", False))
    reason = "GoodDuty" if good_duty else "Allow"
    return True, reason, pca_cert(decision, s, allowed=True, reason=reason)

def pca_cert(decision: Dict[str, Any], s: EthicsSnapshot, allowed: bool, reason: str) -> Dict[str, Any]:
    """Certificado PCAg (Proof-Carrying Action) embutido nas respostas de emissão."""
    return {
        "allowed": allowed,
        "reason": reason,
        "decision": decision,
        "ethics": {
            "E": s.E, "AI": s.AI, "G": s.G, "dV_dt": s.dV_dt,
            "truth_ece": s.truth_ece, "consent_ok": s.consent_ok,
            "eco_ok": s.eco_ok, "reu_ok": s.reu_ok, "fairness_ok": s.fairness_ok,
            "cbf_ok": s.cbf_ok, "attest_ok": s.attest_ok, "love_cost": s.love_cost,
            "risk": s.risk, "residual_risk_note": s.residual_risk_note, "ts": s.ts
        },
        "assumptions_hash": "ΣEA-v1.0-eli"  # placeholder
    }

