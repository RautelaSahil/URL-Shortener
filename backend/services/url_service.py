from urllib.parse import urlparse
import logging

from backend.db import (
    insert_url_custom_code,
    insert_url_with_retry,
    get_all_urls,
    delete_url_by_id,
    get_original_and_increment
)
from backend.workers.scraper_worker import enqueue_scrape_job

logger = logging.getLogger(__name__)

def is_valid_url(url):
    if not url or not isinstance(url, str):
        return False
    try:
        result = urlparse(url)
        if result.scheme not in ['http', 'https']:
            return False
        if not result.netloc:
            return False
        if '.' not in result.netloc and result.netloc != 'localhost':
            return False
        return True
    except ValueError:
        return False

def create_short_url(long_url, custom_code, user_id):
    """
    Validates URL, custom code format, and delegates to the DB layer.
    Raises ValueError on client errors (400) or RuntimeError on server errors (500).
    """
    if not is_valid_url(long_url):
        raise ValueError("Invalid URL format. Must be a valid http or https URL")

    # Fast initial placement so endpoint is non-blocking
    initial_link_name = "Pending..."

    if custom_code:
        if not isinstance(custom_code, str):
            raise ValueError("Invalid custom code format")
        if not custom_code.isalnum():
            raise ValueError("Custom code must be alphanumeric")
        if len(custom_code) < 3 or len(custom_code) > 10:
            raise ValueError("Custom code must be between 3 and 10 characters")

        # Database layer will raise ValueError if duplicate exists
        insert_url_custom_code(long_url, custom_code, initial_link_name, user_id)
        short_code = custom_code
    else:
        # DB handles generation and max 5 retries on collision
        short_code = insert_url_with_retry(long_url, initial_link_name, user_id)

    # Queue the background job to fetch the title
    enqueue_scrape_job(short_code, long_url)

    return short_code

def get_user_urls_service(user_id):
    return get_all_urls(user_id)

def delete_user_url_service(url_id, user_id):
    delete_url_by_id(url_id, user_id)

def resolve_redirect_service(short_code):
    return get_original_and_increment(short_code)
