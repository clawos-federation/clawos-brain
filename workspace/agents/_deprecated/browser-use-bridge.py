import asyncio
import sys
import json
import os
from browser_use import Agent
from langchain_google_genai import ChatGoogleGenerativeAI

# OpenClaw Browser-use Bridge (Orchestration 5.0 - Gemini Version)
# Uses the GEMINI_API_KEY from your environment

async def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No task provided"}))
        return

    task = sys.argv[1]
    
    # Extract API Key from environment or hardcoded fallback from config
    api_key = os.getenv("GEMINI_API_KEY", "AIzaSyCTG4Oho8mttrbEbawA0HN-MVUthl2-mUU")
    
    # Initialize Gemini as the browser's intuition engine
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        google_api_key=api_key,
        timeout=60000
    )
    
    agent = Agent(
        task=task,
        llm=llm,
    )
    
    try:
        # Note: This requires playwright browsers to be installed
        # run: playwright install chromium
        result = await agent.run()
        print(json.dumps({
            "status": "success",
            "final_answer": str(result),
        }))
    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}))

if __name__ == "__main__":
    asyncio.run(main())
