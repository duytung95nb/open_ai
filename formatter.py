"""Markdown formatter for news summaries."""
import logging
from typing import List, Dict
from datetime import datetime

logger = logging.getLogger(__name__)


def format_individual_summaries(articles: List[Dict], summaries: Dict[str, str], date: str = None) -> str:
    """
    Format individual article summaries as Markdown.
    
    Args:
        articles: List of article dictionaries
        summaries: Dictionary mapping article GUID to summary
        date: Date string (YYYY-MM-DD), defaults to today
        
    Returns:
        Formatted Markdown string
    """
    if not articles:
        logger.warning("No articles provided for formatting")
        return "# Tin Tức Tóm Tắt\n\n*Không có bài viết nào.*\n"
    
    if date is None:
        date = datetime.now().strftime('%Y-%m-%d')
    
    # Validate date format
    try:
        datetime.strptime(date, '%Y-%m-%d')
    except ValueError:
        logger.warning(f"Invalid date format: {date}, using today's date")
        date = datetime.now().strftime('%Y-%m-%d')
    
    lines = [
        f"# Tin Tức Tóm Tắt - {date}",
        "",
        f"*Tổng số bài viết: {len(articles)}*",
        "",
        "---",
        ""
    ]
    
    for article in articles:
        article_id = article.get('guid', article.get('link', ''))
        if not article_id:
            logger.warning(f"Skipping article without ID: {article.get('title', 'Unknown')}")
            continue
        
        title = article.get('title', 'No title').strip() or 'No title'
        link = article.get('link', '').strip()
        source = article.get('source', 'Unknown').strip() or 'Unknown'
        pub_date = article.get('pubDate', '').strip()
        summary = summaries.get(article_id, 'Không có tóm tắt.').strip()
        
        # Escape markdown special characters in title
        title_escaped = title.replace('|', '\\|').replace('[', '\\[').replace(']', '\\]')
        
        lines.append(f"## {title_escaped}")
        lines.append("")
        lines.append(f"**Nguồn:** {source}")
        if pub_date:
            lines.append(f"**Ngày:** {pub_date}")
        if link:
            lines.append(f"**Link:** [{link}]({link})")
        else:
            lines.append("**Link:** Không có")
        lines.append("")
        lines.append(f"**Tóm tắt:** {summary}")
        lines.append("")
        lines.append("---")
        lines.append("")
    
    return "\n".join(lines)


def format_daily_digest(digest: str, articles: List[Dict], date: str = None) -> str:
    """
    Format daily digest as Markdown.
    
    Args:
        digest: Daily digest text from OpenAI
        articles: List of article dictionaries
        date: Date string (YYYY-MM-DD), defaults to today
        
    Returns:
        Formatted Markdown string
    """
    if not digest:
        logger.warning("Empty digest provided")
        digest = "*Không có tóm tắt.*"
    
    if not articles:
        logger.warning("No articles provided for digest")
    
    if date is None:
        date = datetime.now().strftime('%Y-%m-%d')
    
    # Validate date format
    try:
        datetime.strptime(date, '%Y-%m-%d')
    except ValueError:
        logger.warning(f"Invalid date format: {date}, using today's date")
        date = datetime.now().strftime('%Y-%m-%d')
    
    lines = [
        f"# Tóm Tắt Tin Tức Hàng Ngày - {date}",
        "",
        f"*Tổng số bài viết: {len(articles)}*",
        "",
        "## Nguồn Tin",
        ""
    ]
    
    # Group articles by source
    sources = {}
    for article in articles:
        source = article.get('source', 'Unknown').strip() or 'Unknown'
        if source not in sources:
            sources[source] = []
        sources[source].append(article)
    
    if sources:
        for source, source_articles in sources.items():
            lines.append(f"- **{source}**: {len(source_articles)} bài viết")
    else:
        lines.append("- *Không có nguồn tin*")
    
    lines.extend([
        "",
        "---",
        "",
        digest,
        "",
        "---",
        "",
        "## Danh Sách Bài Viết",
        ""
    ])
    
    if articles:
        for idx, article in enumerate(articles, 1):
            title = article.get('title', 'No title').strip() or 'No title'
            link = article.get('link', '').strip()
            source = article.get('source', 'Unknown').strip() or 'Unknown'
            
            # Escape markdown in title
            title_escaped = title.replace('|', '\\|')
            
            if link:
                lines.append(f"{idx}. [{title_escaped}]({link}) - *{source}*")
            else:
                lines.append(f"{idx}. {title_escaped} - *{source}*")
    else:
        lines.append("*Không có bài viết nào.*")
    
    lines.append("")
    lines.append(f"*Được tạo vào: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
    
    return "\n".join(lines)


def get_output_filename(prefix: str, date: str = None) -> str:
    """
    Generate output filename for summaries.
    
    Args:
        prefix: File prefix (e.g., 'individual', 'digest')
        date: Date string (YYYY-MM-DD), defaults to today
        
    Returns:
        Filename string
    """
    if date is None:
        date = datetime.now().strftime('%Y-%m-%d')
    
    return f"{prefix}_{date}.md"

