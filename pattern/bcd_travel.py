import re

# Regex for flight blocks
FLIGHT_BLOCK_PATTERN = re.compile(
    r"Flug - .*?\n"
    r"(?P<flight_number>[A-Z0-9]+)\s*\(.*?\)\s*\n"
    r"Lufthansa\s*\n"
    r"LH Buchungsreferenz:\s*(?P<booking_reference>[A-Z0-9]+)\s*\n"
    r"Abreise:\s*\n"
    r".*?\n"
    r"(?P<departure_airport>[A-Z]{3}),\s*Terminal\s*\d+\s*\n"
    r".*?\n"
    r"(?P<departure_time>\d{2}:\d{2})\s*\n"
    r"Ankunft:\s*\n"
    r".*?\n"
    r"(?P<arrival_airport>[A-Z]{3}),\s*Terminal\s*\d+\(.*?\)\s*\n"
    r".*?\n"
    r"(?P<arrival_time>\d{2}:\d{2})\s*\n"
    r"Fluggerät:\s*\n"
    r"(?P<aircraft>[A-Za-z0-9\s\(\)]+)\s*\n"
    r"Sitzplatz:\s*\n"
    r"(?P<seat>[A-Z0-9]+)"
)

# Regex for table rows (class, date, etc.)
TABLE_ROW_PATTERN = re.compile(
    r"(?P<date>\d{2}\s*[A-Za-z]+\s*\d{4})\s*"
    r"(?P<flight_number>[A-Z0-9]+)\s*"
    r"(?P<departure_airport>[A-Z]{3})\s*"
    r"(?P<arrival_airport>[A-Z]{3})\s*"
    r"(?P<departure_time>\d{2}:\d{2})\s*"
    r"(?P<arrival_time>\d{2}:\d{2})\s*"
    r"(?P<class>[A-Za-z]+)\s*"
    r"(?P<booking_reference>[A-Z0-9]+)"
)
