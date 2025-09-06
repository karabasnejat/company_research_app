#!/usr/bin/env python3
"""
Test script for the updated Company Research API with URL and keywords support
"""

import requests
import json
import time

# API endpoint
API_URL = "http://localhost:8000"

def test_company_research():
    """Test the company research endpoint with new fields"""
    
    # Test data with new fields
    test_request = {
        "company_name": "Akbank T.A.Ş.",
        "company_url": "https://www.akbank.com",
        "keywords": ["banking", "financial services", "digital banking", "corporate banking"],
        "partners": ["Hakan Binbaşgil", "Suzan Sabancı Dinçer"],
        "include_esg_analysis": True
    }
    
    print("Testing Company Research API with new fields...")
    print(f"Request: {json.dumps(test_request, indent=2, ensure_ascii=False)}")
    print("\n" + "="*50 + "\n")
    
    try:
        # Make the request
        start_time = time.time()
        response = requests.post(
            f"{API_URL}/research",
            json=test_request,
            headers={"Content-Type": "application/json"},
            timeout=120  # 2 minutes timeout
        )
        end_time = time.time()
        
        print(f"Response Status: {response.status_code}")
        print(f"Request Duration: {end_time - start_time:.2f} seconds")
        
        if response.status_code == 200:
            result = response.json()
            print("\n✅ Research completed successfully!")
            print(f"Company: {result['company_name']}")
            print(f"Company URL: {result.get('company_url', 'Not provided')}")
            print(f"Keywords: {', '.join(result.get('keywords', []))}")
            print(f"Partners: {', '.join(result['partners'])}")
            print(f"Processing Time: {result['processing_time_seconds']} seconds")
            print(f"ESG Analysis Included: {'Yes' if result['esg_analysis'] else 'No'}")
            print(f"Total Research Results: {len(result['raw_research_data'])}")
            print(f"Citations Available: {len(result.get('citations', []))}")
            
            # Print summary preview
            print("\n📄 Research Summary Preview:")
            summary_lines = result['research_summary'].split('\n')[:10]
            print('\n'.join(summary_lines))
            if len(result['research_summary'].split('\n')) > 10:
                print("... (truncated)")
            
            # Facility summary preview
            if result.get('facility_summary'):
                print("\n🏭 Facility Summary Preview:")
                facility_lines = result['facility_summary'].split('\n')[:5]
                print('\n'.join(facility_lines))
                if len(result['facility_summary'].split('\n')) > 5:
                    print("... (truncated)")
            
            # Sustainability summary preview
            if result.get('sustainability_summary'):
                print("\n🌱 Sustainability Summary Preview:")
                sustain_lines = result['sustainability_summary'].split('\n')[:5]
                print('\n'.join(sustain_lines))
                if len(result['sustainability_summary'].split('\n')) > 5:
                    print("... (truncated)")
            
            # Citations preview
            if result.get('citations'):
                print(f"\n📚 Citations Preview (first 3 of {len(result['citations'])}):")
                for i, citation in enumerate(result['citations'][:3], 1):
                    print(f"  [{citation['id']}] {citation['title']}")
                    print(f"      {citation['url']}")
            
            # ESG Analysis preview
            if result['esg_analysis']:
                print("\n🌱 ESG Analysis Available:")
                esg = result['esg_analysis']
                for key, value in esg.items():
                    if value and len(value.strip()) > 0:
                        preview = value[:100] + "..." if len(value) > 100 else value
                        print(f"  - {key}: {preview}")
            
        else:
            print(f"❌ Request failed: {response.status_code}")
            print(f"Error: {response.text}")
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out")
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API. Make sure the server is running.")
    except Exception as e:
        print(f"❌ Error: {e}")


def test_markdown_endpoint():
    """Test the markdown format endpoint"""
    test_request = {
        "company_name": "Banat Fırça ve Plastik San. Anonim Şti",
        "company_url": "https://www.banat.com.tr",
        "keywords": ["plastic manufacturing", "brush production"],
        "partners": ["Abdullah Hakan Özkök"],
        "include_esg_analysis": True
    }
    
    print("\n" + "="*50)
    print("Testing Markdown Format Endpoint...")
    print("="*50)
    
    try:
        response = requests.post(
            f"{API_URL}/research/markdown",
            json=test_request,
            headers={"Content-Type": "application/json"},
            timeout=120
        )
        
        if response.status_code == 200:
            print("✅ Markdown response received!")
            markdown_content = response.text
            
            # Save to file
            with open("test_response.md", "w", encoding="utf-8") as f:
                f.write(markdown_content)
            
            print("📄 Markdown response saved to test_response.md")
            
            # Show preview
            lines = markdown_content.split('\n')[:20]
            print("\n📖 Preview of markdown content:")
            print('\n'.join(lines))
            if len(markdown_content.split('\n')) > 20:
                print("... (truncated)")
        else:
            print(f"❌ Markdown request failed: {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Markdown test error: {e}")

def test_health_check():
    """Test the health check endpoint"""
    try:
        response = requests.get(f"{API_URL}/health")
        if response.status_code == 200:
            health_data = response.json()
            print("🏥 Health Check Results:")
            print(f"  Status: {health_data['status']}")
            print(f"  Service: {health_data['service']}")
            print(f"  Version: {health_data['version']}")
            print("  Components:")
            for component, status in health_data['components'].items():
                print(f"    - {component}: {status}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Company Research API Test")
    print("="*50)
    
    # First test health
    if test_health_check():
        print("\n" + "="*50 + "\n")
        # Then test the main functionality
        test_company_research()
        
        # Test markdown endpoint
        test_markdown_endpoint()
    else:
        print("\n❌ API is not healthy. Please check the server.")
