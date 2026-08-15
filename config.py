import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Email
    IMAP_SERVER = os.getenv("IMAP_SERVER")
    IMAP_PORT = int(os.getenv("IMAP_PORT", 993))
    EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

    # AirTrail
    AIRTRAIL_API_URL = os.getenv("AIRTRAIL_API_URL")
    AIRTRAIL_API_KEY = os.getenv("AIRTRAIL_API_KEY")

    # Daemon
    CHECK_INTERVAL_MINUTES = int(os.getenv("CHECK_INTERVAL_MINUTES", 10))

    # Pattern configuration
    FLIGHT_PATTERN_FILE = os.getenv("FLIGHT_PATTERN_FILE", "bcd_travel")

    # Email senders (comma-separated)
    EMAIL_SENDERS = [s for s in (s.strip() for s in os.getenv("EMAIL_SENDERS", "").split(",")) if s]
