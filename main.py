#!/usr/bin/env python3
# =============================================================================
# main.py – CPU Scheduling Algorithm Simulator
# =============================================================================
#
#  ██████╗██████╗ ██╗   ██╗    ███████╗ ██████╗██╗  ██╗███████╗██████╗
# ██╔════╝██╔══██╗██║   ██║    ██╔════╝██╔════╝██║  ██║██╔════╝██╔══██╗
# ██║     ██████╔╝██║   ██║    ███████╗██║     ███████║█████╗  ██║  ██║
# ██║     ██╔═══╝ ██║   ██║    ╚════██║██║     ██╔══██║██╔══╝  ██║  ██║
# ╚██████╗██║     ╚██████╔╝    ███████║╚██████╗██║  ██║███████╗██████╔╝
#  ╚═════╝╚═╝      ╚═════╝     ╚══════╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚═════╝
#
#  SCHEDULING SIMULATOR  –  v1.0  –  College Research Project Edition
# =============================================================================
#
# Simulates and compares:
#   1. FCFS           – First Come First Serve
#   2. SJF            – Shortest Job First (Non-Preemptive)
#   3. Round Robin    – with user-specified quantum
#   4. Dynamic RR     – quantum = average burst time
#   5. Priority       – Non-Preemptive (lower number = higher priority)
#
# Output:
#   • Per-algorithm result tables
#   • Gantt charts  (PNG)
#   • Comparison table + bar charts (PNG)
#   • CSV export
#   • Analysis / recommendations
# =============================================================================

import sys
import os

# ── Local module imports ───────────────────────────────────────────────────────
from utils       import (collect_processes, get_time_quantum,
                          display_results, draw_gantt,
                          display_comparison, plot_comparison,
                          export_csv, print_analysis, print_formulas,
                          header, separator, subheader, TERM_WIDTH)
from fcfs        import run_fcfs
from sjf         import run_sjf
from round_robin import run_round_robin, run_dynamic_rr
from priority    import run_priority


# ──────────────────────────────────────────────────────────────────────────────
# WELCOME BANNER
# ──────────────────────────────────────────────────────────────────────────────

def print_banner():
    """Display the welcome banner."""
    print()
    print("═" * TERM_WIDTH)
    print("  CPU SCHEDULING ALGORITHM SIMULATOR".center(TERM_WIDTH))
    print("  For Academic / Research Use".center(TERM_WIDTH))
    print("═" * TERM_WIDTH)
    print()
    print("  Algorithms : FCFS  │  SJF  │  Round Robin  │  Dynamic RR  │  Priority")
    print("  Output     : Tables, Gantt Charts, Comparison Charts, CSV Export")
    print()
    separator()


# ──────────────────────────────────────────────────────────────────────────────
# MAIN ORCHESTRATOR
# ──────────────────────────────────────────────────────────────────────────────

