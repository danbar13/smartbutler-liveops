from http.server import BaseHTTPRequestHandler
import urllib.parse
import os
import sys
from collections import defaultdict, Counter
import pandas as pd

# Ensure parent directory is on sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import db
from engine import SmartButlerEngine
import i18n
from i18n import (
    t, get_dept_name, classify_specific_request, get_location_cluster,
    generate_executive_briefing, generate_departmental_action_items,
    LANG_HE, LANG_EN
)

# Official JAYBEE Vector Logo
JAYBEE_LOGO_SVG = """<svg width="120" height="30" viewBox="0 0 134 34" fill="none" xmlns="http://www.w3.org/2000/svg">
<g clip-path="url(#clip0_jb)">
<path d="M42.3543 8.99414V25.1151C42.3543 26.0493 41.949 26.5165 41.1391 26.5165H40.3867V30.0212H41.6594C43.145 30.0212 44.2829 29.6515 45.0736 28.9115C45.8644 28.1714 46.2604 26.9742 46.2604 25.3193V8.99414H42.3543Z" fill="white"/>
<path d="M60.8213 8.99493V11.3899C60.416 10.5718 59.8467 9.91515 59.1142 9.41867C58.381 8.92219 57.3582 8.67395 56.0471 8.67395C55.0051 8.67395 54.0359 8.88349 53.1387 9.30189C52.2422 9.72097 51.4561 10.2949 50.781 11.0249C50.1053 11.7549 49.5751 12.6018 49.1896 13.5654C48.8035 14.529 48.6105 15.5566 48.6105 16.6463C48.6105 18.1071 48.9437 19.4357 49.6088 20.6329C50.2746 21.83 51.1718 22.7843 52.2997 23.495C53.4283 24.2057 54.6772 24.5607 56.0471 24.5607C57.417 24.5607 58.4438 24.2978 59.1862 23.7726C59.9287 23.2467 60.5026 22.5561 60.9079 21.6992V24.181H64.6982V8.99493H60.8213ZM60.3869 18.8078C60.0398 19.4698 59.5525 20.0003 58.9257 20.3993C58.299 20.7984 57.5512 20.9979 56.6838 20.9979C55.8164 20.9979 55.1255 20.7937 54.4987 20.3846C53.8719 19.9756 53.3846 19.4357 53.0375 18.7637C52.6904 18.0924 52.5172 17.3764 52.5172 16.6177C52.5172 15.8195 52.6904 15.0888 53.0375 14.4269C53.3846 13.7656 53.8719 13.235 54.4987 12.8353C55.1255 12.4369 55.854 12.2367 56.6838 12.2367C57.5135 12.2367 58.299 12.4409 58.9257 12.85C59.5525 13.2591 60.0398 13.7949 60.3869 14.4562C60.734 15.1182 60.9079 15.8482 60.9079 16.6463C60.9079 17.4445 60.734 18.1458 60.3869 18.8078Z" fill="white"/>
<path d="M77.8707 8.99414L74.9478 17.6679C74.678 18.4466 74.4658 19.2548 74.3118 20.0916C74.157 19.2548 73.9448 18.4466 73.6751 17.6679L70.7528 8.99414H66.0361L71.9971 23.4795L71.7941 24.1221C71.5819 24.7835 71.2348 25.334 70.7528 25.7724C70.2701 26.2102 69.6533 26.429 68.9009 26.429C68.2642 26.429 67.6758 26.361 67.1356 26.2249L66.5571 29.9918C66.9426 30.1086 67.3769 30.1867 67.8589 30.2261C68.3409 30.2648 68.7753 30.2841 69.1614 30.2841C70.9359 30.2841 72.3343 29.8117 73.3564 28.8674C74.3792 27.9232 75.2083 26.682 75.845 25.1445L82.5001 8.99414H77.8707Z" fill="white"/>
<path d="M99.3472 13.5644C98.961 12.6008 98.4308 11.754 97.7558 11.0239C97.0801 10.2939 96.2946 9.71998 95.3974 9.3009C94.5003 8.8825 93.531 8.67296 92.4897 8.67296C91.1972 8.67296 90.1843 8.91653 89.4517 9.403C88.7178 9.89014 88.1493 10.5321 87.744 11.3302V2.86133H83.8379V24.18H87.6283V21.6983C88.0335 22.5551 88.6074 23.2458 89.3499 23.7716C90.0924 24.2968 91.139 24.5597 92.4897 24.5597C93.8404 24.5597 95.1323 24.2047 96.251 23.494C97.3697 22.7833 98.2622 21.8291 98.9273 20.6319C99.5931 19.4347 99.9257 18.1061 99.9257 16.6454C99.9257 15.5556 99.7326 14.528 99.3472 13.5644ZM95.4986 18.7627C95.1515 19.4347 94.6642 19.9746 94.0375 20.3837C93.4107 20.7927 92.6821 20.9969 91.853 20.9969C91.0239 20.9969 90.2616 20.7974 89.6249 20.3983C88.9882 19.9993 88.4964 19.4688 88.1493 18.8068C87.8021 18.1448 87.6283 17.4248 87.6283 16.6454C87.6283 15.8659 87.8021 15.1172 88.1493 14.4552C88.4964 13.7939 88.9882 13.2581 89.6249 12.849C90.2616 12.4399 91.0041 12.2358 91.853 12.2358C92.7019 12.2358 93.4107 12.4359 94.0375 12.8343C94.6642 13.2341 95.1515 13.7646 95.4986 14.4259C95.8457 15.0878 96.0196 15.8186 96.0196 16.6167C96.0196 17.4148 95.8457 18.0914 95.4986 18.7627Z" fill="white"/>
<path d="M116.068 12.6018C115.421 11.3853 114.525 10.4163 113.377 9.69628C112.229 8.97625 110.903 8.61523 109.399 8.61523C107.895 8.61523 106.558 8.97625 105.391 9.69628C104.224 10.4163 103.303 11.3853 102.628 12.6018C101.952 13.8189 101.615 15.1569 101.615 16.6177C101.615 18.0784 101.938 19.4064 102.584 20.6035C103.23 21.8014 104.142 22.7603 105.319 23.4803C106.495 24.2003 107.855 24.5607 109.399 24.5607C110.943 24.5607 112.224 24.2591 113.421 23.6558C114.617 23.0526 115.513 22.2731 116.112 21.3196L113.074 19.012C112.727 19.5965 112.239 20.083 111.612 20.4721C110.985 20.8618 110.247 21.0566 109.399 21.0566C108.415 21.0566 107.6 20.7744 106.954 20.2098C106.307 19.6453 105.878 18.9152 105.666 18.019H116.922C116.96 17.7661 116.989 17.5225 117.009 17.289C117.027 17.0554 117.037 16.8319 117.037 16.6177C117.037 15.1569 116.714 13.8189 116.068 12.6018ZM105.666 15.0695C105.878 14.1546 106.312 13.4152 106.969 12.85C107.624 12.2855 108.415 12.0032 109.341 12.0032C110.266 12.0032 111.121 12.3055 111.786 12.9087C112.451 13.512 112.89 14.2327 113.102 15.0695H105.666Z" fill="white"/>
<path d="M133.031 12.6017C132.384 11.3852 131.487 10.4163 130.34 9.69622C129.192 8.97619 127.866 8.61517 126.361 8.61517C124.856 8.61517 123.521 8.97619 122.354 9.69622C121.187 10.4163 120.266 11.3852 119.591 12.6017C118.915 13.8189 118.578 15.1569 118.578 16.6176C118.578 18.0784 118.901 19.4063 119.547 20.6035C120.193 21.8013 121.105 22.7602 122.282 23.4803C123.458 24.2003 124.818 24.5606 126.361 24.5606C127.904 24.5606 129.187 24.259 130.384 23.6558C131.579 23.0525 132.476 22.2731 133.074 21.3195L130.036 19.0119C129.689 19.5965 129.201 20.083 128.575 20.472C127.948 20.8617 127.21 21.0566 126.361 21.0566C125.377 21.0566 124.563 20.7743 123.916 20.2097C123.27 19.6452 122.841 18.9152 122.629 18.019H133.884C133.923 17.766 133.952 17.5225 133.971 17.2889C133.99 17.0554 134 16.8318 134 16.6176C134 15.1569 133.677 13.8189 133.031 12.6017ZM122.629 15.0694C122.841 14.1545 123.275 13.4152 123.931 12.8499C124.587 12.2854 125.377 12.0031 126.304 12.0031C127.23 12.0031 128.083 12.3054 128.748 12.9087C129.414 13.5119 129.853 14.2326 130.065 15.0694H122.629Z" fill="white"/>
<path d="M26.7029 17.0933C27.1227 17.894 27.3329 18.7776 27.3329 19.7432C27.3329 20.7088 27.1227 21.5269 26.7029 22.3397C26.2824 23.1525 25.6933 23.8058 24.935 24.3003C24.1766 24.7947 23.2953 25.0423 22.2923 25.0423C21.2894 25.0423 20.3671 24.8014 19.5968 24.3183C18.8272 23.8358 18.2322 23.1938 17.8117 22.3924C17.3919 21.5923 17.1816 20.7208 17.1816 19.7785C17.1816 18.8363 17.3919 17.9294 17.8117 17.1286C18.2322 16.3279 18.8272 15.6799 19.5968 15.1854C20.3671 14.6909 21.2649 14.4434 22.2923 14.4434C23.3198 14.4434 24.1766 14.6849 24.935 15.1674C25.6933 15.6505 26.2824 16.2925 26.7029 17.0933Z" fill="#4BBDDB"/>
<path d="M33.0178 17C32.7963 18.1258 32.4684 19.2248 32.0465 20.2872C32.0538 20.1197 32.0578 19.9495 32.0578 19.7787C32.0578 18.4594 31.8244 17.2169 31.3576 16.0511C30.8909 14.8853 30.2489 13.861 29.4324 12.9774C28.6152 12.0939 27.6651 11.3999 26.5795 10.8927C25.4945 10.3869 24.3223 10.1333 23.0622 10.1333C21.4986 10.1333 20.2734 10.4283 19.3868 11.0169C18.4996 11.6054 17.8113 12.3829 17.3214 13.3485V3.10252H12.5962V28.8935H17.1812V25.8906C17.6712 26.927 18.3654 27.7631 19.2639 28.3991C20.1624 29.035 21.4285 29.3526 23.0622 29.3526C23.9197 29.3526 24.7349 29.2405 25.5071 29.0163C22.0341 31.7963 17.7578 33.5 13.4219 33.5C4.39393 33.5 -1.47114 26.1128 0.322564 17C1.08289 13.1363 3.09874 9.58214 5.85639 6.77075V22.6048C5.85639 23.7352 5.36648 24.3004 4.38666 24.3004H3.47625V28.5405H5.01673C6.81308 28.5405 8.18959 28.0928 9.14694 27.1979C10.1036 26.3024 10.5823 24.8536 10.5823 22.8523V3.10719C13.4524 1.45693 16.6682 0.5 19.9177 0.5C28.9464 0.5 34.8115 7.88783 33.0178 17Z" fill="#4BBDDB"/>
</g>
<defs>
<clipPath id="clip0_jb">
<rect width="134" height="33" fill="white" transform="translate(0 0.5)"/>
</clipPath>
</defs>
</svg>"""

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
        period = kpi["period"] if kpi else "20/Sep/2026 - 20/Sep/2026 (Daily)"
        tickets = kpi["total_tickets"] if kpi else 5
        sla_rate = kpi["overall_success_rate"] if kpi else 80.0
        avg_dur = kpi["avg_duration_str"] if kpi else "00:22"
        total_dur = kpi["total_time_str"] if kpi else "01:51"
        depts_count = kpi["department_count"] if kpi else 3

        # Briefing & Action Directives
        briefing_text = ""
        action_items = {}
        dept_analysis = []
        if engine:
            try:
                briefing_text = generate_executive_briefing(engine, lang=lang)
                action_items = generate_departmental_action_items(engine, lang=lang)
                dept_analysis = engine.get_department_analysis()
            except Exception:
                pass

        # Build Department Table
        dept_rows_html = ""
        for d in dept_analysis:
            d_name = get_dept_name(d["department"], lang)
            succ = d["success_rate"]
            status_badge = f'<span style="background:rgba(16,185,129,0.2); color:#34d399; padding:2px 8px; border-radius:4px; font-size:12px; font-weight:600;">{succ}%</span>' if succ >= 80 else f'<span style="background:rgba(245,158,11,0.2); color:#fbbf24; padding:2px 8px; border-radius:4px; font-size:12px; font-weight:600;">{succ}%</span>'
            dept_rows_html += f"""
            <tr style="border-bottom: 1px solid rgba(255,255,255,0.06);">
                <td style="padding:10px 14px; font-weight:600;">{d_name}</td>
                <td style="padding:10px 14px; text-align:center;">{d['total_tickets']}</td>
                <td style="padding:10px 14px; text-align:center;">{status_badge}</td>
                <td style="padding:10px 14px; text-align:center;">{d['avg_duration_str']}</td>
            </tr>
            """

        # Tab Labels
        tab1_lbl = "📤 העלאת דוחות וארכיון" if is_rtl else "📤 Ingestion & Archive"
        tab2_lbl = "📋 תדריך להנהלה - ישיבת בוקר" if is_rtl else "📋 Executive Standup Briefing"
        tab3_lbl = "🔍 תובנות עיקריות ומשמעותיות" if is_rtl else "🔍 Deep Insights & SLA"
        tab4_lbl = "📊 פירוט לפי מודולים ומחלקות" if is_rtl else "📊 Department Modules"

        # Tab 4 modules cards
        tab4_modules_html = ""
        for d in dept_analysis:
            raw_d = d["department"]
            d_name = get_dept_name(raw_d, lang)
            acts = action_items.get(raw_d, [])
            acts_html = "".join([f"<li style='margin-bottom:6px;'><strong>{a}</strong></li>" for a in acts])
            tab4_modules_html += f"""
            <details class="expander" style="margin-bottom:12px;">
                <summary>📁 {d_name} — {d['total_tickets']} {"קריאות" if is_rtl else "tickets"} | {d['success_rate']}% {"עמידה בתקן" if is_rtl else "SLA"}</summary>
                <div class="expander-body">
                    <div style="display:flex; gap:12px; margin-bottom:14px; flex-wrap:wrap;">
                        <span style="background:#0d1e2e; padding:6px 12px; border-radius:6px; font-size:12px; border:1px solid rgba(75,189,219,0.3);">{"סך קריאות:" if is_rtl else "Tickets:"} <strong>{d['total_tickets']}</strong></span>
                        <span style="background:#0d1e2e; padding:6px 12px; border-radius:6px; font-size:12px; border:1px solid rgba(75,189,219,0.3);">{"עמידה בתקן:" if is_rtl else "SLA:"} <strong>{d['success_rate']}%</strong></span>
                        <span style="background:#0d1e2e; padding:6px 12px; border-radius:6px; font-size:12px; border:1px solid rgba(75,189,219,0.3);">{"זמן ממוצע:" if is_rtl else "Avg Time:"} <strong>{d['avg_duration_str']}</strong></span>
                    </div>
                    <h4 style="color:#38bdf8; font-size:13.5px; margin-bottom:8px;">{"הנחיות לפעולה מיידית:" if is_rtl else "Immediate Actionable Directives:"}</h4>
                    <ul style="padding-{align}: 20px; font-size:13px; color:#e2e8f0; line-height:1.5;">
                        {acts_html or f"<li>{'מעקב שוטף ועמידה בזמני תקן.' if is_rtl else 'Continue standard SLA tracking.'}</li>"}
                    </ul>
                </div>
            </details>
            """

        html = f"""<!DOCTYPE html>
<html lang="{lang}" dir="{direction}">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>SmartButler® — LiveOps Digest</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            background: #090e17;
            color: #f1f5f9;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            direction: {direction};
            text-align: {align};
            padding: 14px;
            min-height: 100vh;
        }}
        .container {{
            max-width: 980px;
            margin: 0 auto;
        }}
        .main-header {{
            background: linear-gradient(135deg, #0d2838, #0a1924);
            border: 1px solid rgba(75, 189, 219, 0.3);
            border-radius: 10px;
            padding: 16px 20px;
            margin-bottom: 16px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        }}
        .header-top {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 12px;
            margin-bottom: 10px;
        }}
        .header-title-box h1 {{
            font-size: 19px;
            color: #ffffff;
            font-weight: 700;
        }}
        .header-title-box p {{
            font-size: 12.5px;
            color: #cbd5e1;
            margin-top: 3px;
        }}
        .header-badges {{
            display: flex;
            align-items: center;
            gap: 10px;
            flex-wrap: wrap;
        }}
        .lang-btn {{
            padding: 5px 12px;
            border-radius: 6px;
            font-size: 12.5px;
            font-weight: 600;
            text-decoration: none;
            color: #cbd5e1;
            background: #1e293b;
            border: 1px solid rgba(75,189,219,0.3);
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }}
        .lang-btn.active {{
            background: linear-gradient(135deg, #0284c7, #0369a1);
            color: #ffffff;
            border-color: #38bdf8;
            box-shadow: 0 0 10px rgba(56,189,248,0.4);
        }}
        .date-badge {{
            background: rgba(75, 189, 219, 0.15);
            border: 1px solid rgba(75, 189, 219, 0.4);
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            color: #38bdf8;
            direction: ltr;
        }}
        .nav-tabs {{
            display: flex;
            gap: 6px;
            border-bottom: 2px solid rgba(255,255,255,0.1);
            margin-bottom: 16px;
            overflow-x: auto;
            scrollbar-width: thin;
        }}
        .tab-btn {{
            padding: 9px 14px;
            background: transparent;
            border: none;
            border-bottom: 3px solid transparent;
            color: #94a3b8;
            font-size: 13.5px;
            font-weight: 600;
            cursor: pointer;
            white-space: nowrap;
            transition: all 0.2s ease;
        }}
        .tab-btn:hover {{ color: #38bdf8; }}
        .tab-btn.active {{
            color: #38bdf8;
            border-bottom-color: #38bdf8;
        }}
        .tab-content {{ display: none; }}
        .tab-content.active {{ display: block; }}
        .brief-banner {{
            background: #0d2131;
            border-{"right" if is_rtl else "left"}: 4px solid #38bdf8;
            border: 1px solid rgba(75, 189, 219, 0.3);
            padding: 12px 16px;
            border-radius: 8px;
            margin-bottom: 16px;
        }}
        .brief-banner h3 {{ color: #38bdf8; font-size: 16px; margin-bottom: 4px; }}
        .brief-banner p {{ color: #cbd5e1; font-size: 12.5px; }}
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 10px;
            margin-bottom: 16px;
        }}
        @media (max-width: 768px) {{
            .kpi-grid {{ grid-template-columns: 1fr 1fr; gap: 8px; }}
            .header-top {{ flex-direction: column; align-items: flex-start; }}
        }}
        .kpi-card {{
            background: #0d1e2e;
            border: 1px solid rgba(75, 189, 219, 0.35);
            border-radius: 8px;
            padding: 12px 14px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        }}
        .kpi-title {{ font-size: 11.5px; color: #cbd5e1; font-weight: 600; margin-bottom: 3px; }}
        .kpi-val {{ font-size: 22px; color: #ffffff; font-weight: 700; }}
        .kpi-delta {{ font-size: 11px; color: #38bdf8; font-weight: 600; margin-top: 3px; }}
        .expander {{
            background: #0d1726;
            border: 1px solid rgba(75, 189, 219, 0.25);
            border-radius: 8px;
            margin-bottom: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.18);
            overflow: hidden;
        }}
        .expander summary {{
            padding: 11px 16px;
            font-size: 14.5px;
            font-weight: 600;
            color: #ffffff;
            cursor: pointer;
            outline: none;
            user-select: none;
            background: rgba(255,255,255,0.02);
            transition: background 0.15s ease;
        }}
        .expander summary:hover {{
            background: rgba(75, 189, 219, 0.08);
            color: #38bdf8;
        }}
        .expander-body {{
            padding: 16px;
            border-top: 1px solid rgba(75, 189, 219, 0.15);
            color: #e2e8f0;
            font-size: 13.5px;
            line-height: 1.6;
        }}
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
        .links-bar {{
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            margin-top: 20px;
            padding-top: 14px;
            border-top: 1px solid rgba(255,255,255,0.08);
            align-items: center;
            justify-content: space-between;
        }}
        .action-link {{
            padding: 8px 14px;
            border-radius: 6px;
            text-decoration: none;
            font-weight: 600;
            font-size: 12.5px;
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }}
        .btn-gh {{ background: #24292e; color: #ffffff; border: 1px solid rgba(255,255,255,0.2); }}
        .btn-st {{ background: #ff4b4b; color: #ffffff; }}
    </style>
</head>
<body>
    <div class="container">
        <header class="main-header">
            <div class="header-top">
                <div style="background:#0D2838; padding:6px 10px; border-radius:6px; display:inline-flex; align-items:center;">
                    {JAYBEE_LOGO_SVG}
                </div>
                <div class="header-badges">
                    <a href="?lang=he" class="lang-btn {'active' if is_rtl else ''}">🇮🇱 עברית</a>
                    <a href="?lang=en" class="lang-btn {'active' if not is_rtl else ''}">🇬🇧 English</a>
                    <span class="date-badge">📅 {period}</span>
                </div>
            </div>
            <div class="header-title-box">
                <h1>SmartButler<sup>&reg;</sup> — {"תדריך בוקר אופרטיבי ומעקב SLA" if is_rtl else "Operational Morning Briefing & SLA Tracking"}</h1>
                <p>{"מערכת SmartButler® מבית ג'ייבי מערכות (www.jaybee.com) | אתר:" if is_rtl else "SmartButler® System by JAYBEE Systems Ltd. (www.jaybee.com) | Site:"} <strong>{site}</strong></p>
            </div>
        </header>

        <nav class="nav-tabs">
            <button class="tab-btn" onclick="openTab('tab1', this)">{tab1_lbl}</button>
            <button class="tab-btn active" onclick="openTab('tab2', this)">{tab2_lbl}</button>
            <button class="tab-btn" onclick="openTab('tab3', this)">{tab3_lbl}</button>
            <button class="tab-btn" onclick="openTab('tab4', this)">{tab4_lbl}</button>
        </nav>

        <!-- TAB 1 -->
        <div id="tab1" class="tab-content">
            <details class="expander" open>
                <summary>ℹ️ {"מצב קליטה ודוח פעיל כעת" if is_rtl else "Active Report Ingestion Status"}</summary>
                <div class="expander-body">
                    <p style="margin-bottom:10px;">🟢 {"דוח פעיל כעת במערכת:" if is_rtl else "Current Active Report:"} <strong>{site}</strong> • {"תקופה:" if is_rtl else "Period:"} <strong>{period}</strong></p>
                    <p>{"בגרסת הענן Vercel Serverless מוצג הדוח הפעיל האחרון מתוך מסד הנתונים. להעלאת דוחות חדשים בזמן אמת עם עיבוד PDF, ניתן להשתמש בגרסת ה-Streamlit המלאה." if is_rtl else "In Vercel Serverless cloud, the active report from database is loaded. For live file uploads with real-time PDF parsing, launch the full Streamlit app."}</p>
                </div>
            </details>
        </div>

        <!-- TAB 2 -->
        <div id="tab2" class="tab-content active">
            <div class="brief-banner">
                <h3>📋 {"תדריך בוקר אופרטיבי להנהלת המלון" if is_rtl else "Operational Morning Briefing for Hotel Management"}</h3>
                <p>{"תקופת הדוח:" if is_rtl else "Report Period:"} <strong>{period}</strong> | {"אתר:" if is_rtl else "Property:"} <strong>{site}</strong></p>
            </div>

            <section class="kpi-grid">
                <div class="kpi-card">
                    <div class="kpi-title">{"סך קריאות" if is_rtl else "Total Tickets"}</div>
                    <div class="kpi-val">{tickets}</div>
                    <div class="kpi-delta">↑ {depts_count} {"מחלקות פעילות" if is_rtl else "active departments"}</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-title">{"עמידה בזמני תקן (SLA)" if is_rtl else "SLA Compliance Rate"}</div>
                    <div class="kpi-val">{sla_rate}%</div>
                    <div class="kpi-delta">↑ {"עמידה ביעד" if is_rtl else "On Target"}</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-title">{"זמן טיפול ממוצע" if is_rtl else "Avg Handling Time"}</div>
                    <div class="kpi-val">{avg_dur} {"ש'" if is_rtl else "hrs"}</div>
                    <div class="kpi-delta">↑ {"שעות:דקות" if is_rtl else "Hours:Mins"}</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-title">{"סך שעות טיפול" if is_rtl else "Cumulative Hours"}</div>
                    <div class="kpi-val">{total_dur} {"ש'" if is_rtl else "hrs"}</div>
                    <div class="kpi-delta">↑ {"כלל המחלקות" if is_rtl else "All Departments"}</div>
                </div>
            </section>

            <details class="expander" open>
                <summary>🗣️ {"תמצית מנהלים והנחיות תפעוליות לישיבת הבוקר" if is_rtl else "Executive Summary & Operational Morning Briefing"}</summary>
                <div class="expander-body" style="white-space: pre-line;">
                    {briefing_text or "No briefing available."}
                </div>
            </details>

            <details class="expander">
                <summary>🏢 {"השוואה מחלקתית מרוכזת" if is_rtl else "Department Performance Summary"} ({len(dept_analysis)} {"מחלקות" if is_rtl else "departments"})</summary>
                <div class="expander-body">
                    <div style="overflow-x: auto;">
                        <table>
                            <thead>
                                <tr>
                                    <th>{"מחלקה" if is_rtl else "Department"}</th>
                                    <th style="text-align:center;">{"סך קריאות" if is_rtl else "Total Tickets"}</th>
                                    <th style="text-align:center;">{"עמידה בתקן" if is_rtl else "SLA Adherence"}</th>
                                    <th style="text-align:center;">{"זמן ממוצע" if is_rtl else "Avg Time"}</th>
                                </tr>
                            </thead>
                            <tbody>
                                {dept_rows_html}
                            </tbody>
                        </table>
                    </div>
                </div>
            </details>
        </div>

        <!-- TAB 3 -->
        <div id="tab3" class="tab-content">
            <details class="expander" open>
                <summary>🔍 {"תובנות עומק, מעקב זמנים ומוקדי שיפור תפעולי" if is_rtl else "Deep Operational Insights & Bottlenecks"}</summary>
                <div class="expander-body">
                    <p style="margin-bottom:12px;">💡 {"סעיפי מעקב וניתוח מעמיק:" if is_rtl else "In-depth tracking areas:"}</p>
                    <ul style="padding-{align}: 20px; line-height: 1.7;">
                        <li><strong>{"יחידות במעקב מיוחד:" if is_rtl else "Special Focus Units:"}</strong> {"ריכוז פניות רב-מחלקתי וזיהוי חדרים הדורשים שיחת אדיבות יזומה (Courtesy Check)." if is_rtl else "Cross-departmental ticket clustering and proactive courtesy checks."}</li>
                        <li><strong>{"מוקדי תקלות חוזרות:" if is_rtl else "Recurring Issues:"}</strong> {"ניתוח תקלות כרוניות באותו חדר או אגף (ציוד חסר, אינסטלציה, מיזוג אוויר)." if is_rtl else "Chronic issue patterns by room or floor cluster."}</li>
                        <li><strong>{"מעקב חריגות תקן קיצוניות:" if is_rtl else "Extreme Duration Outliers:"}</strong> {"קריאות בטיפול ממושך מעבר לפי 1.5–2.0 מזמן התקן המוגדר." if is_rtl else "Extended duration tracking exceeding SLA benchmarks."}</li>
                    </ul>
                </div>
            </details>
        </div>

        <!-- TAB 4 -->
        <div id="tab4" class="tab-content">
            <div style="margin-bottom:14px;">
                <h3 style="color:#38bdf8; font-size:16px;">{"פירוט מלא לפי מחלקות והנחיות לצוותים" if is_rtl else "Departmental Breakdown & Team Directives"}</h3>
                <p style="color:#94a3b8; font-size:12.5px;">{"פתח כל מחלקה לצפייה במדדים המפורטים וההנחיות התפעוליות:" if is_rtl else "Expand each department to review metrics and actionable directives:"}</p>
            </div>
            {tab4_modules_html}
        </div>

        <div class="links-bar">
            <div>
                <a href="https://github.com/danbar13/smartbutler-liveops" target="_blank" class="action-link btn-gh">
                    🐙 {"קוד מקור ב-GitHub" if is_rtl else "GitHub Repository"}
                </a>
            </div>
            <div style="font-size:12px; color:#64748b;">
                SmartButler® LiveOps Digest • JAYBEE Systems Ltd. • Vercel Serverless
            </div>
        </div>
    </div>

    <script>
        function openTab(tabId, btn) {{
            document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
            document.getElementById(tabId).classList.add('active');
            btn.classList.add('active');
        }}
    </script>
</body>
</html>"""
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))
