import httpx, time

BASE = "http://localhost:8000"

def test_health_and_metrics():
    r = httpx.get(f"{BASE}/health")
    assert r.status_code == 200
    j = r.json()
    assert j["status"] == "ok"

    m = httpx.get(f"{BASE}/metrics").text
    assert "lemnisiana_vdot" in m
    assert "lemnisiana_oci" in m

def test_modes_and_guards():
    r = httpx.get(f"{BASE}/mode", params={"set":"shadow"})
    assert r.status_code == 200 and r.json()["mode"] == "shadow"

    r = httpx.get(f"{BASE}/mode", params={"set":"canary","traffic":0.1})
    assert r.status_code == 200
    assert r.json()["mode"] == "canary"
    assert r.json()["canary_traffic"] == 0.1

    r = httpx.get(f"{BASE}/guard/check")
    j = r.json()
    assert j["all_green"] is True

    # volta para main
    r = httpx.get(f"{BASE}/mode", params={"set":"main"})
    assert r.status_code == 200 and r.json()["mode"] == "main"

def test_stubs_endpoints():
    r = httpx.get(f"{BASE}/ednag/propose", params={"n": 2})
    assert r.status_code == 200
    assert r.json()["count"] == 2

    r = httpx.post(f"{BASE}/backpropamine/train", params={"steps": 5})
    assert r.status_code == 200
    js = r.json()
    assert js["loss_end"] < js["loss_start"]