def main():
    print_banner()

    # ── Step 1 : Collect process data from the user ──────────────────────────
    processes = collect_processes()

    # ── Step 2 : Ask for Round Robin quantum ─────────────────────────────────
    avg_burst         = sum(p['burst'] for p in processes) / len(processes)
    manual_q, dyn_q   = get_time_quantum(avg_burst)
    print()

    # ── Step 3 : Print formula reference ─────────────────────────────────────
    print_formulas()

    # ── Step 4 : Run all algorithms ───────────────────────────────────────────
    print()
    header("RUNNING ALL ALGORITHMS …")
    print()

    # FCFS
    fcfs_results, fcfs_metrics, fcfs_gantt = run_fcfs(processes)
    print("  ✔  FCFS          done")

    # SJF
    sjf_results, sjf_metrics, sjf_gantt = run_sjf(processes)
    print("  ✔  SJF           done")

    # Round Robin (manual quantum)
    rr_results, rr_metrics, rr_gantt = run_round_robin(processes, manual_q)
    print(f"  ✔  Round Robin   done  (quantum = {manual_q})")

    # Dynamic Round Robin
    drr_results, drr_metrics, drr_gantt, dyn_q_used = run_dynamic_rr(processes)
    print(f"  ✔  Dynamic RR    done  (quantum = {dyn_q_used})")

    # Priority
    pri_results, pri_metrics, pri_gantt = run_priority(processes)
    print("  ✔  Priority      done")

    separator()
    print()

    # ── Step 5 : Display per-algorithm results ────────────────────────────────
    display_results("FCFS – First Come First Serve",   fcfs_results, fcfs_metrics)
    print()
    display_results("SJF – Shortest Job First",         sjf_results,  sjf_metrics)
    print()
    display_results(f"Round Robin (Quantum = {manual_q})", rr_results, rr_metrics)
    print()
    display_results(f"Dynamic Round Robin (Quantum = {dyn_q_used})", drr_results, drr_metrics)
    print()
    display_results("Priority Scheduling",              pri_results,  pri_metrics)
    print()

    # ── Step 6 : Build Gantt charts ───────────────────────────────────────────
    header("GENERATING GANTT CHARTS …")
    total_time = max(
        max(e for _, _, e in fcfs_gantt),
        max(e for _, _, e in sjf_gantt),
        max(e for _, _, e in rr_gantt),
        max(e for _, _, e in drr_gantt),
        max(e for _, _, e in pri_gantt),
    )

    draw_gantt("FCFS",                  fcfs_gantt, total_time, "gantt_FCFS.png")
    draw_gantt("SJF",                   sjf_gantt,  total_time, "gantt_SJF.png")
    draw_gantt(f"Round Robin Q={manual_q}", rr_gantt, total_time, "gantt_RR.png")
    draw_gantt(f"Dynamic RR Q={dyn_q_used}", drr_gantt, total_time, "gantt_DynamicRR.png")
    draw_gantt("Priority",              pri_gantt,  total_time, "gantt_Priority.png")
    print()

    # ── Step 7 : Comparison table ─────────────────────────────────────────────
    summary = [
        {'algorithm': 'FCFS',                    **fcfs_metrics},
        {'algorithm': 'SJF',                     **sjf_metrics},
        {'algorithm': f'RR (Q={manual_q})',       **rr_metrics},
        {'algorithm': f'Dyn-RR (Q={dyn_q_used})', **drr_metrics},
        {'algorithm': 'Priority',                 **pri_metrics},
    ]
    display_comparison(summary)
    print()

    # ── Step 8 : Comparison bar charts ───────────────────────────────────────
    header("GENERATING COMPARISON CHARTS …")
    plot_comparison(summary, "comparison_charts.png")
    print()

    # ── Step 9 : Export CSV ───────────────────────────────────────────────────
    header("EXPORTING RESULTS TO CSV …")
    all_results = {
        'FCFS'                       : fcfs_results,
        'SJF'                        : sjf_results,
        f'Round Robin Q={manual_q}'  : rr_results,
        f'Dynamic RR Q={dyn_q_used}' : drr_results,
        'Priority'                   : pri_results,
    }
    export_csv(all_results, summary, "scheduling_results.csv")
    print()

    # ── Step 10 : Analysis & recommendations ─────────────────────────────────
    print_analysis(summary)

    # ── Step 11 : RR vs Dynamic RR focused comparison ────────────────────────
    header("ROUND ROBIN vs DYNAMIC ROUND ROBIN")
    print(f"  Manual Quantum   : {manual_q}  →  Avg WT = {rr_metrics['avg_wt']:.2f} ms"
          f"  |  Avg TAT = {rr_metrics['avg_tat']:.2f} ms"
          f"  |  CPU = {rr_metrics['cpu_util']:.2f}%")
    print(f"  Dynamic Quantum  : {dyn_q_used}  →  Avg WT = {drr_metrics['avg_wt']:.2f} ms"
          f"  |  Avg TAT = {drr_metrics['avg_tat']:.2f} ms"
          f"  |  CPU = {drr_metrics['cpu_util']:.2f}%")
    print()
    if drr_metrics['avg_wt'] < rr_metrics['avg_wt']:
        print("  💡  Dynamic RR produced a LOWER average waiting time for this workload.")
    elif drr_metrics['avg_wt'] > rr_metrics['avg_wt']:
        print("  💡  Manual RR produced a LOWER average waiting time for this workload.")
    else:
        print("  💡  Both RR variants produced identical average waiting times.")
    separator()

    # ── Done ──────────────────────────────────────────────────────────────────
    print()
    print("  ✅  Simulation complete!  All files saved in the current directory.")
    print()
    print("  Generated files:")
    files = [
        "gantt_FCFS.png", "gantt_SJF.png", "gantt_RR.png",
        "gantt_DynamicRR.png", "gantt_Priority.png",
        "comparison_charts.png", "scheduling_results.csv",
    ]
    for f in files:
        status = "✔" if os.path.exists(f) else "✘"
        print(f"    {status}  {f}")
    print()
    separator()


# ──────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n  ⚠  Simulation interrupted by user.")
        sys.exit(0)
    except Exception as exc:                        # pragma: no cover
        print(f"\n  ✘  Unexpected error: {exc}")
        raise
