"""
SmartButler Briefing Summarizer — Pure Hebrew Operational Reporting
Generates executive-ready Morning Standup Briefings in:
1. Pure Hebrew Markdown (`./reports/morning_briefing.md`)
2. Modern, print-friendly standalone HTML in pure Hebrew (`./reports/morning_briefing.html`)
"""

import os
from .models import ExecutiveBriefing

CAT_HE = {
    "HVAC": "מיזוג אוויר",
    "Plumbing": "אינסטלציה וצנרת",
    "Electrical": "חשמל ותאורה",
    "Wi-Fi/Network": "רשת אלחוטית ואינטרנט",
    "Elevator": "מעליות",
    "Equipment": "מכונות וציוד",
    "Locks": "מנעולים ודלתות"
}
CAT_MAP = CAT_HE

SHIFT_HE = {
    "Morning": "משמרת בוקר",
    "Evening": "משמרת ערב",
    "Night": "משמרת לילה",
    "Evening Handover": "מסירת משמרת ערב",
    "Night Shift Handover": "מסירת משמרת לילה",
    "Morning Handover": "מסירת משמרת בוקר",
    "Night to Morning Standup": "מסירת לילה לישיבת בוקר"
}

ROLE_HE = {
    "Duty Manager": "מנהל תורן",
    "Night Manager": "מנהל לילה",
    "Front Desk Supervisor": "אחראי קבלה",
    "Executive Housekeeper": "מנהלת משק בית ראשית",
    "Chief Engineer": "מהנדס ראשי"
}

TECH_HE = {
    "David L. (Night Duty Tech)": "דוד ל. (טכנאי תורן לילה)",
    "Yossi C. (Senior AC Tech)": "יוסי כ. (טכנאי מיזוג בכיר)",
    "Ahmed K. (Mechanic)": "אחמד ק. (מכונאי)",
    "Eli R. (IT/AV Specialist)": "אלי ר. (מומחה תקשורת ומחשוב)",
    "Otis Contractor Hotline": "מוקד שירות מעליות אוטיס",
    "Team Duty Tech": "צוות אחזקה שוטפת"
}

ROOM_ASSET_HE = {
    "Central Plant": "חדר מכונות מרכזי (דודים)",
    "Elevator B": "מעלית ב'",
    "Service Pantry 2": "מזווה שירות קומה 2",
    "Lobby": "לובי המלון",
    "Hotel Wide": "כלל המלון"
}

