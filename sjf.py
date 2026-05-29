# =============================================================================
# sjf.py – Shortest Job First (SJF) Non-Preemptive Scheduling Algorithm
# =============================================================================
#
# HOW IT WORKS
# ─────────────
# • At each scheduling decision point the CPU picks the READY process with
#   the shortest remaining burst time (non-preemptive → once a process
#   starts, it runs to completion).
# • "Ready" means: process has arrived (arrival ≤ current_time).
# • Tie-break: if two processes share the same burst, pick the one with the
#   earlier arrival; if still tied, pick alphabetically by PID.
#
# ADVANTAGE
# ─────────
# SJF gives the theoretically minimum average waiting time for a given set
# of processes (proven optimal for non-preemptive, non-online scheduling).
#
# DISADVANTAGE
# ────────────
# • Starvation: long processes may never get the CPU if short ones keep
#   arriving.
# • Requires knowing burst times in advance (rarely possible in practice).
#
# COMPLEXITY
# ──────────
# Time  : O(n²)  – inner loop scans the ready queue at each step
# Space : O(n)
# =============================================================================

import copy

def run_sjf(processes: list[dict]) -> tuple[list[dict], dict, list[tuple]]:
    """
    Simulate Shortest Job First (Non-Preemptive) scheduling.

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
    # ── 1. Work on a deep copy so the caller's data is unchanged ─────────────
    remaining   = copy.deepcopy(processes)
    completed   = []
    gantt       = []
    current_time = 0
    total_burst  = sum(p['burst'] for p in processes)

    # ── 2. Main scheduling loop ──────────────────────────────────────────────
    while remaining:
        # Find all processes that have arrived by current_time
        ready = [p for p in remaining if p['arrival'] <= current_time]

        if not ready:
            # CPU is idle — jump to the next arriving process
            current_time = min(p['arrival'] for p in remaining)
            continue

        # ── Select the shortest job (tie-break: arrival, then pid) ──────────
        chosen = min(ready, key=lambda p: (p['burst'], p['arrival'], p['pid']))
        remaining.remove(chosen)

        start_time = current_time
        end_time   = current_time + chosen['burst']

        # Record Gantt segment
        gantt.append((chosen['pid'], start_time, end_time))

        # ── Compute metrics ──────────────────────────────────────────────────
        ct  = end_time
        tat = ct - chosen['arrival']
        wt  = tat - chosen['burst']

        completed.append({
            'pid'       : chosen['pid'],
            'arrival'   : chosen['arrival'],
            'burst'     : chosen['burst'],
            'completion': ct,
            'tat'       : tat,
            'wt'        : wt,
        })

        current_time = end_time

    # ── 3. Aggregate metrics ─────────────────────────────────────────────────
    n        = len(completed)
    avg_wt   = sum(r['wt']  for r in completed) / n
    avg_tat  = sum(r['tat'] for r in completed) / n
    makespan = current_time - min(p['arrival'] for p in processes)
    cpu_util = (total_burst / makespan * 100) if makespan > 0 else 100.0

    metrics = {
        'avg_wt'  : avg_wt,
        'avg_tat' : avg_tat,
        'cpu_util': cpu_util,
    }

    return completed, metrics, gantt
