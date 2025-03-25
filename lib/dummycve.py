#!/usr/bin/env python
"""
python lib/dummy.py \
    tenant

output:
{
  "issues": {
    "fixed": [
      { "id": "CPAAS-1234", "source": "issues.redhat.com" },
      { "id": "CPAAS-5678", "source": "issues.redhat.com" }
    ]
  }
}
"""

import argparse
import json
import os
import requests


def dummy():
    parser = argparse.ArgumentParser(description='dummy cve collector')
    parser.add_argument(
        "mode",
        choices=["managed", "tenant"],
        help="Mode in which the script is called. It does not have any impact for this script."
    )
    parser.add_argument('-r', '--release', help='Path to current Release json file', required=True)
    parser.add_argument('-p', '--previousRelease', help='Path to previous Release json file', required=True)
    vars(parser.parse_args())

    return create_json_record()

def create_json_record():
    data = {
        "cves":
            [{ "key": "CVE-2024-8260", "component": "comp2" }]
    }
    return data

if __name__ == "__main__":
    return_issues = dummy()
    print(json.dumps(return_issues))
