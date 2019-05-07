[![License](http://img.shields.io/:license-gpl3-blue.svg?style=flat-square)](http://www.gnu.org/licenses/gpl-3.0.html)

# Heatwave

A tool for displaying a visual representation of your git history. 

Heatwave generates a heat map of your git commits, similar to how GitHub's heat map looks. View all commits or a single user's commits for the past year or previous years. Now in stylish red and green colors it makes the perfect Christmas gift.

Behold the beauty of command line graphics!

![Wicked Cool Graphic!](https://github.com/james-stoup/heatwave/blob/master/resources/heatwave-red.png)


## Dependencies
You will probably need to install an environment tool to manage different version of pythons. After you are on Python 3.7+ then install Pip to most easily install heatwave.

[Install PyEnv first](https://github.com/pyenv/pyenv-installer "PyEnv")

[Install Pip second](https://pip.pypa.io/en/stable/installing/ "Pip")


## Installation
I always vote for the easy way, but do what you want I guess...

### Recommend Way
The fastest way to install heatwave is with pip.

```pip install heatwave```

### Manual Way

To install this manually, clone this repo and then install all neede requirements use pip like so:

```
git clone https://github.com/james-stoup/heatwave.git
cd heatwave
pip install -r requirements.txt'
```

  
## Usage

### View All Committers
View repo stats for all committers:

```
$ ./heatwave.py /path/to/my/repo -a
```

![All Commits](https://github.com/james-stoup/heatwave/blob/master/resources/all-users-1-year.png)


### View All Committers For Several Years
View 3 years worth of commits:

```
$ ./heatwave.py /path/to/my/repo -a -y 3
```

![3 Years of Committs](https://github.com/james-stoup/heatwave/blob/master/resources/all-users-3-years.png)


### View A Specific Committer
View stats on a particular committer:

```
$ ./heatwave.py 'James Stoup' /path/to/my/repo
```

![One User](https://github.com/james-stoup/heatwave/blob/master/resources/one-user.png)


### View Number of Commits
View number of commits a user made, instead of color:

```
$ ./heatwave.py --status-type number 'James Stoup' /path/to/my/repo
```

![One User By Numbers](https://github.com/james-stoup/heatwave/blob/master/resources/one-user-numbers.png)


### Other Options
List everyone who committed to this repo:

```
$ ./heatwave.py /path/to/my/repo -l
```


View detailed stats on a particular committer:

```
$ ./heatwave.py -v 'James Stoup' /path/to/my/repo
```


View detailed stats on everyone going back 10 years

```
$ ./heatwave.py /path/to/my/repo -v -a -y 10
```

