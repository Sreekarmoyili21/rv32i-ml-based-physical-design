import re
from collections import defaultdict

def parse_vcd(vcd_path):
    symbol_to_net = {}
    toggle_counts = defaultdict(int)
    
    with open(vcd_path, 'r') as f:
        # 1. Parse header to map symbols to net names
        for line in f:
            line = line.strip()
            if line.startswith('$var'):
                parts = line.split()
                # format: $var wire 32 " alu_out [31:0] $end
                if len(parts) >= 5:
                    symbol = parts[3]
                    net_name = parts[4]
                    symbol_to_net[symbol] = net_name
            elif line.startswith('$enddefinitions'):
                break
                
        # 2. Count transitions
        for line in f:
            line = line.strip()
            if not line or line.startswith('#') or line.startswith('$'):
                continue
            
            # Bus change (e.g., b00101 ") or scalar change (e.g., 1!)
            if line.startswith('b'):
                parts = line.split()
                if len(parts) >= 2:
                    symbol = parts[1]
                    toggle_counts[symbol] += 1
            else:
                symbol = line[1:]
                toggle_counts[symbol] += 1

    # Map back to net names and sort by activity
    net_activity = []
    for symbol, count in toggle_counts.items():
        name = symbol_to_net.get(symbol, f"unknown_{symbol}")
        net_activity.append((name, count))
        
    net_activity.sort(key=lambda x: x[1], reverse=True)
    
    print("=" * 50)
    print("TOP 10 MOST ACTIVE (HOTTEST) SIGNALS IN YOUR RV32I CORE")
    print("=" * 50)
    print(f"{'Signal Name':<30} | {'Toggle Count':<12}")
    print("-" * 50)
    for name, count in net_activity[:10]:
        print(f"{name:<30} | {count:<12}")
    print("=" * 50)
    print(f"Total unique monitored nets: {len(net_activity)}")

if __name__ == "__main__":
    parse_vcd("sim/wave.vcd")
