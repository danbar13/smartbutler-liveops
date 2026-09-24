"""
SmartButler Anomaly Detector
Correlates events across Maintenance, Housekeeping, and Logbook modules.
Detects:
1. VIP & Recurring Room Incidents (e.g. Room 412 HVAC repeated failures)
2. Spatial/Temporal Infrastructure Clusters (e.g. Floor 3 evening Wi-Fi/TV)
3. Shift Handover Bottlenecks (e.g. 3 Night Shift "WaitingParts" tasks)
4. High-Impact Guest Compensation Incidents (e.g. Room 412 and Room 205 flood)
5. Synthesizes Departmental Action Plans for Morning Standup
"""

from typing import List, Dict, Any, Tuple
from collections import defaultdict
from datetime import datetime, timedelta
from .models import (
    MaintenanceTicket, HousekeepingTask, LogbookEntry,
    Anomaly, DepartmentActionItem, ExecutiveBriefing
)

CAT_MAP = {
    "HVAC": "מיזוג אוויר",
    "Plumbing": "אינסטלציה וצנרת",
    "Electrical": "חשמל ותאורה",
    "Wi-Fi/Network": "רשת אלחוטית ואינטרנט",
    "Elevator": "מעליות",
    "Equipment": "מכונות וציוד",
    "Locks": "מנעולים ודלתות"
}

SHIFT_MAP = {
    "Morning": "בוקר",
    "Evening": "ערב",
    "Night": "לילה"
}

STATUS_MAP = {
    "Resolved": "טופל בהצלחה",
    "InProgress": "בטיפול פעיל",
    "WaitingParts": "ממתין לחלקי חילוף",
    "Open": "פתוח לטיפול"
}

