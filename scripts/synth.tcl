# 1. Read the RV32I Verilog hardware description
read_verilog rtl/rv32i_core.v

# 2. Check hierarchy and set the top module
hierarchy -check -top rv32i_core

# 3. Perform standard digital synthesis optimization passes
synth -top rv32i_core

# 4. Display cell count, wire count, and gate statistics
stat

# 5. Save the synthesized gate-level netlist into data/
write_verilog -noattr data/rv32i_gate_level.v
