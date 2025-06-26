# predict_topic.py
from langchain_bot import predict_mlp_topic, refine_with_groq

if __name__ == "__main__":
    question = input("Enter your question: ")
    answer = input("Enter your answer: ")
    prompt = input("Enter refinement instruction (default: 'Refine the topic') ") or "Refine the topic"

    mlp_topic = predict_mlp_topic(question, answer)
    refined_topic = refine_with_groq(question, answer, mlp_topic, prompt)

    print(f"Topic Predicted: {refined_topic}")
