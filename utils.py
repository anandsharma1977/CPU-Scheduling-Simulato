# =============================================================================
# utils.py - Utility Functions for CPU Scheduling Simulator
# =============================================================================
# This module provides:
#   - Process input collection
#   - Table display using pandas
#   - Gantt chart rendering using matplotlib
#   - Comparison chart generation
#   - CSV export
#   - Analysis / recommendation engine
# =============================================================================

import pandas as pd
import matplotlib
matplotlib.use('Agg')          # Use non-interactive backend (safe for all OSes)
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import csv
import os
import sys

# ── Terminal width helper ──────────────────────────────────────────────────────
TERM_WIDTH = 78

def separator(char="═", width=TERM_WIDTH):
    """Print a full-width separator line."""
    print(char * width)

def header(title: str, char="═"):
    """Print a centred section header."""
    separator(char)
    print(f"  {title}")
    separator(char)

def subheader(title: str):
    """Print a lighter sub-section header."""
    separator("─")
    print(f"  {title}")
    separator("─")

# ── Process input ──────────────────────────────────────────────────────────────

def get_int(prompt: str, min_val: int = 0, max_val: int = 9999) -> int:
    """
    Prompt the user for an integer, with validation.
    Keeps asking until a valid value within [min_val, max_val] is entered.
    """
    while True:
        try:
            val = int(input(prompt).strip())
            if min_val <= val <= max_val:
                return val
            print(f"  ⚠  Please enter a value between {min_val} and {max_val}.")
        except ValueError:
            print("  ⚠  Invalid input. Please enter a whole number.")

def collect_processes() -> list[dict]:
    """
    Interactively collect process data from the user.

    Each process is represented as a dictionary:
        {
            'pid'      : str   – Process ID (e.g. "P1")
            'arrival'  : int   – Arrival time (≥ 0)
            'burst'    : int   – CPU burst time (≥ 1)
            'priority' : int   – Priority (lower number = higher priority)
        }

    Returns a list of such dictionaries.
    """
    header("PROCESS INPUT")
    n = get_int("  Enter number of processes (1–20): ", min_val=1, max_val=20)
    print()

    processes = []
    for i in range(n):
        subheader(f"Process {i + 1} of {n}")
        pid      = input(f"  Process ID   [default: P{i+1}]: ").strip() or f"P{i+1}"
        arrival  = get_int("  Arrival Time [≥ 0]           : ", min_val=0)
        burst    = get_int("  Burst Time   [≥ 1]           : ", min_val=1)
        priority = get_int("  Priority     [1=highest]     : ", min_val=1)
        processes.append({
            'pid'     : pid,
            'arrival' : arrival,
            'burst'   : burst,
            'priority': priority,
        })
        print()

    return processes

def get_time_quantum(avg_burst: float) -> tuple[int, int]:
    """
    Ask the user for a manual time quantum.
    Also compute the dynamic quantum (rounded average burst).

    Returns (manual_quantum, dynamic_quantum).
    """
    subheader("Round Robin – Time Quantum")
    dynamic = max(1, round(avg_burst))
    print(f"  Dynamic quantum (avg burst) = {dynamic}")
    manual = get_int("  Enter manual Time Quantum   [≥ 1]: ", min_val=1)
    return manual, dynamic

# ── Result display ─────────────────────────────────────────────────────────────

def display_results(algo_name: str, results: list[dict], metrics: dict):
    """
    Print a pandas table of per-process metrics + summary metrics.

    Parameters
    ----------
    algo_name : str
        Human-readable algorithm name.
    results   : list[dict]
        Each dict must contain: pid, arrival, burst, completion, tat, wt
    metrics   : dict
        Must contain: avg_wt, avg_tat, cpu_util
    """
    header(f"RESULTS  ──  {algo_name}")

    # Build DataFrame
    df = pd.DataFrame(results)[['pid','arrival','burst','completion','tat','wt']]
    df.columns = ['PID','Arrival','Burst','Completion','TAT','WT']
    df = df.sort_values('PID').reset_index(drop=True)

    # Pretty-print the table
    print(df.to_string(index=False))
    print()

    # Summary
    print(f"  {'Average Waiting Time':<30}: {metrics['avg_wt']:.2f}")
    print(f"  {'Average Turnaround Time':<30}: {metrics['avg_tat']:.2f}")
    print(f"  {'CPU Utilization':<30}: {metrics['cpu_util']:.2f}%")
    separator()

# ── Gantt chart ────────────────────────────────────────────────────────────────

