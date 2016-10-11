
"""Repo List Module."""

import re


def parse_repo_list(repo_list_file):
    """Parse Repo List."""
    repos = []

    pattern = re.compile(r"^\s*#.*")
    with open(repo_list_file, 'r') as repo_list_file:
        for line in repo_list_file:
            line = line.strip('\n')

            if line == "":
                continue
            elif pattern.match(line):
                continue

            repos.append(line)

    return repos
