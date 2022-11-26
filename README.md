<h1 align="center">
  🐍 Python Deluge CLI
</h1>

<h4 align="center"> A easy to use Deluge CLI that can connect to Deluge RPC (even over ssh) written entirely in python.</h4>

| Tested version | PyPi package | License |
|:--------|:------|:------|
| [![PyVersion](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/downloads/release/python-3100/) | [![PyPI](https://img.shields.io/pypi/v/delugeClient_kevin)](https://pypi.org/project/delugeClient_kevin/) |[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

| Drone CI | Known vulnerabilities |
|:--------|:------|
| [![Build Status](https://drone.schleppe.cloud/api/badges/KevinMidboe/delugeClient/status.svg)](https://drone.schleppe.cloud/KevinMidboe/delugeClient) | [![Known Vulnerabilities](https://snyk.io/test/github/kevinmidboe/delugeClient/badge.svg?targetFile=requirements.txt)](https://snyk.io/test/github/kevinmidboe/delugeClient?targetFile=requirements.txt)

<p align="center">
  <a href="#abstract">Abstract</a> •
  <a href="#install">Install</a> •
  <a href="#usage">Usage</a> •
  <a href="#setup_virtualenv">Setup Virtual Environment</a> •
  <a href="#configure">Configure</a> •
  <a href="#contributing">Contributing</a>
</p>


## <a name="abstract"></a> Abstract
Create a deluge python client for interfacing with deluge for common tasks like listing, adding, removing and setting download directory for torrents. 

## <a name="install"></a> Install
Install from source:
```bash
python3 setup.py install
```

Install from pip:
```bash
pip3 install delugeClient-kevin
```

## <a name="usage"></a> Usage
View delugeClient cli options with `delugeClient --help`:

```
 Usage: python -m delugeclient [OPTIONS] COMMAND [ARGS]...

╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --debug                       Set log level to debug                                                            │
│ --info                        Set log level to info                                                             │
│ --warning                     Set log level to warning                                                          │
│ --error                       Set log level to error                                                            │
│ --install-completion          Install completion for the current shell.                                         │
│ --show-completion             Show completion for the current shell, to copy it or customize the installation.  │
│ --help                        Show this message and exit.                                                       │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ──────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ add                Add magnet torrent                                                                           │
│ disk               Get free disk space                                                                          │
│ get                Get torrent by id or hash                                                                    │
│ ls                 List all torrents                                                                            │
│ remove             Remove torrent by id or hash                                                                 │
│ rm                 Remove torrent by name                                                                       │
│ search             Search for string segment in torrent name                                                    │
│ toggle             Toggle torrent download state                                                                │
│ version            Print package version                                                                        │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

## <a name="setup_virtualenv"></a> Setup Virtual Environment
Virtual environment allows us to create a local environment for the requirements needed. Because pip does not download packages already downloaded to your system, we can use virtualenv to save our packages in the project folder.


### <a name="installation"></a> Installation
To install virtualenv, simply run:  

```
 $ pip install virutalenv
```


### Virtualenv setup
After you have downloaded this project go to it in your terminal by going to the folder you downloaded and typing the following:


```
 $ cd delugeClient/
```

The to setup a virtual environment enter this:

```
 $ virtualenv -p python3.10 env
```

 > If you get an error now it might be because you don't have python3.10, please make sure you have python version 3.10 if else you can download it from [here](https://www.python.org/downloads/)


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

## <a name="contributing"></a> Contributing
- Fork it!
- Create your feature branch: git checkout -b my-new-feature
- Commit your changes: git commit -am 'Add some feature'
- Push to the branch: git push origin my-new-feature
- Submit a pull request
