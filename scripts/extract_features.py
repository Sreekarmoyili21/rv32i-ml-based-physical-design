import re
from collections import defaultdict
import csv

def parse_vcd_toggles(vcd_path):
    symbol_to_net = {}
    toggle_counts = defaultdict(int)
    
    with open(vcd_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('$var'):
                parts = line.split()
                if len(parts) >= 5:
                    symbol = parts[3]
                    net_name = parts[4]
                    symbol_to_net[symbol] = net_name
            elif line.startswith('$enddefinitions'):
                break
                
        for line in f:
            line = line.strip()
            if not line or line.startswith('#') or line.startswith('$'):
                continue
            if line.startswith('b'):
                parts = line.split()
                if len(parts) >= 2:
                    symbol = parts[1]
                    toggle_counts[symbol] += 1
            else:
                symbol = line[1:]
                toggle_counts[symbol] += 1

    net_toggles = defaultdict(int)
    for symbol, count in toggle_counts.items():
        net_name = symbol_to_net.get(symbol, '')
        if net_name:
            net_toggles[net_name] = count
    return net_toggles

def parse_netlist_and_build_dataset(netlist_path, vcd_path, output_csv):
    net_toggles = parse_vcd_toggles(vcd_path)
    net_fanout = defaultdict(int)
    cells = []
    
    assign_pattern = re.compile(r'^\s*assign\s+([\\$\w\[\]\.]+)\s*=\s*(.*?);', re.MULTILINE)
    
    with open(netlist_path, 'r') as f:
        content = f.read()

    assign_matches = assign_pattern.findall(content)

    for out_net, expr in assign_matches:
        tokens = re.findall(r'[\\$\w]+(?:\[\d+\])?', expr)
        for tok in tokens:
            if tok not in ['1\'h0', '1\'h1', '1\'bx', '1\'hX', '1\'b0', '1\'b1']:
                net_fanout[tok] += 1

    cell_idx = 0
    for out_net, expr in assign_matches:
        out_net = out_net.strip()
        cell_idx += 1
        cell_name = f"gate_{cell_idx}_{out_net.replace('\\', '').replace('[', '_').replace(']', '_')}"
        
        if '?' in expr and ':' in expr:
            cell_type = 'MUX'
            category = 'MULTIPLEXER'
        elif '^' in expr:
            cell_type = 'XOR'
            category = 'ARITHMETIC_XOR'
        elif '&' in expr and '~' in expr:
            cell_type = 'ANDNOT'
            category = 'LOGIC_AND'
        elif '&' in expr:
            cell_type = 'AND'
            category = 'LOGIC_AND'
        elif '|' in expr and '~' in expr:
            cell_type = 'ORNOT'
            category = 'LOGIC_OR'
        elif '|' in expr:
            cell_type = 'OR'
            category = 'LOGIC_OR'
        elif '~' in expr:
            cell_type = 'NOT'
            category = 'INVERTER'
        else:
            cell_type = 'BUF'
            category = 'BUFFER'

        tokens = [tok for tok in re.findall(r'[\\$\w]+(?:\[\d+\])?', expr) 
                  if tok not in ['1\'h0', '1\'h1', '1\'bx', '1\'hX', '1\'b0', '1\'b1']]
        fan_in = max(1, len(tokens))
        fan_out = net_fanout.get(out_net, 1)

        toggles = net_toggles.get(out_net, 0)
        if toggles == 0 and tokens:
            toggles = max([net_toggles.get(tok, 0) for tok in tokens])

        power_proxy = fan_out * toggles

        cells.append({
            'cell_name': cell_name,
            'cell_type': cell_type,
            'category': category,
            'is_sequential': 0,
            'fan_in': fan_in,
            'fan_out': fan_out,
            'toggle_count': toggles,
            'power_proxy': power_proxy
        })

    dff_blocks = re.findall(r'always @\(posedge clk.*?\)\s+if \(reset\)\s+([\\$\w\[\]\.\s]+)\s*<=.*?;', content, re.DOTALL)
    for dff_reg in dff_blocks:
        dff_name = dff_reg.strip().replace('\\', '').replace(' ', '_').replace('[', '_').replace(']', '_')
        cell_idx += 1
        cells.append({
            'cell_name': f"dff_{dff_name}",
            'cell_type': 'DFF',
            'category': 'SEQUENTIAL',
            'is_sequential': 1,
            'fan_in': 2,
            'fan_out': 2,
            'toggle_count': 16,
            'power_proxy': 2 * 16
        })

    all_scores = [c['power_proxy'] for c in cells]
    all_scores.sort()
    thresh_idx = int(len(all_scores) * 0.85)
    hotspot_thresh = all_scores[thresh_idx] if all_scores else 1

    with open(output_csv, 'w', newline='') as f:
        fieldnames = ['cell_name', 'cell_type', 'category', 'is_sequential', 'fan_in', 'fan_out', 'toggle_count', 'power_proxy', 'is_hotspot']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        hotspot_count = 0
        for c in cells:
            is_hot = 1 if c['power_proxy'] >= hotspot_thresh and c['power_proxy'] > 0 else 0
            if is_hot:
                hotspot_count += 1
            c['is_hotspot'] = is_hot
            writer.writerow(c)

    print("=" * 60)
    print("FEATURE EXTRACTION SUCCESSFUL!")
    print("=" * 60)
    print(f"Total logic gates & DFFs parsed : {len(cells)}")
    print(f"Hotspot threshold score         : {hotspot_thresh}")
    print(f"Cells tagged as Hotspots        : {hotspot_count} (Top 15%)")
    print(f"Saved dataset to                : {output_csv}")
    print("=" * 60)

if __name__ == "__main__":
    parse_netlist_and_build_dataset("data/rv32i_gate_level.v", "sim/wave.vcd", "data/dataset.csv")
