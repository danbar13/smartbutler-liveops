from http.server import BaseHTTPRequestHandler
import urllib.parse
import os
import sys

# Ensure parent directory is on sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import db
from engine import SmartButlerEngine
import i18n
from i18n import t, get_dept_name, generate_executive_briefing, LANG_HE, LANG_EN

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        query = urllib.parse.parse_qs(parsed_url.query)
        lang = query.get("lang", [LANG_HE])[0]
        if lang not in [LANG_HE, LANG_EN]:
            lang = LANG_HE

        is_rtl = (lang == LANG_HE)
        direction = "rtl" if is_rtl else "ltr"
        align = "right" if is_rtl else "left"

        # Initialize db and get latest report
        try:
            db.init_db()
            report = db.get_latest_report()
            engine = SmartButlerEngine(report_dict=report) if report else None
            kpi = engine.get_kpi_summary() if engine else None
        except Exception:
            report = None
            engine = None
            kpi = None

        site = kpi["site"] if kpi else "Grand Hotel"
        period = kpi["period"] if kpi else "20/Sep/2026 (Daily)"
        tickets = kpi["total_tickets"] if kpi else 5
        sla_rate = kpi["overall_success_rate"] if kpi else 80.0
        avg_dur = kpi["avg_duration_str"] if kpi else "00:22"
        total_dur = kpi["total_time_str"] if kpi else "01:51"
        depts_count = kpi["department_count"] if kpi else 3

        briefing_text = ""
        if engine:
            try:
                briefing_text = generate_executive_briefing(engine, lang=lang)
            except Exception:
                pass

        dept_rows_html = ""
        if engine:
            try:
                depts = engine.get_department_analysis()
                for d in depts:
                    d_name = get_dept_name(d["department"], lang)
                    succ = d["success_rate"]
                    status_badge = f'<span style="background:rgba(16,185,129,0.2); color:#34d399; padding:2px 8px; border-radius:4px; font-size:12px;">{succ}%</span>' if succ >= 80 else f'<span style="background:rgba(245,158,11,0.2); color:#fbbf24; padding:2px 8px; border-radius:4px; font-size:12px;">{succ}%</span>'
                    dept_rows_html += f"""
                    <tr style="border-bottom: 1px solid rgba(255,255,255,0.06);">
                        <td style="padding:10px 14px; font-weight:600;">{d_name}</td>
                        <td style="padding:10px 14px; text-align:center;">{d['total_tickets']}</td>
                        <td style="padding:10px 14px; text-align:center;">{status_badge}</td>
                        <td style="padding:10px 14px; text-align:center;">{d['avg_duration_str']}</td>
                    </tr>
                    """
            except Exception:
                pass

        page_title = "SmartButler® — LiveOps Digest (Vercel Production)"
        header_title = "SmartButler® — תדריך בוקר אופרטיבי ומעקב SLA" if is_rtl else "SmartButler® — Operational Morning Briefing & SLA Tracking"
        sub_title = "דשבורד מנהלים תפעולי • JAYBEE Systems" if is_rtl else "Executive Operational Dashboard • JAYBEE Systems"
        kpi_tickets_label = "סך קריאות" if is_rtl else "Total Tickets"
        kpi_sla_label = "עמידה בזמני תקן (SLA)" if is_rtl else "SLA Compliance Rate"
        kpi_avg_label = "זמן טיפול ממוצע" if is_rtl else "Avg Handling Time"
        kpi_tot_label = "סך שעות טיפול" if is_rtl else "Cumulative Hours"
        briefing_heading = "📋 תדריך מנהלים לישיבת הבוקר" if is_rtl else "📋 Executive Morning Standup Briefing"
        depts_heading = "🏢 השוואה מחלקתית מרוכזת" if is_rtl else "🏢 Departmental Performance Overview"
        col_dept = "מחלקה" if is_rtl else "Department"
        col_tickets = "סך קריאות" if is_rtl else "Total Tickets"
        col_sla = "עמידה בתקן" if is_rtl else "SLA Adherence"
        col_avg = "זמן ממוצע" if is_rtl else "Avg Time"
        gh_btn_text = "צפה בקוד מקור ב-GitHub" if is_rtl else "View Source on GitHub"
        streamlit_btn_text = "הפעל ב-Streamlit Cloud" if is_rtl else "Launch on Streamlit Cloud"

        html = f"""<!DOCTYPE html>
<html lang="{lang}" dir="{direction}">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{page_title}</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            background: #090e17;
            color: #f1f5f9;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            direction: {direction};
            text-align: {align};
            padding: 16px;
            min-height: 100vh;
        }}
        .container {{
            max-width: 980px;
            margin: 0 auto;
        }}
        .header {{
            background: linear-gradient(135deg, #0d2838, #0a1924);
            border: 1px solid rgba(75, 189, 219, 0.3);
            border-radius: 10px;
            padding: 18px 22px;
            margin-bottom: 18px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 14px;
        }}
        .header h1 {{
            font-size: 20px;
            color: #ffffff;
            margin-bottom: 4px;
        }}
        .header p {{
            font-size: 13px;
            color: #cbd5e1;
        }}
        .lang-switch {{
            display: flex;
            gap: 8px;
        }}
        .lang-btn {{
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 13px;
            font-weight: 600;
            text-decoration: none;
            color: #cbd5e1;
            background: #1e293b;
            border: 1px solid rgba(75,189,219,0.3);
        }}
        .lang-btn.active {{
            background: linear-gradient(135deg, #0284c7, #0369a1);
            color: #ffffff;
            border-color: #38bdf8;
        }}
        .actions-bar {{
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            margin-bottom: 18px;
        }}
        .action-link {{
            padding: 9px 16px;
            border-radius: 6px;
            text-decoration: none;
            font-weight: 600;
            font-size: 13px;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            transition: transform 0.15s ease;
        }}
        .action-link:hover {{ transform: translateY(-1px); }}
        .btn-gh {{ background: #24292e; color: #ffffff; border: 1px solid rgba(255,255,255,0.2); }}
        .btn-st {{ background: #ff4b4b; color: #ffffff; border: 1px solid #ff4b4b; }}
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 12px;
            margin-bottom: 20px;
        }}
        @media (max-width: 600px) {{
            .kpi-grid {{ grid-template-columns: 1fr 1fr; gap: 8px; }}
            .header {{ flex-direction: column; align-items: flex-start; }}
        }}
        .kpi-card {{
            background: #0d1e2e;
            border: 1px solid rgba(75, 189, 219, 0.35);
            border-radius: 8px;
            padding: 14px 16px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        }}
        .kpi-title {{ font-size: 12px; color: #cbd5e1; font-weight: 600; margin-bottom: 4px; }}
        .kpi-val {{ font-size: 24px; color: #ffffff; font-weight: 700; }}
        .kpi-delta {{ font-size: 11px; color: #38bdf8; font-weight: 600; margin-top: 4px; }}
        .card {{
            background: #0d1726;
            border: 1px solid rgba(75, 189, 219, 0.22);
            border-radius: 8px;
            padding: 18px 20px;
            margin-bottom: 18px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.18);
        }}
        .card h2 {{ font-size: 17px; color: #38bdf8; margin-bottom: 12px; }}
        .card p, .card li {{ font-size: 13.5px; line-height: 1.6; color: #e2e8f0; }}
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
        }}
        th {{
            background: #17253a;
            padding: 10px 14px;
            font-weight: 600;
            color: #94a3b8;
            border-bottom: 2px solid rgba(75,189,219,0.3);
            text-align: {align};
        }}
        td {{ text-align: {align}; }}
        .footer {{
            text-align: center;
            font-size: 12px;
            color: #64748b;
            margin-top: 24px;
            padding-top: 14px;
            border-top: 1px solid rgba(255,255,255,0.08);
        }}
    </style>
</head>
<body>
    <div class="container">
        <header class="header">
            <div>
                <h1>{header_title}</h1>
                <p>{sub_title} | {site} • 📅 {period}</p>
            </div>
            <div class="lang-switch">
                <a href="?lang=he" class="lang-btn {'active' if is_rtl else ''}">🇮🇱 עברית</a>
                <a href="?lang=en" class="lang-btn {'active' if not is_rtl else ''}">🇬🇧 English</a>
            </div>
        </header>

        <div class="actions-bar">
            <a href="https://github.com/danbar13/smartbutler-liveops" target="_blank" class="action-link btn-gh">
                🐙 {gh_btn_text}
            </a>
            <a href="https://share.streamlit.io/" target="_blank" class="action-link btn-st">
                🚀 {streamlit_btn_text}
            </a>
        </div>

        <section class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-title">{kpi_tickets_label}</div>
                <div class="kpi-val">{tickets}</div>
                <div class="kpi-delta">↑ {depts_count} {"מחלקות פעילות" if is_rtl else "active departments"}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">{kpi_sla_label}</div>
                <div class="kpi-val">{sla_rate}%</div>
                <div class="kpi-delta">↑ {"עמידה ביעד" if is_rtl else "On Target"}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">{kpi_avg_label}</div>
                <div class="kpi-val">{avg_dur} {"ש'" if is_rtl else "hrs"}</div>
                <div class="kpi-delta">↑ {"שעות:דקות" if is_rtl else "Hours:Mins"}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">{kpi_tot_label}</div>
                <div class="kpi-val">{total_dur} {"ש'" if is_rtl else "hrs"}</div>
                <div class="kpi-delta">↑ {"כלל המחלקות" if is_rtl else "All Departments"}</div>
            </div>
        </section>

        <article class="card">
            <h2>{briefing_heading}</h2>
            <div style="white-space: pre-line; line-height: 1.65; color: #e2e8f0; font-size: 13.5px;">
                {briefing_text or "No briefing generated."}
            </div>
        </article>

        <article class="card">
            <h2>{depts_heading}</h2>
            <div style="overflow-x: auto;">
                <table>
                    <thead>
                        <tr>
                            <th>{col_dept}</th>
                            <th style="text-align:center;">{col_tickets}</th>
                            <th style="text-align:center;">{col_sla}</th>
                            <th style="text-align:center;">{col_avg}</th>
                        </tr>
                    </thead>
                    <tbody>
                        {dept_rows_html}
                    </tbody>
                </table>
            </div>
        </article>

        <footer class="footer">
            SmartButler® LiveOps Digest • JAYBEE Systems Ltd. • Hosted on Vercel Serverless & GitHub
        </footer>
    </div>
</body>
</html>"""
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))
