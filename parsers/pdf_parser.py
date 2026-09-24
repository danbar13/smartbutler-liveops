"""
SmartButler LiveOps Digest - PDF Parser (parsers/pdf_parser.py)
Extracts hierarchical operational log data from SmartButler "Log Report - Providers" PDFs.
Uses pdfplumber with fallback to pypdf.
"""

import os
import io
import re
from typing import List, Dict, Any, Optional, Union
import pdfplumber
from pypdf import PdfReader

from .models import (
    TicketItem, DepartmentSummary, ParsedLogReport,
    parse_duration_to_minutes, format_minutes_to_duration
)

KNOWN_DEPARTMENTS = [
    "Housekeeping", "Maintenance", "Reception", "Front Desk",
    "Food & Beverage", "F&B", "Security", "IT", "Engineering", "Concierge"
]

class SmartButlerPDFParser:
    """Parses SmartButler 'Log Report - Providers' PDF documents."""

    def __init__(self):
        pass

    def parse(self, file_source: Union[str, bytes, io.BytesIO], filename: str = "report.pdf") -> ParsedLogReport:
        text = self._extract_text(file_source)
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        return self._parse_lines(lines, filename)

    def _extract_text(self, file_source: Union[str, bytes, io.BytesIO]) -> str:
        all_text = []

        # Convert bytes or string to stream if needed
        stream = None
        if isinstance(file_source, (bytes, bytearray)):
            stream = io.BytesIO(file_source)
        elif isinstance(file_source, io.BytesIO):
            stream = file_source
        elif isinstance(file_source, str) and os.path.exists(file_source):
            stream = open(file_source, "rb")

        # Try pdfplumber first
        try:
            if stream:
                stream.seek(0)
            with pdfplumber.open(stream or file_source) as pdf:
                for page in pdf.pages:
                    t = page.extract_text()
                    if t:
                        all_text.append(t)
            if all_text:
                return "\n".join(all_text)
        except Exception:
            pass

        # Fallback to pypdf
        try:
            if stream:
                stream.seek(0)
            reader = PdfReader(stream or file_source)
            for page in reader.pages:
                t = page.extract_text()
                if t:
                    all_text.append(t)
            return "\n".join(all_text)
        except Exception as e:
            raise ValueError(f"Failed to extract text from PDF: {e}")

    def _parse_lines(self, lines: List[str], filename: str) -> ParsedLogReport:
        report_title = "Log Report - Providers"
        site_name = "Grand Hotel"
        date_range = "Current Period"

        # 1. Extract Report Metadata from initial lines
        for line in lines[:10]:
            if "Log Report" in line:
                report_title = line.strip()
            date_m = re.search(r"Received Date:\s*([^,]+)(?:,\s*Sites:\s*(.+))?", line, re.IGNORECASE)
            if date_m:
                date_range = date_m.group(1).strip()
                if date_m.group(2):
                    site_name = date_m.group(2).strip()

        # 2. State machine to parse hierarchical departments and task categories
        current_dept: Optional[str] = None
        current_category: Optional[str] = None
        current_category_tickets: List[TicketItem] = []
        
        all_tickets: List[TicketItem] = []
        department_summaries: List[DepartmentSummary] = []
        
        overall_total_tickets = 0
        overall_avg_duration_str = "00:00"
        overall_total_time_str = "00:00"
        overall_success_rate = 0.0

        ticket_pattern = re.compile(
            r"^(\d{1,2}/[A-Za-z]{3}\s+\d{2}:\d{2})\s+(.+?)\s+(\d{1,4}|[A-Za-z0-9\-]+)\s+(.+?)\s+(N/A|\d{1,2}:\d{2})\s+(N/A|\d+:\d{2})\s+(.+)$"
        )
        ticket_pattern_desc_first = re.compile(
            r"^(.+?)\s+(\d{1,2}/[A-Za-z]{3}\s+\d{2}:\d{2})\s+(.+?)\s+(\d{1,4}|[A-Za-z0-9\-]+)\s+(?:\d{1,2}/[A-Za-z]{3}\s+)?(N/A|\d{1,2}:\d{2})\s+(N/A|\d{1,3}:\d{2})\s+(.+)$",
            re.IGNORECASE
        )
        cat_total_pattern = re.compile(
            r"^(.+?)\s+Total:\s*(\d+)\s+Avg\.\s*Duration:\s*([\d:]+|N/A)\s+Standard:\s*([\d:]+)\s+%Success:\s*([\d.]+)",
            re.IGNORECASE
        )
        dept_total_pattern = re.compile(
            r"^Total:\s*([A-Za-z\s&]+?)\s+Total:\s*(\d+)\s+Avg\.\s*Duration:\s*([\d:]+|N/A)\s+Total Time:\s*([\d:]+|N/A)\s+%Success:\s*([\d.]+)",
            re.IGNORECASE
        )
        dept_total_pattern_v2 = re.compile(
            r"^Total:\s*([A-Za-z\s&]+?)\s+Total:\s*(\d+)\s+Total Time:\s*([\d:]+|N/A)\s+%Success:\s*([\d.]+)",
            re.IGNORECASE
        )
        overall_summary_pattern = re.compile(
            r"^Total:\s*Log Report\s+Total:\s*(\d+)\s+Avg\.\s*Duration:\s*([\d:]+|N/A)\s+Total Time:\s*([\d:]+|N/A)\s+%Success:\s*([\d.]+)",
            re.IGNORECASE
        )
        overall_summary_pattern_v2 = re.compile(
            r"^Total:\s*Log Report\s+Total:\s*(\d+)\s+Time:\s*%Success:\s*([\d.]+)",
            re.IGNORECASE
        )

        for line in lines:
            # Check for Overall Summary
            ov_m = overall_summary_pattern.search(line)
            if ov_m:
                overall_total_tickets = int(ov_m.group(1))
                overall_avg_duration_str = ov_m.group(2)
                overall_total_time_str = ov_m.group(3)
                overall_success_rate = float(ov_m.group(4))
                continue

            ov_m2 = overall_summary_pattern_v2.search(line)
            if ov_m2:
                overall_total_tickets = int(ov_m2.group(1))
                overall_success_rate = float(ov_m2.group(2))
                continue

            # Check for Department Total Line (Variant 1)
            dept_m = dept_total_pattern.search(line)
            if dept_m:
                d_name = dept_m.group(1).strip()
                d_tot = int(dept_m.group(2))
                d_avg_str = dept_m.group(3)
                d_time_str = dept_m.group(4)
                d_succ = float(dept_m.group(5))
                
                department_summaries.append(DepartmentSummary(
                    department=d_name,
                    total_tickets=d_tot,
                    avg_duration_str=d_avg_str,
                    avg_duration_minutes=parse_duration_to_minutes(d_avg_str) or 0,
                    total_time_str=d_time_str,
                    total_time_minutes=parse_duration_to_minutes(d_time_str) or 0,
                    success_rate=d_succ
                ))
                current_dept = None
                current_category = None
                continue

            # Check for Department Total Line (Variant 2)
            dept_m2 = dept_total_pattern_v2.search(line)
            if dept_m2:
                d_name = dept_m2.group(1).strip()
                d_tot = int(dept_m2.group(2))
                d_time_str = dept_m2.group(3)
                d_succ = float(dept_m2.group(4))

                department_summaries.append(DepartmentSummary(
                    department=d_name,
                    total_tickets=d_tot,
                    avg_duration_str="00:00",
                    avg_duration_minutes=0,
                    total_time_str=d_time_str,
                    total_time_minutes=parse_duration_to_minutes(d_time_str) or 0,
                    success_rate=d_succ
                ))
                current_dept = None
                current_category = None
                continue

            # Standard Benchmark split line (e.g. '00:22 : 00:30')
            std_split_m = re.match(r"^([\d:]+)\s*:\s*([\d:]+)$", line)
            if std_split_m and current_category_tickets:
                avg_val_str = std_split_m.group(1).strip()
                std_val_str = std_split_m.group(2).strip()
                std_mins = parse_duration_to_minutes(std_val_str) or 15
                for t in current_category_tickets:
                    t.standard_str = std_val_str
                    t.standard_minutes = std_mins
                    if t.duration_minutes is not None:
                        t.sla_met = (t.duration_minutes <= std_mins)
                        t.sla_breach_ratio = round(t.duration_minutes / std_mins, 2) if not t.sla_met else 1.0
                    else:
                        t.sla_met = False
                        t.sla_breach_ratio = 999.0
                current_category_tickets = []
                continue

            # Check for Category Total Line (contains Standard benchmark!)
            cat_m = cat_total_pattern.search(line)
            if cat_m:
                cat_name = cat_m.group(1).strip()
                std_str = cat_m.group(4).strip()
                std_mins = parse_duration_to_minutes(std_str) or 15

                # Update standard on all tickets collected for this category
                for t in current_category_tickets:
                    t.standard_str = std_str
                    t.standard_minutes = std_mins
                    if t.duration_minutes is not None:
                        t.sla_met = (t.duration_minutes <= std_mins)
                        t.sla_breach_ratio = round(t.duration_minutes / std_mins, 2) if not t.sla_met else 1.0
                    else:
                        t.sla_met = False
                        t.sla_breach_ratio = 999.0

                current_category_tickets = []
                current_category = None
                continue

            # Check for Department Header
            if line in KNOWN_DEPARTMENTS or (any(line.startswith(kd) for kd in KNOWN_DEPARTMENTS) and "Total" not in line):
                current_dept = line.strip()
                current_category = None
                continue

            # Check for Ticket Line (Variant 1 - Date first)
            tick_m = ticket_pattern.match(line)
            if tick_m:
                rec_at, creator, loc, desc, prov_at, dur_str, resolver = tick_m.groups()
                creator = creator.strip()
                loc = loc.strip()
                desc = desc.strip()

                # If loc is not numeric and desc starts with a room number (e.g. '320 -' or '109 -')
                m_desc_room = re.match(r"^(\d{1,4})\s*-\s*(.*)$", desc)
                if not loc.isdigit() and m_desc_room:
                    real_room = m_desc_room.group(1)
                    real_desc = m_desc_room.group(2).strip() or "-"
                    creator = f"{creator} {loc}".strip()
                    loc = real_room
                    desc = real_desc

                t_item = TicketItem(
                    department=current_dept or "General",
                    task_category=current_category or "Service Request",
                    received_at=rec_at.strip(),
                    creator=creator,
                    location=loc,
                    description=desc,
                    provided_at=prov_at.strip(),
                    duration_str=dur_str.strip(),
                    resolver=resolver.strip()
                )
                current_category_tickets.append(t_item)
                all_tickets.append(t_item)
                continue

            # Check for Ticket Line (Variant 2 - Description first)
            tick_m2 = ticket_pattern_desc_first.match(line)
            if tick_m2:
                desc, rec_at, creator, loc, prov_at, dur_str, resolver = tick_m2.groups()
                desc = desc.strip()
                rec_at = rec_at.strip()
                creator = creator.strip()
                loc = loc.strip()
                prov_at = prov_at.strip()
                dur_str = dur_str.strip()
                resolver = resolver.strip()

                t_item = TicketItem(
                    department=current_dept or "General",
                    task_category=current_category or desc or "Service Request",
                    received_at=rec_at,
                    creator=creator,
                    location=loc,
                    description=desc,
                    provided_at=prov_at,
                    duration_str=dur_str,
                    resolver=resolver
                )
                current_category_tickets.append(t_item)
                all_tickets.append(t_item)
                continue

            # If inside department and not a recognized header/footer/comment/alert line, this line is the Task Category!
            skip_cat_keywords = [
                "Received", "Total:", "Summary", "Page:", "Powered by", "JB Demo",
                "->", "Alert", "Changing", "Delay", "Please", "******", "To:", "From:",
                "- Changing", "Ticket#:", "Log Report", "Site Name:", "Department:", "Report Type:",
                "Sun Siyam", "Olhuveli", "User:", "Printed:"
            ]
            if current_dept and not any(kw.lower() in line.lower() for kw in skip_cat_keywords):
                if not re.search(r'\d{2}/[A-Za-z]{3}|\d{2}-[A-Za-z]{3}', line) and not line.startswith(('-', '"', '*', '->', '(', '+')) and not line.isdigit():
                    current_category = line.strip()

        # If overall summary was not present or duration was missing, compute from tickets & departments
        if (not overall_total_tickets or overall_avg_duration_str == "00:00") and all_tickets:
            overall_total_tickets = len(all_tickets)
            resolved_tickets = [t for t in all_tickets if t.duration_minutes is not None]
            met_tickets = [t for t in all_tickets if t.sla_met]
            overall_success_rate = round((len(met_tickets) / len(all_tickets)) * 100, 1) if all_tickets else 0.0

            total_mins = sum(t.duration_minutes for t in resolved_tickets)
            avg_mins = round(total_mins / len(resolved_tickets)) if resolved_tickets else 0
            overall_avg_duration_str = format_minutes_to_duration(avg_mins)
            overall_total_time_str = format_minutes_to_duration(total_mins)

        # Recalculate avg duration on department summaries if missing
        if department_summaries and all_tickets:
            for ds in department_summaries:
                if ds.avg_duration_str == "00:00" or ds.avg_duration_minutes == 0:
                    d_ticks = [t for t in all_tickets if t.department.lower() == ds.department.lower() and t.duration_minutes is not None]
                    if d_ticks:
                        t_m = sum(t.duration_minutes for t in d_ticks)
                        a_m = round(t_m / len(d_ticks))
                        ds.avg_duration_str = format_minutes_to_duration(a_m)
                        ds.avg_duration_minutes = a_m
                        if ds.total_time_str == "00:00":
                            ds.total_time_str = format_minutes_to_duration(t_m)
                            ds.total_time_minutes = t_m

        # Fallback department summaries if not parsed from explicit totals
        if not department_summaries and all_tickets:
            dept_groups: Dict[str, List[TicketItem]] = {}
            for t in all_tickets:
                dept_groups.setdefault(t.department, []).append(t)

            for d_name, d_ticks in dept_groups.items():
                resolved = [t for t in d_ticks if t.duration_minutes is not None]
                met = [t for t in d_ticks if t.sla_met]
                succ = round((len(met) / len(d_ticks)) * 100, 1) if d_ticks else 0.0
                t_mins = sum(t.duration_minutes for t in resolved)
                a_mins = round(t_mins / len(resolved)) if resolved else 0
                
                department_summaries.append(DepartmentSummary(
                    department=d_name,
                    total_tickets=len(d_ticks),
                    avg_duration_str=format_minutes_to_duration(a_mins),
                    avg_duration_minutes=a_mins,
                    total_time_str=format_minutes_to_duration(t_mins),
                    total_time_minutes=t_mins,
                    success_rate=succ
                ))

        return ParsedLogReport(
            report_title=report_title,
            site_name=site_name,
            date_range=date_range,
            raw_filename=filename,
            file_format="PDF",
            total_tickets=overall_total_tickets or len(all_tickets),
            overall_success_rate=overall_success_rate,
            avg_duration_str=overall_avg_duration_str,
            avg_duration_minutes=parse_duration_to_minutes(overall_avg_duration_str) or 0,
            total_time_str=overall_total_time_str,
            total_time_minutes=parse_duration_to_minutes(overall_total_time_str) or 0,
            tickets=all_tickets,
            departments=department_summaries
        )
