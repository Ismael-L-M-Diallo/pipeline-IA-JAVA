import joblib
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer

textes = [
    "Fuite détectée sur le circuit primaire, niveau 4.5 mSv/h",
    "Alerte radiation dans la zone B2, évacuation requise",
    "Maintenance préventive de la pompe hydraulique effectuée",
    "Inspection annuelle des vannes conforme aux normes",
]


vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(textes)

kmeans = KMeans(n_clusters=2, random_state=42, n_init="auto")
kmeans.fit(X)


mots = vectorizer.get_feature_names_out()
centres = kmeans.cluster_centers_.argsort()[:, ::-1]
noms_clusters = {
    i: f"Cluster_{i} ({', '.join(mots[ind] for ind in centres[i, :3])})"
    for i in range(2)
}


joblib.dump({"vectorizer": vectorizer, "kmeans": kmeans, "noms": noms_clusters}, "model.joblib")

nouveau_doc = vectorizer.transform(["Augmentation anormale des radiations près du réacteur"])
cluster_id = kmeans.predict(nouveau_doc)[0]

print("Groupe attribué :", noms_clusters[cluster_id])