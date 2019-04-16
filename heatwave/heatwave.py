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



def print_additional_stats(user_history):
    """ Throw out some additional stats on the data generated """
    total_commit_days = len(user_history)
    total_commits = 0

    for key, value in user_history.items():
        total_commits += value

    print('Total Days    : %s' % total_commit_days)
    print('Total Commits : %s' % total_commits)
    

# Function to print a space of different shades of green (lightest to darkest)
def print_color(shade):
    if shade == 1:
        print(u"\u001b[48;5;47m" + " " + u"\u001b[0m", end='')
    elif shade == 2:
        print(u"\u001b[48;5;40m" + " " + u"\u001b[0m", end='')
    elif shade == 3:
        print(u"\u001b[48;5;34m" + " " + u"\u001b[0m", end='')
    elif shade == 4:        
        print(u"\u001b[48;5;28m" + " " + u"\u001b[0m", end='')
    else:
        print(' ', end='')


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

    print(output)
    
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

        # if i == 0:
        #     first_day = commit_date

        # if i == (len(lines)-1):
        #     last_day = commit_date


    first_day = datetime.now()
    last_day = first_day - timedelta(days=365)

    return (user_history, first_day, last_day)


def print_months_header():
    """ Print the header to show the months """
    # get the months, starting from now and working back (so we know what order to print them in)
    prev_month = datetime.now()
    month_order = []
    print('    ', end='')    
    for i in range(1, 13):
        month_order.append(prev_month.strftime('%b'))
        prev_month = prev_month + monthdelta.monthdelta(-1)

    month_order.reverse()
    
    for key in month_order:
        print('%3s  ' % key, end='')
    print('')


def print_heat_map(user_history, first_day, last_day):
    """ Display the heat map to the terminal using colors or symbols """
    # now finally print out the stats

    day_count = 0
    myarray = [[], [], [], [], [], [], []]
    week = 0
    day = 0
    for x in daterange(last_day, first_day):
        cur_day = x.strftime('%Y-%m-%d')
        cur_line = myarray[week]
        cur_line.append(day)
        myarray.insert(week, cur_line)
        week += 1
        day += 1

        if week == 6:
            week = 0

        if day == 51:
            day = 0


    for r in myarray:
        for c in r:
            print(c, end=' ')
        print()

                
    # for day in daterange(last_day, first_day):
    #     cur_day = day.strftime('%Y-%m-%d')
    #     labels=['Mon', 'Wed', 'Fri']
    #     prefix = '    '

    #     if (day_count % 52) == 0:
    #         if (day_count / 52) == 1:
    #             print('%s ' % labels[0], end='')
    #         elif (day_count / 52) == 3:
    #             print('%s ' % labels[1], end='')
    #         elif (day_count / 52) == 5:
    #             print('%s ' % labels[2], end='')
    #         else:
    #             print('    ' , end='')

    #     #print('%s ' % day_count, end='')


    #     if cur_day in user_history:
    #         print('X', end='')
    #     else:
    #         print('.', end='')

            
        #if cur_day in user_history:
        #     symbol = ''
        #     if user_history[cur_day] == 1:
        #         symbol = '.'
        #     if user_history[cur_day] == 2:
        #         symbol = '*'
        #     if user_history[cur_day] > 2:
        #         symbol = '#'
        #     print('%s' % symbol, end='')
        # else:
        #     print(' ', end='')
            
#        day_count = day_count + 1
        
#        if day_count % 52 == 0:
#            print('')

    print('')




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
    print_months_header()
    print_heat_map(user_history, first_day, last_day)

    if verbose:
        print_additional_stats(user_history)

        
if __name__ == '__main__':
    heatwave()
