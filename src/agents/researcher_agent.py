from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.tools import Tool
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from typing import List
import asyncio

from ..services.tavily_service import TavilyService
from ..models.schemas import ResearchResult
from ..config import Config


class ResearcherAgent:
    """Agent responsible for researching companies and partners using Tavily"""
    
    def __init__(self):
        self.tavily_service = TavilyService()
        self.llm = ChatOpenAI(
            model=Config.OPENAI_MODEL,
            api_key=Config.OPENAI_API_KEY,
            temperature=0.1
        )
    
    def _create_search_queries(self, company_name: str, partners: List[str]) -> List[str]:
        """Generate search queries for the company and partners"""
        queries = []
        
        # Main company search
        queries.append(f'"{company_name}" company information business profile')
        queries.append(f'"{company_name}" financial information revenue')
        queries.append(f'"{company_name}" news recent developments')
        
        # Partner searches
        for partner in partners:
            queries.append(f'"{partner}" "{company_name}" executive biography')
            queries.append(f'"{partner}" business executive profile')
        
        # Combined searches
        partners_str = " ".join([f'"{partner}"' for partner in partners[:3]])  # Limit to first 3
        queries.append(f'"{company_name}" {partners_str} executives management')
        
        return queries
    
    def _create_esg_search_queries(self, company_name: str, partners: List[str]) -> List[str]:
        """ESG analizi için özel arama sorguları oluştur"""
        esg_queries = []
        
        # 1. Tesis konumları
        esg_queries.append(f'"{company_name}" fabrika tesis konum adres il ilçe')
        esg_queries.append(f'"{company_name}" factory location address coordinates')
        
        # 2. Sürdürülebilirlik raporlaması
        esg_queries.append(f'"{company_name}" sürdürülebilirlik raporu CDP carbon disclosure')
        esg_queries.append(f'"{company_name}" sustainability report environmental social')
        esg_queries.append(f'"{company_name}" TCFD TSRS entegre faaliyet raporu')
        
        # 3. ESG politikaları
        esg_queries.append(f'"{company_name}" ESG politika çevre sosyal yönetişim')
        esg_queries.append(f'"{company_name}" environmental policy social governance')
        
        # 4. Çevre yönetim sistemi
        esg_queries.append(f'"{company_name}" ISO 14001 ISO 45001 çevre yönetim')
        esg_queries.append(f'"{company_name}" environmental management system certification')
        
        # 5. Hukuki sorunlar
        esg_queries.append(f'"{company_name}" çevre dava ceza ÇED olumsuz')
        esg_queries.append(f'"{company_name}" environmental lawsuit penalty fine')
        esg_queries.append(f'"{company_name}" iş kazası çalışan güvenlik')
        
        # 6. Yönetişim sorunları - ortaklar için
        for partner in partners[:3]:  # İlk 3 ortak
            esg_queries.append(f'"{partner}" vergi dava rüşvet yolsuzluk')
            esg_queries.append(f'"{partner}" adil rekabet insan hakları')
        
        # 7. İklim değişikliği
        esg_queries.append(f'"{company_name}" iklim değişikliği karbon emisyon')
        esg_queries.append(f'"{company_name}" climate change carbon neutral net zero')
        esg_queries.append(f'"{company_name}" renewable energy green energy')
        
        return esg_queries
    
    async def research(self, company_name: str, partners: List[str], include_esg: bool = True) -> List[ResearchResult]:
        """
        Research the company and its partners
        
        Args:
            company_name: Name of the company to research
            partners: List of partner/founder names
            include_esg: Include ESG-specific research
            
        Returns:
            List of ResearchResult objects containing search results
        """
        # Generate search queries
        queries = self._create_search_queries(company_name, partners)
        
        # ESG sorguları ekle
        if include_esg:
            esg_queries = self._create_esg_search_queries(company_name, partners)
            queries.extend(esg_queries)
        
        print(f"Generated {len(queries)} search queries for research (ESG: {include_esg})")
        
        # Perform searches
        research_results = await self.tavily_service.search_multiple(queries)
        
        print(f"Completed research with {len(research_results)} result sets")
        
        return research_results
    
    def get_research_summary(self, research_results: List[ResearchResult]) -> str:
        """Generate a brief summary of research findings"""
        total_results = sum(len(result.results) for result in research_results)
        successful_queries = len([r for r in research_results if r.results])
        
        return f"Research completed: {successful_queries} successful queries, {total_results} total results found"
