import sys, os
from fastapi.testclient import TestClient

sys.path.append(os.getcwd())
from main import app

client = TestClient(app)

def test_hello():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"success": 1}

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"success": 1}

def test_plugin():

    # no args
    response = client.get("/plugin")
    assert response.status_code == 422
    assert response.json() == {'detail': [{'loc': ['query', 'slug'], 'msg': 'field required', 'type': 'value_error.missing'}]}

    # nominal
    response = client.get("/plugin?slug=wordpress-seo")
    assert response.status_code == 200
    assert response.json()["rows"][0]["name"] == 'Yoast SEO'
    assert response.json()["rows"][0]["slug"] == 'wordpress-seo'
    assert response.json()["rows"][0]["version"] >= '18.9'
    assert response.json()["rows"][0]["last_updated_gmt"] >= '2022'
    # {'rows': [{'last_updated_gmt': '2022-05-25 21:39:33', 'name': 'Yoast SEO', 'slug': 'wordpress-seo', 'version': '18.9'}]}

    # multiple rows
    response = client.get("/plugin?slug=wordpress-seo&slug=contact-form-7")
    assert response.status_code == 200
    assert len(response.json()["rows"]) == 2

    # missing rows
    response = client.get("/plugin?slug=wordpress-seo&slug=contact-form-7&slug=blah_blah_asdf")
    assert response.status_code == 200
    assert len(response.json()["rows"]) == 2
