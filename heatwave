#!/usr/bin/env python

# A Git Terminal Commit Viewer
# Author: James Stoup
# Date: 14 APR 2019

import sys
import csv
import optparse
import time
import os

import subprocess
from datetime import timedelta, date, datetime


def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + timedelta(n)

def main():
    """ Print a visualization of your git history """
    # Get a year back from today
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)

    # the git command to pull out what we need
    since_str = start_date.strftime("%d %b %Y")
    before_str = end_date.strftime("%d %b %Y")
    repo = '/home/jstoup/test_repo'
    git_cmd = ['git',
               'log',
               '--date=short',
               '--pretty=format:"%ad %an"',
               '--since="%s"' % since_str,
               '--before="%s"' % before_str]
    
    # process the command 
    process_git = subprocess.Popen(git_cmd, cwd=repo, stdout=subprocess.PIPE)
    process_sort = subprocess.Popen(['sort'], stdin=process_git.stdout, stdout=subprocess.PIPE)
    process_uniq = subprocess.Popen(['uniq', '-c'], stdin=process_sort.stdout, stdout=subprocess.PIPE)
    process_grep = subprocess.Popen(['grep', '-i', 'stoup'], stdin=process_uniq.stdout, stdout=subprocess.PIPE)
    output = process_grep.communicate()[0]

    # clean up the output
    first_day = ''
    last_day = ''
    user_history = {}
    lines = output.splitlines()
    for i, line in enumerate(lines):
        cur_line = line.decode().strip()
        clean_line = cur_line.replace('"', '')
        count, rest_of_str = clean_line.split(' ', 1)
        commit_date, commit_name = rest_of_str.split(' ', 1)

        # build the dictionary
        user_history.update({commit_date : int(count)})

        if i == 0:
            first_day = commit_date

        if i == (len(lines)-1):
            last_day = commit_date

    ###############
    ### WARNING ###
    ###############
    # if they don't have a year's worth of history, this could go bad quickly

    # get the months, starting from now and working back
    month_order = {}
    for key in user_history:
        month_int = int(key.split('-')[1])
        month = date(1900, month_int, 1).strftime('%b')
        month_order[month] = True

    for key in month_order:
        print('%3s  ' % key, end='')
    print('')

    
    # now finally print out the stats
    start_day = date(int(first_day.split('-')[0]), int(first_day.split('-')[1]), int(first_day.split('-')[2]))
    end_day = date(int(last_day.split('-')[0]), int(last_day.split('-')[1]), int(last_day.split('-')[2]))
    day_count = 0
    for day in daterange(start_day, end_day):
        cur_day = day.strftime('%Y-%m-%d')
        labels=['Mon', 'Wed', 'Fri']
        prefix = '    '

        if (day_count % 52) == 0:
            if (day_count / 52) == 1:
                print('%s ' % labels[0], end='')
            elif (day_count / 52) == 3:
                print('%s ' % labels[1], end='')
            elif (day_count / 52) == 5:
                print('%s ' % labels[2], end='')
            else:
                print('    ' , end='')
            
        if cur_day in user_history:
            symbol = '!'
            if user_history[cur_day] == 1:
                symbol = '.'
            if user_history[cur_day] == 2:
                symbol = '*'
            if user_history[cur_day] > 2:
                symbol = '#'
            print('%s' % symbol, end='')
        else:
            print(' ', end='')
            
        day_count = day_count + 1
        
        if day_count % 52 == 0:
            print('')

    print('')

if __name__ == '__main__':
    main()
