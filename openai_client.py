"""OpenAI client for article summarization."""
import os
import logging
from typing import List, Dict, Optional
from openai import OpenAI
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Default model for cost efficiency
DEFAULT_MODEL = os.getenv('OPENAI_MODEL', 'gpt-5-mini')


class OpenAIClient:
    """Client for OpenAI API summarization."""
    
    def __init__(self, model: str = DEFAULT_MODEL):
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        
        self.client = OpenAI(api_key=api_key)
        self.model = model
        logger.info(f"Initialized OpenAI client with model: {model}")
    
    def summarize_article(self, article: Dict, max_retries: int = 3) -> Optional[str]:
        """
        Generate a concise summary for a single article.
        
        Args:
            article: Article dictionary with title, description, link
            max_retries: Maximum number of retry attempts
            
        Returns:
            Summary string or None if generation fails
        """
        title = article.get('title', 'No title')
        description = article.get('description', '')
        
        prompt = f"""Please provide a concise 2-3 sentence summary in Vietnamese of the following news article:

Title: {title}

Description: {description}

Summary:"""
        
        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that summarizes news articles in Vietnamese concisely."},
                        {"role": "user", "content": prompt}
                    ]
                )
                
                summary = response.choices[0].message.content.strip()
                logger.debug(f"Generated summary for article: {title[:50]}...")
                return summary
                
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed for article '{title}': {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    logger.error(f"Failed to summarize article '{title}' after {max_retries} attempts")
                    return None
        
        return None
    
    def summarize_articles_batch(self, articles: List[Dict], max_retries: int = 3) -> Dict[str, str]:
        """
        Generate summaries for multiple articles.
        
        Args:
            articles: List of article dictionaries
            max_retries: Maximum number of retry attempts per article
            
        Returns:
            Dictionary mapping article GUID to summary
        """
        summaries = {}
        total = len(articles)
        
        logger.info(f"Generating summaries for {total} articles...")
        
        for idx, article in enumerate(articles, 1):
            article_id = article.get('guid', article.get('link', ''))
            logger.info(f"Processing article {idx}/{total}: {article.get('title', 'Unknown')[:50]}...")
            
            summary = self.summarize_article(article, max_retries)
            if summary:
                summaries[article_id] = summary
            else:
                logger.warning(f"Failed to generate summary for article: {article.get('title', 'Unknown')}")
            
            # Rate limiting: small delay between requests
            if idx < total:
                time.sleep(0.5)
        
        logger.info(f"Generated {len(summaries)} summaries out of {total} articles")
        return summaries
    
    def generate_daily_digest(self, articles: List[Dict], summaries: Dict[str, str], max_retries: int = 3) -> Optional[str]:
        """
        Generate a daily digest summarizing all articles with key themes.
        
        Args:
            articles: List of article dictionaries
            summaries: Dictionary of article summaries (GUID -> summary)
            max_retries: Maximum number of retry attempts
            
        Returns:
            Daily digest string or None if generation fails
        """
        # Prepare article list with summaries
        article_list = []
        for article in articles:
            article_id = article.get('guid', article.get('link', ''))
            summary = summaries.get(article_id, article.get('description', ''))
            article_list.append({
                'title': article.get('title', 'No title'),
                'source': article.get('source', 'Unknown'),
                'summary': summary
            })
        
        prompt = f"""Please create a comprehensive daily news digest in Vietnamese based on the following articles. 
Identify key themes, categorize news by topic, and provide a cohesive overview of the day's news.

Articles:
{self._format_articles_for_digest(article_list)}

Please provide:
1. A brief introduction (1-2 sentences)
2. Key themes and topics covered
3. Categorized summaries grouped by topic
4. A brief conclusion

Daily Digest:"""
        
        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that creates comprehensive daily news digests in Vietnamese, organizing articles by themes and topics."},
                        {"role": "user", "content": prompt}
                    ]
                )
                
                digest = response.choices[0].message.content.strip()
                logger.info("Generated daily digest successfully")
                return digest
                
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed for daily digest: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    logger.error(f"Failed to generate daily digest after {max_retries} attempts")
                    return None
        
        return None
    
    def _format_articles_for_digest(self, articles: List[Dict]) -> str:
        """Format articles for digest prompt."""
        formatted = []
        for idx, article in enumerate(articles, 1):
            formatted.append(
                f"{idx}. [{article['source']}] {article['title']}\n"
                f"   Summary: {article['summary']}\n"
            )
        return "\n".join(formatted)

