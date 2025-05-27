import os
import time
import random
import hashlib
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class WebstoryGenerator:
    """Class to handle webstory image generation using BytePlus text-to-image API."""
    
    def __init__(self):
        """Initialize the generator with API details from environment variables."""
        self.api_key = os.getenv("CV_API_KEY")
        self.api_secret = os.getenv("CV_API_SECRET")
        self.api_endpoint = os.getenv("CV_API_ENDPOINT")
        self.req_key = os.getenv("CV_REQ_KEY")
        
        if not all([self.api_key, self.api_secret, self.api_endpoint, self.req_key]):
            raise ValueError("Missing required environment variables for text-to-image API")
    
    def _generate_signature(self, nonce, timestamp):
        """Generate signature for API authentication."""
        keys = [str(nonce), self.api_secret, str(timestamp)]
        keys.sort()
        key_str = ''.join(keys).encode('utf-8')
        signature = hashlib.sha1(key_str).hexdigest()
        return signature.lower()
    
    def generate_webstory_image(self, text, style="webstory"):
        """Generate a webstory image based on the provided text.
        
        Args:
            text (str): The text to generate an image for (title or bullet point).
            style (str): The style of image to generate ("webstory" or "title").
            
        Returns:
            str: URL of the generated image.
        """
        timestamp = int(time.time())
        nonce = random.randint(0, (1 << 31) - 1)
        
        # Parameters for signature
        req_params = {
            "api_key": self.api_key,
            "timestamp": str(timestamp),
            "nonce": str(nonce),
            "sign": self._generate_signature(nonce, timestamp)
        }
        
        # Request headers
        req_headers = {
            "Content-Type": "application/json"
        }
        
        # Clean input text by removing markdown and special formatting
        cleaned_text = text
        # Remove Visual prompt prefix
        if "**Visual prompt:**" in cleaned_text:
            cleaned_text = cleaned_text.split("**Visual prompt:**", 1)[1].strip()
        # Remove any remaining markdown formatting
        cleaned_text = cleaned_text.replace("**", "").replace("*", "").strip()
        # Remove any surrounding quotes
        cleaned_text = cleaned_text.strip('"').strip("'")  # Remove both single and double quotes
        
        # Adjust prompt based on style
        if style == "title":
            prompt = cleaned_text
            print(f"\n VLM Generating Title Image:\nStyle: {style}\nInput Text: {cleaned_text}\nPrompt: {prompt}\n")
        else:
            prompt = cleaned_text
            print(f"\n VLM Generating Story Image:\nStyle: {style}\nInput Text: {cleaned_text}\nPrompt: {prompt}\n")
        
        # Clean and truncate the prompt
        prompt = prompt.strip()
        if len(prompt) > 200:
            prompt = prompt[:200]
        
        # Request body
        req_body = {
            "req_key": self.req_key,
            "prompt": prompt,
            "return_url": True,
            "scale" : 7.0,
            "logo_info": {
                "add_logo": True,
                "position": 0,
                "language": 0,
                "opacity": 0.3,
                "width": 720,
                "height": 1280,
                "logo_text_content": "@BytePlus 2025"
            }
        }
        
        try:
            print(f"\nSending API request with parameters:\n{req_params}\n")
            print(f"Request body:\n{req_body}\n")
            
            response = requests.post(
                self.api_endpoint,
                params=req_params,
                headers=req_headers,
                json=req_body
            )
            
            if response.status_code != 200:
                print(f"API Error Response:\n{response.text}\n")
                raise Exception(f"API request failed with status {response.status_code}: {response.text}")
            
            result = response.json()
            print(f"API Response:\n{result}\n")
            
            if result["code"] != 10000 or not result["data"]["image_urls"]:
                raise Exception(f"API error: {result.get('message', 'Unknown error')}")
            
            return result["data"]["image_urls"][0]
            
        except Exception as e:
            print(f"Error details: {str(e)}")
            raise Exception(f"Failed to generate webstory image: {str(e)}")