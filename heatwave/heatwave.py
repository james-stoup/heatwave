#!/usr/bin/env python

"""
A Git Terminal Commit Viewer
Author: James Stoup
Date: 14 APR 2019
"""

import sys
import csv
import optparse
import time
import os
import click
import subprocess
import monthdelta
from datetime import timedelta, date, datetime
from collections import defaultdict





def print_git_users(git_repo):
    """ Print out a list of all users that have committed to the repo """
    print('Git Committers:')
    git_cmd = ['git',
               'shortlog',
               '-s']

    process_git = subprocess.Popen(git_cmd, cwd=git_repo, stdout=subprocess.PIPE)
    output = process_git.communicate()[0]

    lines = output.splitlines()
    users = []
    
    for i, line in enumerate(lines):
        clean_line = line.decode().strip()
        users.append(" ".join(clean_line.split()).split(' ')[1])

    for user in users:
        print('  {}'.format(user))

    print('')
    

def print_additional_stats(user_history, git_repo, user_name):
    """ Throw out some additional stats on the data generated """

    total_commit_days = len(user_history)
    total_commits = 0

    for key, value in user_history.items():
        total_commits += value

    print('Git Repository : {}'.format(os.path.basename(os.path.realpath(git_repo))))
    print('Git Author     : {}'.format(user_name))
    print('Total Days     : {}'.format(total_commit_days))
    print('Total Commits  : {}'.format(total_commits))
    print('')



def generate_status_values():
    """ Return the color and symbol values that will fill in the days  """
    space = '  '
    status_values = dict(
        color={
            1: u"\u001b[48;5;47m" + space + u"\u001b[0m",
            2: u"\u001b[48;5;40m" + space + u"\u001b[0m",
            3: u"\u001b[48;5;34m" + space + u"\u001b[0m",
            4: u"\u001b[48;5;28m" + space + u"\u001b[0m",
            5: u"\u001b[48;5;22m" + space + u"\u001b[0m"
        },
        symbol={
            1: '..',
            2: '--',
            3: '~~',
            4: '**',
            5: '##',
        })

    return status_values



def print_graph_key(status_type):
    """ Print out a key so the colors make sense """

    if status_type != 'number':

        print('  ==   KEY  ==')
        print('    ', end='')
        
        status_values = generate_status_values()
        for key, value in status_values[status_type].items():
            print('{}'.format(value), end='')

        print('')
        print('  0 ', end='')
        
        for key, value in status_values['color'].items():
            if key == 5:
                print('{}+'.format(key), end='')
            else:
                print('{} '.format(key), end='')

        print('')
        print('  ============')
        print('')
    

def print_status(shade, status_type, verbose):
    """ Function to print a space of different shades of green (lightest to darkest) """
    space = '  '
    status = generate_status_values()

    # either print the number of commits, or look in the dict
    if status_type == 'number':
        if shade < 10:
            shade = ' {}'.format(shade)
            if verbose:
                print(u"\u001b[48;5;253m" + str(shade) + u"\u001b[0m ", end='')
            else:
                print(u"\u001b[48;5;253m" + str(shade) + u"\u001b[0m", end='')
    else:
        shade = 5 if shade > 5 else shade
        if verbose:
            print('{} '.format(status[status_type].get(shade, space)), end='')
        else:
            print('{}'.format(status[status_type].get(shade, space)), end='')

        
def daterange(start_date , end_date):
    """ Return a series of dates from start to end  """

    for n in range(int ((end_date - start_date).days)):
        yield start_date + timedelta(n)


def generate_dates():
    """ Return the today's date and the day exactly a year previous  """

    # Get a year's worth of data, working back from today
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)

    since_str  = start_date.strftime("%d %b %Y")
    before_str = end_date.strftime("%d %b %Y")

    return (since_str, before_str)


