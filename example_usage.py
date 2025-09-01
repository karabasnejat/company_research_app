"""
Example usage script for the Company Research API
"""
import asyncio
import json
from src.main import app
from src.models.schemas import CompanyResearchRequest


async def test_research():
    """Test the research functionality"""
    
    # Example request data
    request_data = CompanyResearchRequest(
        company_name="Midas Hediyelik Eşya San. ve Tic. Anonim Şti.",
        partners=[
            "Can Özkök", 
            "Münir Özkök", 
            "İlyas Özkök", 
            "Bülent Özkök", 
            "Gökhan Özkök", 
            "Helen Özkök", 
            "Berlin Özkök", 
            "Şemen Özkök Erbağan"
        ]
    )
    
    print("Testing Company Research API...")
    print(f"Company: {request_data.company_name}")
    print(f"Partners: {request_data.partners}")
    print("\nStarting research...")
    
    try:
        # Import the research function from main
        from src.main import research_company
        
        # Run the research
        result = await research_company(request_data)
        
        print(f"\nResearch completed in {result.processing_time_seconds} seconds")
        print(f"\nSummary:\n{result.research_summary}")
        print(f"\nFound {len(result.raw_research_data)} research result sets")
        
        # Save results to file
        with open("research_results.json", "w", encoding="utf-8") as f:
            json.dump(result.dict(), f, indent=2, ensure_ascii=False)
        
        print("\nResults saved to research_results.json")
        
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    print("Make sure you have set up your .env file with API keys before running this test!")
    print("Press Enter to continue or Ctrl+C to cancel...")
    input()
    
    asyncio.run(test_research())
