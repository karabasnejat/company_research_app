from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
import time
import asyncio

from .config import Config
from .models.schemas import CompanyResearchRequest, CompanyResearchResponse
from .agents.researcher_agent import ResearcherAgent
from .agents.summarizer_agent import SummarizerAgent
from .agents.esg_agent import ESGAgent
from .utils.formatting import format_response_as_markdown

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
esg_agent = ESGAgent()


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
    Research a company and its partners/founders with optional ESG analysis
    
    Args:
        request: CompanyResearchRequest containing company name, partners, and ESG flag
        
    Returns:
        CompanyResearchResponse with summary, ESG analysis, and raw research data
    """
    start_time = time.time()
    
    try:
        print(f"Starting research for company: {request.company_name}")
        print(f"Company URL: {request.company_url}")
        print(f"Keywords: {request.keywords}")
        print(f"Partners: {request.partners}")
        print(f"ESG Analysis: {request.include_esg_analysis}")
        
        # Step 1: Research using Tavily
        print("Step 1: Performing research with Tavily...")
        research_results = await researcher_agent.research(
            company_name=request.company_name,
            company_url=request.company_url,
            keywords=request.keywords,
            partners=request.partners,
            include_esg=request.include_esg_analysis
        )
        
        if not research_results:
            raise HTTPException(
                status_code=500,
                detail="No research results were obtained. Please check your API keys and try again."
            )
        
        # Step 2: Summarize using GPT-4o
        print("Step 2: Generating summary with GPT-4o...")
        research_summary, facility_summary, sustainability_summary, citations = await summarizer_agent.summarize(
            company_name=request.company_name,
            company_url=request.company_url,
            keywords=request.keywords,
            partners=request.partners,
            research_results=research_results
        )
        
        # Step 3: ESG Analysis (if requested)
        esg_analysis = None
        if request.include_esg_analysis:
            print("Step 3: Performing ESG analysis...")
            esg_analysis = await esg_agent.analyze_esg(
                company_name=request.company_name,
                company_url=request.company_url,
                keywords=request.keywords,
                partners=request.partners,
                research_results=research_results
            )
        
        processing_time = time.time() - start_time
        print(f"Research completed in {processing_time:.2f} seconds")
        
        return CompanyResearchResponse(
            company_name=request.company_name,
            company_url=request.company_url,
            keywords=request.keywords,
            partners=request.partners,
            research_summary=research_summary,
            facility_summary=facility_summary,
            sustainability_summary=sustainability_summary,
            esg_analysis=esg_analysis,
            citations=citations,
            raw_research_data=research_results,
            processing_time_seconds=round(processing_time, 2)
        )
        
    except Exception as e:
        print(f"Error during research: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred during research: {str(e)}"
        )


@app.post("/research/markdown", response_class=PlainTextResponse)
async def research_company_markdown(request: CompanyResearchRequest):
    """
    Research a company and return results in markdown format (like test.md)
    """
    # Get JSON response first
    json_response = await research_company(request)
    
    # Convert to markdown format
    markdown_content = format_response_as_markdown(json_response)
    
    return markdown_content


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
