import csv
import os
import uuid
from typing import Optional

import click
import httpx
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

API_BASE = os.environ.get("PHISHGUARD_API_URL", "http://localhost:8000")
console = Console()


@click.group()
def cli():
    """PhishGuard — AI-first phishing simulation platform."""


def _api(method: str, path: str, **kwargs) -> httpx.Response:
    url = f"{API_BASE}{path}"
    try:
        if method == "GET":
            return httpx.get(url, params=kwargs.get("params"), timeout=30)
        elif method == "POST":
            return httpx.post(url, json=kwargs.get("json"), timeout=30)
        elif method == "PUT":
            return httpx.put(url, json=kwargs.get("json"), timeout=30)
        elif method == "DELETE":
            return httpx.delete(url, timeout=30)
    except httpx.ConnectError:
        console.print("[red]Could not connect to API at {}. Is the server running?[/]".format(API_BASE))
        raise SystemExit(1)
    raise ValueError(f"Unsupported method: {method}")


# ── client ───────────────────────────────────────────────────────────────────


@click.group()
def client():
    """Manage clients."""


@client.command("add")
@click.option("--name", required=True, help="Company name")
@click.option("--email", required=True, help="Contact email")
@click.option("--industry", default=None, help="Industry")
@click.option("--employees", type=int, default=0, help="Number of employees")
def client_add(name, email, industry, employees):
    """Create a new client."""
    resp = _api("POST", "/clients", json={
        "company_name": name,
        "contact_email": email,
        "industry": industry,
        "employee_count": employees,
    })
    data = resp.json()
    console.print(Panel(f"[green]Client created[/]\nID: {data['id']}\nName: {data['company_name']}"))


@client.command("list")
def client_list():
    """List all clients."""
    resp = _api("GET", "/clients", params={"active_only": False})
    data = resp.json()
    if not data:
        console.print("[yellow]No clients found.[/]")
        return
    table = Table(title="Clients")
    table.add_column("ID", style="dim")
    table.add_column("Name")
    table.add_column("Email")
    table.add_column("Industry")
    table.add_column("Employees")
    table.add_column("Active")
    for c in data:
        table.add_row(
            str(c["id"])[:8],
            c["company_name"],
            c["contact_email"],
            c.get("industry") or "-",
            str(c["employee_count"]),
            "✅" if c["is_active"] else "❌",
        )
    console.print(table)


@client.command("show")
@click.argument("client_id")
def client_show(client_id):
    """Show client details."""
    resp = _api("GET", f"/clients/{client_id}")
    data = resp.json()
    table = Table(title=f"Client: {data['company_name']}")
    table.add_column("Field", style="bold")
    table.add_column("Value")
    for k, v in data.items():
        table.add_row(k, str(v))
    console.print(table)


@client.group()
def employees():
    """Manage client employees."""


