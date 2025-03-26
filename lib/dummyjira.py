#!/usr/bin/env python
"""
python lib/dummyjira.py \
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
    parser = argparse.ArgumentParser(description='dummy jira collector')
    parser.add_argument(
        "mode",
        choices=["managed", "tenant"],
        help="Mode in which the script is called. It does not have any impact for this script."
    )
    parser.add_argument('-u', '--url', help='URL to Jira', required=True)
    parser.add_argument('-q', '--query', help='Jira qrl query', required=True)
    parser.add_argument('-c', '--credentials-file', help='Path to credentials file', required=True)
    parser.add_argument('-r', '--release', help='Path to current Release json file', required=True)
    parser.add_argument('-p', '--previousRelease', help='Path to previous Release json file', required=True)
    vars(parser.parse_args())

    return create_json_record()

def create_json_record():
    """
    {
        "issues": {
            "fixed": [
               { "id": "CPAAS-1234", "source": "issues.redhat.com" },
               { "id": "CPAAS-5678", "source": "issues.redhat.com" }
            ]
        }
    }
    """
    data = {
        "issues": {
            "fixed":
                [
                    { "id": "RELEASE-1502", "source": "issues.redhat.com" }
                ]
        }
    }
    return data

if __name__ == "__main__":
    return_issues = dummy()
    print(json.dumps(return_issues))
