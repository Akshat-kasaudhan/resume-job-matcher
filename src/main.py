from fastapi import FastAPI
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

app = FastAPI()

# Load the model ONCE, when the server starts
model = SentenceTransformer('all-MiniLM-L6-v2')

class MatchRequest(BaseModel):
    resume_text: str
    job_description_text: str

@app.get("/")
def read_root():
    return {"message": "Resume Matcher API is running"}

@app.post("/match")
def match_resume(request: MatchRequest):
    embeddings = model.encode([request.resume_text, request.job_description_text])
    similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]

    resume_words = set(request.resume_text.lower().split())
    job_words = set(request.job_description_text.lower().split())
    skill_gap = job_words - resume_words

    return {
        "match_score": round(float(similarity), 4),
        "skill_gap_count": len(skill_gap),
        "skill_gap_sample": list(skill_gap)[:10]
    }