import pytest

def pytest_configure(config):
    config.addinivalue_line("markers", "vcr: mark test to run with vcrpy")
