"""
=============================================================
  Uptime Monitoring and Alert System
  - Checks HTTP status codes for multiple URLs
  - Detects 4xx / 5xx errors and alerts the user
  - Continuously monitors at a set interval
  - Bonus: Exponential backoff on consecutive errors
  - Bonus: Logging to uptime_monitor.log
=============================================================
"""

import requests
import time
import logging
import sys
from datetime import datetime

# ── Configuration ─────────────────────────────────────────────────────────────

URLS_TO_MONITOR = [
    "http://httpstat.us/404",         # 4xx  – Client Error
    "http://httpstat.us/500",         # 5xx  – Server Error
    "https://www.google.com/",        # 200  – Healthy
    "http://www.example.com/nonexistentpage",  # 404 – Not Found
]

CHECK_INTERVAL_SECONDS = 10     # How often to check (normal cycle)
REQUEST_TIMEOUT        = 10     # Seconds before a request is considered timed out
MAX_BACKOFF_SECONDS    = 300    # Cap exponential backoff at 5 minutes
MAX_RETRY_ATTEMPTS     = 3      # Retries per URL per cycle before giving up


# ── HTTP Status Code Text Map ─────────────────────────────────────────────────

STATUS_TEXTS = {
    200: "OK",
    201: "Created",
    301: "Moved Permanently",
    302: "Found",
    400: "Bad Request",
    401: "Unauthorized",
    403: "Forbidden",
    404: "Not Found",
    408: "Request Timeout",
    429: "Too Many Requests",
    500: "Internal Server Error",
    502: "Bad Gateway",
    503: "Service Unavailable",
    504: "Gateway Timeout",
}

def status_text(code):
    """Return human-readable text for a status code."""
    return STATUS_TEXTS.get(code, "Unknown Status")


# ── Logging Setup ─────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler("uptime_monitor.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ]
)
logger = logging.getLogger("UptimeMonitor")


# ── Backoff Tracker ───────────────────────────────────────────────────────────

# Tracks consecutive error count per URL for exponential backoff
consecutive_errors: dict[str, int] = {url: 0 for url in URLS_TO_MONITOR}


def get_backoff_delay(url: str) -> float:
    """
    Exponential backoff: 2^n seconds, capped at MAX_BACKOFF_SECONDS.
    Only kicks in after 2 consecutive errors on the same URL.
    """
    errors = consecutive_errors.get(url, 0)
    if errors < 2:
        return 0.0
    delay = min(2 ** errors, MAX_BACKOFF_SECONDS)
    return float(delay)


# ── Core URL Checker ──────────────────────────────────────────────────────────

def check_url(url: str) -> tuple[int | None, float | None]:
    """
    Perform an HTTP GET request to the URL.

    Returns:
        (status_code, response_time_ms) on success
        (None, None)                     on connection error / timeout
    """
    try:
        start = time.perf_counter()
        resp  = requests.get(url, timeout=REQUEST_TIMEOUT, allow_redirects=True)
        elapsed_ms = (time.perf_counter() - start) * 1000
        return resp.status_code, round(elapsed_ms, 1)

    except requests.exceptions.ConnectionError:
        logger.error(f"  Connection error  →  {url}")
        return None, None

    except requests.exceptions.Timeout:
        logger.error(f"  Request timed out →  {url}")
        return None, None

    except requests.exceptions.RequestException as exc:
        logger.error(f"  Request failed    →  {url}  |  {exc}")
        return None, None


# ── Single-URL Monitor Logic ──────────────────────────────────────────────────

