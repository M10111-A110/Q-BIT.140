import os
from dotenv import load_dotenv
from groq import Groq
from retrieval import find_relevant_knowledge

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=api_key)


SYSTEM_PROMPT = """You are the Q-BIT AI Guidance assistant for a quantum
computing learning platform. You help learners understand Grover's
Algorithm and its prerequisites (linear algebra, probability, qubits,
gates, circuits).

Rules:
- Base your answers on the CURRICULUM CONTEXT provided below.
- If the context doesn't fully cover the question, say so honestly rather
  than inventing facts outside the curriculum.
- Never claim a simulation result unless one is explicitly given to you.
- Keep explanations clear and beginner-friendly, correcting common
  misconceptions gently when relevant.
"""
def ask_question(question: str) -> str:
    # Step 1: retrieve relevant curriculum context for THIS question
    context = find_relevant_knowledge(question, top_n=2)

    # Step 2: build the full prompt with that context included
    user_prompt = f"""CURRICULUM CONTEXT:
{context}

LEARNER QUESTION:
{question}

Answer the learner's question using the curriculum context above."""

    # Step 3: send to the AI model
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
    )

    return response.choices[0].message.content


if __name__ == "__main__":
    print("Q-BIT AI Guidance — ask any question (Ctrl+C to quit)\n")
    while True:
        try:
            question = input("Your question: ")
            if not question.strip():
                continue
            answer = ask_question(question)
            print(f"\nAI: {answer}\n")
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
