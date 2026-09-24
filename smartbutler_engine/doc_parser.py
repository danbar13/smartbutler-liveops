"""
SmartButler Multi-Format Document Ingestion Engine
Extracts operational shift reports, maintenance work orders, and duty manager logs
from PDF, Word (.docx), and Excel (.xlsx, .xls, .csv) documents.
"""

import os
import io
import re
import csv
from typing import List, Dict, Any, Tuple, Union, Optional
from datetime import datetime
import pandas as pd
from pypdf import PdfReader
import docx

from .models import MaintenanceTicket, HousekeepingTask, LogbookEntry

class DocumentParser:
    """
    Ingests and normalizes operational hotel reports from PDF, Word, and Excel files.
    """

    def __init__(self):
        pass

    def parse_file(self, file_source: Union[str, io.BytesIO, bytes], filename: str) -> Tuple[List[MaintenanceTicket], List[HousekeepingTask], List[LogbookEntry]]:
        """
        Detects file type by extension and delegates parsing.
        Returns tuple of (maintenance_tickets, housekeeping_tasks, logbook_entries).
        """
        ext = os.path.splitext(filename)[1].lower().lstrip(".")
        if ext == "pdf":
            return self.parse_pdf(file_source, filename)
        elif ext in ("docx", "doc"):
            return self.parse_docx(file_source, filename)
        elif ext in ("xlsx", "xls", "csv"):
            return self.parse_excel(file_source, filename)
        else:
            raise ValueError(f"Unsupported file format: {ext}. Supported: PDF, DOCX, XLSX, XLS, CSV.")

    # -------------------------------------------------------------
    # 1. PDF EXTRACTION
    # -------------------------------------------------------------
    def parse_pdf(self, file_source: Union[str, io.BytesIO, bytes], filename: str = "report.pdf") -> Tuple[List[MaintenanceTicket], List[HousekeepingTask], List[LogbookEntry]]:
        maintenance: List[MaintenanceTicket] = []
        housekeeping: List[HousekeepingTask] = []
        logbook: List[LogbookEntry] = []

        if isinstance(file_source, (bytes, bytearray)):
            stream = io.BytesIO(file_source)
        elif isinstance(file_source, io.BytesIO):
            stream = file_source
        else:
            stream = open(file_source, "rb")

        reader = PdfReader(stream)
        all_text = ""
        for page in reader.pages:
            t = page.extract_text() or ""
            all_text += t + "\n"

        lines = [line.strip() for line in all_text.splitlines() if line.strip()]
        
        # Heuristic extraction of tickets and logs from text lines
        for i, line in enumerate(lines):
            # Check for Maintenance Ticket patterns (e.g., MNT-XXXX or קריאה)
            if re.search(r"(MNT-\d+|קריאה\s*[:#]?\s*\d+)", line, re.IGNORECASE):
                t = self._extract_maintenance_from_line(line, lines, i, filename, "PDF")
                if t:
                    maintenance.append(t)
            # Check for Logbook patterns (e.g. LOG-XXXX or יומן or פיצוי)
            elif re.search(r"(LOG-\d+|יומן\s*[:#]?|פיצוי\s*[:#]?\s*\d+)", line, re.IGNORECASE):
                l = self._extract_logbook_from_line(line, lines, i, filename, "PDF")
                if l:
                    logbook.append(l)
            # Check for Housekeeping patterns (e.g. HK-XXXX or ניקיון)
            elif re.search(r"(HK-\d+|משק\s*בית|חדר\s*\d+\s*(נקי|מלוכלך|בדוק))", line, re.IGNORECASE):
                h = self._extract_housekeeping_from_line(line, lines, i, filename, "PDF")
                if h:
                    housekeeping.append(h)

        return maintenance, housekeeping, logbook

    # -------------------------------------------------------------
    # 2. WORD (.DOCX) EXTRACTION
    # -------------------------------------------------------------
    def parse_docx(self, file_source: Union[str, io.BytesIO, bytes], filename: str = "report.docx") -> Tuple[List[MaintenanceTicket], List[HousekeepingTask], List[LogbookEntry]]:
        maintenance: List[MaintenanceTicket] = []
        housekeeping: List[HousekeepingTask] = []
        logbook: List[LogbookEntry] = []

        if isinstance(file_source, (bytes, bytearray)):
            stream = io.BytesIO(file_source)
        elif isinstance(file_source, io.BytesIO):
            stream = file_source
        else:
            stream = file_source

        doc = docx.Document(stream)

        # 1. Parse tables in DOCX
        for table in doc.tables:
            if not table.rows:
                continue
            headers = [cell.text.strip().lower() for cell in table.rows[0].cells]
            
            # Identify table module by headers
            headers_str = " ".join(headers)
            is_maint = any(k in h for h in headers for k in ["קריאה", "ticket", "תקלה", "מתקן", "חלפים", "טכנאי", "אחזקה"])
            is_log = any(k in h for h in headers for k in ["יומן", "log", "פיצוי", "אורח", "הסלמה", "תקרית"])
            is_hk = any(k in h for h in headers for k in ["משק בית", "housekeeper", "ניקיון", "סטטוס חדר", "משק"])

            for row in table.rows[1:]:
                vals = [c.text.strip() for c in row.cells]
                row_dict = dict(zip(headers, vals))

                if is_maint and not is_log:
                    t = self._row_to_maintenance(row_dict, filename, "DOCX")
                    if t:
                        maintenance.append(t)
                elif is_log:
                    l = self._row_to_logbook(row_dict, filename, "DOCX")
                    if l:
                        logbook.append(l)
                elif is_hk:
                    h = self._row_to_housekeeping(row_dict, filename, "DOCX")
                    if h:
                        housekeeping.append(h)
                elif is_maint:
                    t = self._row_to_maintenance(row_dict, filename, "DOCX")
                    if t:
                        maintenance.append(t)

        # 2. Parse unstructured paragraphs
        para_lines = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
        for i, line in enumerate(para_lines):
            if re.search(r"MNT-\d+", line) and not any(t.ticket_id in line for t in maintenance):
                t = self._extract_maintenance_from_line(line, para_lines, i, filename, "DOCX")
                if t:
                    maintenance.append(t)
            elif re.search(r"LOG-\d+", line) and not any(l.log_id in line for l in logbook):
                l = self._extract_logbook_from_line(line, para_lines, i, filename, "DOCX")
                if l:
                    logbook.append(l)

        return maintenance, housekeeping, logbook

    # -------------------------------------------------------------
    # 3. EXCEL (.XLSX, .XLS, .CSV) EXTRACTION
    # -------------------------------------------------------------
    def parse_excel(self, file_source: Union[str, io.BytesIO, bytes], filename: str = "report.xlsx") -> Tuple[List[MaintenanceTicket], List[HousekeepingTask], List[LogbookEntry]]:
        maintenance: List[MaintenanceTicket] = []
        housekeeping: List[HousekeepingTask] = []
        logbook: List[LogbookEntry] = []

        ext = os.path.splitext(filename)[1].lower().lstrip(".")
        if ext == "csv":
            if isinstance(file_source, (bytes, bytearray)):
                df = pd.read_csv(io.BytesIO(file_source), encoding="utf-8")
            elif isinstance(file_source, io.BytesIO):
                df = pd.read_csv(file_source, encoding="utf-8")
            else:
                df = pd.read_csv(file_source, encoding="utf-8")
            dfs = {"Sheet1": df}
        else:
            if isinstance(file_source, (bytes, bytearray)):
                dfs = pd.read_excel(io.BytesIO(file_source), sheet_name=None)
            elif isinstance(file_source, io.BytesIO):
                dfs = pd.read_excel(file_source, sheet_name=None)
            else:
                dfs = pd.read_excel(file_source, sheet_name=None)

        for sheet_name, df in dfs.items():
            if df.empty:
                continue
            cols = [str(c).strip().lower() for c in df.columns]
            df.columns = cols

            # Fuzzy match helper
            s_lower = sheet_name.lower()
            def col_match(keywords: List[str]) -> bool:
                return any(any(kw in col for kw in keywords) for col in cols) or any(kw in s_lower for kw in keywords)

            is_log = col_match(["log", "יומן", "פיצוי", "compensation", "תקרית", "אירוע"])
            is_hk = col_match(["housekeep", "משק", "ניקיון", "חדרנית", "סטטוס חדר"])
            is_maint = col_match(["maint", "אחזקה", "תקלה", "תקלות", "ticket", "קריאה", "קריאות", "חלפים", "הנדסה", "טכנאי"])

            for _, row in df.iterrows():
                row_dict = {str(k): str(v) if pd.notna(v) else "" for k, v in row.items()}
                row_keys = " ".join(row_dict.keys()).lower()

                if is_log or any(k in row_keys for k in ["פיצוי", "יומן", "תקרית", "compensation", "log_id"]):
                    l = self._row_to_logbook(row_dict, filename, "EXCEL")
                    if l:
                        logbook.append(l)
                elif is_hk or any(k in row_keys for k in ["חדרנית", "משק", "ניקיון", "חדר נקי"]):
                    h = self._row_to_housekeeping(row_dict, filename, "EXCEL")
                    if h:
                        housekeeping.append(h)
                else:
                    # Default to maintenance ticket
                    t = self._row_to_maintenance(row_dict, filename, "EXCEL")
                    if t:
                        maintenance.append(t)
                    else:
                        l = self._row_to_logbook(row_dict, filename, "EXCEL")
                        if l:
                            logbook.append(l)

        return maintenance, housekeeping, logbook

    # -------------------------------------------------------------
    # HELPER PARSERS & FIELD MAPPERS
    # -------------------------------------------------------------
    def _get_val(self, d: Dict[str, Any], keys: List[str], default: str = "") -> str:
        for k in keys:
            for dk in d:
                if k == dk.strip().lower() or k in dk.strip().lower():
                    val = str(d[dk]).strip()
                    if val and val != "nan":
                        return val
        return default

    def _row_to_maintenance(self, d: Dict[str, Any], filename: str, src_type: str) -> Optional[MaintenanceTicket]:
        # Filter out completely empty rows
        non_empty = [v for v in d.values() if v and v != "nan"]
        if not non_empty:
            return None

        tid = self._get_val(d, ["ticket_id", "קריאה", "מס' קריאה", "מספר קריאה", "מזהה", "ticket"])
        desc = self._get_val(d, ["issue_description", "תיאור", "מהות התקלה", "תקלה", "פירוט", "נושא", "קריאה", "description", "issue", "פרטים", "הערות"])
        room = self._get_val(d, ["room_number", "חדר", "מתקן / אזור", "מיקום", "מתקן", "חדר / מתקן", "room", "location", "facility", "asset", "אזור"], "101")
        
        if not desc:
            if room and room != "101":
                desc = f"קריאת שירות / בדיקת אחזקה בחדר {room}"
            else:
                desc = "תקלת אחזקה כללית"

        if not tid or tid == "nan":
            tid = f"MNT-{abs(hash(desc + room)) % 10000:04d}"

        floor = 1
        if room.isdigit():
            floor = int(room[0]) if len(room) >= 3 else 1
        else:
            fl_str = self._get_val(d, ["floor", "קומה"])
            if fl_str.isdigit():
                floor = int(fl_str)

        cat = self._get_val(d, ["category", "קטגוריה", "סיווג", "סיווג מערכת", "תחום", "מחלקה", "system"], "Maintenance")
        pri = self._get_val(d, ["priority", "עדיפות", "רמת דחיפות", "דחיפות"], "Medium")
        stat = self._get_val(d, ["status", "סטטוס", "מצב", "מצב קריאה", "state"], "Open")
        if "חלק" in stat or "waiting" in stat.lower() or "ממתין" in stat:
            stat = "WaitingParts"
        elif "פתור" in stat or "resolved" in stat.lower() or "סגור" in stat:
            stat = "Resolved"
        elif "בטיפול" in stat or "progress" in stat.lower():
            stat = "InProgress"

        tech = self._get_val(d, ["assigned_technician", "טכנאי", "גורם מטפל", "אחראי", "assigned_to", "technician"], "צוות אחזקה")
        shift = self._get_val(d, ["shift", "משמרת"], "Morning")
        created = self._get_val(d, ["created_at", "תאריך ושעה", "מועד", "שעה", "תאריך", "timestamp", "date"], "2026-09-23 02:00:00")
        notes = self._get_val(d, ["notes", "הערות", "חלק חסר", "צפי הגעה"], "")

        # Format created_at if only time
        if ":" in created and len(created) <= 8:
            created = f"2026-09-23 {created}"

        vip = "vip" in desc.lower() or "אח\"מ" in desc or "412" in room

        return MaintenanceTicket(
            ticket_id=tid,
            created_at=created,
            closed_at=None,
            room_number=room,
            floor=floor,
            category=cat,
            issue_description=desc,
            priority=pri,
            status=stat,
            assigned_technician=tech,
            shift=shift,
            resolution_time_minutes=None,
            vip_flag=vip,
            notes=notes,
            source_file=filename,
            source_type=src_type
        )

    def _row_to_logbook(self, d: Dict[str, Any], filename: str, src_type: str) -> Optional[LogbookEntry]:
        non_empty = [v for v in d.values() if v and v != "nan"]
        if not non_empty:
            return None

        lid = self._get_val(d, ["log_id", "מס' יומן", "מספר יומן", "יומן", "log"])
        desc = self._get_val(d, ["incident_description", "פירוט התקרית", "תיאור", "אירוע", "תקרית", "פירוט", "מהות האירוע", "הערות", "incident", "description"])
        room = self._get_val(d, ["room_number", "חדר", "חדר ושם האורח", "מיקום", "room"], "Lobby")

        if not lid and not desc:
            return None
        if not desc:
            desc = f"אירוע תפעולי בחדר {room}"
        if not lid:
            lid = f"LOG-{abs(hash(desc + room)) % 10000:04d}"

        room = self._get_val(d, ["room_number", "חדר", "חדר ושם האורח", "מיקום", "room"], "Lobby")
        vip_name = self._get_val(d, ["vip_guest_name", "שם האורח", "אורח", "guest"], "אורח כללי")
        comp = self._get_val(d, ["compensation_offered", "הפיצוי שהוענק", "פיצוי", "compensation"], "ללא פיצוי")
        
        comp_amt = 0.0
        comp_amt_str = self._get_val(d, ["compensation_amount_ils", "עלות", "עלות (₪)", "סכום", "שווי"])
        if comp_amt_str:
            clean_amt = re.sub(r"[^\d.]", "", comp_amt_str)
            try:
                comp_amt = float(clean_amt)
            except ValueError:
                comp_amt = 0.0

        ts = self._get_val(d, ["timestamp", "מועד", "שעה", "מועד ומשמרת", "תאריך"], "2026-09-23 03:00:00")
        if ":" in ts and len(ts) <= 8:
            ts = f"2026-09-23 {ts}"

        shift = self._get_val(d, ["shift", "משמרת"], "Night")
        author = self._get_val(d, ["author_name", "מחבר", "נרשם ע\"י", "מנהל"], "מנהל תורן")
        role = self._get_val(d, ["author_role", "תפקיד"], "Duty Manager")

        return LogbookEntry(
            log_id=lid,
            timestamp=ts,
            shift=shift,
            author_role=role,
            author_name=author,
            category="Operational Incident",
            room_number=room,
            vip_guest_name=vip_name,
            incident_description=desc,
            compensation_offered=comp,
            compensation_amount_ils=comp_amt,
            escalated_to_gm=(comp_amt > 0),
            action_required="מעקב מנכ\"ל בישיבת בוקר",
            source_file=filename,
            source_type=src_type
        )

    def _row_to_housekeeping(self, d: Dict[str, Any], filename: str, src_type: str) -> Optional[HousekeepingTask]:
        hk_id = self._get_val(d, ["task_id", "משימה", "מס' משימה", "id"], f"HK-{abs(hash(str(d))) % 10000:04d}")
        room = self._get_val(d, ["room_number", "חדר", "room"], "101")
        floor = int(room[0]) if room.isdigit() and len(room) >= 3 else 1
        stat = self._get_val(d, ["room_status", "סטטוס חדר", "סטטוס", "מצב"], "Clean")
        g_stat = self._get_val(d, ["guest_status", "סטטוס אורח", "אורח"], "Stayover")
        notes = self._get_val(d, ["notes", "הערות", "פירוט"], "ניקיון יומי שגרתי")

        return HousekeepingTask(
            task_id=hk_id,
            timestamp="2026-09-23 05:00:00",
            room_number=room,
            floor=floor,
            room_status=stat,
            guest_status=g_stat,
            task_type="Daily Service",
            housekeeper_name="צוות משק בית",
            shift="Night",
            notes=notes,
            source_file=filename,
            source_type=src_type
        )

    def _extract_maintenance_from_line(self, line: str, lines: List[str], idx: int, filename: str, src_type: str) -> Optional[MaintenanceTicket]:
        m_id = re.search(r"MNT-\d+", line)
        tid = m_id.group(0) if m_id else f"MNT-TXT-{idx}"
        
        # Search for room number
        m_room = re.search(r"חדר\s*(\d+)|room\s*(\d+)", line, re.IGNORECASE)
        room = (m_room.group(1) or m_room.group(2)) if m_room else ("Central Plant" if "דוד" in line or "boiler" in line.lower() else ("Elevator B" if "מעלית" in line else "101"))
        
        floor = int(room[0]) if room.isdigit() and len(room) >= 3 else 0
        stat = "WaitingParts" if ("ממתין" in line or "waiting" in line.lower() or "חלק" in line) else ("Resolved" if "פתור" in line or "resolved" in line.lower() else "InProgress")
        
        return MaintenanceTicket(
            ticket_id=tid,
            created_at="2026-09-23 03:00:00",
            closed_at=None,
            room_number=room,
            floor=floor,
            category="מיזוג אוויר" if "מיזוג" in line or "hvac" in line.lower() else ("אינסטלציה" if "מים" in line or "דוד" in line else "אחזקה כללית"),
            issue_description=line,
            priority="Urgent" if "דחוף" in line or "קריטי" in line or "urgent" in line.lower() else "High",
            status=stat,
            assigned_technician="טכנאי תורן",
            shift="Night",
            resolution_time_minutes=None,
            vip_flag=("412" in room or "אח\"מ" in line or "vip" in line.lower()),
            notes=lines[idx+1] if idx + 1 < len(lines) and len(lines[idx+1]) < 80 else "",
            source_file=filename,
            source_type=src_type
        )

    def _extract_logbook_from_line(self, line: str, lines: List[str], idx: int, filename: str, src_type: str) -> Optional[LogbookEntry]:
        m_id = re.search(r"LOG-\d+", line)
        lid = m_id.group(0) if m_id else f"LOG-TXT-{idx}"
        
        m_room = re.search(r"חדר\s*(\d+)|room\s*(\d+)", line, re.IGNORECASE)
        room = (m_room.group(1) or m_room.group(2)) if m_room else "Hotel Wide"
        
        # Extract compensation amount if mentioned (e.g., 850 ₪ or 1,070 ILS)
        comp_amt = 0.0
        m_comp = re.search(r"(\d[\d,]*)\s*(?:₪|ש\"ח|ils)", line, re.IGNORECASE)
        if m_comp:
            try:
                comp_amt = float(m_comp.group(1).replace(",", ""))
            except ValueError:
                comp_amt = 0.0

        return LogbookEntry(
            log_id=lid,
            timestamp="2026-09-23 03:30:00",
            shift="Night",
            author_role="Duty Manager",
            author_name="מנהל תורן",
            category="Duty Manager Shift Handover",
            room_number=room,
            vip_guest_name="אורח מועדף" if "412" in room else "אורח המלון",
            incident_description=line,
            compensation_offered="פיצוי שירותי והטבות" if comp_amt > 0 else "ללא",
            compensation_amount_ils=comp_amt,
            escalated_to_gm=(comp_amt > 0),
            action_required="הסלמה לישיבת הנהלת בוקר",
            source_file=filename,
            source_type=src_type
        )

    def _extract_housekeeping_from_line(self, line: str, lines: List[str], idx: int, filename: str, src_type: str) -> Optional[HousekeepingTask]:
        m_room = re.search(r"חדר\s*(\d+)|room\s*(\d+)", line, re.IGNORECASE)
        room = (m_room.group(1) or m_room.group(2)) if m_room else "101"
        floor = int(room[0]) if room.isdigit() and len(room) >= 3 else 1

        return HousekeepingTask(
            task_id=f"HK-TXT-{idx}",
            timestamp="2026-09-23 06:00:00",
            room_number=room,
            floor=floor,
            room_status="OutOfOrder" if "מושבת" in line or "הצפה" in line else "Clean",
            guest_status="VIP" if "412" in room else "Stayover",
            task_type="Emergency Response" if "הצפה" in line else "Daily Service",
            housekeeper_name="צוות משק בית",
            shift="Night",
            notes=line,
            source_file=filename,
            source_type=src_type
        )
