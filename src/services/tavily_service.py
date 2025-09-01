from tavily import TavilyClient
from typing import List
import asyncio
from ..config import Config
from ..models.schemas import SearchResult, ResearchResult


class TavilyService:
    """Service for interacting with Tavily search API"""
    
    def __init__(self):
        self.client = TavilyClient(api_key=Config.TAVILY_API_KEY)
    
    async def search(self, query: str, max_results: int = None) -> ResearchResult:
        """
        Perform a search using Tavily
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            
        Returns:
            ResearchResult containing search results
        """
        if max_results is None:
            max_results = Config.TAVILY_MAX_RESULTS
        
        try:
            # Perform the search
            response = await asyncio.to_thread(
                self.client.search,
                query=query,
                search_depth="advanced",
                max_results=max_results,
                include_answer=True,
                include_raw_content=True
            )
            
            # Parse results
            search_results = []
            for result in response.get("results", []):
                search_result = SearchResult(
                    title=result.get("title", ""),
                    url=result.get("url", ""),
                    content=result.get("content", ""),
                    relevance_score=result.get("score", 0.0)
                )
                search_results.append(search_result)
            
            return ResearchResult(
                query=query,
                results=search_results
            )
            
        except Exception as e:
            print(f"Error searching with Tavily: {e}")
            return ResearchResult(
                query=query,
                results=[]
            )
    
    async def search_multiple(self, queries: List[str]) -> List[ResearchResult]:
        """
        Perform multiple searches concurrently
        
        Args:
            queries: List of search query strings
            
        Returns:
            List of ResearchResult objects
        """
        # Limit concurrent searches
        semaphore = asyncio.Semaphore(Config.MAX_CONCURRENT_SEARCHES)
        
        async def search_with_semaphore(query):
            async with semaphore:
                return await self.search(query)
        
        tasks = [search_with_semaphore(query) for query in queries]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and return valid results
        valid_results = []
        for result in results:
            if isinstance(result, ResearchResult):
                valid_results.append(result)
            else:
                print(f"Search failed: {result}")
        
        return valid_results
