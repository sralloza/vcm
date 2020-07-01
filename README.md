<h2 align="center">Virtual Campus Manager</h2>

<p align="center">
<a href="https://github.com/sralloza/vcm/actions"><img alt="build" src="https://github.com/sralloza/vcm/workflows/Python application/badge.svg"></a>
<a href="https://codecov.io/gh/sralloza/vcm/branch/test-coverage"><img alt="coverage" src="https://codecov.io/github/sralloza/vcm/coverage.svg"></a>
<a href="https://github.com/sralloza/vcm/blob/master/LICENSE"><img alt="License: MIT" src="https://img.shields.io/badge/License-MIT-yellow.svg"></a>
</p>

## How to install

There are 2 diferent ways: normal instalation and virtualenv instalation.

- Developers who prefer to use a single interpreter should get the normal instalation.
- Developers who doesn't want to have dependency problems and like to manage projects in sepparate virtual environment should get the virtualenv instalation.

_Note: both installations need to have Python 3.6+ installed._

### Virtualenv install

1. Create a folder whenever you want.
2. Inside that folder we will create the virtual environment. To do so, open the terminal and type `virtualenv venv`.
3. Activate the environment using `call venv/scripts/activate.bat`.
4. Install the program with `python -m pip install git+https://github.com/sralloza/vcm.git`
5. Inside that folder, create another folder and add it to the `PATH`. If you don't know how to add folders to the `PATH`, visit [this site](https://docs.alfresco.com/4.2/tasks/fot-addpath.html).
6. Finally, create a file named `vcm.cmd` in that

```
@echo off
"drive:/path/to/your/folder/venv/scripts/python.exe" %*
```

7. Done. To use the program, type `vcm -h`

### General install

1. Run `python -m pip install git+https://github.com/sralloza/vcm.git`
2. Done. To use the program, just type `vcm -h`

# How to use

When executing the program for the first time, the settings and credential files will be automatically created. You can find them in `C:\Users\<username>\vcm-settings.toml` and `C:\Users\<username>\vcm-credentials.toml` (you may need to execute the program twice).

If you are using Linux, the settings and credential files will be created in and `/home/<username>/vcm-credentials.toml`.

## Settings File

The settings file path is `C:\Users\<username>\vcm-settings.toml` (or `/home/<username>/vcm-settings.toml` in Linux). It's written in [TOML](https://github.com/toml-lang/toml#toml). Changing a setting can be done editing the settings file (discouraged, because a syntax error will make the hole program to fail) or using the [`settings` command](#settings-command).

It has 3 sections: general, download and notify.

### General section

Settings:

- **root-folder** - Path to the folder where the files will be downloaded. It will be used to store other files, as logs, notify database, filecache json and others. Must be set, it lacks of a default value.
- **logging-level** - Logging level. Can be `DEBUG`, `INFO`, `WARNING`, `ERROR` or `CRITICAL`. Defaults to `INFO`.
- **timeout** - Number of seconds without response before abandoning download attempt. Defaults to 30.
- **retries** - Number of attempts to download a web page before raising an error. Defaults to 10.
- **max-logs** - Max number of log files. Defaults to 5.
- **exclude-subjects-ids** - List of subject ids to exclude while downloading. It's designed to allow the user to avoid downloading files from first quarter's subjects while cursing second quarter. You can change its content using the commands `vcm settings exclude <subject_id>` and `vcm settings include <subject_id>`, because it can't be changed using `vcm settings set general.exclude-subjects-ids <value>`.

### Download section

Settings:

