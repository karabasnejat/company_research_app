from pydantic import BaseModel
from typing import List, Optional


class ESGAnalysisResult(BaseModel):
    """ESG analizi sonucu"""
    facility_locations: str  # Tesis konumları
    sustainability_reporting: str  # Sürdürülebilirlik raporlaması
    esg_policies: str  # ESG politikaları
    environmental_management: str  # Çevre yönetim sistemi
    legal_issues: str  # Hukuki sorunlar
    governance_issues: str  # Yönetişim sorunları
    climate_action: str  # İklim değişikliği planları


class CompanyResearchRequest(BaseModel):
    """Request model for company research"""
    company_name: str
    partners: List[str]
    include_esg_analysis: bool = True  # ESG analizi dahil edilsin mi


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
    esg_analysis: Optional[ESGAnalysisResult] = None  # ESG analizi sonuçları
    raw_research_data: List[ResearchResult]
    processing_time_seconds: float
