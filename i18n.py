"""
SmartButler® LiveOps Digest — Internationalization (i18n) Module
Provides dual-language support (Hebrew & English) for:
- UI labels, tabs, headers, buttons, and metrics
- Department names (official translations)
- Request classification & location clustering
- Executive morning standup briefing generator
- Departmental actionable directives
"""

from typing import Dict, Any, List, Optional
from collections import Counter

LANG_HE = "he"
LANG_EN = "en"

# =================================================================================================
# DEPARTMENT TRANSLATIONS
# =================================================================================================
DEPT_TRANSLATION_HE = {
    "Housekeeping": "משק בית",
    "Maintenance": "אחזקה והנדסה",
    "Reception": "קבלה ושירות אורחים",
    "Front Desk": "דלפק קבלה",
    "Front Office": "משרד קבלה",
    "Food & Beverage": "מזון ומשקאות",
    "F&B": "מזון ומשקאות",
    "Security": "ביטחון",
    "IT": "מחשוב ומערכות מידע",
    "Engineering": "הנדסה ותשתיות",
    "Concierge": "קונסיירז'",
    "IVD": "שירות וילות (IVD)",
    "Clinic": "מרפאה",
    "Laundry": "מכבסה",
    "Kitchen": "מטבח",
    "Transport": "תחבורה והסעות",
    "General": "כללי"
}

DEPT_TRANSLATION_EN = {
    "Housekeeping": "Housekeeping",
    "Maintenance": "Maintenance & Engineering",
    "Reception": "Front Desk & Guest Services",
    "Front Desk": "Front Desk",
    "Front Office": "Front Office",
    "Food & Beverage": "Food & Beverage",
    "F&B": "Food & Beverage",
    "Security": "Security & Safety",
    "IT": "IT & Systems",
    "Engineering": "Engineering & Facilities",
    "Concierge": "Concierge",
    "IVD": "In-Villa Dining (IVD)",
    "Clinic": "Medical Clinic",
    "Laundry": "Laundry Services",
    "Kitchen": "Kitchen & Culinary",
    "Transport": "Transportation & Buggy",
    "General": "General Operations",
    # Hebrew keys to English
    "משק בית": "Housekeeping",
    "אחזקה והנדסה": "Maintenance & Engineering",
    "קבלה ושירות אורחים": "Front Desk & Guest Services",
    "דלפק קבלה": "Front Desk",
    "משרד קבלה": "Front Office",
    "מזון ומשקאות": "Food & Beverage",
    "ביטחון": "Security & Safety",
    "מחשוב ומערכות מידע": "IT & Systems",
    "הנדסה ותשתיות": "Engineering & Facilities",
    "קונסיירז'": "Concierge",
    "שירות וילות (IVD)": "In-Villa Dining (IVD)",
    "מרפאה": "Medical Clinic",
    "מכבסה": "Laundry Services",
    "מטבח": "Kitchen & Culinary",
    "תחבורה והסעות": "Transportation & Buggy",
    "כללי": "General Operations"
}

def get_dept_name(dept_name: str, lang: str = LANG_HE) -> str:
    """Returns the official department name in the requested language."""
    if not dept_name:
        return "כללי" if lang == LANG_HE else "General"
    dept_clean = dept_name.strip()
    if lang == LANG_HE:
        return DEPT_TRANSLATION_HE.get(dept_clean, dept_clean)
    else:
        return DEPT_TRANSLATION_EN.get(dept_clean, dept_clean)


# =================================================================================================
# GRANULAR REQUEST CLASSIFICATION
# =================================================================================================
CATEGORY_RULES = [
    (['water', 'bottle', 'מים'], 'אספקת בקבוקי מים ושתייה', 'Water Bottles & Drinking Water Supply'),
    (['coffee', 'capsule', 'nescafe', 'creamer', 'tea', 'sugar', 'portion milk', 'קפה', 'תה', 'סוכר'], 'קפסולות קפה, תה, חלב וסוכר', 'Coffee Capsules, Tea, Milk & Sugar'),
    (['bath towel', 'towel bath', 'hand towel', 'towel hand', 'face towel', 'מגבת רחצה', 'מגבות'], 'מגבות רחצה ופנים', 'Bath & Hand Towels'),
    (['beach', 'pool towel', 'towel beach', 'חוף', 'בריכה'], 'מגבות חוף ובריכה', 'Beach & Pool Towels'),
    (['soap', 'shampoo', 'shower gel', 'dental', 'toothbrush', 'comb', 'loofah', 'sewing', 'shaving', 'lotion', 'סבון', 'שמפו', 'ערכת שיניים'], 'מוצרי טואלטיקה ורחצה (סבון, שמפו, ערכת שיניים)', 'Toiletries & Amenities (Soap, Shampoo, Dental Kit)'),
    (['toilet paper', 'tissue', 'נייר טואלט', 'טישו'], 'נייר טואלט וטישו', 'Toilet Paper & Facial Tissues'),
    (['a/c', 'ac ', 'air cond', 'cooling', 'מיזוג'], 'מיזוג אוויר ובקרת אקלים', 'Air Conditioning & Climate Control'),
    (['light', 'bulb', 'lamp', 'power', 'מנורה', 'תאורה', 'חשמל'], 'מנורה שרופה / תאורה וחשמל', 'Burnt Bulb / Lighting & Electrical'),
    (['adaptor', 'charger', 'מתאם', 'כבל'], 'מתאם חשמל ושקעים', 'Power Adapters & Outlets'),
    (['clean', 'makeup', 'make up', 'turndown', 'housekeeping', 'ניקיון'], 'ניקיון חדר ורענון (Room Make-up)', 'Room Cleaning & Refresh (Room Make-up)'),
    (['bed', 'pillow', 'duvet', 'blanket', 'linen', 'כרית', 'שמיכה', 'מצעים'], 'מצעים, כריות ושמיכות נוספות', 'Bedding, Extra Pillows & Blankets'),
    (['clog', 'leak', 'drain', 'plumb', 'סתימה', 'נזילה', 'אינסטלציה'], 'אינסטלציה, נזילות וסתימות', 'Plumbing, Leaks & Drainage'),
    (['tv', 'wifi', 'internet', 'channel', 'טלוויזיה', 'אינטרנט'], 'טלוויזיה, שלט ותקשורת Wi-Fi', 'TV, Remote Control & Wi-Fi'),
    (['laundry', 'iron', 'גיהוץ', 'כביסה'], 'שירותי כביסה וגיהוץ', 'Laundry & Ironing Services'),
    (['safe', 'כספת'], 'פתיחת כספת נעולה', 'Locked Safe Assistance'),
    (['umbrella', 'מטריה', 'מטריות'], 'מטריות וציוד גשם', 'Umbrellas & Rain Gear'),
    (['slippers', 'bathrobe', 'חלוק', 'נעלי בית'], 'חלוקי רחצה ונעלי בית', 'Bathrobes & Slippers'),
    (['life jacket', 'jacket kids', 'חגורת הצלה', 'שנירקול'], 'חגורות הצלה וציוד ימי', 'Life Jackets & Marine Safety Gear'),
    (['match box', 'ashtray', 'גפרורים', 'מאפרה'], 'גפרורים, מאפרות וציוד עישון', 'Matches, Ashtrays & Smoking Accessories'),
    (['buggy', 'culinarium', 'dhoni', 'malaafaiy', 'restaurant to villa', 'reception to', 'transport', 'הסעה', 'באגי'], 'הסעות באגי ושינוע אורחים', 'Buggy Dispatch & Guest Transport'),
]

