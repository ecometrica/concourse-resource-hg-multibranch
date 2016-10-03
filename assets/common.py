import os
import json
import subprocess


def get_payload(stdin):
    """
        Get payload from file desc. Dump it to a file for reference as well.
    """
    payload = json.load(stdin)
    with open("/tmp/hg-resource-payload", 'w') as f:
        json.dump(payload, f)
    return payload


def update_repo(uri, dest):
    """
        Clone/pull hg repo
    """
    if not os.path.exists(dest):
        subprocess.check_call(
            ['hg', 'clone', uri, dest],
            stdout=2
        )
    else:
        subprocess.check_call(
            ['hg', '-R', dest, 'pull'],
            stdout=2
        )


def get_branches(repo):
    """
        Give an repo, get all branches as [<branch_name>:<sha>, ...]
    """
    hg_branches = [
        'hg', '-R', repo, 'branches', '--template', '{branch}:{node};'
    ]

    hg = subprocess.Popen(hg_branches, stdout=subprocess.PIPE)
    branches = hg.communicate()
    return [br for br in str(branches[0]).split(';') if br]


def find_branch(target, branches):
    """
        Looks for a target branch in a list of branches.
        Branches are defined as <brach_name>:<sha>.

    :param target: Branch to look for.
    :param branches: Branches to search among.
    :return: 1, branch if match with same sha
             2, branch if match with different sha
             3, None if no match.
    """
    target_parts = target.split(":")
    target_name = target_parts[0]
    target_rev = target_parts[1]

    for branch in branches:
        branch_parts = branch.split(":")
        branch_name = branch_parts[0]
        branch_rev = branch_parts[1]

        if branch_name == target_name:
            if branch_rev == target_rev:
                return 1, branch
            else:
                return 2, branch

    return 3, None


def get_versions(built_branches, current_branches):
    """ Gets the next set of versions given the already built
        branches and available branches.

        This algorithm will return an ever growing list of branches. Once all
        branches are built, the list will stop growing and the builds will
        stop. Adding new branches or adding new commits to the branch will
        update the list again, hopefully building all new pushes without
        building too much.

        The general algorithm is as follows:

            For each branch in already built branches:
                1. Check if this branch is among the current_branches.
                    - If it is and same rev. Remove from possible new versions.
                    - If it is and different rev. Move the branch up in the
                      version list and return.
                    - If it's not found, remove from the versions list.
                2. If we get to the end (i.e. no updated branches ), check
                   if we have more available than built branches. If so, add
                   one new branch to versions and return. Otherwise return
                   versions.
    """
    versions = list(built_branches)
    possible_new_branches = list(current_branches)

    for branch in built_branches[::-1]:
        status, match = find_branch(branch, current_branches)
        if status == 1: # Found, same version
            possible_new_branches.remove(branch)
        if status == 2: # Found, new versions
            versions.remove(branch)
            return [match] + versions
        if status == 3: # Not found, remove the branch.
            versions.remove(branch)

    if len(versions) != len(current_branches):
        versions = [possible_new_branches[-1]] + versions

    return versions