@employees.command("import")
@click.argument("client_id")
@click.argument("csv_file", type=click.Path(exists=True))
def employees_import(client_id, csv_file):
    """Import employees from a CSV file."""
    employees_data = []
    with open(csv_file, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            employees_data.append({
                "email_hash": row.get("email_hash", ""),
                "name_hash": row.get("name_hash"),
                "role": row.get("role"),
                "department": row.get("department"),
                "group": row.get("group", "general"),
            })
    if not employees_data:
        console.print("[red]No employees found in CSV.[/]")
        return
    resp = _api("POST", f"/clients/{client_id}/employees", json=employees_data)
    data = resp.json()
    console.print(f"[green]Imported {len(data)} employees for client {client_id}.[/]")


cli.add_command(client)
client.add_command(employees)


# ── campaign ─────────────────────────────────────────────────────────────────


@click.group()
def campaign():
    """Manage campaigns."""


@campaign.command("run")
@click.argument("client_id")
@click.option("--difficulty", default="medium", type=click.Choice(["easy", "medium", "hard"]))
def campaign_run(client_id, difficulty):
    """Trigger a campaign immediately."""
    resp = _api("POST", f"/clients/{client_id}/campaigns", json={"difficulty": difficulty})
    data = resp.json()
    console.print(f"[green]Campaign started[/]\nID: {data['id']}\nStatus: {data['status']}")


@campaign.command("list")
@click.option("--client-id", default=None, help="Filter by client ID")
def campaign_list(client_id):
    """List campaigns."""
    if client_id:
        resp = _api("GET", f"/clients/{client_id}/campaigns")
    else:
        console.print("[red]Provide --client-id to list campaigns.[/]")
        return
    data = resp.json()
    if not data:
        console.print("[yellow]No campaigns found.[/]")
        return
    table = Table(title="Campaigns")
    table.add_column("ID", style="dim")
    table.add_column("Client ID")
    table.add_column("Name")
    table.add_column("Status")
    table.add_column("Difficulty")
    table.add_column("Sent")
    table.add_column("Clicks")
    for c in data:
        table.add_row(
            str(c["id"])[:8],
            str(c["client_id"])[:8],
            c["name"],
            c["status"],
            c["difficulty"],
            str(c["sent_count"]),
            str(c["click_count"]),
        )
    console.print(table)


@campaign.command("results")
@click.argument("campaign_id")
def campaign_results(campaign_id):
    """Get detailed campaign results."""
    resp = _api("GET", f"/campaigns/{campaign_id}/results")
    data = resp.json()
    camp = data["campaign"]
    console.print(Panel(f"[bold]Campaign:[/] {camp['name']}  [bold]Status:[/] {camp['status']}"))
    results = data.get("results", [])
    if not results:
        console.print("[yellow]No results yet.[/]")
        return
    table = Table(title="Results")
    table.add_column("Employee")
    table.add_column("Opened")
    table.add_column("Clicked")
    table.add_column("Submitted")
    table.add_column("Reported")
    table.add_column("Trained")
    for r in results:
        table.add_row(
            (r.get("email_hash") or str(r["employee_id"])[:8])[:20],
            "✅" if r["email_opened"] else "—",
            "✅" if r["link_clicked"] else "—",
            "✅" if r["credentials_submitted"] else "—",
            "✅" if r["reported_phishing"] else "—",
            "✅" if r["training_completed"] else "—",
        )
    console.print(table)


@campaign.command("monitor")
@click.option("--campaign-id", default=None, help="Campaign ID to monitor")
@click.option("--client-id", default=None, help="Client ID to list running campaigns")
def campaign_monitor(campaign_id, client_id):
    """Check campaign delivery and results."""
    if campaign_id:
        resp = _api("GET", f"/campaigns/{campaign_id}/results")
        data = resp.json()
        camp = data["campaign"]
        results = data.get("results", [])
        sent = len(results)
        opened = sum(1 for r in results if r["email_opened"])
        clicked = sum(1 for r in results if r["link_clicked"])
        submitted = sum(1 for r in results if r["credentials_submitted"])
        reported = sum(1 for r in results if r["reported_phishing"])
        open_rate = round(opened / sent * 100, 1) if sent else 0.0
        click_rate = round(clicked / sent * 100, 1) if sent else 0.0

        console.print(Panel(f"[bold]Campaign:[/] {camp['name']}"))
        console.print(f"  Status: {camp['status']}  |  Difficulty: {camp['difficulty']}")
        console.print(f"  Sent: {sent}  |  Opened: {opened} ({open_rate}%)")
        console.print(f"  Clicked: {clicked} ({click_rate}%)  |  Credentials: {submitted}  |  Reported: {reported}")

        if results:
            vulnerable = [r for r in results if r["link_clicked"] or r["credentials_submitted"]]
            if vulnerable:
                console.print("\n[bold][yellow]Employees who need attention:[/][/]")
                table = Table(show_header=True)
                table.add_column("Employee")
                table.add_column("Clicked")
                table.add_column("Submitted")
                table.add_column("Trained")
                for r in vulnerable:
                    table.add_row(
                        (r.get("email_hash") or str(r["employee_id"])[:8])[:20],
                        "✅" if r["link_clicked"] else "—",
                        "✅" if r["credentials_submitted"] else "—",
                        "✅" if r["training_completed"] else "—",
                    )
                console.print(table)
    elif client_id:
        resp = _api("GET", f"/clients/{client_id}/campaigns", params={"status": "running"})
        campaigns = resp.json()
        if not campaigns:
            console.print("[yellow]No running campaigns for this client.[/]")
            return
        table = Table(title="Running Campaigns")
        table.add_column("ID", style="dim")
        table.add_column("Name")
        table.add_column("Difficulty")
        table.add_column("Sent")
        table.add_column("Clicks")
        table.add_column("Fails")
        for c in campaigns:
            table.add_row(
                c["id"][:8], c["name"][:30], c["difficulty"],
                str(c["sent_count"]), str(c["click_count"]), str(c["fail_count"]),
            )
        console.print(table)
        console.print("[dim]Use --campaign-id to see detailed results for a specific campaign.[/]")
    else:
        console.print("[yellow]Provide --campaign-id to monitor a campaign, or --client-id to list running campaigns.[/]")


@campaign.command("schedule")
@click.argument("campaign_id")
@click.option("--date", required=True, help="Scheduled date (ISO format: 2026-08-15T10:00:00)")
def campaign_schedule(campaign_id, date):
    """Schedule a draft campaign for future launch."""
    resp = _api("POST", f"/campaigns/{campaign_id}/schedule", json={"scheduled_date": date})
    data = resp.json()
    console.print(f"[green]Campaign scheduled[/]\nID: {data['id']}\nDate: {data['scheduled_date']}\nStatus: {data['status']}")


cli.add_command(campaign)


# ── vishing ───────────────────────────────────────────────────────────────────


@click.group()
def vishing():
    """Manage vishing (voice phishing) sessions."""


@vishing.command("trigger")
@click.argument("employee_id")
@click.option("--campaign-id", default=None, help="Optional campaign ID")
def vishing_trigger(employee_id, campaign_id):
    """Trigger a vishing call to an employee."""
    payload = {"employee_id": employee_id}
    if campaign_id:
        payload["campaign_id"] = campaign_id
    resp = _api("POST", "/vishing/trigger", json=payload)
    data = resp.json()
    console.print(f"[green]Vishing session created[/]\nID: {data.get('id')}")


cli.add_command(vishing)


# ── stats ────────────────────────────────────────────────────────────────────


@cli.command("stats")
@click.argument("client_id")
def stats(client_id):
    """Get aggregate statistics for a client."""
    resp = _api("GET", f"/clients/{client_id}/stats")
    data = resp.json()
    table = Table(title=f"Stats: {data['company_name']}")
    table.add_column("Metric", style="bold")
    table.add_column("Value")
    for k, v in data.items():
        table.add_row(k.replace("_", " ").title(), str(v))
    console.print(table)


@cli.command("dashboard")
@click.argument("client_id")
def dashboard(client_id):
    """Show consolidated client dashboard."""
    resp = _api("GET", f"/clients/{client_id}/dashboard")
    data = resp.json()
    console.print(Panel(f"[bold]{data['company_name']}[/] — Dashboard"))
    s = data["summary"]
    console.print(f"  Employees: {s['total_employees']}  Campaigns: {s['total_campaigns']}  "
                  f"Active: {s['active_campaigns']}  "
                  f"Pending Training: {s['pending_training']}")
    console.print(f"  Click Rate: {s['click_rate']}%  Fail Rate: {s['fail_rate']}%  "
                  f"Vishing Sessions: {s['vishing_sessions']}")
    risk = data.get("risk", {})
    console.print(f"  Avg Risk Score: {risk.get('average_risk_score', 0)}/100  "
                  f"Scored Employees: {risk.get('total_employees_scored', 0)}/{risk.get('total_employees', 0)}")
    dist = risk.get("risk_distribution", {})
    levels = f"Low:{dist.get('low',0)} Med:{dist.get('medium',0)} High:{dist.get('high',0)} Crit:{dist.get('critical',0)}"
    console.print(f"  Risk Distribution: {levels}")
    if data.get("recent_campaigns"):
        console.print("\n[bold]Recent Campaigns[/]")
        table = Table(show_header=True)
        table.add_column("Name")
        table.add_column("Status")
        table.add_column("Difficulty")
        table.add_column("Sent")
        table.add_column("Clicks")
        table.add_column("Rate")
        table.add_column("Date")
        for c in data["recent_campaigns"]:
            table.add_row(c["name"][:25], c["status"], c["difficulty"],
                         str(c["sent_count"]), str(c["click_count"]),
                         f"{c['click_rate']}%", c["created_at"][:10] if c.get("created_at") else "-")
        console.print(table)


# ── risk ──────────────────────────────────────────────────────────────────────


@click.group()
def risk():
    """Employee risk scoring & analysis."""


@risk.command("employee")
@click.argument("employee_id")
def risk_employee(employee_id):
    """Show risk score for an employee."""
    resp = _api("GET", f"/risk/employee/{employee_id}")
    data = resp.json()
    console.print(Panel(f"[bold]Risk Score:[/] {data['score']}/100  [bold]Level:[/] {data['risk_level']}"))
    console.print(f"Total campaigns attended: {data['total_campaigns_attended']}")


@risk.command("trend")
@click.argument("employee_id")
@click.option("--limit", default=12, help="Number of data points")
def risk_trend(employee_id, limit):
    """Show risk trend for an employee."""
    resp = _api("GET", f"/risk/employee/{employee_id}/trend", params={"limit": limit})
    data = resp.json()
    if not data:
        console.print("[yellow]No risk data yet.[/]")
        return
    table = Table(title="Risk Trend")
    table.add_column("Date")
    table.add_column("Score")
    table.add_column("Level")
    for item in data:
        table.add_row(
            item["calculated_at"][:10],
            str(item["score"]),
            item["risk_level"],
        )
    console.print(table)


@risk.command("client")
@click.argument("client_id")
def risk_client(client_id):
    """Show risk summary for a client."""
    resp = _api("GET", f"/risk/client/{client_id}")
    data = resp.json()
    console.print(Panel(f"[bold]Client Risk Summary[/]\nAverage Score: {data['average_risk_score']}/100"))
    dist = data["risk_distribution"]
    dist_table = Table(title="Risk Distribution")
    dist_table.add_column("Level")
    dist_table.add_column("Count")
    for level in ("low", "medium", "high", "critical"):
        dist_table.add_row(level.capitalize(), str(dist.get(level, 0)))
    console.print(dist_table)
    if data.get("highest_risk_employees"):
        high_table = Table(title="Highest Risk Employees")
        high_table.add_column("Employee ID")
        high_table.add_column("Score")
        high_table.add_column("Level")
        for e in data["highest_risk_employees"]:
            high_table.add_row(e["employee_id"][:8], str(e["score"]), e["risk_level"])
        console.print(high_table)


@risk.command("summary")
@click.argument("client_id")
def risk_summary(client_id):
    """Show risk score summary for a client (alias for risk client)."""
    risk_client.callback(client_id)


@risk.command("departments")
@click.argument("client_id")
def risk_departments(client_id):
    """Show department-level risk benchmarking."""
    resp = _api("GET", f"/risk/client/{client_id}/departments")
    data = resp.json()
    if not data:
        console.print("[yellow]No department data yet.[/]")
        return
    table = Table(title="Department Benchmarking")
    table.add_column("Department", style="bold")
    table.add_column("Employees")
    table.add_column("Sent")
    table.add_column("Click Rate")
    table.add_column("Fail Rate")
    table.add_column("Avg Risk")
    for d in data:
        table.add_row(
            d["department"].replace("_", " ").title(),
            str(d["employee_count"]),
            str(d["total_sent"]),
            f"{d['click_rate']}%",
            f"{d['fail_rate']}%",
            str(d["avg_risk_score"]),
        )
    console.print(table)


@risk.command("heatmap")
@click.argument("client_id")
def risk_heatmap(client_id):
    """Show click timing heatmap (day/hour distribution)."""
    resp = _api("GET", f"/risk/client/{client_id}/heatmap")
    data = resp.json()
    console.print(Panel(f"[bold]Click Heatmap[/] — {data['total_clicks']} total clicks"))
    console.print(f"Peak day: [bold]{data.get('peak_day', 'N/A')}[/]  Peak hour: [bold]{data.get('peak_hour', 'N/A')}:00[/]")
    console.print("\n[bold]By Day of Week[/]")
    for day, count in data.get("by_day_of_week", {}).items():
        bar = "█" * (count // 2 + 1) if count else ""
        console.print(f"  {day[:3]}: {bar} ({count})")
    console.print("\n[bold]By Hour (business hours)[/]")
    for h in range(6, 20):
        hour_str = f"{h:02d}:00"
        count = data.get("by_hour", {}).get(str(h), 0)
        bar = "█" * (count // 2 + 1) if count else ""
        console.print(f"  {hour_str}: {bar} ({count})")


cli.add_command(risk)


@click.group()
def feedback():
    """View employee training feedback."""


@feedback.command("list")
@click.argument("employee_id")
@click.option("--campaign-id", default=None, help="Filter by campaign ID")
def feedback_list(employee_id, campaign_id):
    """Show training feedback for an employee."""
    params = {}
    if campaign_id:
        params["campaign_id"] = campaign_id
    resp = _api("GET", f"/training/feedback/{employee_id}", params=params)
    data = resp.json()
    if not data:
        console.print("[yellow]No feedback found for this employee.[/]")
        return
    for entry in data:
        console.print(Panel(f"[bold]{entry['training_title']}[/]\nScore before: {entry['score_before']}\nSent: {entry.get('feedback_sent_at', 'N/A')[:10]}"))
        console.print(entry.get("feedback_html", "")[:500] + "...")


@feedback.command("show")
@click.argument("employee_id")
@click.option("--campaign-id", default=None, help="Filter by campaign ID")
@click.option("--output", default=None, help="Save feedback HTML to file")
def feedback_show(employee_id, campaign_id, output):
    """Show full training feedback HTML for an employee."""
    params = {}
    if campaign_id:
        params["campaign_id"] = campaign_id
    resp = _api("GET", f"/training/feedback/{employee_id}", params=params)
    data = resp.json()
    if not data:
        console.print("[yellow]No feedback found for this employee.[/]")
        return
    for entry in data:
        html = entry.get("feedback_html", "")
        if output:
            with open(output, "w", encoding="utf-8") as f:
                f.write(html)
            console.print(f"[green]Feedback saved to {output}[/]")
        else:
            console.print(html[:2000] + "\n... (use --output to save full HTML)")


cli.add_command(feedback)


# ── training ──────────────────────────────────────────────────────────────────


@click.group()
def training():
    """Manage security awareness training."""


@training.command("pending")
@click.option("--client-id", default=None, help="Filter by client ID")
def training_pending(client_id):
    """List pending training assignments."""
    params = {}
    if client_id:
        params["client_id"] = client_id
    resp = _api("GET", "/training/pending", params=params)
    data = resp.json()
    if not data:
        console.print("[yellow]No pending training assignments.[/]")
        return
    table = Table(title="Pending Training")
    table.add_column("ID", style="dim")
    table.add_column("Employee")
    table.add_column("Type")
    table.add_column("Title")
    table.add_column("Score Before")
    table.add_column("Assigned")
    for a in data:
        table.add_row(
            a["id"][:8],
            a["employee_id"][:8],
            a["training_type"],
            a["training_title"][:30],
            str(a["score_before"]),
            a["assigned_at"][:10],
        )
    console.print(table)


@training.command("assign")
@click.argument("employee_id")
@click.argument("campaign_id")
@click.option("--failure-type", default="link_clicked", help="Failure type")
def training_assign(employee_id, campaign_id, failure_type):
    """Assign training to an employee."""
    resp = _api("POST", f"/training/assign?employee_id={employee_id}&campaign_id={campaign_id}&failure_type={failure_type}")
    data = resp.json()
    console.print(f"[green]Training assigned[/]\nType: {data['training_type']}\nStatus: {data['status']}")


@training.command("complete")
@click.argument("assignment_id")
@click.option("--score-after", type=float, default=None, help="Score after training")
def training_complete(assignment_id, score_after):
    """Mark training as completed."""
    payload = {}
    if score_after is not None:
        payload["score_after"] = score_after
    resp = _api("POST", f"/training/{assignment_id}/complete", json=payload)
    data = resp.json()
    console.print(f"[green]Training completed[/]\nStatus: {data['status']}")


@training.command("content")
@click.argument("training_type")
def training_content(training_type):
    """Show training content."""
    resp = _api("GET", f"/training/content/{training_type}")
    data = resp.json()
    console.print(Panel(f"[bold]{data['title']}[/]"))
    console.print(data["html"][:500] + "...")


@training.command("roi")
@click.argument("client_id")
def training_roi(client_id):
    """Show training ROI (pre/post score improvement)."""
    resp = _api("GET", f"/training/client/{client_id}/roi")
    data = resp.json()
    console.print(Panel(f"[bold]Training ROI[/] — {data['total_assignments']} total assignments"))
    console.print(f"  Completed: {data['total_completed']}  Pending: {data['total_pending']}  "
                  f"Completion rate: {data['completion_rate']}%")
    console.print(f"  Avg Score Before: {data['overall_avg_score_before']}/100  "
                  f"After: {data['overall_avg_score_after']}/100  "
                  f"Improvement: {data['overall_score_improvement']} pts ({data['improvement_percent']}%)")
    if data.get("by_training_type"):
        console.print("\n[bold]By Training Type[/]")
        table = Table()
        table.add_column("Type")
        table.add_column("Assigned")
        table.add_column("Completed")
        table.add_column("Rate")
        table.add_column("Before")
        table.add_column("After")
        table.add_column("Improvement")
        for t in data["by_training_type"]:
            table.add_row(
                t["title"][:25],
                str(t["assigned"]),
                str(t["completed"]),
                f"{t['completion_rate']}%",
                str(t["avg_score_before"]),
                str(t["avg_score_after"]),
                f"{t['score_improvement']} pts ({t['improvement_percent']}%)",
            )
        console.print(table)


cli.add_command(training)


# ── reports ───────────────────────────────────────────────────────────────────


@click.group()
def reports():
    """Generate executive reports."""


@reports.command("client")
@click.argument("client_id")
@click.option("--days", default=365, help="Report period in days")
@click.option("--output", default=None, help="Output file path")
def report_client(client_id, days, output):
    """Generate client security report."""
    resp = _api("GET", f"/reports/client/{client_id}", params={"days": days})
    html = resp.text
    if output:
        with open(output, "w", encoding="utf-8") as f:
            f.write(html)
        console.print(f"[green]Report saved to {output}[/]")
    else:
        console.print(html[:2000] + "\n... (use --output to save to file)")


@reports.command("campaign")
@click.argument("campaign_id")
@click.option("--output", default=None, help="Output file path")
def report_campaign(campaign_id, output):
    """Generate campaign report."""
    resp = _api("GET", f"/reports/campaign/{campaign_id}")
    html = resp.text
    if output:
        with open(output, "w", encoding="utf-8") as f:
            f.write(html)
        console.print(f"[green]Report saved to {output}[/]")
    else:
        console.print(html[:2000] + "\n... (use --output to save to file)")


cli.add_command(reports)


@reports.command("campaign-csv")
@click.argument("campaign_id")
@click.option("--output", required=True, help="Output CSV file path")
def report_campaign_csv(campaign_id, output):
    """Export campaign results as CSV."""
    resp = _api("GET", f"/reports/campaign/{campaign_id}/csv")
    with open(output, "w", encoding="utf-8") as f:
        f.write(resp.text)
    console.print(f"[green]Campaign CSV saved to {output}[/]")


@reports.command("client-csv")
@click.argument("client_id")
@click.option("--days", default=365, help="Report period in days")
@click.option("--output", required=True, help="Output CSV file path")
def report_client_csv(client_id, days, output):
    """Export client campaign history as CSV."""
    resp = _api("GET", f"/reports/client/{client_id}/csv", params={"days": days})
    with open(output, "w", encoding="utf-8") as f:
        f.write(resp.text)
    console.print(f"[green]Client CSV saved to {output}[/]")


# ── templates ────────────────────────────────────────────────────────────────


@click.group()
def template():
    """Manage campaign templates."""


@template.command("create")
@click.argument("client_id")
@click.argument("name")
@click.option("--description", default=None, help="Template description")
@click.option("--difficulty", default="medium", help="Difficulty level")
def template_create(client_id, name, description, difficulty):
    """Create a new campaign template."""
    resp = _api("POST", "/templates", json={
        "client_id": client_id,
        "name": name,
        "description": description,
        "difficulty": difficulty,
    })
    data = resp.json()
    console.print(f"[green]Template created[/]\nID: {data['id']}\nName: {data['name']}")


@template.command("list")
@click.option("--client-id", default=None, help="Filter by client ID")
def template_list(client_id):
    """List campaign templates."""
    params = {}
    if client_id:
        params["client_id"] = client_id
    resp = _api("GET", "/templates", params=params)
    data = resp.json()
    if not data:
        console.print("[yellow]No templates found.[/]")
        return
    table = Table(title="Campaign Templates")
    table.add_column("ID", style="dim")
    table.add_column("Name")
    table.add_column("Client")
    table.add_column("Difficulty")
    table.add_column("Active")
    table.add_column("Created")
    for t in data:
        table.add_row(
            t["id"][:8],
            t["name"],
            t["client_id"][:8],
            t["difficulty"],
            "✅" if t["is_active"] else "—",
            t["created_at"][:10],
        )
    console.print(table)


@template.command("get")
@click.argument("template_id")
def template_get(template_id):
    """Show template details."""
    resp = _api("GET", f"/templates/{template_id}")
    data = resp.json()
    console.print(Panel(f"[bold]{data['name']}[/]"))
    console.print(f"Description: {data.get('description', '-')}")
    console.print(f"Difficulty: {data['difficulty']}")
    console.print(f"Scenario Weights: {data.get('scenario_weights', 'None')}")
    console.print(f"Active: {'✅' if data['is_active'] else '—'}")


@template.command("delete")
@click.argument("template_id")
def template_delete(template_id):
    """Deactivate a template."""
    resp = _api("DELETE", f"/templates/{template_id}")
    console.print(f"[green]Template deactivated[/]")


cli.add_command(template)


if __name__ == "__main__":
    cli()
