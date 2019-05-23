# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
- Add django-waffle and configure Django & React apps to enable feature flags [#531](https://github.com/open-apparel-registry/open-apparel-registry/pull/531)

### Changed

### Deprecated

### Removed

### Fixed
- Fixed script name in release issue template [#529](https://github.com/open-apparel-registry/open-apparel-registry/pull/529)

### Security
- Bumped Django REST framework to version not impacted by [WS-2019-0037](https://github.com/encode/django-rest-framework/commit/75a489150ae24c2f3c794104a8e98fa43e2c9ce9) [#536](https://github.com/open-apparel-registry/open-apparel-registry/pull/536)

## [2.4.0] - 2019-05-20
### Added
- Add django-simple-history and create audit model for facilities [#521](https://github.com/open-apparel-registry/open-apparel-registry/pull/521)
- Facility list items can be filtered by status [#507](https://github.com/open-apparel-registry/open-apparel-registry/pull/507)
- Facility lists pages displays a count of item statuses [#511](https://github.com/open-apparel-registry/open-apparel-registry/pull/511)
- Retry failed batch jobs up to 3 times and report job failures to Rollbar [#512](https://github.com/open-apparel-registry/open-apparel-registry/pull/512/)

### Changed
- Set maximum page size for Facilities list API endpoint to 500 facilities per request. [#509](https://github.com/open-apparel-registry/open-apparel-registry/pull/509)
- Upgraded React to 16.8.6 [#511](https://github.com/open-apparel-registry/open-apparel-registry/pull/511)
- Changed the name of country code MK to North Macedonia [#525](https://github.com/open-apparel-registry/open-apparel-registry/pull/525)

### Fixed
- Made some fields read only in the Django admin to prevent slow page loads resulting in service interruptions. [#527](https://github.com/open-apparel-registry/open-apparel-registry/pull/527)

## [2.3.0] - 2019-05-08
### Changed
- Change facility list CSV download to request one page at a time [#496](https://github.com/open-apparel-registry/open-apparel-registry/pull/496)
- Handle CSV files that include a byte order mark [#498](https://github.com/open-apparel-registry/open-apparel-registry/pull/498)

## [2.2.0] - 2019-04-11
### Added
- Password can be changed from the profile page [#469](https://github.com/open-apparel-registry/open-apparel-registry/pull/469)

### Changed
- Update release checklist to keep default commit messages [#451](https://github.com/open-apparel-registry/open-apparel-registry/pull/451)
- Add support for encrypted RDS for PostgreSQL storage [#461](https://github.com/open-apparel-registry/open-apparel-registry/pull/461)
- Update the text on the home page "Guide" tab [#468](https://github.com/open-apparel-registry/open-apparel-registry/pull/468)

### Fixed
- Add a new error boundary to enable the FacilitiesMap component to crash without crashing the rest of the app [#446](https://github.com/open-apparel-registry/open-apparel-registry/pull/446)
- Revise geocoding unit test to be more robust [#466](https://github.com/open-apparel-registry/open-apparel-registry/pull/466)
- Remove duplicate values from the contributors API [#453](https://github.com/open-apparel-registry/open-apparel-registry/pull/453)

## [2.1.0] - 2019-04-01
### Added
- Add `reprocess_geocode_failures` management command [#439](https://github.com/open-apparel-registry/open-apparel-registry/pull/439)

### Changed
- Add protocol to contributor website if mising [#445](https://github.com/open-apparel-registry/open-apparel-registry/pull/445)
- Rename "Account Name" and "Account Description" registration form fields to "Contributor Name" and "Account Description" [#444](https://github.com/open-apparel-registry/open-apparel-registry/pull/444)
- Filter contributors with no active and public lists from contributors search dropdown [#430](https://github.com/open-apparel-registry/open-apparel-registry/pull/430)
- Remove `"(beta)"` from page title [#418](https://github.com/open-apparel-registry/open-apparel-registry/pull/418)

### Fixed
- Set ERROR_MATCHING status to non-geocoded list items for which all potential matches have been rejected [#437](https://github.com/open-apparel-registry/open-apparel-registry/pull/437)
- Return 400/Bad Request error for /api/facilities request with invalid contributor parameter type. [#433](https://github.com/open-apparel-registry/open-apparel-registry/pull/433)
- Avoid unhandled exception when matching a list with no geocoded items [#439](https://github.com/open-apparel-registry/open-apparel-registry/pull/439)

## [2.0.0] - 2019-03-27
### Added
- Google Analytics which activates only upon user's explicit consent [#409](https://github.com/open-apparel-registry/open-apparel-registry/pull/409)

## [0.2.0] - 2019-03-27
### Added
- Summary status for facility lists [#378](https://github.com/open-apparel-registry/open-apparel-registry/pull/378)
- Environment variables for Google Analytics [#395](https://github.com/open-apparel-registry/open-apparel-registry/pull/395)

### Changed
- Do not show facilities from inactive lists when searching [#401](https://github.com/open-apparel-registry/open-apparel-registry/pull/401)
- Redirect to facility list upon successful upload [#404](https://github.com/open-apparel-registry/open-apparel-registry/pull/404)
- Better support for wide and narrow browser widths [#392](https://github.com/open-apparel-registry/open-apparel-registry/pull/392)

### Fixed
- Handle geocodes with unescaped `#` character [#402](https://github.com/open-apparel-registry/open-apparel-registry/pull/402)

## [0.1.0] - 2019-03-26
### Added
- Initial release.

[Unreleased]: https://github.com/open-apparel-registry/open-apparel-registry/compare/v2.4.0...HEAD
[2.4.0]: https://github.com/open-apparel-registry/open-apparel-registry/releases/tag/2.4.0
[2.3.0]: https://github.com/open-apparel-registry/open-apparel-registry/releases/tag/2.3.0
[2.2.0]: https://github.com/open-apparel-registry/open-apparel-registry/releases/tag/2.2.0
[2.1.0]: https://github.com/open-apparel-registry/open-apparel-registry/releases/tag/2.1.0
[2.0.0]: https://github.com/open-apparel-registry/open-apparel-registry/releases/tag/2.0.0
[0.2.0]: https://github.com/open-apparel-registry/open-apparel-registry/releases/tag/0.2.0
[0.1.0]: https://github.com/open-apparel-registry/open-apparel-registry/releases/tag/0.1.0
