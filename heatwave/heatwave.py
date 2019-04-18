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
from datetime import timedelta, date, datetime
import monthdelta


def print_git_users(git_repo):
    git_cmd = ['git',
               'shortlog',
               '-s']

    process_git = subprocess.Popen(git_cmd, cwd=git_repo, stdout=subprocess.PIPE)
    process_cut = subprocess.Popen(['cut', '-c8-'], stdin=process_git.stdout, stdout=subprocess.PIPE)
    process_sort = subprocess.Popen(['sort'], stdin=process_cut.stdout, stdout=subprocess.PIPE)
    output = process_sort.communicate()[0]

    lines = output.splitlines()
    for line in lines:
        print('  {}'.format(line.decode().strip()))
    

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
    

def print_status(shade, status_type):
    """ Function to print a space of different shades of green (lightest to darkest) """
    space = '  '
    status = generate_status_values()

    # either print the number of commits, or look in the dict
    if status_type == 'number':
        print('{} '.format(shade), end='')
    else:
        shade = 5 if shade > 5 else shade
        print('{} '.format(status[status_type].get(shade, space)), end='')

        
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

    sed_cmd = ['sed',
               's/\([A-Za-z]\)-\([A-Za-z]\)/\1 \2/g']

    tr_cmd = ['tr',
              '[:upper:]',
              '[:lower:]']
    
    # a series of bash tricks to get what we want
    # so this is super hacky and really needs to be reworked
    process_git  = subprocess.Popen(git_cmd, cwd=git_repo, stdout=subprocess.PIPE)
    process_sed  = subprocess.Popen(sed_cmd, stdin=process_git.stdout, stdout=subprocess.PIPE)
    process_tr   = subprocess.Popen(tr_cmd, stdin=process_sed.stdout, stdout=subprocess.PIPE)
    process_sort = subprocess.Popen(['sort'], stdin=process_tr.stdout, stdout=subprocess.PIPE)
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

    suns = []
    mons = []
    tues = []
    weds = []
    thrs = []
    fris = []
    sats = []

    # make sure we always start on a Sunday
    year_of_commits = daterange(last_day, first_day + timedelta(days=1))
    for date in year_of_commits:
        if date.strftime('%a') == "Sun":
            last_day = date
            break
    year_of_commits = daterange(last_day, first_day + timedelta(days=1))
    
    # sort the dates into weeks
    for x in year_of_commits:
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
        else:
            print('Something has gone wrong...')


    weeks = [suns, mons, tues, weds, thrs, fris, sats]

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
                print_status(user_history[day], status_type)
            else:
                if verbose:
                    print('{} '.format(day.split('-')[2]), end='')
                else:
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
        print('Git Committers:')
        print_git_users(git_repo)
        sys.exit()
        
    # Get the start and end dates corresponding to exactly a year from today
    since_str, before_str = generate_dates()

    # Use git to determine what commits they made on which days
    output = find_commits(user_name, git_repo, since_str, before_str)

    # Clean up the output so it can be used
    user_history, first_day, last_day = process_output(output)

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
