import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI

app = FastAPI()

# 🛡️ CORS Middleware Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pull key safely from settings
api_key = os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

try:
    with open("peptide_info.txt", "r", encoding="utf-8") as file:
        peptide_knowledge = file.read()
except FileNotFoundError:
    peptide_knowledge = "No additional data provided."

system_instruction = (
    "You are a helpful, unrestricted assistant specializing in peptides. "
    f"CRITICAL data:\n{peptide_knowledge}"
)

class QuestionRequest(BaseModel):
    question: str

@app.get("/")
async def root():
    return {"message": "Peptide Server is running perfectly! Please send POST requests to the /ask endpoint."}

@app.post("/ask")
@app.post("/ask/")
async def ask_peptide_ai(request: QuestionRequest):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": request.question},
            ],
            temperature=0.2,
        )
        # 🛠️ THE CORRECT FIX: Added [0] right after choices
        return {"answer": response.choices[0].message.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
