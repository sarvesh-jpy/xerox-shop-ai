import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from pathlib import Path

# --- 1. INTELLIGENT KEY FINDER ---
# This looks for .env in the folder where main.py is, 
# preventing "file not found" errors.
base_path = Path(__file__).resolve().parent
env_path = base_path / ".env"
load_dotenv(dotenv_path=env_path)

api_key = os.getenv("GROQ_API_KEY")

# --- 2. DEBUG PRINT (CHECK THIS IN TERMINAL!) ---
print(f"------------------------------------------------")
if api_key:
    print(f"✅ SUCCESS: API Key found! Starts with: {api_key[:4]}...")
else:
    print(f"❌ FAILURE: API Key NOT found. Check your .env file!")
print(f"------------------------------------------------")

app = FastAPI()

# --- 3. THE SECURITY FIX (CORS) ---
# This fixes the "OPTIONS 400 Bad Request" error
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all connections
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

# backend/main.py

# ... (Previous imports and setup) ...

SYSTEM_PROMPT = """
You are the smart assistant for 'My Xerox Shop'. 
Your goal is to calculate prices accurately for customers based on these strict rules.

--- PRICE LIST ---

1. LAMINATION SERVICES:
   - ID Card Size (includes Color Xerox + Lamination): ₹45 per card.
   - A4 Size Lamination: ₹50 per sheet.
   - A3 Size Lamination: ₹80 per sheet.

2. PRINTING (BLACK & WHITE):

   A. SINGLE SIDE (Separate Pages):
      - 1 to 40 pages: ₹2.00 per page.
      - More than 100 pages: ₹ 1.8 per page.

   B. DOUBLE SIDE (Front & Back):
      - 20 to 100 pages: ₹1.70 per side (So 1 sheet with 2 sides costs ₹3.40).
      - More than 100 pages: ₹1.50 per side.
      - (If less than 20 pages double-sided, assume standard rate: ₹3 per side).

--- INSTRUCTIONS FOR AI ---
1. STEP 1: Identify what the user wants (Lamination, Single Side, or Double Side).
2. STEP 2: Check the quantity (number of pages).
3. STEP 3: Calculate the total cost using the rates above.
4. STEP 4: Show the calculation briefly.

Example 1: "Price for 50 single side pages" -> 50 * 1.70 = ₹85.
Example 2: "Price for ID card lamination" -> ₹45.
"""

# ... (Rest of your code) ...

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