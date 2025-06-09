# Sonatype IQ Server Raw Report Fetcher

This tool connects to your Sonatype IQ Server, fetches security scan reports for all your applications, and saves them as CSV files. Use these CSVs for analysis, compliance, or sharing.

## 🚀 Getting Started

### 1. **Download or Clone**

- [Download the latest release](https://github.com/your-repo/your-project/releases) or clone this repository.

### 2. **Configure Settings**

- Navigate to the `config` directory.
- Copy `.env.example` to `.env`:
  ```sh
  cp config/.env.example config/.env
  ```
- Open `config/.env` and fill in your Sonatype IQ Server details:

  - `IQ_SERVER_URL`: IQ Server address (e.g., `https://your-iq-server.com`)
  - `IQ_USERNAME`: Your username
  - `IQ_PASSWORD`: Your password
  - `ORGANIZATION_ID`: (Optional) Filter applications by organization ID.
  - `OUTPUT_DIR`: (Optional) Directory for CSV files (default: `raw_reports`)
  - `NUM_WORKERS`: (Optional) Number of concurrent workers (default: 8)
  - `LOG_LEVEL`: (Optional) Set to `DEBUG`, `INFO`, `WARNING`, or `ERROR`.

### 3. **Run the Tool**

```sh
./iq-fetch
```

- On Windows: `iq-fetch.exe`

## 📝 Configuration Reference

Configure settings via `config/.env` (recommended) or environment variables.

**Example `.env` file:**

```
IQ_SERVER_URL=https://your-iq-server.com
IQ_USERNAME=your-username
IQ_PASSWORD=your-password
OUTPUT_DIR=raw_reports
NUM_WORKERS=8
LOG_LEVEL=INFO
```

## 🏗️ Project Structure

```
iqserver_report_fetch/
├── src/
│   └── iq_fetcher/
│       ├── __init__.py          # Package initialization
│       ├── config.py            # Configuration management
│       ├── client.py            # IQ Server API client
│       ├── fetcher.py           # Core report fetching logic
│       └── utils.py             # Utilities, logging, error handling
├── config/
│   ├── .env.example         # Configuration template
│   └── .env                 # Your configuration (not in git)
├── pyproject.toml           # Project dependencies (uv)
├── uv.lock                  # Locked dependencies
├── README.md                # This file
└── scripts/
    └── build_macos.sh       # Build script for macOS
```
