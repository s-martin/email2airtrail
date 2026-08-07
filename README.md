# Email2AirTrail

![GitHub Container Registry](https://img.shields.io/badge/Container%20Registry-ghcr.io-blue)

A **Docker-based daemon** that monitors an IMAP inbox for emails from configured senders, extracts flight information, and inserts it into an **AirTrail** instance.

This daemon is designed to:

- Monitor an IMAP inbox for new emails from specified senders.
- Extract flight details such as flight number, departure/arrival times, airport codes, class, booking reference, aircraft, and seat.
- Insert the extracted flight information into an **AirTrail** instance via its API.
- Avoid duplicate entries by checking if the flight already exists in AirTrail.
- Mark processed emails as read.
- Support multiple email senders for monitoring.

## Features

- **Email Monitoring**: Continuously checks an IMAP inbox for new emails from configured senders.
- **Flight Information Extraction**: Uses regex patterns to extract flight details from emails.
- **AirTrail Integration**: Sends extracted flight data to an AirTrail instance using its API.
- **Duplicate Check**: Ensures that the same flight is not inserted multiple times.
- **Mark as Read**: Marks emails as read after processing.
- **Configurable Senders**: Allows monitoring emails from multiple senders.
- **Dynamic Pattern Loading**: Supports different email formats by loading the appropriate regex pattern.

## Prerequisites

Before you begin, ensure you have the following:

- **Docker** and **Docker Compose** installed on your system.
- **IMAP Access**: Your email account must support IMAP access.
- **AirTrail Instance**: You need access to an AirTrail instance with a valid API key.

## Installation

### 1. Clone or Download the Project

Clone the repository or download the project files to your local machine:

```bash
git clone https://github.com/s-martin/email2airtrail
```

### 2. Download the Compose File and Example Environment

If you want to fetch the example compose file and environment template directly from GitHub, you can use:

```bash
wget -O docker-compose.yml https://raw.githubusercontent.com/s-martin/email2airtrail/main/docker-compose.yml
wget -O eample.env https://raw.githubusercontent.com/s-martin/email2airtrail/main/eample.env
mv eample.env .env
```

### 3. Project Structure

The project has the following structure:

```text
airtrail-daemon/
├── docker-compose.yml    # Docker Compose configuration
├── Dockerfile            # Dockerfile for building the daemon image
├── requirements.txt      # Python dependencies
├── .env                  # Environment variables
├── config.py             # Configuration settings
├── daemon.py             # Main daemon script
├── logs/                 # Directory for log files
└── patterns/             # Directory for regex patterns
    ├── __init__.py       # Dynamic pattern loading
    ├── bcd_travel.py     # Regex pattern for BCD Travel emails
    └── ryanair.py        # Regex pattern for Ryanair emails (example)
```

### 3. Configure Environment Variables

Edit the .env file to configure the daemon according to your environment. Here is an example configuration:

```ini
# Email Configuration (IMAP)

IMAP_SERVER=imap.bcdtravel.com
IMAP_PORT=993
EMAIL_ADDRESS=your@email.com
EMAIL_PASSWORD=your-password

# AirTrail Configuration

AIRTRAIL_API_URL=http://your-airtrail-instance:3000/api/flights
AIRTRAIL_API_KEY=your-api-key

# Daemon Settings

CHECK_INTERVAL_MINUTES=10

# Pattern Configuration (Default: bcd_travel)

FLIGHT_PATTERN_FILE=bcd_travel

# Email Senders (comma-separated)

EMAIL_SENDERS=hensoldt@bcdtravel.de,bcdtravel@example.com
```

#### Environment Variables Description

| Variable | Description |
| -------- | ----------- |
| IMAP_SERVER | The IMAP server address for your email provider. |
| IMAP_PORT | The port for IMAP access (default: 993 for SSL). |
| EMAIL_ADDRESS | Your email address. |
| EMAIL_PASSWORD | Your email password or app-specific password. |
| AIRTRAIL_API_URL | The URL of your AirTrail API endpoint. |
| AIRTRAIL_API_KEY | The API key for accessing your AirTrail instance. |
| CHECK_INTERVAL_MINUTES | The interval in minutes for checking new emails. |
| FLIGHT_PATTERN_FILE | The name of the pattern file in the patterns/ directory. |
| EMAIL_SENDERS | Comma-separated list of email senders to monitor. |

## Usage

### 1. Build and Start the Docker Container

To build and start the Docker container, run the following command in the project directory:

```bash
docker-compose up -d --build
```

The --build flag ensures that the Docker image is rebuilt.
The -d flag runs the container in detached mode (in the background).

### 1a. Use a prebuilt image from GitHub Container Registry

If you want to run the published image instead of building locally, use:

```bash
docker pull ghcr.io/s-martin/email2airtrail:latest
docker run --rm -d --name email2airtrail ghcr.io/s-martin/email2airtrail:latest
```

Example Compose file using the published image:

```yaml
services:
  airtrail-daemon:
    image: ghcr.io/s-martin/email2airtrail:latest
    restart: unless-stopped
    env_file:
      - .env
    volumes:
      - ./logs:/app/logs
```

You can also push the image manually with:

```bash
docker build -t ghcr.io/s-martin/email2airtrail:latest .
docker push ghcr.io/s-martin/email2airtrail:latest
```

### 2. Check Logs

Logs are stored in the logs/daemon.log file. You can view them in real-time using:

```bash
tail -f logs/daemon.log
```

Or directly from the Docker container:

```bash
docker logs -f email2airtrail_email2airtrail_1
```

### 3. Stop the Daemon

To stop the daemon, use:

```bash
docker-compose down
```

## Customization

### 1. Adjust Regex Patterns

The daemon uses regex patterns to extract flight information from emails. If your emails have a different format, you can adjust the patterns in the patterns/ directory.
Example: Adding a New Pattern

Create a new file in the patterns/ directory, e.g., lufthansa.py.
Define the FLIGHT_BLOCK_PATTERN and TABLE_ROW_PATTERN for the new email format.

```python
import re

FLIGHT_BLOCK_PATTERN = re.compile(
    r"Your regex pattern for flight blocks"
)

TABLE_ROW_PATTERN = re.compile(
    r"Your regex pattern for table rows"
)
```

Update the .env file to use the new pattern:

```ini
FLIGHT_PATTERN_FILE=lufthansa
```

### 2. Add Multiple Email Senders

To monitor emails from multiple senders, add their email addresses to the EMAIL_SENDERS variable in the .env file:

```ini
EMAIL_SENDERS=sender1@example.com,sender2@example.com,sender3@example.com
```

#### 3. Adjust Date and Time Format

If your emails use a different date format (e.g., 26. Aug. 2026 instead of 26 Aug 2026), adjust the datetime.strptime format in the daemon.py file:

```python
departure_datetime = datetime.strptime(
    f"{flight_info['date']} {flight_info['departure_time']}",
    "%d. %b. %Y %H:%M"  # Example for "26. Aug. 2026 10:15"
).isoformat()
```

## File Descriptions

### docker-compose.yml

Defines the Docker Compose configuration to build and run the daemon as a service.

### Dockerfile

Contains instructions to build the Docker image for the daemon, including installing dependencies and setting up the environment.

### requirements.txt

Lists the Python dependencies required for the daemon.

### config.py

Loads environment variables and provides a configuration class for the daemon.

### daemon.py

The main script for the daemon. It:

- Connects to the IMAP server.
- Fetches and processes new emails.
- Extracts flight information using regex patterns.
- Sends flight data to the AirTrail API.
- Marks processed emails as read.
patterns/__init__.py
- Dynamically loads the configured regex pattern for flight information extraction.

### patterns/bcd_travel.py

Contains regex patterns for extracting flight information from BCD Travel emails.

### patterns/ryanair.py

Contains regex patterns for extracting flight information from Ryanair emails (example).

## Troubleshooting

| Issue | Solution |
| ----- | -------- |
| Docker container fails to start | Check the .env file for missing or incorrect values. Ensure Docker is running. |
| No emails found | Verify IMAP credentials and the EMAIL_SENDERS configuration. |
| Flight data not extracted | Adjust the regex pattern in the appropriate pattern file to match your email format. |
| AirTrail API errors | Verify the AIRTRAIL_API_URL and AIRTRAIL_API_KEY in the .env file. |
| Date or time parsing errors | Adjust the datetime.strptime format in daemon.py to match your email's date format. |
| Permission issues with logs | Ensure the logs/ directory exists and has write permissions. |

The regex patterns in patterns/bcd_travel.py are designed to match this format.

## Contributions

Contributions to this project are welcome! If you have suggestions, improvements, or bug fixes, feel free to create a pull request or open an issue.

## Contact

For questions or support, please open an issue.
