from __future__ import annotations

import time

import matplotlib.pyplot as plt
import streamlit as st

from src.evaluation import ALGORITHMS, results_dataframe, run_algorithm
from src.scenarios import build_grid, load_locations, load_scenarios, parse_coordinates
from src.visualization import draw_grid


APP_CSS = """
<style>
    .stApp {
        background:
            radial-gradient(circle at top left, rgba(37,99,235,.10), transparent 32%),
            radial-gradient(circle at top right, rgba(124,58,237,.08), transparent 28%);
    }
    .block-container {
        max-width: 1500px;
        padding-top: 1.35rem;
        padding-bottom: 3rem;
    }
    .hero {
        padding: 1.1rem 1.25rem;
        border: 1px solid rgba(148,163,184,.20);
        border-radius: 18px;
        background: linear-gradient(135deg, rgba(15,23,42,.92), rgba(30,41,59,.82));
        box-shadow: 0 18px 48px rgba(2,6,23,.18);
        margin-bottom: 1rem;
    }
    .hero h1 {
        margin: 0;
        font-size: 1.85rem;
        line-height: 1.2;
        color: #F8FAFC;
    }
    .hero p {
        margin: .45rem 0 0 0;
        color: #CBD5E1;
        font-size: .96rem;
    }
    .status-chip {
        display: inline-block;
        padding: .30rem .65rem;
        margin: .15rem .25rem .15rem 0;
        border-radius: 999px;
        background: rgba(37,99,235,.12);
        border: 1px solid rgba(96,165,250,.28);
        color: #93C5FD;
        font-size: .80rem;
        font-weight: 600;
    }
    div[data-testid="stMetric"] {
        border: 1px solid rgba(148,163,184,.20);
        background: rgba(15,23,42,.34);
        padding: .70rem .85rem;
        border-radius: 14px;
    }
    div[data-testid="stDataFrame"] {
        border: 1px solid rgba(148,163,184,.18);
        border-radius: 14px;
        overflow: hidden;
    }
    div[data-testid="stSidebar"] button {
        border-radius: 10px;
        font-weight: 650;
    }
    .section-title {
        font-size: 1.10rem;
        font-weight: 700;
        margin: .25rem 0 .2rem 0;
    }
    .small-note {
        color: #94A3B8;
        font-size: .85rem;
    }
</style>
"""


def scenario_signature(
    scenario_name: str,
    location_name: str,
    crowd_raw: str,
    smoke_raw: str,
    fire_raw: str,
    blocked_raw: str = "",
):
    return (
        scenario_name,
        location_name,
        crowd_raw.strip(),
        smoke_raw.strip(),
        fire_raw.strip(),
        blocked_raw.strip(),
    )


def reset_for_scenario(key) -> None:
    if st.session_state.get("scenario_key") == key:
        return
    st.session_state.scenario_key = key
    st.session_state.completed_results = {}
    st.session_state.last_algorithm = None


