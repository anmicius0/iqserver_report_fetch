#!/usr/bin/env python3
"""Sonatype IQ Server Raw Report Fetcher entry point.

This script fetches and processes raw scan reports from Sonatype IQ Server.
"""

import sys
import multiprocessing
from iq_fetcher.config import get_config
from iq_fetcher.fetcher import RawReportFetcher
from iq_fetcher.utils import logger


def main():
    logger.info("🚀 Starting fetch process…")
    try:
        cfg = get_config()
        fetcher = RawReportFetcher(cfg)
        fetcher.fetch_all_reports()
        logger.info("✅ Fetch process completed successfully!")
    except Exception as e:
        logger.error(f"💥 Error during fetch process: {e}")
        sys.exit(1)  # Exit with a non-zero code to indicate an error


if __name__ == "__main__":
    multiprocessing.freeze_support()
    try:
        main()
    except KeyboardInterrupt:
        logger.warning("⏹️ Cancelled by user")
        sys.exit(0)
