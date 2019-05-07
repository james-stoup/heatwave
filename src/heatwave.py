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
from datetime import date, datetime, timedelta

import click
import git
import monthdelta
from git import Repo


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
    if user_name is None:
        user_name = "All"

    total_commit_days = len(user_history)
    total_commits = 0

    for key, value in user_history.items():
        total_commits += value

    print("Git Repository : {}".format(os.path.basename(os.path.realpath(git_repo))))
    print("Git Author     : {}".format(user_name))
    print("Total Days     : {}".format(total_commit_days))
    print("Total Commits  : {}".format(total_commits))
    print("")


def generate_status_values():
    """ Return the color and symbol values that will fill in the days  
    """

    space = "  "
    status_values = dict(
        color={
            1: u"\u001b[48;5;47m" + space + u"\u001b[0m",
            2: u"\u001b[48;5;40m" + space + u"\u001b[0m",
            3: u"\u001b[48;5;34m" + space + u"\u001b[0m",
            4: u"\u001b[48;5;28m" + space + u"\u001b[0m",
            5: u"\u001b[48;5;22m" + space + u"\u001b[0m",
        },
        symbol={1: "..", 2: "--", 3: "~~", 4: "**", 5: "##"},
    )

    return status_values


def print_graph_key(status_type):
    """ Print out a key so the colors make sense 

    :param status_type: 

    """
    if status_type != "number":

        print("  == COMMITS ==")
        print("    ", end="")

        status_values = generate_status_values()
        for key, value in status_values[status_type].items():
            print("{}".format(value), end="")

        print("")
        print("  0 ", end="")

        for key, value in status_values["color"].items():
            if key == 5:
                print("{}+".format(key), end="")
            else:
                print("{} ".format(key), end="")

        print("")
        print("  ============")
        print("")


def print_status(shade, status_type, verbose):
    """ Function to print a space of different shades of green (lightest to darkest) 

    :param shade: 
    :param status_type: 
    :param verbose: 

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
        shade = 5 if shade > 5 else shade
        if verbose:
            print("{} ".format(status[status_type].get(shade, space)), end="")
        else:
            print("{}".format(status[status_type].get(shade, space)), end="")


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


def print_heat_map(user_history, first_day, last_day, status_type, verbose):
    """ Display the heat map to the terminal using colors or symbols 

    :param user_history: 
    :param first_day: 
    :param last_day: 
    :param status_type: 
    :param verbose: 

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
                print_status(user_history[day], status_type, verbose)
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
@click.argument("git-repo-path", type=click.Path(exists=True), default=".")
@click.argument("user-name", required=False)
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
@click.option("-v", "--verbose", is_flag=True, help="Prints additional information")
def cli(
    user_name, git_repo_path, list_committers, years, all_users, status_type, verbose
):
    """ 

    Now you can view a beautiful representation of your git progress
    right here on the command line. No longer will you have to log
    into github to compulsively check to see how many commits you've
    made this year, now you can feel inadequate without ever having
    to leave the command line!

    Example: 
        # print standard output
        ./heatwave.py "James Stoup" /home/jstoup/my_git_repo

    Example:
        # print number of commits each day and show additional stats
        ./heatwave.py stoup /home/jstoup/my_git_repo --status-type number -v

    :param user_name: 
    :param git_repo_path: 
    :param list_committers: 
    :param years: 
    :param all_users: 
    :param status_type: 
    :param verbose: 

    """
    # Error checking
    dot_git_dir = os.path.join(git_repo_path, ".git")
    if os.path.isdir(dot_git_dir) is False:
        print("Invalid Repository Path: {}".format(git_repo_path))
        print("Please enter a path to a valid git repository!")
        sys.exit()

    if all_users is False and list_committers is False and user_name is None:
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
        user_history = find_commits(
            user_name, git_repo_path, end_date, start_date, all_users
        )

        # Print everything out
        header_len = print_months_header(verbose)
        print_border(header_len, years_label)
        print_heat_map(user_history, end_date, start_date, status_type, verbose)
        print_border(header_len)
        print("")

        end_date = start_date
        start_date = end_date - timedelta(days=365)

        if verbose:
            print_additional_stats(user_history, git_repo_path, user_name)

    print_graph_key(status_type)

    print(" ")


if __name__ == "__main__":
    cli()