def classify_specific_request(desc: str, cat: str, lang: str = LANG_HE) -> str:
    """Classifies granular hotel guest requests into clear service categories in either Hebrew or English."""
    desc_str = (desc or "").strip()
    cat_str = (cat or "").strip()
    text = f"{desc_str} {cat_str}".lower()

    for keywords, heb_label, en_label in CATEGORY_RULES:
        if any(k in text for k in keywords):
            return heb_label if lang == LANG_HE else en_label

    if cat_str and cat_str not in ['Service Request', 'Notified', 'Provided', 'Log Report - Providers (Descending Order)']:
        return cat_str
    if desc_str and desc_str != '-':
        return desc_str
    return 'בקשת שירות כללית' if lang == LANG_HE else 'General Service Request'

def get_location_cluster(loc: Any, lang: str = LANG_HE) -> str:
    """Groups rooms into wings / floors / clusters in either Hebrew or English."""
    loc_str = str(loc).strip()
    if loc_str.isdigit():
        if len(loc_str) >= 3:
            return f"אגף / קומה {loc_str[0]}" if lang == LANG_HE else f"Wing / Floor {loc_str[0]}"
        return f"חדרי קומה {loc_str[0]}" if lang == LANG_HE else f"Floor {loc_str[0]} Rooms"
    return "אזורים ציבוריים / וילות מיוחדות" if lang == LANG_HE else "Public Areas / Specialty Villas"


# =================================================================================================
# OFFICIAL VECTOR FLAGS (SVG)
# =================================================================================================
FLAG_IL_SVG = """<svg width="22" height="16" viewBox="0 0 220 160" style="border-radius:3px; vertical-align:middle; display:inline-block; box-shadow:0 1px 3px rgba(0,0,0,0.3); border:1px solid rgba(255,255,255,0.2);">
<rect width="220" height="160" fill="#ffffff"/>
<rect y="16" width="220" height="24" fill="#0038b8"/>
<rect y="120" width="220" height="24" fill="#0038b8"/>
<g fill="none" stroke="#0038b8" stroke-width="6.5" stroke-linejoin="round" transform="translate(110, 80) scale(1.15)">
  <polygon points="0,-28 24.2,14 -24.2,14"/>
  <polygon points="0,28 24.2,-14 -24.2,-14"/>
</g>
</svg>"""

FLAG_GB_SVG = """<svg width="22" height="16" viewBox="0 0 60 40" style="border-radius:3px; vertical-align:middle; display:inline-block; box-shadow:0 1px 3px rgba(0,0,0,0.3); border:1px solid rgba(255,255,255,0.2);">
<clipPath id="t_gb"><path d="M0,0 v40 h60 v-40 z"/></clipPath>
<clipPath id="w_gb"><path d="M0,0 L60,40 M60,0 L0,40"/></clipPath>
<g clip-path="url(#t_gb)">
  <path d="M0,0 v40 h60 v-40 z" fill="#012169"/>
  <path d="M0,0 L60,40 M60,0 L0,40" stroke="#fff" stroke-width="8"/>
  <path d="M0,0 L60,40 M60,0 L0,40" clip-path="url(#w_gb)" stroke="#C8102E" stroke-width="4"/>
  <path d="M30,0 v40 M0,20 h60" stroke="#fff" stroke-width="12"/>
  <path d="M30,0 v40 M0,20 h60" stroke="#C8102E" stroke-width="6"/>
</g>
</svg>"""

