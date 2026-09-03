'''BEFORE THIS WILL WORK, YOU NEED:
    1. A .env file in this same folder containing your own Groq API key:
           GROQ_API_KEY=gsk_your_key_here ;everyone on the team needs to create their own.
    2. The venv activated, with packages installed:
           python -m venv venv
           venv\\Scripts\\activate      (Windows)
           pip install groq python-dotenv
 
WHY "None" MIGHT APPEAR IF SOMETHING IS WRONG:
    - If .env is missing or the key is wrong, Groq will raise an
      authentication error (you'll see a traceback, not silently "None").
    - If you see literally "AI: None" printed, it usually means the model
      response had no text content — check that the model name below is
      still valid (Groq occasionally deprecates model names — see the
      Groq console for the current list) and that your question isn't
      empty.'''

import os
#Reads our .env file into memeory
from dotenv import load_dotenv
from groq import Groq
from retrieval import find_relevant_knowledge
# Reads .env file and makes content available
load_dotenv()
#using os.getenv we check if .env is missing , api key will be none
api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=api_key)
#Creates reusable connection 

SYSTEM_PROMPT = """You are the Q-BIT AI Guidance assistant for a quantum
computing learning platform. You help learners understand Grover's
Algorithm and its prerequisites (linear algebra, probability, qubits,
gates, circuits).

Rules:
- Base your answers on the CURRICULUM CONTEXT provided below.
- If a VERIFIED SIMULATION RESULT is provided, treat its numbers as fact.
  Never invent or alter counts, probabilities, or circuit details.
- If no simulation result is provided, do not claim any specific circuit
  outcome — speak conceptually instead.
- If the context doesn't fully cover the question, say so honestly rather
  than inventing facts outside the curriculum.
- Keep explanations clear and beginner-friendly, correcting common
  misconceptions gently when relevant.
"""


def _format_simulation_result(result: dict) -> str:
    circuit = result.get("circuit", {})
    return f"""Algorithm: {result.get('algorithm')}
Target state: {result.get('target_state')}
Shots: {result.get('shots')}
Most likely measured state: {result.get('most_likely_state')}
Target state probability: {result.get('target_probability'):.2%}
Full probability distribution: {result.get('probabilities')}
Raw counts: {result.get('counts')}
Circuit depth: {circuit.get('depth')}
Circuit qubits: {circuit.get('num_qubits')}
Gate counts: {circuit.get('gate_counts')}"""


def ask_question(question: str, simulation_result: dict = None) -> str:
    # Step 1: retrieve relevant curriculum context for THIS question
    #Searches relevant keywords from knowledge folder 
    '''answer "grounded" in our actual curriculum instead of just whatever the model happens to know generally about quantum computing.'''
    context = find_relevant_knowledge(question, top_n=2)

    evidence_block = ""
    if simulation_result:
        evidence_block = (
            "\n\nVERIFIED SIMULATION RESULT (treat as ground truth, "
            "never contradict or invent different numbers):\n"
            + _format_simulation_result(simulation_result)
        )

    # Step 2: build the full prompt with that context included
    '''We put together the retrieved context and the learner's question together into one message.
    The model looks at both the pieces and is instructed to answer according to the context'''
    user_prompt = f"""CURRICULUM CONTEXT:
{context}
{evidence_block}

LEARNER QUESTION:
{question}

Answer the learner's question using the curriculum context (and the
verified simulation result, if provided) above."""

    # Step 3: send to the AI model
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
    )
    '''The API returns a complex object with lots of metadata (tokencounts, timing, etc).
    We only care about the actual text reply,'''
    return response.choices[0].message.content


if __name__ == "__main__":
    fake_result = {
        "algorithm": "grover",
        "target_state": "101",
        "shots": 1024,
        "counts": {"101": 897, "010": 42, "111": 30, "000": 55},
        "probabilities": {"101": 0.876, "010": 0.041, "111": 0.029, "000": 0.054},
        "target_probability": 0.876,
        "most_likely_state": "101",
        "circuit": {
            "num_qubits": 3,
            "num_clbits": 3,
            "depth": 12,
            "gate_counts": {"h": 3, "cx": 4, "measure": 3},
            "diagram": "(circuit diagram text)",
        },
    }

    print("Q-BIT AI Guidance — ask any question (Ctrl+C to quit)\n")
    while True:
        try:
            question = input("Your question: ")
            if not question.strip():
                #Skips the empty input
                continue
            answer = ask_question(question, simulation_result=fake_result)
            print(f"\nAI: {answer}\n")
        except KeyboardInterrupt:
            #For a clean exit
            print("\nGoodbye!")
            break
