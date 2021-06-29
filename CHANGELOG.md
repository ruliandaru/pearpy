# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog][Keep a Changelog] and this project adheres to [Semantic Versioning][Semantic Versioning].

## [Unreleased]


---

## [Released]

## [0.0.2-alpha] 2021-02-01
### Added
- added find_main_stem from whitebox
- added vector output
- added another typing
- added maximum length percentage for finding starting point
- use entire main stem before starting point to calculate volume estimation
### Changed
- major change in finding starting point. Now, only use main stem
- layout change in starting point and main
- use dataclass for model to simplify it
- changed gui to be more aligned

### Fixed
- fixed progress bar in finding sp. it showed generating surface hydro instead finding sp


## [0.0.1-alpha1] - 2021-01-01
### Added
- added create surface hydro using whitebox
- added stop when flow direction is 0 at lahar inundation
- add tempoorary directory for non preserving surface hydro data
- delete duplicate if there are another point nearby (distance  should be user-defined later)

### Changed
- changed layout to accomodate simpler workflow
- changed how to find surface hydro file
- return the lowest starting point

### Removed
- remove unused input bar in main page

### Fixed
- fixed progress callback to return i+1
- fixed starting point not returning any point when differences of x is negative and y is positive by adding abs()


---

<!-- Links -->
[Keep a Changelog]: https://keepachangelog.com/
[Semantic Versioning]: https://semver.org/

<!-- Versions -->
[Unreleased]: https://github.com/Author/Repository/compare/v1.0.0...HEAD
[Released]: https://github.com/Author/Repository/releases
[0.0.1]: https://github.com/Author/Repository/releases/v0.0.1