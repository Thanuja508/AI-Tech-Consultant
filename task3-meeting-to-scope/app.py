import json
from datetime import datetime, timezone
from pathlib import Path

import requests
import streamlit as st

st.set_page_config(
    page_title="AI Tech Consultant - Meeting to Scope",
    page_icon="📝",
    layout="wide",
)

PROJECT_DIR = Path(__file__).resolve().parent
FEEDBACK_FILE = PROJECT_DIR / "scope_feedback.json"
KNOWLEDGE_API = "http://127.0.0.1:8000"


def save_feedback(record):
    records = []

    if FEEDBACK_FILE.exists():
        try:
            records = json.loads(
                FEEDBACK_FILE.read_text(encoding="utf-8")
            )
        except (json.JSONDecodeError, OSError):
            records = []

    records.append(record)
    FEEDBACK_FILE.write_text(
        json.dumps(records, indent=2),
        encoding="utf-8",
    )


def search_knowledge(query):
    try:
        response = requests.post(
            f"{KNOWLEDGE_API}/search",
            json={"query": query, "top_k": 3},
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        return data.get("results", data.get("sources", []))
    except requests.RequestException:
        return []


def make_scope(notes, project_name, budget, deadline, extra_requirements):
    combined = f"""
Project: {project_name}

Meeting notes:
{notes}

Budget: {budget or "Not specified"}
Deadline: {deadline or "Not specified"}

Additional requirements:
{extra_requirements or "None provided"}
"""

    lines = [
        line.strip(" -*\t")
        for line in notes.splitlines()
        if line.strip()
    ]

    requirements = []
    for line in lines:
        clean_line = line.lstrip("0123456789. )-").strip()
        if clean_line and len(clean_line) > 3:
            requirements.append(clean_line)

    requirements = list(dict.fromkeys(requirements))

    if not requirements:
        requirements = [
            "Clarify project goals with the client",
            "Identify functional and non-functional requirements",
            "Confirm integrations, data, and security needs",
            "Agree on acceptance criteria",
        ]

    task_templates = [
        ("Discovery and clarification", 4),
        ("Design and planning", 6),
        ("Core implementation", 16),
        ("Integration and testing", 8),
        ("Review and handover", 4),
    ]

    total_hours = sum(hours for _, hours in task_templates)
    contingency = round(total_hours * 0.20)
    total_with_contingency = total_hours + contingency

    return {
        "project_name": project_name,
        "meeting_summary": combined.strip(),
        "requirements": requirements,
        "estimate": [
            {"task": task, "hours": hours}
            for task, hours in task_templates
        ],
        "base_hours": total_hours,
        "contingency_hours": contingency,
        "total_hours": total_with_contingency,
        "assumptions": [
            "Estimates are preliminary and need technical review.",
            "Requirements inferred from notes must be confirmed.",
            "Third-party costs and external dependencies are excluded.",
            "The schedule depends on client feedback and access to systems.",
        ],
        "knowledge_sources": search_knowledge(
            " ".join(requirements[:5]) or project_name
        ),
    }


st.title("📝 AI Tech Consultant — Meeting to Scope")
st.write(
    "Turn client meeting notes into structured requirements, "
    "a preliminary effort estimate, and a reviewable project scope."
)

st.info(
    "Prototype: estimates use transparent baseline task hours, "
    "not an AI-validated quote. Review all requirements and estimates "
    "before sharing them with a client."
)

with st.form("scope_form"):
    project_name = st.text_input(
        "Project name",
        placeholder="Example: Customer support portal",
    )

    notes = st.text_area(
        "Meeting notes / transcript",
        height=220,
        placeholder=(
            "Example:\n"
            "Customer needs user login and a dashboard.\n"
            "Admin should manage users.\n"
            "The system should work on mobile.\n"
            "Need a first version in six weeks."
        ),
    )

    col1, col2 = st.columns(2)

    with col1:
        budget = st.text_input(
            "Budget (optional)",
            placeholder="Example: €5,000",
        )

    with col2:
        deadline = st.text_input(
            "Target deadline (optional)",
            placeholder="Example: Six weeks",
        )

    extra_requirements = st.text_area(
        "Additional requirements / constraints (optional)",
        height=100,
    )

    submitted = st.form_submit_button(
        "Generate project scope",
        type="primary",
    )

if submitted:
    if not project_name.strip():
        st.error("Enter a project name.")
    elif not notes.strip():
        st.error("Enter meeting notes first.")
    else:
        st.session_state["scope_result"] = make_scope(
            notes,
            project_name.strip(),
            budget.strip(),
            deadline.strip(),
            extra_requirements.strip(),
        )
        st.session_state["scope_decision"] = None

if "scope_result" in st.session_state:
    result = st.session_state["scope_result"]

    st.divider()
    st.header("1. Project overview")
    st.write(f"**Project:** {result['project_name']}")
    st.write(result["meeting_summary"])

    st.header("2. Extracted requirements")
    for index, requirement in enumerate(result["requirements"], start=1):
        st.write(f"{index}. {requirement}")

    st.header("3. Preliminary effort estimate")
    st.caption("Hours are baseline estimates and must be reviewed.")

    st.dataframe(
        result["estimate"],
        use_container_width=True,
        hide_index=True,
    )

    c1, c2, c3 = st.columns(3)
    c1.metric("Base effort", f"{result['base_hours']} hours")
    c2.metric("20% contingency", f"{result['contingency_hours']} hours")
    c3.metric("Total estimate", f"{result['total_hours']} hours")

    st.header("4. Scope options")
    basic, recommended, extended = st.columns(3)

    with basic:
        st.subheader("Basic")
        st.write("Core requirements only")
        st.write(f"**{round(result['total_hours'] * 0.7)} hours**")
        st.caption("Some optional requirements excluded.")

    with recommended:
        st.subheader("Recommended")
        st.write("Core work plus contingency")
        st.write(f"**{result['total_hours']} hours**")
        st.caption("Includes a preliminary risk allowance.")

    with extended:
        st.subheader("Extended")
        st.write("Core work, enhancements, and extra testing")
        st.write(f"**{round(result['total_hours'] * 1.4)} hours**")
        st.caption("Requires more detailed discovery.")

    st.header("5. Assumptions and risks")
    for assumption in result["assumptions"]:
        st.write(f"- {assumption}")

    st.header("6. Knowledge Brain references")
    sources = result["knowledge_sources"]

    if sources:
        for source in sources:
            title = source.get("title", "Documentation")
            url = source.get("url", "")
            if url:
                st.markdown(f"- [{title}]({url})")
            else:
                st.write(f"- {title}")
    else:
        st.warning(
            "Knowledge Brain references are unavailable. "
            "Check that Task 1 is running at http://127.0.0.1:8000."
        )

    st.header("7. Review and approval")
    st.write(
        "Review the requirements, estimates, and assumptions "
        "before approving this draft."
    )

    edited_requirements = st.text_area(
        "Edit requirements before approval",
        value="\n".join(result["requirements"]),
        key="edited_requirements",
    )

    review_notes = st.text_area(
        "Reviewer comments (optional)",
        key="review_notes",
    )

    approve_col, reject_col = st.columns(2)

    with approve_col:
        if st.button("Approve scope", type="primary"):
            save_feedback({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "decision": "approved",
                "project_name": result["project_name"],
                "requirements": edited_requirements.splitlines(),
                "estimated_hours": result["total_hours"],
                "review_notes": review_notes,
            })
            st.session_state["scope_decision"] = "approved"

    with reject_col:
        if st.button("Request changes"):
            save_feedback({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "decision": "changes_requested",
                "project_name": result["project_name"],
                "requirements": edited_requirements.splitlines(),
                "estimated_hours": result["total_hours"],
                "review_notes": review_notes,
            })
            st.session_state["scope_decision"] = "changes_requested"

    decision = st.session_state.get("scope_decision")

    if decision == "approved":
        st.success("Scope approval recorded locally.")
    elif decision == "changes_requested":
        st.warning("Change request recorded locally.")

    st.download_button(
        "Download scope as JSON",
        data=json.dumps(result, indent=2),
        file_name="project_scope.json",
        mime="application/json",
    )

st.divider()
st.caption(
    "Prototype only: no client email is sent. "
    "Approval records are stored locally in scope_feedback.json."
)