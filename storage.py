"""Storage system for tracking processed articles."""
import json
import os
import logging
from typing import Set, List, Dict
from pathlib import Path

logger = logging.getLogger(__name__)

STORAGE_FILE = "processed_articles.json"


class ArticleStorage:
    """Manages storage of processed article IDs."""
    
    def __init__(self, storage_file: str = STORAGE_FILE):
        self.storage_file = storage_file
        self.processed_ids: Set[str] = set()
        self.article_data: Dict[str, Dict] = {}
        self._load()
    
    def _load(self):
        """Load processed articles from JSON file."""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.processed_ids = set(data.get('processed_ids', []))
                    self.article_data = data.get('article_data', {})
                logger.info(f"Loaded {len(self.processed_ids)} processed articles from storage")
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"Error loading storage file: {str(e)}")
                self.processed_ids = set()
                self.article_data = {}
        else:
            logger.info("No existing storage file found, starting fresh")
    
    def _save(self):
        """Save processed articles to JSON file."""
        try:
            data = {
                'processed_ids': list(self.processed_ids),
                'article_data': self.article_data
            }
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.debug(f"Saved {len(self.processed_ids)} processed articles to storage")
        except IOError as e:
            logger.error(f"Error saving storage file: {str(e)}")
    
    def is_processed(self, article_id: str) -> bool:
        """
        Check if an article has been processed.
        
        Args:
            article_id: Article GUID or link
            
        Returns:
            True if article has been processed, False otherwise
        """
        return article_id in self.processed_ids
    
    def mark_processed(self, article_id: str, article_data: Dict = None):
        """
        Mark an article as processed.
        
        Args:
            article_id: Article GUID or link
            article_data: Optional article metadata to store
        """
        self.processed_ids.add(article_id)
        if article_data:
            self.article_data[article_id] = article_data
        self._save()
    
    def mark_multiple_processed(self, article_ids: List[str]):
        """
        Mark multiple articles as processed.
        
        Args:
            article_ids: List of article GUIDs or links
        """
        for article_id in article_ids:
            self.processed_ids.add(article_id)
        self._save()
    
    def get_processed_ids(self) -> Set[str]:
        """
        Get all processed article IDs.
        
        Returns:
            Set of processed article IDs
        """
        return self.processed_ids.copy()
    
    def get_unprocessed_articles(self, articles: List[Dict]) -> List[Dict]:
        """
        Filter out already processed articles.
        
        Args:
            articles: List of article dictionaries
            
        Returns:
            List of unprocessed articles
        """
        unprocessed = [
            article for article in articles
            if not self.is_processed(article.get('guid', article.get('link', '')))
        ]
        logger.info(f"Filtered {len(unprocessed)} unprocessed articles from {len(articles)} total")
        return unprocessed
    
    def clear(self):
        """Clear all processed articles from storage."""
        self.processed_ids = set()
        self.article_data = {}
        if os.path.exists(self.storage_file):
            os.remove(self.storage_file)
        logger.info("Cleared all processed articles from storage")
    
    def get_count(self) -> int:
        """Get the number of processed articles."""
        return len(self.processed_ids)

