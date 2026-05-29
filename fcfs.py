# =============================================================================
# fcfs.py – First Come First Serve (FCFS) Scheduling Algorithm
# =============================================================================
#
# HOW IT WORKS
# ─────────────
# • Processes are executed in the order they arrive (non-preemptive).
# • If two processes arrive at the same time, the one with the lower PID
#   (alphabetical) is picked first — a common tie-breaking rule.
# • Simple to implement but can cause the "Convoy Effect": a long process
#   near the front of the queue delays all shorter ones behind it.
#
# COMPLEXITY
# ──────────
# Time  : O(n log n)  — due to the initial sort by arrival time
# Space : O(n)
# =============================================================================

import copy

def run_fcfs(processes: list[dict]) -> tuple[list[dict], dict, list[tuple]]:
    """
    Simulate First Come First Serve scheduling.

    Parameters
    ----------
    processes : list[dict]
        Each dict: { 'pid', 'arrival', 'burst', 'priority' }

    Returns
    -------
    results   : list[dict]   – per-process metrics
    metrics   : dict         – avg_wt, avg_tat, cpu_util
    gantt     : list[tuple]  – (pid, start, end) segments
    """
    # ── 1. Sort by arrival time (tie-break on pid) ──────────────────────────
    queue = sorted(copy.deepcopy(processes), key=lambda p: (p['arrival'], p['pid']))

    current_time = 0
    gantt        = []           # Gantt chart segments
    results      = []           # Completed process metrics
    total_burst  = sum(p['burst'] for p in queue)

    # ── 2. Execute each process in order ────────────────────────────────────
    for proc in queue:
        # If CPU is idle (current_time < arrival), jump forward
        if current_time < proc['arrival']:
            current_time = proc['arrival']

        start_time = current_time
        end_time   = current_time + proc['burst']

        # Record Gantt segment
        gantt.append((proc['pid'], start_time, end_time))

        # Calculate metrics
        # ─────────────────────────────────────────────────────
        # Completion Time (CT)  = time when process finishes
        # Turnaround Time (TAT) = CT - Arrival Time
        # Waiting Time (WT)     = TAT - Burst Time
        # ─────────────────────────────────────────────────────
        ct  = end_time
        tat = ct - proc['arrival']
        wt  = tat - proc['burst']

        results.append({
            'pid'       : proc['pid'],
            'arrival'   : proc['arrival'],
            'burst'     : proc['burst'],
            'completion': ct,
            'tat'       : tat,
            'wt'        : wt,
        })

        current_time = end_time   # advance clock

    # ── 3. Aggregate metrics ─────────────────────────────────────────────────
    n        = len(results)
    avg_wt   = sum(r['wt']  for r in results) / n
    avg_tat  = sum(r['tat'] for r in results) / n

    # CPU Utilization = (total burst time) / (makespan) × 100
    # Makespan = last completion time − earliest arrival time
    makespan = current_time - min(p['arrival'] for p in processes)
    cpu_util = (total_burst / makespan * 100) if makespan > 0 else 100.0

    metrics = {
        'avg_wt'  : avg_wt,
        'avg_tat' : avg_tat,
        'cpu_util': cpu_util,
    }

    return results, metrics, gantt
