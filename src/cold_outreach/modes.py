"""B2B / B2C mode briefs: search strategy, pain-signal definitions, and tone.

Search query templates use plain Python `{industry}` / `{region}` formatting
done in `runner.py` — NOT CrewAI's `kickoff(inputs=...)` interpolation — so
they are fully resolved before ever reaching the LLM.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ModeBrief:
    """Everything that differs between the B2B and B2C outreach modes."""

    key: str
    label: str
    entity_type: str
    research_brief: str
    search_queries: list[str] = field(default_factory=list)
    email_tone: str = ""
    cta_style: str = ""


MODE_BRIEFS: dict[str, ModeBrief] = {
    "b2b": ModeBrief(
        key="b2b",
        label="B2B — Company with an L&D / talent gap",
        entity_type="company",
        research_brief=(
            "Find a specific, named company in the given industry and region that is "
            "showing a concrete data/AI/finance talent or upskilling gap. Look for: open "
            "job requisitions for data analyst, data scientist, or AI roles; posts or news "
            "about digital-transformation initiatives; L&D or learning-and-development "
            "announcements; hiring surges in data-related roles; statements from "
            "leadership about needing data/AI capability. A real pain signal is a job "
            "posting, a company blog post, a news article, or a LinkedIn post that "
            "explicitly names a hiring need or a skills gap — not a vague industry trend. "
            "Also try to identify the relevant decision-maker (Head of L&D, Data Lead, "
            "CHRO, or similar) if their name and title are discoverable. If you cannot "
            "find a real, named company with at least 2 citable sources, do not invent "
            "one — report what you found and set confidence to low."
        ),
        search_queries=[
            '"{industry}" "{region}" (hiring OR "job opening") ("data analyst" OR "data scientist")',
            '"{industry}" "{region}" (upskilling OR "learning and development") site:linkedin.com',
            '"{industry}" "{region}" (funding OR "digital transformation") data AI',
        ],
        email_tone="Professional, peer-to-peer, consultative — written as one L&D-minded operator to another, not a vendor pitch.",
        cta_style="A brief, low-friction ask such as a 15-minute call or a short reply, framed as optional and easy to decline.",
    ),
    "b2c": ModeBrief(
        key="b2c",
        label="B2C — Individual signalling a career switch",
        entity_type="person",
        research_brief=(
            "Find a specific, named individual in the given industry/region context who is "
            "publicly signalling an interest in switching careers into data, AI, or "
            "finance. Look for: LinkedIn posts or profiles mentioning 'career transition', "
            "'switching to data science', 'learning data analytics', course enrollment "
            "announcements, or similar publicly visible statements of intent. A real pain "
            "signal is an actual post or profile update in the person's own words — not an "
            "assumption based on their current job title alone. If you cannot find a real, "
            "named person with at least 2 citable sources, do not invent one — report what "
            "you found and set confidence to low."
        ),
        search_queries=[
            'site:linkedin.com/in "career transition" "data analyst" "{region}"',
            'site:linkedin.com/posts "switching to data science" "{industry}"',
            '"{industry}" "{region}" "breaking into data" OR "learning data analytics"',
        ],
        email_tone="Warm, encouraging, one individual to another — like a mentor reaching out, not a company blasting a lead list.",
        cta_style="An easy, non-salesy next step such as a free resource, a short chat, or a course info link, never pressuring.",
    ),
}
