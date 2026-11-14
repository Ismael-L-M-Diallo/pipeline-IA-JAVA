import os
import joblib
import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = FastAPI(title="Classification Service (Non-Supervisé)")
MODEL_PATH = "models/model.joblib"

STOP_WORDS_FR_EN = [
    "the", "and", "to", "of", "in", "for", "on", "is", "your", "we", "our", "all", "be", "can", "from",
    "le", "la", "les", "des", "de", "du", "un", "une", "et", "en", "au", "aux", "par", "pour", "avec", "sur"
]


class FitRequest(BaseModel):
    texts: list[str]
    n_clusters: int = 2

class PredictRequest(BaseModel):
    text: str
    top_k: int = 3


def load_bundle():
    if not os.path.exists(MODEL_PATH):
        raise HTTPException(status_code=400, detail="Modèle non entraîné. Appelez /fit d'abord.")
    return joblib.load(MODEL_PATH)


@app.post("/fit")
def fit(data: FitRequest):
    if len(data.texts) < data.n_clusters:
        raise HTTPException(status_code=400, detail="Il faut au moins autant de textes que de clusters.")

    vectorizer = TfidfVectorizer(stop_words=STOP_WORDS_FR_EN)
    X = vectorizer.fit_transform(data.texts)

    kmeans = KMeans(n_clusters=data.n_clusters, random_state=42, n_init="auto")
    clusters = kmeans.fit_predict(X)



    mots = vectorizer.get_feature_names_out()
    centres = kmeans.cluster_centers_.argsort()[:, ::-1]
    noms_clusters = {
        i: f"Cluster_{i} ({', '.join(mots[ind] for ind in centres[i, :3])})"
        for i in range(data.n_clusters)
    }

    os.makedirs("models", exist_ok=True)
    joblib.dump(
        {
            "vectorizer": vectorizer,
            "kmeans": kmeans,
            "noms": noms_clusters,
            "texts": data.texts,
            "clusters": clusters.tolist(),
        },
        MODEL_PATH,
    )

    return {"status": "ok", "documents_appris": len(data.texts), "clusters_decouverts": noms_clusters}


@app.post("/predict")
def predict(data: PredictRequest):
    bundle = load_bundle()
    vecteur = bundle["vectorizer"].transform([data.text])

    cluster_id = int(bundle["kmeans"].predict(vecteur)[0])
    label = bundle["noms"][cluster_id]

   
    distances = bundle["kmeans"].transform(vecteur)[0]
    proximites = 1 / (distances + 1e-6)
    probas = proximites / np.sum(proximites)

    scores = {bundle["noms"][i]: round(float(p), 4) for i, p in enumerate(probas)}

    return {"label": label, "scores": scores}


@app.post("/recommend")
def recommend(data: PredictRequest):
    bundle = load_bundle()
    vectorizer = bundle["vectorizer"]

    matrice_docs = vectorizer.transform(bundle["texts"])
    vecteur_requete = vectorizer.transform([data.text])
    similarites = cosine_similarity(vecteur_requete, matrice_docs)[0]

    meilleurs_index = similarites.argsort()[::-1][: data.top_k]
    resultats = [
        {
            "text": bundle["texts"][i],
            "label": bundle["noms"][bundle["clusters"][i]],
            "score": round(float(similarites[i]), 4),
        }
        for i in meilleurs_index
    ]

    return {"recommendations": resultats}