"""Deterministic synthetic reports for the eight-street UI preview."""

MOCK_REPORT_COUNTS = {
    "WATER ST": 65,
    "DUCKWORTH ST": 50,
    "KENMOUNT RD": 35,
    "MILITARY RD": 25,
    "PRINCE PHILIP DR": 15,
    "FRESHWATER RD": 7,
    "GOWER ST": 3,
    "SIGNAL HILL RD": 0,
}


def generate_mock_reports() -> list[dict[str, str]]:
    """Return one report per fictional person; never use real identities."""
    reports = []
    for street_name, count in MOCK_REPORT_COUNTS.items():
        for _ in range(count):
            number = len(reports) + 1
            reports.append({
                "report_id": f"mock-report-{number:03d}",
                "reporter_id": f"mock-person-{number:03d}",
                "street_name": street_name,
                "source": "mock",
            })
    return reports
