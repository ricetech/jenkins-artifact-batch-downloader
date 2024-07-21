# Jenkins Artifact Batch Downloader

As a person who manages a couple of Minecraft servers, this script is mostly meant
to solve my own annoyance of having to individually download and copy each of the different
[EssentialsX](https://essentialsx.net/) 
Minecraft Server plugins into each of my server folders.

The main Python script loads the list of artifacts from whatever URL you provide in the `.env`
file. The script was written to deal with Jenkins, but can be modified to suit whatever CI
system you're dealing with.

To make file replacement easier, the script strips version information from the filename.

## Setup

Using a [venv](https://docs.python.org/3/library/venv.html) is recommended.

This project was developed using Python 3.12.

In the root folder of this project, run:

```shell
pip install -r requirements.txt
```

Copy the `.env.example` file to `.env` and set the values within based on your own needs.

## Usage

```shell
python main.py
```
