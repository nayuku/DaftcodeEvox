from fastapi.testclient import TestClient
from main import app
import base64


# /auth
def test_correct_auth():
    with TestClient(app) as client:
        valid_credentials = base64.b64encode(b"admin:hard_password").decode("utf-8")
        response = client.post("/auth", headers={"Authorization": "Basic " + valid_credentials})
        assert response.status_code == 201
        assert response.json() == {"detail": "Authorized"}


def test_incorrect_auth():
    with TestClient(app) as client:
        invalid_credentials = base64.b64encode(b"wrong:wrong").decode("utf-8")
        response = client.post("/auth", headers={"Authorization": "Basic " + invalid_credentials})
        assert response.status_code == 401


def test_empty_auth():
    with TestClient(app) as client:
        response = client.post("/auth")
        assert response.status_code == 401


def test_wrong_methods_auth():
    with TestClient(app) as client:
        response = client.get("/auth")
        assert response.status_code == 405
        response = client.options("/auth")
        assert response.status_code == 405
        response = client.head("/auth")
        assert response.status_code == 405
        response = client.put("/auth")
        assert response.status_code == 405
        response = client.delete("/auth")
        assert response.status_code == 405


# /read_msg
def test_read_correct_msg():
    with TestClient(app) as client:
        response = client.get("/read_msg/1")  # msg with id 1 exists in db
        assert response.status_code == 200


def test_counter_read_msg():
    with TestClient(app) as client:
        responses = []
        for i in range(3):
            responses.append(client.get("/read_msg/1"))

        assert responses[0].json()["counter"] + 1 == responses[1].json()["counter"]
        assert responses[1].json()["counter"] + 1 == responses[2].json()["counter"]


def test_read_incorrect_msg():
    with TestClient(app) as client:
        # non-existing id
        response = client.get("/read_msg/0")
        assert response.status_code == 404
        # wrong symbol as id
        response = client.get("/read_msg/abc")
        assert response.status_code == 422


# helper function for testing authentication in various actions
def auth(client):
    valid_credentials = base64.b64encode(b"admin:hard_password").decode("utf-8")
    client.post("/auth", headers={"Authorization": "Basic " + valid_credentials})


# /add_msg
def test_add_correct_msg():
    with TestClient(app) as client:
        auth(client)
        response = client.post("/add_msg", json={"text": "test"})
        assert response.status_code == 201  # msg created

        # test if counter is 1 after first view of added msg
        msg_id = response.json()["detail"].split(" ")[-1]  # id of created msg
        response = client.get(f"/read_msg/{msg_id}")  # msg with id 1 exists in db
        assert response.status_code == 200
        assert response.json()["counter"] == 1

        # edge cases e.g. len == 1 or len == 160
        response = client.post("/add_msg", json={"text": "a"})
        assert response.status_code == 201  # msg created
        response = client.post("/add_msg", json={"text": f"{'a' * 160}"})
        assert response.status_code == 201  # msg created


def test_add_msg_unauth():
    with TestClient(app) as client:
        response = client.post("/add_msg", json={"text": "test"})
        assert response.status_code == 401


def test_add_incorrect_msg():
    with TestClient(app) as client:
        auth(client)
        # too long msg
        response = client.post("/add_msg", json={"text": f"{'a' * 161}"})
        assert response.status_code == 400
        # empty message
        response = client.post("/add_msg", json={"text": ""})
        assert response.status_code == 400
        # only whitespaces
        response = client.post("/add_msg", json={"text": "   \r\n "})
        assert response.status_code == 400
        # wrong parameter
        response = client.post("/add_msg", json={"text1": "test"})
        assert response.status_code == 422
        # no parameter
        response = client.post("/add_msg")
        assert response.status_code == 422


# /delete_msg
def test_delete_msg_unauth():
    with TestClient(app) as client:
        response = client.delete("/delete_msg/1")
        assert response.status_code == 401


def test_correct_delete_msg():
    with TestClient(app) as client:
        auth(client)
        # first add new record
        response = client.post("/add_msg", json={"text": "test"})
        assert response.status_code == 201  # msg created
        # id of created msg
        msg_id = response.json()["detail"].split(" ")[-1]
        # now delete
        response = client.delete(f"/delete_msg/{msg_id}")
        assert response.status_code == 200


def test_incorrect_delete_msg():
    with TestClient(app) as client:
        auth(client)
        # non-existing msg id
        response = client.delete("/delete_msg/0")
        assert response.status_code == 404
        # wrong symbol as id
        response = client.delete("/delete_msg/abc")
        assert response.status_code == 422


# edit_msg
def test_edit_msg_unauth():
    with TestClient(app) as client:
        response = client.put("/edit_msg/1", json={"text": "test"})
        assert response.status_code == 401


def test_correct_edit_msg():
    with TestClient(app) as client:
        auth(client)
        response = client.put("/edit_msg/1", json={"text": "test"})
        assert response.status_code == 200
        # check if counter was resetted
        response = client.get(f"/read_msg/1")
        assert response.status_code == 200
        assert response.json()["counter"] == 1


def test_incorrect_edit_msg():
    with TestClient(app) as client:
        auth(client)
        # non-existing msg id
        response = client.put("/edit_msg/0", json={"text": "test"})
        assert response.status_code == 404
        # too long msg
        response = client.put("/edit_msg/1", json={"text": f"{'a' * 161}"})
        assert response.status_code == 400
        # empty message
        response = client.put("/edit_msg/1", json={"text": ""})
        assert response.status_code == 400
        # only whitespaces
        response = client.put("/edit_msg/1", json={"text": "   \r\n "})
        assert response.status_code == 400
        # wrong parameter
        response = client.put("/edit_msg/1", json={"text1": "test"})
        assert response.status_code == 422
        # no parameter
        response = client.put("/edit_msg/1")
        assert response.status_code == 422
