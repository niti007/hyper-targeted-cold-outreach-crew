"""Streamlit UI for the hyper-targeted cold outreach crew."""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Allow running `streamlit run app.py` straight from a clone with no install step.
_SRC_DIR = Path(__file__).resolve().parent / "src"
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))

import streamlit as st  # noqa: E402
from dotenv import load_dotenv  # noqa: E402

from cold_outreach.modes import MODE_BRIEFS  # noqa: E402
from cold_outreach.runner import run_outreach  # noqa: E402

load_dotenv()

st.set_page_config(page_title="Hyper-Targeted Cold Outreach", page_icon="🎯", layout="wide")

st.title("🎯 Hyper-Targeted Cold Outreach")
st.caption(
    "A 3-agent CrewAI pipeline that researches a real prospect, matches their pain to a "
    "DataMantra offering, and writes a 3-sentence cold email grounded in live web evidence."
)

# --- Key status ---------------------------------------------------------
openrouter_key = os.environ.get("OPENROUTER_API_KEY")
serper_key = os.environ.get("SERPER_API_KEY")
keys_ready = bool(openrouter_key) and bool(serper_key)

with st.sidebar:
    st.header("Configuration")

    mode = st.radio(
        "Mode",
        options=list(MODE_BRIEFS.keys()),
        format_func=lambda k: MODE_BRIEFS[k].label,
        index=0,
    )
    industry = st.text_input("Industry", value="fintech")
    region = st.text_input("Region", value="India")
    seed_hint = st.text_input("Seed hint (optional)", value="", help="A company or person you already have in mind.")
    model_override = st.text_input(
        "Model override (optional)",
        value="",
        help="OpenRouter model slug, e.g. 'anthropic/claude-sonnet-5'. Leave blank to use the default.",
    )

    st.divider()
    st.subheader("Key status")
    st.write(f"{'✅' if openrouter_key else '❌'} OPENROUTER_API_KEY")
    st.write(f"{'✅' if serper_key else '❌'} SERPER_API_KEY")

# --- Main area -----------------------------------------------------------
if not keys_ready:
    st.warning("Missing API keys — the crew cannot run until both are set.")
    st.markdown(
        "1. Create a `.env` file in the project root (copy `.env.example` if present).\n"
        "2. Set `OPENROUTER_API_KEY` (from https://openrouter.ai/keys).\n"
        "3. Set `SERPER_API_KEY` (from https://serper.dev).\n"
        "4. Optionally set `OPENROUTER_MODEL` to pick a default model.\n"
        "5. Restart this app."
    )
else:
    run_clicked = st.button("Run crew", type="primary")

    if run_clicked:
        try:
            with st.status("Running the outreach crew...", expanded=True) as status:
                status.write("Researching ICP and pain signal (live web search)...")
                result = run_outreach(
                    mode=mode,
                    industry=industry,
                    region=region,
                    seed_hint=seed_hint,
                    model=model_override or None,
                )
                status.write("Matching offering and drafting email...")
                status.update(label="Run complete.", state="complete")

            icp = result.icp
            angle = result.angle
            email = result.email

            confidence_color = {"low": "orange", "medium": "blue", "high": "green"}.get(icp.confidence, "gray")

            st.subheader("1. ICP Profile")
            with st.container(border=True):
                st.markdown(f"**{icp.name}** — {icp.entity_type} &nbsp;|&nbsp; :{confidence_color}[confidence: {icp.confidence}]")
                st.write(f"**Title:** {icp.title or '—'}")
                st.write(f"**Industry:** {icp.industry} &nbsp;|&nbsp; **Size/Seniority:** {icp.size_or_seniority}")
                if icp.linkedin_url:
                    st.write(f"**LinkedIn:** [{icp.linkedin_url}]({icp.linkedin_url})")
                st.write(f"**Pain point:** {icp.pain_point}")
                st.markdown("**Evidence:**")
                for ev in icp.evidence:
                    st.markdown(f"> {ev.quote}")
                    st.markdown(f"[{ev.source_url}]({ev.source_url}) {f'· {ev.date}' if ev.date else ''}")

            st.subheader("2. Outreach Angle")
            with st.container(border=True):
                st.write(f"**Pain restated:** {angle.pain_restated}")
                st.write(f"**Matched offering:** {angle.matched_offering}")
                st.write(f"**Mechanism:** {angle.mechanism}")
                st.write(f"**Proof point:** {angle.proof_point}")
                st.write(f"**Angle:** {angle.angle_one_liner}")
                st.write(f"**What to avoid:** {angle.what_to_avoid}")

            st.subheader("3. Cold Email")
            with st.container(border=True):
                st.markdown("**Subject**")
                st.code(email.subject, language=None)
                st.markdown("**Body**")
                st.code(email.body, language=None)
                st.caption(f"Word count: {email.word_count} | Personalization hook: {email.personalization_hook}")

            st.download_button(
                "Download JSON",
                data=result.json_path.read_text(encoding="utf-8"),
                file_name=result.json_path.name,
                mime="application/json",
            )

        except Exception as exc:  # noqa: BLE001
            st.error(f"The crew run failed: {exc}")
            st.exception(exc)
