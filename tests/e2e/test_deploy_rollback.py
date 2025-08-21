import httpx, time
BASE = "http://localhost:8000"
def test_canary_rollback_on_guard_fail():
    httpx.post(f"{BASE}/guard/force", params={"vdot_v": 0.05})  # força falha
    httpx.get(f"{BASE}/mode", params={"set":"shadow"})
    r = httpx.post(f"{BASE}/deploy/canary", params={"windows":2,"window_seconds":2})
    assert r.status_code == 200
    time.sleep(5)
    st = httpx.get(f"{BASE}/deploy/status").json()
    assert st["state"]["mode"] == "shadow"  # rollback efetuado
    httpx.post(f"{BASE}/guard/force", params={"reset": True})
