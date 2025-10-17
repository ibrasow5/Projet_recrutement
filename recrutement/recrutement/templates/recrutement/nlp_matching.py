# recrutement/nlp_matching.py
import re
import numpy as np
from pathlib import Path
from gensim.models import Word2Vec
from gensim.utils import simple_preprocess
from gensim.parsing.preprocessing import STOPWORDS
from django.conf import settings

# Chemin de sauvegarde du modèle (met à jour si besoin)
MODEL_DIR = Path(settings.BASE_DIR) / "recrutement" / "models_nlp"
MODEL_PATH = MODEL_DIR / "word2vec.model"

# Hyperparams (ajuste pour ton prototype)
VECTOR_SIZE = 100
WINDOW = 5
MIN_COUNT = 1
WORKERS = 2

# ---------------------------------------------------------
# Prétraitement
# ---------------------------------------------------------
def preprocess_text(text: str):
    """Nettoyage de base et tokenisation (fr)."""
    if not text:
        return []
    text = text.lower()
    # autorise les caractères français de base
    text = re.sub(r'[^a-z0-9\sàâéèêôùûç\-]', ' ', text)
    tokens = simple_preprocess(text, deacc=True)
    tokens = [t for t in tokens if t not in STOPWORDS]
    return tokens

# ---------------------------------------------------------
# Construction du corpus
# ---------------------------------------------------------
def build_corpus_from_offres_and_candidats(offres, candidats):
    """
    Prend des QuerySets/itérables d'offres et de candidats et retourne
    une liste de listes de tokens pour l'entraînement.
    """
    corpus = []
    for o in offres:
        text = " ".join(filter(None, [getattr(o, 'titre', ''), getattr(o, 'description', ''), getattr(o, 'competences', '')]))
        tokens = preprocess_text(text)
        if tokens:
            corpus.append(tokens)

    for c in candidats:
        # priorité : texte extrait du CV si disponible (champ cv_text), sinon nom complet + poste souhaité si existant
        candidate_texts = []
        if getattr(c, 'cv_text', None):
            candidate_texts.append(c.cv_text)
        else:
            if getattr(c, 'user', None):
                candidate_texts.append(c.user.get_full_name() or '')
        for txt in candidate_texts:
            tokens = preprocess_text(txt)
            if tokens:
                corpus.append(tokens)
    return corpus

# ---------------------------------------------------------
# Entraînement / Chargement du modèle
# ---------------------------------------------------------
def train_model(corpus, rebuild=False):
    """
    Entraîne et sauvegarde un Word2Vec sur le corpus (list of token lists).
    Si rebuild=False et modèle existant, charge le modèle existant.
    """
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    if MODEL_PATH.exists() and not rebuild:
        model = Word2Vec.load(str(MODEL_PATH))
        return model

    # entraînement
    model = Word2Vec(sentences=corpus, vector_size=VECTOR_SIZE, window=WINDOW, min_count=MIN_COUNT, workers=WORKERS)
    model.save(str(MODEL_PATH))
    return model

def load_model():
    if MODEL_PATH.exists():
        return Word2Vec.load(str(MODEL_PATH))
    return None

# ---------------------------------------------------------
# Vectorisation et similarité
# ---------------------------------------------------------
def vectorize_text(model, text: str):
    tokens = preprocess_text(text)
    vecs = [model.wv[t] for t in tokens if t in model.wv]
    if not vecs:
        return np.zeros(model.vector_size, dtype=float)
    return np.mean(vecs, axis=0)

def cosine_similarity_percent(a: np.ndarray, b: np.ndarray):
    if a is None or b is None or np.linalg.norm(a) == 0 or np.linalg.norm(b) == 0:
        return 0.0
    cos = float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))
    return round(max(0.0, cos) * 100.0, 2)

# ---------------------------------------------------------
# Fonction d'usage (appelée depuis views)
# ---------------------------------------------------------
def calcul_score_matching(offre, candidat, model=None):
    """
    Retourne un score [0,100] de similarité sémantique entre l'offre et le candidat.
    - Offre: titre + description + competences
    - Candidat: nom/prenom + (optionnel) cv_text si disponible
    """
    # Charger modèle si besoin
    if model is None:
        model = load_model()
        if model is None:
            # modèle indisponible -> renvoyer None/0.0 (on ne lance pas d'entraînement ici)
            return 0.0

    offre_text = " ".join(filter(None, [getattr(offre, 'titre', ''), getattr(offre, 'description', ''), getattr(offre, 'competences', '')]))
    candidat_text = ""
    if getattr(candidat, 'user', None):
        candidat_text = candidat.user.get_full_name() or ""
    if getattr(candidat, 'cv_text', None):
        candidat_text += " " + candidat.cv_text

    vec_offre = vectorize_text(model, offre_text)
    vec_cand = vectorize_text(model, candidat_text)
    return cosine_similarity_percent(vec_offre, vec_cand)
