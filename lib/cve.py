#!/usr/bin/env python
"""
python lib/cve.py \
    tenant \
    --release release.json \
    --previousRelease previous_release.json
"""


import argparse
import os
import tempfile
import re
import subprocess
import json
import logging
import sys
from typing import Any

pattern = r'CVE-\d+-\d+|CVE-\d+'

def find_cve():
    file_not_exists = 0
    parser = argparse.ArgumentParser()
    parser.add_argument(
            "mode",
            choices=["managed", "tenant"],
            help="Mode in which the script is called. It does not have any impact for this script.")
    parser.add_argument('-r', '--release', help='Path to current release file', required=True)
    parser.add_argument('-p', '--previousRelease', help='Path to previous release file', required=True)
    args = vars(parser.parse_args())

    if not os.path.isfile(args['release']):
        print(f"ERROR: Path to release file {args['release']} doesn't exists")
        file_not_exists = 1
    if not os.path.isfile(args['previousRelease']):
        print.error(f"ERROR: Path to previousRelease file {args['previousRelease']} doesn't exists")
        file_not_exists = 1
    if file_not_exists:
        exit(1)

    return components_info(args['release'], args['previousRelease'])


def read_json(file):
    if os.path.getsize(file) > 0:
        with open(file, 'r') as f:
            data = json.load(f)
        return data


def get_component_names(data_list):
    component_list = []
    for component_info in data_list:
        print(f"component_info: {component_info}", file=sys.stderr)
        for key, value in component_info.items():
            if (key == "name"):
                component_list.append(value)
    return component_list


def get_component_detail(data_list, component):
    print(f"looking for component detail: {component}", file=sys.stderr)
    for component_info in data_list:
        print(f"component_info: {components_info}", file=sys.stderr)
        if component == component_info["name"]:
            return component_info["source"]["git"]["url"], component_info["source"]["git"]["revision"]
    return([])


def get_snapshot_data(namespace, snapshot):
    cmd = ["kubectl", "get", "snapshot", snapshot, "-n", namespace, "-ojson"]
    try:
        cmd_str = " ".join(cmd)
        print(f"Running {cmd_str}", file=sys.stderr)
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError:
        print(f"Command {cmd_str} failed, check exception for details", file=sys.stderr)
        raise
    except Exception as exc:
        print("Unknown error occurred", file=sys.stderr)
        raise RuntimeError from exc

    print(result.stdout, file=sys.stderr)
    return json.loads(result.stdout)


def get_snapshot_name(data_release):
    return data_release['spec']['snapshot']


def get_snapshot_namespace(data_release):
    return data_release['metadata']['namespace']


def components_info(release, previousRelease):
    prev_component_list = []
    cves = {}
    data_release = read_json(release)
    data_prev_release = read_json(previousRelease)

    if data_release:
        snapshot_name = get_snapshot_name(data_release)
        snapshot_ns = get_snapshot_namespace(data_release)
        snapshot_data = get_snapshot_data(snapshot_ns, snapshot_name)
        current_component_list = snapshot_data['spec']['components']
        print(current_component_list, file=sys.stderr)
    else:
        print(f"Empty release file {release}", file=sys.stderr)
        exit(0)

    if data_prev_release:
        snapshot_prev_release_name = get_snapshot_name(data_prev_release)
        snapshot_prev_release_data = get_snapshot_data(snapshot_ns, snapshot_prev_release_name)
        prev_component_list = snapshot_prev_release_data['spec']['components']

    current_components = get_component_names(current_component_list)
    print(f"current_components: {current_components}", file=sys.stderr)
    prev_components = get_component_names(prev_component_list)
    print(f"prev_components: {prev_components}", file=sys.stderr)

    for component in current_components:
        (url_current, revision_current) = get_component_detail(current_component_list, component)
        print(f"url_current: {url_current}", file=sys.stderr)
        print(f"revision_current: {revision_current}", file=sys.stderr)
        if component in prev_components:
            (url_prev, revision_prev) = get_component_detail(prev_component_list, component)
            print(f"url_prev: {url_prev}", file=sys.stderr)
            print(f"revision_prev: {revision_prev}", file=sys.stderr)
            cves[component] = git_log_titles_per_component(url_current, revision_current, revision_prev)
        else:
            cves[component] = git_log_titles_per_component(url_current, revision_current, "")
    return create_cves_record(cves)


def git_log_titles_per_component(git_url, revision_current, revision_prev):
    tmpdir = tempfile.mkdtemp()
    git_cmd = ["git", "clone", git_url, tmpdir]
    cmd_str = " ".join(git_cmd)
    print(f"Running {cmd_str}", file=sys.stderr)
    result = subprocess.run(git_cmd, check=True, capture_output=True, text=True)
    if result.returncode != 0:
        print("Something went wrong cloning, details below:", file=sys.stderr)
        print(f"Command: '{' '.join(git_cmd)}'", file=sys.stderr)
        print(f"Stdout: '{result.stdout}'", file=sys.stderr)
        print(f"Stderr: '{result.stderr}'", file=sys.stderr)
        exit(result.returncode)

    print(f"Stdout: '{result.stdout}'", file=sys.stderr)
    os.chdir(tmpdir)

    if revision_prev and revision_current != revision_prev:
        git_cmd = ["git", "log", f"{revision_prev}..{revision_current}"]
    else:
        git_cmd = ["git", "show", "--quiet", f"{revision_current}"]

    cmd_str = " ".join(git_cmd)
    print(f"Running {cmd_str}", file=sys.stderr)
    result = subprocess.run(git_cmd, check=True, capture_output=True, text=True)
    if result.returncode != 0:
        print("Something went wrong cloning, details below:", file=sys.stderr)
        print(f"Command: '{' '.join(git_cmd)}'", file=sys.stderr)
        print(f"Stdout: '{result.stdout}'", file=sys.stderr)
        print(f"Stderr: '{result.stderr}'", file=sys.stderr)
        exit(result.returncode)

    print(f"Stdout: '{result.stdout}'", file=sys.stderr)
    return find_log_titles(result.stdout)


def find_log_titles(commit_titles):
    matching_titles = re.findall(pattern, commit_titles)
    return matching_titles


def create_cves_record(cves):
    """
    Input: cves (dictonary)
    {
      'comp1': ['CVE-1', 'CVE-3'],
      'comp2': ['CVE-2', 'CVE-4']
    }
    Output:
    {
        "releaseNotes": {
            "cves":  [
                { "key": "CVE-1", "component": "comp1" },
                { "key": "CVE-3", "component": "comp1" },
                { "key": "CVE-2", "component": "comp2" },
                { "key": "CVE-4", "component": "comp2" },
            ]
        }
    }
    or empty when no cves
    {"releaseNotes": {"cves": []}}
    """

    result = {
        "releaseNotes": {
            "cves": [
            ]
        }
    }

    if cves:

        print(cves, file=sys.stderr)
        for comp_name, keys in cves.items():
            for key in keys:
                result["releaseNotes"]["cves"].append({
                    "key": key,
                    "component": comp_name
                })

    return json.dumps(result)


if __name__ == "__main__":
    print(find_cve())