def monitor_url(url: str) -> None:
    """
    Check one URL, handle backoff, log results, and print alerts.
    """
    # ── Exponential backoff skip ─────────────────────────────
    backoff = get_backoff_delay(url)
    if backoff > 0:
        logger.warning(
            f"  ⏳ BACKOFF  →  {url}  |  "
            f"Waiting {backoff:.0f}s due to {consecutive_errors[url]} consecutive errors"
        )
        time.sleep(backoff)

    separator = "─" * 65
    print(f"\n{separator}")

    # ── Attempt with retries ─────────────────────────────────
    status_code = None
    response_ms = None

    for attempt in range(1, MAX_RETRY_ATTEMPTS + 1):
        logger.info(f"  Checking URL      →  {url}  (attempt {attempt}/{MAX_RETRY_ATTEMPTS})")
        status_code, response_ms = check_url(url)

        if status_code is not None:
            break  # Got a response; no need to retry

        if attempt < MAX_RETRY_ATTEMPTS:
            retry_wait = 2 ** attempt
            logger.warning(f"  Retrying in {retry_wait}s …")
            time.sleep(retry_wait)

    # ── Unreachable ──────────────────────────────────────────
    if status_code is None:
        consecutive_errors[url] = consecutive_errors.get(url, 0) + 1
        logger.error(
            f"  🔴 UNREACHABLE  →  {url}  |  "
            f"Failed after {MAX_RETRY_ATTEMPTS} attempts"
        )
        print(f"  🔴 ALERT: URL is UNREACHABLE after {MAX_RETRY_ATTEMPTS} attempts!")
        return

    text  = status_text(status_code)
    label = f"{status_code} {text}"
    rt    = f"{response_ms} ms" if response_ms is not None else "N/A"

    logger.info(f"  Status Code       →  {label}  |  Response time: {rt}")

    # ── 4xx – Client Error ───────────────────────────────────
    if 400 <= status_code < 500:
        consecutive_errors[url] = consecutive_errors.get(url, 0) + 1
        logger.warning(f"  ⚠️  ALERT: 4xx error for {url}")
        print(f"  Status Code : {label}")
        print(f"  ⚠️  ALERT: 4xx Client Error encountered for URL: {url}")
        print(f"  Consecutive errors: {consecutive_errors[url]}")

    # ── 5xx – Server Error ───────────────────────────────────
    elif 500 <= status_code < 600:
        consecutive_errors[url] = consecutive_errors.get(url, 0) + 1
        logger.error(f"  🔴 ALERT: 5xx error for {url}")
        print(f"  Status Code : {label}")
        print(f"  🔴 ALERT: 5xx Server Error encountered for URL: {url}")
        print(f"  Consecutive errors: {consecutive_errors[url]}")

    # ── 2xx / 3xx – Healthy ──────────────────────────────────
    else:
        consecutive_errors[url] = 0          # Reset on success
        logger.info(f"  ✅ UP  →  {url}")
        print(f"  Status Code : {label}")
        print(f"  ✅ The website is UP and running.  (response: {rt})")


# ── Main Monitoring Loop ──────────────────────────────────────────────────────

def run_monitor(urls: list[str], interval: int = CHECK_INTERVAL_SECONDS) -> None:
    """
    Continuously monitor a list of URLs every `interval` seconds.
    Press Ctrl+C to stop.
    """
    cycle = 0

    logger.info("=" * 65)
    logger.info("  Uptime Monitor started")
    logger.info(f"  Monitoring {len(urls)} URL(s) every {interval} second(s)")
    logger.info(f"  Log file  →  uptime_monitor.log")
    logger.info("=" * 65)

    print("\n" + "=" * 65)
    print("  🚀 Uptime Monitor — Press Ctrl+C to stop")
    print(f"  Interval : {interval}s   |   URLs : {len(urls)}")
    print("=" * 65)

    try:
        while True:
            cycle += 1
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            print(f"\n\n{'━' * 65}")
            print(f"  📡 Cycle #{cycle}   |   {timestamp}")
            print(f"{'━' * 65}")
            logger.info(f"─── Cycle #{cycle} started ───")

            for url in urls:
                monitor_url(url)

            logger.info(f"─── Cycle #{cycle} complete. Next check in {interval}s ───\n")
            print(f"\n  ⏱  Next check in {interval} seconds …  (Ctrl+C to quit)")
            time.sleep(interval)

    except KeyboardInterrupt:
        print("\n\n" + "=" * 65)
        print("  Monitor stopped by user.")
        print("  Log saved to  →  uptime_monitor.log")
        print("=" * 65)
        logger.info("Monitor stopped by user (KeyboardInterrupt).")


# ── Entry Point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    run_monitor(URLS_TO_MONITOR, interval=CHECK_INTERVAL_SECONDS)