# heatwave

A tool for displaying a visual representation of your git history. This generates a heat map of your git commits, similar to how GitHub's heat map looks.


## Requirements

To run this you will need the following modules from pip:

  * click
  * monthdelta
  
  
## Usage

To view basic status on a user do this:

```./heatwave.py 'James Stoup' /path/to/my/repo```


To view more stats on the user:

```./heatwave.py --verbose 'James Stoup' /path/to/my/repo```


To view status with symbols instead of color:

```./heatwave.py --status-type symbol 'James Stoup' /path/to/my/repo```

