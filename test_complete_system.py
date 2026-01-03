import requests
import json
import time
from pathlib import Path

BASE_URL = "http://localhost:8000"

def test_all_agents_complete():
    """Test all 4 agents with comprehensive scenarios"""
    
    print("="*60)
    print("COMPLETE SYSTEM TEST - ALL 4 AGENTS")
    print("="*60)
    
    test_results = []
    
    # 1. Test Weather Agent
    print("\n1. Testing Weather Agent...")
    weather_queries = [
        "What is the weather in Chennai today?",
        "What was the weather in Bengaluru yesterday?",
        "What will the weather be like in London tomorrow?"
    ]
    
    for query in weather_queries:
        response = requests.post(
            f"{BASE_URL}/api/weather",
            json={"query": query}
        )
        success = response.status_code == 200 and response.json().get("success", False)
        test_results.append(("Weather", query, success))
        print(f"  ✓ {query[:50]}...: {'PASS' if success else 'FAIL'}")
    
    # 2. Test Database Agent
    print("\n2. Testing Database Agent...")
    db_queries = [
        "Show all meetings scheduled tomorrow",
        "Do we have any meetings today?",
        "List meetings next week",
        "Is there any review meeting?"
    ]
    
    for query in db_queries:
        response = requests.post(
            f"{BASE_URL}/api/query",
            json={"query": query}
        )
        success = response.status_code == 200 and response.json().get("success", False)
        test_results.append(("Database", query, success))
        print(f"  ✓ {query[:50]}...: {'PASS' if success else 'FAIL'}")
    
    # 3. Test Meeting Agent
    print("\n3. Testing Meeting Agent...")
    meeting_queries = [
        "Verify tomorrow's weather and schedule a team meeting if the weather is good",
        "Schedule a project review meeting tomorrow at 2 PM"
    ]
    
    for query in meeting_queries:
        response = requests.post(
            f"{BASE_URL}/api/query",
            json={"query": query}
        )
        success = response.status_code == 200
        test_results.append(("Meeting", query, success))
        print(f"  ✓ {query[:50]}...: {'PASS' if success else 'FAIL'}")
    
    # 4. Test Document Agent
    print("\n4. Testing Document Agent...")
    
    # First load example document
    print("  Loading example resume...")
    response = requests.post(f"{BASE_URL}/api/document/example")
    if response.status_code == 200:
        print("  ✓ Example resume loaded")
        
        # Test document queries
        doc_queries = [
            "What is John Doe's experience?",
            "What skills does he have?",
            "Where did he study?",
            "Who is the CEO of Google?"  # This should trigger web search
        ]
        
        for query in doc_queries:
            response = requests.post(
                f"{BASE_URL}/api/document/query",
                json={"query": query}
            )
            success = response.status_code == 200
            test_results.append(("Document", query, success))
            
            result = response.json()
            source = "Document" if result.get("from_document", False) else "Web Search"
            print(f"  ✓ {query[:40]}...: {'PASS' if success else 'FAIL'} ({source})")
    else:
        print("  ✗ Failed to load example resume")
        test_results.append(("Document", "Load example", False))
    
    # 5. Test Orchestrator Routing
    print("\n5. Testing Agent Orchestrator Routing...")
    mixed_queries = [
        ("Weather", "What's the temperature in Mumbai?"),
        ("Database", "What meetings do I have tomorrow?"),
        ("Meeting", "Check weather and schedule meeting"),
        ("Document", "What are the key skills in the resume?")
    ]
    
    for expected_agent, query in mixed_queries:
        response = requests.post(
            f"{BASE_URL}/api/query",
            json={"query": query}
        )
        
        if response.status_code == 200:
            result = response.json()
            actual_agent = result.get("agent", "Unknown")
            routed_correctly = expected_agent in actual_agent
            test_results.append(("Orchestrator", f"Route: {query[:30]}", routed_correctly))
            print(f"  ✓ {query[:40]}...: {'PASS' if routed_correctly else 'FAIL'} (Expected: {expected_agent}, Got: {actual_agent})")
        else:
            test_results.append(("Orchestrator", f"Route: {query[:30]}", False))
            print(f"  ✗ {query[:40]}...: FAIL (HTTP {response.status_code})")
    
    # 6. Test Complex Multi-Agent Scenario
    print("\n6. Testing Complex Scenario...")
    complex_query = "Check tomorrow's weather, see if I have meetings, and tell me about the skills in my resume"
    
    response = requests.post(
        f"{BASE_URL}/api/query",
        json={"query": complex_query}
    )
    
    if response.status_code == 200:
        result = response.json()
        complex_success = result.get("success", False)
        test_results.append(("Complex", "Multi-agent query", complex_success))
        print(f"  ✓ Complex query: {'PASS' if complex_success else 'FAIL'}")
        if complex_success:
            print(f"     Agent used: {result.get('agent')}")
            print(f"     Response preview: {result.get('response', '')[:100]}...")
    else:
        test_results.append(("Complex", "Multi-agent query", False))
        print(f"  ✗ Complex query: FAIL")
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    total_tests = len(test_results)
    passed_tests = sum(1 for _, _, success in test_results if success)
    
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    # Print detailed results
    print("\nDetailed Results:")
    print("-"*60)
    
    current_category = None
    for category, query, success in test_results:
        if category != current_category:
            print(f"\n{category}:")
            current_category = category
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"  {status}: {query}")
    
    return passed_tests == total_tests