def render_animation(
    algorithm_name,
    grid,
    result,
    *,
    frame_placeholder,
    status_placeholder,
    progress_placeholder,
    delay_seconds,
):
    path = result.get("path", [])
    if delay_seconds == 0:
        return  # Instant playback: the final frame is rendered after the rerun.
    stages = result["stages"]
    total_frames = max(result["nodes_explored"] + len(path), 1)
    completed_frames = 0
    for stage in stages:
        is_fallback = stage["phase"] == "central_stairs"
        stage_name = "Central stairs search" if is_fallback else "Emergency exit search"
        if is_fallback:
            status_placeholder.warning(
                "All emergency exits are unreachable. Central stairs activated; replanning from the start."
            )
        trace = stage.get("exploration_order", [])
        # Also reveal blocked stairs when the fallback has no searchable goal.
        fig = draw_grid(
            grid,
            stairs_visible=is_fallback,
            title=f"{algorithm_name} · {stage_name}",
        )
        frame_placeholder.pyplot(fig, use_container_width=True, clear_figure=True)
        plt.close(fig)
        if is_fallback:
            time.sleep(delay_seconds)
        for index, current in enumerate(trace, start=1):
            fig = draw_grid(
                grid, explored=trace[:index], current=current,
                stairs_visible=is_fallback,
                title=f"{algorithm_name} · {stage_name}",
            )
            frame_placeholder.pyplot(fig, use_container_width=True, clear_figure=True)
            plt.close(fig)
            completed_frames += 1
            progress_placeholder.progress(completed_frames / total_frames)
            status_placeholder.info(
                f"{stage_name} · node {current} · {index}/{len(trace)} expanded"
            )
            time.sleep(delay_seconds)

    if not path:
        status_placeholder.error(result["message"])
        progress_placeholder.progress(1.0)
        return

    destination_label = "central stairs" if result["fallback_used"] else "emergency exit"
    final_trace = stages[-1].get("exploration_order", [])
    for index, traveler in enumerate(path, start=1):
        partial_path = path[:index]
        fig = draw_grid(
            grid,
            path=partial_path,
            explored=final_trace,
            traveler=traveler,
            stairs_visible=result["stairs_visible"],
            risk_level=result["risk_level"],
            title=f"{algorithm_name} · Moving to {destination_label}",
        )
        frame_placeholder.pyplot(fig, use_container_width=True, clear_figure=True)
        plt.close(fig)
        completed_frames += 1
        progress_placeholder.progress(completed_frames / total_frames)
        movement_message = (
            f"Moving to {destination_label} · position {traveler} · "
            f"step {max(index - 1, 0)}/{max(len(path) - 1, 0)}"
        )
        if result["risk_level"] == "risky":
            status_placeholder.warning("Risky route: " + movement_message)
        else:
            status_placeholder.success(movement_message)
        time.sleep(max(delay_seconds * 1.35, 0.03))

    if result["risk_level"] == "risky":
        status_placeholder.warning(result["message"])
    else:
        status_placeholder.success(result["message"])


def execute_with_animation(
    algorithm_name,
    grid,
    *,
    frame_placeholder,
    status_placeholder,
    progress_placeholder,
    delay_seconds,
):
    result = run_algorithm(algorithm_name, grid, include_trace=True)
    render_animation(
        algorithm_name,
        grid,
        result,
        frame_placeholder=frame_placeholder,
        status_placeholder=status_placeholder,
        progress_placeholder=progress_placeholder,
        delay_seconds=delay_seconds,
    )
    st.session_state.completed_results[algorithm_name] = result
    st.session_state.last_algorithm = algorithm_name
    return result


def show_result_metrics(result) -> None:
    st.markdown(f"### {result['algorithm']} result")
    first, second, third = st.columns(3)
    first.metric("Route found", "YES" if result["route_found"] else "NO")
    second.metric("Destination", "Central stairs" if result["destination_type"] == "central_stairs" else "Emergency exit" if result["route_found"] else "—")
    third.metric("Route cost", result["route_cost"] if result["route_cost"] is not None else "—")

    fourth, fifth, sixth = st.columns(3)
    fourth.metric("Path steps", result["path_steps"])
    fifth.metric("Nodes explored", result["nodes_explored"])
    sixth.metric("Execution", f"{result['execution_ms']:.4f} ms")

    if result["fallback_used"]:
        st.warning("Emergency exits are unreachable. Central-stairs fallback activated.")
    if result["risk_level"] == "risky":
        st.warning("RISKY ROUTE · " + result["message"])
    elif result["route_found"]:
        st.success("SAFE (MODEL) · No smoke/crowd or elevated-cost cells on this route.")
    else:
        st.error(result["message"])
    if result["path"]:
        st.write(f"Selected destination: **{result['selected_destination']}**")
        if result["destination_type"] == "central_stairs":
            st.caption("This route reaches the staircase on this floor; onward evacuation is not modelled.")
        with st.expander("Route coordinates", expanded=False):
            st.code(" → ".join(str(node) for node in result["path"]))
    with st.expander("Search stages", expanded=False):
        for stage in result["stages"]:
            label = "Emergency exits" if stage["phase"] == "emergency_exits" else "Central stairs"
            outcome = "route found" if stage["route_found"] else "no reachable target"
            st.write(f"**{label}**: {outcome} · {stage['nodes_explored']} expanded · {stage['execution_ms']:.4f} ms")


