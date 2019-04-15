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
    """ Print a visualization of your git history """

    # put in a check in to see if the user name is valid
    # put in a check in to see if that directory is a git repo
    # put in a check to see if the user even has a year's worth of data
    
    if verbose:
        click.echo('EXTRA DATA COMING YOUR WAY!')

    # Get the start and end dates corresponding to exactly a year from today
    since_str, before_str = generate_dates()

    # Use git to determine what commits they made on which days
    output = find_commits(user_name, git_repo, since_str, before_str)

    # Clean up the output so it can be used
    user_history, first_day, last_day = process_output(output)

    # Print everything out
    print_months_header()
    print_heat_map(user_history, first_day, last_day)
    

if __name__ == '__main__':
    heatwave()
