from tavily import TavilyClient
from typing import List
import asyncio
from ..config import Config
from ..models.schemas import SearchResult, ResearchResult

# Timeout for external Tavily API calls (in seconds)
TAVILY_CALL_TIMEOUT = 30.0


class TavilyService:
    """Service for interacting with Tavily search API"""
    
    def __init__(self):
        self.client = TavilyClient(api_key=Config.TAVILY_API_KEY)
        
        # Türkiye'deki önemli kaynaklar için include domains
        self.include_domains = [
            "kap.org.tr",           # Kamuyu Aydınlatma Platformu
            "ticaretsicil.gov.tr",  # Ticaret Sicil Gazetesi
            "resmigazete.gov.tr",   # Resmi Gazete
            "ilan.gov.tr",          # İlan portalı
            "linkedin.com",         # Profesyonel ağ
            "hurriyet.com.tr",      # Yerel gazete
            "sabah.com.tr",         # Yerel gazete
            "milliyet.com.tr",      # Yerel gazete
            "haberturk.com",        # Yerel gazete
            "sozcu.com.tr",         # Yerel gazete
            "cumhuriyet.com.tr",    # Yerel gazete
            "aa.com.tr",            # Anadolu Ajansı
            "reuters.com",          # Uluslararası haber
            "bloomberg.com",        # Finansal haber
            "ft.com",               # Financial Times
            "wsj.com",              # Wall Street Journal
            "investing.com",        # Finansal bilgi
            "finans.mynet.com",     # Türkiye finansal
            "bigpara.hurriyet.com.tr", # Finansal
            "foreks.com",           # Finansal
            "tr.tradingview.com"    # Finansal analiz
        ]
        
        # Hariç tutulacak domainler
        self.exclude_domains = [
            "youtube.com",
            "youtu.be",
            "instagram.com",
            "facebook.com",
            "twitter.com",
            "x.com",
            "tiktok.com",
            "huggingface.co",
            "github.com",
            "stackoverflow.com",
            "reddit.com",
            "pinterest.com",
            "tumblr.com",
            "snapchat.com",
            "discord.com",
            "telegram.org",
            "whatsapp.com",
            "medium.com",
            "wordpress.com",
            "blogger.com",
            "wix.com",
            "squarespace.com"
        ]
    
    async def search(self, query: str, max_results: int = None, use_include_domains: bool = True) -> ResearchResult:
        """
        Perform a search using Tavily with domain filtering
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            use_include_domains: Whether to use include_domains filter
            
        Returns:
            ResearchResult containing search results
        """
        if max_results is None:
            max_results = Config.TAVILY_MAX_RESULTS
        
        try:
            # Prepare search parameters
            search_params = {
                "query": query,
                "search_depth": "advanced",
                "max_results": max_results,
                "include_answer": True,
                "include_raw_content": True,
                "exclude_domains": self.exclude_domains
            }
            
            # Add include domains for targeted searches
            if use_include_domains:
                search_params["include_domains"] = self.include_domains
            
            # Perform the search with timeout
            try:
                response = await asyncio.wait_for(
                    asyncio.to_thread(
                        self.client.search,
                        **search_params
                    ),
                    timeout=TAVILY_CALL_TIMEOUT
                )
            except asyncio.TimeoutError:
                print(f"Tavily search timed out after {TAVILY_CALL_TIMEOUT} seconds for query: {query}")
                return ResearchResult(
                    query=query,
                    results=[]
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
        Perform multiple searches concurrently with different strategies
        
        Args:
            queries: List of search query strings
            
        Returns:
            List of ResearchResult objects
        """
        # Limit concurrent searches
        semaphore = asyncio.Semaphore(Config.MAX_CONCURRENT_SEARCHES)
        
        async def search_with_semaphore(query_info):
            query, use_include = query_info
            async with semaphore:
                return await self.search(query, use_include_domains=use_include)
        
        # Prepare queries with different strategies
        query_tasks = []
        for query in queries:
            # First search with targeted domains
            query_tasks.append((query, True))
            
            # For some queries, also do general search
            if any(keyword in query.lower() for keyword in ["dava", "olumsuz", "risk", "sorun"]):
                query_tasks.append((query + " -site:youtube.com -site:facebook.com", False))
        
        tasks = [search_with_semaphore(query_info) for query_info in query_tasks]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and return valid results
        valid_results = []
        for result in results:
            if isinstance(result, ResearchResult):
                valid_results.append(result)
            else:
                print(f"Search failed: {result}")
        
        return valid_results
    
    async def search_with_legal_focus(self, company_name: str, partners: List[str]) -> List[ResearchResult]:
        """
        Perform searches with focus on legal, financial and regulatory information
        
        Args:
            company_name: Company name
            partners: List of partner names
            
        Returns:
            List of ResearchResult objects
        """
        # Sanitize inputs to prevent query breakage
        def sanitize_query_input(text: str) -> str:
            """Escape quotes and backslashes for safe query interpolation"""
            return text.replace('\\', '\\\\').replace('"', '\\"')
        
        sanitized_company_name = sanitize_query_input(company_name)
        sanitized_partners = [sanitize_query_input(partner) for partner in partners]
        
        legal_queries = []
        
        # KAP specific searches
        legal_queries.extend([
            f'site:kap.org.tr "{sanitized_company_name}"',
            f'site:kap.org.tr "{sanitized_company_name}" mali tablo',
            f'site:kap.org.tr "{sanitized_company_name}" özel durum'
        ])
        
        # Ticaret Sicil searches
        legal_queries.extend([
            f'site:ticaretsicil.gov.tr "{sanitized_company_name}"',
            f'"{sanitized_company_name}" ticaret sicili sermaye',
            f'"{sanitized_company_name}" ortaklık yapısı'
        ])
        
        # Legal and risk searches
        for sanitized_partner in sanitized_partners[:3]:  # Limit to first 3 partners
            legal_queries.extend([
                f'"{sanitized_partner}" "{sanitized_company_name}" dava',
                f'"{sanitized_partner}" "{sanitized_company_name}" icra',
                f'"{sanitized_partner}" risk analizi'
            ])
        
        # Resmi Gazete searches for critical information
        legal_queries.extend([
            f'site:resmigazete.gov.tr "{sanitized_company_name}"',
            f'site:ilan.gov.tr "{sanitized_company_name}"'
        ])
        
        return await self.search_multiple(legal_queries)
