
import re


# Explicit aliases prevent common wording variations from
# being incorrectly reported as scope changes.
ALIASES = {
    "backend development": "backend",
    "back-end development": "backend",
    "back end development": "backend",
    "frontend development": "frontend",
    "front-end development": "frontend",
    "front end development": "frontend",
    "database setup": "database",
    "email notification system": "email notifications",
    "user account management": "customer accounts",
    "customer account management": "customer accounts",
    "user authentication": "authentication",
    "customer login": "login",
    "log in": "login",
    "website design": "website design",
}


def normalize_text(value: str) -> str:
    text = str(value).strip().casefold()
    text = re.sub(r"[^\w\s-]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return ALIASES.get(text, text)


def compare_items(old_items: list, new_items: list) -> tuple:
    """Compare items after applying explicit wording aliases."""

    old_map = {}
    new_map = {}

    for item in old_items:
        text = str(item).strip()
        key = normalize_text(text)
        if key:
            old_map.setdefault(key, text)

    for item in new_items:
        text = str(item).strip()
        key = normalize_text(text)
        if key:
            new_map.setdefault(key, text)

    added = [
        new_map[key]
        for key in sorted(new_map.keys() - old_map.keys())
    ]
    removed = [
        old_map[key]
        for key in sorted(old_map.keys() - new_map.keys())
    ]

    return added, removed


def compare_scopes(
    previous_scope: dict,
    updated_scope: dict,
) -> dict:
    """Compare two project scopes and identify changes."""

    old_analysis = previous_scope.get("meeting_analysis", {})
    new_analysis = updated_scope.get("meeting_analysis", {})

    added, removed = compare_items(
        old_analysis.get("requirements", []),
        new_analysis.get("requirements", []),
    )

    added_deliverables, removed_deliverables = compare_items(
        previous_scope.get("deliverables", []),
        updated_scope.get("deliverables", []),
    )

    def calculate_hours(scope: dict) -> float:
        total = 0.0
        for task in scope.get("tasks", []):
            try:
                total += float(task.get("estimate_hours", 0) or 0)
            except (TypeError, ValueError):
                pass
        return total

    old_hours = calculate_hours(previous_scope)
    new_hours = calculate_hours(updated_scope)

    return {
        "added_requirements": added,
        "removed_requirements": removed,
        "added_deliverables": added_deliverables,
        "removed_deliverables": removed_deliverables,
        "previous_estimated_hours": old_hours,
        "updated_estimated_hours": new_hours,
        "estimate_change_hours": new_hours - old_hours,
        "possible_scope_change": bool(
            added or removed or added_deliverables or removed_deliverables
        ),
        "approval_required": True,
    }

