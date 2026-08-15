# Email2AirTrail

![GitHub Container Registry](https://img.shields.io/badge/Container%20Registry-ghcr.io-blue) [![Tests](https://github.com/s-martin/email2airtrail/actions/workflows/tests.yml/badge.svg)](https://github.com/s-martin/email2airtrail/actions/workflows/tests.yml) [![CodeQL](https://github.com/s-martin/email2airtrail/actions/workflows/github-code-scanning/codeql/badge.svg)](https://github.com/s-martin/email2airtrail/actions/workflows/github-code-scanning/codeql)

A **Docker-based daemon** that monitors an IMAP inbox for flight information emails and inserts them into an **[AirTrail](https://github.com/johanohly/AirTrail)** instance.

## Features

- **Email Monitoring**: Continuously checks an IMAP inbox for new emails from configured senders.
- **Flight Information Extraction**: Extracts flight details such as flight number, departure/arrival times, airport codes, class, booking reference, aircraft, and seat from emails.
- **AirTrail Integration**: Imports extracted flight data to an AirTrail instance using its API.
- **Duplicate Check**: Ensures that the same flight is not inserted multiple times.
- **Configurable Senders**: Monitors emails from multiple senders.
- **Dynamic Pattern Loading**: Supports different email formats by loading the appropriate regex pattern at runtime.

## Prerequisites

- **Docker** and **Docker Compose** installed on your system.
- **IMAP Access**: Your email account must support IMAP access.
- **AirTrail Instance**: Access to an AirTrail instance with a valid API key.

## Project Structure

```text
email2airtrail/
├── docker-compose.yml    # Docker Compose configuration
├── Dockerfile            # Dockerfile for building the daemon image
├── requirements.txt      # Python dependencies
├── example.env           # Example environment variable file
├── config.py             # Loads and exposes configuration from environment variables
├── daemon.py             # Main daemon script
├── logs/                 # Directory for log files (created at runtime)
└── pattern/              # Directory for email regex patterns
    ├── __init__.py       # Dynamic pattern loading
    ├── bcd_travel.py     # Regex patterns for BCD Travel emails
    └── ryanair.py        # Regex patterns for Ryanair emails
```

## Installation

### Option A: Use the prebuilt image from GitHub Container Registry (recommended)

1. Download the Docker Compose file and the example environment template:

   ```bash
   wget -O docker-compose.yml https://raw.githubusercontent.com/s-martin/email2airtrail/main/docker-compose.yml
   wget -O .env https://raw.githubusercontent.com/s-martin/email2airtrail/main/example.env
   ```

2. Edit `.env` with your settings (see [Configuration](#configuration) below).

3. Start the daemon:

   ```bash
   docker compose up -d
   ```

### Option B: Build from source

1. Clone the repository:

   ```bash
   git clone https://github.com/s-martin/email2airtrail
   cd email2airtrail
   ```

2. Copy the example environment file and edit it:

   ```bash
   cp example.env .env
   ```

3. Build and start the container:

   ```bash
   docker compose up -d --build
   ```

## Configuration

Edit the `.env` file to match your environment:

```ini
# Email configuration (IMAP)
IMAP_SERVER=imap.example.com
IMAP_PORT=993
EMAIL_ADDRESS=your@email.com
EMAIL_PASSWORD=your-password

# AirTrail configuration
AIRTRAIL_API_URL=http://your-airtrail-instance:3000/api/flights
AIRTRAIL_API_KEY=your-api-key

# Daemon settings
CHECK_INTERVAL_MINUTES=10

# Pattern configuration (name of a file in the pattern/ directory, without .py)
FLIGHT_PATTERN_FILE=bcd_travel

# Email senders to monitor (comma-separated)
EMAIL_SENDERS=info@bcdtravel.de,bcdtravel@example.com
```

### Environment Variables

| Variable | Description |
| -------- | ----------- |
| `IMAP_SERVER` | IMAP server address for your email provider. |
| `IMAP_PORT` | IMAP port (default: `993` for SSL). |
| `EMAIL_ADDRESS` | Your email address. |
| `EMAIL_PASSWORD` | Your email password or app-specific password. |
| `AIRTRAIL_API_URL` | URL of your AirTrail API endpoint. |
| `AIRTRAIL_API_KEY` | API key for your AirTrail instance. |
| `CHECK_INTERVAL_MINUTES` | How often (in minutes) to check for new emails. |
| `FLIGHT_PATTERN_FILE` | Filename (without `.py`) of the pattern module in `pattern/`. |
| `EMAIL_SENDERS` | Comma-separated list of sender addresses to monitor. |

## Usage

### Start the daemon

```bash
docker compose up -d
```

### View logs

```bash
# From the host (log file is mounted to ./logs/)
tail -f logs/daemon.log

# From Docker
docker logs -f email2airtrail
```

### Stop the daemon

```bash
docker compose down
```

## Adding Support for a New Email Format

The daemon uses regex patterns to extract flight data from email text. Each email provider has its own pattern module in the `pattern/` directory.

1. Create a new file in `pattern/`, e.g. `pattern/lufthansa.py`, and define the required patterns:

   ```python
   import re

   FLIGHT_BLOCK_PATTERN = re.compile(
       r"<your regex for a flight block>"
   )

   TABLE_ROW_PATTERN = re.compile(
       r"<your regex for individual table rows>"
   )
   ```

2. Set `FLIGHT_PATTERN_FILE=lufthansa` in your `.env` file.

3. Restart the daemon:

   ```bash
   docker compose restart
   ```

## Troubleshooting

| Issue | Solution |
| ----- | -------- |
| Container fails to start | Check `.env` for missing or incorrect values. Ensure Docker is running. |
| No emails found | Verify IMAP credentials and `EMAIL_SENDERS` configuration. |
| Flight data not extracted | Adjust the regex patterns in the relevant `pattern/` file to match your email format. |
| AirTrail API errors | Verify `AIRTRAIL_API_URL` and `AIRTRAIL_API_KEY` in `.env`. |
| Date/time parsing errors | Check that the `datetime.strptime` format in `daemon.py` matches the date format in your emails. |
| Permission issues with logs | Ensure the `logs/` directory exists and has write permissions. |

## Contributing

Contributions are welcome! Feel free to open an issue or submit a pull request.

## License

See [LICENSE](LICENSE).

## Contact

For questions or support, please open an issue.
