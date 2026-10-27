"""Warehouse Asset Maintenance Registry System.

This module registers warehouse machines, records service dates, raises alerts
for overdue inspections, and exports maintenance reports to JSON files.
"""

import json
import logging
import tempfile
from datetime import datetime, timedelta

# Global state and configuration
assets = {}
service_config = {"interval_days": 90}


def register_asset(asset_id, machine_type, logs=None):
    """Register a new warehouse asset into the registry."""
    if logs is None:
        logs = []

    if not asset_id or not str(asset_id).strip():
        logging.warning("Registration failed: Asset ID cannot be empty.")
        return

    if asset_id in assets:
        logging.warning(
            "Registration skipped: Asset %s is already registered.", asset_id
        )
        return

    today = datetime.now().strftime("%Y-%m-%d")
    assets[asset_id] = {"type": machine_type, "last_service": today}
    logs.append(asset_id)
    print(
        f"Registered {asset_id} - total registrations this call: {len(logs)}"
    )


def update_service_date(asset_id, date_str):
    """Update the last service date of an existing asset after validation."""
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        assets[asset_id]["last_service"] = date_str
    except KeyError:
        logging.error("Could not update %s: Asset not found.", asset_id)
    except ValueError:
        logging.error(
            "Invalid date format '%s' for %s. Expected YYYY-MM-DD.",
            date_str,
            asset_id,
        )


def due_for_inspection():
    """Return a list of asset IDs that are overdue for inspection."""
    due = []
    interval = timedelta(days=service_config["interval_days"])
    now = datetime.now()

    for asset_id, details in assets.items():
        last = datetime.strptime(details["last_service"], "%Y-%m-%d")
        if now - last > interval:
            due.append(asset_id)
    return due


def change_interval(days):
    """Update the global service inspection interval in days."""
    if not isinstance(days, int) or days <= 0:
        logging.warning(
            "Invalid service interval (%s days). Must be a positive integer.",
            days,
        )
        return
    service_config["interval_days"] = days


def export_service_report(filepath="maintenance.json"):
    """Export the current assets dictionary to a formatted JSON report."""
    with open(filepath, "w", encoding="utf-8") as report_file:
        report_file.write(json.dumps(assets, indent=2))
    print(f"Report written to {filepath}")


def write_scratch_copy():
    """Write a temporary scratch copy of the asset registry safely."""
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False, encoding="utf-8"
    ) as scratch_file:
        scratch_file.write(json.dumps(assets))
        path = scratch_file.name
    print(f"Scratch copy at {path}")


def print_alerts():
    """Print overdue inspection alerts for all qualifying assets."""
    for asset_id in due_for_inspection():
        machine_type = assets[asset_id]["type"]
        print(f"ALERT: inspection overdue for {asset_id} ({machine_type})")


def main():
    """Execute the main warehouse asset registry workflow."""
    logging.basicConfig(
        level=logging.INFO, format="%(levelname)s: %(message)s"
    )

    register_asset("FL-01", "Forklift")
    register_asset("CV-07", "Conveyor")
    register_asset("", "Pallet Jack")
    register_asset("FL-01", "Crane")

    update_service_date("FL-01", "2025-01-15")
    update_service_date("XX-99", "2025-02-01")
    change_interval(-30)

    prompt = "Last service date for CV-07 (YYYY-MM-DD, Enter to skip): "
    user_date = input(prompt).strip()
    if user_date:
        update_service_date("CV-07", user_date)

    if not assets:
        raise RuntimeError("No assets registered in the system.")

    print_alerts()
    export_service_report()
    write_scratch_copy()


if __name__ == "__main__":
    main()