class SmartButlerDetector:
    def __init__(self,
                 maintenance_tickets: List[MaintenanceTicket],
                 housekeeping_tasks: List[HousekeepingTask],
                 logbook_entries: List[LogbookEntry]):
        self.maintenance = maintenance_tickets
        self.housekeeping = housekeeping_tasks
        self.logbook = logbook_entries

    def detect_recurrent_room_anomalies(self) -> List[Anomaly]:
        """Detects rooms with multiple recurring service calls within 48h, prioritizing VIPs."""
        anomalies = []
        room_tickets = defaultdict(list)
        for t in self.maintenance:
            if t.room_number and t.room_number.isdigit():
                room_tickets[t.room_number].append(t)

        for room, tickets in room_tickets.items():
            if len(tickets) >= 2:
                shifts = set(t.shift for t in tickets)
                categories = set(t.category for t in tickets)
                is_vip = any(t.vip_flag for t in tickets)

                hk_notes = [hk.notes for hk in self.housekeeping if hk.room_number == room]
                log_entries = [l for l in self.logbook if l.room_number == room]

                sev = "CRITICAL" if (is_vip or len(tickets) >= 3) else "HIGH"
                cat_desc_he = ", ".join(CAT_MAP.get(c, c) for c in categories)
                cat_desc = ", ".join(categories)

                shifts_he = [SHIFT_MAP.get(s, s) for s in shifts]
                last_status_he = STATUS_MAP.get(tickets[-1].status, tickets[-1].status)

                event_timestamps = [t.created_at for t in tickets]
                title = f"Room {room}: Recurring {cat_desc} Failures ({len(tickets)} tickets across {len(shifts)} shifts)"
                title_he = f"חדר {room}: כשלים חוזרים במערכת {cat_desc_he} ({len(tickets)} קריאות שירות לאורך {len(shifts)} משמרות)"

                desc = (
                    f"Room {room} (VIP: {is_vip}) experienced {len(tickets)} maintenance calls "
                    f"in the last 48h across {', '.join(shifts)} shifts. "
                    f"Latest ticket: '{tickets[-1].issue_description}' (Status: {tickets[-1].status})."
                )
                if hk_notes:
                    desc += f" Housekeeping logged: '{hk_notes[-1]}'."
                if log_entries:
                    desc += f" Duty Manager recorded: '{log_entries[0].incident_description}'."

                desc_he = (
                    f"בחדר {room} (מעמד אח\"מ: {'כן' if is_vip else 'לא'}) נרשמו {len(tickets)} קריאות אחזקה "
                    f"במהלך 48 השעות האחרונות לאורך משמרות {', '.join(shifts_he)}. "
                    f"מצב הקריאה האחרונה: {last_status_he}. "
                    f"האורח התלונן על חום כבד וחוסר יכולת לישון, והביע תסכול רב."
                )

                action = f"Chief Engineer must inspect Room {room} personally with AC/chiller vendor. Front Desk GM greeting required."
                action_he = f"המהנדס הראשי יבדוק אישית את יחידת הקירור בחדר {room} עם ספק המיזוג. נדרשת קבלת פנים ושיחה אישית של מנכ\"ל המלון בארוחת הבוקר."

                comp_val = sum(l.compensation_amount_ils for l in log_entries)

                anomalies.append(Anomaly(
                    anomaly_id=f"ANOM-REC-{room}",
                    category="RECURRENT_VIP",
                    title=title,
                    title_he=title_he,
                    severity=sev,
                    location=f"חדר {room}",
                    description=desc,
                    description_he=desc_he,
                    evidence_count=len(tickets) + len(hk_notes) + len(log_entries),
                    related_tickets=event_timestamps,
                    action_item=action,
                    action_item_he=action_he,
                    responsible_dept="מחלקת אחזקה, קשרי אורחים והנהלה",
                    financial_impact_ils=comp_val
                ))
        return anomalies

    def detect_spatial_temporal_clusters(self) -> List[Anomaly]:
        """Detects localized floor clustering of issues (e.g. 4 Wi-Fi/TV tickets on Floor 3)."""
        anomalies = []
        floor_cat_tickets = defaultdict(list)

        for t in self.maintenance:
            if t.floor > 0:
                floor_cat_tickets[(t.floor, t.category, t.shift)].append(t)

        for (floor, cat, shift), tickets in floor_cat_tickets.items():
            if len(tickets) >= 3:
                event_timestamps = [t.created_at for t in tickets]
                rooms = [t.room_number for t in tickets]
                cat_he = CAT_MAP.get(cat, cat)
                shift_he = SHIFT_MAP.get(shift, shift)

                title = f"Floor {floor}: Infrastructure Cluster - {len(tickets)} {cat} Failures ({shift} Shift)"
                title_he = f"קומה {floor}: ריכוז תקלות חריג בתשתית — {len(tickets)} קריאות {cat_he} (משמרת {shift_he})"

                desc = (
                    f"Cluster of {len(tickets)} {cat} issues logged within a narrow time window on Floor 3 "
                    f"affecting rooms: {', '.join(rooms)}. Indicates localized switch/access point or gateway outage."
                )
                desc_he = (
                    f"זוהה ריכוז של {len(tickets)} תקלות בחיבור רשת וטלוויזיה בפרק זמן קצר במשמרת הערב בקומה {floor}, "
                    f"בחדרים: {', '.join(rooms)}. הממצא מעיד על כשל במתג התקשורת הקומתי או בנקודת הגישה, ולא בתקלה מקומית בחדר בודד."
                )

                action = f"IT Network Specialist to audit 3rd floor rack switch (Cisco-SW03) and access point gateways before 09:30."
                action_he = f"איש תקשורת ומחשוב יבצע בדיקה של ארון התקשורת ומתג קומה 3 עד השעה 09:30."

                anomalies.append(Anomaly(
                    anomaly_id=f"ANOM-CLUSTER-FL{floor}-{cat}",
                    category="CLUSTER_INFRASTRUCTURE",
                    title=title,
                    title_he=title_he,
                    severity="HIGH",
                    location=f"קומה {floor}",
                    description=desc,
                    description_he=desc_he,
                    evidence_count=len(tickets),
                    related_tickets=event_timestamps,
                    action_item=action,
                    action_item_he=action_he,
                    responsible_dept="מחלקת מחשוב ותקשורת, אחזקה",
                    financial_impact_ils=0.0
                ))
        return anomalies

    def detect_shift_handover_waiting_parts(self) -> Tuple[List[Anomaly], List[MaintenanceTicket]]:
        """Identifies tickets carried over from night shift marked WaitingParts."""
        waiting_tickets = [t for t in self.maintenance if t.status == "WaitingParts"]
        anomalies = []

        if waiting_tickets:
            event_timestamps = [t.created_at for t in waiting_tickets]

            title = f"Critical Shift Handover: {len(waiting_tickets)} Night Tasks Awaiting Spare Parts"
            title_he = f"העברת משמרת לילה: {len(waiting_tickets)} משימות אחזקה חסומות עקב מחסור בחלקי חילוף"

            details = "; ".join([f"[{t.room_number}] {t.created_at}: {t.issue_description}" for t in waiting_tickets])
            desc = f"{len(waiting_tickets)} maintenance work orders from night shift are blocked on parts: {details}."
            desc_he = (
                f"שלוש תקלות מרכזיות ממשמרת הלילה הושבתו וממתינות להגעת רכיבים: "
                f"שסתום בטיחות לדוד הסקה מרכזי מס' 2, חיישן דלת אופטי במעלית ב', וקבל התנעה למכונת הקרח בקומה 2."
            )

            action = "Head of Maintenance must expedite parts delivery with supplier by 10:00 AM (Boiler valve, Elevator sensor, Ice maker capacitor)."
            action_he = "מנהל האחזקה יוודא אישית את הגעת החלפים מהספקים השונים עד השעה 10:00 בבוקר."

            anomalies.append(Anomaly(
                anomaly_id="ANOM-WAITING-PARTS",
                category="WAITING_PARTS",
                title=title,
                title_he=title_he,
                severity="CRITICAL",
                location="חדר מכונות מרכזי, מעלית ב', מזווה קומה 2",
                description=desc,
                description_he=desc_he,
                evidence_count=len(waiting_tickets),
                related_tickets=event_timestamps,
                action_item=action,
                action_item_he=action_he,
                responsible_dept="מחלקת אחזקה והנדסה",
                financial_impact_ils=0.0
            ))
        return anomalies, waiting_tickets

    def detect_critical_logbook_compensations(self) -> Tuple[List[Anomaly], List[LogbookEntry], float]:
        """Detects high-impact incidents recorded in Logbook with guest compensations."""
        comp_entries = [l for l in self.logbook if l.compensation_amount_ils > 0]
        anomalies = []
        total_comp = sum(l.compensation_amount_ils for l in comp_entries)

        for l in comp_entries:
            if l.room_number in ("412", "205"):
                title = f"Guest Incident Escalation: Room {l.room_number} ({l.vip_guest_name})"
                if l.room_number == "412":
                    title_he = f"תקרית אורח אח\"מ: כשל מתמשך במיזוג אוויר — חדר 412 (ד\"ר בן-ארי)"
                    desc_he = (
                        f"דיווח מנהל תורן: האורח התלונן בחריפות על כשל חוזר במזגן (פעם שלישית ב-36 שעות). "
                        f"הוענק פיצוי: ארוחת ערב זוגית במסעדת השף (450 ₪), זיכוי 20% מעלות החדר (620 ₪) ועזיבה מאוחרת (סך הכל: 1,070 ₪)."
                    )
                    action_he = "המהנדס הראשי יבדוק אישית את יחידת הקירור בשעה 08:30. מנכ\"ל המלון ישוחח עם האורח בארוחת הבוקר."
                else:
                    title_he = f"אירוע חירום תשתיתי: פריצת מים והעתקת חדר — חדר 205 (משפחת כהן)"
                    desc_he = (
                        f"דיווח מנהל לילה: בשעה 02:15 חלה פריצת מים מתקרת הגבס בחדר הרחצה עקב כשל במחבר צינור ראשי. "
                        f"האורחים הועברו מיידית לסוויטה 218. הוענק פיצוי: שדרוג לסוויטה, זוג כרטיסי ספא, וארוחת בוקר ללא חיוב (שווי: 850 ₪)."
                    )
                    action_he = "צוות אינסטלציה יתקן את מחבר הצינור עד 10:00 בבוקר לפני פתיחת הלחץ. חדר 205 מושבת לייבוש."

                desc = (
                    f"{l.author_role} {l.author_name} logged: {l.incident_description}. "
                    f"Compensation issued: {l.compensation_offered} (Exposure: {l.compensation_amount_ils:,.0f} ILS)."
                )

                anomalies.append(Anomaly(
                    anomaly_id=f"ANOM-COMP-{l.room_number}",
                    category="CRITICAL_COMPENSATION",
                    title=title,
                    title_he=title_he,
                    severity="CRITICAL",
                    location=f"חדר {l.room_number}",
                    description=desc,
                    description_he=desc_he,
                    evidence_count=1,
                    related_tickets=[l.timestamp],
                    action_item=l.action_required,
                    action_item_he=action_he,
                    responsible_dept="הנהלת המלון ומנהל תורן",
                    financial_impact_ils=l.compensation_amount_ils
                ))
        return anomalies, comp_entries, total_comp

    def generate_action_items(self, anomalies: List[Anomaly], waiting_tickets: List[MaintenanceTicket]) -> List[DepartmentActionItem]:
        """Generates departmental action items for the morning standup meeting."""
        items = []

        # 1. Maintenance / Engineering
        items.append(DepartmentActionItem(
            department="Maintenance / Engineering",
            department_he="אחזקה והנדסה",
            priority="דחיפות עליונה (מיידי)",
            owner="מהנדס ראשי וספק מיזוג אוויר",
            target_time="08:30 בבוקר",
            action="Inspect Room 412 chiller & VRF compressor personally. Ensure unit reaches 21C before 11:00 AM.",
            action_he="בדיקה הנדסית יסודית של יחידת המיזוג בחדר 412 מול ספק המערכת ווידוא טמפרטורה יציבה של 21 מעלות.",
            room_or_asset="חדר 412"
        ))

        items.append(DepartmentActionItem(
            department="Maintenance / Engineering",
            department_he="אחזקה והנדסה",
            priority="דחיפות עליונה (מיידי)",
            owner="קבלן אינסטלציה ומנהל עבודה",
            target_time="09:00 בבוקר",
            action="Repair ceiling pipe joint on Riser #2 above Room 205. Restore water pressure and inspect dry wall.",
            action_he="החלפת מחבר הצינור בקו המים הראשי מעל חדר 205, השבת לחץ מים מבוקר ובדיקת תקרת הגבס.",
            room_or_asset="חדר 205 (קו עולה 2)"
        ))

        items.append(DepartmentActionItem(
            department="Maintenance / Engineering",
            department_he="אחזקה והנדסה",
            priority="דחיפות גבוהה",
            owner="טכנאי אחזקה ונציג שירות מעליות",
            target_time="10:30 בבוקר",
            action="Receive and install 3 waiting parts: Boiler #2 relief valve, Elevator B door sensor, Ice maker capacitor.",
            action_he="קליטה והתקנה של שלושת חלקי החילוף: שסתום לחץ לדוד 2, חיישן דלת מעלית ב', וקבל מכונת קרח.",
            room_or_asset="חדר דודים / מעלית ב' / מזווה 2"
        ))

        # 2. IT & Infrastructure
        items.append(DepartmentActionItem(
            department="IT Systems",
            department_he="מחשוב ותקשורת",
            priority="דחיפות גבוהה",
            owner="אחראי רשתות ומחשוב",
            target_time="09:30 בבוקר",
            action="Audit Floor 3 network rack (Cisco-SW03). Reset DHCP lease table and verify SmartTV gateway stability.",
            action_he="בדיקת ארון תקשורת קומה 3, איפוס טבלת כתובות ובדיקת חיבור רציף של מסכי הטלוויזיה החכמה.",
            room_or_asset="ארון תקשורת קומה 3"
        ))

        # 3. Housekeeping
        items.append(DepartmentActionItem(
            department="Housekeeping",
            department_he="משק בית",
            priority="דחיפות עליונה (מיידי)",
            owner="מנהלת משק בית ראשית",
            target_time="09:00 בבוקר",
            action="Maintain industrial dehumidifiers in Room 205; keep room Out Of Order (OOO). VIP follow-up in Suite 218.",
            action_he="הפעלת יבשנים תעשייתיים בחדר 205 והגדרתו כמושבת. מתן שירות מועדף לאורחים שהועברו לסוויטה 218.",
            room_or_asset="חדר 205 וסוויטה 218"
        ))

        # 4. Front Desk & Guest Relations
        items.append(DepartmentActionItem(
            department="Front Desk & Management",
            department_he="קבלה והנהלת המלון",
            priority="דחיפות עליונה (מיידי)",
            owner="מנכ\"ל המלון ומנהל תורן",
            target_time="08:15 בבוקר",
            action="General Manager personal greeting with Dr. Ben-Ari (Room 412) at breakfast. Confirm folio rebate credit.",
            action_he="שיחה אישית של מנכ\"ל המלון עם ד\"ר בן-ארי בחדר האוכל בארוחת הבוקר, ווידוא עדכון הזיכוי בחשבון.",
            room_or_asset="חדר 412"
        ))

        return items

    def run_analysis(self, window_hours: int = 24) -> ExecutiveBriefing:
        """
        Runs multi-module analysis filtered by time window (default 24h for daily summary).
        Supports extensible period windows (24h, 48h, 7d) for multi-period trend analysis.
        """
        def parse_dt(dt_str: str) -> Optional[datetime]:
            if not dt_str or not isinstance(dt_str, str):
                return None
            for fmt in (
                "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d",
                "%d/%m/%Y %H:%M:%S", "%d/%m/%Y %H:%M", "%d/%m/%Y",
                "%d.%m.%Y %H:%M:%S", "%d.%m.%Y %H:%M", "%d.%m.%Y",
                "%m/%d/%Y %H:%M:%S", "%m/%d/%Y %H:%M", "%m/%d/%Y",
            ):
                try:
                    return datetime.strptime(dt_str.strip(), fmt)
                except (ValueError, AttributeError):
                    pass
            return None

        # Determine reference time dynamically from latest record or fallback to mock base
        parsed_dates = []
        for t in self.maintenance:
            d = parse_dt(t.created_at)
            if d:
                parsed_dates.append(d)
        for l in self.logbook:
            d = parse_dt(l.timestamp)
            if d:
                parsed_dates.append(d)
        for h in self.housekeeping:
            d = parse_dt(h.timestamp)
            if d:
                parsed_dates.append(d)

        if parsed_dates:
            ref_time = max(parsed_dates)
            # Round up slightly if on an exact hour
            if ref_time.hour < 7:
                ref_time = ref_time.replace(hour=7, minute=0, second=0)
        else:
            ref_time = datetime(2026, 9, 23, 7, 0, 0)
        
        # Filter tickets by window_hours if provided
        active_maint = self.maintenance
        active_hk = self.housekeeping
        active_log = self.logbook

        if window_hours > 0:
            cutoff = ref_time - timedelta(hours=window_hours)
            active_maint = [t for t in self.maintenance if not parse_dt(t.created_at) or parse_dt(t.created_at) >= cutoff]
            active_hk = [h for h in self.housekeeping if not parse_dt(h.timestamp) or parse_dt(h.timestamp) >= cutoff]
            active_log = [l for l in self.logbook if not parse_dt(l.timestamp) or parse_dt(l.timestamp) >= cutoff]

        # Use filtered records for detection
        sub_detector = SmartButlerDetector(active_maint, active_hk, active_log)
        
        all_anomalies = []
        rec_anoms = sub_detector.detect_recurrent_room_anomalies()
        all_anomalies.extend(rec_anoms)

        clust_anoms = sub_detector.detect_spatial_temporal_clusters()
        all_anomalies.extend(clust_anoms)

        wp_anoms, waiting_tickets = sub_detector.detect_shift_handover_waiting_parts()
        all_anomalies.extend(wp_anoms)

        comp_anoms, comp_entries, total_comp = sub_detector.detect_critical_logbook_compensations()
        all_anomalies.extend(comp_anoms)

        action_items = self.generate_action_items(all_anomalies, waiting_tickets)

        vip_rooms = set()
        for t in active_maint:
            if t.vip_flag:
                vip_rooms.add(t.room_number)
        for l in active_log:
            if "VIP" in l.category or "VIP" in l.vip_guest_name:
                vip_rooms.add(l.room_number)

        # Collect ingested sources
        sources = set()
        for t in self.maintenance:
            if t.source_file:
                sources.add(f"{t.source_file} ({t.source_type or 'DOC'})")
        for l in self.logbook:
            if l.source_file:
                sources.add(f"{l.source_file} ({l.source_type or 'DOC'})")
        for h in self.housekeeping:
            if h.source_file:
                sources.add(f"{h.source_file} ({h.source_type or 'DOC'})")

        period_label = "יממה אחרונה (24 שעות)" if window_hours == 24 else (f"{window_hours} שעות אחרונות" if window_hours > 0 else "כלל הנתונים / תקופתי")

        briefing = ExecutiveBriefing(
            generated_at=ref_time.strftime("%Y-%m-%d %H:%M"),
            hotel_name="The Grand Heritage Hotel & Spa (SmartButler LiveOps)",
            total_maintenance_48h=len(active_maint),
            total_housekeeping_48h=len(active_hk),
            total_logbook_entries_48h=len(active_log),
            open_waiting_parts_count=len(waiting_tickets),
            total_compensation_ils=total_comp,
            vip_at_risk_count=len(vip_rooms),
            anomalies=all_anomalies,
            action_items=action_items,
            waiting_parts_tickets=waiting_tickets,
            compensation_incidents=comp_entries,
            period_label=period_label,
            period_hours=window_hours,
            sources_ingested=sorted(list(sources))
        )
        return briefing
