"""Tests for the flight pattern modules."""
import pytest
from pattern.bcd_travel import FLIGHT_BLOCK_PATTERN, TABLE_ROW_PATTERN
from pattern.ryanair import FLIGHT_INFO_PATTERN


# ── BCD Travel patterns ──────────────────────────────────────────────────────

BCD_FLIGHT_BLOCK = (
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
    "12A"
)

BCD_TABLE_ROW = "15 Jan 2024 LH100 FRA MUC 10:30 11:30 Economy ABC123"


class TestBCDFlightBlockPattern:
    def test_matches_valid_block(self):
        match = FLIGHT_BLOCK_PATTERN.search(BCD_FLIGHT_BLOCK)
        assert match is not None

    def test_captures_flight_number(self):
        match = FLIGHT_BLOCK_PATTERN.search(BCD_FLIGHT_BLOCK)
        assert match.group("flight_number") == "LH100"

    def test_captures_departure_airport(self):
        match = FLIGHT_BLOCK_PATTERN.search(BCD_FLIGHT_BLOCK)
        assert match.group("departure_airport") == "FRA"

    def test_captures_arrival_airport(self):
        match = FLIGHT_BLOCK_PATTERN.search(BCD_FLIGHT_BLOCK)
        assert match.group("arrival_airport") == "MUC"

    def test_captures_departure_time(self):
        match = FLIGHT_BLOCK_PATTERN.search(BCD_FLIGHT_BLOCK)
        assert match.group("departure_time") == "10:30"

    def test_captures_arrival_time(self):
        match = FLIGHT_BLOCK_PATTERN.search(BCD_FLIGHT_BLOCK)
        assert match.group("arrival_time") == "11:30"

    def test_captures_booking_reference(self):
        match = FLIGHT_BLOCK_PATTERN.search(BCD_FLIGHT_BLOCK)
        assert match.group("booking_reference") == "ABC123"

    def test_captures_aircraft(self):
        match = FLIGHT_BLOCK_PATTERN.search(BCD_FLIGHT_BLOCK)
        assert "Airbus A320" in match.group("aircraft")

    def test_captures_seat(self):
        match = FLIGHT_BLOCK_PATTERN.search(BCD_FLIGHT_BLOCK)
        assert match.group("seat") == "12A"

    def test_no_match_for_unrelated_text(self):
        assert FLIGHT_BLOCK_PATTERN.search("Hello, world!") is None


class TestBCDTableRowPattern:
    def test_matches_valid_row(self):
        match = TABLE_ROW_PATTERN.search(BCD_TABLE_ROW)
        assert match is not None

    def test_captures_date(self):
        match = TABLE_ROW_PATTERN.search(BCD_TABLE_ROW)
        assert "Jan" in match.group("date")
        assert "2024" in match.group("date")

    def test_captures_flight_number(self):
        match = TABLE_ROW_PATTERN.search(BCD_TABLE_ROW)
        assert match.group("flight_number") == "LH100"

    def test_captures_departure_airport(self):
        match = TABLE_ROW_PATTERN.search(BCD_TABLE_ROW)
        assert match.group("departure_airport") == "FRA"

    def test_captures_arrival_airport(self):
        match = TABLE_ROW_PATTERN.search(BCD_TABLE_ROW)
        assert match.group("arrival_airport") == "MUC"

    def test_captures_departure_time(self):
        match = TABLE_ROW_PATTERN.search(BCD_TABLE_ROW)
        assert match.group("departure_time") == "10:30"

    def test_captures_arrival_time(self):
        match = TABLE_ROW_PATTERN.search(BCD_TABLE_ROW)
        assert match.group("arrival_time") == "11:30"

    def test_captures_class(self):
        match = TABLE_ROW_PATTERN.search(BCD_TABLE_ROW)
        assert match.group("class") == "Economy"

    def test_captures_booking_reference(self):
        match = TABLE_ROW_PATTERN.search(BCD_TABLE_ROW)
        assert match.group("booking_reference") == "ABC123"

    def test_no_match_for_unrelated_text(self):
        assert TABLE_ROW_PATTERN.search("Hello, world!") is None


