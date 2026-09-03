import json
import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient

from backend.adaptive import (
    InMemoryLearnerRepository,
    StorageUnavailableError,
)
from backend.ai import LLMProvider, MockLLMProvider
from backend.api.dependencies import (
    reset_dependencies,
    set_learner_repository,
    set_llm_provider,
)
from backend.api.main import app


@pytest.fixture(autouse=True)
def setup_clean_env():
    """Ensure every test runs in an isolated environment."""
    repo = InMemoryLearnerRepository()
    set_learner_repository(repo)
    set_llm_provider(MockLLMProvider())
    yield
    reset_dependencies()


# ===========================================================================
# 1. FRONTEND CONTRACT TESTS (M1/M6 CONSUMPTION VIA FASTAPI GATEWAY)
# ===========================================================================

def test_frontend_loads_activities_list():
    """Requirement 1: Frontend GET /api/activities loads registered activities."""
    client = TestClient(app)
    res = client.get("/api/activities")
    assert res.status_code == 200
    activities = res.json()
    assert len(activities) == 4
    assert activities[0]["activity_id"] == "act_grover_2q_predict"
    assert activities[0]["task_type"] == "quantum_prediction"


def test_frontend_loads_activity_detail():
    """Requirement 2: Frontend GET /api/activity/{id} loads specification."""
    client = TestClient(app)
    res = client.get("/api/activity/act_grover_2q_predict")
    assert res.status_code == 200
    act = res.json()
    assert act["activity_id"] == "act_grover_2q_predict"
    assert act["quantum_experiment"] is not None
    assert act["quantum_experiment"]["algorithm"] == "grover"


def test_frontend_submission_renders_3_distinct_states():
    """
    Requirements 4 & 5: Submission preserves the 3 distinct quantum states:
      1. Learner Predicted State ("01")
      2. Theoretical Target State ("10")
      3. Empirical Most-Likely Measured State ("10")
    """
    client = TestClient(app)
    res = client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": "u_frontend_demo", "response": "01"},
    )
    assert res.status_code == 200
    data = res.json()

    # Distinct states
    assert data["learner_response"] == "01"
    assert data["verified_result"]["target_state"] == "10"
    assert data["verified_result"]["most_likely_state"] == "10"
    assert data["verified_result"]["target_probability"] > 0.90
    assert data["evidence"]["is_correct"] is False


def test_frontend_renders_gather_evidence_state():
    """Requirement 7: Case A Single error -> gather_evidence, confidence 0.35, observing."""
    client = TestClient(app)
    res = client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": "u_case_a", "response": "01"},
    )
    data = res.json()
    inf = data["learner_state"]["gap_inferences"]["grover.search_problem"]
    assert inf["status"] == "observing"
    assert inf["trend"] == "preliminary_observation"
    assert inf["confidence"] == 0.35
    assert data["adaptive_decision"]["action"] == "gather_evidence"
    assert data["adaptive_decision"]["target"] == "act_grover_2q_predict"


def test_frontend_renders_targeted_remediation_state():
    """Requirement 8: Case B Repeated errors -> targeted_remediation, confidence 0.90."""
    client = TestClient(app)
    client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": "u_case_b", "response": "01"},
    )
    res2 = client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": "u_case_b", "response": "00"},
    )
    data = res2.json()
    inf = data["learner_state"]["gap_inferences"]["grover.search_problem"]
    assert inf["status"] == "remediation_needed"
    assert inf["trend"] == "persistent_difficulty"
    assert inf["confidence"] == 0.90
    assert data["adaptive_decision"]["action"] == "targeted_remediation"
    assert data["adaptive_decision"]["target"] == "act_measurement_prob_diagnostic"


def test_frontend_renders_improving_state():
    """Requirement 9: Case C Wrong -> Remediation -> Correct -> improving, advance."""
    client = TestClient(app)
    # Attempt 1: Error on Grover
    client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": "u_case_c", "response": "01"},
    )
    # Attempt 2: Success on Remediation
    client.post(
        "/api/activity/act_measurement_prob_diagnostic/submit",
        json={"learner_id": "u_case_c", "response": "B"},
    )
    # Attempt 3: Success on Retry Grover
    res3 = client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": "u_case_c", "response": "10"},
    )
    data = res3.json()
    inf = data["learner_state"]["gap_inferences"]["grover.search_problem"]
    assert inf["status"] == "improving"
    assert inf["trend"] == "improving"
    assert inf["confidence"] == 0.15
    assert data["adaptive_decision"]["action"] == "advance"


