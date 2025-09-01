from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import time
import asyncio

from .config import Config
from .models.schemas import CompanyResearchRequest, CompanyResearchResponse
from .agents.researcher_agent import ResearcherAgent
from .agents.summarizer_agent import SummarizerAgent

# Validate configuration on startup
try:
    Config.validate_config()
except ValueError as e:
    print(f"Configuration error: {e}")
    print("Please check your .env file and ensure all required API keys are set.")
    exit(1)

# Initialize FastAPI app
app = FastAPI(
    title="Company Research API",
    description="A REST service for researching companies and their partners using Tavily and GPT-4o",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agents
researcher_agent = ResearcherAgent()
summarizer_agent = SummarizerAgent()


@app.get("/")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Company Research API",
        "version": "1.0.0"
    }


@app.post("/research", response_model=CompanyResearchResponse)
async def research_company(request: CompanyResearchRequest):
    """
    Bir şirket ve ortaklarını/kurucularını araştır
    
    Args:
        request: Şirket adı ve ortakları içeren CompanyResearchRequest
        
    Returns:
        Özet ve ham araştırma verileri içeren CompanyResearchResponse
    """
    start_time = time.time()
    
    try:
        print(f"🏢 Araştırma başlatılıyor: {request.company_name}")
        print(f"👥 Ortaklar: {request.partners}")
        
        # Adım 1: Tavily ile araştırma
        print("🔍 1. Adım: Tavily ile veri toplama...")
        research_results = await researcher_agent.research(
            company_name=request.company_name,
            partners=request.partners
        )
        
        if not research_results:
            raise HTTPException(
                status_code=500,
                detail="Araştırma sonucu alınamadı. Lütfen API anahtarlarınızı kontrol edin ve tekrar deneyin."
            )
        
        # Adım 2: GPT-4o ile özetleme
        print("🤖 2. Adım: GPT-4o ile özet oluşturuluyor...")
        summary = await summarizer_agent.summarize(
            company_name=request.company_name,
            partners=request.partners,
            research_results=research_results
        )
        
        processing_time = time.time() - start_time
        print(f"✅ Araştırma {processing_time:.2f} saniyede tamamlandı")
        
        return CompanyResearchResponse(
            company_name=request.company_name,
            partners=request.partners,
            research_summary=summary,
            raw_research_data=research_results,
            processing_time_seconds=round(processing_time, 2)
        )
        
    except HTTPException:
        # Re-raise HTTPException unchanged to preserve original status and detail
        raise
    except Exception as e:
        print(f"❌ Araştırma sırasında hata: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Araştırma sırasında bir hata oluştu: {str(e)}"
        )


@app.get("/health")
async def detailed_health_check():
    """Detailed health check with service status"""
    return {
        "status": "healthy",
        "service": "Company Research API",
        "version": "1.0.0",
        "components": {
            "tavily_api": "configured" if Config.TAVILY_API_KEY else "not configured",
            "openai_api": "configured" if Config.OPENAI_API_KEY else "not configured",
            "model": Config.OPENAI_MODEL
        },
        "configuration": {
            "max_tavily_results": Config.TAVILY_MAX_RESULTS,
            "search_timeout": Config.SEARCH_TIMEOUT,
            "max_concurrent_searches": Config.MAX_CONCURRENT_SEARCHES
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
