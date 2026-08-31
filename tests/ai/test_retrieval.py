from backend.ai.retrieval import _load_knowledge_files, _score, find_relevant_knowledge


def test_load_knowledge_files_finds_all_documents():
    files = _load_knowledge_files()
    assert len(files) == 12
    assert "00_purpose_and_scope.md" in files
    assert "07_grovers_algorithm.md" in files
    assert "09_common_misconceptions.md" in files
    assert "10_ai_guidance_rules.md" in files
    assert "11_concept_ids.md" in files


def test_retrieval_scores_grover_question_to_grovers_algorithm():
    query = "How does Grover's algorithm amplify the target state amplitude with the diffusion operator?"
    result = find_relevant_knowledge(query, top_n=2)
    assert "07_grovers_algorithm.md" in result
    assert "Diffusion" in result or "amplitude" in result


def test_retrieval_scores_superposition_to_quantum_foundations():
    query = "What is quantum superposition and Hadamard gate transformation?"
    result = find_relevant_knowledge(query, top_n=2)
    assert "03_quantum_foundations.md" in result or "04_quantum_gates.md" in result


def test_score_filters_stopwords():
    text = "The quantum computer is in a superposition of states."
    score_stopwords_only = _score("the is a of in", text)
    assert score_stopwords_only == 0

    score_meaningful = _score("superposition quantum states", text)
    assert score_meaningful > 0
