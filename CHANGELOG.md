All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [unreleased]
### Added
* Add `utils.Key` (returned by redesigned `utils.getch`)
* Add support for `Chat` links.
* Add support for `Kalvidres` links.

### Changed
* Use links of the [virtual campus](https://campusvirtual.uva.es/my) instead of [google drive](https://drive.google.com/drive).
* Renamed `IconType.unkown` to `IconType.unknown` (**typo**).
* Redesigned `utils.getch`. Now returns `utils.Key`.

### Removed
* Removed `IconType.not_id`.


## [3.0.2] - 2020-03-13
### Added
* Improved detection for excel files.

### Changed
* If an exception is catched in a thread, it will be logged and printed (if the `quiet` flag is not set, of course), but not re-raised.

### Fixed
* Fixed `time_operations` if the input is `inf` or `-inf`.
* Fixed parsing emtpy web pages (called `weird pages`, they have a tag called `applet`).


## [3.0.1] - 2020-02-17
### Fixed
* Updated `CHANGELOG`.


## [3.0.0] - 2020-02-15
### Added
* Add `--check-updates` option to CLI, to check for new updates of the VCM.
* Add `names` attribute to links database.
* Add `general.max-logs` setting.
* Add `exclude` subcommand of `settings` command. It excludes subjects from being processed using its ID.
* Add `include` subcommand of `settings` command. It includes subjects which were previously excluded by the `excude` subcommand using its ID.
* Add `discover` command to CLI to only discover subjects, so then the user can rename them.

### Changed
* Improve alias database (`alias.json`). Now it only has two attributes for each entry: id and alias. No ID


## [2.1.1] - 2020-02-02
### Added
* Detect if final servers are under maintenance


## [2.1.0] - 2019-11-22
### Changed
* If email not sent successfully, database will remain untouched.


## [2.0.1] - 2019-11-27
### Fixed
* Fix notifier error.


[unreleased]: https://github.com/sralloza/vcm/compare/v3.0.2...HEAD
[3.0.2]: https://github.com/sralloza/vcm/compare/v3.0.1...v3.0.2
[3.0.1]: https://github.com/sralloza/vcm/compare/v3.0.0...v3.0.1
[3.0.0]: https://github.com/sralloza/vcm/compare/v2.1.1...v3.0.0
[2.1.1]: https://github.com/sralloza/vcm/compare/v2.1.0...v2.1.1
[2.1.0]: https://github.com/sralloza/vcm/compare/v2.0.1...v2.1.0
[2.0.1]: https://github.com/sralloza/vcm/compare/v2.0.0...v2.0.1