# =================================================================================================
# EXECUTIVE BRIEFING GENERATOR (DUAL LANGUAGE)
# =================================================================================================
def generate_executive_briefing(eng: Any, k: Dict[str, Any], lang: str = LANG_HE) -> str:
    """Generates the executive morning briefing in Hebrew or English with constructive hospitality phrasing."""
    depts = eng.get_department_analysis()
    rooms = eng.detect_problematic_rooms()
    extreme = eng.detect_extreme_sla_breaches()

    if lang == LANG_HE:
        raw_period = k.get("period", "תקופה שוטפת")
        clean_period = raw_period.replace("Current Period", "תקופה שוטפת").replace("Current Month", "חודש נוכחי")

        lines = []
        lines.append(f"**תדריך בוקר אופרטיבי להנהלה - {k['site']}**  \nתקופת דיווח: {clean_period} | סה\"כ {k['total_tickets']} קריאות במערכת.\n")

        succ = k['overall_success_rate']
        if succ < 50:
            lines.append(f"📌 **סטטוס עמידה ביעדים:** נרשמו {succ}% עמידה בזמני התקן. מומלץ למקד את תדריך הבוקר בסנכרון זמני השירות ומעקב קריאות בהמתנה.\n")
        elif succ < 80:
            lines.append(f"⚡ **סטטוס עמידה ביעדים:** {succ}% עמידה בזמני התקן. נדרש מיקוד במחלקות המרכזיות לקיצור זמני תגובה.\n")
        else:
            lines.append(f"✅ **סטטוס עמידה ביעדים:** ביצועים חיוביים של {succ}% עמידה בזמני התקן.\n")

        lines.append(f"- **זמן טיפול ממוצע כולל:** {k['avg_duration_str']} שעות.")
        lines.append(f"- **סה\"כ שעות טיפול מצטברות:** {k['total_time_str']} שעות.\n")

        lines.append("**תמונת מצב מחלקתית:**")
        for d in depts:
            dept_name = get_dept_name(d["department"], LANG_HE)
            dept_status = "🟢 תקין" if d["success_rate"] >= 80 else ("🟡 בתהליך שיפור" if d["success_rate"] >= 50 else "🟡 דורש תיאום זמנים")
            lines.append(f"- **{dept_name}**: {d['total_tickets']} קריאות, {d['success_rate']}% עמידה בתקן (זמן ממוצע: {d['avg_duration_str']}) - {dept_status}")

        lines.append("")
        if rooms:
            cross_rooms = [r for r in rooms if r["is_cross_dept"]]
            if cross_rooms:
                depts_str = ", ".join(get_dept_name(dp, LANG_HE) for dp in cross_rooms[0]['departments'])
                lines.append(f"🛎️ **יחידות במעקב מיוחד:** חדר **{cross_rooms[0]['room']}** מציג ריכוז פניות מקביל במספר תחומים ({depts_str}). מומלץ לבצע שיחת אדיבות יזומה (Courtesy Check) לשביעות רצון האורח.\n")
            else:
                lines.append(f"🔍 **חדרים בריכוז פניות:** חדרים {', '.join(r['room'] for r in rooms[:3])} מומלצים למעקב שירות יזום.\n")

        if extreme:
            worst = extreme[0]
            t = worst["ticket"]
            dept_name = get_dept_name(t.get('department'), LANG_HE)
            desc = t.get('description') if (t.get('description') and t.get('description') != "-") else (t.get('task_category') or "פניית שירות")
            loc_str = f"חדר {t.get('location')}" if str(t.get('location')).isdigit() else t.get('location')
            dur_str = t.get('duration_str') if t.get('duration_str') != "N/A" else "בהמתנה"
            lines.append(f"⏱️ **קריאה בטיפול ממושך:** {desc} ב{loc_str} ({dept_name}) - משך: {dur_str} (יעד תקן: {t.get('standard_str')}).")

        return "\n".join(lines)

    else:
        # English Briefing
        lines = []
        lines.append(f"**Operational Morning Standup Briefing — {k['site']}**  \nReporting Period: {k['period']} | Total System Tickets: **{k['total_tickets']}**.\n")

        succ = k['overall_success_rate']
        if succ < 50:
            lines.append(f"📌 **SLA Compliance Status:** Recorded **{succ}%** SLA compliance. Priority should be given to service synchronization and pending dispatch backlog.\n")
        elif succ < 80:
            lines.append(f"⚡ **SLA Compliance Status:** Recorded **{succ}%** SLA compliance. Focus required across key departments to shorten response times.\n")
        else:
            lines.append(f"✅ **SLA Compliance Status:** High operational standard with **{succ}%** SLA adherence.\n")

        lines.append(f"- **Overall Average Handling Time:** {k['avg_duration_str']} hrs.")
        lines.append(f"- **Cumulative Service Labor:** {k['total_time_str']} hrs.\n")

        lines.append("**Department Performance Summary:**")
        for d in depts:
            dept_name = get_dept_name(d["department"], LANG_EN)
            dept_status = "🟢 Optimal" if d["success_rate"] >= 80 else ("🟡 In Progress" if d["success_rate"] >= 50 else "🟡 Needs Coordination")
            lines.append(f"- **{dept_name}**: {d['total_tickets']} tickets, {d['success_rate']}% SLA compliance (Avg time: {d['avg_duration_str']}) — {dept_status}")

        lines.append("")
        if rooms:
            cross_rooms = [r for r in rooms if r["is_cross_dept"]]
            if cross_rooms:
                depts_str = ", ".join(get_dept_name(dp, LANG_EN) for dp in cross_rooms[0]['departments'])
                lines.append(f"🛎️ **Units Under Special Focus:** Room **{cross_rooms[0]['room']}** displays concurrent requests across multiple departments ({depts_str}). A proactive **Courtesy Check** by the Duty Manager is recommended for guest satisfaction.\n")
            else:
                lines.append(f"🔍 **Concentrated Room Requests:** Rooms {', '.join(r['room'] for r in rooms[:3])} are flagged for proactive service follow-up.\n")

        if extreme:
            worst = extreme[0]
            t = worst["ticket"]
            dept_name = get_dept_name(t.get('department'), LANG_EN)
            desc = t.get('description') if (t.get('description') and t.get('description') != "-") else (t.get('task_category') or "Service Request")
            loc_str = f"Room {t.get('location')}" if str(t.get('location')).isdigit() else t.get('location')
            dur_str = t.get('duration_str') if t.get('duration_str') != "N/A" else "Pending"
            lines.append(f"⏱️ **Extended Duration Ticket:** {desc} in {loc_str} ({dept_name}) — Duration: {dur_str} (Standard Target: {t.get('standard_str')}).")

        return "\n".join(lines)


