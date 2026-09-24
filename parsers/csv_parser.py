"""
SmartButler LiveOps Digest - CSV Parser (parsers/csv_parser.py)
Extracts operational log data from SmartButler CSV exports.
Handles metadata headers, column mapping variations, and SLA metrics.
"""

import io
import csv
import re
from typing import List, Dict, Any, Optional, Union
from .models import (
    TicketItem, DepartmentSummary, ParsedLogReport,
    parse_duration_to_minutes, format_minutes_to_duration
)

class SmartButlerCSVParser:
    """Parses SmartButler operational log CSV exports."""

    def parse(self, file_source: Union[str, bytes, io.BytesIO], filename: str = "report.csv") -> ParsedLogReport:
        content = self._read_text(file_source)
        lines = [l.strip() for l in content.splitlines() if l.strip()]
        return self._parse_csv_lines(lines, filename)

    def _read_text(self, file_source: Union[str, bytes, io.BytesIO]) -> str:
        if isinstance(file_source, (bytes, bytearray)):
            try:
                return file_source.decode("utf-8-sig")
            except UnicodeDecodeError:
                return file_source.decode("latin-1", errors="replace")
        elif isinstance(file_source, io.BytesIO):
            data = file_source.getvalue()
            try:
                return data.decode("utf-8-sig")
            except UnicodeDecodeError:
                return data.decode("latin-1", errors="replace")
        elif isinstance(file_source, str):
            with open(file_source, "r", encoding="utf-8-sig", errors="replace") as f:
                return f.read()
        return ""

    def _parse_csv_lines(self, lines: List[str], filename: str) -> ParsedLogReport:
        report_title = "Log Report - Providers"
        site_name = "Grand Hotel"
        date_range = "Current Period"

        # Check header metadata in lines before column header
        data_start_idx = 0
        for i, line in enumerate(lines[:10]):
            if "Log Report" in line:
                report_title = line.strip().split(",")[0].strip()
            date_m = re.search(r"Received Date:\s*([^,]+)(?:,\s*Sites:\s*(.+))?", line, re.IGNORECASE)
            if date_m:
                date_range = date_m.group(1).strip()
                if date_m.group(2):
                    site_name = date_m.group(2).strip()

            # Detect CSV header row (must not be metadata lines like 'Received Date:' or 'Log Report')
            if not line.startswith("Received Date:") and not line.startswith("Log Report"):
                row_parts = [c.strip().lower() for c in line.split(",") if c.strip()]
                matches = sum(1 for c in row_parts if any(k in c for k in ["department", "category", "received", "location", "room", "duration", "description", "creator", "standard", "provider"]))
                if matches >= 2:
                    data_start_idx = i
                    break

        csv_reader = csv.reader(lines[data_start_idx:])
        rows = list(csv_reader)
        if not rows:
            return ParsedLogReport(
                report_title=report_title, site_name=site_name, date_range=date_range,
                raw_filename=filename, file_format="CSV", total_tickets=0,
                overall_success_rate=0.0, avg_duration_str="00:00", avg_duration_minutes=0,
                total_time_str="00:00", total_time_minutes=0
            )

        header = [c.strip().lower() for c in rows[0]]
        col_map = self._map_columns(header)

        tickets: List[TicketItem] = []
        current_dept = "General"
        current_cat = "Service Request"

        for row in rows[1:]:
            if not row or not any(row):
                continue

            first_val = row[0].strip()
            # Check for department or category line if structured like PDF
            if len(row) == 1 or all(c.strip() == "" for c in row[1:]):
                if any(first_val.startswith(kw) for kw in ["Total:", "Page:"]):
                    continue
                current_dept = first_val
                continue

            # Extract fields using mapped columns
            dept = self._get_val(row, col_map, "department") or current_dept
            cat = self._get_val(row, col_map, "category") or current_cat
            rec = self._get_val(row, col_map, "received")
            creator = self._get_val(row, col_map, "creator") or "Staff"
            loc = self._get_val(row, col_map, "location") or "-"
            desc = self._get_val(row, col_map, "description") or "-"
            prov = self._get_val(row, col_map, "provided") or "N/A"
            dur_str = self._get_val(row, col_map, "duration") or "N/A"
            resolver = self._get_val(row, col_map, "resolver") or "-"
            std_str = self._get_val(row, col_map, "standard") or "00:15"

            if not rec and not desc:
                continue

            ticket = TicketItem(
                department=dept,
                task_category=cat,
                received_at=rec,
                creator=creator,
                location=loc,
                description=desc,
                provided_at=prov,
                duration_str=dur_str,
                resolver=resolver,
                standard_str=std_str
            )
            tickets.append(ticket)

        # Department aggregation
        dept_summaries: List[DepartmentSummary] = []
        dept_groups: Dict[str, List[TicketItem]] = {}
        for t in tickets:
            dept_groups.setdefault(t.department, []).append(t)

        for d_name, d_ticks in dept_groups.items():
            resolved = [t for t in d_ticks if t.duration_minutes is not None]
            met = [t for t in d_ticks if t.sla_met]
            succ = round((len(met) / len(d_ticks)) * 100, 1) if d_ticks else 0.0
            t_mins = sum(t.duration_minutes for t in resolved)
            a_mins = round(t_mins / len(resolved)) if resolved else 0

            dept_summaries.append(DepartmentSummary(
                department=d_name,
                total_tickets=len(d_ticks),
                avg_duration_str=format_minutes_to_duration(a_mins),
                avg_duration_minutes=a_mins,
                total_time_str=format_minutes_to_duration(t_mins),
                total_time_minutes=t_mins,
                success_rate=succ
            ))

        # Overall summary
        tot_tickets = len(tickets)
        resolved_all = [t for t in tickets if t.duration_minutes is not None]
        met_all = [t for t in tickets if t.sla_met]
        tot_mins = sum(t.duration_minutes for t in resolved_all)
        avg_mins = round(tot_mins / len(resolved_all)) if resolved_all else 0
        overall_succ = round((len(met_all) / tot_tickets) * 100, 1) if tot_tickets else 0.0

        return ParsedLogReport(
            report_title=report_title,
            site_name=site_name,
            date_range=date_range,
            raw_filename=filename,
            file_format="CSV",
            total_tickets=tot_tickets,
            overall_success_rate=overall_succ,
            avg_duration_str=format_minutes_to_duration(avg_mins),
            avg_duration_minutes=avg_mins,
            total_time_str=format_minutes_to_duration(tot_mins),
            total_time_minutes=tot_mins,
            tickets=tickets,
            departments=dept_summaries
        )

    def _map_columns(self, header: List[str]) -> Dict[str, int]:
        mapping = {}
        for idx, col in enumerate(header):
            c = col.lower().replace("_", " ").strip()
            if "department" in c or c == "dept":
                mapping["department"] = idx
            elif "category" in c or "task category" in c:
                mapping["category"] = idx
            elif "received" in c or "date" in c or "created" in c:
                if "received" not in mapping:
                    mapping["received"] = idx
            elif "creator" in c or "created by" in c:
                mapping["creator"] = idx
            elif "location" in c or "room" in c or "unit" in c:
                mapping["location"] = idx
            elif "desc" in c or "task" in c or "issue" in c:
                mapping["description"] = idx
            elif "provided" in c or "closed" in c or "completed" in c:
                mapping["provided"] = idx
            elif "duration" in c:
                mapping["duration"] = idx
            elif "resolver" in c or "provider" in c or "assigned" in c:
                mapping["resolver"] = idx
            elif "standard" in c or "sla" in c or "benchmark" in c:
                mapping["standard"] = idx
        return mapping

    def _get_val(self, row: List[str], mapping: Dict[str, int], key: str) -> str:
        if key in mapping and mapping[key] < len(row):
            return row[mapping[key]].strip()
        return ""