- **forum-subfolders** - If true, all the files found inside a forum discussion will be stored in a separate folder. Defaults to true.
- **section-indexing** - List of subject's ids that will have section indexing enabled. You can change its content using the commands `vcm settings index <subject_id>` and `vcm settings unindex <subject_id>`, because it can't be changed using `vcm settings set download.section-indexing <value>`. For more info read [What is a section](#what-is-a-section).
- **secure-section-filename** - If true, sections folder's name will have its white spaces replaced with low bars.

### Notify section

Settings:

- **email** - Recipient of the notify email. Must be set, it lacks of a default value.

### Settings file example

**_vcm-settings.toml_**

```toml
[general]
root-folder = "/home/user/virtual-campus-data"
logging-level = "INFO"
timeout = 30
retries = 10
max-logs = 7
exclude-urls = [ 89712, ]

[download]
forum-subfolders = true
section-indexing = [16942, 82645, 45651, ]
secure-section-filename = false

[notify]
email = "email@example.com"

```

## Credentials file

The credentials file path is `C:\Users\<username>\vcm-credentials.toml` (or `/home/<username>/vcm-credentials.toml` if you are using Linux). It's written in [TOML](https://github.com/toml-lang/toml#toml).
**Note that the credentials will be stored in plain text.**

It has 2 sections: VirtualCampus and Email.
All settings must be set, there are no default values.

### VirtualCampus section

Settings:

- **username** - Username of the virtual campus.
- **password** - Password of the virtual campus.

### Email section

- **username** - email address to send the report from.
- **password** - password of the email.
- **smtp_server** - stmp server name. For Gmail is `smtp.gmail.com`.
- **smtp_port** - stmp port. For Gmail is `587`

## Command Line Interface arguments

There are 4 commands: `download`, `notify`, `settings` and `discover`.

General arguments:

- `-v`, `--version` - Prints the current version and exits.
- `-nss`, `--no-status-server` - Disables the status server. See [During the Execution](#during-the-execution) for more info.
- `--check-updates` - Check for updates

**Note**: place the general arguments before the command.
Example: `vcm --no-status-server download --nthreads 23 --no-killer`

To see more info use `vcm -h` or `vcm --help`

### Download command

It downloads all the virtual campus files in the root folder.

Arguments:

- `--nthreads NTHREADS` - Select the number of threads to use. Default value is 20.
- `--no-killer` - Disables the Killer thread
- `-d`, `--debug` - Opens Google Chrome in localhost after start. See [During the Execution](#during-the-execution) for more info.
- `-q`, `--quiet` - Disables stdout, so nothing gets printed.

To view the command help, use `vcm download -h` or `vcm download --help`.

### Notify command

It search all files in the virtual campus but it doesn't download them. Instead, it sends an email if there are new files, with a link to each new file. This is done using a local sqlite database stored in the root folder.

Arguments:

- `--nthreads NTHREADS` - Select the number of threads to use. Default value is 20.
- `--no-icons` - Disable the icons in the email.

Note: this command will not start the killer thread, because it's design to avoid using stdin and stdout, so it can be used with [tasks managers](#cron-integration-task-scheduler) like cron.

To view the command help, use `vcm notify -h` or `vcm notify --help`.

### Settings command

It can show or change settings.

Uses:

- **List all settings:** `vcm settings list`.
- **List one specific setting:** `vcm settings show <setting>`
- **List key settings (not values):** `vcm settings keys`
- **Set settings value:** `vcm settings set section.key value`.
  - _Section_ is the settings section, can be one of `general`, `download` or `notify`.
  - _Key_ is the settings key you want to change. It depends on the section.
  - _Value_ is the settings value you want to set.
  - To view the comand help, use `vcm settings set -h` or `vcm settings set --help`.
- **Excluding and including subjects in parsing:**
  - _Exclude a subject in parsing:_ `vcm settings exclude <subject_id>`
  - _Include a subject in parsing:_ `vcm settings include <subject_id>` (to include a subject it must be previously excluded)
- **Index and unindex subjects using section names:**
  - _Index subject using its sections:_ `vcm settings index <subject_id>`
  - _Unindex subject using its sections:_ `vcm settings unindex <subject_id>` (to unindex a subject it must be previously indexed)
- **Check integrity of the settings file:** `vcm settings check`

### Discover command

It will only discover subjects, and insert their alias in the alias database (`alias.json`), so the user can change the subject's alias to easily rename all the files in the subject's folder.

## During the execution

During the execution you can open a web browser in localhost to access to real time information of the threading status. It is shown what is the state of each thread and what it's downloading each thread.

To view the status of a thread, a color code is used:

- Blue: thread is idle (ready to work).
- Green: thread downloading for less than 30 seconds.
- Orange: thread downloading between 30 seconds and 1 minute.
- Red: thread downloading between 1 minute and 1 and a half minutes.
- Magenta: thread downloading for more than 1 and a half minutes. The total time is shown in this case.
- Black: thread was killed (not working anymore, the program is closing).

## Cron integration (Task Scheduler)

VCM is designed to work with a task scheduler. Commands are:

- Download: `virtualenv/path/bin/python -m vcm -nss download -q`
- Notify: `virtualenv/path/bin/python -m vcm -nss notify`

# How are notes stored (downloaded)

Inside the root folder, a folder will be created for each subject.
A section is how notes are classified in the virtual campus.
For each subject, if its url is not in the `disable-section-indexing` list, a folder will be created for each section. The files will be downloaded inside the section's folder, which is inside the subject's folder.

The setting `general.secure-section-filename` will replace white spaces with low bars.

To sum up:
**`/root-folder-path/subject-name/section-name/filename.extension`**

## What is a section

![example](https://raw.githubusercontent.com/sralloza/vcm/master/.github/example.png)
A section is how notes are classified in the virtual campus. In this example, you can see the title **`Tema 1`**, and then 3 resources (2 pdfs and 1 zip file). The title **`Tema 1`** is the section.
