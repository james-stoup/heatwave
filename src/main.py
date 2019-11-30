#!/usr/bin/env python

"""

A Git Terminal Commit Viewer

:author James Stoup

Date: 14 APR 2019

"""


import csv
import optparse
import os
import subprocess
import sys
import time
from collections import defaultdict
from datetime import date
from datetime import datetime
from datetime import timedelta

import click
import git
import monthdelta
from git import Repo

VERSION = "1.2.0"

# shamelessly copied from thispointer.com by Varun
def mergeDict(dict1, dict2):
    """ Merge dictionaries and add values of common keys"""
    dict3 = {**dict1, **dict2}
    for key, value in dict3.items():
        if key in dict1 and key in dict2:
            dict3[key] = value + dict1[key]

    return dict3


def init_git(git_repo_path):
    """ Test to see if we can even connect to the repo given 

    :param git_repo_path: 

    """
    repo = Repo(git_repo_path)
    if repo.bare:
        print("Error - unable to access the git repo")
        sys.exit()


def print_git_users(git_repo_path):
    """ Print out a list of all users that have committed to the repo 

    :param git_repo_path: 

    """
    print("Git Committers:")
    g = git.Git(git_repo_path)
    lines = g.shortlog("-s").splitlines()
    users = {}

    for line in lines:
        clean_line = line.strip()
        commits = (" ".join(line.split()).split(" ", 1))[0]
        author = (" ".join(line.split()).split(" ", 1))[1]
        users[author] = commits

    for key, val in users.items():
        print("     {:>5} - {}".format(val, key))

    print("")


def print_additional_stats(user_history, git_repo, user_name):
    """ Throw out some additional stats on the data generated 

    :param user_history: 
    :param git_repo: 
    :param user_name: 

    """
    if not user_name:
        user_name = "All"

    total_commit_days = len(user_history)
    total_commits = 0

    for key, value in user_history.items():
        total_commits += value

    print("Git Author     : {}".format(user_name))
    print("Total Days     : {}".format(total_commit_days))
    print("Total Commits  : {}".format(total_commits))
    print("")


def gen_slots(offset):
    """ Generate the slots that the slotter function will use"""

    # the slots list will get used by the legend at the end
    slots = [offset * i for i in range(1, 6)]
    return slots


def slotter(offset, input_value):
    """ Creates buckets based on an offset and returns which index the input goes in """
    slots = gen_slots(offset)

    # walk through the slots until we find the index that it goes in
    for index, value in enumerate(slots):
        if input_value <= value:
            return index + 1

    return len(slots)


def generate_status_values():
    """ Return the color and symbol values that will fill in the days """

    space = "  "
    end = u"\u001b[0m"

    # normal colors
    g1 = u"\u001b[48;5;118m"  # bright green (less commits)
    g2 = u"\u001b[48;5;40m"
    g3 = u"\u001b[48;5;34m"
    g4 = u"\u001b[48;5;29m"
    g5 = u"\u001b[48;5;22m"  # dark green   (more commits)

    # colors for those with dark terminal schemes
    r1 = u"\u001b[48;5;52m"  # dark red (less commits)
    r2 = u"\u001b[48;5;88m"
    r3 = u"\u001b[48;5;124m"
    r4 = u"\u001b[48;5;160m"
    r5 = u"\u001b[48;5;196m"  # bright red   (more commits)

    status_values = dict(
        greens={
            1: g1 + space + end,
            2: g2 + space + end,
            3: g3 + space + end,
            4: g4 + space + end,
            5: g5 + space + end,
        },
        reds={
            1: r1 + space + end,
            2: r2 + space + end,
            3: r3 + space + end,
            4: r4 + space + end,
            5: r5 + space + end,
        },
        symbol={1: "..", 2: "--", 3: "~~", 4: "**", 5: "##"},
    )

    return status_values


def print_graph_key(status_type, dark_mode, shade_offset):
    """ Print out a key so the colors make sense 

    :param status_type: 
    :param dark_mode: 

    """

    # number's don't need a key, only symbols and colors
    if status_type != "number":

        print("  == COMMITS ==")

        status_values = generate_status_values()
        status_color = "symbol"

        # put in a check to handle darker terminals
        if status_type == "color":
            status_color = "greens"
            if dark_mode == True:
                status_color = "reds"

        # I liked the colors to be horizontal rather than vertical,
        # but now that you can specify the offset, if the offset is
        # larger than 4 then it starts to not line up anymore and so
        # to permanently combat that I just did it this way. Sigh.
        slots = gen_slots(shade_offset)
        print("          0")

        for key, value in enumerate(slots):
            color_to_print = status_values[status_color][key + 1]
            print("    {}".format(color_to_print), end="")
            print("{}".format(color_to_print), end="")

            if key == len(slots) - 1:
                print("  {}+".format(value))
            else:
                print("  {} ".format(value))

        print("  ============")
        print("")


