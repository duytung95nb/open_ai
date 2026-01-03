"""RSS feed fetcher and parser for Vietnamese news sources."""
import feedparser
import logging
from typing import List, Dict, Optional
from datetime import datetime
from time import struct_time

logger = logging.getLogger(__name__)

RSS_FEEDS = [
    "https://vnexpress.net/rss/tin-moi-nhat.rss",
    "https://thanhnien.vn/rss/home.rss"
]


def fetch_rss_feeds() -> List[Dict]:
    """
    Fetch and parse RSS feeds from all configured sources.
    
    Returns:
        List of article dictionaries with keys: title, description, link, 
        pubDate, guid, source
    """
    all_articles = []
    
    for feed_url in RSS_FEEDS:
        try:
            logger.info(f"Fetching RSS feed: {feed_url}")
            feed = feedparser.parse(feed_url)
            
            if feed.bozo and feed.bozo_exception:
                logger.warning(f"Feed parsing warning for {feed_url}: {feed.bozo_exception}")
            
            source_name = _extract_source_name(feed_url)
            
            for entry in feed.entries:
                # Try to get date from feedparser's parsed date first
                pub_date = None
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    try:
                        if isinstance(entry.published_parsed, struct_time):
                            pub_date = datetime(*entry.published_parsed[:6]).strftime('%Y-%m-%d')
                    except (ValueError, TypeError, IndexError):
                        pass
                
                # Fallback to string parsing
                if not pub_date:
                    pub_date = _parse_date(entry.get('published', ''))
                
                # Validate required fields
                article_id = entry.get('id') or entry.get('link') or ''
                if not article_id:
                    logger.warning(f"Skipping article without ID or link: {entry.get('title', 'Unknown')}")
                    continue
                
                article = {
                    'title': entry.get('title', 'No title').strip(),
                    'description': entry.get('description', '').strip(),
                    'link': entry.get('link', '').strip(),
                    'pubDate': pub_date,
                    'guid': article_id.strip(),
                    'source': source_name
                }
                all_articles.append(article)
            
            logger.info(f"Fetched {len(feed.entries)} articles from {source_name}")
            
        except Exception as e:
            logger.error(f"Error fetching feed {feed_url}: {str(e)}")
            continue
    
    logger.info(f"Total articles fetched: {len(all_articles)}")
    return all_articles


def _extract_source_name(url: str) -> str:
    """Extract source name from RSS feed URL."""
    if 'vnexpress' in url:
        return 'VnExpress'
    elif 'thanhnien' in url:
        return 'Thanh Nien'
    else:
        return 'Unknown'


def _parse_date(date_str: str) -> Optional[str]:
    """
    Parse date string from RSS feed.
    
    Returns:
        ISO format date string (YYYY-MM-DD) or None if parsing fails
    """
    if not date_str:
        return None
    
    # Try using feedparser's parsed date if available (more reliable)
    # This will be handled by the caller if they pass the entry object
    
    # Common RSS date formats
    date_formats = [
        '%a, %d %b %Y %H:%M:%S %z',  # RFC 822 format
        '%d %b %Y %H:%M:%S %z',       # Without day name
        '%Y-%m-%d %H:%M:%S',          # ISO format
        '%Y-%m-%d',                   # Date only
    ]
    
    for fmt in date_formats:
        try:
            dt = datetime.strptime(date_str.strip(), fmt)
            return dt.strftime('%Y-%m-%d')
        except (ValueError, AttributeError):
            continue
    
    # If all formats fail, try parsing with feedparser's published_parsed
    # This requires the entry object, so we'll log and return None
    logger.warning(f"Could not parse date: {date_str}")
    return None

