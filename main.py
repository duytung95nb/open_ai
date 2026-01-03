"""Main CLI entry point for news summary application."""
import argparse
import logging
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict

from rss_fetcher import fetch_rss_feeds
from storage import ArticleStorage
from openai_client import OpenAIClient
from formatter import format_individual_summaries, format_daily_digest, get_output_filename

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def setup_output_directory(output_dir: str) -> Path:
    """Create output directory if it doesn't exist."""
    try:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Verify write permissions
        test_file = output_path / '.write_test'
        try:
            test_file.touch()
            test_file.unlink()
        except (IOError, OSError):
            raise PermissionError(f"Cannot write to output directory: {output_path}")
        
        logger.info(f"Output directory: {output_path.absolute()}")
        return output_path
    except Exception as e:
        logger.error(f"Error setting up output directory: {str(e)}")
        raise


def fetch_and_process(
    storage: ArticleStorage,
    openai_client: OpenAIClient,
    output_dir: Path,
    generate_individual: bool = True,
    generate_digest: bool = True
):
    """
    Fetch RSS feeds, process new articles, and generate summaries.
    
    Args:
        storage: ArticleStorage instance
        openai_client: OpenAIClient instance
        output_dir: Output directory path
        generate_individual: Whether to generate individual summaries
        generate_digest: Whether to generate daily digest
    """
    try:
        logger.info("Starting RSS feed fetch...")
        all_articles = fetch_rss_feeds()
        
        if not all_articles:
            logger.warning("No articles fetched from RSS feeds")
            return
        
        # Filter out already processed articles
        new_articles = storage.get_unprocessed_articles(all_articles)
        
        if not new_articles:
            logger.info("No new articles to process")
            return
        
        logger.info(f"Processing {len(new_articles)} new articles...")
        
        # Get today's date for filename
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Generate summaries
        summaries = {}
        if generate_individual or generate_digest:
            try:
                summaries = openai_client.summarize_articles_batch(new_articles)
                if not summaries:
                    logger.error("Failed to generate any summaries")
                    return
            except Exception as e:
                logger.error(f"Error generating summaries: {str(e)}")
                return
        
        # Mark articles as processed only if summaries were generated
        if summaries:
            for article in new_articles:
                article_id = article.get('guid', article.get('link', ''))
                if article_id:
                    storage.mark_processed(article_id, {
                        'title': article.get('title', 'Unknown'),
                        'source': article.get('source', 'Unknown'),
                        'date': today
                    })
        
        # Generate individual summaries
        if generate_individual and summaries:
            try:
                logger.info("Generating individual summaries Markdown...")
                individual_md = format_individual_summaries(new_articles, summaries, today)
                individual_file = output_dir / get_output_filename('individual', today)
                
                with open(individual_file, 'w', encoding='utf-8') as f:
                    f.write(individual_md)
                
                logger.info(f"Individual summaries saved to: {individual_file}")
            except IOError as e:
                logger.error(f"Error writing individual summaries file: {str(e)}")
            except Exception as e:
                logger.error(f"Error formatting individual summaries: {str(e)}")
        
        # Generate daily digest
        if generate_digest and summaries:
            try:
                logger.info("Generating daily digest...")
                digest = openai_client.generate_daily_digest(new_articles, summaries)
                
                if digest:
                    digest_md = format_daily_digest(digest, new_articles, today)
                    digest_file = output_dir / get_output_filename('digest', today)
                    
                    with open(digest_file, 'w', encoding='utf-8') as f:
                        f.write(digest_md)
                    
                    logger.info(f"Daily digest saved to: {digest_file}")
                else:
                    logger.error("Failed to generate daily digest")
            except IOError as e:
                logger.error(f"Error writing digest file: {str(e)}")
            except Exception as e:
                logger.error(f"Error generating daily digest: {str(e)}")
    
    except KeyboardInterrupt:
        logger.info("\nOperation cancelled by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error in fetch_and_process: {str(e)}", exc_info=True)
        sys.exit(1)


def list_processed(storage: ArticleStorage):
    """List all processed articles."""
    processed_ids = storage.get_processed_ids()
    count = len(processed_ids)
    
    print(f"\nProcessed articles: {count}")
    print("-" * 50)
    
    if count == 0:
        print("No articles have been processed yet.")
        return
    
    # Load article data if available
    for article_id in list(processed_ids)[:20]:  # Show first 20
        article_data = storage.article_data.get(article_id, {})
        title = article_data.get('title', article_id[:50])
        source = article_data.get('source', 'Unknown')
        date = article_data.get('date', 'Unknown')
        print(f"[{date}] {source}: {title}")
    
    if count > 20:
        print(f"\n... and {count - 20} more articles")


def clear_storage(storage: ArticleStorage):
    """Clear all processed articles from storage."""
    confirm = input("Are you sure you want to clear all processed articles? (yes/no): ")
    if confirm.lower() == 'yes':
        storage.clear()
        print("Storage cleared successfully.")
    else:
        print("Operation cancelled.")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='News Summary CLI - Fetch and summarize Vietnamese news from RSS feeds using OpenAI'
    )
    
    parser.add_argument(
        'command',
        choices=['fetch', 'list', 'clear'],
        help='Command to execute: fetch (process new articles), list (show processed), clear (clear storage)'
    )
    
    parser.add_argument(
        '--individual',
        action='store_true',
        help='Generate individual article summaries only'
    )
    
    parser.add_argument(
        '--digest',
        action='store_true',
        help='Generate daily digest only'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        default='./summaries',
        help='Output directory for summary files (default: ./summaries)'
    )
    
    args = parser.parse_args()
    
    # Determine what to generate
    # Default: both (if neither --individual nor --digest is specified)
    if args.individual:
        generate_individual = True
        generate_digest = False
    elif args.digest:
        generate_individual = False
        generate_digest = True
    else:
        # Default: both
        generate_individual = True
        generate_digest = True
    
    # Initialize storage
    storage = ArticleStorage()
    
    # Handle commands
    if args.command == 'list':
        list_processed(storage)
        return
    
    if args.command == 'clear':
        clear_storage(storage)
        return
    
    if args.command == 'fetch':
        try:
            # Initialize OpenAI client
            openai_client = OpenAIClient()
        except ValueError as e:
            logger.error(str(e))
            logger.error("Please set OPENAI_API_KEY environment variable or create a .env file")
            sys.exit(1)
        
        # Setup output directory
        output_dir = setup_output_directory(args.output_dir)
        
        # Fetch and process
        fetch_and_process(
            storage,
            openai_client,
            output_dir,
            generate_individual,
            generate_digest
        )


if __name__ == '__main__':
    main()

