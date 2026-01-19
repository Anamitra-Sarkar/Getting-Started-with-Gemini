import os
import httpx
import asyncio

async def test_groq():
    # Read key from environment variable to avoid push protection issues
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("FAILURE: GEMINI_API_KEY environment variable not set")
        return False
        
    api_url = "https://api.groq.com/openai/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    body = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "user", "content": "Hello, are you working?"}
        ],
        "max_tokens": 100
    }
    
    print(f"Testing Groq API connection...")
    print(f"URL: {api_url}")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(api_url, json=body, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            print("SUCCESS!")
            print(f"Status Code: {response.status_code}")
            print(f"Response Text: {data['choices'][0]['message']['content']}")
            return True
    except Exception as e:
        print("FAILURE!")
        print(f"Error: {e}")
        if hasattr(e, 'response'):
            print(f"Response body: {e.response.text}")
        return False

if __name__ == "__main__":
    asyncio.run(test_groq())
