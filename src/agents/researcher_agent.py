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
    
    async def research(self, company_name: str, partners: List[str]) -> List[ResearchResult]:
        """
        Research the company and its partners
        
        Args:
            company_name: Name of the company to research
            partners: List of partner/founder names
            
        Returns:
            List of ResearchResult objects containing search results
        """
        # Generate search queries
        queries = self._create_search_queries(company_name, partners)
        
        print(f"Generated {len(queries)} search queries for research")
        
        # Perform searches
        research_results = await self.tavily_service.search_multiple(queries)
        
        print(f"Completed research with {len(research_results)} result sets")
        
        return research_results
    
    def get_research_summary(self, research_results: List[ResearchResult]) -> str:
        """Generate a brief summary of research findings"""
        total_results = sum(len(result.results) for result in research_results)
        successful_queries = len([r for r in research_results if r.results])
        
        return f"Research completed: {successful_queries} successful queries, {total_results} total results found"