def main() -> None:
    st.set_page_config(
        page_title="Campus Emergency Evacuation Planner",
        page_icon="🚨",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.markdown(APP_CSS, unsafe_allow_html=True)
    st.markdown(
        """
        <div class="hero">
            <h1>Campus Emergency Evacuation Route Planner</h1>
            <p>Week 3 · emergency exits first · central-stairs fallback · hazard-aware route status</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    scenarios = load_scenarios()
    locations = load_locations()

    with st.sidebar:
        st.header("Evacuation Controls")
        scenario_name = st.selectbox("Emergency scenario", list(scenarios))
        occupied_cells = {
            tuple(position)
            for label in ("crowd", "smoke", "fire", "blocked")
            for position in scenarios[scenario_name].get(label, [])
        }
        available_locations = [name for name, position in locations.items() if position not in occupied_cells]
        if not available_locations:
            st.error("No clear named starting location is available in this scenario.")
            st.stop()
        location_name = st.selectbox("Starting location", available_locations)
        excluded = [name for name in locations if name not in available_locations]
        if excluded:
            st.caption("Unavailable starting locations in this scenario: " + ", ".join(excluded))
        selected_algorithm = st.selectbox("Algorithm", list(ALGORITHMS))
        animation_speed = st.select_slider(
            "Animation speed",
            options=["Slow", "Normal", "Fast", "Instant"],
            value="Normal",
        )

        with st.expander("Custom hazards"):
            extra_crowd_raw = st.text_input("Crowd cells", placeholder="3,2; 4,3")
            extra_smoke_raw = st.text_input("Smoke cells", placeholder="0,2; 0,3")
            extra_fire_raw = st.text_input("Fire cells", placeholder="0,3")
            extra_blocked_raw = st.text_input("Blocked cells", placeholder="0,5; 5,5")
            st.caption("Format: row,column. Separate multiple cells with semicolons.")
            st.caption("Emergency exits and central stairs may be fire/blocked. The starting cell must remain clear.")

        run_selected = st.button(
            "▶ Run Selected Algorithm",
            type="primary",
            use_container_width=True,
        )
        run_remaining = st.button(
            "Run Remaining for Comparison",
            use_container_width=True,
        )
        reset_results = st.button("Reset Current Results", use_container_width=True)

        st.divider()
        st.markdown("**Movement model**")
        st.caption("Normal = 1 · Crowd = 3 · Smoke = 8 · Fire/Wall = blocked")
        st.markdown("**Fallback policy**")
        st.caption("Use an emergency exit if reachable. Reveal central stairs only when all exit routes fail.")

    delay_lookup = {"Slow": 0.22, "Normal": 0.11, "Fast": 0.045, "Instant": 0.0}
    delay_seconds = delay_lookup[animation_speed]

    key = scenario_signature(
        scenario_name, location_name, extra_crowd_raw, extra_smoke_raw,
        extra_fire_raw, extra_blocked_raw,
    )
    reset_for_scenario(key)
    try:
        grid = build_grid(
            scenario_name,
            locations[location_name],
            extra_crowd=parse_coordinates(extra_crowd_raw),
            extra_smoke=parse_coordinates(extra_smoke_raw),
            extra_fire=parse_coordinates(extra_fire_raw),
            extra_blocked=parse_coordinates(extra_blocked_raw),
        )
    except ValueError as error:
        st.error(str(error))
        st.stop()

    if reset_results:
        st.session_state.completed_results = {}
        st.session_state.last_algorithm = None

    completed = st.session_state.completed_results
    completed_count = len(completed)
    total_algorithms = len(ALGORITHMS)

    progress_left, progress_right = st.columns([3, 1])
    with progress_left:
        st.markdown('<div class="section-title">Experiment progress</div>', unsafe_allow_html=True)
        st.progress(completed_count / total_algorithms)
        if completed:
            chips = "".join(
                f'<span class="status-chip">✓ {name}</span>' for name in ALGORITHMS if name in completed
            )
            st.markdown(chips, unsafe_allow_html=True)
        else:
            st.caption("Run algorithms individually or use Run Remaining for Comparison.")
    with progress_right:
        st.metric("Algorithms completed", f"{completed_count}/{total_algorithms}")

    map_col, info_col = st.columns([1.5, 1], gap="large")
    with map_col:
        frame_placeholder = st.empty()
        status_placeholder = st.empty()
        progress_placeholder = st.empty()

    execution_finished = False
    if run_selected:
        execute_with_animation(
            selected_algorithm,
            grid,
            frame_placeholder=frame_placeholder,
            status_placeholder=status_placeholder,
            progress_placeholder=progress_placeholder,
            delay_seconds=delay_seconds,
        )
        execution_finished = True
    elif run_remaining:
        missing = [name for name in ALGORITHMS if name not in st.session_state.completed_results]
        if not missing:
            status_placeholder.success("All algorithms are already complete for this scenario.")
        else:
            batch_delay = max(delay_seconds * 0.55, 0.025) if delay_seconds else 0.0
            for index, algorithm_name in enumerate(missing, start=1):
                status_placeholder.info(
                    f"Comparison run {index}/{len(missing)} · starting {algorithm_name}"
                )
                execute_with_animation(
                    algorithm_name,
                    grid,
                    frame_placeholder=frame_placeholder,
                    status_placeholder=status_placeholder,
                    progress_placeholder=progress_placeholder,
                    delay_seconds=batch_delay,
                )
            execution_finished = True

    # Refresh once after the animation so progress cards/comparison use the newly stored results.
    if execution_finished:
        st.rerun()

    completed = st.session_state.completed_results
    result_to_show = completed.get(selected_algorithm)
    if result_to_show is None and st.session_state.last_algorithm:
        result_to_show = completed.get(st.session_state.last_algorithm)

    if result_to_show:
        final_fig = draw_grid(
            grid,
            path=result_to_show["path"],
            explored=result_to_show["stages"][-1].get("exploration_order", []),
            traveler=result_to_show["selected_destination"] if result_to_show["route_found"] else None,
            stairs_visible=result_to_show["stairs_visible"],
            risk_level=result_to_show["risk_level"],
            title=f"{result_to_show['algorithm']} · {'Central stairs fallback' if result_to_show['fallback_used'] else 'Emergency exit route'}",
        )
    else:
        final_fig = draw_grid(grid, title="Campus map · Ready to simulate")
    frame_placeholder.pyplot(final_fig, use_container_width=True, clear_figure=True)
    plt.close(final_fig)

    with info_col:
        st.markdown("### Live simulation")
        st.caption(
            "Blue cells show nodes already explored. The yellow outline is the current expansion. "
            "If exit search fails, CS appears and the same algorithm searches for central stairs. "
            "Movement starts only after planning. Orange routes contain modelled hazards."
        )
        if result_to_show:
            show_result_metrics(result_to_show)
        else:
            st.info("Choose an algorithm and click Run Selected Algorithm to start the live search.")

        st.markdown("#### Scenario")
        st.write(f"**{scenario_name}** · start: **{location_name} {grid.start}**")
        exit_summary = ", ".join(
            f"E{index} {exit_}" + (" [FIRE/BLOCKED]" if grid.is_blocked(exit_) else "")
            for index, exit_ in enumerate(grid.exits, start=1)
        )
        st.write(f"Emergency exits: **{exit_summary}**")
        if result_to_show and result_to_show["stairs_visible"]:
            st.write(f"Central stairs: **{grid.central_stairs}** · fallback active")
        st.caption("Academic simulation only; this synthetic map is not a certified emergency-navigation system.")

    st.divider()
    st.markdown("## Algorithm Comparison")

    completed = st.session_state.completed_results
    if len(completed) < total_algorithms:
        remaining = [name for name in ALGORITHMS if name not in completed]
        st.info(
            "Comparison is intentionally locked until every algorithm has completed on the same scenario. "
            f"Remaining: {', '.join(remaining)}."
        )
        st.progress(len(completed) / total_algorithms)
    else:
        ordered_results = [completed[name] for name in ALGORITHMS]
        table = results_dataframe(ordered_results)
        st.success("All five algorithms completed. Comparison results are now available.")
        st.dataframe(table, use_container_width=True, hide_index=True)

        chart_left, chart_right = st.columns(2, gap="large")
        with chart_left:
            st.markdown("#### Route cost")
            routes = table[table["Route Found"] == "Yes"]
            if routes.empty:
                st.info("No traversable routes; route cost is unavailable.")
            else:
                st.bar_chart(routes.set_index("Algorithm")[["Route Cost"]])
        with chart_right:
            st.markdown("#### Search effort")
            st.bar_chart(table.set_index("Algorithm")[["Nodes Explored"]].fillna(0))

        st.download_button(
            "Download comparison CSV",
            data=table.to_csv(index=False).encode("utf-8"),
            file_name="evacuation_algorithm_comparison.csv",
            mime="text/csv",
            use_container_width=True,
        )


if __name__ == "__main__":
    main()
