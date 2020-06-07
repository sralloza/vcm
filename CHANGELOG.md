All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [3.3.1] - 2020.06.07
### Fixed
* Infinite loop while logging in inserted in release [3.3.0].


## [3.3.0] - 2020.06.07
### Added
* `login-retries` and `logout-retries` can be changed in settings. Their default values are `5`.


## [3.2.3] - 2020.05.30
### Added
* New way of showing version: `vcm version` (`vcm --version` still works).

### Fixed
* Thread stops if receives `SystemExit` ([#91](https://github.com/sralloza/vcm/issues/91))
* In case of error during login, `pickle` data will only be stored if the login response exists.
* In case of error during logout, `pickle` data will only be stored if the logout error was not generated because of a `server error` (HTTP 500) ([#90](https://github.com/sralloza/vcm/issues/90))
* During login, 400 responses are considereded as failed.


## [3.2.2] - 2020.05.27
### Added
* Added retry control to `logout`.
* Added summary of errors at the end of the log.
* Added system to save context in case of fatal error.
* Insert retry control for every http method.

### Changed
* Changed status http server port from `80` to `8080`.
* In case of error dump login or logout response as `pickle`.
* `Login attempts` reduced to 5.

### Fixed
* `@timing` always logs time delta, whether an exception is raised or not.
* Detect initial failure of moodle.
* Improve detection of `4xx` and `5xx` errors from the server.
* Support handing of `503` errors from the server.
* `utils.Printer` is now thread safe.


## [3.2.1] - 2020-05-21
### Added
* Log message when starting execution.

### Changed
* Print timestamp instead of counter for new and updated files.


## [3.2.0] - 2020-05-13
### Added
* Add support for `Blackboard` links.

### Changed
* Improved memory management.


## [3.1.3] - 2020-04-08
### Fixed
* Use `content-type` to define extension if all other methods fail.


## [3.1.2] - 2020-03-31
### Fixed
* Fixed typo in `README`.
* Fixed filtering of links (accept only if they have a valid link).


## [3.1.1] - 2020-03-26
### Added
* Add support for `Quiz` links.
* Created new class to download images: `Image`.
* Created new class to parse html files: `HTML`.

### Changed
* Implement new algorithm to identify images.
* It can implements multiple algorithms, named `check_algorith_xxxx(name)`.
* Include links in the database even if they are external to the `UVA`.


## [3.1.0] - 2020-03-23
### Added
* Add `utils.Key` (returned by redesigned `utils.getch`).
* Add support for `Chat` links.
* Add support for `Page` links.
* Add support for `Url` links.
* Add support for `Kalvidres` links.

### Changed
* Renamed `IconType.unkown` to `IconType.unknown` (**typo**).
* Redesigned `utils.getch`. Now returns `utils.Key`.

### Removed
* Removed `IconType.not_id`.
* Removed setting `NotifySettings.use_base64_icons`.

### Fixed
* Fix display of icons in gmail.


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
* Add `--check-updates` option to CLI, to check for new updates of the `VCM`.
* Add `names` attribute to links database.
* Add `general.max-logs` setting.
* Add `exclude` subcommand of `settings` command. It excludes subjects from being processed using its `ID`.
* Add `include` subcommand of `settings` command. It includes subjects which were previously excluded by the `excude` subcommand using its `ID`.
* Add `discover` command to CLI to only discover subjects, so then the user can rename them.

### Changed
* Improve alias database (`alias.json`). Now it only has two attributes for each entry: `id` and `alias`. No `ID`


## [2.1.1] - 2020-02-02
### Added
* Detect if final servers are under maintenance


## [2.1.0] - 2019-11-22
### Changed
* If email not sent successfully, database will remain untouched.


## [2.0.1] - 2019-11-27
### Fixed
* Fix notifier error.


[unreleased]: https://github.com/sralloza/vcm/compare/v3.3.1...HEAD
[3.3.1]: https://github.com/sralloza/vcm/compare/v3.3.0...v3.3.1
[3.3.0]: https://github.com/sralloza/vcm/compare/v3.2.3...v3.3.0
[3.2.3]: https://github.com/sralloza/vcm/compare/v3.2.2...v3.2.3
[3.2.2]: https://github.com/sralloza/vcm/compare/v3.2.1...v3.2.2
[3.2.1]: https://github.com/sralloza/vcm/compare/v3.2.0...v3.2.1
[3.2.0]: https://github.com/sralloza/vcm/compare/v3.1.3...v3.2.0
[3.1.3]: https://github.com/sralloza/vcm/compare/v3.1.2...v3.1.3
[3.1.2]: https://github.com/sralloza/vcm/compare/v3.1.1...v3.1.2
[3.1.1]: https://github.com/sralloza/vcm/compare/v3.1.0...v3.1.1
[3.1.0]: https://github.com/sralloza/vcm/compare/v3.0.2...v3.1.0
[3.0.2]: https://github.com/sralloza/vcm/compare/v3.0.1...v3.0.2
[3.0.1]: https://github.com/sralloza/vcm/compare/v3.0.0...v3.0.1
[3.0.0]: https://github.com/sralloza/vcm/compare/v2.1.1...v3.0.0
[2.1.1]: https://github.com/sralloza/vcm/compare/v2.1.0...v2.1.1
[2.1.0]: https://github.com/sralloza/vcm/compare/v2.0.1...v2.1.0
[2.0.1]: https://github.com/sralloza/vcm/compare/v2.0.0...v2.0.1
