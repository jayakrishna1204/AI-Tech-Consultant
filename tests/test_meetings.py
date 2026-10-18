
import pytest

from task3_meeting_scope.scope_diff import (
    normalize_text,
    compare_items,
    compare_scopes,
)
from task3_meeting_scope.agents import extract_json


def test_normalize_text_ignores_case_and_extra_spaces():
    assert normalize_text("  BACKEND   DEVELOPMENT ") == "backend"


def test_normalize_text_handles_known_aliases():
    assert normalize_text("Frontend Development") == "frontend"
    assert normalize_text("Back-end development") == "backend"


def test_compare_items_detects_added_and_removed_items():
    added, removed = compare_items(
        ["Backend", "Email Notifications"],
        ["Backend", "Shopping Cart"],
    )

    assert added == ["Shopping Cart"]
    assert removed == ["Email Notifications"]


def test_compare_items_ignores_duplicate_items():
    added, removed = compare_items(
        ["Backend", "Backend"],
        ["Backend"],
    )

    assert added == []
    assert removed == []


def test_compare_scopes_detects_scope_changes():
    previous = {
        "meeting_analysis": {
            "requirements": ["Backend", "Email Notifications"]
        },
        "deliverables": ["Admin Dashboard"],
        "tasks": [{"estimate_hours": 10}],
    }

    updated = {
        "meeting_analysis": {
            "requirements": ["Backend", "Shopping Cart"]
        },
        "deliverables": ["Customer Dashboard"],
        "tasks": [{"estimate_hours": 15}],
    }

    result = compare_scopes(previous, updated)

    assert result["added_requirements"] == ["Shopping Cart"]
    assert result["removed_requirements"] == ["Email Notifications"]
    assert result["added_deliverables"] == ["Customer Dashboard"]
    assert result["removed_deliverables"] == ["Admin Dashboard"]
    assert result["previous_estimated_hours"] == 10
    assert result["updated_estimated_hours"] == 15
    assert result["estimate_change_hours"] == 5
    assert result["possible_scope_change"] is True
    assert result["approval_required"] is True


def test_compare_scopes_accepts_equivalent_wording():
    previous = {
        "meeting_analysis": {
            "requirements": ["Backend Development"]
        },
        "deliverables": [],
        "tasks": [{"estimate_hours": 20}],
    }

    updated = {
        "meeting_analysis": {
            "requirements": ["Backend"]
        },
        "deliverables": [],
        "tasks": [{"estimate_hours": 25}],
    }

    result = compare_scopes(previous, updated)

    assert result["added_requirements"] == []
    assert result["removed_requirements"] == []
    assert result["possible_scope_change"] is False
    assert result["estimate_change_hours"] == 5
    assert result["approval_required"] is True


def test_compare_scopes_handles_invalid_estimates():
    previous = {
        "meeting_analysis": {"requirements": []},
        "deliverables": [],
        "tasks": [
            {"estimate_hours": "invalid"},
            {"estimate_hours": 5},
        ],
    }

    updated = {
        "meeting_analysis": {"requirements": []},
        "deliverables": [],
        "tasks": [{"estimate_hours": 8}],
    }

    result = compare_scopes(previous, updated)

    assert result["previous_estimated_hours"] == 5
    assert result["updated_estimated_hours"] == 8
    assert result["estimate_change_hours"] == 3


def test_extract_json_parses_plain_json():
    result = extract_json('{"requirements": ["Login"], "approval_required": true}')

    assert result["requirements"] == ["Login"]
    assert result["approval_required"] is True


def test_extract_json_parses_markdown_fenced_json():
    result = extract_json(
        '```json\n{"project_summary": "Website"}\n```'
    )

    assert result["project_summary"] == "Website"


def test_extract_json_finds_json_inside_text():
    result = extract_json(
        'Result follows: {"project_summary": "Store"} complete.'
    )

    assert result["project_summary"] == "Store"


def test_extract_json_rejects_invalid_input():
    with pytest.raises(ValueError):
        extract_json("This is not JSON")


def test_extract_json_rejects_empty_input():
    with pytest.raises(ValueError):
        extract_json("")
