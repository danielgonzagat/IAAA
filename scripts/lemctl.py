#!/usr/bin/env python3
import argparse, json, os, sys, time, subprocess
from pathlib import Path
import httpx

BASE = os.environ.get("LEM_BASE", "http://localhost:8000")

def jprint(obj): print(json.dumps(obj, ensure_ascii=False, indent=2))

def req(method, path, **kw):
    url = f"{BASE}{path}"
    r = httpx.request(method, url, timeout=10, **kw)
    r.raise_for_status()
    return r

def cmd_health(_):
    jprint(req("GET","/health").json())

def cmd_mode(args):
    if args.set is None and args.traffic is None:
        jprint(req("GET","/mode").json())
    else:
        params={}
        if args.set: params["set"]=args.set
        if args.traffic is not None: params["traffic"]=args.traffic
        jprint(req("GET","/mode", params=params).json())

def cmd_guard(_):
    jprint(req("GET","/guard/check").json())

def cmd_ednag(args):
    jprint(req("GET","/ednag/propose", params={"n": args.n}).json())

def cmd_backprop(args):
    jprint(req("POST","/backpropamine/train", params={"steps": args.steps}).json())

def cmd_snapshot(args):
    ts = time.strftime("%Y%m%d-%H%M%S")
    tag = args.tag or ts
    root = Path("snapshots")/tag
    root.mkdir(parents=True, exist_ok=True)

    # salvar config atual
    cfg_src = Path("configs")/"default.yaml"
    if cfg_src.exists():
        cfg_dst = root/"default.yaml"
        cfg_dst.write_text(cfg_src.read_text())

    # salvar estado do orquestrador
    (root/"health.json").write_text(req("GET","/health").text)
    (root/"mode.json").write_text(req("GET","/mode").text)
    (root/"guard.json").write_text(req("GET","/guard/check").text)
    (root/"metrics.txt").write_text(req("GET","/metrics").text)

    print(f"OK: snapshot salvo em {root}")

def cmd_snapshot_list(_):
    snaps = sorted([p.name for p in Path("snapshots").glob("*") if p.is_dir()])
    jprint({"snapshots": snaps})

def cmd_snapshot_restore(args):
    tag = args.tag
    root = Path("snapshots")/tag
    cfg = root/"default.yaml"
    if not root.exists() or not cfg.exists():
        print(f"ERRO: snapshot '{tag}' inválido (sem default.yaml).", file=sys.stderr)
        sys.exit(1)
    # restaura config
    Path("configs")/"default.yaml"
    (Path("configs")/"default.yaml").write_text(cfg.read_text())
    print("Config restaurada. Reiniciando orchestrator…")
    # requer docker compose instalado no host:
    subprocess.call("docker compose restart orchestrator", shell=True)

def main():
    p = argparse.ArgumentParser(prog="lemctl", description="CLI Lemnisiana")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("health"); s.set_defaults(func=cmd_health)

    s = sub.add_parser("mode")
    s.add_argument("--set", choices=["main","shadow","canary"])
    s.add_argument("--traffic", type=float)
    s.set_defaults(func=cmd_mode)

    s = sub.add_parser("guard"); s.set_defaults(func=cmd_guard)

    s = sub.add_parser("ednag"); s.add_argument("-n", type=int, default=2); s.set_defaults(func=cmd_ednag)

    s = sub.add_parser("backprop"); s.add_argument("--steps", type=int, default=5); s.set_defaults(func=cmd_backprop)

    s = sub.add_parser("snapshot"); s.add_argument("--tag"); s.set_defaults(func=cmd_snapshot)
    s = sub.add_parser("snapshots"); s.set_defaults(func=cmd_snapshot_list)
    s = sub.add_parser("restore"); s.add_argument("--tag", required=True); s.set_defaults(func=cmd_snapshot_restore)

    args = p.parse_args()
    try:
        args.func(args)
    except httpx.HTTPStatusError as e:
        print(f"HTTP {e.response.status_code}: {e.response.text}", file=sys.stderr); sys.exit(2)

if __name__ == "__main__":
    main()
