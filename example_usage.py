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
        company_name="Banat Fırça ve Plastik San. Anonim Şti",
        partners=[
            "Abdullah Hakan Özkök", 
            "Gökhan Özkök", 
            "Şemen Özkök Erbağan", 
            "Helen Özkök"
        ],
        include_esg_analysis=True  # ESG analizi dahil et
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
        
        # ESG Analizi sonuçlarını yazdır
        if result.esg_analysis:
            print(f"\n{'='*50}")
            print("ESG ANALİZİ SONUÇLARI")
            print(f"{'='*50}")
            
            print(f"\n🏭 TESİS KONUMLARI:")
            print(result.esg_analysis.facility_locations)
            
            print(f"\n📊 SÜRDÜRÜLEBİLİRLİK RAPORLAMASI:")
            print(result.esg_analysis.sustainability_reporting)
            
            print(f"\n📋 ESG POLİTİKALARI:")
            print(result.esg_analysis.esg_policies)
            
            print(f"\n🌱 ÇEVRE YÖNETİM SİSTEMİ:")
            print(result.esg_analysis.environmental_management)
            
            print(f"\n⚖️ HUKUKİ SORUNLAR:")
            print(result.esg_analysis.legal_issues)
            
            print(f"\n🏛️ YÖNETİŞİM SORUNLARI:")
            print(result.esg_analysis.governance_issues)
            
            print(f"\n🌍 İKLİM AKSIYON PLANLARI:")
            print(result.esg_analysis.climate_action)
        
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