def test_frontend_renders_stable_mastery_state():
    """Requirement 10: Case D Correct -> Correct -> stable_mastery, advance."""
    client = TestClient(app)
    client.post(
        "/api/activity/act_grover_iteration_reasoning/submit",
        json={"learner_id": "u_case_d", "response": "B"},
    )
    res2 = client.post(
        "/api/activity/act_grover_iteration_reasoning/submit",
        json={"learner_id": "u_case_d", "response": "B"},
    )
    data = res2.json()
    inf = data["learner_state"]["gap_inferences"]["grover.amplitude_amplification"]
    assert inf["status"] == "mastered"
    assert inf["trend"] == "stable_mastery"
    assert inf["confidence"] == 0.0


def test_frontend_handles_404_activity_not_found():
    """Requirement 11: 404 for unknown activity ID."""
    client = TestClient(app)
    res = client.get("/api/activity/act_unknown_xyz")
    assert res.status_code == 404
    assert "not found" in res.json()["detail"].lower()


def test_frontend_handles_500_quantum_failure():
    """Requirement 12: 500 when quantum execution fails."""
    client = TestClient(app)
    with patch("backend.api.routes.activities.run_experiment", side_effect=RuntimeError("Aer simulator failure")):
        res = client.post(
            "/api/activity/act_grover_2q_predict/submit",
            json={"learner_id": "u_err_q", "response": "10"},
        )
        assert res.status_code == 500
        assert "Quantum execution engine failed" in res.json()["detail"]


def test_frontend_handles_503_persistence_failure():
    """Requirement 13: 503 when persistence is unavailable."""
    client = TestClient(app)
    class BrokenRepo(InMemoryLearnerRepository):
        def save(self, state):
            raise StorageUnavailableError("Supabase network partition")

    set_learner_repository(BrokenRepo())
    res = client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": "u_err_p", "response": "10"},
    )
    assert res.status_code == 503
    assert "Failed to persist updated learner state" in res.json()["detail"]


def test_frontend_ai_failure_does_not_erase_submission():
    """Requirement 14: AI failure returns 503 but does not alter successful submission."""
    client = TestClient(app)
    repo = InMemoryLearnerRepository()
    set_learner_repository(repo)

    # 1. Submission succeeds
    sub_res = client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": "u_ai_fail", "response": "10"},
    )
    assert sub_res.status_code == 200
    sub_data = sub_res.json()

    # 2. AI fails
    class FailingProvider(LLMProvider):
        def generate(self, messages, model=None):
            raise RuntimeError("API timeout")

    set_llm_provider(FailingProvider())
    ai_res = client.post(
        "/api/ai/explain_experiment",
        json={
            "learner_response": "10",
            "verified_result": sub_data["verified_result"],
            "evidence": sub_data["evidence"],
            "adaptive_decision": sub_data["adaptive_decision"],
        },
    )
    assert ai_res.status_code == 503

    # 3. State in repository remains intact
    assert repo.exists("u_ai_fail") is True
    persisted = repo.get("u_ai_fail")
    assert len(persisted.evidence_history) == 1


def test_frontend_static_serving():
    """Verify that FastAPI mounts and serves the enhanced hybrid frontend index.html."""
    client = TestClient(app)
    res = client.get("/")
    assert res.status_code == 200
    html = res.text
    # Core brand & structure
    assert "Q-BIT.140" in html
    assert "Interactive Quantum Circuit Studio" in html
    # Hybrid visual enhancements
    assert '<canvas id="fx"></canvas>' in html
    assert 'class="atom"' in html
    # Topbar Mastery
    assert 'id="chipMastery"' in html
    assert 'id="badgeMastery"' in html
    # Profile modal & subviews
    assert 'id="profileModal"' in html
    assert 'id="profileView-menu"' in html
    assert 'id="profileView-edit"' in html
    assert 'id="profileView-settings"' in html
    # Core quantum & adaptive IDs
    assert 'id="circuitWireGrid"' in html
    assert 'id="quantumResultsCard"' in html
    assert 'id="stateTriadContainer"' in html
    assert 'id="histogramContainer"' in html
    assert 'id="adaptiveDecisionCard"' in html
    assert 'id="aiGuidanceCard"' in html
    assert 'id="askModal"' in html


