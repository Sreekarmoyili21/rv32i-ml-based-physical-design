read_lef /OpenROAD-flow-scripts/flow/platforms/sky130hd/lef/sky130_fd_sc_hd.tlef
read_lef /OpenROAD-flow-scripts/flow/platforms/sky130hd/lef/sky130_fd_sc_hd_merged.lef
read_liberty /OpenROAD-flow-scripts/flow/platforms/sky130hd/lib/sky130_fd_sc_hd__tt_025C_1v80.lib
read_verilog data/rv32i_sky130.v
link_design rv32i_core

initialize_floorplan -utilization 50 -aspect_ratio 1.0 -core_space 10.0 -site unithd
source /OpenROAD-flow-scripts/flow/platforms/sky130hd/make_tracks.tcl
place_pins -hor_layers met3 -ver_layers met2

puts "=== RUNNING BASELINE GLOBAL PLACEMENT ==="
global_placement -density 0.65

puts "=== RUNNING BASELINE DETAILED PLACEMENT (NO PADDING) ==="
detailed_placement
write_def data/baseline.def
puts "Baseline DEF saved!"
exit
