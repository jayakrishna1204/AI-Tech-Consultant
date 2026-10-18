

import json
import streamlit as st

from task3_meeting_scope.agents import generate_project_scope
from task3_meeting_scope.scope_diff import compare_scopes


st.set_page_config(
    page_title="Meeting to Scope",
    page_icon="📋",
    layout="wide",
)

if "current_scope" not in st.session_state:
    st.session_state.current_scope = None

if "previous_scope" not in st.session_state:
    st.session_state.previous_scope = None

if "scope_reviewed" not in st.session_state:
    st.session_state.scope_reviewed = False

st.title("📋 Meeting to Scope")
st.caption(
    "Convert meeting transcripts into a draft project scope "
    "with tasks, estimates, assumptions, and risks."
)

st.warning(
    "AI-generated scopes and estimates are preliminary. "
    "A human must review and approve them before they become commitments."
)

generate_tab, compare_tab = st.tabs(
    ["Generate Scope", "Compare Follow-up"]
)

with generate_tab:
    st.subheader("Meeting Transcript")

    transcript = st.text_area(
        "Paste the meeting transcript",
        placeholder=(
            "Customer: We need an online bookstore website...\n"
            "Consultant: Which features are essential for launch?"
        ),
        height=300,
        key="meeting_transcript",
    )

    if st.button("Generate Project Scope", type="primary"):
        if len(transcript.strip()) < 30:
            st.warning(
                "Please enter a transcript containing at least 30 characters."
            )
        else:
            with st.spinner("Generating draft project scope..."):
                try:
                    new_scope = generate_project_scope(transcript.strip())

                    if st.session_state.current_scope is not None:
                        st.session_state.previous_scope = (
                            st.session_state.current_scope.copy()
                        )

                    st.session_state.current_scope = new_scope
                    st.session_state.scope_reviewed = False

                    st.success("Scope generated successfully.")

                except Exception as error:
                    st.error(f"Scope generation failed: {error}")

    scope = st.session_state.current_scope

    if scope:
        st.divider()
        st.subheader("Draft Project Scope")

        st.markdown("### Project Summary")
        st.write(scope.get("project_summary", "No summary was generated."))

        st.markdown("### Deliverables")
        deliverables = scope.get("deliverables", [])

        if deliverables:
            for item in deliverables:
                st.markdown(f"- {item}")
        else:
            st.info("No deliverables were returned.")

        st.markdown("### Implementation Tasks")
        tasks = scope.get("tasks", [])

        if tasks:
            task_rows = [
                {
                    "Task": task.get("task", "Unspecified task"),
                    "Estimated hours": task.get("estimate_hours", 0),
                    "Rationale": task.get("rationale", ""),
                }
                for task in tasks
            ]

            st.dataframe(
                task_rows,
                width="stretch",
                hide_index=True,
            )

            total_hours = sum(
                float(task.get("estimate_hours", 0) or 0)
                for task in tasks
            )
            st.metric("Total estimated effort", f"{total_hours:g} hours")
        else:
            st.info("No implementation tasks were returned.")

        for section, title in [
            ("assumptions", "Assumptions"),
            ("exclusions", "Out of Scope"),
            ("risks", "Risks"),
            ("open_questions", "Open Questions"),
        ]:
            st.markdown(f"### {title}")
            items = scope.get(section, [])

            if items:
                for item in items:
                    st.markdown(f"- {item}")
            else:
                st.write("None identified.")

        st.markdown("### Product Knowledge Sources")
        sources = scope.get("knowledge_sources", [])

        if sources:
            for source in sources:
                title = source.get("title", "Help article")
                url = source.get("url", "")

                if url:
                    st.markdown(f"- [{title}]({url})")
                else:
                    st.write(title)
        else:
            st.info("No product knowledge sources were returned.")

        if scope.get("knowledge_review_required", True):
            st.warning(
                "Product knowledge needs human verification before approval."
            )

        st.warning("Status: Draft — human approval required.")

        st.download_button(
            "Download Scope JSON",
            data=json.dumps(scope, indent=2, ensure_ascii=False),
            file_name="project_scope.json",
            mime="application/json",
        )

        if st.button("Mark Scope as Human-Reviewed"):
            st.session_state.scope_reviewed = True
            st.success(
                "Review acknowledgement recorded for this session. "
                "This does not constitute persistent approval tracking."
            )

with compare_tab:
    st.subheader("Compare a Follow-up Meeting")

    previous_scope = st.session_state.previous_scope
    current_scope = st.session_state.current_scope

    if previous_scope is None or current_scope is None:
        st.info(
            "Generate two scopes first. The second scope will be "
            "compared with the first."
        )
    else:
        st.write("**Previous scope:**")
        st.write(previous_scope.get("project_summary", "Summary unavailable"))

        st.write("**Updated scope:**")
        st.write(current_scope.get("project_summary", "Summary unavailable"))

        if st.button("Compare Scopes", type="primary"):
            try:
                diff = compare_scopes(previous_scope, current_scope)

                st.markdown("### Scope Change Summary")
                st.json(diff)

                st.metric(
                    "Previous estimated hours",
                    diff["previous_estimated_hours"],
                )
                st.metric(
                    "Updated estimated hours",
                    diff["updated_estimated_hours"],
                )
                st.metric(
                    "Estimate change (hours)",
                    diff["estimate_change_hours"],
                )

                if diff["possible_scope_change"]:
                    st.warning(
                        "Potential scope changes detected. "
                        "Human approval is required."
                    )
                else:
                    st.success("No scope changes detected by the comparison.")

            except Exception as error:
                st.error(f"Comparison failed: {error}")

st.divider()
st.caption("Task 3 — Meeting to Scope | Drafts require human approval")
