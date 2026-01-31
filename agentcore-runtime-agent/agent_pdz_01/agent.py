"""
Production-ready FastAPI agent for Amazon Bedrock AgentCore Runtime.
Implements required /invocations and /ping endpoints.
"""

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime
import json
from strands import Agent

# ============================================================================
# Initialization
# ============================================================================

print("\n" + "=" * 70)
print(" Agent PDZ-01 - Initializing")
print("=" * 70)

app = FastAPI(title="Agent PDZ-01", version="2.0.0")

# Initialize Strands agent
print("[Step 1/2] Creating Strands agent...")
try:
    strands_agent = Agent()
    AGENT_READY = True
    print("   ✓ Strands agent initialized successfully")
except Exception as e:
    strands_agent = None
    AGENT_READY = False
    print(f"   ⚠ Strands agent failed: {str(e)}")
    print("   ℹ Agent will operate in mock mode")

print("[Step 2/2] FastAPI configured")
print("=" * 70 + "\n")


# ============================================================================
# Request/Response Models
# ============================================================================

class InvocationResponse(BaseModel):
    """Response model"""
    output: Dict[str, Any]


# ============================================================================
# Middleware for request logging
# ============================================================================

@app.middleware("http")
async def log_all_requests(request: Request, call_next):
    """Log all incoming requests with full details"""
    print("\n" + "=" * 70)
    print(f"[REQUEST] {request.method} {request.url.path}")
    print(f"[TIME] {datetime.utcnow().isoformat()}Z")
    
    if request.method == "POST":
        try:
            body = await request.body()
            print(f"[BODY] {body.decode('utf-8')}")
        except:
            pass
    
    print("=" * 70)
    
    response = await call_next(request)
    return response


# ============================================================================
# Main Endpoints
# ============================================================================

@app.post("/invocations", response_model=InvocationResponse)
async def invoke_agent(request: Request):
    """
    REQUIRED: Main invocation endpoint for agent interactions.
    AWS AgentCore Runtime sends: {"prompt": "..."}
    """
    print("\n" + "=" * 70)
    print(f" [INVOCATION] {datetime.utcnow().isoformat()}Z")
    print("=" * 70)
    
    try:
        # Parse JSON body
        raw_body = await request.body()
        request_data = json.loads(raw_body)
        
        print(f"[REQUEST DATA] {json.dumps(request_data, indent=2)}")
        
        # Extract prompt from AWS format: {"prompt": "..."}
        user_message = request_data.get("prompt", "")
        
        if not user_message:
            print(f"[ERROR] No prompt found")
            raise HTTPException(
                status_code=400,
                detail="No prompt provided"
            )
        
        print(f"[PROMPT] {user_message}")
        
        # Process with Strands agent
        response_text = ""
        
        if AGENT_READY and strands_agent:
            print("[PROCESSING] Invoking Strands agent...")
            print(f"[STRANDS INPUT] {user_message}")
            try:
                result = strands_agent(user_message)
                print(f"[STRANDS RESULT TYPE] {type(result)}")
                
                # result.message is a DICT, not an object!
                if hasattr(result, 'message'):
                    message = result.message
                    print(f"[STRANDS MESSAGE TYPE] {type(message)}")
                    print(f"[STRANDS MESSAGE] {message}")
                    
                    # message is a dict with 'role' and 'content' keys
                    if isinstance(message, dict) and 'content' in message:
                        content = message['content']
                        print(f"[STRANDS CONTENT TYPE] {type(content)}")
                        print(f"[STRANDS CONTENT LENGTH] {len(content) if content else 0}")
                        
                        # content is a list of dicts
                        if content and len(content) > 0:
                            first_content = content[0]
                            print(f"[STRANDS CONTENT[0] TYPE] {type(first_content)}")
                            print(f"[STRANDS CONTENT[0]] {first_content}")
                            
                            # Extract text from the dict
                            if isinstance(first_content, dict) and 'text' in first_content:
                                response_text = first_content['text']
                                print(f"[STRANDS TEXT EXTRACTED] {response_text[:100]}...")
                            else:
                                print(f"[WARNING] Content[0] has no 'text' key")
                                response_text = str(first_content)
                    else:
                        print(f"[WARNING] Message structure unexpected")
                        response_text = str(message)
                else:
                    print(f"[WARNING] Result has no 'message' attribute")
                    response_text = str(result)
                
                if not response_text:
                    print("[WARNING] Response text is empty, using default")
                    response_text = "Agent processed your request successfully."
                
                print("[SUCCESS] Agent completed processing")
                
            except Exception as e:
                print(f"[STRANDS ERROR] {str(e)}")
                import traceback
                print(f"[STRANDS TRACEBACK] {traceback.format_exc()}")
                response_text = f"Error from Strands agent: {str(e)}"
        else:
            print("[MOCK] Strands agent not available")
            response_text = f"Mock response: {user_message}"
        
        # Build response
        output = {
            "message": {
                "role": "assistant",
                "content": [{"text": response_text}]
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        print(f"[RESPONSE TEXT] {response_text}")
        print(f"[OUTPUT OBJECT] {json.dumps(output, indent=2)}")
        print("[RESPONSE] Returning output")
        print("=" * 70 + "\n")
        
        return InvocationResponse(output=output)
    
    except HTTPException:
        print("=" * 70 + "\n")
        raise
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        print(f"[ERROR] {error_msg}")
        print("=" * 70 + "\n")
        raise HTTPException(status_code=500, detail=error_msg)


@app.get("/ping")
async def ping():
    """
    REQUIRED: Health check endpoint.
    """
    print(f"[PING] Healthy - Agent ready: {AGENT_READY}")
    return {"status": "healthy"}


@app.get("/")
async def root():
    """Info endpoint"""
    return {
        "agent": "PDZ-01",
        "version": "2.0.0",
        "status": "running",
        "agent_ready": AGENT_READY
    }


# ============================================================================
# Server Entry Point
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "=" * 70)
    print(" Starting Agent PDZ-01")
    print("=" * 70)
    print(" Host: 0.0.0.0")
    print(" Port: 8080")
    print("=" * 70 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8080)
