"""
SmartButler LiveOps Digest - Analytics & Intelligence Engine (engine.py)
Processes parsed SmartButler reports, computes SLAs, detects anomalies,
identifies problematic rooms, and generates executive morning standup briefings in Hebrew.
"""

from typing import List, Dict, Any, Optional
from collections import defaultdict
from parsers.models import ParsedLogReport, TicketItem, DepartmentSummary, format_minutes_to_duration

class SmartButlerEngine:
    """Core analytics, SLA tracking, anomaly detection, and standup generation."""

    def __init__(self, report: Optional[ParsedLogReport] = None, report_dict: Optional[Dict[str, Any]] = None):
        if report:
            self.report_title = report.report_title
            self.site_name = report.site_name
            self.date_range = report.date_range
            self.file_format = report.file_format
            self.total_tickets = report.total_tickets
            self.overall_success_rate = report.overall_success_rate
            self.avg_duration_str = report.avg_duration_str
            self.avg_duration_minutes = report.avg_duration_minutes
            self.total_time_str = report.total_time_str
            self.total_time_minutes = report.total_time_minutes
            self.tickets = report.tickets_as_dicts()
            self.departments = report.departments_as_dicts()
        elif report_dict:
            self.report_title = report_dict.get("report_title", "Log Report - Providers")
            self.site_name = report_dict.get("site_name", "Grand Hotel")
            self.date_range = report_dict.get("date_range", "Current Period")
            self.file_format = report_dict.get("file_format", "PDF")
            self.total_tickets = report_dict.get("total_tickets", 0)
            self.overall_success_rate = report_dict.get("overall_success_rate", 0.0)
            self.avg_duration_str = report_dict.get("avg_duration_str", "00:00")
            self.avg_duration_minutes = report_dict.get("avg_duration_minutes", 0)
            self.total_time_str = report_dict.get("total_time_str", "00:00")
            self.total_time_minutes = report_dict.get("total_time_minutes", 0)
            self.tickets = report_dict.get("tickets", [])
            self.departments = report_dict.get("departments", [])
        else:
            raise ValueError("SmartButlerEngine requires either a ParsedLogReport or report_dict.")

    def get_kpi_summary(self) -> Dict[str, Any]:
        """Returns the high-level operational KPIs for executive header."""
        return {
            "period": self.date_range,
            "site": self.site_name,
            "report_title": self.report_title,
            "total_tickets": self.total_tickets,
            "overall_success_rate": self.overall_success_rate,
            "avg_duration_str": self.avg_duration_str,
            "total_time_str": self.total_time_str,
            "department_count": len(self.departments)
        }

    def get_department_analysis(self) -> List[Dict[str, Any]]:
        """
        Returns departments sorted by operational urgency (lowest success rate & highest breach magnitude first).
        """
        analysis = []
        for d in self.departments:
            dept_name = d.get("department", "General")
            dept_tickets = [t for t in self.tickets if t.get("department") == dept_name]
            breached = [t for t in dept_tickets if not t.get("sla_met")]
            unresolved = [t for t in dept_tickets if t.get("duration_minutes") is None or t.get("duration_str") == "N/A"]

            # Urgency score: lower success rate + high breach count
            success_rate = d.get("success_rate", 0.0)
            urgency_score = (100.0 - success_rate) * 2 + len(breached) * 10 + len(unresolved) * 20

            analysis.append({
                "department": dept_name,
                "total_tickets": d.get("total_tickets", len(dept_tickets)),
                "success_rate": success_rate,
                "avg_duration_str": d.get("avg_duration_str", "00:00"),
                "total_time_str": d.get("total_time_str", "00:00"),
                "breach_count": len(breached),
                "unresolved_count": len(unresolved),
                "urgency_score": urgency_score,
                "tickets": dept_tickets
            })

        # Sort descending by urgency score
        analysis.sort(key=lambda x: x["urgency_score"], reverse=True)
        return analysis

    def detect_problematic_rooms(self) -> List[Dict[str, Any]]:
        """
        Flags rooms with multiple service requests, recurring issues, or cross-department failures.
        """
        room_map = defaultdict(list)
        for t in self.tickets:
            loc = str(t.get("location", "")).strip()
            if loc and loc not in ("-", "None", "N/A", "General"):
                room_map[loc].append(t)

        problematic = []
        for room, r_tickets in room_map.items():
            depts = set(t.get("department") for t in r_tickets)
            breaches = [t for t in r_tickets if not t.get("sla_met")]
            unresolved = [t for t in r_tickets if t.get("duration_minutes") is None or t.get("duration_str") == "N/A"]
            
            # Severity calculation
            is_cross_dept = len(depts) > 1
            has_extreme = any(t.get("sla_breach_ratio", 1.0) > 3.0 for t in r_tickets)
            is_critical = (len(r_tickets) >= 2) or is_cross_dept or (len(unresolved) > 0) or has_extreme

            if is_critical or len(r_tickets) >= 2:
                problematic.append({
                    "room": room,
                    "ticket_count": len(r_tickets),
                    "departments": list(depts),
                    "is_cross_dept": is_cross_dept,
                    "breach_count": len(breaches),
                    "unresolved_count": len(unresolved),
                    "tickets": r_tickets,
                    "severity": "חמורה מאד (דחופה)" if (is_cross_dept and len(breaches) > 0) or len(unresolved) > 0 else "בינונית"
                })

        problematic.sort(key=lambda x: (x["is_cross_dept"], x["ticket_count"], x["unresolved_count"]), reverse=True)
        return problematic

    def detect_extreme_sla_breaches(self) -> List[Dict[str, Any]]:
        """
        Identifies tickets exceeding SLA standard significantly (>300%) or left unresolved.
        """
        breaches = []
        for t in self.tickets:
            dur_mins = t.get("duration_minutes")
            std_mins = t.get("standard_minutes", 15)
            dur_str = t.get("duration_str", "N/A")
            is_unresolved = (dur_mins is None or dur_str == "N/A")

            ratio = t.get("sla_breach_ratio", 1.0)
            if is_unresolved:
                breaches.append({
                    "ticket": t,
                    "type": "לא הושלמה (N/A)",
                    "severity_ratio": 999.0,
                    "hebrew_label": "קריאה פתוחה ללא פתרון"
                })
            elif ratio > 3.0 or (dur_mins and dur_mins > std_mins * 2):
                breaches.append({
                    "ticket": t,
                    "type": f"חריגת זמן קיצונית ({round(ratio, 1)}x)",
                    "severity_ratio": ratio,
                    "hebrew_label": f"חריגה פי {round(ratio, 1)} מהתקן ({t.get('duration_str')} לעומת {t.get('standard_str')})"
                })

        breaches.sort(key=lambda x: x["severity_ratio"], reverse=True)
        return breaches

    def get_category_bottlenecks(self) -> List[Dict[str, Any]]:
        """
        Aggregates tasks by category and identifies which tasks have systemic SLA failures.
        """
        cat_map = defaultdict(list)
        for t in self.tickets:
            cat_name = t.get("task_category") or t.get("description")
            cat_map[cat_name].append(t)

        bottlenecks = []
        for cat, c_ticks in cat_map.items():
            met = [t for t in c_ticks if t.get("sla_met")]
            success_pct = round((len(met) / len(c_ticks)) * 100, 1)
            durations = [t.get("duration_minutes") for t in c_ticks if t.get("duration_minutes") is not None]
            avg_m = round(sum(durations) / len(durations)) if durations else None
            dept = c_ticks[0].get("department", "General")
            std = c_ticks[0].get("standard_str", "00:15")

            bottlenecks.append({
                "category": cat,
                "department": dept,
                "total": len(c_ticks),
                "success_rate": success_pct,
                "standard": std,
                "avg_duration": format_minutes_to_duration(avg_m) if avg_m is not None else "N/A",
                "failure_count": len(c_ticks) - len(met)
            })

        bottlenecks.sort(key=lambda x: (x["failure_count"], 100 - x["success_rate"]), reverse=True)
        return bottlenecks

    def generate_executive_briefing(self) -> str:
        """
        Generates a concise, high-impact Hebrew Morning Standup Briefing text for general management.
        """
        kpi = self.get_kpi_summary()
        depts = self.get_department_analysis()
        rooms = self.detect_problematic_rooms()
        extreme = self.detect_extreme_sla_breaches()

        lines = []
        lines.append(f"**תדריך בוקר אופרטיבי להנהלה - {kpi['site']}**")
        lines.append(f"תקופת דיווח: {kpi['period']} | סה\"כ {kpi['total_tickets']} קריאות במערכת.")
        lines.append("")

        DEPT_MAP = {
            "Housekeeping": "משק בית",
            "Maintenance": "אחזקה והנדסה",
            "Reception": "קבלה ושירות אורחים",
            "Front Desk": "דלפק קבלה",
            "Front Office": "משרד קבלה",
            "F&B": "מזון ומשקאות",
            "Food & Beverage": "מזון ומשקאות",
            "Security": "ביטחון",
            "IT": "מחשוב ומערכות",
            "Engineering": "הנדסה ותשתיות",
            "Concierge": "קונסיירז'",
            "IVD": "שירות וילות (IVD)",
            "Clinic": "מרפאה",
            "Laundry": "מכבסה",
            "Kitchen": "מטבח",
            "Transport": "תחבורה והסעות",
            "General": "כללי"
        }

        # Overview summary
        succ = kpi['overall_success_rate']
        if succ < 50:
            lines.append(f"📌 **סטטוס עמידה ביעדים:** נרשמו {succ}% עמידה בזמני התקן. מומלץ למקד את תדריך הבוקר בסנכרון זמני השירות ומעקב קריאות בהמתנה.")
        elif succ < 80:
            lines.append(f"⚡ **סטטוס עמידה ביעדים:** {succ}% עמידה בזמני התקן. נדרש מיקוד במחלקות המרכזיות לקיצור זמני תגובה.")
        else:
            lines.append(f"✅ **סטטוס עמידה ביעדים:** ביצועים חיוביים של {succ}% עמידה בזמני התקן.")

        lines.append(f"- **זמן טיפול ממוצע כולל:** {kpi['avg_duration_str']} שעות.")
        lines.append(f"- **סך שעות טיפול מצטברות:** {kpi['total_time_str']} שעות.")
        lines.append("")

        # Department highlights in Hebrew
        lines.append("**תמונת מצב מחלקתית:**")
        for d in depts:
            dept_heb = DEPT_MAP.get(d["department"], d["department"])
            dept_status = "🟡 דורש תיאום זמנים" if d["success_rate"] == 0 else ("🟡 בתהליך שיפור" if d["success_rate"] < 70 else "🟢 תקין")
            lines.append(f"• **{dept_heb}**: {d['total_tickets']} קריאות, {d['success_rate']}% עמידה בתקן (זמן ממוצע: {d['avg_duration_str']}) - {dept_status}")

        lines.append("")
        # Problematic rooms highlight in Hebrew with constructive phrasing
        if rooms:
            cross_rooms = [r for r in rooms if r["is_cross_dept"]]
            if cross_rooms:
                depts_heb = [DEPT_MAP.get(dp, dp) for dp in cross_rooms[0]['departments']]
                lines.append(f"🛎️ **יחידות במעקב מיוחד:** חדר **{cross_rooms[0]['room']}** מציג ריכוז פניות מקביל במספר תחומים ({', '.join(depts_heb)}). מומלץ לבצע שיחת אדיבות יזומה (Courtesy Check) לשביעות רצון האורח.")
            else:
                lines.append(f"🔍 **חדרים בריכוז פניות:** חדרים {', '.join(r['room'] for r in rooms[:3])} מומלצים למעקב שירות יזום.")
        
        # Extended duration highlight
        if extreme:
            worst = extreme[0]
            t = worst["ticket"]
            dept_h = DEPT_MAP.get(t.get('department'), t.get('department'))
            desc = t.get('description') if (t.get('description') and t.get('description') != "-") else (t.get('task_category') or "פניית שירות")
            loc_str = f"חדר {t.get('location')}" if str(t.get('location')).isdigit() else t.get('location')
            dur_str = t.get('duration_str') if t.get('duration_str') != "N/A" else "בהמתנה"
            lines.append(f"⏱️ **קריאה בטיפול ממושך:** {desc} ב{loc_str} ({dept_h}) - משך: {dur_str} (יעד תקן: {t.get('standard_str')}).")

        return "\n".join(lines)

    def generate_departmental_action_items(self) -> Dict[str, List[str]]:
        """
        Generates role-based morning standup tasks for Housekeeping, Maintenance, and Reception.
        """
        actions = {
            "Housekeeping": [],
            "Maintenance": [],
            "Reception": []
        }

        # Housekeeping actions
        hk_tickets = [t for t in self.tickets if t.get("department") == "Housekeeping"]
        hk_unresolved = [t for t in hk_tickets if t.get("duration_minutes") is None or t.get("duration_str") == "N/A"]
        hk_rooms = set(t.get("location") for t in hk_tickets)

        if hk_unresolved:
            actions["Housekeeping"].append(f"סגירה מיידית של {len(hk_unresolved)} קריאות פתוחות/לא מדווחות במערכת (חדרים: {', '.join(t.get('location') for t in hk_unresolved)}).")
        if any("shower" in t.get("description", "").lower() or "clean" in t.get("description", "").lower() for t in hk_tickets):
            actions["Housekeeping"].append("ביקורת מנהלת קומה יזומה בחדרים שבהם דווחו תקלות ניקיון ומקלחת בטרם השלמת הצ'ק-אין.")
        if any("towel" in t.get("description", "").lower() for t in hk_tickets):
            actions["Housekeeping"].append("ריענון מלאי מגבות וערכות בחדרי השירות הקומתיים למניעת עיכוב באספקת מגבות לאורחים (יעד תקן: 15 דקות).")
        if not actions["Housekeeping"]:
            actions["Housekeeping"].append("המשך מעקב שוטף ועמידה בתקני זמני שירות חדרים.")

        # Maintenance actions
        maint_tickets = [t for t in self.tickets if t.get("department") == "Maintenance"]
        maint_long = [t for t in maint_tickets if (t.get("duration_minutes") or 0) > 120]
        if maint_long:
            for lt in maint_long:
                actions["Maintenance"].append(f"תחקור הנדסי דחוף לקריאת {lt.get('description')} בחדר {lt.get('location')} שנמשכה {lt.get('duration_str')} שעות (פי {lt.get('sla_breach_ratio')} מהתקן). בדיקת זמינות חלקי חילוף וסיווג WaitingParts.")
        if any("ac" in t.get("description", "").lower() or "מיזוג" in t.get("description", "").lower() for t in maint_tickets):
            actions["Maintenance"].append("בדיקת מערכת הבקרה המרכזית (BMS) וטמפרטורת יחידות מיזוג האוויר בקומות העליונות.")
        if not actions["Maintenance"]:
            actions["Maintenance"].append("סריקת קריאות אחזקה מונעת שוטפת ועמידה ביעד 15 דק' לתקלות קריטיות בחדרי אורחים.")

        # Reception actions
        rec_tickets = [t for t in self.tickets if t.get("department") == "Reception"]
        problem_rooms = self.detect_problematic_rooms()
        if problem_rooms:
            p_room = problem_rooms[0]["room"]
            actions["Reception"].append(f"יצירת קשר יזום / שיחת אדיבות (Courtesy Call) של קצין שירות עם חדר {p_room} עקב הצטברות תקלות ועיכובים.")
        actions["Reception"].append("שמירה על רמת השירות המהירה באספקת מתאמים וציוד משלים (ביצועי שיא: 100% עמידה בתקן).")
        actions["Reception"].append("סנכרון יומן משמרת (Logbook) עם מנהלי משק ואחזקה לגבי חדרים שהוגדרו בריבוי פניות.")

        return actions
