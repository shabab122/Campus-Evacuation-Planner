from __future__ import annotations

from collections.abc import Iterable

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Circle, Patch, Rectangle


CELL_COLORS = {
    "normal": "#F8FAFC",
    "wall": "#1F2937",
    "crowd": "#F59E0B",
    "smoke": "#94A3B8",
    "fire": "#DC2626",
    "path": "#2563EB",
    "start": "#7C3AED",
    "exit": "#16A34A",
    "explored": "#38BDF8",
    "current": "#FACC15",
    "traveler": "#0F172A",
}


def draw_grid(
    grid,
    path=None,
    *,
    explored: Iterable[tuple[int, int]] | None = None,
    current: tuple[int, int] | None = None,
    traveler: tuple[int, int] | None = None,
    title: str = "Campus Evacuation Map",
):
    """Render a presentation-ready evacuation grid.

    ``explored`` and ``current`` are used while an algorithm is searching.
    ``traveler`` is used after a route is found to animate evacuation movement.
    """
    path = list(path or [])
    explored_set = set(explored or [])

    fig, ax = plt.subplots(figsize=(9.2, 7.2))
    fig.patch.set_facecolor("#0B1220")
    ax.set_facecolor("#0B1220")

    for row in range(grid.rows):
        for col in range(grid.cols):
            position = (row, col)
            y = grid.rows - row - 1

            if grid.base_grid[row][col] == -1:
                cell_type = "wall"
            else:
                cell_type = grid.hazard_type(position) or "normal"

            ax.add_patch(
                Rectangle(
                    (col + 0.04, y + 0.04),
                    0.92,
                    0.92,
                    facecolor=CELL_COLORS[cell_type],
                    edgecolor="#334155",
                    linewidth=1.15,
                    zorder=1,
                )
            )

            if position in explored_set and position not in {grid.start, *grid.exits}:
                ax.add_patch(
                    Rectangle(
                        (col + 0.10, y + 0.10),
                        0.80,
                        0.80,
                        facecolor=CELL_COLORS["explored"],
                        edgecolor="none",
                        alpha=0.28,
                        zorder=2,
                    )
                )

            _draw_cell_label(ax, grid, position, col, y)

    if path:
        x_values = [col + 0.5 for _, col in path]
        y_values = [grid.rows - row - 0.5 for row, _ in path]
        ax.plot(
            x_values,
            y_values,
            color=CELL_COLORS["path"],
            linewidth=5.5,
            alpha=0.92,
            solid_capstyle="round",
            zorder=5,
        )
        ax.scatter(
            x_values,
            y_values,
            s=42,
            facecolor="#DBEAFE",
            edgecolor=CELL_COLORS["path"],
            linewidth=1.4,
            zorder=6,
        )

    _draw_special_node(ax, grid, grid.start, "S", CELL_COLORS["start"])
    for index, exit_position in enumerate(grid.exits, start=1):
        _draw_special_node(ax, grid, exit_position, f"E{index}", CELL_COLORS["exit"])

    if current is not None:
        row, col = current
        y = grid.rows - row - 1
        ax.add_patch(
            Rectangle(
                (col + 0.08, y + 0.08),
                0.84,
                0.84,
                fill=False,
                edgecolor=CELL_COLORS["current"],
                linewidth=4,
                zorder=8,
            )
        )

    if traveler is not None:
        row, col = traveler
        ax.add_patch(
            Circle(
                (col + 0.5, grid.rows - row - 0.5),
                radius=0.20,
                facecolor="#FFFFFF",
                edgecolor=CELL_COLORS["traveler"],
                linewidth=2.4,
                zorder=10,
            )
        )
        ax.text(
            col + 0.5,
            grid.rows - row - 0.5,
            "●",
            color=CELL_COLORS["path"],
            ha="center",
            va="center",
            fontsize=13,
            weight="bold",
            zorder=11,
        )

    legend = [
        Patch(facecolor=CELL_COLORS["start"], label="Start"),
        Patch(facecolor=CELL_COLORS["exit"], label="Exit"),
        Line2D([0], [0], color=CELL_COLORS["path"], lw=4, label="Safe route"),
        Patch(facecolor=CELL_COLORS["explored"], alpha=0.35, label="Explored"),
        Patch(facecolor=CELL_COLORS["crowd"], label="Crowd · cost 3"),
        Patch(facecolor=CELL_COLORS["smoke"], label="Smoke · cost 8"),
        Patch(facecolor=CELL_COLORS["fire"], label="Fire · blocked"),
        Patch(facecolor=CELL_COLORS["wall"], label="Wall"),
    ]
    legend_obj = ax.legend(
        handles=legend,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.07),
        ncol=4,
        frameon=False,
        fontsize=9,
    )
    for text in legend_obj.get_texts():
        text.set_color("#CBD5E1")

    ax.set_xlim(0, grid.cols)
    ax.set_ylim(0, grid.rows)
    ax.set_aspect("equal")
    ax.set_xticks([index + 0.5 for index in range(grid.cols)])
    ax.set_yticks([index + 0.5 for index in range(grid.rows)])
    ax.set_xticklabels([f"C{index}" for index in range(grid.cols)], color="#94A3B8", fontsize=8)
    ax.set_yticklabels(
        [f"R{grid.rows - index - 1}" for index in range(grid.rows)],
        color="#94A3B8",
        fontsize=8,
    )
    ax.tick_params(length=0, pad=4)
    for spine in ax.spines.values():
        spine.set_visible(False)

    ax.set_title(title, loc="left", color="#F8FAFC", fontsize=15, weight="bold", pad=14)
    ax.text(
        1.0,
        1.025,
        f"{grid.rows} × {grid.cols} grid  •  {len(grid.exits)} exits",
        transform=ax.transAxes,
        ha="right",
        va="bottom",
        color="#94A3B8",
        fontsize=9,
    )
    fig.tight_layout(pad=1.6)
    return fig


def _draw_cell_label(ax, grid, position, col, y):
    hazard = grid.hazard_type(position)
    if grid.base_grid[position[0]][position[1]] == -1:
        label, color = "W", "#CBD5E1"
    elif hazard == "crowd":
        label, color = "C", "#78350F"
    elif hazard == "smoke":
        label, color = "SM", "#0F172A"
    elif hazard == "fire":
        label, color = "F", "#FFFFFF"
    else:
        return

    ax.text(
        col + 0.5,
        y + 0.5,
        label,
        color=color,
        ha="center",
        va="center",
        fontsize=9,
        weight="bold",
        zorder=4,
    )


def _draw_special_node(ax, grid, position, label, color):
    row, col = position
    y = grid.rows - row - 1
    ax.add_patch(
        Rectangle(
            (col + 0.14, y + 0.14),
            0.72,
            0.72,
            facecolor=color,
            edgecolor="#FFFFFF",
            linewidth=2.0,
            zorder=7,
        )
    )
    ax.text(
        col + 0.5,
        y + 0.5,
        label,
        color="#FFFFFF",
        ha="center",
        va="center",
        fontsize=10,
        weight="bold",
        zorder=8,
    )
