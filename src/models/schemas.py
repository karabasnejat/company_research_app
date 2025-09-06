from pydantic import BaseModel
from typing import List, Optional


class Citation(BaseModel):
    """Citation/kaynak referansı"""
    id: str  # [1], [2] gibi
    title: str
    url: str
    content_preview: str = ""  # İçerik önizlemesi


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
    company_url: Optional[str] = None  # Şirket web sitesi URL'si
    keywords: List[str] = []  # Firma hakkında anahtar kelimeler
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
    company_url: Optional[str] = None
    keywords: List[str]
    partners: List[str]
    research_summary: str
    facility_summary: str = ""  # Tesis bilgileri özeti
    sustainability_summary: str = ""  # Sürdürülebilirlik özeti
    esg_analysis: Optional[ESGAnalysisResult] = None  # ESG analizi sonuçları
    citations: List[Citation] = []  # Kaynak referansları
    raw_research_data: List[ResearchResult]
    processing_time_seconds: float
