"""
Ka-Nova Full Systems Diagnostic
Run before every paper run to verify all layers are operational.
Usage: python3 tests/test_full_diagnostic.py
"""
from model_phase3 import KaNovaModelPhase3
from agents.citizen import CitizenAgent
from agents.official import OfficialAgent
from agents.oversight import IIGAgent
import ast

def check_syntax():
    print("\n=== SYNTAX CHECK ===")
    files = [
        "model_phase3.py", "institutions/iig.py",
        "agents/oversight.py", "feedback/loops.py",
        "monitor/telegram_bot.py", "engine/elite_agents_v3.py",
        "engine/cves.py"
    ]
    all_pass = True
    for f in files:
        try:
            with open(f) as fh:
                ast.parse(fh.read())
            print(f"  PASS: {f}")
        except SyntaxError as e:
            print(f"  FAIL: {f} line {e.lineno} — {e.msg}")
            all_pass = False
    return all_pass

def check_model_init():
    print("\n=== MODEL INIT ===")
    mA = KaNovaModelPhase3(n_citizens=50, scenario="A", seed=42)
    mC = KaNovaModelPhase3(n_citizens=50, scenario="C", seed=42)
    print(f"  PASS: Model A — {len(mA.schedule.agents)} agents")
    print(f"  PASS: Model C — {len(mC.schedule.agents)} agents")
    return mA, mC

def check_iig_floor(m):
    print("\n=== IIG FLOOR ===")
    dropped = False
    for i in range(10):
        m.step()
        iig = m.shared_data.get("iig_effectiveness", 0)
        if iig < 0.25:
            print(f"  FAIL: IIG dropped to {iig:.4f} at year {i+1}")
            dropped = True
    if not dropped:
        iig_val = m.shared_data.get('iig_effectiveness', 0)
        print(f"  PASS: IIG held above floor (final: {iig_val:.4f})")
    return not dropped

def check_kpi_differentiation():
    print("\n=== KPI DIFFERENTIATION (50 steps) ===")
    mA = KaNovaModelPhase3(n_citizens=100, scenario="A", seed=42)
    mC = KaNovaModelPhase3(n_citizens=100, scenario="C", seed=42)
    for _ in range(50):
        mA.step()
        mC.step()
    cA = mA.shared_data.get("corruption_index")
    cC = mC.shared_data.get("corruption_index")
    tA = mA.shared_data.get("trust_index")
    tC = mC.shared_data.get("trust_index")
    kA = mA.shared_data.get("coup_risk")
    kC = mC.shared_data.get("coup_risk")
    print(f"  Corruption: A={cA:.4f} C={cC:.4f} {'PASS' if cA < cC else 'FAIL'}")
    print(f"  Trust:      A={tA:.4f} C={tC:.4f} {'PASS' if tA > tC else 'FAIL'}")
    print(f"  Coup risk:  A={kA:.4f} C={kC:.4f} {'PASS' if kA < kC else 'FAIL'}")
    return cA < cC and tA > tC and kA < kC

def check_elite_feedback(m):
    print("\n=== ELITE TO MESA FEEDBACK ===")
    budget = m.shared_data.get("elite_budget_impact")
    weights = m.shared_data.get("elite_ethnic_weights")
    history = m.shared_data.get("annual_history", [])
    print(f"  Budget impact: {budget}")
    print(f"  Annual history: {len(history)} entries")
    ok = budget is not None and weights is not None
    print(f"  {'PASS' if ok else 'FAIL'}: Elite to Mesa feedback")
    return ok

def check_external_layer(m):
    print("\n=== EXTERNAL LAYER ===")
    ext = m.shared_data.get("external", {})
    shocks = m.shared_data.get("total_shocks_fired", 0)
    print(f"  External keys: {list(ext.keys())[:4]}")
    print(f"  Shocks fired: {shocks}")
    ok = bool(ext)
    print(f"  {'PASS' if ok else 'FAIL'}: External layer")
    return ok

def check_social_media(m):
    print("\n=== SOCIAL MEDIA ===")
    sm = m.social_media.vpn_floor if hasattr(m, "social_media") else None
    print(f"  VPN floor: {sm}")
    ok = sm is not None
    print(f"  {'PASS' if ok else 'FAIL'}: Social media layer")
    return ok

if __name__ == "__main__":
    print("=" * 60)
    print("KA-NOVA FULL SYSTEMS DIAGNOSTIC")
    print("=" * 60)
    results = []
    results.append(check_syntax())
    mA, mC = check_model_init()
    results.append(check_iig_floor(mA))
    results.append(check_kpi_differentiation())
    results.append(check_elite_feedback(mA))
    results.append(check_external_layer(mA))
    results.append(check_social_media(mA))
    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"RESULT: {passed}/{total} checks passed")
    if passed == total:
        print("ALL SYSTEMS GO — safe to fire paper run")
    else:
        print("ISSUES FOUND — fix before paper run")
    print("=" * 60)