# Colour palette – cycles automatically when there are many processes
_PALETTE = [
    "#4C72B0","#DD8452","#55A868","#C44E52","#8172B2",
    "#937860","#DA8BC3","#8C8C8C","#CCB974","#64B5CD",
]

def draw_gantt(algo_name: str, gantt: list[tuple], total_time: int,
               filename: str | None = None):
    """
    Draw and save a Gantt chart.

    Parameters
    ----------
    algo_name  : str
        Title shown above the chart.
    gantt      : list of (pid, start, end) tuples
        Execution segments in chronological order.
    total_time : int
        Maximum time axis value (usually last end time).
    filename   : str | None
        If provided, save to this path. Otherwise auto-generate.
    """
    if not gantt:
        print("  ⚠  No Gantt data available.")
        return

    # Assign a consistent colour per PID
    pids   = list(dict.fromkeys(p for p, _, _ in gantt))   # preserve order
    colour = {p: _PALETTE[i % len(_PALETTE)] for i, p in enumerate(pids)}

    fig, ax = plt.subplots(figsize=(max(10, total_time * 0.6), 2.8))
    y_bar   = 0.4    # vertical centre of the bar
    height  = 0.4

    for pid, start, end in gantt:
        ax.barh(y_bar, end - start, left=start, height=height,
                color=colour[pid], edgecolor='white', linewidth=0.8)
        mid = (start + end) / 2
        ax.text(mid, y_bar, pid, ha='center', va='center',
                fontsize=9, fontweight='bold', color='white')

    # Axis formatting
    ax.set_xlim(0, total_time)
    ax.set_ylim(0, 1)
    ax.set_xlabel("Time →", fontsize=10)
    ax.set_yticks([])
    ax.set_title(f"Gantt Chart  –  {algo_name}", fontsize=12, fontweight='bold', pad=10)

    # Tick marks at each segment boundary
    ticks = sorted(set(t for _, s, e in gantt for t in (s, e)))
    ax.set_xticks(ticks)
    ax.tick_params(axis='x', labelsize=8)

    # Legend
    patches = [mpatches.Patch(color=colour[p], label=p) for p in pids]
    ax.legend(handles=patches, loc='upper right', fontsize=8,
              framealpha=0.7, ncol=min(len(pids), 6))

    plt.tight_layout()

    # Save
    if filename is None:
        safe = algo_name.replace(" ", "_").replace("/", "_")
        filename = f"gantt_{safe}.png"
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  📊  Gantt chart saved  →  {filename}")

# ── Comparison table & charts ──────────────────────────────────────────────────

def display_comparison(summary: list[dict]):
    """
    Print a side-by-side comparison table for all algorithms.

    summary : list of dicts with keys: algorithm, avg_wt, avg_tat, cpu_util
    """
    header("ALGORITHM COMPARISON TABLE")
    df = pd.DataFrame(summary)
    df.columns = ['Algorithm', 'Avg WT', 'Avg TAT', 'CPU Util (%)']
    df['Avg WT']       = df['Avg WT'].map(lambda x: f"{x:.2f}")
    df['Avg TAT']      = df['Avg TAT'].map(lambda x: f"{x:.2f}")
    df['CPU Util (%)'] = df['CPU Util (%)'].map(lambda x: f"{x:.2f}")
    print(df.to_string(index=False))
    separator()

def plot_comparison(summary: list[dict], filename: str = "comparison_charts.png"):
    """
    Generate a 3-panel bar chart comparing algorithms on:
      – Average Waiting Time
      – Average Turnaround Time
      – CPU Utilization
    """
    algos    = [d['algorithm']  for d in summary]
    avg_wt   = [d['avg_wt']     for d in summary]
    avg_tat  = [d['avg_tat']    for d in summary]
    cpu_util = [d['cpu_util']   for d in summary]

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.suptitle("CPU Scheduling Algorithms – Performance Comparison",
                 fontsize=14, fontweight='bold', y=1.02)

    bars_cfg = [
        (axes[0], avg_wt,   "Average Waiting Time",     "#4C72B0"),
        (axes[1], avg_tat,  "Average Turnaround Time",  "#55A868"),
        (axes[2], cpu_util, "CPU Utilization (%)",       "#DD8452"),
    ]

    for ax, values, title, colour in bars_cfg:
        bars = ax.bar(algos, values, color=colour, edgecolor='white',
                      linewidth=0.8, width=0.5)
        ax.set_title(title, fontsize=11, fontweight='bold')
        ax.set_ylabel("Time (ms)" if "Time" in title else "%")
        ax.set_xticks(range(len(algos)))
        ax.set_xticklabels(algos, rotation=30, ha='right', fontsize=8)
        ax.yaxis.grid(True, linestyle='--', alpha=0.6)
        ax.set_axisbelow(True)
        # Label each bar
        for bar, val in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + max(values) * 0.02,
                    f"{val:.1f}", ha='center', va='bottom', fontsize=8)

    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  📊  Comparison chart saved  →  {filename}")