# =================================================================================================
# DEPARTMENTAL ACTION DIRECTIVES
# =================================================================================================
def generate_departmental_action_items(engine: Any, lang: str = LANG_HE) -> Dict[str, List[str]]:
    """Generates role-based morning standup tasks in Hebrew or English."""
    actions = {
        "Housekeeping": [],
        "Maintenance": [],
        "Reception": [],
        "Front Desk": [],
        "Food & Beverage": [],
        "F&B": []
    }

    # Housekeeping actions
    hk_tickets = [t for t in engine.tickets if t.get("department") in ["Housekeeping", "משק בית"]]
    hk_unresolved = [t for t in hk_tickets if t.get("duration_minutes") is None or t.get("duration_str") == "N/A"]
    
    if lang == LANG_HE:
        if hk_unresolved:
            actions["Housekeeping"].append(f"סגירה מיידית של {len(hk_unresolved)} קריאות פתוחות/לא מדווחות במערכת (חדרים: {', '.join(str(t.get('location')) for t in hk_unresolved[:5])}).")
        if any("shower" in str(t.get("description", "")).lower() or "clean" in str(t.get("description", "")).lower() for t in hk_tickets):
            actions["Housekeeping"].append("ביקורת מנהלת קומה יזומה בחדרים שבהם דווחו תקלות ניקיון ומקלחת בטרם השלמת הצ'ק-אין.")
        if any("towel" in str(t.get("description", "")).lower() or "מגבת" in str(t.get("description", "")).lower() for t in hk_tickets):
            actions["Housekeeping"].append("ריענון מלאי מגבות וערכות בחדרי השירות הקומתיים למניעת עיכוב באספקת מגבות לאורחים (יעד תקן: 15 דקות).")
        if not actions["Housekeeping"]:
            actions["Housekeeping"].append("המשך מעקב שוטף ועמידה בתקני זמני שירות חדרים.")

        # Maintenance actions
        maint_tickets = [t for t in engine.tickets if t.get("department") in ["Maintenance", "אחזקה והנדסה", "Engineering"]]
        maint_long = [t for t in maint_tickets if (t.get("duration_minutes") or 0) > 120]
        if maint_long:
            for lt in maint_long[:2]:
                actions["Maintenance"].append(f"תחקור הנדסי דחוף לקריאת {lt.get('description')} בחדר {lt.get('location')} שנמשכה {lt.get('duration_str')} שעות (פי {lt.get('sla_breach_ratio')} מהתקן). בדיקת זמינות חלקי חילוף וסיווג WaitingParts.")
        if any("ac" in str(t.get("description", "")).lower() or "מיזוג" in str(t.get("description", "")).lower() for t in maint_tickets):
            actions["Maintenance"].append("בדיקת מערכת הבקרה המרכזית (BMS) וטמפרטורת יחידות מיזוג האוויר בקומות העליונות.")
        if not actions["Maintenance"]:
            actions["Maintenance"].append("סריקת קריאות אחזקה מונעת שוטפת ועמידה ביעד 15 דק' לתקלות קריטיות בחדרי אורחים.")

        # Reception actions
        problem_rooms = engine.detect_problematic_rooms()
        if problem_rooms:
            p_room = problem_rooms[0]["room"]
            actions["Reception"].append(f"יצירת קשר יזום / שיחת אדיבות (Courtesy Call) של קצין שירות עם חדר {p_room} עקב הצטברות תקלות ועיכובים.")
        actions["Reception"].append("שמירה על רמת השירות המהירה באספקת מתאמים וציוד משלים (ביצועי שיא: 100% עמידה בתקן).")
        actions["Reception"].append("סנכרון יומן משמרת (Logbook) עם מנהלי משק ואחזקה לגבי חדרים שהוגדרו בריבוי פניות.")
        actions["Front Desk"] = actions["Reception"]

    else:
        # English Directives
        if hk_unresolved:
            actions["Housekeeping"].append(f"Immediate closure of {len(hk_unresolved)} open/unresolved tickets in system (Rooms: {', '.join(str(t.get('location')) for t in hk_unresolved[:5])}).")
        if any("shower" in str(t.get("description", "")).lower() or "clean" in str(t.get("description", "")).lower() for t in hk_tickets):
            actions["Housekeeping"].append("Floor Supervisor proactive inspection on rooms with logged cleaning/shower issues prior to check-in completion.")
        if any("towel" in str(t.get("description", "")).lower() or "מגבת" in str(t.get("description", "")).lower() for t in hk_tickets):
            actions["Housekeeping"].append("Restock pantry towel inventories on high-demand floors to prevent delivery bottlenecks (Standard Target: 15 mins).")
        if not actions["Housekeeping"]:
            actions["Housekeeping"].append("Maintain current positive room service delivery times and standard adherence.")

        # Maintenance actions
        maint_tickets = [t for t in engine.tickets if t.get("department") in ["Maintenance", "אחזקה והנדסה", "Engineering"]]
        maint_long = [t for t in maint_tickets if (t.get("duration_minutes") or 0) > 120]
        if maint_long:
            for lt in maint_long[:2]:
                actions["Maintenance"].append(f"Urgent engineering review for '{lt.get('description')}' in Room {lt.get('location')} taking {lt.get('duration_str')} hrs ({lt.get('sla_breach_ratio')}x standard). Verify spare parts stock and WaitingParts status.")
        if any("ac" in str(t.get("description", "")).lower() or "מיזוג" in str(t.get("description", "")).lower() for t in maint_tickets):
            actions["Maintenance"].append("Inspect BMS central control telemetry and cooling coil outputs on top-floor rooms.")
        if not actions["Maintenance"]:
            actions["Maintenance"].append("Perform routine preventive maintenance sweeps; maintain 15-min critical response threshold.")

        # Reception actions
        problem_rooms = engine.detect_problematic_rooms()
        if problem_rooms:
            p_room = problem_rooms[0]["room"]
            actions["Reception"].append(f"Proactive Courtesy Call by Duty Manager to Room {p_room} regarding recurring requests and past delays.")
        actions["Reception"].append("Maintain rapid turn-around for electrical adapters and guest amenities (optimal 100% SLA).")
        actions["Reception"].append("Cross-check Duty Logbook with Housekeeping and Engineering leads for prioritized rooms.")
        actions["Front Desk"] = actions["Reception"]

    return actions


