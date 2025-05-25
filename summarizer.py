"""Module for article summarization using BytePlus LLM API."""

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ArticleSummarizer:
    """Class to handle article summarization using BytePlus LLM API."""
    
    def __init__(self):
        """Initialize the summarizer with API details from environment variables."""
        self.api_key = os.getenv("ARK_API_KEY")
        self.api_endpoint = os.getenv("ARK_API_ENDPOINT")
        self.model_id = os.getenv("ARK_MODEL_ID")
        
        if not all([self.api_key, self.api_endpoint, self.model_id]):
            raise ValueError("Missing required environment variables for LLM API")
    
    def summarize_article(self, article_text):
        """Summarize the given article text using BytePlus LLM API.
        
        Args:
            article_text (str): The news article text to summarize.
            
        Returns:
            list: A list of bullet points summarizing the article.
            
        Raises:
            Exception: If the API request fails.
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        payload = {
            "model": self.model_id,
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert in summarizing news article and return summary of article in maximum 3 bullet points."
                },
                {
                    "role": "user",
                    "content": article_text
                }
            ]
        }
        
        try:
            response = requests.post(self.api_endpoint, headers=headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            summary_text = result["choices"][0]["message"]["content"]
            
            # Parse the bullet points from the markdown response
            bullet_points = [point.strip().lstrip('-').strip() for point in summary_text.split('\n') if point.strip().startswith('-')]
            
            return bullet_points
            
        except Exception as e:
            raise Exception(f"Failed to summarize article: {str(e)}")