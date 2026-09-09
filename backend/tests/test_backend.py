import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.services.validation.rules import (
    check_land_area,
    check_survey_number,
    check_area_unit,
    check_administrative_hierarchy
)
from backend.app.services.extraction.confidence import calculate_field_confidence

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_auth_login():
    response = client.post(
        "/api/v1/auth/login-json",
        json={"username": "verifier", "password": "verifierpassword123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["role"] == "verifier"


def test_validation_rule_area_positive():
    res_pos = check_land_area({"land_area": "2.45"})
    assert res_pos.passed is True

    res_neg = check_land_area({"land_area": "-1.50"})
    assert res_neg.passed is False

    res_zero = check_land_area({"land_area": "0.0"})
    assert res_zero.passed is False


def test_validation_rule_survey_format():
    res_valid = check_survey_number({"survey_number": "124/2"})
    assert res_valid.passed is True

    res_valid_alpha = check_survey_number({"survey_number": "88/1A"})
    assert res_valid_alpha.passed is True

    res_smudge = check_survey_number({"survey_number": "124/?"})
    assert res_smudge.passed is False


def test_validation_rule_hierarchy():
    res_valid = check_administrative_hierarchy({
        "state": "Telangana",
        "district": "Ranga Reddy",
        "mandal_tehsil": "Shamshabad",
        "village": "Mamidipally"
    })
    assert res_valid.passed is True

    res_invalid = check_administrative_hierarchy({
        "state": "Telangana",
        "district": "Ranga Reddy",
        "mandal_tehsil": "Shamshabad",
        "village": "FakeVillageXYZ"
    })
    assert res_invalid.passed is False


def test_confidence_scoring():
    high_conf = calculate_field_confidence("survey_number", "124/2", token_confidence=0.96)
    assert high_conf >= 0.90

    smudged_conf = calculate_field_confidence("survey_number", "124/?", token_confidence=0.52)
    assert smudged_conf < 0.70


def test_gis_parcels():
    response = client.get("/api/v1/gis/parcels")
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "FeatureCollection"
    assert len(data["features"]) > 0


def test_analytics_dashboard():
    response = client.get("/api/v1/analytics/dashboard")
    assert response.status_code == 200
    data = response.json()
    assert "metrics" in data
    assert data["metrics"]["total_documents"] > 0
