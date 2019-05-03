# heatwave

A tool for displaying a visual representation of your git history. 

Heatwave generates a heat map of your git commits, similar to how GitHub's heat map looks. View all commits or a single user's commits for the past year or previous years.


## Installation

Clone this repo and then install all neede requirements use pip like so:

```pip install -r requirements.txt'```

  
## Usage

View repo stats for all committers:

```./heatwave.py /path/to/my/repo -a```


List everyone who committed to this repo:

```./heatwave.py /path/to/my/repo -l```


View stats on a particular committer:

```./heatwave.py 'James Stoup' /path/to/my/repo```


View detailed stats on a particular committer:

```./heatwave.py -v 'James Stoup' /path/to/my/repo```


View number of commits instead of color:

```./heatwave.py --status-type number 'James Stoup' /path/to/my/repo```


View several years worth of commits:

```./heatwave.py 'James Stoup' /path/to/my/repo -y 3```


View detailed stats on everyone going back 10 years

```./heatwave.py /path/to/my/repo -v -a -y 10```

