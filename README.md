# heatwave

A tool for displaying a visual representation of your git history. 

Heatwave generates a heat map of your git commits, similar to how GitHub's heat map looks. View all commits or a single user's commits for the past year or previous years.


## Installation

Clone this repo and then install all neede requirements use pip like so:

```pip install -r requirements.txt'```

  
## Usage

### View All Committers
View repo stats for all committers:

```./heatwave.py /path/to/my/repo -a```

[[https://github.com/james-stoup/heatwave/blob/master/resources/all-users-1-year.png]]


### View All Committers For Several Years
View 3 years worth of commits:

```./heatwave.py 'James Stoup' /path/to/my/repo -y 3```

[[https://github.com/james-stoup/heatwave/blob/master/resources/all-users-3-years.png]]


### View A Specific Committer
View stats on a particular committer:

```./heatwave.py 'James Stoup' /path/to/my/repo```

[[https://github.com/james-stoup/heatwave/blob/master/resources/one-user.png]]


### View Number of Commits
View number of commits a user made, instead of color:

```./heatwave.py --status-type number 'James Stoup' /path/to/my/repo```

[[https://github.com/james-stoup/heatwave/blob/master/resources/one-user-numbers.png]]


### Other Options
List everyone who committed to this repo:

```./heatwave.py /path/to/my/repo -l```


View detailed stats on a particular committer:

```./heatwave.py -v 'James Stoup' /path/to/my/repo```


View detailed stats on everyone going back 10 years

```./heatwave.py /path/to/my/repo -v -a -y 10```