def find_commits(user_name, git_repo, since_str, before_str):
    """ Find the number of commits for a user on each day of the preceeding year  """

    git_cmd = ['git',
               'log',
               '--date=short',
               '--pretty=format:"%ad %an"',
               '--since="{}"'.format(since_str),
               '--before="{}"'.format(before_str)]

    # eventually this git command will be replaced with a pure python implementation
    process_git  = subprocess.Popen(git_cmd, cwd=git_repo, stdout=subprocess.PIPE)
    output = process_git.communicate()[0]

    lines = output.splitlines()
    cleaned_lines = []

    for i, line in enumerate(lines):
        cleaned_lines.append(line.decode().strip().replace('"', ''))

    user_data = defaultdict(list)

    # get the commits per day for the user in question
    for cl in cleaned_lines:
        commit_date = (cl.split(' ', 1)[0])
        commit_user = (cl.split(' ', 1)[1])
        if user_name.lower() in commit_user.lower():
            user_data[commit_date].append(commit_user)

    user_history = {}
    
    # need to sort this list
    # now save number of commits per day
    for k, v in user_data.items():
        user_history[k] = len(v)

    first_day = datetime.now()
    last_day = first_day - timedelta(days=365)

    return user_history, first_day, last_day


def print_border(size):
    """ Print a simple border """

    for i in range(0, size):
        print('=', end='')
    print('')

    
def print_months_header(verbose):
    """ Print the header to show the months """

    prev_month = datetime.now()
    month_order = []
    month_header_str = '    '
    
    # get the months, starting from now and working back (so we know what order to print them in)
    for i in range(1, 13):
        month_order.append(prev_month.strftime('%b'))
        prev_month = prev_month + monthdelta.monthdelta(-1)

    month_order.reverse()

    for key in month_order:
        if verbose:
            month_header_str += ('       {}   '.format(key))
        else:
            month_header_str += ('   {}   '.format(key))

    print('')
    print(month_header_str, end='')
    print('')

    return len(month_header_str)

def print_heat_map(user_history, first_day, last_day, status_type, verbose):
    """ Display the heat map to the terminal using colors or symbols """

    # make sure we always start on a Sunday
    year_of_commits = daterange(last_day, first_day + timedelta(days=1))
    for date in year_of_commits:
        if date.strftime('%a') == "Sun":
            last_day = date
            break
    year_of_commits = daterange(last_day, first_day + timedelta(days=1))

    # sort the dates into weeks
    week_days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
    days = defaultdict(list)

    for x in year_of_commits:
        cur_day = x.strftime('%Y-%m-%d')   # format of the git commits
        week_day = x.strftime('%a')        # format to tell the day of the week
        days[week_day].append(cur_day)

    weeks = [days[day] for day in week_days]

    # Now print everything
    labels = ['   ', 'Mon', '   ', 'Wed', '   ', 'Fri', '   ']
    print_label = 0

    for days in weeks:
        # print the mon/wed/fri labels
        print('{}  '.format(labels[print_label]), end='')
        print_label += 1

        # print each commit day in the chosen format
        for day in days:
            if day in user_history:
                print_status(user_history[day], status_type, verbose)
            else:
                # verbose mode will print the day of the month
                if verbose:
                    print('{} '.format(day.split('-')[2]), end='')
                else:
                    # otherwise just print an empty space (might change later)
                    print('  ', end='')
        print(' ')



@click.command()
@click.argument('user-name')
@click.argument('git-repo', type=click.Path(exists=True), default='.')
@click.option('-l', '--list-committers', is_flag=True, help='Lists all the committers for a git repo')
@click.option('--status-type', type=click.Choice(['color', 'symbol', 'number']), default='color', help = 'Choose how to visualize the data')
@click.option('-v', '--verbose', is_flag=True, help='Prints additional information')
def heatwave(user_name, git_repo, status_type, verbose, list_committers):
    """ 
    Visualize your git history on the terminal!

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

    """

    dot_git_dir = os.path.join(git_repo, '.git')
    if os.path.isdir(dot_git_dir) is False:
        print('Invalid Repository Path: {}'.format(git_repo))
        print('Please enter a path to a valid git repository!')
        sys.exit()

    if list_committers:
        print_git_users(git_repo)
        sys.exit()
        
    # Get the start and end dates corresponding to exactly a year from today
    since_str, before_str = generate_dates()

    # Use git to determine what commits they made on which days
    #output = find_commits(user_name, git_repo, since_str, before_str)

    # Clean up the output so it can be used
    user_history, first_day, last_day = find_commits(user_name, git_repo, since_str, before_str)

    # Print everything out
    header_len = print_months_header(verbose)
    print_border(header_len)
    print_heat_map(user_history, first_day, last_day, status_type, verbose)
    print_border(header_len)
    print_graph_key(status_type)
    print(' ')

    if verbose:
        print_additional_stats(user_history, git_repo, user_name)

        
if __name__ == '__main__':
    heatwave()
