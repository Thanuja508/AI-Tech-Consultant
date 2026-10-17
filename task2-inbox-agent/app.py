import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path

import requests
import streamlit as st
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

KNOWLEDGE_API = os.getenv(
    "KNOWLEDGE_API_URL", "http://127.0.0.1:8000"
).rstrip("/")

FEEDBACK_FILE = BASE_DIR / "feedback.json"

st.set_page_config(
    page_title="AI Inbox Agent",
    page_icon="📨",
    layout="wide",
)

st.title("📨 AI Tech Consultant — Inbox Agent")
st.caption(
    "Classify support emails, retrieve documentation, "
    "draft replies, and approve them before sending."
)


def log_feedback(record):
    """Append feedback safely without overwriting previous records."""
    records = []

    if FEEDBACK_FILE.exists():
        try:
            records = json.loads(
                FEEDBACK_FILE.read_text(encoding="utf-8")
            )
            if not isinstance(records, list):
                records = []
        except (OSError, json.JSONDecodeError):
            records = []

    records.append(record)
    temporary_file = FEEDBACK_FILE.with_suffix(".tmp")
    temporary_file.write_text(
        json.dumps(records, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    temporary_file.replace(FEEDBACK_FILE)


def classify_email(subject, body):
    """Rule-based baseline classification."""
    text = f"{subject}\n{body}".lower()

    urgent_terms = [
        "urgent", "critical", "outage", "down", "cannot access",
        "can't access", "payment failed", "security breach",
    ]
    billing_terms = [
        "invoice", "billing", "refund", "payment", "subscription",
    ]
    technical_terms = [
        "error", "bug", "not working", "configure", "settings",
        "email", "domain", "website", "login", "integration",
    ]

    if any(term in text for term in urgent_terms):
        category = "Urgent"
        priority = "High"
    elif any(term in text for term in billing_terms):
        category = "Billing"
        priority = "Medium"
    elif any(term in text for term in technical_terms):
        category = "Technical Support"
        priority = "Medium"
    else:
        category = "General Inquiry"
        priority = "Low"

    return {
        "category": category,
        "priority": priority,
    }


def ask_knowledge_brain(question):
    """Retrieve an answer from Task 1's FastAPI service."""
    response = requests.post(
        f"{KNOWLEDGE_API}/ask",
        json={"query": question},
        timeout=90,
    )
    response.raise_for_status()
    return response.json()


def build_draft(subject, body, result):
    answer = str(result.get("answer", "")).strip()
    sources = result.get("sources", [])
    needs_review = result.get("needs_human_review", False)

    source_lines = "\n".join(
        f"- {item.get('title', 'Documentation')}: {item.get('url', '')}"
        for item in sources
        if item.get("url")
    )

    if needs_review or not sources or not answer:
        draft = (
            "Hello,\n\n"
            "Thank you for contacting support.\n\n"
            "We need to verify the details of your request "
            "before providing a reliable solution. Our support "
            "team will review your question and follow up with you.\n\n"
            "Best regards,\nSupport Team"
        )
    else:
        clean_answer = answer.replace("**INSUFFICIENT EVIDENCE**", "").strip()
        clean_answer = clean_answer.replace("**", "").strip()

        draft = (
            "Hello,\n\n"
            "Thank you for contacting support.\n\n"
            f"{clean_answer}\n\n"
            "Documentation references:\n"
            f"{source_lines}\n\n"
            "Please let us know if you need any further assistance.\n\n"
            "Best regards,\n"
            "Support Team"
        )

    return draft


if "email_id" not in st.session_state:
    st.session_state.email_id = None

if "draft" not in st.session_state:
    st.session_state.draft = ""

if "analysis" not in st.session_state:
    st.session_state.analysis = None

if "knowledge_result" not in st.session_state:
    st.session_state.knowledge_result = None


with st.form("email_form"):
    st.subheader("1. Enter an incoming email")

    sender = st.text_input(
        "Sender email",
        placeholder="customer@example.com",
    )
    subject = st.text_input(
        "Subject",
        placeholder="Email forwarding is not working",
    )
    body = st.text_area(
        "Email body",
        height=180,
        placeholder="Describe the customer's question...",
    )

    analyze = st.form_submit_button(
        "Classify email and draft reply",
        type="primary",
    )


if analyze:
    if not subject.strip() or not body.strip():
        st.error("Please enter both the subject and email body.")
    else:
        st.session_state.email_id = str(uuid.uuid4())
        st.session_state.analysis = classify_email(subject, body)
        st.session_state.knowledge_result = None

        question = (
            f"Email subject: {subject.strip()}\n"
            f"Customer message: {body.strip()}"
        )

        with st.spinner("Searching the Knowledge Brain..."):
            try:
                result = ask_knowledge_brain(question)
                st.session_state.knowledge_result = result
                st.session_state.draft = build_draft(
                    subject, body, result
                )
                st.success("Email classified and draft prepared.")
            except requests.RequestException as exc:
                st.error(
                    "Could not contact the Knowledge Brain API. "
                    "Check that Task 1 is running at "
                    f"{KNOWLEDGE_API}. Details: {exc}"
                )


if st.session_state.analysis:
    st.divider()
    st.subheader("2. Classification")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Category",
        st.session_state.analysis["category"],
    )
    col2.metric(
        "Priority",
        st.session_state.analysis["priority"],
    )
    col3.metric(
        "Status",
        "Draft ready" if st.session_state.draft else "No draft",
    )


if st.session_state.knowledge_result:
    result = st.session_state.knowledge_result

    st.subheader("3. Knowledge Brain evidence")

    if result.get("needs_human_review"):
        st.warning(
            "The Knowledge Brain flagged this question for human review. "
            "The draft below is a holding response, not a verified solution."
        )

        task_id = result.get("expert_task_id")
        if task_id:
            st.write(f"Expert review task: `{task_id}`")
    else:
        st.info("Review the generated answer and sources before approval.")

    sources = result.get("sources", [])
    if sources:
        for source in sources:
            title = source.get("title", "Source")
            url = source.get("url", "")
            if url:
                st.markdown(f"- [{title}]({url})")
            else:
                st.write(f"- {title}")
    else:
        st.write("No supporting documentation was retrieved.")


if st.session_state.draft:
    st.subheader("4. Review and approve reply")

    edited_draft = st.text_area(
        "Editable email draft",
        value=st.session_state.draft,
        height=300,
        key="draft_editor",
    )

    st.caption(
        "This prototype does not send email. Approval records your "
        "decision; it does not send a message to the customer."
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Approve draft", type="primary"):
            log_feedback({
                "id": st.session_state.email_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "decision": "approved",
                "draft": edited_draft,
                "analysis": st.session_state.analysis,
                "knowledge_result": st.session_state.knowledge_result,
            })
            st.success("Approval recorded in feedback.json.")

    with col2:
        if st.button("Reject draft"):
            log_feedback({
                "id": st.session_state.email_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "decision": "rejected",
                "draft": edited_draft,
                "analysis": st.session_state.analysis,
                "knowledge_result": st.session_state.knowledge_result,
            })
            st.warning("Rejection recorded in feedback.json.")


st.divider()
st.caption(
    "Prototype note: classification is rule-based, feedback is stored "
    "locally, and email sending is intentionally disabled."
)