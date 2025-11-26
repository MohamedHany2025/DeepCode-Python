# Web Scraper Pro - Intelligent Web Scraping Tool
# Project: Web Scraper Pro
# Language: Python
# Description: Intelligent web scraping tool with proxy support, rate limiting, and data transformation

import asyncio
import aiohttp
from bs4 import BeautifulSoup
import logging
from typing import List, Dict, Optional, Callable
from datetime import datetime, timedelta
from collections import defaultdict
import json
from abc import ABC, abstractmethod

# ==================== Configuration ====================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ScraperConfig:
    def __init__(self):
        self.timeout = 10
        self.max_retries = 3
        self.retry_delay = 1
        self.rate_limit_requests = 10
        self.rate_limit_window = 60
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        ]
        self.proxies = []

# ==================== Rate Limiting ====================
class RateLimiter:
    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = defaultdict(list)
    
    async def acquire(self, identifier: str = "default") -> bool:
        """Check if we can make a request"""
        now = datetime.utcnow()
        cutoff = now - timedelta(seconds=self.window_seconds)
        
        # Remove old requests
        self.requests[identifier] = [
            req_time for req_time in self.requests[identifier]
            if req_time > cutoff
        ]
        
        if len(self.requests[identifier]) < self.max_requests:
            self.requests[identifier].append(now)
            return True
        
        return False
    
    async def wait_if_needed(self, identifier: str = "default"):
        """Wait until we can make a request"""
        while not await self.acquire(identifier):
            await asyncio.sleep(0.1)

# ==================== Data Transformers ====================
class DataTransformer(ABC):
    @abstractmethod
    def transform(self, data: Dict) -> Dict:
        pass

class CleaningTransformer(DataTransformer):
    """Remove empty values and normalize data"""
    def transform(self, data: Dict) -> Dict:
        return {
            k: v.strip() if isinstance(v, str) else v
            for k, v in data.items()
            if v is not None and v != ""
        }

class ValidatingTransformer(DataTransformer):
    """Validate data against schema"""
    def __init__(self, schema: Dict[str, type]):
        self.schema = schema
    
    def transform(self, data: Dict) -> Dict:
        validated = {}
        for key, expected_type in self.schema.items():
            if key in data:
                try:
                    validated[key] = expected_type(data[key])
                except (ValueError, TypeError):
                    logger.warning(f"Could not convert {key} to {expected_type}")
        return validated

class CachingTransformer(DataTransformer):
    """Cache transformed data"""
    def __init__(self):
        self.cache = {}
    
    def transform(self, data: Dict) -> Dict:
        key = json.dumps(data, sort_keys=True)
        if key not in self.cache:
            self.cache[key] = data
        return self.cache[key]

# ==================== Web Scraper ====================
class WebScraper:
    def __init__(self, config: Optional[ScraperConfig] = None):
        self.config = config or ScraperConfig()
        self.rate_limiter = RateLimiter(
            self.config.rate_limit_requests,
            self.config.rate_limit_window
        )
        self.transformers: List[DataTransformer] = []
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def add_transformer(self, transformer: DataTransformer):
        """Add a data transformer"""
        self.transformers.append(transformer)
        return self
    
    async def fetch(self, url: str, **kwargs) -> Optional[str]:
        """Fetch URL with retry logic and rate limiting"""
        await self.rate_limiter.wait_if_needed()
        
        headers = kwargs.pop('headers', {})
        headers['User-Agent'] = self._get_user_agent()
        
        for attempt in range(self.config.max_retries):
            try:
                async with self.session.get(
                    url,
                    timeout=self.config.timeout,
                    headers=headers,
                    **kwargs
                ) as response:
                    if response.status == 200:
                        return await response.text()
                    else:
                        logger.warning(f"Status {response.status} for {url}")
            except asyncio.TimeoutError:
                logger.warning(f"Timeout for {url}, attempt {attempt + 1}")
                if attempt < self.config.max_retries - 1:
                    await asyncio.sleep(self.config.retry_delay)
            except Exception as e:
                logger.error(f"Error fetching {url}: {e}")
        
        return None
    
    def _get_user_agent(self) -> str:
        """Get random user agent"""
        import random
        return random.choice(self.config.user_agents)
    
    def parse_html(self, html: str, selector: str) -> List[str]:
        """Parse HTML with CSS selector"""
        soup = BeautifulSoup(html, 'html.parser')
        elements = soup.select(selector)
        return [str(el) for el in elements]
    
    def extract_data(self, html: str, extractors: Dict[str, str]) -> Dict:
        """Extract data using CSS selectors"""
        soup = BeautifulSoup(html, 'html.parser')
        data = {}
        
        for key, selector in extractors.items():
            element = soup.select_one(selector)
            data[key] = element.get_text(strip=True) if element else None
        
        return data
    
    def apply_transformers(self, data: Dict) -> Dict:
        """Apply all transformers to data"""
        for transformer in self.transformers:
            data = transformer.transform(data)
        return data
    
    async def scrape(
        self,
        url: str,
        extractors: Dict[str, str],
        transform: bool = True
    ) -> Optional[Dict]:
        """Complete scrape operation"""
        html = await self.fetch(url)
        if not html:
            return None
        
        data = self.extract_data(html, extractors)
        
        if transform:
            data = self.apply_transformers(data)
        
        return data
    
    async def scrape_multiple(
        self,
        urls: List[str],
        extractors: Dict[str, str],
        transform: bool = True
    ) -> List[Dict]:
        """Scrape multiple URLs concurrently"""
        tasks = [self.scrape(url, extractors, transform) for url in urls]
        results = await asyncio.gather(*tasks)
        return [r for r in results if r is not None]

# ==================== Usage Example ====================
async def main():
    config = ScraperConfig()
    config.rate_limit_requests = 5
    config.rate_limit_window = 60
    
    async with WebScraper(config) as scraper:
        # Add transformers
        scraper.add_transformer(CleaningTransformer())
        scraper.add_transformer(ValidatingTransformer({
            'title': str,
            'price': float,
            'description': str
        }))
        
        # Single URL scrape
        url = "https://example.com/product"
        extractors = {
            'title': 'h1.product-title',
            'price': 'span.product-price',
            'description': 'p.product-description'
        }
        
        result = await scraper.scrape(url, extractors)
        print("Scraped data:", result)
        
        # Multiple URLs
        urls = [
            "https://example.com/product/1",
            "https://example.com/product/2",
            "https://example.com/product/3",
        ]
        
        results = await scraper.scrape_multiple(urls, extractors)
        print(f"Scraped {len(results)} products")
        for i, result in enumerate(results):
            print(f"Product {i+1}: {result}")

if __name__ == "__main__":
    asyncio.run(main())
