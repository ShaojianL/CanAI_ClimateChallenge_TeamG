"""Print the UI preview's 200 synthetic reports as JSON.

Run from the repository root: python -m scripts.generate_mock_reports
"""

import json

from services.mock_reports import generate_mock_reports


if __name__ == "__main__":
    print(json.dumps({"mock": True, "reports": generate_mock_reports()}, indent=2))
