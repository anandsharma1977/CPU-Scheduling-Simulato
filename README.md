# CPU-Scheduling-Simulation
It clearly highlights the modular design, the advanced Dynamic Round Robin feature, and the visual plotting metrics which will make your project stand out immediately to anyone visiting your profile.
# Multi-Algorithm CPU Scheduling Simulator with Dynamic Optimization

A comprehensive, modular Python-based simulation tool designed to evaluate, analyze, and visualize core Operating System CPU scheduling algorithms. Built with an object-oriented approach, this project features interactive terminal inputs, automated performance metrics calculation, professional visual plots, and an advanced **Dynamic Round Robin** implementation.

This simulator serves as an excellent practical framework for academic research, operating system studies, and performance benchmarking.

---

## 🚀 Key Features

* **Comprehensive Algorithm Suite:** Simulates five distinct scheduling strategies:
  1. **First-Come, First-Served (FCFS)**
  2. **Shortest Job First (SJF)** *(Non-preemptive)*
  3. **Priority Scheduling** *(Non-preemptive)*
  4. **Standard Round Robin (RR)** *(User-defined Time Quantum)*
  5. **Dynamic Round Robin (DRR)** *(Adaptive tuning where $Time\ Quantum = Average\ Burst\ Time$)*
* **Automated OS Metrics:** Computes Completion Time (CT), Turnaround Time (TAT), Waiting Time (WT), and overall CPU Utilization percentage for every process.
* **Professional Gantt Charts:** Generates individual, color-coded timeline charts for each algorithm using `matplotlib`.
* **Side-by-Side Comparative Analysis:** Automatically builds performance comparison dataframes using `pandas` and exports a 3-panel bar chart evaluating Average WT, Average TAT, and CPU Efficiency.
* **Data Portability:** Seamlessly exports all simulated raw data and execution summaries into an external `.csv` file for external spreadsheet analysis.
* **Robust Error Handling:** Features complete input-validation loops to handle invalid or erratic data entry without system crashes.

---

## 📊 Analytical Evaluation Summary
The simulator compares performance metrics across all models, specifically isolating how an optimized, adaptive Time Quantum (Dynamic RR) performs against an arbitrary static quantum under varying workloads. 

### Metrics Formats Modeled:
$$\text{Turnaround Time (TAT)} = \text{Completion Time} - \text{Arrival Time}$$
$$\text{Waiting Time (WT)} = \text{Turnaround Time} - \text{Burst Time}$$

---

## 🛠️ Tech Stack & Dependencies

* **Language:** Python 3.x
* **Data Processing:** `pandas`
* **Data Visualization:** `matplotlib`

---

## 📂 Project Structure

```text
├── main.py            # System entry point, handles workflow & core orchestration
├── fcfs.py            # First-Come First-Served scheduling engine
├── sjf.py             # Shortest Job First scheduling engine
├── round_robin.py     # Standard and Dynamic Round Robin scheduling engines
├── priority.py        # Priority-based execution scheduling engine
├── utils.py           # Core utilities: input validation, chart generation, CSV exports
└── README.md          # Comprehensive documentation
