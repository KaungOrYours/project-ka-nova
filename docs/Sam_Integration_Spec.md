# Ka-Nova Phase 3 — Elite Agent Integration Spec
> For: Sam | Role: LLM Architecture and Agent Validation Lead
> From: Kaung Htet | Date: June 15, 2026
> Deadline: End of July 2026

---

## 1. Files You Own

| You own | Do not touch |
|---|---|
| `engine/elite_agents_v3.py` | `model_phase3.py` |
| `engine/cves.py` | `engine/external_layer.py` |
| | `engine/social_media.py` |
| | `engine/elite_agents.py` |
| | `config/constitution.py` |
| | `agents/citizen.py` |
| | `run_phase3.py` |

---

## 2. elite_agents_v3.py — Interface Contract

### Class and import alias
```python
class EliteAgentLayerV3:  # exact name — imported with alias in model_phase3
    ...
```

### Constructor
```python
def __init__(self, use_llm: bool = False):
    self.use_llm = use_llm  # MUST exist — model reads this directly
```

### step() — locked signature
```python
def step(self, shared_data: dict, year: int, scenario: str) -> None:
```

### shared_data keys

Reads:
- `corruption_index`, `trust_index`, `coup_risk`, `gdp_growth`
- `ethnic_tension`, `iig_effectiveness`, `vpn_floor`
- `social_media_openness`, `china_influence`

Writes (CRITICAL):
- `elite_coup_signal` (bool) — read immediately after step() in model_phase3
- `elite_decisions` (dict) — summary of all agent decisions

### The 7 elite agents

| Agent | Scenario |
|---|---|
| President | A |
| Chancellor | A |
| Chief Justice | A |
| Finance Minister | A and C |
| IIG Director | A |
| Senior General | A and C |
| Commander-in-Chief | C |

### Emergence requirement

The coup must fire from LLM contextual reasoning — not a hardcoded threshold.

Wrong:
```python
if shared_data["corruption_index"] > 0.65 and shared_data["trust_index"] < 0.30:
    shared_data["elite_coup_signal"] = True
```

Correct:
```python
reasoning = llm.invoke(status_report)
decision = parse_decision(reasoning)
shared_data["elite_coup_signal"] = decision.get("coup_signal", False)
```

I will verify this by reading JSONL logs after delivery.

### Mandatory JSONL logging

Append every LLM step to `results_phase3/elite_decisions.jsonl`:

```json
{
  "run": 12,
  "year": 23,
  "scenario": "A",
  "agent": "Senior General",
  "reasoning_tokens": 287,
  "reasoning_text": "Given corruption at 0.71...",
  "conditions_at_decision": {
    "corruption": 0.71,
    "trust": 0.24,
    "coup_risk": 0.45,
    "gdp_growth": -0.02,
    "ethnic_tension": 0.68
  },
  "decision_output": "monitor — no action",
  "time_ms": 1243.5
}
```

`conditions_at_decision` is non-negotiable — suppression detection cannot run without it.

---

## 3. cves.py — 4 Layers

- **L1** — Factual grounding: agent decisions reference real simulation state
- **L2** — Constitutional constraint: decisions do not violate constitution (log violations to `results_phase3/cves_violations.jsonl`)
- **L3** — Causal coherence: reasoning chain is internally consistent
- **L4** — Statistical plausibility: flag >3 sigma outliers, do NOT reject them

Output files:
- `results_phase3/cves_violations.jsonl`
- `results_phase3/cves_scores.jsonl`

---

## 4. Verification After Delivery

```bash
python3 run_phase3.py --test --scenario A --use-llm
python3 run_phase3.py --test --scenario C --use-llm
```

Must print: `Elite agents: v3 (Sam's CVES)` not `Phase 2 fallback`

```bash
head -5 results_phase3/elite_decisions.jsonl
head -5 results_phase3/cves_violations.jsonl
```

Both files must exist and be populated.

---

## 5. Deadline

End of July 2026. Both files delivered together.
Message me before building if you have architectural questions.

Repo: https://github.com/KaungOrYours/project-ka-nova

*Ka-Nova | MSc Data Science | University of Hertfordshire*