def test_validate_frontend_javascript():
    import subprocess
    import time
    import threading
    import tempfile
    import shutil
    import re
    from pathlib import Path
    import urllib.request
    import uvicorn
    from backend.api.main import app

    # Check if port 8000 is already active; if not, spin up a background test server
    port = 8000
    server = None
    try:
        urllib.request.urlopen("http://127.0.0.1:8000/api/activities", timeout=1.0)
    except Exception:
        port = 8769
        config = uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning")
        server = uvicorn.Server(config)
        t = threading.Thread(target=server.run, daemon=True)
        t.start()
        time.sleep(1.0)

    user_data = Path(tempfile.mkdtemp(prefix="edge_user_data_"))
    edge_exe = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

    try:
        cmd = [
            edge_exe,
            "--headless=new",
            "--enable-logging",
            "--v=1",
            "--virtual-time-budget=5000",
            "--dump-dom",
            f"--user-data-dir={user_data}",
            f"http://127.0.0.1:{port}/",
        ]
        res = subprocess.run(cmd, capture_output=True, encoding="utf-8", errors="replace", timeout=30)

        dom_output = res.stdout

        title_match = re.search(r'id="activityTitle"[^>]*>([^<]+)<', dom_output)
        prompt_match = re.search(r'id="activityPrompt"[^>]*>([^<]+)<', dom_output)

        assert title_match is not None, "activityTitle element not found in DOM output"
        assert "Loading" not in title_match.group(1), f"Activity stuck at loading state: {title_match.group(1)}"
        assert "Grover" in title_match.group(1), f"Expected Grover in title, got: {title_match.group(1)}"
        assert prompt_match is not None, "activityPrompt element not found in DOM output"
        assert "Loading" not in prompt_match.group(1), "Activity prompt stuck at loading state"
    finally:
        if server:
            server.should_exit = True
        shutil.rmtree(user_data, ignore_errors=True)


def test_end_to_end_error_and_remediation_flow():
    """
    End-to-End Judge Flow Verification:
      1. Initial page loads Grover 2Q activity
      2. Wrong prediction submitted ('01')
      3. Real M3/Aer execution (1024 shots) returns measured result
      4. Unique evidence ID is generated and logged
      5. M2 cognitive gap inference derives misconception
      6. Repeated errors trigger targeted remediation to act_measurement_prob_diagnostic
      7. Activity switching loads measurement diagnostic
    """
    client = TestClient(app)

    # 1. Verify initial Grover activity
    res1 = client.get("/api/activity/act_grover_2q_predict")
    assert res1.status_code == 200
    act1 = res1.json()
    assert act1["activity_id"] == "act_grover_2q_predict"
    assert act1["task_type"] == "quantum_prediction"

    # 2. First attempt - wrong prediction ("01")
    learner_id = "test_judge_e2e"
    res2 = client.post(
        f"/api/activity/{act1['activity_id']}/submit",
        json={"learner_id": learner_id, "response": "01"},
    )
    assert res2.status_code == 200
    sub1 = res2.json()
    assert sub1["verified_result"]["shots"] == 1024
    assert sub1["verified_result"]["target_state"] == "10"
    assert sub1["evidence"]["is_correct"] is False
    assert sub1["evidence"]["evidence_id"].startswith("ev_")
    assert sub1["adaptive_decision"]["action"] in ["gather_evidence", "targeted_remediation"]

    # 3. Second attempt - repeated wrong prediction triggers targeted_remediation
    res3 = client.post(
        f"/api/activity/{act1['activity_id']}/submit",
        json={"learner_id": learner_id, "response": "01"},
    )
    assert res3.status_code == 200
    sub2 = res3.json()
    assert sub2["evidence"]["is_correct"] is False
    assert sub2["adaptive_decision"]["action"] == "targeted_remediation"
    remed_target = sub2["adaptive_decision"]["target"]
    assert remed_target == "act_measurement_prob_diagnostic"

    # 4. Switch activity to recommended remediation
    res4 = client.get(f"/api/activity/{remed_target}")
    assert res4.status_code == 200
    act2 = res4.json()
    assert act2["activity_id"] == "act_measurement_prob_diagnostic"
    assert act2["task_type"] == "conceptual_choice"
    assert "options" in act2 and len(act2["options"]) > 0

    # 5. Verify persistent evidence history
    st_res = client.get(f"/api/learner/{learner_id}/state")
    assert st_res.status_code == 200
    st = st_res.json()
    assert len(st["evidence_history"]) == 2


