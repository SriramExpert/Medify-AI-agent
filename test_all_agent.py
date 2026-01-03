import asyncio
import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    response = requests.get(f"{BASE_URL}/health")
    print(f"Health Check: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    return response.status_code == 200

def test_agents_list():
    """Test agents list endpoint"""
    response = requests.get(f"{BASE_URL}/api/agents")
    print(f"\nAgents List: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    return response.status_code == 200

def test_weather_agent():
    """Test weather agent"""
    test_queries = [
        "What is the weather in Chennai today?",
        "What was the weather in Bengaluru yesterday?",
        "What will the weather be like in London tomorrow?"
    ]
    
    print("\n" + "="*50)
    print("Testing Weather Agent")
    print("="*50)
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        response = requests.post(
            f"{BASE_URL}/api/weather",
            json={"query": query}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"Success: {result.get('success')}")
            print(f"Agent: {result.get('agent')}")
            print(f"Response: {result.get('response', '')[:200]}...")
        else:
            print(f"Error: {response.status_code}")
            print(response.text)

def test_database_agent():
    """Test database agent"""
    test_queries = [
        "Show all meetings scheduled tomorrow",
        "Do we have any meetings today?",
        "List meetings next week",
        "Is there any review meeting?"
    ]
    
    print("\n" + "="*50)
    print("Testing Database Agent")
    print("="*50)
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        response = requests.post(
            f"{BASE_URL}/api/query",
            json={"query": query}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"Success: {result.get('success')}")
            print(f"Agent: {result.get('agent')}")
            print(f"Count: {result.get('count', 0)} meetings")
            print(f"Response: {result.get('response', '')[:200]}...")
        else:
            print(f"Error: {response.status_code}")

def test_meeting_agent():
    """Test meeting agent"""
    test_queries = [
        "Verify tomorrow's weather and schedule a team meeting if the weather is good",
        "Schedule a project review meeting tomorrow at 2 PM",
        "Check weather and schedule outdoor meeting"
    ]
    
    print("\n" + "="*50)
    print("Testing Meeting Agent")
    print("="*50)
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        response = requests.post(
            f"{BASE_URL}/api/query",
            json={"query": query}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"Success: {result.get('success')}")
            print(f"Agent: {result.get('agent')}")
            print(f"Weather Checked: {result.get('weather_checked', False)}")
            print(f"Response: {result.get('response', '')[:200]}...")
        else:
            print(f"Error: {response.status_code}")

def test_orchestrator():
    """Test agent orchestrator"""
    print("\n" + "="*50)
    print("Testing Agent Orchestrator")
    print("="*50)
    
    response = requests.get(f"{BASE_URL}/api/test")
    if response.status_code == 200:
        results = response.json()
        print(f"Total Tests: {results['total_tests']}")
        print(f"Successful: {results['successful']}")
        
        for test in results['test_results']:
            print(f"\n{test['agent_type']}: {test['query']}")
            print(f"  Success: {test['success']}")
            print(f"  Agent Used: {test.get('agent_used', 'N/A')}")
    else:
        print(f"Error: {response.status_code}")

def main():
    """Run all tests"""
    print("Starting Agentic AI Chatbot Tests...")
    
    # Test basic endpoints
    if not test_health():
        print("Health check failed. Is the server running?")
        return
    
    test_agents_list()
    
    # Test individual agents
    test_weather_agent()
    test_database_agent()
    test_meeting_agent()
    
    # Test orchestrator
    test_orchestrator()
    
    print("\n" + "="*50)
    print("All tests completed!")
    print("="*50)

if __name__ == "__main__":
    main()