# ── Ryanair pattern ──────────────────────────────────────────────────────────

RYANAIR_FLIGHT = (
    "Flug: FR1234 "
    "Von: DUB "
    "Nach: STN "
    "Abflug: 15/01/2024 um 06:25 "
    "Ankunft: 15/01/2024 um 09:40 "
    "Klasse: Economy "
    "Buchungsnr.: XYZ789 "
    "Flugzeug: Boeing 737 "
    "Sitz: 14C"
)


class TestRyanairPattern:
    def test_matches_valid_block(self):
        match = FLIGHT_INFO_PATTERN.search(RYANAIR_FLIGHT)
        assert match is not None

    def test_captures_flight_number(self):
        match = FLIGHT_INFO_PATTERN.search(RYANAIR_FLIGHT)
        assert match.group("flight_number") == "FR1234"

    def test_captures_departure_airport(self):
        match = FLIGHT_INFO_PATTERN.search(RYANAIR_FLIGHT)
        assert match.group("departure_airport") == "DUB"

    def test_captures_arrival_airport(self):
        match = FLIGHT_INFO_PATTERN.search(RYANAIR_FLIGHT)
        assert match.group("arrival_airport") == "STN"

    def test_captures_departure_date(self):
        match = FLIGHT_INFO_PATTERN.search(RYANAIR_FLIGHT)
        assert match.group("departure_date") == "15/01/2024"

    def test_captures_departure_time(self):
        match = FLIGHT_INFO_PATTERN.search(RYANAIR_FLIGHT)
        assert match.group("departure_time") == "06:25"

    def test_captures_arrival_date(self):
        match = FLIGHT_INFO_PATTERN.search(RYANAIR_FLIGHT)
        assert match.group("arrival_date") == "15/01/2024"

    def test_captures_arrival_time(self):
        match = FLIGHT_INFO_PATTERN.search(RYANAIR_FLIGHT)
        assert match.group("arrival_time") == "09:40"

    def test_captures_class(self):
        match = FLIGHT_INFO_PATTERN.search(RYANAIR_FLIGHT)
        assert match.group("class") == "Economy"

    def test_captures_booking_reference(self):
        match = FLIGHT_INFO_PATTERN.search(RYANAIR_FLIGHT)
        assert match.group("booking_reference") == "XYZ789"

    def test_captures_aircraft(self):
        match = FLIGHT_INFO_PATTERN.search(RYANAIR_FLIGHT)
        assert "Boeing 737" in match.group("aircraft")

    def test_captures_seat(self):
        match = FLIGHT_INFO_PATTERN.search(RYANAIR_FLIGHT)
        assert match.group("seat") == "14C"

    def test_no_match_for_unrelated_text(self):
        assert FLIGHT_INFO_PATTERN.search("Hello, world!") is None


# ── pattern loader fallback warning ─────────────────────────────────────────

class TestPatternLoaderWarning:
    """Verify that a warning is logged when the configured pattern module is missing."""

    def test_get_flight_info_pattern_warns_on_missing_module(self, caplog):
        import logging
        from unittest.mock import patch
        import pattern as pattern_pkg
        with patch("pattern.Config") as mock_cfg:
            mock_cfg.FLIGHT_PATTERN_FILE = "nonexistent_module"
            with caplog.at_level(logging.WARNING, logger="pattern"):
                pattern_pkg.get_flight_info_pattern()
        assert any("nonexistent_module" in r.message for r in caplog.records)

    def test_get_table_row_pattern_warns_on_missing_module(self, caplog):
        import logging
        from unittest.mock import patch
        import pattern as pattern_pkg
        with patch("pattern.Config") as mock_cfg:
            mock_cfg.FLIGHT_PATTERN_FILE = "nonexistent_module"
            with caplog.at_level(logging.WARNING, logger="pattern"):
                pattern_pkg.get_table_row_pattern()
        assert any("nonexistent_module" in r.message for r in caplog.records)
