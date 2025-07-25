"""
Simple LLM Router for Make Know Pipe

Routes different content types to appropriate LLMs:
- Groq: Images, diagrams, screenshots
- Gemini: Code, docs, complex analysis
"""

import os
import base64
from typing import Any, Dict, Optional
from enum import Enum
import logging

try:
    from groq import Groq
except ImportError:
    Groq = None

try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None
    types = None

logger = logging.getLogger(__name__)

class ContentType(Enum):
    """Content types for processing"""
    CODE = "code"
    DOCUMENTATION = "documentation"
    API = "api"
    LOGS = "logs"
    IMAGE = "image"
    TEXT = "text"

class LLMRouter:
    """Simple LLM routing for different content types"""
    
    def __init__(self):
        """Initialize LLM clients"""
        self.groq_client = None
        self.gemini_client = None
        
        # Initialize clients if API keys are available
        if os.environ.get("GROQ_API_KEY") and Groq:
            try:
                self.groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
                logger.info("Groq client initialized")
            except Exception as e:
                logger.warning(f"Could not initialize Groq client: {e}")
        
        if os.environ.get("GEMINI_API_KEY") and genai:
            try:
                self.gemini_client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
                logger.info("Gemini client initialized")
            except Exception as e:
                logger.warning(f"Could not initialize Gemini client: {e}")
    
    async def analyze_content(self, content: str, content_type: ContentType, prompt: str) -> str:
        """
        Analyze content using appropriate LLM
        
        Args:
            content: Content to analyze
            content_type: Type of content
            prompt: Analysis prompt
            
        Returns:
            Analysis result as string
        """
        if content_type == ContentType.IMAGE:
            return await self._analyze_image(content, prompt)
        else:
            return await self._analyze_text(content, prompt, content_type)
    
    async def _analyze_image(self, image_path: str, prompt: str) -> str:
        """Analyze image using Groq vision"""
        if not self.groq_client:
            return "Image analysis not available - Groq client not initialized"
        
        try:
            # Encode image
            with open(image_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')
            
            # Create completion
            chat_completion = self.groq_client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}",
                                },
                            },
                        ],
                    }
                ],
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                max_tokens=4096,
                temperature=0.1,
            )
            
            return chat_completion.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error analyzing image: {e}")
            return f"Error analyzing image: {str(e)}"
    
    async def _analyze_text(self, content: str, prompt: str, content_type: ContentType) -> str:
        """Analyze text content using Gemini"""
        if not self.gemini_client:
            return "Text analysis not available - Gemini client not initialized"
        
        try:
            # Prepare input
            full_prompt = f"{prompt}\n\nContent to analyze:\n{content}"
            
            contents = [
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=full_prompt)],
                ),
            ]
            
            generate_content_config = types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(thinking_budget=-1),
            )
            
            # Generate response
            response_text = ""
            async for chunk in self.gemini_client.models.generate_content_stream(
                model="gemini-2.5-pro",
                contents=contents,
                config=generate_content_config,
            ):
                if chunk.text:
                    response_text += chunk.text
            
            return response_text
            
        except Exception as e:
            logger.error(f"Error analyzing text content: {e}")
            return f"Error analyzing content: {str(e)}"
    
    def is_available(self) -> bool:
        """Check if at least one LLM client is available"""
        return self.groq_client is not None or self.gemini_client is not None