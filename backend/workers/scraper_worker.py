import threading
import logging
import requests
from bs4 import BeautifulSoup

from backend.db import update_link_name

logger = logging.getLogger(__name__)


def _fetch_link_name(url):
    """Fetch page title from a URL. Returns the domain as fallback."""
    try:
        res = requests.get(url, timeout=5)
        soup = BeautifulSoup(res.text, "html.parser")
        if soup.title and soup.title.string:
            return soup.title.string.strip()[:250]
    except Exception as e:
        logger.warning(f"fetch_link_name failed for {url}: {e}")
    return url.split("//")[-1].split("/")[0]


def process_scrape(short_code, url):
    """
    Background task: fetch page title and update the DB row.
    Must NEVER raise — any exception is caught and logged.
    """
    try:
        link_name = _fetch_link_name(url)
        update_link_name(short_code, link_name)
        logger.info(f"Background scrape complete for {short_code}: '{link_name}'")
    except Exception as e:
        logger.error(f"Background scrape failed for {short_code}: {e}", exc_info=True)


def enqueue_scrape_job(short_code, url):
    """
    Starts a daemon thread to scrape link_name for the given short_code.
    Returns immediately — caller is NOT blocked.
    Daemon=True ensures the thread does not prevent app shutdown.
    """
    thread = threading.Thread(
        target=process_scrape,
        args=(short_code, url),
        daemon=True
    )
    thread.start()
    logger.debug(f"Scrape job enqueued for short_code={short_code}")
