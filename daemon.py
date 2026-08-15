import imaplib
import email
import re
import requests
import schedule
import time
import logging
from datetime import datetime
from bs4 import BeautifulSoup
from config import Config
from pattern import get_flight_info_pattern, get_table_row_pattern

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/daemon.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load the flight info pattern dynamically
FLIGHT_BLOCK_PATTERN = get_flight_info_pattern()
TABLE_ROW_PATTERN = get_table_row_pattern()


def extract_text_from_html(html):
    """Extract text from HTML."""
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text()


def extract_flight_info(email_body):
    """Extract flight information from BCD Travel emails."""
    # Search for flight blocks
    flight_blocks = FLIGHT_BLOCK_PATTERN.finditer(email_body)
    flights = []

    for block in flight_blocks:
        flight_info = block.groupdict()

        # Search for the class in the table
        table_matches = TABLE_ROW_PATTERN.finditer(email_body)
        for table_match in table_matches:
            table_info = table_match.groupdict()
            if table_info["flight_number"] == flight_info["flight_number"]:
                flight_info["class"] = table_info["class"]
                flight_info["date"] = table_info["date"]
                break

        # Convert date and time to ISO format
        try:
            departure_datetime = datetime.strptime(
                f"{flight_info['date']} {flight_info['departure_time']}",
                "%d %b %Y %H:%M"
            ).isoformat()
            arrival_datetime = datetime.strptime(
                f"{flight_info['date']} {flight_info['arrival_time']}",
                "%d %b %Y %H:%M"
            ).isoformat()
        except ValueError:
            logger.error(
                f"Error parsing date or time for flight {flight_info.get('flight_number', 'Unknown')}"
            )
            continue

        flights.append({
            "flightNumber": flight_info["flight_number"],
            "departureAirport": flight_info["departure_airport"],
            "arrivalAirport": flight_info["arrival_airport"],
            "departureTime": departure_datetime,
            "arrivalTime": arrival_datetime,
            "class": flight_info.get("class", "Unknown"),
            "bookingReference": flight_info["booking_reference"],
            "aircraft": flight_info["aircraft"],
            "seat": flight_info["seat"],
        })

    return flights if flights else None


def flight_exists(flight_number, departure_time):
    """Check whether the flight already exists in AirTrail."""
    headers = {"Authorization": f"Bearer {Config.AIRTRAIL_API_KEY}"}
    try:
        response = requests.get(
            f"{Config.AIRTRAIL_API_URL}?flightNumber={flight_number}&departureTime={departure_time}",
            headers=headers
        )
        if response.status_code == 200:
            flights = response.json()
            return any(
                flight.get("flightNumber") == flight_number and
                flight.get("departureTime") == departure_time
                for flight in flights
            )
        else:
            logger.error(f"Error querying AirTrail: {response.text}")
            return False
    except Exception as e:
        logger.error(f"API error during duplicate check: {e}")
        return False


def send_to_airtrail(flight_data):
    """Send flight data to the AirTrail API."""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {Config.AIRTRAIL_API_KEY}"
    }
    try:
        response = requests.post(
            Config.AIRTRAIL_API_URL,
            json=flight_data,
            headers=headers
        )
        if response.status_code in (200, 201):
            logger.info(
                f"Flight {flight_data['flightNumber']} successfully inserted into AirTrail."
            )
            return True
        else:
            logger.error(f"Error inserting into AirTrail: {response.text}")
            return False
    except Exception as e:
        logger.error(f"API error: {e}")
        return False


def build_imap_search_query():
    """Build the IMAP search query for multiple senders."""
    if not Config.EMAIL_SENDERS:
        return 'UNSEEN'

    from_clauses = [f'FROM "{sender.strip()}"' for sender in Config.EMAIL_SENDERS]
    if len(from_clauses) == 1:
        return f'UNSEEN ({from_clauses[0]})'
    # IMAP OR is binary; nest pairs right-to-left for 3+ operands
    result = from_clauses[-1]
    for clause in reversed(from_clauses[:-1]):
        result = f'OR ({clause}) ({result})'
    return f'UNSEEN ({result})'


def fetch_emails():
    """Fetch new emails and process them."""
    try:
        mail = imaplib.IMAP4_SSL(Config.IMAP_SERVER, Config.IMAP_PORT)
        mail.login(Config.EMAIL_ADDRESS, Config.EMAIL_PASSWORD)
        mail.select("inbox")

        # Search for unread emails from configured senders
        search_query = build_imap_search_query()
        status, messages = mail.search(None, search_query)
        if status != "OK":
            logger.info("No new emails found from configured senders.")
            return

        email_ids = messages[0].split()
        for email_id in email_ids:
            # Fetch email
            status, msg_data = mail.fetch(email_id, "(RFC822)")
            if status != "OK":
                continue

            raw_email = msg_data[0][1]
            email_message = email.message_from_bytes(raw_email)
            email_body = ""

            # Extract text from plain text or HTML
            if email_message.is_multipart():
                for part in email_message.walk():
                    content_type = part.get_content_type()
                    if content_type == "text/plain":
                        email_body += part.get_payload(decode=True).decode()
                    elif content_type == "text/html":
                        email_body += extract_text_from_html(part.get_payload(decode=True).decode())
            else:
                if email_message.get_content_type() == "text/html":
                    email_body = extract_text_from_html(email_message.get_payload(decode=True).decode())
                else:
                    email_body = email_message.get_payload(decode=True).decode()

            # Extract flight information
            flights = extract_flight_info(email_body)
            if flights:
                logger.info(f"Flight info found: {flights}")

                all_succeeded = True
                for flight in flights:
                    # Check whether the flight already exists
                    if flight_exists(flight["flightNumber"], flight["departureTime"]):
                        logger.info(f"Flight {flight['flightNumber']} already exists in AirTrail.")
                    else:
                        # Insert the flight into AirTrail
                        if send_to_airtrail(flight):
                            logger.info(f"Flight {flight['flightNumber']} inserted into AirTrail.")
                        else:
                            logger.error(f"Flight {flight['flightNumber']} could not be inserted into AirTrail.")
                            all_succeeded = False

                if all_succeeded:
                    # Mark the email as read only after all flights have been processed
                    mail.store(email_id, '+FLAGS', '\\Seen')
                    logger.info("Email marked as read.")

        mail.close()
        mail.logout()
    except Exception as e:
        logger.error(f"Email error: {e}")


def run_daemon():
    """Run the daemon."""
    logger.info(f"Daemon started. Monitoring emails every {Config.CHECK_INTERVAL_MINUTES} minutes...")
    fetch_emails()


# Schedule the daemon
schedule.every(Config.CHECK_INTERVAL_MINUTES).minutes.do(run_daemon)

if __name__ == "__main__":
    run_daemon()  # Run immediately
    while True:
        schedule.run_pending()
        time.sleep(1)
