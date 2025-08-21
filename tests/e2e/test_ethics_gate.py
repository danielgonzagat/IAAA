import httpx, time

BASE = "http://localhost:8000"

def test_ethics_blocks_when_vdot_positive():
    # força Lyapunov subir (vdot>0) e ativa enforce
    httpx.post(f"{BASE}/ethics/force", params={"vdot": 0.05})
    httpx.get(f"{BASE}/mode", params={"set":"shadow"})
    r = httpx.post(f"{BASE}/deploy/canary", params={"windows":1, "window_seconds":1, "enforce_ethics": True})
    assert r.status_code == 451
    detail = r.json()["detail"]
    assert detail["error"] == "ethics_block"
    assert detail["reason"] in ("Invariant","Risk>0","Truth/Eco/Consent","REU/CBF/Fairness","NoSacrificialCost","Unattested")

    # limpa e verifica que passa com enforce
    httpx.post(f"{BASE}/ethics/force", params={"reset": True})
    r2 = httpx.post(f"{BASE}/deploy/canary", params={"windows":1, "window_seconds":1, "enforce_ethics": True})
    assert r2.status_code == 200
    j = r2.json()
    assert "pca" in j and j["pca"]["allowed"] is True

def test_ethics_check_endpoint():
    r = httpx.get(f"{BASE}/ethics/check")
    assert r.status_code == 200
    snap = r.json()["snapshot"]
    for key in ("E","AI","G","dV_dt","truth_ece","risk"):
        assert key in snap

