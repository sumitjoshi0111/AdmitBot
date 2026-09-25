"""
chatbot.py

Simple RULE-BASED / KEYWORD-BASED chatbot logic for AdmitBot.

This is NOT a machine-learning model. It is a rule-based intent
detection system, which is a valid and common way to demonstrate an
AI-style conversational component in a mini-project.

Responsibilities:
    - Detect the user's intent (GREETING / FAQ / PREDICTION / COUNSELLING / UNKNOWN)
    - Answer FAQs using keyword matching
    - Collect rank, category, branch step-by-step (slot filling)
    - Call predictor.py for the actual HIGH/MEDIUM/LOW result
    - Keep conversation context for the current session
"""

import json
import os
import re

import predictor

FAQ_PATH = os.path.join(os.path.dirname(__file__), "data", "faq.json")

# Placeholder link - replace with the real AdmitPro URL when available.
PLACEHOLDER_ADMITPRO_URL = "PLACEHOLDER_ADMITPRO_URL"

CATEGORY_LIST = ["OPEN", "OBC", "SC", "ST", "EWS"]

# Maps common ways a user might type a branch name to the exact
# branch name used in colleges.csv.
BRANCH_ALIASES = {
    "computer": "Computer Engineering",
    "comp": "Computer Engineering",
    "cse": "Computer Engineering",
    "computer engineering": "Computer Engineering",
    "it": "Information Technology",
    "information technology": "Information Technology",
    "mechanical": "Mechanical Engineering",
    "mech": "Mechanical Engineering",
    "mechanical engineering": "Mechanical Engineering",
}

GREETING_WORDS = ["hi", "hello", "hey", "good morning", "good evening", "good afternoon"]
COUNSELLING_WORDS = [
    "counsellor", "counselor", "counselling", "counseling",
    "talk to someone", "human help", "guidance", "book a session",
]
PREDICTION_WORDS = [
    "predict", "prediction", "college", "colleges", "eligible",
    "chance", "chances", "suggest", "suitable college", "get admission",
]

# Load FAQ data once when this module is imported.
with open(FAQ_PATH, encoding="utf-8") as f:
    FAQ_DATA = json.load(f)


def default_context():
    """A fresh, empty conversation context."""
    return {
        "rank": None,
        "category": None,
        "branch": None,
        "stage": None,  # None -> "awaiting_category" -> "awaiting_branch" -> "ready"
    }


def detect_intent(message):
    """Very simple keyword-based intent classifier."""
    msg = message.lower()

    if any(word in msg for word in GREETING_WORDS):
        return "GREETING"

    if search_faq(message) is not None:
        return "FAQ"

    if any(word in msg for word in COUNSELLING_WORDS):
        return "COUNSELLING"

    if any(word in msg for word in PREDICTION_WORDS) or extract_rank(message) is not None:
        return "PREDICTION"

    return "UNKNOWN"


def search_faq(message):
    """Return the FAQ answer if any keyword matches, else None."""
    msg = message.lower()
    for item in FAQ_DATA:
        for keyword in item["keywords"]:
            if keyword in msg:
                return item["answer"]
    return None


def extract_rank(message):
    """Extract a plausible CET rank (1 to 6 digit number) from text."""
    match = re.search(r"\b(\d{1,6})\b", message)
    if match:
        return int(match.group(1))
    return None


def extract_category(message):
    """Extract a known category keyword from text (whole-word match)."""
    msg = message.upper()
    for category in CATEGORY_LIST:
        if re.search(r"\b" + category + r"\b", msg):
            return category
    return None


def extract_branch(message):
    """Extract a known branch using alias matching."""
    msg = message.lower()
    for alias, branch_name in BRANCH_ALIASES.items():
        if alias in msg:
            return branch_name
    return None


