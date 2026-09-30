# Week 2 Team Development and Git Workflow — Revised Live Visualization Build

This plan keeps Week 2 limited to the current roadmap while correcting the visualization and experiment-flow problems found during testing.

All four members should work through separate branches and open pull requests to `main`. Do not force-push shared branches and do not push Week-2 feature work directly to `main`.

---

## Member 1 — Farnip: Map, hazards and multiple exits

**Branch:** `dev/farnip_week2_hazards`

### Owned files
- `data/map.json`
- `data/scenarios.json`
- `src/grid.py`
- `src/scenarios.py`
- `tests/test_grid_scenarios.py`

### Work
1. Upgrade the Week-1 map from one exit to multiple exits.
2. Add named starting locations.
3. Add crowd, smoke and fire hazards.
4. Keep movement rules: normal = 1, crowd = 3, smoke = 8, fire = blocked.
5. Validate invalid/out-of-map hazards and prevent hazards from replacing starts/exits/walls incorrectly.
6. Provide reusable scenario-building functions for all algorithms and the Streamlit UI.

### Commit
```bash
git commit -m "feat: add Week 2 hazards scenarios and multiple exits"
```

### Push commands
```bash
git switch main
git pull origin main
git switch -c dev/farnip_week2_hazards

git add data/map.json data/scenarios.json src/grid.py src/scenarios.py tests/test_grid_scenarios.py
git status
git commit -m "feat: add Week 2 hazards scenarios and multiple exits"
git push -u origin dev/farnip_week2_hazards
```

---

## Member 2 — Shabab: A* safe routing and live search trace

**Branch:** `dev/shabab_week2_astar`

### Owned files
- `src/heuristic.py`
- `src/astar.py`
- `src/cost.py`

### Work
1. Extend A* to search for any available exit.
2. Use minimum Manhattan distance to all exits as `h(n)`.
3. Include weighted hazard cost in `g(n)`.
4. Return path, total cost and explored-node count using the original compatible interface.
5. Add optional live-search tracing with `return_trace=True`.
6. Preserve the exact expansion order so Member 4 can animate the real A* search instead of showing a fake/static path.
7. Verify A* can choose a physically farther exit when the weighted route is safer.

### Commit
```bash
git commit -m "feat: add weighted A star routing with live search trace"
```

### Push commands
```bash
git switch main
git pull origin main
git switch -c dev/shabab_week2_astar

git add src/heuristic.py src/astar.py src/cost.py
git status
git commit -m "feat: add weighted A star routing with live search trace"
git push -u origin dev/shabab_week2_astar
```

---

## Member 3 — Sinan: Search algorithms, traces and comparison metrics

**Branch:** `dev/sinan_week2_algorithms`

### Owned files
- `src/bfs.py`
- `src/dfs.py`
- `src/ucs.py`
- `src/greedy.py`
- `src/evaluation.py`
- `tests/test_week2_algorithms.py`
- `tests/test_live_visualization.py`

### Work
1. Update BFS for multiple exits.
2. Add DFS, UCS and Greedy Best First Search.
3. Add optional exploration traces to every algorithm without breaking the normal return interfaces.
4. Normalize each run into route found, selected exit, path steps, route cost, nodes explored and execution time.
5. Return the exploration order only when the UI requests live tracing.
6. Build the Pandas comparison table from results that have actually been executed.
7. Add tests confirming trace length matches the explored-node count and routes end at a valid exit.

### Commit
```bash
git commit -m "feat: add traced search algorithms and comparison metrics"
```

### Push commands
```bash
git switch main
git pull origin main
git switch -c dev/sinan_week2_algorithms

git add src/bfs.py src/dfs.py src/ucs.py src/greedy.py src/evaluation.py tests/test_week2_algorithms.py tests/test_live_visualization.py
git status
git commit -m "feat: add traced search algorithms and comparison metrics"
git push -u origin dev/sinan_week2_algorithms
```

---

## Member 4 — Ome: Dynamic Streamlit simulation and professional UI

**Branch:** `dev/ome_week2_streamlit`

### Owned files
- `app.py`
- `src/visualization.py`
- `requirements.txt`
- `README.md`

### Work
1. Replace the old static/final-route-only behavior with actual live visualization.
2. Animate the algorithm expansion order node-by-node.
3. Highlight the currently expanded node.
4. After search completion, animate the evacuee moving along the discovered route.
5. Add Slow/Normal/Fast animation speed control.
6. Store each algorithm result in Streamlit session state only after that algorithm runs.
7. Reset experiment results when scenario/start/custom hazards change.
8. Keep algorithm comparison locked until all five algorithms have completed on the same experiment.
9. Add **Run Remaining for Comparison** for sequential completion of missing algorithms.
10. Improve the dashboard styling, metric cards, grid colors, map labels, legend, route line and result layout.
11. Keep Pandas table/chart/CSV comparison available only after completion.

### Commit
```bash
git commit -m "feat: build animated Streamlit evacuation dashboard"
```

### Push commands
```bash
git switch main
git pull origin main
git switch -c dev/ome_week2_streamlit

git add app.py src/visualization.py requirements.txt README.md
git status
git commit -m "feat: build animated Streamlit evacuation dashboard"
git push -u origin dev/ome_week2_streamlit
```

---

# Recommended pull-request merge order

1. **Member 1** — map/scenario contract
2. **Member 2** — A* safe routing + A* trace
3. **Member 3** — remaining algorithms + normalized trace/results
4. **Member 4** — Streamlit integration and visualization

Before merging a later PR, update that member's branch with the latest `main`:

```bash
git switch main
git pull origin main
git switch <member-branch>
git merge main
```

Resolve conflicts locally, rerun the tests, then push the branch.

---

# Final integration verification

After all four pull requests are merged:

```bash
git switch main
git pull origin main

python3 -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest -q
python -m streamlit run app.py
```

Expected automated result for this package:

```text
6 passed
```

## Manual UI acceptance checks

1. Opening the page must show the map but **must not precompute all algorithm comparisons**.
2. Click **Run Selected Algorithm**.
3. Nodes must appear progressively as they are explored; the current node must be highlighted.
4. After the algorithm finds an exit, the evacuee marker must move along the route step-by-step.
5. The completed-algorithm counter must increase only after a real run.
6. The comparison table must stay locked before all five algorithms finish.
7. Run the other algorithms manually or click **Run Remaining for Comparison**.
8. Only after `5/5` completes should the comparison table, charts and CSV download appear.
9. Change scenario/start/custom hazards. The comparison progress must reset to `0/5` so results from different experiments cannot be mixed.
10. For **Smoke near north exit**, verify weighted algorithms can avoid the expensive smoke route when a safer lower exit exists.
