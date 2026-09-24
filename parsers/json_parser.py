"""
SmartButler LiveOps Digest - JSON Parser (parsers/json_parser.py)
Extracts operational log data from SmartButler JSON exports and API responses.
"""

import io
import json
from typing import List, Dict, Any, Optional, Union
from .models import (
    TicketItem, DepartmentSummary, ParsedLogReport,
    parse_duration_to_minutes, format_minutes_to_duration
)

class SmartButlerJSONParser:
    """Parses SmartButler operational log JSON documents."""

    def parse(self, file_source: Union[str, bytes, io.BytesIO], filename: str = "report.json") -> ParsedLogReport:
        content = self._read_text(file_source)
        data = json.loads(content)
        return self._parse_json_data(data, filename)

    def _read_text(self, file_source: Union[str, bytes, io.BytesIO]) -> str:
        if isinstance(file_source, (bytes, bytearray)):
            return file_source.decode("utf-8")
        elif isinstance(file_source, io.BytesIO):
            return file_source.getvalue().decode("utf-8")
        elif isinstance(file_source, str):
            with open(file_source, "r", encoding="utf-8") as f:
                return f.read()
        return ""

    def _parse_json_data(self, data: Union[Dict[str, Any], List[Dict[str, Any]]], filename: str) -> ParsedLogReport:
        if isinstance(data, list):
            # Bare list of tickets
            raw_tickets = data
            meta = {}
        else:
            raw_tickets = data.get("tickets", [])
            meta = data

        report_title = meta.get("report_title", "Log Report - Providers")
        site_name = meta.get("site_name", "Grand Hotel")
        date_range = meta.get("date_range", "Current Period")

        tickets: List[TicketItem] = []
        for t in raw_tickets:
            dur_str = t.get("duration_str") or t.get("duration") or "N/A"
            dur_mins = t.get("duration_minutes")
            if dur_mins is None and dur_str != "N/A":
                dur_mins = parse_duration_to_minutes(dur_str)

            std_str = t.get("standard_str") or t.get("standard") or "00:15"
            std_mins = t.get("standard_minutes") or parse_duration_to_minutes(std_str) or 15

            ticket = TicketItem(
                department=t.get("department", "General"),
                task_category=t.get("task_category") or t.get("category", "Service Request"),
                received_at=t.get("received_at") or t.get("received", ""),
                creator=t.get("creator", "Staff"),
                location=t.get("location") or t.get("room", "-"),
                description=t.get("description") or t.get("task", "-"),
                provided_at=t.get("provided_at") or t.get("provided", "N/A"),
                duration_str=dur_str,
                duration_minutes=dur_mins,
                resolver=t.get("resolver", "-"),
                standard_str=std_str,
                standard_minutes=std_mins
            )
            tickets.append(ticket)

        # Department aggregation
        dept_summaries: List[DepartmentSummary] = []
        raw_depts = meta.get("departments", [])
        if raw_depts:
            for d in raw_depts:
                avg_m = d.get("avg_duration_minutes") or parse_duration_to_minutes(d.get("avg_duration_str", "00:00")) or 0
                tot_m = d.get("total_time_minutes") or parse_duration_to_minutes(d.get("total_time_str", "00:00")) or 0
                dept_summaries.append(DepartmentSummary(
                    department=d.get("department", "General"),
                    total_tickets=d.get("total_tickets", 0),
                    avg_duration_str=d.get("avg_duration_str", format_minutes_to_duration(avg_m)),
                    avg_duration_minutes=avg_m,
                    total_time_str=d.get("total_time_str", format_minutes_to_duration(tot_m)),
                    total_time_minutes=tot_m,
                    success_rate=float(d.get("success_rate", 0.0))
                ))
        else:
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
        tot_tickets = meta.get("total_tickets", len(tickets))
        resolved_all = [t for t in tickets if t.duration_minutes is not None]
        met_all = [t for t in tickets if t.sla_met]
        tot_mins = meta.get("total_time_minutes") or sum(t.duration_minutes for t in resolved_all)
        avg_mins = meta.get("avg_duration_minutes") or (round(tot_mins / len(resolved_all)) if resolved_all else 0)
        overall_succ = meta.get("overall_success_rate", round((len(met_all) / tot_tickets) * 100, 1) if tot_tickets else 0.0)

        return ParsedLogReport(
            report_title=report_title,
            site_name=site_name,
            date_range=date_range,
            raw_filename=filename,
            file_format="JSON",
            total_tickets=tot_tickets,
            overall_success_rate=overall_succ,
            avg_duration_str=format_minutes_to_duration(avg_mins),
            avg_duration_minutes=avg_mins,
            total_time_str=format_minutes_to_duration(tot_mins),
            total_time_minutes=tot_mins,
            tickets=tickets,
            departments=dept_summaries
        )
