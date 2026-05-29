# =============================================================================
# priority.py – Priority Scheduling (Non-Preemptive)
# =============================================================================
#
# HOW IT WORKS
# ─────────────
# • Each process is assigned a PRIORITY NUMBER.
# • Convention used here: LOWER number = HIGHER priority (1 is the highest).
#   This matches the convention used by most OS textbooks (UNIX nice values,
#   Windows thread priorities, etc.).
# • At each scheduling point the CPU picks the highest-priority process from
#   all READY processes (arrival ≤ current_time).
# • Non-preemptive: once chosen, the process runs to completion.
#
# TIE-BREAKING
# ─────────────
# If two processes have equal priority:
#   1. Earlier arrival time wins.
#   2. If still tied, lower PID (alphabetical) wins.
#
# STARVATION
# ───────────
# Low-priority processes may starve if high-priority ones keep arriving.
# The classic solution is "ageing" (gradually raise priority of waiting
# processes) — not implemented here for clarity, but noted for students.
#
# COMPLEXITY
# ──────────
# Time  : O(n²)  – inner scan at each scheduling decision
# Space : O(n)
# =============================================================================

import copy

def run_priority(processes: list[dict]) -> tuple[list[dict], dict, list[tuple]]:
    """
    Simulate Priority Scheduling (Non-Preemptive).

    Parameters
    ----------
    processes : list[dict]
        Each dict: { 'pid', 'arrival', 'burst', 'priority' }
        priority: int  (1 = highest priority)

    Returns
    -------
    results  : list[dict]   – per-process metrics
    metrics  : dict         – avg_wt, avg_tat, cpu_util
    gantt    : list[tuple]  – (pid, start, end) segments
    """
    # ── 1. Work on a deep copy ────────────────────────────────────────────────
    remaining    = copy.deepcopy(processes)
    completed    = []
    gantt        = []
    current_time = 0
    total_burst  = sum(p['burst'] for p in processes)

    # ── 2. Main scheduling loop ───────────────────────────────────────────────
    while remaining:
        # Collect all processes that have arrived
        ready = [p for p in remaining if p['arrival'] <= current_time]

        if not ready:
            # CPU idle — advance to next arrival
            current_time = min(p['arrival'] for p in remaining)
            continue

        # ── Select highest priority (lowest priority number) ─────────────────
        # Tie-break: earlier arrival, then alphabetical PID
        chosen = min(ready, key=lambda p: (p['priority'], p['arrival'], p['pid']))
        remaining.remove(chosen)

        start_time = current_time
        end_time   = current_time + chosen['burst']

        # Record Gantt segment
        gantt.append((chosen['pid'], start_time, end_time))

        # ── Compute metrics ───────────────────────────────────────────────────
        ct  = end_time
        tat = ct - chosen['arrival']
        wt  = tat - chosen['burst']

        completed.append({
            'pid'       : chosen['pid'],
            'arrival'   : chosen['arrival'],
            'burst'     : chosen['burst'],
            'priority'  : chosen['priority'],
            'completion': ct,
            'tat'       : tat,
            'wt'        : wt,
        })

        current_time = end_time

    # ── 3. Aggregate metrics ──────────────────────────────────────────────────
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