def print_status(shade, status_type, verbose, dark_mode, shade_offset):
    """ Function to print a space of different shades of green (lightest to darkest) 

    :param shade: 
    :param status_type: 
    :param verbose: 
    :param dark_mode: 

    """
    space = "  "
    status = generate_status_values()

    # either print the number of commits, or look in the dict
    if status_type == "number":
        if shade < 10:
            shade = " {}".format(shade)

        if verbose:
            print(u"\u001b[48;5;253m" + str(shade) + u"\u001b[0m ", end="")
        else:
            print(u"\u001b[48;5;253m" + str(shade) + u"\u001b[0m", end="")
    else:
        status_color = ""
        # put in a check to handle darker terminals
        if status_type == "color":
            status_color = "greens"
            if dark_mode is True:
                status_color = "reds"
        else:
            status_color = "symbol"

        new_shade = slotter(shade_offset, shade)

        if verbose:
            print("{} ".format(status[status_color].get(new_shade, space)), end="")
        else:
            print("{}".format(status[status_color].get(new_shade, space)), end="")


def daterange(start_date, end_date):
    """ Return a series of dates from start to end  

    :param start_date: 
    :param end_date: 

    """
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)


def find_commits(user_name, git_repo_path, end_date, start_date, all_users):
    """ Find the number of commits for a user on each day of the preceeding year  

    :param user_name: 
    :param git_repo_path: 
    :param end_date: 
    :param start_date: 
    :param all_users: 

    """
    since_str = start_date.strftime("%d %b %Y")
    before_str = end_date.strftime("%d %b %Y")

    g = git.Git(git_repo_path)
    lines = g.log(
        "--date=short",
        '--pretty=format:"%ad %an"',
        '--since="{}"'.format(since_str),
        '--before="{}"'.format(before_str),
    ).splitlines()

    cleaned_lines = []

    for line in lines:
        cleaned_lines.append(line.strip().replace('"', ""))

    user_data = defaultdict(list)

    # get the commits per day for the user in question
    for cl in cleaned_lines:
        commit_date = cl.split(" ", 1)[0]
        commit_user = cl.split(" ", 1)[1]
        if all_users is True:
            user_data[commit_date].append(commit_user)
        else:
            if user_name.lower() in commit_user.lower():
                user_data[commit_date].append(commit_user)

    user_history = {}

    # now save number of commits per day
    for k, v in user_data.items():
        user_history[k] = len(v)

    first_day = datetime.now()
    last_day = first_day - timedelta(days=365)

    return user_history


def print_border(size, msg=""):
    """ Print a simple border 

    :param size: 
    :param msg: 

    """
    for i in range(0, size):
        print("=", end="")
    print(msg, end="")
    print("")


def print_months_header(verbose):
    """ Print the header to show the months 

    :param verbose: 

    """
    prev_month = datetime.now()
    month_order = []
    month_header_str = "    "

    # get the months, starting from now and working back (so we know what order to print them in)
    for i in range(1, 13):
        month_order.append(prev_month.strftime("%b"))
        prev_month = prev_month + monthdelta.monthdelta(-1)

    month_order.reverse()

    for key in month_order:
        if verbose:
            month_header_str += "       {}   ".format(key)
        else:
            month_header_str += "   {}   ".format(key)

    print(month_header_str, end="")
    print("")

    return len(month_header_str)


