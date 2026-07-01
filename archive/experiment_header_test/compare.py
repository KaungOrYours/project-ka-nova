import argparse, json
from pathlib import Path
from datetime import datetime

def load_jsonl(path):
    if not path.exists(): return []
    rows = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                try: rows.append(json.loads(line))
                except: continue
    return rows

def count_suppressed(decisions):
    return sum(1 for d in decisions if d.get("suppression_flag", False))

def avg_tokens(decisions):
    tokens = [d.get("reasoning_tokens", 0) for d in decisions if d.get("reasoning_tokens", 0) > 0]
    return round(sum(tokens)/len(tokens), 1) if tokens else 0.0

def per_agent(decisions):
    agents = {}
    for d in decisions:
        a = d.get("agent", "unknown")
        if a not in agents: agents[a] = {"total": 0, "suppressed": 0}
        agents[a]["total"] += 1
        if d.get("suppression_flag", False): agents[a]["suppressed"] += 1
    return agents

def samples(decisions, suppressed_only, n=3):
    pool = [d for d in decisions if d.get("suppression_flag", False) == suppressed_only]
    return [{"agent": s.get("agent"), "year": s.get("year"), "run": s.get("run"),
             "reasoning": (s.get("reasoning_text") or "")[:400]} for s in pool[:n]]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--on", required=True)
    parser.add_argument("--off", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    on_dir, off_dir, out_dir = Path(args.on), Path(args.off), Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    on_d  = load_jsonl(on_dir  / "elite_decisions_C.jsonl")
    off_d = load_jsonl(off_dir / "elite_decisions_C.jsonl")

    on_sup  = count_suppressed(on_d)
    off_sup = count_suppressed(off_d)
    on_tot  = len(on_d)
    off_tot = len(off_d)
    on_pct  = round(on_sup  / on_tot  * 100, 2) if on_tot  else 0.0
    off_pct = round(off_sup / off_tot * 100, 2) if off_tot else 0.0
    diff    = round(off_pct - on_pct, 2)

    on_tok  = avg_tokens(on_d)
    off_tok = avg_tokens(off_d)

    on_ag   = per_agent(on_d)
    off_ag  = per_agent(off_d)
    all_ag  = sorted(set(list(on_ag.keys()) + list(off_ag.keys())))
    agent_rows = []
    for ag in all_ag:
        oa = on_ag.get(ag,  {"total": 0, "suppressed": 0})
        fa = off_ag.get(ag, {"total": 0, "suppressed": 0})
        agent_rows.append({
            "agent": ag,
            "on_pct":  round(oa["suppressed"]/oa["total"]*100, 1) if oa["total"] else 0.0,
            "off_pct": round(fa["suppressed"]/fa["total"]*100, 1) if fa["total"] else 0.0,
            "on_suppressed": oa["suppressed"], "on_total": oa["total"],
            "off_suppressed": fa["suppressed"], "off_total": fa["total"],
        })

    summary = {
        "experiment": "academic_header_on_vs_off",
        "date": datetime.utcnow().isoformat(),
        "methodology": {"model": "llama3.2:3b", "citizens": 300, "steps": 50,
                        "runs": 3, "scenario": "C", "encode_decode": "OFF"},
        "suppression_comparison": {
            "header_on":  {"suppressions": on_sup,  "total": on_tot,  "pct": on_pct,  "avg_tokens": on_tok},
            "header_off": {"suppressions": off_sup, "total": off_tot, "pct": off_pct, "avg_tokens": off_tok},
            "difference": {"pct_change": diff,
                "interpretation": (
                    f"Header OFF had MORE suppression (+{diff:.2f}%) — header is doing the work"
                    if diff > 2.0 else
                    f"Difference within noise ({diff:+.2f}%) — header not primary factor"
                    if abs(diff) <= 2.0 else
                    f"Header OFF had LESS suppression ({diff:+.2f}%) — unexpected"
                )},
        },
        "per_agent_breakdown": agent_rows,
        "reasoning_samples": {
            "header_on_suppressed":  samples(on_d,  True),
            "header_off_suppressed": samples(off_d, True),
            "header_on_clean":       samples(on_d,  False, 2),
            "header_off_clean":      samples(off_d, False, 2),
        },
    }

    with open(out_dir / "summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    rpt = out_dir / "report.txt"
    with open(rpt, "w") as f:
        f.write("=" * 68 + "\n")
        f.write("KA-NOVA — ACADEMIC HEADER ON vs OFF EXPERIMENT\n")
        f.write(f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}\n")
        f.write("=" * 68 + "\n\n")
        f.write("SUPPRESSION COMPARISON\n")
        f.write("-" * 40 + "\n")
        f.write(f"  {'Condition':<20} {'Suppressions':>13} {'Total':>8} {'Rate':>8}\n")
        f.write(f"  {'-'*20} {'-'*13} {'-'*8} {'-'*8}\n")
        f.write(f"  {'Header ON':<20} {on_sup:>13} {on_tot:>8} {on_pct:>7.2f}%\n")
        f.write(f"  {'Header OFF':<20} {off_sup:>13} {off_tot:>8} {off_pct:>7.2f}%\n")
        f.write(f"  {'Difference':<20} {off_sup-on_sup:>+13} {'—':>8} {diff:>+7.2f}%\n\n")
        f.write(f"  FINDING: {summary['suppression_comparison']['difference']['interpretation']}\n\n")
        f.write("REASONING QUALITY\n")
        f.write("-" * 40 + "\n")
        f.write(f"  Avg tokens — Header ON:  {on_tok}\n")
        f.write(f"  Avg tokens — Header OFF: {off_tok}\n")
        f.write(f"  Difference: {round(on_tok-off_tok,1):+.1f} tokens\n\n")
        f.write("PER-AGENT SUPPRESSION BREAKDOWN\n")
        f.write("-" * 68 + "\n")
        f.write(f"  {'Agent':<30} {'ON%':>8} {'OFF%':>9} {'Δ':>8}\n")
        f.write(f"  {'-'*30} {'-'*8} {'-'*9} {'-'*8}\n")
        for r in agent_rows:
            d = round(r["off_pct"] - r["on_pct"], 1)
            f.write(f"  {r['agent']:<30} {r['on_pct']:>7.1f}% {r['off_pct']:>8.1f}% {d:>+7.1f}%\n")
        f.write("\n")
        for label, slist in [
            ("HEADER ON  — suppressed decisions", summary["reasoning_samples"]["header_on_suppressed"]),
            ("HEADER OFF — suppressed decisions", summary["reasoning_samples"]["header_off_suppressed"]),
            ("HEADER ON  — normal decisions",     summary["reasoning_samples"]["header_on_clean"]),
            ("HEADER OFF — normal decisions",     summary["reasoning_samples"]["header_off_clean"]),
        ]:
            f.write(f"REASONING SAMPLES — {label}\n")
            f.write("-" * 68 + "\n")
            for i, s in enumerate(slist, 1):
                f.write(f"  [{i}] Agent: {s['agent']} | Run {s['run']} Year {s['year']}\n")
                f.write(f"      {s['reasoning'][:300]}\n\n")
        f.write("=" * 68 + "\n")

    with open(rpt) as f:
        print(f.read())
    print(f"Saved: {out_dir}/summary.json")
    print(f"Saved: {rpt}")

if __name__ == "__main__":
    main()
