"""
predictor.py

Reads the sample cutoff dataset (data/colleges.csv) and predicts
admission chance (HIGH / MEDIUM / LOW) for a given rank, category
and branch.

IMPORTANT: This uses SAMPLE / DEMONSTRATION cutoff data only.
It is NOT official current cutoff data.

Prediction rule (deterministic, no AI/ML involved):

    Let closing_rank = the stored closing rank for that
    college + branch + category.

    If student_rank <= 0.8 * closing_rank      -> HIGH
    elif student_rank <= closing_rank          -> MEDIUM
    elif student_rank <= 1.2 * closing_rank    -> LOW
    else                                       -> not shown (too far beyond cutoff)

Lower rank number = better merit (rank 1 is the best possible rank).
"""

import csv
import os

CSV_PATH = os.path.join(os.path.dirname(__file__), "data", "colleges.csv")

# Thresholds used for the HIGH / MEDIUM / LOW rule (kept as constants
# so they are easy to find and explain in a viva).
HIGH_FACTOR = 0.8
LOW_FACTOR = 1.2


def load_colleges():
    """Load all rows from colleges.csv into a list of dictionaries."""
    colleges = []
    try:
        with open(CSV_PATH, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                colleges.append(
                    {
                        "college": row["College"].strip(),
                        "branch": row["Branch"].strip(),
                        "category": row["Category"].strip(),
                        "closing_rank": int(row["Closing_Rank"]),
                    }
                )
    except FileNotFoundError:
        # Return an empty list rather than crashing; predict() will
        # then correctly report "no data available".
        return []
    return colleges


# Load once when the module is imported (small file, fine for MVP).
COLLEGE_DATA = load_colleges()


def classify(student_rank, closing_rank):
    """Return HIGH / MEDIUM / LOW / None based on the rule above."""
    if student_rank <= HIGH_FACTOR * closing_rank:
        return "HIGH"
    if student_rank <= closing_rank:
        return "MEDIUM"
    if student_rank <= LOW_FACTOR * closing_rank:
        return "LOW"
    return None  # too far beyond cutoff - not a realistic option


def predict(rank, category, branch):
    """
    Predict suitable colleges for the given rank, category and branch.

    Returns a list of dicts:
        [{"college": ..., "branch": ..., "category": ...,
          "closing_rank": ..., "result": "HIGH"/"MEDIUM"/"LOW"}, ...]

    Returns an empty list if no matching data is found.
    """
    results = []

    category_norm = category.strip().upper()
    branch_norm = branch.strip().lower()

    for row in COLLEGE_DATA:
        if row["category"].upper() != category_norm:
            continue
        if row["branch"].lower() != branch_norm:
            continue

        result = classify(rank, row["closing_rank"])
        if result is not None:
            results.append(
                {
                    "college": row["college"],
                    "branch": row["branch"],
                    "category": row["category"],
                    "closing_rank": row["closing_rank"],
                    "result": result,
                }
            )

    # Show the best (HIGH first) and most relevant options first.
    order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    results.sort(key=lambda r: (order[r["result"]], r["closing_rank"]))
    return results


def get_available_branches():
    """Return the sorted list of unique branch names in the dataset."""
    return sorted({row["branch"] for row in COLLEGE_DATA})


def get_available_categories():
    """Return the sorted list of unique category names in the dataset."""
    return sorted({row["category"] for row in COLLEGE_DATA})