def print_heat_map(
    user_history, first_day, last_day, status_type, verbose, dark_mode, shade_offset
):
    """ Display the heat map to the terminal using colors or symbols 

    :param user_history: 
    :param first_day: 
    :param last_day: 
    :param status_type: 
    :param verbose: 
    :param dark_mode: 

    """
    # make sure we always start on a Sunday
    year_of_commits = daterange(last_day, first_day + timedelta(days=1))
    for date in year_of_commits:
        if date.strftime("%a") == "Sun":
            last_day = date
            break
    year_of_commits = daterange(last_day, first_day + timedelta(days=1))

    # sort the dates into weeks
    week_days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    days = defaultdict(list)

    for x in year_of_commits:
        cur_day = x.strftime("%Y-%m-%d")  # format of the git commits
        week_day = x.strftime("%a")  # format to tell the day of the week
        days[week_day].append(cur_day)

    weeks = [days[day] for day in week_days]

    # Now print everything
    labels = ["   ", "Mon", "   ", "Wed", "   ", "Fri", "   "]
    print_label = 0

    for days in weeks:
        # print the mon/wed/fri labels
        print("{}  ".format(labels[print_label]), end="")

        # print each commit day in the chosen format
        for day in days:
            if day in user_history:
                print_status(
                    user_history[day], status_type, verbose, dark_mode, shade_offset
                )
            else:
                # verbose mode will print the day of the month
                if verbose:
                    print("{} ".format(day.split("-")[2]), end="")
                else:
                    # otherwise just print an empty space (might change later)
                    print("  ", end="")

        print_label += 1
        print(" ")


@click.command()
@click.version_option(version=VERSION)
@click.argument(
    "git-repo-path", type=click.Path(exists=True), default=".", required=True
)
@click.argument("user-names", nargs=-1, required=False)
@click.option(
    "-l",
    "--list-committers",
    is_flag=True,
    help="Lists all the committers for a git repo",
)
@click.option("-y", "--years", default=1, help="Print more than one year")
@click.option(
    "-a",
    "--all-users",
    is_flag=True,
    help="Print heat map for all users, not just a single user",
)
@click.option(
    "--status-type",
    type=click.Choice(["color", "symbol", "number"]),
    default="color",
    help="Choose how to visualize the data",
)
@click.option(
    "-o",
    "--shade-offset",
    default=1,
    help="Manually set the offset for determining the colors",
)
@click.option("-v", "--verbose", is_flag=True, help="Prints additional information")
@click.option(
    "-d",
    "--dark-mode",
    is_flag=True,
    default=False,
    help="Prints in red for darker color schemes",
)
def cli(
    user_names,
    git_repo_path,
    list_committers,
    years,
    all_users,
    status_type,
    shade_offset,
    verbose,
    dark_mode,
):
    """ 

    Now you can view a beautiful representation of your git progress
    right here on the command line. No longer will you have to log
    into github to compulsively check to see how many commits you've
    made this year, now you can feel inadequate without ever having
    to leave the command line!

    ######### Example 1 #########

        Print standard output

        ./heatwave.py /path/to/git/repo "James Stoup"


    ######### Example 2 #########

        Print number of commits each day and show additional stats

        ./heatwave.py /path/to/git/repo stoup --status-type number -v


    ######### Example 3 #########

        Print several users combined output

        ./heatwave.py /path/to/git/repo james, bob, "LORD CODER III", jack


    ######### Example 4 #########

        Change the default offset to a step of 5

        ./heatwave.py /path/to/git/repo captain_derp -o 5

    """

    # Error checking
    dot_git_dir = os.path.join(git_repo_path, ".git")
    if os.path.isdir(dot_git_dir) is False:
        print("Invalid Repository Path: {}".format(git_repo_path))
        print("Please enter a path to a valid git repository!")
        sys.exit()

    if all_users is False and list_committers is False and not user_names:
        print("Must supply a USER NAME if the -l or -a flags are not used")
        sys.exit()

    # everything else depends on git working, so hop to it
    init_git(git_repo_path)

    if list_committers:
        print_git_users(git_repo_path)
        sys.exit()

    # loop through the years
    end_date = datetime.now()
    start_date = end_date - timedelta(
        days=365
    )  # Get a year's worth of data, working back from today

    for i in range(years):
        print("")
        years_label = "\t{} - {}".format(
            start_date.strftime("%Y"), end_date.strftime("%Y")
        )

        # if no users specified, just print everything
        if all_users:
            user_names = ["All"]

        # this handles multiple users, a new and handy feature!
        merged_history = {}

        for user in user_names:
            # find each user's history
            user_history = find_commits(
                user, git_repo_path, end_date, start_date, all_users
            )

            if verbose:
                print_additional_stats(user_history, git_repo_path, user)

            merged_history = mergeDict(merged_history, user_history)

        # Print everything out
        header_len = print_months_header(verbose)
        print_border(header_len, years_label)
        print_heat_map(
            merged_history,
            end_date,
            start_date,
            status_type,
            verbose,
            dark_mode,
            shade_offset,
        )
        print_border(header_len)
        print("")

        end_date = start_date
        start_date = end_date - timedelta(days=365)

    print_graph_key(status_type, dark_mode, shade_offset)

    print(" ")


if __name__ == "__main__":
    cli()
