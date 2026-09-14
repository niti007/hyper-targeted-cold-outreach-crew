"""Pydantic output contracts for each task in the outreach crew.

Field descriptions double as prompt instructions: CrewAI feeds a model's JSON
schema (including every `Field(description=...)`) to the LLM when
`output_pydantic` is set, so descriptions here are effectively part of the
prompt, not just documentation for humans.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class Evidence(BaseModel):
    """A single citable piece of evidence backing an ICP finding."""

    quote: str = Field(
        description=(
            "The exact sentence or phrase copied from the source page that "
            "supports the pain point or profile detail. Must be a real "
            "quote found on the page, never paraphrased or invented."
        )
    )
    source_url: str = Field(
        description=(
            "The full URL of the page the quote was found on. Must be a "
            "real, working URL returned by search or visited via scraping "
            "— never a guessed or fabricated link."
        )
    )
    date: str = Field(
        default="",
        description=(
            "Publication or posting date of the source, in any human-"
            "readable form (e.g. '2024-03', 'March 2024'), if available on "
            "the page. Leave empty if no date could be found."
        ),
    )


class ICPProfile(BaseModel):
    """The specific prospect (company or person) identified by research."""

    name: str = Field(
        description=(
            "The specific, real, named company or person this profile is "
            "about. Never a placeholder, category, or generic description "
            "— it must be a proper name found in the research."
        )
    )
    entity_type: Literal["company", "person"] = Field(
        description="Whether this ICP is a company (B2B) or an individual (B2C)."
    )
    title: str = Field(
        default="",
        description=(
            "For a person: their job title. For a company: the title of "
            "the relevant decision-maker to address (e.g. 'Head of L&D'), "
            "if identified. Leave empty if unknown."
        )
    )
    linkedin_url: str = Field(
        default="",
        description="LinkedIn profile or company page URL, if found. Leave empty if not found.",
    )
    industry: str = Field(description="The industry this company or person operates in.")
    size_or_seniority: str = Field(
        description=(
            "For a company: approximate size or stage (e.g. '200-500 "
            "employees', 'Series B'). For a person: seniority level (e.g. "
            "'mid-career', 'senior manager')."
        )
    )
    pain_point: str = Field(
        description=(
            "The specific, concrete pain signal discovered in research — "
            "e.g. an open data-analyst req, a stated upskilling gap, a "
            "career-transition post. Must be traceable to the evidence "
            "list below, not inferred or assumed."
        )
    )
    evidence: list[Evidence] = Field(
        description=(
            "At least 2 pieces of evidence, each with a real quote and "
            "source URL, that ground the pain_point above. If fewer than 2 "
            "solid pieces of evidence exist, do not invent a prospect — "
            "return what was found and set confidence to 'low' instead."
        )
    )
    confidence: Literal["low", "medium", "high"] = Field(
        description=(
            "Your honest confidence in this profile. Use 'low' when "
            "evidence is thin or indirect rather than fabricating detail "
            "to appear more confident."
        )
    )


class OutreachAngle(BaseModel):
    """The strategic mapping from the prospect's pain to a DataMantra offering."""

    pain_restated: str = Field(
        description="The prospect's pain point restated crisply in one sentence, in your own words."
    )
    matched_offering: str = Field(
        description=(
            "The DataMantra course track or offering that best addresses "
            "the pain, copied VERBATIM (exact name) from the offering "
            "catalogue provided — never invented or paraphrased."
        )
    )
    mechanism: str = Field(
        description="How the matched offering concretely solves the stated pain point — the causal link, not marketing fluff."
    )
    proof_point: str = Field(
        description=(
            "One concrete, specific proof point copied or closely drawn "
            "from the offering catalogue (a case study, placement, or "
            "stat) that is directly relevant to this prospect's pain."
        )
    )
    angle_one_liner: str = Field(
        description="A single-sentence summary of the outreach angle: the hook that connects this prospect's pain to this offering."
    )
    what_to_avoid: str = Field(
        description="Specific generic phrasing or claims the email copywriter should avoid for this particular prospect, to keep the email non-generic."
    )


class ColdEmail(BaseModel):
    """The final 3-sentence cold email, generated under strict constraints."""

    subject: str = Field(
        description="A short, specific, non-generic subject line referencing the prospect's actual situation. No clickbait, no superlatives."
    )
    sentence_1: str = Field(
        description=(
            "The specific observed detail that proves real research was "
            "done — references the exact pain signal and its source "
            "context. Must be unique to this prospect."
        )
    )
    sentence_2: str = Field(
        description="States the mechanism connecting the pain to the DataMantra offering, plus the proof point."
    )
    sentence_3: str = Field(
        description="A low-friction call to action — easy to say yes to, no pressure, no superlatives."
    )
    cta: str = Field(description="The call to action extracted as a short standalone phrase, e.g. 'a 15-minute call next week'.")
    body: str = Field(
        description=(
            "The full email body assembled from sentence_1, sentence_2, "
            "and sentence_3 in order, forming exactly 3 sentences total."
        )
    )
    personalization_hook: str = Field(
        description="The single specific fact used to personalize this email, stated plainly for internal reference."
    )
    word_count: int = Field(description="Total word count of the body across all 3 sentences. Must be 75 or fewer.")
