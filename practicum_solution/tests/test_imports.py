from importlib import import_module


def test_api_importable() -> None:
    assert import_module("practicum_solution.api.main")


def test_scripts_importable() -> None:
    assert import_module("practicum_solution.scripts.generate_data")
