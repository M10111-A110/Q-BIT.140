from fastapi.testclient import TestClient
from backend.api.main import app

client = TestClient(app)


def test_get_all_activities():
    response = client.get("/api/activities")
    assert response.status_code == 200
    activities = response.json()
    assert len(activities) == 4
    act_ids = [a["activity_id"] for a in activities]
    assert "act_grover_2q_predict" in act_ids
    assert "act_measurement_prob_diagnostic" in act_ids


def test_get_activity_detail():
    response = client.get("/api/activity/act_grover_2q_predict")
    assert response.status_code == 200
    data = response.json()
    assert data["activity_id"] == "act_grover_2q_predict"
    assert data["concept_id"] == "grover.search_problem"
    assert data["task_type"] == "quantum_prediction"
    assert data["quantum_experiment"] is not None
    assert data["quantum_experiment"]["algorithm"] == "grover"
    assert data["quantum_experiment"]["num_qubits"] == 2
    assert data["remediation_activity_id"] == "act_measurement_prob_diagnostic"


def test_get_activity_unknown_returns_404():
    response = client.get("/api/activity/non_existent_activity")
    assert response.status_code == 404
    assert "Activity 'non_existent_activity' not found" in response.json()["detail"]
