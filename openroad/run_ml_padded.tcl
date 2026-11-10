read_lef /OpenROAD-flow-scripts/flow/platforms/sky130hd/lef/sky130_fd_sc_hd.tlef
read_lef /OpenROAD-flow-scripts/flow/platforms/sky130hd/lef/sky130_fd_sc_hd_merged.lef
read_liberty /OpenROAD-flow-scripts/flow/platforms/sky130hd/lib/sky130_fd_sc_hd__tt_025C_1v80.lib
read_verilog data/rv32i_sky130.v
link_design rv32i_core

initialize_floorplan -utilization 50 -aspect_ratio 1.0 -core_space 10.0 -site unithd
source /OpenROAD-flow-scripts/flow/platforms/sky130hd/make_tracks.tcl
place_pins -hor_layers met3 -ver_layers met2

puts "=== APPLYING ML PADDING ==="
set_placement_padding -masters {sky130_fd_sc_hd__dfxtp_1 sky130_fd_sc_hd__dfrtp_1 sky130_fd_sc_hd__dfbbp_1} -left 2 -right 2

puts "=== RUNNING ML GLOBAL PLACEMENT ==="
global_placement -density 0.65 -pad_left 2 -pad_right 2

puts "=== RUNNING ML DETAILED PLACEMENT (LEGALIZING PADDING GAPS) ==="
detailed_placement
write_def data/ml_padded.def
puts "ML-Padded DEF saved!"
exit
