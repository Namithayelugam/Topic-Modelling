import pandas as pd # type: ignore
import joblib # type: ignore
from sklearn.ensemble import RandomForestClassifier # type: ignore
from sentence_transformers import SentenceTransformer # type: ignore
from langchain_huggingface import HuggingFaceEmbeddings # type: ignore
from langchain_community.vectorstores import Chroma # type: ignore
from langchain.docstore.document import Document # type: ignore
import os
from sklearn.neural_network import MLPClassifier # type: ignore

# Load dataset
df = pd.read_csv("/Users/dr/Downloads/third_stage_filtered_data.csv")
texts = df["Merged_Text"].fillna("").tolist()
labels = df["third_filter"].tolist()

# Encode text
encoder = SentenceTransformer("all-MiniLM-L6-v2")
X = encoder.encode(texts, show_progress_bar=True)

# Train classifier
clf = MLPClassifier(hidden_layer_sizes=(128, 64), max_iter=500, random_state=42)
clf.fit(X, labels)

# Save model & encoder
#os.makedirs("models", exist_ok=True)
joblib.dump(clf, "models/topic_classifier.pkl")
joblib.dump(encoder, "models/sentence_encoder")