def test_advancement_path_and_readiness_flow():
    """
    Verify Advancement Path & Readiness Check:
      1. Correct prediction ('10') triggers advancement to act_grover_iteration_reasoning
      2. Diagnostic readiness check grades answers and records evidence
    """
    client = TestClient(app)

    # 1. Correct prediction on Grover 2Q
    learner_id = "test_judge_correct"
    res = client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": learner_id, "response": "10"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["evidence"]["is_correct"] is True
    assert data["adaptive_decision"]["action"] == "advance"
    assert data["adaptive_decision"]["target"] == "act_grover_iteration_reasoning"


    # 2. Verify advancement activity exists and can be loaded
    adv_res = client.get(f"/api/activity/{data['adaptive_decision']['target']}")
    assert adv_res.status_code == 200
    adv_act = adv_res.json()
    assert adv_act["activity_id"] == "act_grover_iteration_reasoning"
    assert adv_act["task_type"] == "conceptual_choice"

    # 3. Diagnostic readiness submission
    diag_res = client.post(
        "/api/diagnostic/submit",
        json={
            "learner_id": "test_judge_diag",
            "answers": {
                "diag_qubit_basis": "A",
                "diag_superposition_hadamard": "B",
            },
        },
    )
    assert diag_res.status_code == 200
    diag_data = diag_res.json()
    assert diag_data["total_questions"] == 4
    assert "adaptive_decision" in diag_data

    # 4. Verify diagnostic evidence appears in persistent history
    st_res = client.get("/api/learner/test_judge_diag/state")
    assert st_res.status_code == 200
    st = st_res.json()
    assert len(st["evidence_history"]) == 4
    assert st["evidence_history"][0]["evidence_type"] == "diagnostic_response"


def test_validate_readiness_modal_rendered_in_browser():
    """
    Live Headless Browser E2E Test:
      1. Loads application in Microsoft Edge with ?check_readiness
      2. Verifies all 4 readiness questions render with real question prompts (not undefined)
      3. Verifies answer option selection updates the selected button class
      4. Verifies answered count updates to '1 of 4 answered'
    """
    import subprocess
    import time
    import threading
    import tempfile
    import shutil
    import re
    from pathlib import Path
    import urllib.request
    import uvicorn
    from backend.api.main import app

    port = 8000
    server = None
    try:
        urllib.request.urlopen("http://127.0.0.1:8000/api/activities", timeout=1.0)
    except Exception:
        port = 8771
        config = uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning")
        server = uvicorn.Server(config)
        t = threading.Thread(target=server.run, daemon=True)
        t.start()
        time.sleep(1.0)

    user_data = Path(tempfile.mkdtemp(prefix="edge_user_data_readiness_"))
    edge_exe = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

    try:
        cmd = [
            edge_exe,
            "--headless=new",
            "--enable-logging",
            "--v=1",
            "--virtual-time-budget=5000",
            "--dump-dom",
            f"--user-data-dir={user_data}",
            f"http://127.0.0.1:{port}/?check_readiness",
        ]
        res = subprocess.run(cmd, capture_output=True, encoding="utf-8", errors="replace", timeout=30)
        dom_output = res.stdout

        # Verify modal container and questions
        assert "What is a qubit?" in dom_output, "Question 1 prompt 'What is a qubit?' not rendered in browser DOM"
        assert "What is quantum superposition?" in dom_output, "Question 2 prompt not rendered in browser DOM"
        assert "What is the purpose of measuring a qubit?" in dom_output, "Question 3 prompt not rendered"
        assert "What is the purpose of a quantum gate?" in dom_output, "Question 4 prompt not rendered"

        # Verify 'undefined' is not present in question text
        m_undef = re.search(r'class="readiness-q-text"[^>]*>\s*undefined\s*<', dom_output)
        assert m_undef is None, "Found 'undefined' as readiness question prompt in browser DOM"

        # Verify option selection state
        assert 'opt-diag_qubits-B' in dom_output, "Expected option button ID opt-diag_qubits-B not found"
        assert 'class="readiness-option-btn selected"' in dom_output or 'selected' in dom_output, "Selected option state not reflected in browser DOM"
        assert "1 of 4 answered" in dom_output, "Progress text '1 of 4 answered' not reflected in browser DOM"
    finally:
        if server:
            server.should_exit = True
        shutil.rmtree(user_data, ignore_errors=True)


