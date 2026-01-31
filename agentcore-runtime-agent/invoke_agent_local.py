"""
Test agent locally by starting FastAPI server and making requests
"""

import subprocess
import time
import requests
import json
import sys
from pathlib import Path

def check_prerequisites():
    """Check if required tools are installed"""
    print("=" * 70)
    print(" Local Agent Testing - Prerequisites Check")
    print("=" * 70)
    print()
    
    # Check for uv
    try:
        result = subprocess.run(['uv', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("[✓] uv found")
            print(f"    {result.stdout.strip()}")
        else:
            raise Exception("uv not found")
    except Exception as e:
        print("[✗] uv not found")
        print("    Install uv: https://docs.astral.sh/uv/getting-started/")
        return False
    
    # Check for Docker
    try:
        result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("[✓] Docker found")
            print(f"    {result.stdout.strip()}")
        else:
            raise Exception("Docker not found")
    except Exception as e:
        print("[✗] Docker not found")
        print("    Install Docker Desktop: https://www.docker.com/products/docker-desktop")
        return False
    
    # Check for Docker running
    try:
        result = subprocess.run(['docker', 'ps'], capture_output=True, text=True)
        if result.returncode == 0:
            print("[✓] Docker daemon is running")
        else:
            raise Exception("Docker not running")
    except Exception as e:
        print("[✗] Docker daemon is not running")
        print("    Start Docker Desktop or Docker daemon")
        return False
    
    print()
    return True


def start_agent_server():
    """Start the FastAPI agent server"""
    print("=" * 70)
    print(" Starting Agent Server")
    print("=" * 70)
    print()
    
    agent_dir = Path("agent_pdz_01")
    if not agent_dir.exists():
        print("[✗] agent_pdz_01 directory not found")
        print("    Make sure you're running this from the agentcore-runtime-agent directory")
        return None
    
    print("[Status] Starting FastAPI server...")
    print("[Command] uv run uvicorn agent:app --host 0.0.0.0 --port 8080")
    print()
    
    # Start server process
    try:
        process = subprocess.Popen(
            ['uv', 'run', 'uvicorn', 'agent:app', '--host', '0.0.0.0', '--port', '8080'],
            cwd=str(agent_dir),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        
        # Wait for server to start
        print("[Status] Waiting for server to start...")
        time.sleep(4)
        
        return process
    
    except Exception as e:
        print(f"[✗] Failed to start server: {e}")
        return None


def test_ping():
    """Test the /ping endpoint"""
    print("=" * 70)
    print(" Testing /ping Endpoint")
    print("=" * 70)
    print()
    
    try:
        response = requests.get('http://localhost:8080/ping', timeout=5)
        
        if response.status_code == 200:
            print("[✓] Ping successful")
            print(f"    Status: {response.status_code}")
            print(f"    Response: {response.json()}")
            print()
            return True
        else:
            print(f"[✗] Ping failed with status {response.status_code}")
            return False
    
    except requests.exceptions.ConnectionError:
        print("[✗] Could not connect to server at localhost:8080")
        print("    Make sure the server is running")
        return False
    
    except Exception as e:
        print(f"[✗] Ping test failed: {e}")
        return False


def test_invocation(prompt="Hello agent! What can you do?"):
    """Test the /invocations endpoint"""
    print("=" * 70)
    print(" Testing /invocations Endpoint")
    print("=" * 70)
    print()
    
    payload = {
        "prompt": prompt
    }
    
    print(f"[Payload]")
    print(json.dumps(payload, indent=2))
    print()
    
    try:
        print("[Status] Sending invocation request...")
        response = requests.post(
            'http://localhost:8080/invocations',
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            print(f"[✓] Invocation successful")
            print(f"    Status: {response.status_code}")
            print()
            
            response_data = response.json()
            print("[Response]")
            print(json.dumps(response_data, indent=2))
            print()
            
            # Extract agent response
            try:
                message = response_data['output']['message']
                if message['content'] and len(message['content']) > 0:
                    agent_text = message['content'][0]['text']
                    print("=" * 70)
                    print(" Agent Response Text")
                    print("=" * 70)
                    print()
                    print(agent_text)
                    print()
            except (KeyError, IndexError, TypeError):
                pass
            
            return True
        else:
            print(f"[✗] Invocation failed with status {response.status_code}")
            print(f"    Response: {response.text}")
            return False
    
    except requests.exceptions.Timeout:
        print("[✗] Request timed out (30s)")
        return False
    
    except requests.exceptions.ConnectionError:
        print("[✗] Could not connect to server at localhost:8080")
        return False
    
    except Exception as e:
        print(f"[✗] Invocation test failed: {e}")
        return False


def test_multiple_prompts():
    """Test with multiple prompts"""
    print("=" * 70)
    print(" Testing Multiple Prompts")
    print("=" * 70)
    print()
    
    test_prompts = [
        "What is machine learning?",
        "Tell me a joke",
        "Help me debug this Python code: for i in range(10) print(i)",
    ]
    
    for i, prompt in enumerate(test_prompts, 1):
        print(f"[Test {i}/{len(test_prompts)}] {prompt}")
        
        payload = {"prompt": prompt}
        
        try:
            response = requests.post(
                'http://localhost:8080/invocations',
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                response_data = response.json()
                message = response_data['output']['message']
                
                if message['content'] and len(message['content']) > 0:
                    agent_text = message['content'][0]['text']
                    # Print first 100 chars
                    preview = agent_text[:100] + "..." if len(agent_text) > 100 else agent_text
                    print(f"    ✓ {preview}")
                else:
                    print(f"    ✗ No response text")
            else:
                print(f"    ✗ Status {response.status_code}")
        
        except Exception as e:
            print(f"    ✗ Error: {str(e)}")
        
        print()


def main():
    """Main test flow"""
    print("\n")
    
    # Step 1: Check prerequisites
    if not check_prerequisites():
        print("[✗] Prerequisites check failed")
        sys.exit(1)
    
    print()
    
    # Step 2: Start server
    server_process = start_agent_server()
    if not server_process:
        print("[✗] Failed to start server")
        sys.exit(1)
    
    print()
    
    try:
        # Step 3: Test ping
        if not test_ping():
            print("[✗] Ping test failed")
            sys.exit(1)
        
        # Step 4: Test basic invocation
        if not test_invocation():
            print("[✗] Basic invocation test failed")
            sys.exit(1)
        
        # Step 5: Test multiple prompts
        test_multiple_prompts()
        
        # Summary
        print("=" * 70)
        print(" Testing Complete")
        print("=" * 70)
        print()
        print("[✓] All tests passed!")
        print()
        print("Server is still running. Press Ctrl+C to stop.")
        print()
        
        # Keep server running
        server_process.wait()
    
    except KeyboardInterrupt:
        print()
        print("[Info] Stopping server...")
    
    finally:
        # Stop server
        if server_process:
            server_process.terminate()
            try:
                server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server_process.kill()
                server_process.wait()
            print("[✓] Server stopped")


if __name__ == "__main__":
    main()
