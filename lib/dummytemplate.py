#!/usr/bin/env python
"""
python lib/dummytemplate.py \
    tenant

output:
{
  "template": {
    "synopsis": "testing title"
  }
}
"""

import argparse
import json
import os
import requests


def dummy():
    parser = argparse.ArgumentParser(description='dummy template collector')
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
        "template": {
            "synopsis": "testing title"
        }
    }
    return data

if __name__ == "__main__":
    return_issues = dummy()
    print(json.dumps(return_issues))
