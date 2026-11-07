# RV32I Core - ML-Guided Physical Design & Power Optimization

Project work under **Dr. Binod Kumar**, Department of Electronics Engineering, IIT Jodhpur.

## About the Project
Standard physical design tools like OpenROAD place logic gates on a chip to minimize wire length, but they don't know which gates switch together when actual software runs. This often packs high-activity gates (like the ALU and pipeline registers) too close together, causing localized dynamic power hotspots and voltage drops (IR drop).

In this project, I'm building an automated flow that:
1. Simulates an RV32I core running real instructions to record gate switching activity.
2. Trains a machine learning model to flag which gates form dangerous power clusters.
3. Automatically generates placement padding commands (`set_placement_padding`) for OpenROAD to give those hot gates breathing room before clock tree synthesis and routing.

---

## Project Structure
* `rtl/` - Verilog hardware code for the single-cycle RV32I core (`rv32i_core.v`).
* `sim/` - Testbench (`tb_rv32i.v`) and simulation waveform trace (`wave.vcd`).
* `scripts/` - Python and Yosys scripts to parse waveforms, synthesize the netlist, and extract features.
* `data/` - Synthesized gate-level netlist (`rv32i_gate_level.v`) and ML dataset (`dataset.csv`).
* `ml/` - Random Forest training script (`train_model.py`).
* `openroad/` - Generated OpenROAD padding script (`ml_padding.tcl`).

---

## What I've Done So Far

### 1. Processor RTL & Verification
* Built a synthesizable 32-bit single-cycle RV32I core with Program Counter, 32 registers (x0 hardwired to 0), instruction decoder, and ALU.
* Verified execution with an Icarus Verilog testbench running arithmetic and memory instructions.
* Generated `wave.vcd` to capture net-by-net switching activity.

### 2. Logic Synthesis
* Synthesized the design using Yosys 0.52 down to 6,579 physical cells:
  * 993 Register File flip-flops
  * 30 Program Counter flip-flops
  * 5,556 combinational logic gates (AND, OR, MUX, XOR)

### 3. Feature Extraction & Machine Learning
* Wrote `extract_features.py` to merge circuit connections (fan-in, fan-out, cell types) with VCD switching data into `dataset.csv`.
* Labeled the top 15% highest dynamic power gates as hotspots.
* Trained a Random Forest classifier in `train_model.py`:
  * Achieved 100% test accuracy on 1,316 unseen test gates.
  * Found that sequential flip-flops account for over 83% of power hotspot risk, followed by fan-out loading (~10.6%).
* Automatically exported `openroad/ml_padding.tcl` with 2-site padding rules around the 1,023 predicted hotspot gates.

---

## How to Run

1. **Simulate the processor:**
   ```bash
   iverilog -o sim/sim_rv32i rtl/rv32i_core.v sim/tb_rv32i.v
   vvp sim/sim_rv32i
yosys -s scripts/synth.ys
python3 scripts/extract_features.py
python3 ml/train_model.py
