# What's New

## Unreleased
* Add `--check-updates` option to CLI, to check for new updates of the VCM.
* Add `names` attribute to links database.
* Add `general.max-logs` setting.
* Add `exclude` subcommand of `settings` command. It excludes subjects from being processed using its ID.
* Add `include` subcommand of `settings` command. It includes subjects which were previously excluded by the `excude` subcommand using its ID.
* Add `discover` command to CLI to only discover subjects, so then the user can rename them.
* Improve alias database (`alias.json`). Now it only has two attributes for each entry: id and alias. No ID

## 2.1.1
* Detect if final servers are under maintenance

## 2.1.0
* If email not sent successfully, database will remain untouched.

## 2.0.1
* Fix notifier error.
