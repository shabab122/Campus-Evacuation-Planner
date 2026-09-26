# Campus Emergency Evacuation Route Planner — Week 2

This Week-2 build extends the completed Week-1 project (grid map + A* + BFS + basic visualization) into a Streamlit-based interactive simulation.

## Week-2 scope

- Multiple exits and named starting locations
- Hazard-aware movement costs
  - Normal cell = 1
  - Crowd = 3
  - Smoke = 8
  - Fire and walls = blocked
- Algorithms: A*, BFS, DFS, Uniform Cost Search (UCS), Greedy Best First Search
- Live node-expansion animation for every algorithm
- Step-by-step evacuation movement after a route is found
- Per-algorithm metrics stored only after that algorithm actually runs
- Comparison table/charts locked until all five algorithms finish on the same scenario
- Pandas comparison DataFrame and CSV export
- Professional Streamlit dashboard and improved Matplotlib grid

## Important Week-2 behavior

The comparison is no longer precomputed when the page loads. Run algorithms one at a time with **Run Selected Algorithm**, or use **Run Remaining for Comparison**. The comparison section unlocks only when all five results exist for the current scenario.

Changing the scenario, starting location, or custom hazards creates a new experiment and resets the completed-algorithm results. This prevents results from different scenarios being mixed together.

## Run on Ubuntu

```bash
python3 -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest -q
python -m streamlit run app.py
```

Streamlit normally opens the app at `http://localhost:8501`.

## Live visualization

Each run has two visual phases:

1. **Search phase** — explored cells appear progressively, and the current expanded node is highlighted.
2. **Evacuation phase** — after the route is found, the route grows and an evacuee marker moves cell-by-cell to the selected exit.

Use the sidebar animation-speed control for Slow, Normal, or Fast playback.

## Project structure

```text
app.py
main.py
data/
  map.json
  scenarios.json
src/
  astar.py
  bfs.py
  cost.py
  dfs.py
  evaluation.py
  greedy.py
  grid.py
  heuristic.py
  scenarios.py
  ucs.py
  visualization.py
tests/
  test_grid_scenarios.py
  test_week2_algorithms.py
  test_live_visualization.py
```

## Validation

The current automated suite checks the map/scenario rules, weighted routing, all five algorithms, live exploration traces, and visualization layers.

```bash
python -m pytest -q
```

Current result: **6 tests passed**.

## Academic limitation

This is a synthetic AI-lab simulation. It is not a certified real-world emergency navigation or building-safety system.
