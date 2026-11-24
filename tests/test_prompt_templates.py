"""
================================================================================
PROJECT KA-NOVA
tests/test_prompt_templates.py

Guards the failure mode that cost a pod session on 2026-11-24 and would have
cost a paid campaign: a literal brace in a constitution's own
ELITE_SYSTEM_PROMPTS silently turning every LLM call into an exception.

WHAT HAPPENED. engine/elite_agents_v3.py::_invoke_llm used to build its
prompt as:

    ChatPromptTemplate.from_messages([("system", system_prompt), ...])

A ("system", text) tuple is parsed by LangChain as an f-string TEMPLATE, so
any literal `{token}` inside the prompt becomes a REQUIRED input variable.
South Korea, Pakistan and Chile each ship a JSON schema example in their
ELITE_SYSTEM_PROMPTS, so `{"budget_weight"}` was read as a variable named
'"budget_weight"'. Every call raised before reaching the model: 7 roles x 3
scenarios, 100 percent of invocations. Measured on the pod, South Korea and
Chile both returned `Successful 0 / Failed 3`.

WHY NO EXISTING TEST CAUGHT IT. The Mac has no Ollama, so `_invoke_llm` had
never once executed locally in the project's history. Every gate in tests/
runs rule-based, and the rule-based path never builds a prompt template at
all. The defect was only visible on a GPU pod, i.e. only while paying.

WHAT THIS TEST DOES. It builds the real prompt object for every role of every
registered scenario and renders it, with NO LLM and NO network, then asserts
the rendered text is byte-identical to the source prompt. That is enough to
catch the whole class: any brace, any scenario, any future constitution
encoded with a JSON example in its prompt text.

Run directly:
    python3 tests/test_prompt_templates.py

Exits non-zero on failure so CI can gate on it.

Author: Kaung Htet
License: MIT
================================================================================
"""

from __future__ import annotations

import os
import sys
import warnings

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
warnings.filterwarnings("ignore")

# Never let an import of the engine try to reach a real LLM.
os.environ.setdefault("WANDB_MODE", "disabled")

import json  # noqa: E402
import re  # noqa: E402

from langchain_core.messages import HumanMessage, SystemMessage  # noqa: E402
from langchain_core.prompts import ChatPromptTemplate  # noqa: E402

import engine.elite_agents_v3 as ea  # noqa: E402
from config.scenario_registry import SCENARIOS  # noqa: E402
from engine.cves import CVES  # noqa: E402
from engine.elite_agents_v3 import _canonicalise_braces  # noqa: E402

# A user message deliberately containing the characters that break an
# f-string template, so the test also proves the HUMAN side is literal.
# Real status reports carry ethnic-weight arrays and JSON-ish fragments.
PROBE_USER_MESSAGE = 'STATUS {"corruption": 0.878, "ethnic_weights": [0.2, 0.8]}'


def build_prompt(system_prompt: str, user_message: str):
    """Mirror engine/elite_agents_v3.py::_invoke_llm exactly.

    If that function changes, change this with it — the test is only
    meaningful while it builds the same object the engine builds.
    """
    return ChatPromptTemplate.from_messages([
        SystemMessage(content=_canonicalise_braces(system_prompt)),
        HumanMessage(content=user_message),
    ])


