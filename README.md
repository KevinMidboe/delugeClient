<h1 align="center">
  🐍 Python Deluge CLI
</h1>

<h4 align="center"> A easy to use Deluge CLI that can connect to Deluge RPC (even over ssh) written entirely in python.</h4>

| Tested version | PyPi package | Drone CI |
|:--------|:------|:------|:------------|
| [![PyVersion](https://img.shields.io/badge/python-3.8-blue.svg)](https://www.python.org/downloads/release/python-380/) | [![PyPI](https://img.shields.io/pypi/v/delugeClient_kevin)](https://pypi.org/project/delugeClient_kevin/) | [![Build Status](https://drone.schleppe.cloud/api/badges/KevinMidboe/delugeClient/status.svg)](https://drone.schleppe.cloud/KevinMidboe/delugeClient)


| Known vulnerabilities | License |
|:--------|:------|
| [![Known Vulnerabilities](https://snyk.io/test/github/kevinmidboe/delugeClient/badge.svg?targetFile=requirements.txt)](https://snyk.io/test/github/kevinmidboe/delugeClient?targetFile=requirements.txt) |[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)


<p align="center">
  <a href="#abstract">Abstract</a> •
  <a href="#setup_virtualenv">Setup virtualenv</a> •
  <a href="#configure">Configure</a> •
  <a href="#installation">Install dependencies</a> •
  <a href="#usage">Usage</a> •
  <a href="#running">Running</a> •
  <a href="#contributing">Contributing</a>
</p>


## <a name="abstract"></a> Abstract
Create a deluge python client for interfacing with deluge for common tasks like listing, adding, removing and setting download directory for torrents. 


## <a name="setup_virtualenv"></a> Setup Virtual Environment
Virtual environment allows us to create a local environment for the requirements needed. Because pip does not download packages already downloaded to your system, we can use virtualenv to save our packages in the project folder.


### <a name="installation"></a> Installation
To install virtualenv, simply run:  

```
 $ pip install virutalenv
```


### Usage
After you have downloaded this project go to it in your terminal by going to the folder you downloaded and typing the following:


```
 $ cd delugeClient/
```

The to setup a virtual environment enter this:

```
 $ virtualenv -p python3.6 env
```

 > If you get an error now it might be because you don't have python3.6, please make sure you have python version 3.6 if else you can download it from [here](https://www.python.org/downloads/)


First we navigate to the folder we downloaded.

Then we use the ```virtualenv``` command to create a ```env``` subdirectory in our project. This is where pip will download everything to and where we can add other specific python versions. Then we need to *activate* our virtual environment by doing:

```
 $ source env/bin/activate
```

You should now see a ```(env)``` appear at the beginning of your terminal prompt indicating that you are working from within the virtual environment. Now when you install something: 

```
 $ pip install <package>
```

It will get installed in the env folder, and not globaly on our machine. 

The leave our virtual environment run: 

```
 $ deactivate
```


## <a name="configure"></a> Configure the Config File

The following is where we need to do some manual editing of our config file. Open to ```config.ini``` in your favorite text editor. 

``` 
 $ (vi) config.ini
```

Then you need to change the HOST and PORT to reflect the address for your deluged client. The username and password needed to connect can be found under:  

(Only tested on ubuntu)
```
 $ cat /home/USER/.config/deluge/auth
```


## <a name="install"></a> Install Required Dependencies
Now that we have our virutalenv set up and activated we want to install all the necessary packages listed in `requirements.txt`. To install it's dependencies do the following:

```
 $ pip install -r requirements.txt
```

Now we have our neccessary packages installed!


## <a name="usage"></a> Usage

```
Custom delugeRPC client
Usage:
   deluge_cli add MAGNET [DIR] [--debug | --warning | --error]
   deluge_cli get TORRENT
   deluge_cli ls [--downloading | --seeding | --paused]
   deluge_cli toggle TORRENT
   deluge_cli rm TORRENT [--debug | --warning | --error]
   deluge_cli (-h | --help)
   deluge_cli --version

Arguments:
   MAGNET        Magnet link to add
   DIR           Directory to save to
   TORRENT       A selected torrent

Options:
   -h --help     Show this screen
   --version     Show version
   --debug       Print all debug log
   --warning     Print only logged warnings
   --error       Print error messages (Error/Warning)
```

### <a name="running"></a> Running
To interface with deluged :

```
 $ ./deluge_cli.py ls
```


## <a name="contributing"></a> Contributing
- Fork it!
- Create your feature branch: git checkout -b my-new-feature
- Commit your changes: git commit -am 'Add some feature'
- Push to the branch: git push origin my-new-feature
- Submit a pull request