def format_prediction_results(results, rank, category, branch):
    """Turn predictor.py's output into a readable chat message."""
    header = (
        f"Based on rank {rank}, category {category}, branch {branch} "
        f"(using SAMPLE demonstration cutoff data, not official data):\n"
    )
    if not results:
        return (
            header
            + "No matching cutoff data is available for this combination "
            "in the sample dataset. Please try a different branch/category, "
            "or check AdmitPro / official CAP sources for real data."
        )

    lines = [header]
    for r in results:
        lines.append(
            f"- {r['college']} ({r['branch']}, {r['category']}): "
            f"{r['result']} (sample closing rank: {r['closing_rank']})"
        )
    lines.append(
        "\nNote: This is an indication based on sample data only, not a guarantee of admission."
    )
    return "\n".join(lines)


def run_prediction(context):
    """Call predictor.py using the values stored in context."""
    results = predictor.predict(context["rank"], context["category"], context["branch"])
    return format_prediction_results(results, context["rank"], context["category"], context["branch"])


def ask_for_category_message():
    return (
        "Great. What is your category? "
        f"(Available in sample data: {', '.join(CATEGORY_LIST)})"
    )


def ask_for_branch_message():
    branches = predictor.get_available_branches()
    return f"Which branch are you interested in? (e.g., {', '.join(branches)})"


def counselling_response():
    return (
        "I understand you'd like to talk to a counsellor for personalised guidance. "
        "You can get full counselling support through AdmitPro.\n"
        f"Open AdmitPro: {PLACEHOLDER_ADMITPRO_URL}"
    )


def greeting_response():
    return (
        "Hello! I am AdmitBot, your engineering admission assistant. "
        "You can ask me about CAP, CET, cutoffs, categories, or say things like "
        "'my rank is 2500' to get a sample college prediction."
    )


def fallback_response():
    return (
        "I am AdmitBot and I currently focus on engineering admission and "
        "counselling queries. Please ask me about CAP, CET, rank, category, "
        "branches, colleges, or counselling."
    )


def get_response(message, context):
    """
    Main entry point used by app.py.

    Args:
        message: the raw text the user typed.
        context: the current session's context dict (see default_context()).

    Returns:
        (response_text, updated_context)
    """
    message = (message or "").strip()
    if context is None:
        context = default_context()

    if not message:
        return "Please type a message so I can help you.", context

    stage = context.get("stage")

    # --- Slot-filling state machine (only active once we've started
    # collecting rank/category/branch) ---
    if stage == "awaiting_rank":
        rank = extract_rank(message)
        if rank is None:
            return (
                "Please enter your CET rank as a number (e.g., 2500).",
                context,
            )
        context["rank"] = rank
        context["stage"] = "awaiting_category"
        return ask_for_category_message(), context

    if stage == "awaiting_category":
        category = extract_category(message)
        if category is None:
            return (
                f"Sorry, I didn't recognise that category. "
                f"Please choose one of: {', '.join(CATEGORY_LIST)}",
                context,
            )
        context["category"] = category
        context["stage"] = "awaiting_branch"
        return ask_for_branch_message(), context

    if stage == "awaiting_branch":
        branch = extract_branch(message)
        if branch is None:
            branches = predictor.get_available_branches()
            return (
                f"Sorry, I didn't recognise that branch. "
                f"Please choose one of: {', '.join(branches)}",
                context,
            )
        context["branch"] = branch
        context["stage"] = "ready"
        return run_prediction(context), context

    # --- Not currently mid-collection: classify intent normally ---
    intent = detect_intent(message)

    if intent == "GREETING":
        return greeting_response(), context

    if intent == "COUNSELLING":
        return counselling_response(), context

    if intent == "FAQ":
        answer = search_faq(message)
        return answer, context

    if intent == "PREDICTION":
        # Opportunistically pick up a rank if the user just typed one
        # (e.g. "My rank is 2500") even without saying "predict".
        rank = extract_rank(message)
        if rank is not None:
            context["rank"] = rank

        if context["rank"] is None:
            context["stage"] = "awaiting_rank"
            return "Okay. What is your CET rank (a number)?", context

        if context["category"] is None:
            context["stage"] = "awaiting_category"
            return ask_for_category_message(), context

        if context["branch"] is None:
            context["stage"] = "awaiting_branch"
            return ask_for_branch_message(), context

        # All three already known (e.g. user asks again later) - reuse them.
        context["stage"] = "ready"
        return run_prediction(context), context

    return fallback_response(), context
