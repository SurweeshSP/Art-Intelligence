from __future__ import annotations

import csv
import io
import json
from datetime import datetime
from typing import List
from .models import Opportunity

try:
    from icalendar import Calendar, Event
except ImportError:
    Calendar = None
    Event = None

def export_to_csv(opps: List[Opportunity]) -> str:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "ID", "Title", "Provider", "Type", "Geo Scope", "Location",
        "Deadline", "Days Left", "Bucket", "Fee", "Status", "Verification",
        "Priority Score", "URL"
    ])
    for o in opps:
        loc = f"{o.location.city or ''}, {o.location.country or ''}".strip(", ")
        writer.writerow([
            o.id, o.title, o.provider, o.type, o.geo_scope, loc,
            o.deadline_date or "UNKNOWN", o.days_left if o.days_left is not None else "",
            o.bucket_label, o.financial.application_fee, o.status, o.verification,
            o.priority_score, o.application_url
        ])
    return output.getvalue()

def export_to_json(opps: List[Opportunity]) -> str:
    return json.dumps([o.model_dump() for o in opps], indent=2, default=str)

def export_to_markdown(opps: List[Opportunity]) -> str:
    lines = [
        "# Fine Arts Opportunities Export",
        f"*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*",
        "",
        "| Title | Provider | Type | Geo | Deadline | Fee | Score | Link |",
        "|---|---|---|---|---|---|---|---|"
    ]
    for o in opps:
        fee_str = "Free" if o.financial.application_fee == 0 else str(o.financial.application_fee)
        lines.append(
            f"| {o.title} | {o.provider} | {o.type} | {o.geo_scope} | "
            f"{o.deadline_date or 'No deadline'} | {fee_str} | {o.priority_score} | [Apply]({o.application_url}) |"
        )
    return "\n".join(lines)

def export_to_ics(opps: List[Opportunity]) -> bytes:
    """Generate RFC 5545 iCalendar format for deadlines."""
    if not Calendar or not Event:
        return b"BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//AOIA//EN\nEND:VCALENDAR"

    cal = Calendar()
    cal.add("prodid", "-//AOIA Fine Arts Opportunity Intelligence//EN")
    cal.add("version", "2.0")

    for o in opps:
        if not o.deadline_date or o.deadline_date == "UNKNOWN":
            continue
        try:
            dl = datetime.strptime(o.deadline_date, "%Y-%m-%d").date()
            event = Event()
            event.add("summary", f"[AOIA] {o.title} ({o.provider})")
            event.add("description", f"Type: {o.type}\nLocation: {o.geo_scope}\nURL: {o.application_url}\n{o.why_text}")
            event.add("dtstart", dl)
            event.add("dtend", dl)
            event.add("url", o.application_url)
            cal.add_component(event)
        except Exception:
            continue

    return cal.to_ical()
