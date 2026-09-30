# Week 3 — Central-Stairs Fallback Integration

## Agreed scope

Deliver one feature: when no emergency exit is reachable, reveal the central staircase and rerun the selected search algorithm toward it. Report route risk, preserve fire/block barriers, and handle the case where stairs are also unreachable.

The implementation preserves all five algorithms and the existing Week-2 dashboard/comparison workflow. It does not introduce fire-spread simulation, new search algorithms, or multi-floor navigation.

## Implementation map

| Area | Files | What to review |
|---|---|---|
| Map and hazards | `data/map.json`, `data/scenarios.json`, `src/grid.py`, `src/scenarios.py` | Configurable CS coordinate; fire/blocks allowed on exits and stairs; invalid starts rejected |
| Destination policy | `src/routing.py`, `src/evaluation.py` | Emergency-exit priority; same algorithm for both stages; unchanged hazard map; real risk classification |
| UI and animation | `app.py`, `src/visualization.py` | CS hidden during primary search; revealed during fallback; smoky/fire destinations remain visibly hazardous |
| Validation and documentation | `tests/`, `README.md` | Correct routes and no-route results, state reset, comparison data, reproducible demo |

The search kernels (`astar.py`, `bfs.py`, `dfs.py`, `ucs.py`, `greedy.py`) are unchanged. The shared policy supplies a read-only view with the active target set; the actual floor map and emergency-exit metadata are preserved.

## Branch workflow

One feature branch is sufficient for the integrated change:

```text
feat/central-stairs-fallback → pull request → main
```

Before updating your local project, inspect its state and preserve any unfinished changes:

```bash
git status
git branch --show-current
```

If your working tree is clean and your local `main` is the agreed starting point:

```bash
git switch main
git pull --ff-only origin main
git switch -c feat/central-stairs-fallback
```

Then copy the updated project files into your existing repository, preserving that repository's `.git` directory and any work you still need. The distribution does not contain a `.git` directory or virtual environment. Do not delete the original repository or overwrite unfinished changes to import the ZIP.

Run the checks and inspect the patch before committing:

```bash
python -m pytest -q
git diff --stat
git diff
git status
```

Stage only the Week-3 files you intend to submit. For a clean Week-2 starting point, the changed and new paths are:

```bash
git add app.py main.py README.md WEEK3_TEAM_GUIDE.md .gitignore
git add src/grid.py src/scenarios.py src/routing.py src/evaluation.py src/visualization.py
git add data/map.json data/scenarios.json docs/images
git add tests/test_stairs_fallback.py tests/test_week3_app.py tests/test_week3_grid_validation.py tests/test_week3_visualization.py
git diff --cached --stat
git commit -m "feat: add central-stairs fallback for unreachable emergency exits"
git push -u origin feat/central-stairs-fallback
```

Open a pull request from that branch into `main`. A team leader can make the integration commit while other members review and test. Members need separate branches only for independent edits. Do not invent authorship, rewrite old commits, or create cosmetic commits merely to distribute activity.

## Suggested review participation

| Member | Useful review work |
|---|---|
| 1 | Check map/CS assumptions, hazard overlays, unavailable starting locations |
| 2 / team leader | Review fallback selection and A* / UCS cost agreement; integrate the feature |
| 3 | Verify BFS/DFS/Greedy behavior, route-risk reporting, comparison and CSV |
| 4 | Test animation, final result messages, scenario changes, reset behavior, and README steps |

These are proposed review responsibilities, not claims about work already completed by individual members.

## Demo acceptance flow

1. **Normal conditions → Room A → A***: exit route, no CS marker.
2. **All exit corridors blocked (stairs fallback)**: show primary search failure, CS appearing, second search, and movement to CS.
3. **Risky stairs fallback**: show orange route, smoke on CS, and an explicit risk warning.
4. **No traversable destination**: show fire on both exits and stairs; no traveler movement and no fabricated route.
5. **Run Remaining for Comparison**: all five results unlock comparison; CSV contains destination and risk fields.
6. Change the scenario or a custom hazard: prior experiment results reset.

The example staircase is `(2,3)`, not a verified physical UIU stair location. The simulation ends at the current floor's stairs; onward evacuation remains outside the implemented model.
