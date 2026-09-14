"""Shared crew-execution and output-writing logic used by both app.py and main.py."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from cold_outreach.crew import OutreachCrew
from cold_outreach.models import ColdEmail, ICPProfile, OutreachAngle
from cold_outreach.modes import MODE_BRIEFS
from cold_outreach.offering import format_offering_catalogue

_OUTPUT_DIR = Path(__file__).resolve().parents[2] / "output"


@dataclass
class RunResult:
    """The parsed outputs of one crew run, plus where they were written."""

    icp: ICPProfile
    angle: OutreachAngle
    email: ColdEmail
    raw_output: str
    json_path: Path
    md_path: Path


def build_inputs(mode: str, industry: str, region: str, seed_hint: str = "") -> dict[str, Any]:
    """Build the full `kickoff(inputs=...)` dict for the given mode and brief.

    Formats the mode's search-query templates with `industry`/`region` in
    plain Python (not CrewAI interpolation) and supplies every placeholder
    referenced in `config/tasks.yaml` and `config/agents.yaml`.
    """
    if mode not in MODE_BRIEFS:
        raise ValueError(f"Unknown mode '{mode}'. Expected one of: {list(MODE_BRIEFS)}")

    brief = MODE_BRIEFS[mode]
    formatted_queries = [q.format(industry=industry, region=region) for q in brief.search_queries]

    return {
        "mode_label": brief.label,
        "entity_type": brief.entity_type,
        "research_brief": brief.research_brief,
        "search_queries": "\n".join(f"- {q}" for q in formatted_queries),
        "industry": industry,
        "region": region,
        "seed_hint": seed_hint.strip() or "none provided",
        "email_tone": brief.email_tone,
        "cta_style": brief.cta_style,
        "offering_catalogue": format_offering_catalogue(),
    }


def _write_outputs(mode: str, inputs: dict[str, Any], icp: ICPProfile, angle: OutreachAngle, email: ColdEmail) -> tuple[Path, Path]:
    """Write the run's results as JSON and a human-readable Markdown file."""
    _OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    stem = f"{timestamp}-{mode}"

    json_path = _OUTPUT_DIR / f"{stem}.json"
    md_path = _OUTPUT_DIR / f"{stem}.md"

    payload = {
        "mode": mode,
        "inputs": {k: v for k, v in inputs.items() if k != "offering_catalogue"},
        "icp": icp.model_dump(),
        "angle": angle.model_dump(),
        "email": email.model_dump(),
    }
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    md_lines = [
        f"# Cold Outreach Run — {mode.upper()} — {timestamp}",
        "",
        "## ICP Profile",
        f"- **Name:** {icp.name}",
        f"- **Entity type:** {icp.entity_type}",
        f"- **Title:** {icp.title or '—'}",
        f"- **Industry:** {icp.industry}",
        f"- **Size / seniority:** {icp.size_or_seniority}",
        f"- **Pain point:** {icp.pain_point}",
        f"- **Confidence:** {icp.confidence}",
        "",
        "### Evidence",
    ]
    for ev in icp.evidence:
        md_lines.append(f"- \"{ev.quote}\" — [{ev.source_url}]({ev.source_url}){f' ({ev.date})' if ev.date else ''}")

    md_lines += [
        "",
        "## Outreach Angle",
        f"- **Pain restated:** {angle.pain_restated}",
        f"- **Matched offering:** {angle.matched_offering}",
        f"- **Mechanism:** {angle.mechanism}",
        f"- **Proof point:** {angle.proof_point}",
        f"- **Angle:** {angle.angle_one_liner}",
        f"- **What to avoid:** {angle.what_to_avoid}",
        "",
        "## Cold Email",
        f"**Subject:** {email.subject}",
        "",
        email.body,
        "",
        f"*Word count: {email.word_count}*",
    ]
    md_path.write_text("\n".join(md_lines), encoding="utf-8")

    return json_path, md_path


def run_outreach(mode: str, industry: str, region: str, seed_hint: str = "", model: str | None = None) -> RunResult:
    """Kick off the outreach crew and return the parsed, structured results.

    Writes `output/<UTC timestamp>-<mode>.json` and a matching `.md` file.
    """
    inputs = build_inputs(mode=mode, industry=industry, region=region, seed_hint=seed_hint)

    crew_obj = OutreachCrew().crew()

    if model:
        # `.agents`/`.tasks` only exist on the built `Crew`, not on the
        # `@CrewBase` instance itself, so build the crew first. Each agent's
        # `LLM.model` is stored WITHOUT the `openrouter/` routing prefix once
        # constructed (see `llm.py`: `LLM(model=f"openrouter/{slug}", ...)`
        # strips the prefix internally and sends the bare `provider/model`
        # slug as the literal `"model"` field of the OpenRouter API request),
        # so the override must match that same bare format.
        overridden_agent_ids: set[int] = set()
        for built_agent in crew_obj.agents:
            built_agent.llm.model = model
            overridden_agent_ids.add(id(built_agent))
        for built_task in crew_obj.tasks:
            if id(built_task.agent) not in overridden_agent_ids:
                built_task.agent.llm.model = model

    result = crew_obj.kickoff(inputs=inputs)

    icp = result.tasks_output[0].pydantic
    angle = result.tasks_output[1].pydantic
    email = result.tasks_output[2].pydantic

    for task_name, parsed in (
        ("research_icp_task", icp),
        ("match_offering_task", angle),
        ("write_email_task", email),
    ):
        if parsed is None:
            raise RuntimeError(
                f"Crew task '{task_name}' did not produce a valid structured "
                "output (its Pydantic parse failed) — check the raw task "
                "output in the crew log for what the agent actually returned."
            )

    json_path, md_path = _write_outputs(mode, inputs, icp, angle, email)

    return RunResult(
        icp=icp,
        angle=angle,
        email=email,
        raw_output=str(result.raw),
        json_path=json_path,
        md_path=md_path,
    )
