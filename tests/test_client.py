import os


def test_login(workforce_planner_client):
    page = workforce_planner_client._login()
    assert page is not None


def test_slet_personressource(workforce_planner_client):
    email = os.getenv("TEST_MAIL", "")
    workforce_planner_client.slet_personressource(email)


def test_deaktiver_bruger(workforce_planner_client):
    email = os.getenv("TEST_MAIL", "")
    workforce_planner_client.deaktiver_bruger(email)
