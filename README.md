# RV32I Processor - ML-Guided Physical Design & Power Optimization

Project work under **Dr. Binod Kumar**, Department of Electronics Engineering, Indian Institute of Technology (IIT) Jodhpur.

## About the Project
When physical design tools like OpenROAD place logic gates on a chip, they only optimize to make wires as short as possible. They have no awareness of which gates switch together when real software runs. 

Because of this, gates that toggle heavily (like the ALU and the Program Counter registers) get placed right next to each other in tight clusters. When they all switch at the same time, they draw a sudden surge of current, causing localized overheating and supply voltage sags (IR drop).

In this project, I built an automated flow that:
1. Simulates an RV32I core running real instructions to capture switching activity.
2. Trains a Machine Learning model to identify which gates cause power hotspots.
3. Automatically generates placement padding rules (`set_placement_padding`) for OpenROAD to give those hot gates breathing room before clock tree synthesis and routing.
4. Completes the full silicon flow (Power Grid, Clock Tree, and Detailed Routing) down to a manufacturing GDSII file.

---

## What I Built & The Results

### 1. Processor RTL & Simulation
* Designed a synthesizable 32-bit single-cycle RV32I processor (`rtl/rv32i_core.v`) with PC, 32 registers (x0 hardwired to 0), instruction decoder, ALU, and RAM memory interface.
* Verified execution with an Icarus Verilog testbench running arithmetic and memory instructions (`ADDI`, `ADD`, `SUB`, `SW`, `LW`).
* Generated `wave.vcd` and parsed the activity with Python, proving that the Clock and Program Counter lines toggle the most heavily.

### 2. Logic Synthesis on SkyWater 130nm
* Synthesized the design into **6,579 physical gates** using Yosys:
  * **993 Register File flip-flops**
  * **30 Program Counter flip-flops**
  * **5,556 combinational logic gates** (AND, OR, MUX, XOR)
* Total standard cell area: **54,378 um²** (sequential flip-flops account for 47.08% of silicon area).

### 3. Machine Learning Hotspot Predictor
* Extracted cell features (fan-in, fan-out, cell type, and toggle counts) into `data/dataset.csv`.
* Trained a Random Forest classifier in `ml/train_model.py`:
  * Evaluated on **1,316 unseen test gates** and achieved **100% test accuracy**.
  * **Key Discovery:** Sequential flip-flops account for **83.29% of power hotspot risk**, while output fan-out load accounts for **10.59%**.
* Automatically generated `openroad/ml_padding.tcl` enforcing 2-site physical clearance (`-left 2 -right 2`) around all 1,023 high-activity flip-flops.

### 4. Physical Design in OpenROAD & Results
I ran OpenROAD on a 350um x 350um silicon die to compare the **Baseline Layout (Without ML)** against the **ML-Guided Layout (With ML)**:

| Metric | Without ML (Baseline) | With ML (Our Flow) | Result |
| :--- | :--- | :--- | :--- |
| **Peak Power Density Score** | 188.0 | **150.0** | **-20.2% Peak Hotspot Reduction** |
| **Power Distribution Variance (Std Dev)** | 47.5 | **40.3** | **+15.1% Smoother Thermal Spread** |
| **Total Placed Instances** | 6,388 | 6,388 | Zero logic overhead |
| **Core Footprint Penalty** | 100.0% | 100.0% | Zero die area increase |
| **Design Rule Violations (DRC)** | 0 | 0 | Clean manufacturing closure |

* Generated the side-by-side comparison heatmap saved in `reports/power_density_comparison.png`.

### 5. Full Silicon Implementation (PDN, CTS & Detailed Routing)
* **Power Distribution Network (PDN):** Created horizontal power rails on `met1` and thick vertical/horizontal power mesh straps on `met4` and `met5` for 1.8V VDD and VSS.
* **Clock Tree Synthesis (CTS):** Synthesized a balanced clock network across all 1,023 flip-flops using 145 clock buffers with a matched path depth of 3 levels.
* **Detailed Routing (TritonRoute):** Routed all 6,600 signal nets across 5 metal layers (`met1` to `met5`).
* **Silicon GDSII Stream-Out:** Compiled the final layout into **`data/full_chip_detailed_routed.gds`** and inspected the metal wires and power mesh in KLayout.
* **Interactive Dashboard:** Built `reports/dashboard.html` summarizing all project metrics, tables, and visual heatmaps.

---

## How to Run the Project

1. **Simulate the core:**
   ```bash
   iverilog -o sim/sim_rv32i rtl/rv32i_core.v sim/tb_rv32i.v
   vvp sim/sim_rv32i
   python3 scripts/parse_vcd.py