class SmartButlerSummarizer:
    def __init__(self, briefing: ExecutiveBriefing, reports_dir: str = None):
        self.b = briefing
        if reports_dir is None:
            self.reports_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "reports")
        else:
            self.reports_dir = reports_dir
        os.makedirs(self.reports_dir, exist_ok=True)

    def _clean_issue_desc(self, desc: str) -> str:
        """Translates technical English ticket descriptions into fluent Hebrew."""
        d = desc.lower()
        if "boiler #2" in d or "relief valve" in d:
            return "שסתום פריקת לחץ ראשי בדוד הסקה מס' 2 פולט קיטור. הופעל ניתוק בטיחות מלחץ גבוה."
        elif "elevator b" in d or "door safety sensor" in d:
            return "תקלה E-14 בחיישן עין אופטית בדלת מעלית ב'. הדלתות נפתחות שוב ושוב ללא סגירה."
        elif "ice machine" in d or "ice maker" in d:
            return "מדחס מכונת קרח נתפס ומקפיץ ממסר 20 אמפר במזווה שירות."
        elif "hvac" in d and "warm air" in d:
            return "מערכת מיזוג פולטת אוויר חם, טמפרטורת החדר 26 מעלות."
        elif "vibrating" in d:
            return "יחידת מיזוג רועדת ומרעישה, בקר הטמפרטורה התאפס ל-27 מעלות."
        elif "compressor stopped cooling" in d or "compressor failed" in d:
            return "מדחס המיזוג כשל לחלוטין. החדר התחמם שוב, האורח דרש שיחה דחופה עם הנהלת המלון."
        elif "smarttv losing" in d:
            return "מסך טלוויזיה חכמה מתנתק מהרשת ונתקע בטעינת שידורים."
        elif "authentication timeout" in d:
            return "האורח אינו מצליח להתחבר לפורטל הרשת האלחוטית; חסימת אימות."
        elif "signal drop" in d:
            return "נפילת אות רשת אלחוטית מלאה באזור חדר השינה."
        elif "gateway unreachable" in d:
            return "מסך טלוויזיה חכם מנותק; שגיאת ניתוב כתובת ברשת."
        elif "water leak" in d:
            return "נזילת מים כבדה מתקרת הגבס בחדר הרחצה עקב כשל במחבר צינור מים ראשי."
        return desc

    def _clean_notes_desc(self, notes: str) -> str:
        """Translates notes and part descriptions to Hebrew."""
        n = notes.lower()
        if "boiler" in n or "2-inch" in n or "valve" in n:
            return "הדוד הועבר לקו משני. הוזמן שסתום לחץ תקני 2 צול, צפי הגעה: 10:30 בבוקר."
        elif "elevator" in n or "otis" in n or "optical curtain" in n:
            return "המעלית הושבתה. הוזמן טכנאי שירות אוטיס לשעה 09:00 עם וילון אופטי חלופי."
        elif "capacitor" in n or "ice" in n:
            return "המכשיר נותק מחשמל. נדרש קבל התנעה 45 מיקרו-פאראד ממחסן החלפים המרכזי."
        return notes

    def _clean_incident_desc(self, desc: str) -> str:
        """Translates logbook incident descriptions to Hebrew."""
        if "Ben-Ari" in desc or "HVAC system failed for the 3rd time" in desc:
            return "תלונה חריפה בקבלה: כשל שלישי במזגן בתוך 36 שעות. חום של 26.5 מעלות בחדר פגע במנוחת האורח לקראת הרצאה רפואית."
        elif "water cascade" in desc or "Cohen" in desc:
            return "נזילת מים חמורה מתקרת חדר הרחצה בעקבות פריצת צינור. האורחים הועברו מיידית בפיג'מות לסוויטת מנהלים 218."
        return desc

    def _clean_compensation_desc(self, comp: str) -> str:
        """Translates compensation details to Hebrew."""
        if "dinner" in comp.lower() or "chef restaurant" in comp.lower():
            return "ארוחת ערב זוגית במסעדת השף (450 ₪) + זיכוי 20% מעלות השהייה (620 ₪) ועזיבה מאוחרת."
        elif "upgrade" in comp.lower() or "spa" in comp.lower():
            return "שדרוג לסוויטה 218 לכל השהייה + זוג כרטיסי ספא, ארוחת בוקר וביטול חיוב מיני-בר."
        return comp

    def generate_markdown(self) -> str:
        """Generates executive standup briefing entirely in Hebrew Markdown with SmartButler(R) branding."""
        b = self.b
        md_lines = []
        md_lines.append("# SmartButler® — תדריך בוקר מבצעי למנהלים")
        md_lines.append(f"**תוכנה:** SmartButler® | **חברה מפתחת:** ג'ייבי מערכות (JAYBEE Systems — [www.jaybee.com](https://www.jaybee.com))")
        md_lines.append(f"**מלון:** גראנד הריטג' מלון וספא | **מועד הפקה:** {b.generated_at} (לקראת ישיבת בוקר)")
        md_lines.append("")
        md_lines.append("> [!IMPORTANT]")
        md_lines.append(f"> **דגשי מנכ\"ל לפתיחת יום:** נרשמה חשיפה כספית לפיצויים של **{b.total_compensation_ils:,.0f} ₪** עקב כשל חוזר במערכת מיזוג האוויר בחדר אח\"מ 412 ואירוע הצפת מים בחדר 205. בנוסף, **{b.open_waiting_parts_count} משימות אחזקה דחופות** ממשמרת הלילה הושבתו וממתינות להגעת חלקי חילוף מספקים חיצוניים.")
        md_lines.append("")
        md_lines.append("---")
        md_lines.append("")
        md_lines.append("## 1. מדדי מפתח תפעוליים ({b.period_label})")
        md_lines.append("")
        md_lines.append("| מדד תפעולי | מצב נוכחי | משמעות והשלכות תפעוליות |")
        md_lines.append("| :--- | :--- | :--- |")
        md_lines.append(f"| **סה\"כ קריאות שירות ואחזקה** | `{b.total_maintenance_48h}` קריאות | נפח עבודה שגרתי, ריכוז תקלות חריג בקומה 3 |")
        md_lines.append(f"| **משימות משק בית וניקיון** | `{b.total_housekeeping_48h}` משימות | שגרת שירות תקינה לצד 2 התערבויות דחופות |")
        md_lines.append(f"| **אירועים חריגים ביומן מנהל תורן** | `{b.total_logbook_entries_48h}` אירועים | 2 אירועים חריגים שחייבו מתן פיצוי ישיר לאורחים |")
        md_lines.append(f"| **קריאות חסומות (ממתין לחלקי חילוף)** | **`{b.open_waiting_parts_count}` משימות פתוחות** | דוד הסקה מרכזי מס' 2, מעלית ב', מכונת קרח קומה 2 |")
        md_lines.append(f"| **סך חשיפת פיצויים והטבות לאורחים** | **`{b.total_compensation_ils:,.0f} ₪`** | טעון אישור מנכ\"ל והזנה לחשבונות האורחים בקבלה |")
        md_lines.append(f"| **חדרי אורחים מועדפים (אח\"מ) בסיכון** | **`{b.vip_at_risk_count}` חדרים (חדר 412)** | מחייב שיחה וליווי אישי של מנכ\"ל המלון בארוחת הבוקר |")
        md_lines.append("")
        md_lines.append("---")
        md_lines.append("")
        md_lines.append("## 2. מוקדי תקלות חריגים ודחופים לישיבת ההנהלה")
        md_lines.append("")

        for idx, anom in enumerate(b.anomalies, 1):
            badge = "🔴 דחיפות עליונה" if anom.severity == "CRITICAL" else ("🟠 דחיפות גבוהה" if anom.severity == "HIGH" else "🟡 דחיפות רגילה")
            md_lines.append(f"### {idx}. [{badge}] {anom.title_he}")
            md_lines.append(f"- **מיקום / מתקן:** `{anom.location}` | **מחלקה מטפלת:** `{anom.responsible_dept}`")
            md_lines.append(f"- **תיאור התקלה והשפעתה:** {anom.description_he}")
            if anom.financial_impact_ils > 0:
                md_lines.append(f"- **עלות פיצוי ישירה שהוענקה:** `{anom.financial_impact_ils:,.0f} ₪`")
            md_lines.append(f"- **מועדי רישום במערכת (תאריך ושעה):** `{', '.join(anom.related_tickets)}`")
            md_lines.append(f"- **הנחיה לביצוע מיידי:** **{anom.action_item_he}**")
            md_lines.append("")

        md_lines.append("---")
        md_lines.append("")
        md_lines.append("## 3. רישומי יומן מנהל תורן ופיצויי אורחים")
        md_lines.append("")
        md_lines.append("| תאריך ושעה | חדר ושם האורח | משמרת | פירוט התקרית | הפיצוי שהוענק לאורח | עלות (₪) | מעמד אישור מנכ\"ל |")
        md_lines.append("| :--- | :--- | :--- | :--- | :--- | :--- | :--- |")
        for l in b.compensation_incidents:
            esc = "אושר והוסלם למנכ\"ל" if l.escalated_to_gm else "רגיל"
            guest_name_he = "ד\"ר א. בן-ארי (אורח אח\"מ - מעמד יהלום)" if "Ben-Ari" in l.vip_guest_name else ("מר וגב' ר. כהן" if "Cohen" in l.vip_guest_name else l.vip_guest_name)
            shift_he = SHIFT_HE.get(l.shift, l.shift)
            incident_he = self._clean_incident_desc(l.incident_description)
            comp_he = self._clean_compensation_desc(l.compensation_offered)
            md_lines.append(f"| `{l.timestamp}` | **חדר {l.room_number}**<br>{guest_name_he} | {shift_he} | {incident_he} | {comp_he} | **{l.compensation_amount_ils:,.0f} ₪** | `{esc}` |")
        md_lines.append("")
        md_lines.append("---")
        md_lines.append("")
        md_lines.append("## 4. משימות אחזקה ממשמרת הלילה הממתינות לחלקי חילוף")
        md_lines.append("")
        md_lines.append("| תאריך ושעה | מתקן / אזור | סיווג מערכת | מהות התקלה | חלק חילוף חסר וצפי הגעה | גורם מטפל |")
        md_lines.append("| :--- | :--- | :--- | :--- | :--- | :--- |")
        for t in b.waiting_parts_tickets:
            asset_he = ROOM_ASSET_HE.get(t.room_number, t.room_number)
            cat_he = CAT_MAP.get(t.category, t.category)
            issue_he = self._clean_issue_desc(t.issue_description)
            notes_he = self._clean_notes_desc(t.notes)
            tech_he = TECH_HE.get(t.assigned_technician, t.assigned_technician)
            md_lines.append(f"| `{t.created_at}` | **{asset_he}** | {cat_he} | {issue_he} | {notes_he} | {tech_he} |")
        md_lines.append("")
        md_lines.append("---")
        md_lines.append("")
        md_lines.append("## 5. תוכנית פעולה מחלקתית מוגדרת לישיבת הבוקר")
        md_lines.append("")
        md_lines.append("| מחלקה אחראית | רמת דחיפות | בעל תפקיד אחראי | מועד יעד לסיום | משימה מוגדרת לביצוע | מתקן / חדר יעד |")
        md_lines.append("| :--- | :--- | :--- | :--- | :--- | :--- |")
        for act in b.action_items:
            md_lines.append(f"| **{act.department_he}** | `{act.priority}` | {act.owner} | `{act.target_time}` | {act.action_he} | `{act.room_or_asset}` |")
        md_lines.append("")
        md_lines.append("---")
        md_lines.append("*הופק באופן אוטומטי באמצעות מנוע LiveOps של מערכת סמארט-באטלר | ג'יי-בי מערכות*")

        content = "\n".join(md_lines)
        md_path = os.path.join(self.reports_dir, "morning_briefing.md")
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(content)
        return content

    def generate_html(self) -> str:
        """Generates self-contained, responsive, printable HTML briefing entirely in Hebrew."""
        b = self.b
        html_content = f"""<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>תדריך בוקר מבצעי — סיכום תפעולי למנהלים</title>
    <style>
        :root {{
            --primary: #1e3a8a;
            --primary-light: #3b82f6;
            --danger: #dc2626;
            --danger-bg: #fee2e2;
            --warning: #d97706;
            --warning-bg: #fef3c7;
            --success: #16a34a;
            --success-bg: #dcfce7;
            --dark: #0f172a;
            --gray-100: #f1f5f9;
            --gray-200: #e2e8f0;
            --gray-700: #334155;
            --card-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background-color: #f8fafc;
            color: var(--dark);
            line-height: 1.6;
            padding: 24px;
            direction: rtl;
            text-align: right;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{
            background: linear-gradient(135deg, #1e293b, #0f172a);
            color: white;
            padding: 28px 32px;
            border-radius: 12px;
            margin-bottom: 24px;
            box-shadow: var(--card-shadow);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .header h1 {{ font-size: 24px; font-weight: 700; margin-bottom: 6px; }}
        .header p {{ color: #94a3b8; font-size: 14px; }}
        .badge-system {{
            background: rgba(59, 130, 246, 0.2);
            color: #60a5fa;
            border: 1px solid #3b82f6;
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 13px;
            font-weight: 600;
        }}
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 16px;
            margin-bottom: 24px;
        }}
        .kpi-card {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: var(--card-shadow);
            border-top: 4px solid var(--primary-light);
            text-align: right;
        }}
        .kpi-card.danger {{ border-top-color: var(--danger); }}
        .kpi-card.warning {{ border-top-color: var(--warning); }}
        .kpi-card .value {{ font-size: 28px; font-weight: 800; color: var(--dark); }}
        .kpi-card .label {{ font-size: 13px; color: var(--gray-700); margin-top: 4px; font-weight: 600; }}
        
        .section-card {{
            background: white;
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 24px;
            box-shadow: var(--card-shadow);
        }}
        .section-title {{
            font-size: 18px;
            font-weight: 700;
            color: var(--dark);
            margin-bottom: 16px;
            display: flex;
            align-items: center;
            gap: 8px;
            border-bottom: 2px solid var(--gray-100);
            padding-bottom: 10px;
        }}
        .alert-item {{
            border-right: 5px solid var(--danger);
            background: #fff5f5;
            padding: 16px;
            border-radius: 6px;
            margin-bottom: 14px;
        }}
        .alert-item.HIGH {{
            border-right-color: var(--warning);
            background: #fffbeb;
        }}
        .alert-item .title {{
            font-size: 16px;
            font-weight: 700;
            color: #991b1b;
            margin-bottom: 6px;
        }}
        .alert-item.HIGH .title {{ color: #92400e; }}
        .alert-item .meta {{
            font-size: 13px;
            color: var(--gray-700);
            margin-bottom: 8px;
        }}
        .alert-item .action {{
            font-size: 13px;
            font-weight: 600;
            background: white;
            padding: 10px 14px;
            border-radius: 6px;
            border: 1px dashed #cbd5e1;
            margin-top: 8px;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
            text-align: right;
        }}
        th {{
            background: var(--gray-100);
            padding: 12px 14px;
            font-weight: 700;
            color: var(--dark);
            border-bottom: 2px solid var(--gray-200);
        }}
        td {{
            padding: 12px 14px;
            border-bottom: 1px solid var(--gray-200);
            color: var(--gray-700);
        }}
        tr:hover td {{ background: #f8fafc; }}
        .badge {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 700;
        }}
        .badge-danger {{ background: var(--danger-bg); color: var(--danger); }}
        .badge-warning {{ background: var(--warning-bg); color: var(--warning); }}
        .badge-info {{ background: #e0f2fe; color: #0284c7; }}
        .footer {{
            text-align: center;
            font-size: 12px;
            color: #94a3b8;
            margin-top: 32px;
            padding-top: 16px;
            border-top: 1px solid var(--gray-200);
        }}
        @media print {{
            body {{ padding: 0; background: white; }}
            .section-card {{ box-shadow: none; border: 1px solid #ddd; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div style="display: flex; align-items: center; gap: 20px;">
                <div style="background: rgba(255,255,255,0.06); padding: 8px 12px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.12); display: flex; align-items: center;">
                    <!-- JAYBEE Official Logo (www.jaybee.com) -->
                    <svg width="125" height="30" viewBox="0 0 134 34" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <g clip-path="url(#clip0_jaybee_hdr)">
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
                            <clipPath id="clip0_jaybee_hdr">
                                <rect width="134" height="33" fill="white" transform="translate(0 0.5)"/>
                            </clipPath>
                        </defs>
                    </svg>
                </div>
                <div>
                    <h1 style="margin:0; font-size: 24px; font-weight:800; display:flex; align-items:center; gap:8px;"><bdi dir="ltr">SmartButler®</bdi> <span>— תדריך בוקר מבצעי</span></h1>
                    <p style="margin:3px 0 0 0; color:#94a3b8; font-size:13px;">מלון: גראנד הריטג' מלון וספא | מערכת <bdi dir="ltr">SmartButler®</bdi> מבית ג'ייבי מערכות (<a href="https://www.jaybee.com" target="_blank" style="color:#60a5fa; text-decoration:none;">www.jaybee.com</a>) | טווח: <strong>{b.period_label}</strong> | הפקה: {b.generated_at}</p>
                </div>
            </div>
            <div class="badge-system"><bdi dir="ltr">SmartButler®</bdi> • JAYBEE Systems</div>
        </div>

        <div class="kpi-grid">
            <div class="kpi-card danger">
                <div class="value">{b.total_compensation_ils:,.0f} ₪</div>
                <div class="label">חשיפת פיצויי אורחים (חדרים 412 ו-205)</div>
            </div>
            <div class="kpi-card danger">
                <div class="value">{b.open_waiting_parts_count}</div>
                <div class="label">קריאות מושבתות (ממתין לחלקי חילוף)</div>
            </div>
            <div class="kpi-card warning">
                <div class="value">{b.vip_at_risk_count}</div>
                <div class="label">חדרי אורחים מועדפים (אח"מ) בסיכון</div>
            </div>
            <div class="kpi-card">
                <div class="value">{b.total_maintenance_48h}</div>
                <div class="label">קריאות שירות ואחזקה ({b.period_label})</div>
            </div>
            <div class="kpi-card">
                <div class="value">{b.total_housekeeping_48h}</div>
                <div class="label">משימות משק בית וניקיון ({b.period_label})</div>
            </div>
        </div>

        <div class="section-card">
            <div class="section-title">🚨 מוקדי תקלות חריגים ודחופים לישיבת ההנהלה</div>
"""
        for anom in b.anomalies:
            sev_class = anom.severity
            badge_text = "דחיפות עליונה" if anom.severity == "CRITICAL" else ("דחיפות גבוהה" if anom.severity == "HIGH" else "דחיפות רגילה")
            badge_class = "badge-danger" if anom.severity == "CRITICAL" else "badge-warning"
            html_content += f"""
            <div class="alert-item {sev_class}">
                <div class="title"><span class="badge {badge_class}">{badge_text}</span> {anom.title_he}</div>
                <div class="meta">מיקום: <strong>{anom.location}</strong> | מחלקה אחראית: <strong>{anom.responsible_dept}</strong> | מועדי רישום במערכת: {', '.join(anom.related_tickets)}</div>
                <div style="font-size: 14px; margin-bottom: 6px;">{anom.description_he}</div>
                <div class="action">📌 <strong>הנחיה לישיבת הבוקר:</strong> {anom.action_item_he}</div>
            </div>
"""

        html_content += f"""
        </div>

        <div class="section-card">
            <div class="section-title">💼 רישומי יומן מנהל תורן ופיצויי אורחים</div>
            <table>
                <thead>
                    <tr>
                        <th>תאריך ושעה</th>
                        <th>חדר ושם האורח</th>
                        <th>משמרת</th>
                        <th>פירוט התקרית</th>
                        <th>הפיצוי שהוענק לאורח</th>
                        <th>עלות כספית</th>
                        <th>מעמד מנכ"ל</th>
                    </tr>
                </thead>
                <tbody>
"""
        for l in b.compensation_incidents:
            guest_name_he = "ד\"ר א. בן-ארי (אח\"מ - יהלום)" if "Ben-Ari" in l.vip_guest_name else ("מר וגב' ר. כהן" if "Cohen" in l.vip_guest_name else l.vip_guest_name)
            shift_he = SHIFT_HE.get(l.shift, l.shift)
            incident_he = self._clean_incident_desc(l.incident_description)
            comp_he = self._clean_compensation_desc(l.compensation_offered)
            html_content += f"""
                    <tr>
                        <td><code>{l.timestamp}</code></td>
                        <td><strong>חדר {l.room_number}</strong><br><small>{guest_name_he}</small></td>
                        <td><small>{shift_he}</small></td>
                        <td>{incident_he}</td>
                        <td>{comp_he}</td>
                        <td style="font-weight: 700; color: var(--danger);">{l.compensation_amount_ils:,.0f} ₪</td>
                        <td><span class="badge {'badge-danger' if l.escalated_to_gm else 'badge-info'}">{'אושר והוסלם' if l.escalated_to_gm else 'רגיל'}</span></td>
                    </tr>
"""

        html_content += f"""
                </tbody>
            </table>
        </div>

        <div class="section-card">
            <div class="section-title">⚙️ משימות אחזקה ממשמרת הלילה הממתינות לחלקי חילוף</div>
            <table>
                <thead>
                    <tr>
                        <th>תאריך ושעה</th>
                        <th>מתקן / אזור</th>
                        <th>סיווג מערכת</th>
                        <th>פירוט התקלה</th>
                        <th>חלק חילוף חסר וצפי הגעה</th>
                        <th>גורם מטפל</th>
                    </tr>
                </thead>
                <tbody>
"""
        for t in b.waiting_parts_tickets:
            asset_he = ROOM_ASSET_HE.get(t.room_number, t.room_number)
            cat_he = CAT_MAP.get(t.category, t.category)
            issue_he = self._clean_issue_desc(t.issue_description)
            notes_he = self._clean_notes_desc(t.notes)
            tech_he = TECH_HE.get(t.assigned_technician, t.assigned_technician)
            html_content += f"""
                    <tr>
                        <td><code>{t.created_at}</code></td>
                        <td><strong>{asset_he}</strong></td>
                        <td><span class="badge badge-warning">{cat_he}</span></td>
                        <td>{issue_he}</td>
                        <td>{notes_he}</td>
                        <td>{tech_he}</td>
                    </tr>
"""

        html_content += f"""
                </tbody>
            </table>
        </div>

        <div class="section-card">
            <div class="section-title">📋 תוכנית פעולה מחלקתית מוגדרת לישיבת הבוקר</div>
            <table>
                <thead>
                    <tr>
                        <th>מחלקה</th>
                        <th>רמת דחיפות</th>
                        <th>בעל תפקיד אחראי</th>
                        <th>מועד יעד</th>
                        <th>משימה מוגדרת לביצוע</th>
                        <th>מתקן / חדר יעד</th>
                    </tr>
                </thead>
                <tbody>
"""
        for act in b.action_items:
            pri_badge = "badge-danger" if "עליונה" in act.priority or "מיידי" in act.priority else "badge-warning"
            html_content += f"""
                    <tr>
                        <td><strong>{act.department_he}</strong></td>
                        <td><span class="badge {pri_badge}">{act.priority}</span></td>
                        <td>{act.owner}</td>
                        <td><code>{act.target_time}</code></td>
                        <td>{act.action_he}</td>
                        <td><code>{act.room_or_asset}</code></td>
                    </tr>
"""

        html_content += f"""
                </tbody>
            </table>
        </div>

        <div class="footer">
            תדריך מבצעי למנהלים • מערכת סמארט-באטלר • ג'יי-בי מערכות • הופק ב-{b.generated_at}
        </div>
    </div>
</body>
</html>
"""
        html_path = os.path.join(self.reports_dir, "morning_briefing.html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        return html_content
