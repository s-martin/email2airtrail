import importlib
from config import Config


def get_flight_info_pattern():
    """Load the configured flight info pattern."""
    try:
        pattern_module = importlib.import_module(f"pattern.{Config.FLIGHT_PATTERN_FILE}")
        return pattern_module.FLIGHT_BLOCK_PATTERN
    except ImportError:
        # Fallback to the default pattern (bcd_travel)
        from pattern.bcd_travel import FLIGHT_BLOCK_PATTERN
        return FLIGHT_BLOCK_PATTERN


def get_table_row_pattern():
    """Load the configured table row pattern."""
    try:
        pattern_module = importlib.import_module(f"pattern.{Config.FLIGHT_PATTERN_FILE}")
        return pattern_module.TABLE_ROW_PATTERN
    except ImportError:
        # Fallback to the default pattern (bcd_travel)
        from pattern.bcd_travel import TABLE_ROW_PATTERN
        return TABLE_ROW_PATTERN
