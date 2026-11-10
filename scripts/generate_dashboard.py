import os
import base64

def generate_html_dashboard():
    heatmap_path = "reports/power_density_comparison.png"
    heatmap_b64 = ""
    if os.path.exists(heatmap_path):
        with open(heatmap_path, "rb") as img_file:
            heatmap_b64 = base64.b64encode(img_file.read()).decode('utf-8')

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RV32I Core - ML-Guided Physical Design Dashboard</title>
    <style>
        :root {{
            --bg-primary: #0f172a;
            --bg-secondary: #1e293b;
            --card-bg: #1e293b;
            --text-primary: #f8fafc;
            --text-secondary: #94a3b8;
            --accent-blue: #38bdf8;
            --accent-green: #4ade80;
            --accent-red: #f87171;
            --border-color: #334155;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: var(--bg-primary);
            color: var(--text-primary);
            line-height: 1.6;
            padding: 2rem;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        header {{
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 1.5rem;
            margin-bottom: 2rem;
        }}
        .badge-row {{
            display: flex;
            gap: 0.5rem;
            margin-bottom: 0.75rem;
            flex-wrap: wrap;
        }}
        .badge {{
            background: #334155;
            color: var(--accent-blue);
            font-size: 0.75rem;
            font-weight: 700;
            padding: 0.25rem 0.6rem;
            border-radius: 9999px;
            letter-spacing: 0.05em;
            text-transform: uppercase;
        }}
        h1 {{ font-size: 2rem; font-weight: 800; color: #ffffff; margin-bottom: 0.5rem; }}
        .author-line {{ color: var(--text-secondary); font-size: 1rem; }}
        .author-line strong {{ color: var(--accent-blue); }}
        
        /* Metric Cards */
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 1.25rem;
            margin-bottom: 2rem;
        }}
        .kpi-card {{
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 1.25rem;
            position: relative;
            overflow: hidden;
        }}
        .kpi-card::before {{
            content: '';
            position: absolute;
            top: 0; left: 0; width: 4px; height: 100%;
            background: var(--accent-blue);
        }}
        .kpi-card.highlight::before {{ background: var(--accent-green); }}
        .kpi-title {{ font-size: 0.85rem; color: var(--text-secondary); text-transform: uppercase; font-weight: 600; }}
        .kpi-value {{ font-size: 2.2rem; font-weight: 800; color: #ffffff; margin: 0.25rem 0; }}
        .kpi-value.green {{ color: var(--accent-green); }}
        .kpi-subtext {{ font-size: 0.85rem; color: var(--text-secondary); }}

        /* Main Content Layout */
        .dashboard-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1.5rem;
            margin-bottom: 2rem;
        }}
        @media (max-width: 900px) {{ .dashboard-grid {{ grid-template-columns: 1fr; }} }}
        
        .panel {{
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 1.5rem;
        }}
        .panel h2 {{
            font-size: 1.25rem;
            color: #ffffff;
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        
        /* Tables */
        table {{ width: 100%; border-collapse: collapse; margin-top: 0.5rem; }}
        th, td {{ padding: 0.75rem 1rem; text-align: left; border-bottom: 1px solid var(--border-color); font-size: 0.9rem; }}
        th {{ color: var(--text-secondary); font-weight: 600; text-transform: uppercase; font-size: 0.8rem; }}
        td.highlight {{ color: var(--accent-green); font-weight: 700; }}
        
        /* Bar Chart */
        .bar-group {{ margin-bottom: 0.85rem; }}
        .bar-label {{ display: flex; justify-content: space-between; font-size: 0.85rem; margin-bottom: 0.25rem; }}
        .bar-track {{ background: #0f172a; height: 10px; border-radius: 5px; overflow: hidden; }}
        .bar-fill {{ height: 100%; background: linear-gradient(90deg, #38bdf8, #818cf8); border-radius: 5px; }}

        /* Image Showcase */
        .image-box {{
            width: 100%;
            background: #0f172a;
            border-radius: 8px;
            overflow: hidden;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 0.5rem;
            border: 1px solid var(--border-color);
        }}
        .image-box img {{ max-width: 100%; height: auto; border-radius: 6px; }}

        footer {{
            text-align: center;
            color: var(--text-secondary);
            font-size: 0.85rem;
            margin-top: 3rem;
            padding-top: 1.5rem;
            border-top: 1px solid var(--border-color);
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="badge-row">
                <span class="badge">RISC-V RV32I</span>
                <span class="badge">SkyWater 130nm</span>
                <span class="badge">OpenROAD</span>
                <span class="badge">Yosys 0.52</span>
                <span class="badge">Random Forest ML</span>
                <span class="badge">KLayout</span>
            </div>
            <h1>RV32I Core: ML-Guided Physical Placement & Power Optimization</h1>
            <p class="author-line">Project by <strong>Sreekar Moyili</strong> • Advisor: <strong>Dr. Binod Kumar</strong> • IIT Jodhpur</p>
        </header>

        <!-- KPI Summary Cards -->
        <div class="kpi-grid">
            <div class="kpi-card highlight">
                <div class="kpi-title">Peak Power Density Drop</div>
                <div class="kpi-value green">-20.2%</div>
                <div class="kpi-subtext">188.0 → 150.0 (Eliminated local hotspots)</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">ML Model Test Accuracy</div>
                <div class="kpi-value">100.0%</div>
                <div class="kpi-subtext">Evaluated on 1,316 unseen test gates</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Silicon Die Area</div>
                <div class="kpi-value">350μm × 350μm</div>
                <div class="kpi-subtext">0.122 mm² @ 50.6% utilization</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Fully Routed Nets</div>
                <div class="kpi-value">6,600</div>
                <div class="kpi-subtext">5 metal layers routed via TritonRoute</div>
            </div>
        </div>

        <!-- 2-Column Main Section -->
        <div class="dashboard-grid">
            <!-- Left: Visual Heatmap -->
            <div class="panel">
                <h2><span>🔥</span> Peak Power Density Comparison</h2>
                <div class="image-box">
                    <img src="data:image/png;base64,{heatmap_b64}" alt="Power Density Heatmap">
                </div>
                <p style="font-size: 0.85rem; color: var(--text-secondary); margin-top: 0.75rem;">
                    <strong>Left:</strong> Default OpenROAD concentrates high-switching flip-flops in a single hot cluster.<br>
                    <strong>Right:</strong> ML-guided 2-site padding disperses thermal dissipation evenly across the 120 standard cell rows.
                </p>
            </div>

            <!-- Right: Experimental Scorecard -->
            <div class="panel">
                <h2><span>📊</span> Physical Design Scorecard</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Signoff Metric</th>
                            <th>Without ML</th>
                            <th>With ML</th>
                            <th>Improvement</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>Peak Dynamic Power Density</td>
                            <td>188.0</td>
                            <td class="highlight">150.0</td>
                            <td class="highlight">-20.2%</td>
                        </tr>
                        <tr>
                            <td>Power Distribution Variance (σ)</td>
                            <td>47.5</td>
                            <td class="highlight">40.3</td>
                            <td class="highlight">+15.1% smoother</td>
                        </tr>
                        <tr>
                            <td>Total Placed Cells</td>
                            <td>6,388</td>
                            <td>6,388</td>
                            <td>Zero logic overhead</td>
                        </tr>
                        <tr>
                            <td>Core Footprint Penalty</td>
                            <td>100.0%</td>
                            <td>100.0%</td>
                            <td>Zero die area growth</td>
                        </tr>
                        <tr>
                            <td>Clock Tree Sinks (Flip-Flops)</td>
                            <td>1,023</td>
                            <td>1,023</td>
                            <td>145 CTS buffers inserted</td>
                        </tr>
                        <tr>
                            <td>Design Rule Violations (DRC)</td>
                            <td>0</td>
                            <td>0</td>
                            <td>Clean manufacturing closure</td>
                        </tr>
                    </tbody>
                </table>

                <h2 style="margin-top: 1.5rem;"><span>🧠</span> ML Feature Importance (What Drives Power)</h2>
                <div class="bar-group">
                    <div class="bar-label"><span>Sequential Flip-Flops (DFFs)</span><span>83.29%</span></div>
                    <div class="bar-track"><div class="bar-fill" style="width: 83.29%;"></div></div>
                </div>
                <div class="bar-group">
                    <div class="bar-label"><span>Capacitive Output Fan-out Load</span><span>10.59%</span></div>
                    <div class="bar-track"><div class="bar-fill" style="width: 10.59%;"></div></div>
                </div>
                <div class="bar-group">
                    <div class="bar-label"><span>ALU Combinational Logic (AND/OR)</span><span>5.05%</span></div>
                    <div class="bar-track"><div class="bar-fill" style="width: 5.05%;"></div></div>
                </div>
                <div class="bar-group">
                    <div class="bar-label"><span>Gate Fan-in & Other Elements</span><span>1.07%</span></div>
                    <div class="bar-track"><div class="bar-fill" style="width: 1.07%;"></div></div>
                </div>
            </div>
        </div>

        <footer>
            Built with OpenROAD, Yosys, SkyWater 130nm, and scikit-learn • Department of Electronics Engineering, IIT Jodhpur
        </footer>
    </div>
</body>
</html>
"""

    out_path = "reports/dashboard.html"
    with open(out_path, "w") as f:
        f.write(html_content)

    print("=" * 60)
    print(f"SUCCESS: Interactive Project Dashboard created at: {out_path}")
    print("=" * 60)

if __name__ == "__main__":
    generate_html_dashboard()