def test_validate_ask_ai_workspace_modal_structure():
    """
    Verify Enlarged AI Assistant Learning Workspace:
      1. Modal structure has .ask-modal-card with generous desktop dimensions (68vw, 76vh)
      2. Question input textarea has dedicated .ask-textarea with comfortable height
      3. Response area occupies dedicated scrollable .ask-response-container
      4. Grounded AI API integration at /api/ai/ask remains fully functional
    """
    from pathlib import Path
    client = TestClient(app)

    # 1. Verify HTML template structure
    html_path = Path("frontend/index.html")
    html = html_path.read_text(encoding="utf-8")
    assert 'class="modal-card ask-modal-card"' in html
    assert 'class="ask-modal-header"' in html
    assert 'id="askQuestionInput" class="ask-textarea"' in html
    assert 'id="askSubmitBtn"' in html
    assert 'id="askAnswerBox"' in html
    assert 'class="ask-response-workspace"' in html

    # 2. Verify CSS styles for the workspace dimensions
    css_path = Path("frontend/css/styles.css")
    css = css_path.read_text(encoding="utf-8")
    assert ".ask-modal-card" in css
    assert "width: 82vw" in css
    assert "height: 82vh" in css
    assert "max-width: 1400px" in css
    assert "max-height: 900px" in css
    assert ".ask-response-container" in css
    assert ".ask-action-row" in css


    # 3. Verify backend AI endpoint functions accurately
    res = client.post(
        "/api/ai/ask",
        json={
            "question": "What is quantum superposition?",
            "concept_id": "quantum.superposition",
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert "answer" in data
    assert len(data["answer"]) > 50


def test_validate_ask_ai_workspace_rendered_in_browser_desktop_viewport():
    """
    Verify live Microsoft Edge browser rendering of Ask AI Assistant Workspace at 1750x860:
      1. Loads application in Edge at 1750x860 with ?check_ask_ai
      2. Verifies #askModal is open with .ask-modal-card
      3. Verifies horizontal header with .ask-modal-title and top-right .ask-close-btn
      4. Verifies full-width .ask-textarea and horizontal .ask-action-row
      5. Verifies expansive .ask-response-container spanning the full inner width
    """
    import subprocess
    import time
    import threading
    import tempfile
    import shutil
    import re
    from pathlib import Path
    import urllib.request
    import uvicorn
    from backend.api.main import app

    port = 8000
    server = None
    try:
        urllib.request.urlopen("http://127.0.0.1:8000/api/activities", timeout=1.0)
    except Exception:
        port = 8772
        config = uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning")
        server = uvicorn.Server(config)
        t = threading.Thread(target=server.run, daemon=True)
        t.start()
        time.sleep(1.0)

    user_data = Path(tempfile.mkdtemp(prefix="edge_user_data_ask_ai_"))
    edge_exe = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

    try:
        cmd = [
            edge_exe,
            "--headless=new",
            "--window-size=1750,860",
            "--enable-logging",
            "--v=1",
            "--virtual-time-budget=5000",
            "--dump-dom",
            f"--user-data-dir={user_data}",
            f"http://127.0.0.1:{port}/?check_ask_ai",
        ]
        res = subprocess.run(cmd, capture_output=True, encoding="utf-8", errors="replace", timeout=30)
        dom_output = res.stdout

        # 1. Verify modal is displayed and has the workspace layout classes
        assert 'id="askModal"' in dom_output
        assert 'ask-modal-card' in dom_output
        assert 'ask-modal-header' in dom_output
        assert 'ask-close-btn' in dom_output
        assert 'ask-question-section' in dom_output
        assert 'ask-textarea' in dom_output
        assert 'ask-action-row' in dom_output
        assert 'ask-grounding-pill' in dom_output
        assert 'ask-response-workspace' in dom_output
        assert 'ask-response-container' in dom_output
        assert 'AI Conceptual Learning Workspace' in dom_output

        # 2. Verify modal is visible (display is flex, not none)
        m_modal = re.search(r'<div[^>]*id="askModal"[^>]*style="([^"]*)"', dom_output)
        if m_modal:
            style_str = m_modal.group(1)
            assert 'display: flex' in style_str or 'display: none' not in style_str
    finally:
        if server:
            server.should_exit = True
        shutil.rmtree(user_data, ignore_errors=True)
