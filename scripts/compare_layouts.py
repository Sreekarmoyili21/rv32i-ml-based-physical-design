import re
import numpy as np
import matplotlib.pyplot as plt

def parse_def_placements(def_path):
    placements = {}
    # Matches: - instance_name cell_master + PLACED ( X Y ) ORIENT ;
    pattern = re.compile(r'-\s+(\S+)\s+(\S+)\s+\+\s+PLACED\s*\(\s*(\d+)\s+(\d+)\s*\)')
    
    with open(def_path, 'r') as f:
        for line in f:
            match = pattern.search(line)
            if match:
                inst_name = match.group(1)
                cell_master = match.group(2)
                x = int(match.group(3)) / 1000.0 # Convert DBU to microns
                y = int(match.group(4)) / 1000.0
                
                # High power weight for sequential flip-flops (matching our ML discovery)
                if 'dfxtp' in cell_master or 'dfrtp' in cell_master or 'dfbbp' in cell_master:
                    weight = 32.0 # High dynamic switching
                else:
                    weight = 2.0  # Combinational logic
                    
                placements[inst_name] = (x, y, weight)
    return placements

def compute_density_grid(placements, grid_size=25, die_size=350.0):
    grid = np.zeros((grid_size, grid_size))
    bin_size = die_size / grid_size
    
    for x, y, weight in placements.values():
        bx = min(int(x / bin_size), grid_size - 1)
        by = min(int(y / bin_size), grid_size - 1)
        grid[by, bx] += weight
        
    return grid

def main():
    print("=" * 60)
    print("COMPARING WITHOUT-ML vs. WITH-ML SILICON LAYOUTS")
    print("=" * 60)
    
    baseline_places = parse_def_placements("data/baseline.def")
    ml_places = parse_def_placements("data/ml_padded.def")
    
    print(f"Baseline cells placed : {len(baseline_places)}")
    print(f"ML-padded cells placed: {len(ml_places)}")
    
    # Compute 2D power density maps
    grid_baseline = compute_density_grid(baseline_places)
    grid_ml = compute_density_grid(ml_places)
    
    peak_base = np.max(grid_baseline)
    peak_ml = np.max(grid_ml)
    reduction = ((peak_base - peak_ml) / peak_base) * 100.0
    
    std_base = np.std(grid_baseline)
    std_ml = np.std(grid_ml)
    evenness = ((std_base - std_ml) / std_base) * 100.0
    
    print("\n" + "=" * 60)
    print("FINAL EXPERIMENTAL RESULTS (SCORECARD)")
    print("=" * 60)
    print(f"{'Metric':<32} | {'Without ML':<12} | {'With ML':<12}")
    print("-" * 60)
    print(f"{'Peak Power Density (Score)':<32} | {peak_base:<12.1f} | {peak_ml:<12.1f}")
    print(f"{'Peak Hotspot Reduction':<32} | {'Baseline':<12} | {f'-{reduction:.1f}%':<12}")
    print(f"{'Power Variance (Std Dev)':<32} | {std_base:<12.1f} | {std_ml:<12.1f}")
    print(f"{'Thermal Distribution Spread':<32} | {'Uneven':<12} | {f'+{evenness:.1f}% smoother':<12}")
    print("=" * 60)
    
    # Generate Visual Side-by-Side Heatmaps
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    vmax = max(peak_base, peak_ml)
    
    im1 = ax1.imshow(grid_baseline, cmap='hot', origin='lower', extent=[0, 350, 0, 350], vmin=0, vmax=vmax)
    ax1.set_title("WITHOUT ML (Default OpenROAD)\nConcentrated Red Hotspots", fontsize=13, fontweight='bold', pad=12)
    ax1.set_xlabel("Die X (microns)")
    ax1.set_ylabel("Die Y (microns)")
    
    im2 = ax2.imshow(grid_ml, cmap='hot', origin='lower', extent=[0, 350, 0, 350], vmin=0, vmax=vmax)
    ax2.set_title(f"WITH ML (Our Guided Placement)\n{reduction:.1f}% Lower Peak Power Density", fontsize=13, fontweight='bold', color='green', pad=12)
    ax2.set_xlabel("Die X (microns)")
    ax2.set_ylabel("Die Y (microns)")
    
    cbar = fig.colorbar(im2, ax=[ax1, ax2], location='right', shrink=0.8)
    cbar.set_label("Dynamic Switching Power Density (Relative Score)", rotation=270, labelpad=15)
    
    output_png = "reports/power_density_comparison.png"
    plt.savefig(output_png, dpi=300, bbox_inches='tight')
    print(f"\nHeatmap plot successfully saved to: {output_png}")
    print("=" * 60)

if __name__ == "__main__":
    main()
