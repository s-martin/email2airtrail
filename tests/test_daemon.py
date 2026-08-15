"""Tests for daemon.py helper functions."""
import os
import sys
import pytest
from unittest.mock import MagicMock, patch

# Ensure the repo root is on the path so that daemon.py's imports work
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Prevent the module-level schedule.every() call and IMAP connections from
# running at import time by providing stub environment variables.
os.environ.setdefault("IMAP_SERVER", "imap.example.com")
os.environ.setdefault("EMAIL_ADDRESS", "test@example.com")
os.environ.setdefault("EMAIL_PASSWORD", "secret")
os.environ.setdefault("AIRTRAIL_API_URL", "http://localhost/api/flights")
os.environ.setdefault("AIRTRAIL_API_KEY", "testkey")
os.environ.setdefault("CHECK_INTERVAL_MINUTES", "10")
os.environ.setdefault("FLIGHT_PATTERN_FILE", "bcd_travel")

# Patch schedule and the file logger before importing daemon
import schedule  # noqa: E402  (needed before daemon import)
with patch("builtins.open", MagicMock()), \
        patch("logging.FileHandler", MagicMock()):
    import daemon  # noqa: E402


# ── extract_text_from_html ───────────────────────────────────────────────────

class TestExtractTextFromHtml:
    def test_plain_text_preserved(self):
        html = "<p>Hello World</p>"
        result = daemon.extract_text_from_html(html)
        assert "Hello World" in result

    def test_tags_stripped(self):
        html = "<b>Bold</b> <i>Italic</i>"
        result = daemon.extract_text_from_html(html)
        assert "<b>" not in result
        assert "Bold" in result
        assert "Italic" in result

    def test_empty_html(self):
        assert daemon.extract_text_from_html("") == ""

    def test_nested_html(self):
        html = "<div><span>Nested <strong>text</strong></span></div>"
        result = daemon.extract_text_from_html(html)
        assert "Nested" in result
        assert "text" in result

    def test_html_entities_decoded(self):
        html = "<p>Frankfurt &amp; München</p>"
        result = daemon.extract_text_from_html(html)
        assert "&amp;" not in result
        assert "Frankfurt" in result


# ── extract_flight_info ──────────────────────────────────────────────────────

BCD_EMAIL_BODY = (
    "Flug - Frankfurt → München\n"
    "LH100 (Economy)\n"
    "Lufthansa\n"
    "LH Buchungsreferenz: ABC123\n"
    "Abreise:\n"
    "Frankfurt am Main\n"
    "FRA, Terminal 1\n"
    "2024-01-15\n"
    "10:30\n"
    "Ankunft:\n"
    "München\n"
    "MUC, Terminal 2(International)\n"
    "2024-01-15\n"
    "11:30\n"
    "Fluggerät:\n"
    "Airbus A320\n"
    "Sitzplatz:\n"
    "12A\n"
    "\n"
    "15 Jan 2024 LH100 FRA MUC 10:30 11:30 Economy ABC123\n"
)

# Overnight flight: departs 22:00, arrives 01:30 next day
BCD_EMAIL_BODY_OVERNIGHT = (
    "Flug - Frankfurt → New York\n"
    "LH400 (Economy)\n"
    "Lufthansa\n"
    "LH Buchungsreferenz: XYZ789\n"
    "Abreise:\n"
    "Frankfurt am Main\n"
    "FRA, Terminal 1\n"
    "2024-01-15\n"
    "22:00\n"
    "Ankunft:\n"
    "New York JFK\n"
    "JFK, Terminal 1(International)\n"
    "2024-01-15\n"
    "01:30\n"
    "Fluggerät:\n"
    "Boeing 747\n"
    "Sitzplatz:\n"
    "30A\n"
    "\n"
    "15 Jan 2024 LH400 FRA JFK 22:00 01:30 Economy XYZ789\n"
)