def test_api_endpoints():
    """Test all API endpoints"""
    print("\n" + "="*60)
    print("API ENDPOINTS TEST")
    print("="*60)
    
    endpoints = [
        ("GET", "/", "Root endpoint"),
        ("GET", "/health", "Health check"),
        ("GET", "/api/agents", "List agents"),
        ("POST", "/api/query", "General query"),
        ("POST", "/api/weather", "Weather query"),
        ("GET", "/api/meetings", "Get meetings"),
        ("GET", "/api/document/status", "Document status"),
        ("POST", "/api/document/example", "Load example"),
    ]
    
    all_success = True
    for method, endpoint, description in endpoints:
        try:
            if method == "GET":
                response = requests.get(f"{BASE_URL}{endpoint}")
            elif method == "POST":
                if endpoint == "/api/query":
                    response = requests.post(f"{BASE_URL}{endpoint}", json={"query": "test"})
                elif endpoint == "/api/weather":
                    response = requests.post(f"{BASE_URL}{endpoint}", json={"query": "weather"})
                elif endpoint == "/api/document/example":
                    response = requests.post(f"{BASE_URL}{endpoint}")
                else:
                    continue
            
            success = response.status_code in [200, 201]
            status = "✓" if success else "✗"
            print(f"{status} {method} {endpoint}: {description} - HTTP {response.status_code}")
            
            if not success:
                all_success = False
                
        except Exception as e:
            print(f"✗ {method} {endpoint}: {description} - ERROR: {str(e)}")
            all_success = False
    
    return all_success

def main():
    """Run complete test suite"""
    print("Starting Complete System Tests...")
    print(f"Base URL: {BASE_URL}")
    print("="*60)
    
    # Wait for server to be ready
    print("Waiting for server to be ready...")
    for i in range(10):
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=2)
            if response.status_code == 200:
                print("Server is ready!")
                break
        except:
            pass
        time.sleep(1)
    else:
        print("Server not responding. Make sure it's running.")
        return False
    
    # Run tests
    print("\n" + "="*60)
    print("RUNNING COMPLETE TEST SUITE")
    print("="*60)
    
    try:
        # Test API endpoints
        api_success = test_api_endpoints()
        
        # Test all agents
        agents_success = test_all_agents_complete()
        
        # Final verdict
        print("\n" + "="*60)
        print("FINAL VERDICT")
        print("="*60)
        
        if api_success and agents_success:
            print("🎉 ALL TESTS PASSED! System is working correctly.")
            print("\nAll 4 Agents are functional:")
            print("1. ✅ Weather Agent - OpenWeatherMap integration")
            print("2. ✅ Database Agent - NL to SQL queries")
            print("3. ✅ Meeting Agent - Weather-aware scheduling")
            print("4. ✅ Document Agent - PDF/TXT processing with web search fallback")
            print("\nAgentic workflow is operational!")
            return True
        else:
            print("❌ SOME TESTS FAILED")
            if not api_success:
                print("  - API endpoints are not working correctly")
            if not agents_success:
                print("  - Some agents are not functioning properly")
            return False
            
    except Exception as e:
        print(f"❌ TEST SUITE ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)