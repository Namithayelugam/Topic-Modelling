import bcrypt
from auth.db import users_collection

# -------------------- Auth Logic (Email/Password) --------------------

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def signup_user(email: str, password: str):
    if users_collection.find_one({"email": email}):
        return "User already exists."

    hashed_pwd = hash_password(password)
    users_collection.insert_one({
        "email": email,
        "password": hashed_pwd,
        "history": []  # Initialize empty prediction history
    })
    return {"email": email}

def login_user(email, password):
    user = users_collection.find_one({"email": email})
    if user and verify_password(password, user["password"]):
        return {"email": email}
    return None

# -------------------- Prediction Storage --------------------

def save_user_prediction(email: str, question: str, answer: str, mlp_topic: str, refined_topic: str, user_prompt: str):
    users_collection.update_one(
        {"email": email},
        {"$push": {
            "history": {
                "question": question,
                "answer": answer,
                "user_prompt": user_prompt,
                "mlp_topic": mlp_topic,
                "refined_topic": refined_topic
            }
        }}
    )

def get_user_history(email: str):
    user = users_collection.find_one({"email": email})
    if user and "history" in user:
        return user["history"]
    return []

def clear_user_history(email: str):
    users_collection.update_one({"email": email}, {"$set": {"history": []}})