# =================================================================================================
# UI TEXT STRINGS DICTIONARY
# =================================================================================================
TEXTS = {
    LANG_HE: {
        "page_title": "SmartButler® — LiveOps Digest",
        "app_title": "SmartButler® LiveOps",
        "by_jaybee": "מבית ג'ייבי מערכות (JAYBEE Systems Ltd.) • [www.jaybee.com](https://www.jaybee.com)",
        "header_title": "SmartButler® — תדריך בוקר אופרטיבי ומעקב SLA",
        "header_subtitle_prefix": "מערכת",
        "header_subtitle_mid": "מבית ג'ייבי מערכות (",
        "header_site": "אתר",
        "no_report_selected": "טרם נבחר דוח",
        "sidebar_history": "📚 היסטוריית דוחות שמורים",
        "sidebar_select": "בחר דוח לצפייה וניתוח:",
        "sidebar_active": "[פעיל]",
        "sidebar_active_box": "**דוח פעיל כעת:** #{id}\n- קובץ: `{filename}`\n- קריאות: **{tickets}**\n- עמידה בתקן: **{rate}%**",
        "sidebar_del_btn": "🗑️ מחק דוח פעיל זה",
        "sidebar_del_success": "הדוח נמחק בהצלחה.",
        "sidebar_empty": "אין כרגע דוחות שמורים במאגר. אנא העלה דוח בלשונית ההעלאה.",
        "sidebar_quick_load": "🚀 טעינה מהירה של דוחות דוגמה",
        "sidebar_load_pdf": "📄 טען דוח PDF מקורי (Grand Hotel)",
        "sidebar_load_csv": "📊 טען דוח CSV לדוגמה",
        "sidebar_pdf_success": "דוח PDF נטען ונשמר כדוח #{id}!",
        "sidebar_csv_success": "דוח CSV נטען ונשמר כדוח #{id}!",
        "sidebar_footer": "פיתוח: מומחה מערכות תפעול מלונאיות • JAYBEE Systems",
        # Tabs
        "tab1_name": "📤 העלאת דוחות ושמירה",
        "tab2_name": "📋 תדריך להנהלה - ישיבת בוקר",
        "tab3_name": "🔍 תובנות עיקריות ומשמעותיות",
        "tab4_name": "📊 פירוט לפי מודולים ומחלקות",
        # Tab 1
        "tab1_header": "📤 קליטה, העלאה וארכיון דוחות תפעוליים",
        "tab1_up_expander": "📤 העלאת דוח סמארט-באטלר חדש למערכת (PDF / CSV / JSON)",
        "tab1_up_desc": "העלה דוחות תפעוליים שהופקו ממערכת **SmartButler** (בפורמט PDF, CSV או JSON). המערכת תפענח באופן אוטומטי את טווח התאריכים, שיוך המחלקות, יעדי התקן (Standard SLA) ומשכי הזמן.",
        "tab1_file_label": "בחר קובץ דוח סמארט-באטלר להעלאה:",
        "tab1_file_help": "תומך בדוחות 'Log Report - Providers' מ-JAYBEE Systems",
        "tab1_no_tickets_err": "⚠️ הקובץ **{filename}** נקלט, אך לא אותרו בו שורות קריאה תקינות (0 קריאות).",
        "tab1_parse_err": "שגיאה בפענוח הקובץ: {err}",
        "tab1_up_success": "✅ הדוח **{filename}** נקלט ומוגדר כעת כדוח הפעיל במערכת (דוח #{id}).",
        "tab1_title_label": "כותרת הדוח:",
        "tab1_site_label": "מלון / אתר:",
        "tab1_date_label": "טווח תאריכים:",
        "tab1_tickets_label": "סך קריאות פעילות:",
        "tab1_depts_label": "מחלקות שזוהו:",
        "tab1_sla_label": "אחוז עמידה בתקן:",
        "tab1_next_info": "💡 כעת ניתן לעבור לכרטיסייה **'📋 תדריך להנהלה - ישיבת בוקר'** או לשאר הכרטיסיות לצפייה בניתוח המלא.",
        "tab1_spec_title": "ℹ️ מבנה הדוח הנתמך",
        "tab1_spec_body": """דוחות מערכת **SmartButler (JAYBEE Systems)** כוללים:
- **מטא-דאטה**: אתר, טווח תאריכים (`Received Date: ...`).
- **היררכיה מחלקתית**: משק בית, אחזקה והנדסה, קבלה ושירות אורחים.
- **פרטי קריאה**: תאריך ושעה, חדר/מיקום, תיאור פנייה, פותח קריאה, זמן טיפול בפועל (`Duration`), נותן מענה.
- **עמידה ביעד**: תקן מוגדר מראש (`Standard`), חישוב עמידה ביעד (`%Success`).""",
        "tab1_arch_expander": "📚 ארכיון דוחות היסטוריים שמורים במאגר ({count} דוחות)",
        "tab1_arch_prompt": "👇 בחר דוח לצפייה בעמודה הימנית ביותר (או בלחיצה על השורה):",
        "tab1_active_banner": "🟢 **דוח נבחר ופעיל בכל הכרטיסיות:** דוח #{id} • {site} • תקופה: **{period}** ({tickets} קריאות • עמידה בתקן: **{rate}%**)",
        "tab1_del_active_btn": "🗑️ מחק דוח זה מהמאגר",
        "tab1_del_confirm": "דוח #{id} נמחק בהצלחה.",
        "tab1_no_history": "אין כרגע דוחות בהיסטוריה.",
        # Table 1 Columns
        "t1_col_select": "בחירה",
        "t1_col_status": "סטטוס",
        "t1_col_id": "מזהה",
        "t1_col_hotel": "מלון",
        "t1_col_period": "תקופת הדוח",
        "t1_col_tickets": "סך קריאות",
        "t1_col_sla": "% עמידה בתקן",
        "t1_col_avg": "זמן ממוצע",
        "t1_col_file": "קובץ מקור",
        # Tab 2
        "no_report_warn": "⚠️ טרם נטען דוח פעיל. אנא העלה או בחר דוח בלשונית 'העלאת דוחות ושמירה'.",
        "tab2_brief_header": "📋 תדריך בוקר אופרטיבי להנהלת המלון",
        "tab2_brief_meta": "תקופת הדוח: <strong>{period}</strong> | אתר: <strong>{site}</strong> | מזהה דוח: #{id}",
        "kpi_total_tickets": "סך קריאות",
        "kpi_active_depts": "{count} מחלקות פעילות",
        "kpi_sla": "עמידה בזמני תקן (SLA)",
        "kpi_sla_ok": "עמידה ביעד",
        "kpi_sla_improve": "בתהליך שיפור",
        "kpi_sla_monitor": "במעקב שירות",
        "kpi_avg_duration": "זמן טיפול ממוצע",
        "kpi_avg_sub": "שעות:דקות",
        "kpi_total_time": "סך שעות טיפול מצטברות",
        "kpi_total_sub": "כלל המחלקות",
        "tab2_briefing_expander": "🗣️ תמצית מנהלים והנחיות תפעוליות לישיבת הבוקר",
        "tab2_dept_comp_expander": "🏢 השוואה מחלקתית מרוכזת ({count} מחלקות)",
        "t2_col_dept": "מחלקה",
        "t2_col_tickets": "סך קריאות",
        "t2_col_sla": "עמידה בתקן (%)",
        "t2_col_avg": "זמן ממוצע",
        "t2_col_total": "סך שעות",
        "t2_col_status": "סטטוס תפעולי",
        "status_optimal_100": "🟢 תקין (100%)",
        "status_improving": "🟡 בתהליך שיפור",
        "status_needs_coordination": "🟡 דורש תיאום זמנים",
        # Tab 3
        "tab3_header": "🔍 תובנות עומק, מעקב זמנים ומוקדי שיפור תפעולי",
        "tab3_caption": "💡 לחץ על כל נושא כדי לפתוח או לסגור את פירוט הנתונים והטבלאות:",
        "t3_sec1_title": "🛎️ 1. יחידות וחדרים במעקב שירות מיוחד (ריכוז פניות) — {count} יחידות",
        "t3_sec1_none": "לא אותרו חדרים בריכוז פניות מיוחד בתקופת הדוח.",
        "t3_sec1_col_room": "חדר / יחידה",
        "t3_sec1_col_depts": "מחלקות מעורבות",
        "t3_sec1_col_tickets": "סך פניות",
        "t3_sec1_col_unresolved": "פניות פתוחות/בהמתנה",
        "t3_sec1_col_class": "סיווג מעקב",
        "t3_sec1_col_rec": "המלצה תפעולית",
        "t3_sec1_courtesy": "שיחת אדיבות יזומה לאורח (Courtesy Check)",
        "t3_sec1_routine": "מעקב מנהל תורן שוטף",
        "t3_sec1_cross_class": "ריכוז פניות רב-מחלקתי",
        "t3_sec1_single_class": "ריכוז פניות",
        "t3_sec2_title": "🔁 2. מוקדי בקשות ותקלות חוזרות באותו חדר או קומה — {rooms} מוקדי חדרים | {floors} אגפים",
        "t3_sec2_subtab_room": "📍 תקלות ובקשות חוזרות באותו חדר (2 מופעים ומעלה)",
        "t3_sec2_subtab_floor": "🏢 ניתוח עומסי שירות וריכוז לפי קומה / אגף",
        "t3_sec2_room_none": "לא זוהו מוקדי תקלות חוזרות כרוניות באותו חדר.",
        "t3_sec2_room_col_room": "חדר / יחידה",
        "t3_sec2_room_col_type": "סוג בקשה / תקלה חוזרת",
        "t3_sec2_room_col_count": "מופעים חוזרים",
        "t3_sec2_room_col_dept": "מחלקה",
        "t3_sec2_room_col_avg": "זמן טיפול ממוצע",
        "t3_sec2_room_col_rec": "המלצה תפעולית למניעת הישנות",
        "t3_sec2_rec_high": "אספקה מוגדלת מראש / וידוא פיזי של מנהל תורן",
        "t3_sec2_rec_normal": "מעקב לוודא שביעות רצון האורח",
        "t3_sec2_floor_col_cluster": "קומה / אגף",
        "t3_sec2_floor_col_total": "סך פניות באגף",
        "t3_sec2_floor_col_top3": "3 הפניות המובילות באגף",
        "t3_sec2_floor_col_insight": "תובנה תפעולית",
        "t3_sec2_floor_heavy": "עומס אספקה מרוכז - מומלץ ריכוז מלאי ביניים בעמדת הקומה",
        "t3_sec2_floor_normal": "פעילות שוטפת תקינה",
        "t3_sec3_title": "📊 3. שכיחות בקשות שירות ותקלות נפוצות במלון — {count} קטגוריות מוגדרות",
        "t3_sec3_col_cat": "סוג בקשה / תקלה מפורטת",
        "t3_sec3_col_total": "סך מופעים במלון",
        "t3_sec3_col_dept": "מחלקה מובילה",
        "t3_sec3_col_sla": "% עמידה בתקן",
        "t3_sec3_col_avg": "זמן ממוצע בפועל",
        "t3_sec3_col_status": "סטטוס תפעולי",
        "t3_sec3_stat_target": "🟢 עמידה ביעד",
        "t3_sec3_stat_monitor": "🟡 דורש מעקב זמנים",
        "t3_sec3_stat_ok": "🔵 תקין",
        "t3_sec4_title": "⏱️ 4. מעקב קריאות בטיפול ממושך (מעבר ליעד התקן) — {count} קריאות",
        "t3_sec4_none": "כלל הקריאות עומדות בטווח הזמנים המוגדר.",
        "t3_sec4_col_dept": "מחלקה",
        "t3_sec4_col_loc": "חדר / מיקום",
        "t3_sec4_col_desc": "תיאור פנייה מפורט",
        "t3_sec4_col_dur": "משך בפועל",
        "t3_sec4_col_sla": "יעד תקן (SLA)",
        "t3_sec4_col_ratio": "מעקב זמנים",
        "t3_sec4_col_creator": "פותח פנייה",
        "t3_sec4_col_resolver": "מבצע",
        "t3_sec4_ratio_str": "פי {ratio:.1f} מהתקן",
        "t3_sec4_unres_str": "קריאה פתוחה בהמתנה",
        "t3_sec5_title": "👥 5. אנשי צוות במעקב עמידה בזמני תקן — {count} אנשי צוות שחרגו מהתקן",
        "t3_sec5_none": "כלל אנשי הצוות עמדו בזמני התקן ללא חריגות.",
        "t3_sec5_col_staff": "איש צוות (מבצע)",
        "t3_sec5_col_dept": "מחלקה",
        "t3_sec5_col_breaches": "חריגות מתקן (מופעים)",
        "t3_sec5_col_total": "סך משימות שבוצעו",
        "t3_sec5_col_sla": "% עמידה בתקן",
        "t3_sec5_col_avg_breach": "זמן ממוצע בחריגות",
        "t3_sec5_col_sample": "דוגמה לקריאה שחרגה מהתקן",
        # Tab 4
        "tab4_header": "📊 פירוט מודולים תפעוליים והנחיות לפעולה",
        "tab4_caption": "💡 לחץ על כל מחלקה כדי לפתוח או לסגור את פירוט הפניות, המדדים וההנחיות:",
        "tab4_status_ok": "🟢 ביצועים תקינים",
        "tab4_status_improve": "🟡 בתהליך שיפור",
        "tab4_status_coords": "🟡 דורש תיאום זמנים",
        "tab4_expander_title": "{icon} מחלקת {dept_name} — {tickets} קריאות | {succ}% עמידה בתקן | {status}",
        "tab4_mc_tickets": "סך פניות",
        "tab4_mc_sla": "עמידה בתקן",
        "tab4_mc_avg": "זמן טיפול ממוצע",
        "tab4_mc_breaches": "פניות במעקב זמנים / בהמתנה",
        "tab4_actions_title": "##### 📌 תובנות לפעולה לישיבת הבוקר:",
        "tab4_tickets_title": "##### 📋 פירוט מלא של קריאות המחלקה:",
        "tab4_no_tickets": "אין קריאות רשומות למחלקה זו.",
        "t4_col_received": "מועד קבלה",
        "t4_col_loc": "מיקום / חדר",
        "t4_col_desc": "תיאור קריאה",
        "t4_col_dur": "זמן טיפול בפועל",
        "t4_col_sla": "יעד תקן (SLA)",
        "t4_col_status": "סטטוס יעד",
        "t4_col_creator": "פותח פנייה",
        "t4_col_resolver": "מבצע / נותן מענה",
        "t4_stat_met": "✅ עמד בתקן",
        "t4_stat_open": "⏳ קריאה פתוחה",
        "t4_stat_breach": "⏱️ חריגה מהתקן",
        "room_prefix": "חדר ",
        "pending_label": "בהמתנה",
        "waiting_close": "ממתין לסגירה",
        "hours_suffix": " ש'",
        "mins_suffix": " דק'",
        "times_suffix": " פעמים",
        "no_data_table": "אין נתונים להצגה בטבלה זו."
    },
    LANG_EN: {
        "page_title": "SmartButler® — LiveOps Digest",
        "app_title": "SmartButler® LiveOps",
        "by_jaybee": "By JAYBEE Systems Ltd. • [www.jaybee.com](https://www.jaybee.com)",
        "header_title": "SmartButler® — Operational Morning Briefing & SLA Tracking",
        "header_subtitle_prefix": "",
        "header_subtitle_mid": "System by JAYBEE Systems Ltd. (",
        "header_site": "Property",
        "no_report_selected": "No report selected",
        "sidebar_history": "📚 Saved Reports History",
        "sidebar_select": "Select report for analysis:",
        "sidebar_active": "[Active]",
        "sidebar_active_box": "**Active Report:** #{id}\n- File: `{filename}`\n- Tickets: **{tickets}**\n- SLA Adherence: **{rate}%**",
        "sidebar_del_btn": "🗑️ Delete active report",
        "sidebar_del_success": "Report deleted successfully.",
        "sidebar_empty": "No saved reports in database. Please upload a report in the ingestion tab.",
        "sidebar_quick_load": "🚀 Quick Load Sample Reports",
        "sidebar_load_pdf": "📄 Load Original PDF Report (Grand Hotel)",
        "sidebar_load_csv": "📊 Load Sample CSV Report",
        "sidebar_pdf_success": "PDF Report loaded and saved as Report #{id}!",
        "sidebar_csv_success": "CSV Report loaded and saved as Report #{id}!",
        "sidebar_footer": "Engineered by Hotel Operations Systems Expert • JAYBEE Systems",
        # Tabs
        "tab1_name": "📤 Report Ingestion & Archive",
        "tab2_name": "📋 Executive Standup Briefing",
        "tab3_name": "🔍 Key Operational Insights",
        "tab4_name": "📊 Department Modules & Logs",
        # Tab 1
        "tab1_header": "📤 Operational Report Ingestion, Upload & Archive",
        "tab1_up_expander": "📤 Upload New SmartButler Report (PDF / CSV / JSON)",
        "tab1_up_desc": "Upload operational service reports generated from **SmartButler** (PDF, CSV, or JSON format). The engine automatically extracts date ranges, department allocations, Standard SLA targets, and resolution durations.",
        "tab1_file_label": "Choose a SmartButler report file to upload:",
        "tab1_file_help": "Supports 'Log Report - Providers' by JAYBEE Systems",
        "tab1_no_tickets_err": "⚠️ The file **{filename}** was read, but no valid ticket records were found (0 tickets).",
        "tab1_parse_err": "Error parsing file: {err}",
        "tab1_up_success": "✅ Report **{filename}** successfully ingested and set as active (Report #{id}).",
        "tab1_title_label": "Report Title:",
        "tab1_site_label": "Property / Site:",
        "tab1_date_label": "Date Range:",
        "tab1_tickets_label": "Total Active Tickets:",
        "tab1_depts_label": "Identified Departments:",
        "tab1_sla_label": "SLA Compliance Rate:",
        "tab1_next_info": "💡 You can now proceed to the **'📋 Executive Standup Briefing'** tab or other tabs to review the full analysis.",
        "tab1_spec_title": "ℹ️ Supported Report Structure",
        "tab1_spec_body": """**SmartButler (JAYBEE Systems)** operational reports contain:
- **Metadata**: Property site, date range (`Received Date: ...`).
- **Department Hierarchy**: Housekeeping, Maintenance & Engineering, Front Desk.
- **Ticket Details**: Timestamp, room/location, request description, creator, actual handling time (`Duration`), resolver.
- **SLA Adherence**: Preset SLA standard (`Standard`), compliance calculation (`%Success`).""",
        "tab1_arch_expander": "📚 Historical Reports Archive ({count} reports)",
        "tab1_arch_prompt": "👇 Select a report to view in the leftmost column (or click any row):",
        "tab1_active_banner": "🟢 **Selected Active Report Across All Tabs:** Report #{id} • {site} • Period: **{period}** ({tickets} tickets • SLA Adherence: **{rate}%**)",
        "tab1_del_active_btn": "🗑️ Delete this report from database",
        "tab1_del_confirm": "Report #{id} deleted successfully.",
        "tab1_no_history": "No reports currently saved in history.",
        # Table 1 Columns
        "t1_col_select": "Select",
        "t1_col_status": "Status",
        "t1_col_id": "ID",
        "t1_col_hotel": "Property",
        "t1_col_period": "Report Period",
        "t1_col_tickets": "Total Tickets",
        "t1_col_sla": "% SLA Met",
        "t1_col_avg": "Avg Duration",
        "t1_col_file": "Source File",
        # Tab 2
        "no_report_warn": "⚠️ No active report loaded. Please upload or select a report in the 'Report Ingestion & Archive' tab.",
        "tab2_brief_header": "📋 Operational Morning Briefing for Hotel Management",
        "tab2_brief_meta": "Report Period: <strong>{period}</strong> | Property: <strong>{site}</strong> | Report ID: #{id}",
        "kpi_total_tickets": "Total Tickets",
        "kpi_active_depts": "{count} active departments",
        "kpi_sla": "SLA Compliance Rate",
        "kpi_sla_ok": "On Target",
        "kpi_sla_improve": "Improving",
        "kpi_sla_monitor": "Service Monitoring",
        "kpi_avg_duration": "Avg Handling Time",
        "kpi_avg_sub": "Hours:Mins",
        "kpi_total_time": "Cumulative Service Labor",
        "kpi_total_sub": "All Departments",
        "tab2_briefing_expander": "🗣️ Executive Summary & Operational Directives for Morning Briefing",
        "tab2_dept_comp_expander": "🏢 Consolidated Departmental Comparison ({count} departments)",
        "t2_col_dept": "Department",
        "t2_col_tickets": "Total Tickets",
        "t2_col_sla": "SLA Compliance (%)",
        "t2_col_avg": "Avg Duration",
        "t2_col_total": "Total Hours",
        "t2_col_status": "Operational Status",
        "status_optimal_100": "🟢 Optimal (100%)",
        "status_improving": "🟡 Improving",
        "status_needs_coordination": "🟡 Needs Coordination",
        # Tab 3
        "tab3_header": "🔍 Deep Operational Insights, SLA Monitoring & Service Bottlenecks",
        "tab3_caption": "💡 Click each topic to expand or collapse data details and tables:",
        "t3_sec1_title": "🛎️ 1. Units & Rooms Under Special Service Focus (Request Concentration) — {count} units",
        "t3_sec1_none": "No rooms identified with concentrated service requests during this reporting period.",
        "t3_sec1_col_room": "Room / Unit",
        "t3_sec1_col_depts": "Involved Departments",
        "t3_sec1_col_tickets": "Total Requests",
        "t3_sec1_col_unresolved": "Open / Pending",
        "t3_sec1_col_class": "Tracking Level",
        "t3_sec1_col_rec": "Operational Recommendation",
        "t3_sec1_courtesy": "Proactive Courtesy Check by Duty Manager",
        "t3_sec1_routine": "Routine Duty Manager Follow-up",
        "t3_sec1_cross_class": "Cross-Department Concentration",
        "t3_sec1_single_class": "Request Concentration",
        "t3_sec2_title": "🔁 2. Recurring Requests & Issues by Room or Floor — {rooms} room clusters | {floors} wings",
        "t3_sec2_subtab_room": "📍 Recurring Requests in Same Room (2+ occurrences)",
        "t3_sec2_subtab_floor": "🏢 Service Load & Request Clustering by Floor / Wing",
        "t3_sec2_room_none": "No chronic recurring issues identified in any single room.",
        "t3_sec2_room_col_room": "Room / Unit",
        "t3_sec2_room_col_type": "Recurring Request / Issue Type",
        "t3_sec2_room_col_count": "Occurrences",
        "t3_sec2_room_col_dept": "Department",
        "t3_sec2_room_col_avg": "Avg Handling Time",
        "t3_sec2_room_col_rec": "Preventive Recommendation",
        "t3_sec2_rec_high": "Pre-emptive supply / Physical inspection by Duty Manager",
        "t3_sec2_rec_normal": "Follow-up to ensure guest satisfaction",
        "t3_sec2_floor_col_cluster": "Floor / Wing",
        "t3_sec2_floor_col_total": "Total Requests in Wing",
        "t3_sec2_floor_col_top3": "Top 3 Requests in Wing",
        "t3_sec2_floor_col_insight": "Operational Insight",
        "t3_sec2_floor_heavy": "High supply load - consider intermediate floor pantry stocking",
        "t3_sec2_floor_normal": "Standard operational pace",
        "t3_sec3_title": "📊 3. Frequency of Specific Guest Requests & Hotel Issues — {count} defined categories",
        "t3_sec3_col_cat": "Detailed Request / Issue Type",
        "t3_sec3_col_total": "Total Occurrences",
        "t3_sec3_col_dept": "Primary Department",
        "t3_sec3_col_sla": "% SLA Compliance",
        "t3_sec3_col_avg": "Avg Duration",
        "t3_sec3_col_status": "Operational Status",
        "t3_sec3_stat_target": "🟢 Target Met",
        "t3_sec3_stat_monitor": "🟡 Needs Time Monitoring",
        "t3_sec3_stat_ok": "🔵 Normal",
        "t3_sec4_title": "⏱️ 4. Calls Under Extended Duration Tracking (Beyond SLA Standard) — {count} tickets",
        "t3_sec4_none": "All service tickets were resolved within their defined standard timeframes.",
        "t3_sec4_col_dept": "Department",
        "t3_sec4_col_loc": "Room / Location",
        "t3_sec4_col_desc": "Detailed Request Description",
        "t3_sec4_col_dur": "Actual Duration",
        "t3_sec4_col_sla": "Standard Target (SLA)",
        "t3_sec4_col_ratio": "Time Tracking",
        "t3_sec4_col_creator": "Created By",
        "t3_sec4_col_resolver": "Assigned / Resolver",
        "t3_sec4_ratio_str": "{ratio:.1f}x SLA Standard",
        "t3_sec4_unres_str": "Open Pending Ticket",
        "t3_sec5_title": "👥 5. Staff Members Under SLA Compliance Monitoring — {count} staff exceeding schedule",
        "t3_sec5_none": "All staff members met their SLA targets with zero excessive delays.",
        "t3_sec5_col_staff": "Staff Member (Resolver)",
        "t3_sec5_col_dept": "Department",
        "t3_sec5_col_breaches": "SLA Breaches (Count)",
        "t3_sec5_col_total": "Total Tasks Completed",
        "t3_sec5_col_sla": "% SLA Compliance",
        "t3_sec5_col_avg_breach": "Avg Breach Duration",
        "t3_sec5_col_sample": "Sample Breached Ticket",
        # Tab 4
        "tab4_header": "📊 Department Operational Modules & Directives",
        "tab4_caption": "💡 Click each department to expand or collapse request logs, metrics, and directives:",
        "tab4_status_ok": "🟢 Optimal Performance",
        "tab4_status_improve": "🟡 Improving",
        "tab4_status_coords": "🟡 Needs Coordination",
        "tab4_expander_title": "{icon} {dept_name} — {tickets} tickets | {succ}% SLA Compliance | {status}",
        "tab4_mc_tickets": "Total Requests",
        "tab4_mc_sla": "SLA Compliance",
        "tab4_mc_avg": "Avg Handling Time",
        "tab4_mc_breaches": "Pending / Breached Requests",
        "tab4_actions_title": "##### 📌 Actionable Directives for Morning Briefing:",
        "tab4_tickets_title": "##### 📋 Complete Department Ticket Log:",
        "tab4_no_tickets": "No logged tickets for this department.",
        "t4_col_received": "Received At",
        "t4_col_loc": "Location / Room",
        "t4_col_desc": "Request Description",
        "t4_col_dur": "Actual Duration",
        "t4_col_sla": "Standard Target (SLA)",
        "t4_col_status": "SLA Status",
        "t4_col_creator": "Created By",
        "t4_col_resolver": "Assigned / Resolver",
        "t4_stat_met": "✅ Met SLA",
        "t4_stat_open": "⏳ Open Ticket",
        "t4_stat_breach": "⏱️ SLA Breached",
        "room_prefix": "Room ",
        "pending_label": "Pending",
        "waiting_close": "Awaiting Closure",
        "hours_suffix": " hrs",
        "mins_suffix": " mins",
        "times_suffix": " times",
        "no_data_table": "No data to display in this table."
    }
}

def t(key: str, lang: str = LANG_HE, **kwargs) -> str:
    """Helper to retrieve translated text formatted with kwargs."""
    lang_dict = TEXTS.get(lang, TEXTS[LANG_HE])
    raw = lang_dict.get(key, TEXTS[LANG_HE].get(key, key))
    if kwargs:
        try:
            return raw.format(**kwargs)
        except Exception:
            return raw
    return raw
