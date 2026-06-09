"""Economics test configuration — all tests require --live flag."""

import pytest


@pytest.fixture(autouse=True)
def skip_if_not_live(live_mode):
    """Skip economics tests in pickle mode — all methods fetch live API data."""
    if not live_mode:
        pytest.skip("Economics tests require --live flag")
