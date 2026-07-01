import pytest
import os

from workforce_planner_client.client import WorkforcePlannerClient


@pytest.fixture
def workforce_planner_client():
    raw_headless = os.getenv("TEST_HEADLESS")
    if raw_headless is None:
        raw_headless = os.getenv("PLAYWRIGHT_HEADLESS", "true")
    test_headless = raw_headless.strip().lower() in {"1", "true", "yes", "on"}
    client = WorkforcePlannerClient(
        base_url=os.getenv("BASE_URL", "about:blank"),
        username=os.getenv("USERNAME", ""),
        password=os.getenv("PASSWORD", ""),
        headless=test_headless,
    )
    yield client
    client.close()
