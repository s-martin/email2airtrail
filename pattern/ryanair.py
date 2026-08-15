import re

# Ryanair emails embed all flight details in a single block; there is no
# separate summary table, so TABLE_ROW_PATTERN reuses FLIGHT_INFO_PATTERN.
# It is defined first so FLIGHT_INFO_PATTERN can reference it below.

# Regex pattern for Ryanair emails
FLIGHT_INFO_PATTERN = re.compile(
    r"Flug:\s*(?P<flight_number>[A-Z0-9]+)\s*"
    r"Von:\s*(?P<departure_airport>[A-Z]{3})\s*"
    r"Nach:\s*(?P<arrival_airport>[A-Z]{3})\s*"
    r"Abflug:\s*(?P<departure_date>\d{2}/\d{2}/\d{4})\s*um\s*(?P<departure_time>\d{2}:\d{2})\s*"
    r"Ankunft:\s*(?P<arrival_date>\d{2}/\d{2}/\d{4})\s*um\s*(?P<arrival_time>\d{2}:\d{2})\s*"
    r"Klasse:\s*(?P<class>[A-Za-z]+)\s*"
    r"Buchungsnr\.:?\s*(?P<booking_reference>[A-Z0-9]+)\s*"
    r"Flugzeug:\s*(?P<aircraft>[A-Za-z0-9\s]+)\s*"
    r"Sitz:\s*(?P<seat>[A-Z0-9]+)"
)

# Ryanair has no separate summary table; alias to FLIGHT_INFO_PATTERN.
FLIGHT_BLOCK_PATTERN = FLIGHT_INFO_PATTERN
TABLE_ROW_PATTERN = FLIGHT_INFO_PATTERN
