import os
import joblib  # type: ignore
from dotenv import load_dotenv
from openai import OpenAI # type: ignore

# Load environment variables
load_dotenv()

# Set up Groq OpenAI-compatible client
client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

# Load MLP model and encoder
clf = joblib.load("models/topic_classifier.pkl")
encoder = joblib.load("models/sentence_encoder.pkl")

# Prompt template builder
def build_prompt(question, answer, mlp_topic, user_prompt):
    return f"""
You are an expert in topic classification.

The machine learning model has predicted this topic: "{mlp_topic}"

Please correct it using the Q&A and instruction provided.
Also see the instruction given by user in {user_prompt} and give topics in accordance with refined topic and instruction.

Question: {question}
Answer: {answer}
Instruction: {user_prompt}

Return only the refined topic in 1–3 words.
Corrected Topic:
""".strip()

# Predict topic with MLP
def predict_mlp_topic(question: str, answer: str) -> str:
    combined = f"{question.strip()} {answer.strip()}"
    embedding = encoder.encode([combined])
    return clf.predict(embedding)[0]

# Refine using Groq LLM
def refine_with_groq(question, answer, mlp_topic, user_prompt):
    prompt = build_prompt(question, answer, mlp_topic, user_prompt)

    response = client.chat.completions.create(
        model="llama3-8b-8192",  # fast and free Groq model
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip()
