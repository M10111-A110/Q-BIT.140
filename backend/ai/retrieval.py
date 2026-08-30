import os
import re
KNOWLEDGE_DIR = os.path.join(os.path.dirname(__file__), "knowledge")
def _load_knowledge_files():
    files = {}
    for filename in sorted(os.listdir(KNOWLEDGE_DIR)):
        if filename.endswith(".md"):
            path = os.path.join(KNOWLEDGE_DIR, filename)
            with open(path, "r", encoding="utf-8") as f:
                files[filename] = f.read()
    return files

def _score(question: str, text: str) -> int:
    question_words = set(re.findall(r"[a-z]+", question.lower()))
    text_lower = text.lower()

    stopwords = {
        "the", "is", "a", "an", "of", "to", "in", "and", "what", "why",
        "how", "does", "do", "did", "it", "on", "for", "with", "was",
        "were", "are", "this", "that", "my", "i",
    }
    question_words -= stopwords

    score = 0
    for word in question_words:
        if len(word) < 3:
            continue
        score += text_lower.count(word)
    return score


def find_relevant_knowledge(question: str, top_n: int = 2) -> str:
    files = _load_knowledge_files()

    scored = []
    for filename, text in files.items():
        score = _score(question, text)
        scored.append((score, filename, text))

    scored.sort(key=lambda x: x[0], reverse=True)

    top_matches = scored[:top_n]

    combined = ""
    for score, filename, text in top_matches:
        combined += f"\n\n--- From {filename} ---\n{text}"

    return combined.strip()

if __name__ == "__main__":
    test_question = "why did grover not give 100 percent probability"
    result = find_relevant_knowledge(test_question)
    print(f"Question: {test_question}\n")
    print("Matched knowledge:")
    print(result[:500] + "...\n[truncated for preview]")
