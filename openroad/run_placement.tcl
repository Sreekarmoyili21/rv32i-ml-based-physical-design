# 1. Read Technology and Cell Physical LEF
read_lef /OpenROAD-flow-scripts/flow/platforms/sky130hd/lef/sky130_fd_sc_hd.tlef
read_lef /OpenROAD-flow-scripts/flow/platforms/sky130hd/lef/sky130_fd_sc_hd_merged.lef

# 2. Read Timing Liberty Library
read_liberty /OpenROAD-flow-scripts/flow/platforms/sky130hd/lib/sky130_fd_sc_hd__tt_025C_1v80.lib

# 3. Read the Synthesized Sky130 Netlist
read_verilog data/rv32i_sky130.v
link_design rv32i_core

# 4. Initialize Floorplan (50% utilization, 1.0 aspect ratio, 10um margin)
initialize_floorplan -utilization 50 -aspect_ratio 1.0 -core_space 10.0 -site unithd
source /OpenROAD-flow-scripts/flow/platforms/sky130hd/make_tracks.tcl

# 5. Automatically place IO pins around the die boundary on Metal 2 and Metal 3
place_pins -hor_layers met3 -ver_layers met2

# -------------------------------------------------------------------
# RUN 1: BASELINE PLACEMENT (WITHOUT ML)
# -------------------------------------------------------------------
puts {=== RUNNING BASELINE PLACEMENT (WITHOUT ML) ===}
global_placement -density 0.55
write_def data/baseline.def
puts {Baseline placement saved to: data/baseline.def}

# -------------------------------------------------------------------
# RUN 2: ML-GUIDED PLACEMENT (WITH ML)
# -------------------------------------------------------------------
puts {=== APPLYING ML PADDING TO FLIP-FLOPS (WITH ML) ===}
set_placement_padding -masters {sky130_fd_sc_hd__dfxtp_1 sky130_fd_sc_hd__dfrtp_1 sky130_fd_sc_hd__dfbbp_1} -left 2 -right 2

puts {=== RUNNING ML-GUIDED PLACEMENT (WITH ML) ===}
global_placement -density 0.55
write_def data/ml_padded.def
puts {ML-guided placement saved to: data/ml_padded.def}

puts {BOTH SILICON LAYOUTS COMPLETED SUCCESSFULLY!}
exit
