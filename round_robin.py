# =============================================================================
# round_robin.py – Round Robin (RR) & Dynamic Round Robin Scheduling
# =============================================================================
#
# HOW ROUND ROBIN WORKS
# ──────────────────────
# • Each process is given a fixed time slice called the TIME QUANTUM (TQ).
# • If a process does not finish within its quantum, it is preempted and
#   placed at the back of the ready queue.
# • New arrivals are added to the queue in the order they arrive.
# • This gives every process a fair share of the CPU — ideal for
#   time-sharing / interactive systems.
#
# DYNAMIC ROUND ROBIN
# ─────────────────────
# • The time quantum is set to the AVERAGE BURST TIME of all processes
#   (rounded to the nearest integer, minimum 1).
# • This adapts the quantum to the actual workload, potentially reducing
#   unnecessary context switches for short jobs while still being fair.
#
# QUEUE MANAGEMENT DETAIL
# ───────────────────────
# When a process is preempted:
#   1. Any NEW arrivals (arrival ≤ current_time, not yet enqueued) join first.
#   2. The preempted process then joins at the back.
# This matches the behaviour expected in standard exam problems.
#
# COMPLEXITY
# ──────────
# Time  : O(n × max_burst / quantum)   in the worst case
# Space : O(n)
# =============================================================================

import copy
from collections import deque

def run_round_robin(processes: list[dict],
                    quantum: int) -> tuple[list[dict], dict, list[tuple]]:
    """
    Simulate Round Robin scheduling.

    Parameters
    ----------
    processes : list[dict]
        Each dict: { 'pid', 'arrival', 'burst', 'priority' }
    quantum   : int
        Time slice (≥ 1).

    Returns
    -------
    results  : list[dict]   – per-process metrics
    metrics  : dict         – avg_wt, avg_tat, cpu_util
    gantt    : list[tuple]  – (pid, start, end) segments
    """
    # ── 1. Prepare ────────────────────────────────────────────────────────────
    # remaining_burst tracks how much CPU time each process still needs
    procs = copy.deepcopy(processes)
    procs.sort(key=lambda p: (p['arrival'], p['pid']))   # sort by arrival

    remaining_burst = {p['pid']: p['burst'] for p in procs}
    arrival_map     = {p['pid']: p['arrival'] for p in procs}
    original_burst  = {p['pid']: p['burst']  for p in procs}

    total_burst  = sum(p['burst'] for p in procs)
    n            = len(procs)
    completed    = {}    # pid → completion time
    gantt        = []

    # ── 2. Initialise queue with processes that arrive at time 0 ─────────────
    ready_queue   = deque()
    enqueued      = set()
    not_yet_added = list(procs)   # processes not yet put in the ready queue

    current_time = 0

    # Add all processes with arrival == 0
    for p in not_yet_added[:]:
        if p['arrival'] <= current_time:
            ready_queue.append(p['pid'])
            enqueued.add(p['pid'])
            not_yet_added.remove(p)

    # If nothing is ready yet, jump to the first arrival
    if not ready_queue and not_yet_added:
        current_time = not_yet_added[0]['arrival']
        for p in not_yet_added[:]:
            if p['arrival'] <= current_time:
                ready_queue.append(p['pid'])
                enqueued.add(p['pid'])
                not_yet_added.remove(p)

    # ── 3. Main scheduling loop ───────────────────────────────────────────────
    while ready_queue or not_yet_added:
        if not ready_queue:
            # CPU idle – jump to next arrival
            current_time = not_yet_added[0]['arrival']
            for p in not_yet_added[:]:
                if p['arrival'] <= current_time:
                    ready_queue.append(p['pid'])
                    enqueued.add(p['pid'])
                    not_yet_added.remove(p)

        pid = ready_queue.popleft()

        # How long does this process run this slice?
        run_time = min(quantum, remaining_burst[pid])
        start    = current_time
        end      = current_time + run_time
        gantt.append((pid, start, end))

        current_time        = end
        remaining_burst[pid] -= run_time

        # ── Enqueue newly arrived processes BEFORE re-queuing the preempted ──
        for p in not_yet_added[:]:
            if p['arrival'] <= current_time:
                ready_queue.append(p['pid'])
                enqueued.add(p['pid'])
                not_yet_added.remove(p)

        if remaining_burst[pid] == 0:
            # Process finished
            completed[pid] = current_time
        else:
            # Process was preempted → go to back of queue
            ready_queue.append(pid)

    # ── 4. Compute per-process metrics ────────────────────────────────────────
    results = []
    for pid, ct in completed.items():
        tat = ct - arrival_map[pid]
        wt  = tat - original_burst[pid]
        results.append({
            'pid'       : pid,
            'arrival'   : arrival_map[pid],
            'burst'     : original_burst[pid],
            'completion': ct,
            'tat'       : tat,
            'wt'        : wt,
        })

    # ── 5. Aggregate metrics ──────────────────────────────────────────────────
    avg_wt   = sum(r['wt']  for r in results) / n
    avg_tat  = sum(r['tat'] for r in results) / n
    makespan = max(r['completion'] for r in results) - min(arrival_map.values())
    cpu_util = (total_burst / makespan * 100) if makespan > 0 else 100.0

    metrics = {
        'avg_wt'  : avg_wt,
        'avg_tat' : avg_tat,
        'cpu_util': cpu_util,
    }

    return results, metrics, gantt


def run_dynamic_rr(processes: list[dict]) -> tuple[list[dict], dict, list[tuple], int]:
    """
    Run Round Robin with Dynamic Quantum = round(average burst time).

    Returns the same as run_round_robin plus the computed quantum.
    """
    n_procs  = len(processes)
    avg_burst = sum(p['burst'] for p in processes) / n_procs
    dynamic_q = max(1, round(avg_burst))

    results, metrics, gantt = run_round_robin(processes, dynamic_q)
    return results, metrics, gantt, dynamic_q