def main() -> int:
    print("=" * 70)
    print("PROMPT TEMPLATE RENDER TEST — all scenarios, all roles, no LLM")
    print("=" * 70)

    scenarios = ea.SCENARIO_PROMPTS
    if not scenarios:
        print("FAIL: no scenario prompts registered at all")
        return 1

    total_roles = 0
    failures: list[str] = []

    for code in sorted(scenarios):
        prompts = scenarios[code]
        rendered_ok = 0
        for role, text in sorted(prompts.items()):
            total_roles += 1
            try:
                messages = build_prompt(text, PROBE_USER_MESSAGE).invoke({}).to_messages()
            except Exception as exc:  # noqa: BLE001 — we want every failure named
                failures.append(f"{code}/{role}: raised {type(exc).__name__}: {exc}")
                continue

            # Rendering must not mutate the prompt. A template that silently
            # consumed or rewrote a brace would still "work" while sending the
            # model different text than the constitution file declares, which
            # is a provenance problem as much as a crash problem.
            if messages[0].content != _canonicalise_braces(text):
                failures.append(f"{code}/{role}: system prompt was altered during rendering")
                continue
            if messages[1].content != PROBE_USER_MESSAGE:
                failures.append(f"{code}/{role}: user message was altered during rendering")
                continue
            seen = messages[0].content

            # The model must never be shown an f-string escape. Prompts that
            # used {{ }} rendered correctly only while the text was parsed as
            # a template; once passed literally the model sees {{ and copies
            # it, producing an example decision block it cannot validly
            # imitate. Observed on the pod: South Korea emitted
            # {{"budget_weight": 0.0, ...}} verbatim.
            if "{{" in seen or "}}" in seen:
                failures.append(f"{code}/{role}: model would see an unescaped {{{{ or }}}}")
                continue

            # The example decision block must be parseable JSON, because the
            # model is explicitly told to imitate it and CVES L1 then parses
            # what comes back. A malformed example guarantees L1 reprompts on
            # every single decision.
            block = re.search(r"<DECISION>\s*(\{.*?\})\s*</DECISION>", seen, re.S)
            if block:
                try:
                    json.loads(block.group(1))
                except json.JSONDecodeError as exc:
                    failures.append(f"{code}/{role}: example decision block is not valid JSON ({exc})")
                    continue

                # Closed loop: the exact block we tell this scenario's model to
                # emit must survive this scenario's own CVES L1 parse. This is
                # the check that would have caught the hardcoded `len(ew) == 8`
                # in parse_decision, which silently discarded the model's
                # ethnic_weights for every constitution whose ETHNIC_GROUPS
                # count was not 8 — South Korea (1), Pakistan (6), Chile (0),
                # Germany (0) — and then failed L1 on the substituted Myanmar
                # vector. Measured on the pod before the fix: Germany at 26.2s
                # per decision, 20 of 20 parse failures, three retries each,
                # with the model's own coup_signal discarded and replaced by
                # the ROLE_DEFAULTS False. Any "this constitution emits no
                # coup signals" conclusion drawn from those scenarios was an
                # artifact of that line, not a property of the constitution.
                entry = SCENARIOS[code]
                cves = CVES(llm=None, constitution=entry.constitution,
                            chain_type=entry.chain_type, scenario=code)
                parsed = cves.l1_parse(
                    f"<DECISION>{block.group(1)}</DECISION>", role, seen, "probe", None
                )
                if parsed.get("_l1_parse_failure"):
                    failures.append(
                        f"{code}/{role}: CVES L1 cannot parse this scenario's own example "
                        f"decision block (n_ethnic={cves.n_ethnic})"
                    )
                    continue
                declared = json.loads(block.group(1))
                if "budget_weight" in declared and parsed.get("budget_weight") != declared["budget_weight"]:
                    failures.append(
                        f"{code}/{role}: L1 silently replaced budget_weight "
                        f"{declared['budget_weight']} with {parsed.get('budget_weight')}"
                    )
                    continue

            rendered_ok += 1

        status = "OK" if rendered_ok == len(prompts) else "FAIL"
        print(f"  {code:<4} {rendered_ok}/{len(prompts)} roles render byte-identical   {status}")

    print("-" * 70)
    if failures:
        print(f"RESULT: {len(failures)} of {total_roles} role-prompts FAILED\n")
        for f in failures[:20]:
            print(f"  {f}")
        if len(failures) > 20:
            print(f"  ... and {len(failures) - 20} more")
        print("\nA literal brace in a system prompt is read as a template variable.")
        print("Fix the engine's prompt construction, not the constitution text —")
        print("escaping braces per-file breaks again on the next constitution.")
        return 1

    print(f"RESULT: {total_roles}/{total_roles} role-prompts render byte-identical")
    print("PASS: no prompt can raise a missing-variable error at invoke time")
    return 0


if __name__ == "__main__":
    sys.exit(main())
