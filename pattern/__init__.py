import importlib
import logging
from config import Config

logger = logging.getLogger(__name__)


def get_flight_info_pattern():
    """Load the configured flight info pattern."""
    try:
        pattern_module = importlib.import_module(f"pattern.{Config.FLIGHT_PATTERN_FILE}")
        return pattern_module.FLIGHT_BLOCK_PATTERN
    except ImportError:
        logger.warning(
            "Pattern module 'pattern.%s' not found; falling back to bcd_travel.",
            Config.FLIGHT_PATTERN_FILE,
        )
        from pattern.bcd_travel import FLIGHT_BLOCK_PATTERN
        return FLIGHT_BLOCK_PATTERN


def get_table_row_pattern():
    """Load the configured table row pattern."""
    try:
        pattern_module = importlib.import_module(f"pattern.{Config.FLIGHT_PATTERN_FILE}")
        return pattern_module.TABLE_ROW_PATTERN
    except ImportError:
        logger.warning(
            "Pattern module 'pattern.%s' not found; falling back to bcd_travel.",
            Config.FLIGHT_PATTERN_FILE,
        )
        from pattern.bcd_travel import TABLE_ROW_PATTERN
        return TABLE_ROW_PATTERN