class TestExtractFlightInfo:
    def test_returns_none_for_empty_body(self):
        assert daemon.extract_flight_info("") is None

    def test_returns_none_for_unrelated_text(self):
        assert daemon.extract_flight_info("No flight info here.") is None

    def test_extracts_flight_from_bcd_email(self):
        flights = daemon.extract_flight_info(BCD_EMAIL_BODY)
        assert flights is not None
        assert len(flights) == 1

    def test_flight_number(self):
        flights = daemon.extract_flight_info(BCD_EMAIL_BODY)
        assert flights[0]["flightNumber"] == "LH100"

    def test_departure_airport(self):
        flights = daemon.extract_flight_info(BCD_EMAIL_BODY)
        assert flights[0]["departureAirport"] == "FRA"

    def test_arrival_airport(self):
        flights = daemon.extract_flight_info(BCD_EMAIL_BODY)
        assert flights[0]["arrivalAirport"] == "MUC"

    def test_departure_time_is_iso(self):
        flights = daemon.extract_flight_info(BCD_EMAIL_BODY)
        assert "2024-01-15T10:30:00" == flights[0]["departureTime"]

    def test_arrival_time_is_iso(self):
        flights = daemon.extract_flight_info(BCD_EMAIL_BODY)
        assert "2024-01-15T11:30:00" == flights[0]["arrivalTime"]

    def test_booking_reference(self):
        flights = daemon.extract_flight_info(BCD_EMAIL_BODY)
        assert flights[0]["bookingReference"] == "ABC123"

    def test_seat(self):
        flights = daemon.extract_flight_info(BCD_EMAIL_BODY)
        assert flights[0]["seat"] == "12A"

    def test_class_from_table_row(self):
        flights = daemon.extract_flight_info(BCD_EMAIL_BODY)
        assert flights[0]["class"] == "Economy"

    def test_aircraft(self):
        flights = daemon.extract_flight_info(BCD_EMAIL_BODY)
        assert "Airbus A320" in flights[0]["aircraft"]


class TestExtractFlightInfoOvernight:
    def test_overnight_arrival_date_advances_by_one_day(self):
        flights = daemon.extract_flight_info(BCD_EMAIL_BODY_OVERNIGHT)
        assert flights is not None
        assert flights[0]["arrivalTime"].startswith("2024-01-16")

    def test_overnight_departure_date_unchanged(self):
        flights = daemon.extract_flight_info(BCD_EMAIL_BODY_OVERNIGHT)
        assert flights is not None
        assert flights[0]["departureTime"].startswith("2024-01-15")

    def test_overnight_arrival_time_correct(self):
        flights = daemon.extract_flight_info(BCD_EMAIL_BODY_OVERNIGHT)
        assert flights is not None
        assert flights[0]["arrivalTime"] == "2024-01-16T01:30:00"


# ── build_imap_search_query ──────────────────────────────────────────────────

class TestBuildImapSearchQuery:
    def test_no_senders_returns_unseen(self):
        # An empty list triggers the early-return; [""] (default) does not.
        with patch.object(daemon.Config, "EMAIL_SENDERS", []):
            result = daemon.build_imap_search_query()
        assert result == "UNSEEN"

    def test_single_sender(self):
        with patch.object(daemon.Config, "EMAIL_SENDERS", ["travel@bcd.com"]):
            result = daemon.build_imap_search_query()
        assert 'FROM "travel@bcd.com"' in result
        assert "UNSEEN" in result

    def test_multiple_senders_uses_or(self):
        with patch.object(daemon.Config, "EMAIL_SENDERS", ["a@a.com", "b@b.com"]):
            result = daemon.build_imap_search_query()
        assert result == 'UNSEEN (OR (FROM "a@a.com") (FROM "b@b.com"))'

    def test_three_senders_uses_nested_or(self):
        with patch.object(daemon.Config, "EMAIL_SENDERS", ["a@a.com", "b@b.com", "c@c.com"]):
            result = daemon.build_imap_search_query()
        assert result == 'UNSEEN (OR (FROM "a@a.com") (OR (FROM "b@b.com") (FROM "c@c.com")))'

    def test_strips_whitespace_from_sender(self):
        with patch.object(daemon.Config, "EMAIL_SENDERS", [" travel@bcd.com "]):
            result = daemon.build_imap_search_query()
        assert 'FROM "travel@bcd.com"' in result


# ── flight_exists ────────────────────────────────────────────────────────────

