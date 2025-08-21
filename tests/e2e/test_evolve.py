import httpx
BASE = "http://localhost:8000"
def test_evolve_shadow_transition():
    r = httpx.post(f"{BASE}/evolve", params={"steps":2,"n_candidates":3,"auto":True,"force":True})
    assert r.status_code == 200
    data = r.json()
    assert data["state"]["mode"] == "shadow"
