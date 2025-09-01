from pydantic import BaseModel
from typing import List


class CompanyResearchRequest(BaseModel):
    """Request model for company research"""
    company_name: str
    partners: List[str]


class SearchResult(BaseModel):
    """Individual search result"""
    title: str
    url: str
    content: str
    relevance_score: float = 0.0


class ResearchResult(BaseModel):
    """Research results from Tavily"""
    query: str
    results: List[SearchResult]


class CompanyResearchResponse(BaseModel):
    """Response model for company research"""
    company_name: str
    partners: List[str]
    research_summary: str
    raw_research_data: List[ResearchResult]
    processing_time_seconds: float
