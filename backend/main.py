import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from pathlib import Path


base_path = Path(__file__).resolve().parent
env_path = base_path / ".env"
load_dotenv(dotenv_path=env_path)

api_key = os.getenv("GROQ_API_KEY")


print(f"------------------------------------------------")
if api_key:
    print(f"✅ SUCCESS: API Key found! Starts with: {api_key[:4]}...")
else:
    print(f"❌ FAILURE: API Key NOT found. Check your .env file!")
print(f"------------------------------------------------")

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=api_key
)

class UserRequest(BaseModel):
    message: str

SYSTEM_PROMPT = """
You are a smart, concise assistant for 'My Xerox Shop'.
Your goal is to calculate printing costs instantly. Do not explain your logic. Just give the price.

PRICING RULES (Strict):
- 1 to 15 pages: ₹3.00 per page
- 16 to 99 pages: ₹2.00 per page
- 100 or more pages: ₹1.50 per page
- Binding: ₹40 extra
- Lamination: ₹30 extra
-

If the user asks for a price, reply ONLY like this:
"Total: ₹[Amount] (Calculation: [Pages] x [Rate])"
"""


@app.post("/chat")
async def chat_endpoint(request: UserRequest):
    if not api_key:
        raise HTTPException(status_code=500, detail="API Key is missing on Server")
    
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": request.message}
            ]
        )
        return {"reply": response.choices[0].message.content}
    except Exception as e:
        print(f"❌ CRASH REPORT: {e}")
        raise HTTPException(status_code=500, detail=str(e))