# ── CSV export ─────────────────────────────────────────────────────────────────

def export_csv(all_results: dict[str, list[dict]], summary: list[dict],
               filename: str = "scheduling_results.csv"):
    """
    Export per-process results for every algorithm + the comparison summary
    to a single CSV file.

    Parameters
    ----------
    all_results : dict  {algorithm_name: [result_dicts]}
    summary     : list  [{algorithm, avg_wt, avg_tat, cpu_util}]
    filename    : str   destination path
    """
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)

        # ── Per-algorithm detail ──
        for algo, results in all_results.items():
            writer.writerow([f"=== {algo} ==="])
            writer.writerow(['PID','Arrival','Burst','Completion','TAT','WT'])
            for r in results:
                writer.writerow([r['pid'], r['arrival'], r['burst'],
                                  r['completion'], r['tat'], r['wt']])
            writer.writerow([])   # blank separator

        # ── Summary ──
        writer.writerow(["=== COMPARISON SUMMARY ==="])
        writer.writerow(['Algorithm','Avg WT','Avg TAT','CPU Util (%)'])
        for row in summary:
            writer.writerow([row['algorithm'],
                              f"{row['avg_wt']:.2f}",
                              f"{row['avg_tat']:.2f}",
                              f"{row['cpu_util']:.2f}"])

    print(f"  💾  Results exported       →  {filename}")

# ── Analysis & recommendations ─────────────────────────────────────────────────

def print_analysis(summary: list[dict]):
    """
    Print human-readable insights based on the comparison summary.
    """
    header("ANALYSIS & RECOMMENDATIONS")

    best_wt   = min(summary, key=lambda x: x['avg_wt'])
    best_tat  = min(summary, key=lambda x: x['avg_tat'])
    best_cpu  = max(summary, key=lambda x: x['cpu_util'])

    print(f"  ✅  Lowest Average Waiting Time   → {best_wt['algorithm']}"
          f"  ({best_wt['avg_wt']:.2f} ms)")
    print(f"  ✅  Lowest Average Turnaround Time → {best_tat['algorithm']}"
          f"  ({best_tat['avg_tat']:.2f} ms)")
    print(f"  ✅  Best CPU Utilization           → {best_cpu['algorithm']}"
          f"  ({best_cpu['cpu_util']:.2f}%)")
    print()

    # Fixed recommendations
    print("  📌  SUITABILITY GUIDE")
    print("  ─────────────────────────────────────────────────────────────────")
    tips = [
        ("FCFS",             "Batch systems where simplicity matters more than speed."),
        ("SJF",              "Batch processing; optimal average WT but needs burst prediction."),
        ("Round Robin",      "Time-sharing & interactive systems (fair CPU distribution)."),
        ("Dynamic RR",       "Interactive systems where workload burst times vary widely."),
        ("Priority",         "Real-time / OS kernels needing process prioritisation."),
    ]
    for algo, tip in tips:
        print(f"  {'•'} {algo:<18}: {tip}")

    print()
    print("  ℹ   Note: No single algorithm is universally 'best' — the right")
    print("      choice depends on system goals (fairness vs throughput vs")
    print("      responsiveness) and workload characteristics.")
    separator()

# ── Formula reference ──────────────────────────────────────────────────────────

def print_formulas():
    """Print the scheduling metric formulas for student reference."""
    header("FORMULA REFERENCE")
    formulas = [
        ("Completion Time (CT)",    "Time at which the process finishes execution."),
        ("Turnaround Time (TAT)",   "CT  −  Arrival Time"),
        ("Waiting Time (WT)",       "TAT −  Burst Time"),
        ("Average WT",              "Σ WT  /  n"),
        ("Average TAT",             "Σ TAT /  n"),
        ("CPU Utilization",         "(Total Burst Time / Total Time) × 100%"),
        ("Dynamic Quantum (RR)",    "round( Σ Burst / n )  ──  average burst time"),
    ]
    for name, formula in formulas:
        print(f"  {name:<30}:  {formula}")
    separator()
