import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pytest

from app import render_animation
from src.evaluation import run_algorithm
from src.scenarios import build_grid, load_locations
from src.visualization import CELL_COLORS, draw_grid


def labels(figure):
    return [text.get_text() for text in figure.axes[0].texts]


def test_stairs_marker_is_hidden_until_fallback_is_active():
    grid = build_grid("Both emergency exits on fire", load_locations()["Room A"])
    hidden = draw_grid(grid)
    shown = draw_grid(grid, stairs_visible=True)
    assert "CS" not in labels(hidden)
    assert "CS" in labels(shown)
    assert "E1 ×" in labels(shown) and "E2 ×" in labels(shown)
    assert labels(shown).count("F") == 2
    plt.close(hidden)
    plt.close(shown)


def test_fire_on_stairs_remains_visible_as_blocked_destination():
    grid = build_grid("No traversable destination", load_locations()["Room A"])
    figure = draw_grid(grid, stairs_visible=True)
    assert "CS ×" in labels(figure)
    assert labels(figure).count("F") == 3
    plt.close(figure)


def test_risky_route_is_orange_instead_of_being_labelled_safe():
    grid = build_grid("Risky stairs fallback", load_locations()["Room A"])
    result = run_algorithm("A*", grid)
    figure = draw_grid(grid, path=result["path"], stairs_visible=True, risk_level=result["risk_level"])
    assert figure.axes[0].lines[0].get_color() == CELL_COLORS["risky_path"]
    assert "Risky route" in [text.get_text() for text in figure.axes[0].get_legend().get_texts()]
    assert "SM" in labels(figure) and "CS" in labels(figure)
    plt.close(figure)


class Recorder:
    def __init__(self):
        self.frames = []
        self.messages = []
        self.progress_values = []

    def pyplot(self, figure, **kwargs):
        self.frames.append(labels(figure))

    def info(self, message):
        self.messages.append(("info", message))

    def warning(self, message):
        self.messages.append(("warning", message))

    def success(self, message):
        self.messages.append(("success", message))

    def error(self, message):
        self.messages.append(("error", message))

    def progress(self, value):
        self.progress_values.append(value)


@pytest.mark.parametrize("scenario", ["All exit corridors blocked (stairs fallback)", "Risky stairs fallback", "No traversable destination"])
def test_animation_reveals_stairs_only_after_primary_search(scenario, monkeypatch):
    monkeypatch.setattr("app.time.sleep", lambda duration: None)
    grid = build_grid(scenario, load_locations()["Room A"])
    result = run_algorithm("A*", grid, include_trace=True)
    frames, status, progress = Recorder(), Recorder(), Recorder()
    render_animation(
        "A*", grid, result, frame_placeholder=frames,
        status_placeholder=status, progress_placeholder=progress, delay_seconds=0.001,
    )
    primary_count = result["stages"][0]["nodes_explored"] + 1
    assert all(not any(label.startswith("CS") for label in frame) for frame in frames.frames[:primary_count])
    assert all(any(label.startswith("CS") for label in frame) for frame in frames.frames[primary_count:])
    assert progress.progress_values[-1] == 1.0
    assert progress.progress_values == sorted(progress.progress_values)
    if result["risk_level"] == "risky":
        assert status.messages[-1][0] == "warning"
    elif not result["route_found"]:
        assert status.messages[-1][0] == "error"
