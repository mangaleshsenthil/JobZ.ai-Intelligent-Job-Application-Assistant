from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

_model = None

def get_model():
    global _model
    if _model is None:
        try:
            _model = SentenceTransformer("all-MiniLM-L6-v2")
        except Exception as e:
            print(f"Error loading embedding model: {e}")
            return None
    return _model

def compute_similarity(text1, text2):
    model = get_model()
    if not model:
        return 0.0
    try:
        if not text1 or not text2:
            return 0.0
        emb1 = model.encode([text1])
        emb2 = model.encode([text2])
        score = cosine_similarity(emb1, emb2)[0][0]
        return float(score)
    except Exception:
        return 0.0
