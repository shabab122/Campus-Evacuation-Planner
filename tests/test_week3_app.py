"""Dashboard integration tests with instant playback (no artificial sleeps)."""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest


APP_PATH = Path(__file__).resolve().parents[1] / "app.py"


def launch():
    app = AppTest.from_file(str(APP_PATH), default_timeout=20).run()
    assert not app.exception
    app.select_slider[0].set_value("Instant")
    return app


@pytest.mark.parametrize("scenario,risk", [
    ("Normal conditions", "safe"),
    ("All exit corridors blocked (stairs fallback)", "safe"),
    ("Risky stairs fallback", "risky"),
    ("No traversable destination", "unavailable"),
])
def test_dashboard_runs_selected_algorithm_and_displays_correct_destination(scenario, risk):
    app = launch()
    app.selectbox[0].select(scenario)
    app.button[0].click().run()
    assert not app.exception
    result = app.session_state["completed_results"]["A*"]
    assert result["risk_level"] == risk
    assert len(app.session_state["completed_results"]) == 1
    assert not app.dataframe  # Comparison stays locked until every algorithm runs.
    destination = next(metric.value for metric in app.metric if metric.label == "Destination")
    expected = "Emergency exit" if scenario == "Normal conditions" else "—" if risk == "unavailable" else "Central stairs"
    assert destination == expected
    if risk == "risky":
        assert any("RISKY ROUTE" in element.value for element in app.warning)
    elif risk == "unavailable":
        assert any("No traversable route" in element.value for element in app.error)


def test_all_algorithm_comparison_unlocks_and_resets_on_model_changes():
    app = launch()
    app.selectbox[0].select("Risky stairs fallback")
    app.button[1].click().run()
    assert not app.exception
    assert len(app.session_state["completed_results"]) == 5
    assert len(app.dataframe) == 1
    assert set(app.dataframe[0].value["Destination Type"]) == {"central stairs"}
    assert set(app.dataframe[0].value["Route Risk"]) == {"Risky"}

    # Algorithm/speed are presentation controls and keep this experiment's results.
    app.selectbox[2].select("BFS").run()
    assert len(app.session_state["completed_results"]) == 5
    # The new blocked-cell field must participate in the model signature.
    app.text_input[3].input("0,4").run()
    assert not app.exception
    assert app.session_state["completed_results"] == {}
    assert not app.dataframe


def test_custom_exit_fire_is_accepted_and_invalid_start_fire_is_a_visible_error():
    app = launch()
    app.text_input[2].input("0,5; 5,5")
    app.button[0].click().run()
    assert not app.exception
    assert app.session_state["completed_results"]["A*"]["destination_type"] == "central_stairs"

    app.text_input[2].input("0,0").run()
    assert not app.exception
    assert any("Start" in element.value for element in app.error)
    assert app.session_state["completed_results"] == {}


def test_no_route_comparison_does_not_turn_missing_cost_into_zero():
    app = launch()
    app.selectbox[0].select("No traversable destination")
    app.button[1].click().run()
    assert not app.exception
    table = app.dataframe[0].value
    assert set(table["Route Found"]) == {"No"}
    assert table["Route Cost"].isna().all()
    assert any("route cost is unavailable" in element.value for element in app.info)


def test_reset_and_start_location_change_clear_completed_results():
    app = launch()
    app.button[0].click().run()
    app.button[2].click().run()
    assert app.session_state["completed_results"] == {}
    app.button[0].click().run()
    app.selectbox[1].select("Computer Lab").run()
    assert not app.exception
    assert app.session_state["completed_results"] == {}


def test_scenario_change_excludes_a_named_location_that_is_on_fire():
    app = launch()
    app.selectbox[1].select("Cafeteria").run()
    app.selectbox[0].select("All exit corridors blocked (stairs fallback)").run()
    assert not app.exception
    assert "Cafeteria" not in app.selectbox[1].options
    assert app.selectbox[1].value != "Cafeteria"
    assert any("Cafeteria" in item.value for item in app.caption)
