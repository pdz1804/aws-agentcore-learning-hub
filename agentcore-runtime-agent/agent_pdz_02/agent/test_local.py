"""Test Agent locally - Focus on MCP tool invocation"""
import requests
import json


def test_agent():
    base_url = "http://localhost:8080"
    
    print("=" * 70)
    print(" Testing Agent with MCP Tools (Local)")
    print("=" * 70)
    print(f" URL: {base_url}\n")
    
    # Test 1: Health check
    print("[Test 1/5] GET /ping - Health check")
    response = requests.get(f"{base_url}/ping")
    print(f"  Status: {response.status_code}")
    data = response.json()
    print(f"  Agent Ready: {data.get('agent_ready')}")
    print(f"  Tools Count: {data.get('tools_count')}\n")
    
    # Test 2: Get MCP tools info
    print("[Test 2/5] GET / - Get MCP tools")
    response = requests.get(base_url)
    print(f"  Status: {response.status_code}")
    data = response.json()
    if "mcp_tools" in data and isinstance(data["mcp_tools"], list):
        if len(data["mcp_tools"]) > 0:
            print(f"  Available MCP Tools:")
            for tool in data["mcp_tools"]:
                print(f"    - {tool['name']}: {tool['description']}")
        else:
            print(f"  Note: MCP tools are auto-discovered by Strands at runtime")
    print()
    
    # Test 3: Calculate statistics tool
    print("[Test 3/5] POST /invocations - Calculate Statistics Tool")
    payload = {"prompt": "Calculate statistics for these numbers: 10, 20, 30, 40, 50"}
    response = requests.post(
        f"{base_url}/invocations",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    print(f"  Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        if "output" in data:
            text = data["output"]["message"]["content"][0]["text"]
            # Handle unicode by encoding/decoding
            text_safe = text.encode('ascii', 'ignore').decode('ascii')
            print(f"  Response: {text_safe[:300]}...\n")
        else:
            print(f"  Error: {json.dumps(data, indent=2)}\n")
    else:
        print(f"  Error {response.status_code}: {response.text}\n")
    
    # Test 4: Compound interest tool
    print("[Test 4/5] POST /invocations - Compound Interest Tool")
    payload = {"prompt": "Calculate compound interest: $5000 invested at 6% for 10 years, compounded monthly"}
    response = requests.post(
        f"{base_url}/invocations",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    print(f"  Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        if "output" in data:
            text = data["output"]["message"]["content"][0]["text"]
            text_safe = text.encode('ascii', 'ignore').decode('ascii')
            print(f"  Response: {text_safe[:300]}...\n")
        else:
            print(f"  Error: {json.dumps(data, indent=2)}\n")
    else:
        print(f"  Error {response.status_code}: {response.text}\n")
    
    # Test 5: Text analyzer tool
    print("[Test 5/5] POST /invocations - Text Analyzer Tool")
    payload = {"prompt": "Analyze this text: 'Hello world. This is a test. Testing AI capabilities.'"}
    response = requests.post(
        f"{base_url}/invocations",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    print(f"  Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        if "output" in data:
            text = data["output"]["message"]["content"][0]["text"]
            text_safe = text.encode('ascii', 'ignore').decode('ascii')
            print(f"  Response: {text_safe[:300]}...\n")
        else:
            print(f"  Error: {json.dumps(data, indent=2)}\n")
    else:
        print(f"  Error {response.status_code}: {response.text}\n")
    
    print("=" * 70)
    print(" All MCP tool tests completed!")
    print("=" * 70)


if __name__ == "__main__":
    test_agent()