class TestFlightExists:
    def _make_response(self, status_code, json_data):
        resp = MagicMock()
        resp.status_code = status_code
        resp.json.return_value = json_data
        resp.text = str(json_data)
        return resp

    def test_returns_true_when_flight_found(self):
        flights = [{"flightNumber": "LH100", "departureTime": "2024-01-15T10:30:00"}]
        with patch("daemon.requests.get", return_value=self._make_response(200, flights)):
            assert daemon.flight_exists("LH100", "2024-01-15T10:30:00") is True

    def test_returns_false_when_flight_not_in_list(self):
        flights = [{"flightNumber": "LH200", "departureTime": "2024-01-15T10:30:00"}]
        with patch("daemon.requests.get", return_value=self._make_response(200, flights)):
            assert daemon.flight_exists("LH100", "2024-01-15T10:30:00") is False

    def test_returns_false_on_non_200(self):
        with patch("daemon.requests.get", return_value=self._make_response(500, [])):
            assert daemon.flight_exists("LH100", "2024-01-15T10:30:00") is False

    def test_returns_false_on_exception(self):
        with patch("daemon.requests.get", side_effect=Exception("network error")):
            assert daemon.flight_exists("LH100", "2024-01-15T10:30:00") is False

    def test_empty_response_list(self):
        with patch("daemon.requests.get", return_value=self._make_response(200, [])):
            assert daemon.flight_exists("LH100", "2024-01-15T10:30:00") is False

    def test_sends_bearer_api_key_header(self):
        flights = [{"flightNumber": "LH100", "departureTime": "2024-01-15T10:30:00"}]
        with patch("daemon.requests.get", return_value=self._make_response(200, flights)) as mock_get:
            daemon.flight_exists("LH100", "2024-01-15T10:30:00")
            headers = mock_get.call_args[1]["headers"]
        expected = f"Bearer {daemon.Config.AIRTRAIL_API_KEY}"
        assert headers.get("Authorization") == expected


# ── send_to_airtrail ─────────────────────────────────────────────────────────

SAMPLE_FLIGHT = {
    "flightNumber": "LH100",
    "departureAirport": "FRA",
    "arrivalAirport": "MUC",
    "departureTime": "2024-01-15T10:30:00",
    "arrivalTime": "2024-01-15T11:30:00",
    "class": "Economy",
    "bookingReference": "ABC123",
    "aircraft": "Airbus A320",
    "seat": "12A",
}


class TestSendToAirtrail:
    def _make_response(self, status_code):
        resp = MagicMock()
        resp.status_code = status_code
        resp.text = "ok"
        return resp

    def test_returns_true_on_200(self):
        with patch("daemon.requests.post", return_value=self._make_response(200)):
            assert daemon.send_to_airtrail(SAMPLE_FLIGHT) is True

    def test_returns_true_on_201(self):
        with patch("daemon.requests.post", return_value=self._make_response(201)):
            assert daemon.send_to_airtrail(SAMPLE_FLIGHT) is True

    def test_returns_false_on_400(self):
        with patch("daemon.requests.post", return_value=self._make_response(400)):
            assert daemon.send_to_airtrail(SAMPLE_FLIGHT) is False

    def test_returns_false_on_exception(self):
        with patch("daemon.requests.post", side_effect=Exception("timeout")):
            assert daemon.send_to_airtrail(SAMPLE_FLIGHT) is False

    def test_posts_to_configured_url(self):
        with patch("daemon.requests.post", return_value=self._make_response(201)) as mock_post:
            daemon.send_to_airtrail(SAMPLE_FLIGHT)
            call_url = mock_post.call_args[0][0]
        assert call_url == daemon.Config.AIRTRAIL_API_URL

    def test_sends_correct_flight_number(self):
        with patch("daemon.requests.post", return_value=self._make_response(201)) as mock_post:
            daemon.send_to_airtrail(SAMPLE_FLIGHT)
            posted_data = mock_post.call_args[1]["json"]
        assert posted_data["flightNumber"] == "LH100"
    def test_sends_bearer_api_key_header(self):
        with patch("daemon.requests.post", return_value=self._make_response(201)) as mock_post:
            daemon.send_to_airtrail(SAMPLE_FLIGHT)
            headers = mock_post.call_args[1]["headers"]
        expected = f"Bearer {daemon.Config.AIRTRAIL_API_KEY}"
        assert headers.get("Authorization") == expected


# ── timeout parameter ────────────────────────────────────────────────────────

class TestRequestTimeouts:
    """Verify that HTTP calls include a timeout parameter."""

    def _make_response(self, status_code, json_data=None):
        resp = MagicMock()
        resp.status_code = status_code
        resp.json.return_value = json_data or []
        resp.text = ""
        return resp

    def test_flight_exists_passes_timeout(self):
        with patch("daemon.requests.get", return_value=self._make_response(200, [])) as mock_get:
            daemon.flight_exists("LH100", "2024-01-15T10:30:00")
            _, kwargs = mock_get.call_args
        assert "timeout" in kwargs

    def test_send_to_airtrail_passes_timeout(self):
        with patch("daemon.requests.post", return_value=self._make_response(201)) as mock_post:
            daemon.send_to_airtrail(SAMPLE_FLIGHT)
            _, kwargs = mock_post.call_args
        assert "timeout" in kwargs
