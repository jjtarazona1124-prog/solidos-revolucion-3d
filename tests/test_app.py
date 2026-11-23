"""Pruebas de humo de la interfaz Streamlit (sin navegador)."""

from pathlib import Path

from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).resolve().parent.parent / "app.py")


def test_app_carga_sin_errores():
    at = AppTest.from_file(APP, default_timeout=60).run()
    assert not at.exception
    assert len(at.metric) == 3


def test_app_modo_personalizado():
    at = AppTest.from_file(APP, default_timeout=60).run()
    at.sidebar.radio[0].set_value("Personalizado").run()
    assert not at.exception
