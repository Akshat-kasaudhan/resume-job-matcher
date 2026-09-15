from fastapi import FastAPI
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import string

app = FastAPI()
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

model = SentenceTransformer('all-MiniLM-L6-v2')

STOP_WORDS = {
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "as", "is", "are", "was", "were", "be",
    "been", "being", "this", "that", "these", "those", "it", "its", "we",
    "you", "your", "our", "their", "his", "her", "he", "she", "they",
    "will", "would", "can", "could", "should", "may", "might", "must",
    "have", "has", "had", "not", "no", "do", "does", "did", "if", "than"
}

def clean_text(text):
    text = text.lower()
    text = text.translate(str.maketrans(string.punctuation, ' ' * len(string.punctuation)))
    words = text.split()
    words = [w for w in words if w not in STOP_WORDS]
    return set(words)

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

    resume_words = clean_text(request.resume_text)
    job_words = clean_text(request.job_description_text)
    skill_gap = job_words - resume_words

    return {
        "match_score": round(float(similarity), 4),
        "skill_gap_count": len(skill_gap),
        "skill_gap_sample": list(skill_gap)[:10]
    }