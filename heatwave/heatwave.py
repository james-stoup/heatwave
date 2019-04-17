#!/usr/bin/env python

# A Git Terminal Commit Viewer
# Author: James Stoup
# Date: 14 APR 2019


import sys
import csv
import optparse
import time
import os
import click

import subprocess
from datetime import timedelta, date, datetime
import monthdelta



def print_additional_stats(user_history, git_repo, user_name):
    """ Throw out some additional stats on the data generated """
    total_commit_days = len(user_history)
    total_commits = 0

    for key, value in user_history.items():
        total_commits += value

    print('Git Repository : %s' % os.path.basename(os.path.normpath(git_repo)))
    print('Git Author     : %s' % user_name)
    print('Total Days     : %s' % total_commit_days)
    print('Total Commits  : %s' % total_commits)
    print('')
    

# Function to print a space of different shades of green (lightest to darkest)
def print_color(shade):
    space = '  '
    if shade == 1:
        print(u"\u001b[48;5;47m" + space + u"\u001b[0m", end='')
    elif shade == 2:
        print(u"\u001b[48;5;40m" + space + u"\u001b[0m", end='')
    elif shade == 3:
        print(u"\u001b[48;5;34m" + space + u"\u001b[0m", end='')
    elif shade >= 4:        
        print(u"\u001b[48;5;28m" + space + u"\u001b[0m", end='')
    else:
        print(space, end='')


def daterange(start_date, end_date):
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
    # the git command to pull out what we need
    # yeah, I know I could have use the git library, but that just seemed overkill...

    git_cmd = ['git',
               'log',
               '--date=short',
               '--pretty=format:"%ad %an"',
               '--since="%s"' % since_str,
               '--before="%s"' % before_str]

    # a series of bash tricks to get what we want
    process_git  = subprocess.Popen(git_cmd, cwd=git_repo, stdout=subprocess.PIPE)
    process_sort = subprocess.Popen(['sort'], stdin=process_git.stdout, stdout=subprocess.PIPE)
    process_uniq = subprocess.Popen(['uniq', '-c'], stdin=process_sort.stdout, stdout=subprocess.PIPE)
    process_grep = subprocess.Popen(['grep', '-i', user_name], stdin=process_uniq.stdout, stdout=subprocess.PIPE)
    output = process_grep.communicate()[0]

    return output


def process_output(output):
    """ Build a dictionary that ties number of commits to a date  """
    user_history = {}
    first_day = ''
    last_day  = ''
    lines = output.splitlines()

    for i, line in enumerate(lines):
        # this will turn each line into a format that can be easily used
        cur_line   = line.decode().strip()
        clean_line = cur_line.replace('"', '')
        count, rest_of_str = clean_line.split(' ', 1)
        commit_date, commit_name = rest_of_str.split(' ', 1)

        # build the dictionary
        user_history.update({commit_date : int(count)})


    first_day = datetime.now()
    last_day = first_day - timedelta(days=365)

    return (user_history, first_day, last_day)


def print_border(size):
    for i in range(0, size):
        print('=', end='')
    print('')
    
def print_months_header():
    """ Print the header to show the months """
    # get the months, starting from now and working back (so we know what order to print them in)
    prev_month = datetime.now()
    month_order = []
    month_header_str = '    '
    for i in range(1, 13):
        month_order.append(prev_month.strftime('%b'))
        prev_month = prev_month + monthdelta.monthdelta(-1)

    month_order.reverse()


    for key in month_order:
        month_header_str += ('   %s   ' % key)

    print('')
    print(month_header_str, end='')
    print('')

    return len(month_header_str)

def print_heat_map(user_history, first_day, last_day):
    """ Display the heat map to the terminal using colors or symbols """
    # now finally print out the stats
    suns = []
    mons = []
    tues = []
    weds = []
    thrs = []
    fris = []
    sats = []

    for x in daterange(last_day, first_day):
        cur_day = x.strftime('%Y-%m-%d')
        week_day = x.strftime('%a')
        
        if week_day == 'Sun':
            suns.append(cur_day)
        elif week_day == 'Mon':
            mons.append(cur_day)
        elif week_day == 'Tue':
            tues.append(cur_day)
        elif week_day == 'Wed':
            weds.append(cur_day)
        elif week_day == 'Thu':
            thrs.append(cur_day)
        elif week_day == 'Fri':
            fris.append(cur_day)
        elif week_day == 'Sat':
            sats.append(cur_day)

    weeks = [suns, mons, tues, weds, thrs, fris, sats]

    labels = ['   ', 'Mon', '   ', 'Wed', '   ', 'Fri', '   ']
    print_label = 0

    for days in weeks:
        print('%s  ' % labels[print_label], end='')
        print_label += 1

        for day in days:
            if day in user_history:
                #print('%s - %s' % (day, user_history[day]))
                print_color(user_history[day])
            else:
                print('  ', end='')
                #print('%s  ' % day, end='')
        print(' ')



@click.command()
@click.argument('user-name')
@click.argument('git-repo', type=click.Path(exists=True), default='.')
@click.option('--status-type', type=click.Choice(['color', 'symbol']), default='color', help = 'Choose how to visualize the data')
@click.option('--verbose', is_flag=True, help='Prints additional information')
def heatwave(user_name, git_repo, status_type, verbose):
    """ 
    Visualize your git history on the terminal!

    Now you can view a beautiful representation of your git progress
    right here on the command line. No longer will you have to log
    into github to compulsively check to see how many commits you've
    made this year, now you can feel inadequate without ever having
    to leave the command line!

    Example: ./heatwave.py "James Stoup" /home/jstoup/my_git_repo

    """

    dot_git_dir = os.path.join(git_repo, '.git')
    if os.path.isdir(dot_git_dir) is False:
        print('Invalid Repository Path: %s' % git_repo)
        print('Please enter a path to a valid git repository!')
        sys.exit()

    # Get the start and end dates corresponding to exactly a year from today
    since_str, before_str = generate_dates()

    # Use git to determine what commits they made on which days
    output = find_commits(user_name, git_repo, since_str, before_str)

    # Clean up the output so it can be used
    user_history, first_day, last_day = process_output(output)

    # Print everything out
    header_len = print_months_header()
    print_border(header_len)
    print_heat_map(user_history, first_day, last_day)
    print_border(header_len)
    print(' ')

    if verbose:
        print_additional_stats(user_history, git_repo, user_name)

        
if __name__ == '__main__':
    heatwave()
