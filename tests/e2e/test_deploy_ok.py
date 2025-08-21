import httpx, time
BASE = "http://localhost:8000"
def test_canary_promotes_to_main():
    httpx.post(f"{BASE}/guard/force", params={"reset": True})
    httpx.get(f"{BASE}/mode", params={"set":"shadow"})
    r = httpx.post(f"{BASE}/deploy/canary", params={"traffic":0.1,"windows":2,"window_seconds":3})
    assert r.status_code == 200
    time.sleep(7)  # > 2*3s
    st = httpx.get(f"{BASE}/deploy/status").json()
    assert st["state"]["mode"] == "main"
