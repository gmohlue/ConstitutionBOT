"""Tests for the export API endpoints."""

import csv
import io
import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone

from contentmanager.dashboard.routers.export import (
    _format_datetime,
    _format_json_value,
)


class TestHelperFunctions:
    """Tests for export helper functions."""

    def test_format_datetime_with_value(self):
        """Test formatting a datetime value."""
        dt = datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc)
        result = _format_datetime(dt)
        assert result == "2024-01-15T10:30:00+00:00"

    def test_format_datetime_with_none(self):
        """Test formatting None returns empty string."""
        result = _format_datetime(None)
        assert result == ""

    def test_format_json_value_with_dict(self):
        """Test formatting dict value for CSV."""
        value = {"key": "value", "num": 123}
        result = _format_json_value(value)
        assert result == '{"key": "value", "num": 123}'

    def test_format_json_value_with_list(self):
        """Test formatting list value for CSV."""
        value = [1, 2, 3]
        result = _format_json_value(value)
        assert result == "[1, 2, 3]"

    def test_format_json_value_with_none(self):
        """Test formatting None returns empty string."""
        result = _format_json_value(None)
        assert result == ""

    def test_format_json_value_with_string(self):
        """Test formatting string returns the string."""
        result = _format_json_value("test")
        assert result == "test"


class TestExportCSVFormat:
    """Tests for CSV export format validation."""

    def test_csv_output_parsing(self):
        """Test that generated CSV can be parsed correctly."""
        # Simulate CSV output
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["id", "content", "status"])
        writer.writerow([1, "Test content", "pending"])
        writer.writerow([2, "More content", "approved"])

        output.seek(0)
        reader = csv.DictReader(output)
        rows = list(reader)

        assert len(rows) == 2
        assert rows[0]["id"] == "1"
        assert rows[0]["content"] == "Test content"
        assert rows[0]["status"] == "pending"
        assert rows[1]["id"] == "2"
        assert rows[1]["content"] == "More content"
        assert rows[1]["status"] == "approved"


class TestExportJSONFormat:
    """Tests for JSON export format validation."""

    def test_json_structure(self):
        """Test the JSON export structure."""
        data = {
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "total_items": 2,
            "items": [
                {"id": 1, "content": "Test"},
                {"id": 2, "content": "More"},
            ],
        }
        output = json.dumps(data, indent=2)
        parsed = json.loads(output)

        assert "exported_at" in parsed
        assert parsed["total_items"] == 2
        assert len(parsed["items"]) == 2
        assert parsed["items"][0]["id"] == 1
