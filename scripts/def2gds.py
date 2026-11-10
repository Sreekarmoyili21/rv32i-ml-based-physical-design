import pya
import os

layout = pya.Layout()
opt = pya.LoadLayoutOptions()
lef_path = os.path.abspath("data/lef/sky130_fd_sc_hd_merged.lef")
opt.lefdef_config.lef_files = [lef_path]
opt.lefdef_config.read_lef_with_def = True

def_path = os.path.abspath("data/full_chip_detailed_routed.def")
layout.read(def_path, opt)

out_gds = os.path.abspath("data/full_chip_detailed_routed.gds")
layout.write(out_gds)
print("=" * 60)
print(f"SUCCESS: FULLY ROUTED GDSII SAVED TO: {out_gds}")
print("=" * 60)
