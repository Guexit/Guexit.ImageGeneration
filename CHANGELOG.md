# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.6.2] - 2023-12-25

### Added

- Adds tags to service bus message

## [0.6.1] - 2023-12-25

### Added

- GitHub action to make a release, with a changelog and a tag.

## [0.6.0] - 2023-12-24

### Added

- `cloud_manager` module while removing the existing repository.

## [0.5.0] - 2023-12-07

### Added

- [stabilityai/sdxl-turbo](https://huggingface.co/stabilityai/sdxl-turbo) model which is x10 faster than [segmind/SSD-1B](https://huggingface.co/segmind/SSD-1B).

### Changed

- Pytorch version from `==2.0.0` to `>=2.1.1`.

## [0.4.0] - 2023-12-05

### Added

- Probability to variables in styles.

## [0.3.0] - 2023-11-11

### Added

- `test_prompt_randomness` feature for improved prompt generation.
- Plot variable distributions utils for quickly displaying prompt variable value distribution across generated prompts.

### Changed

- Public domain characters now used for famous characters variables.
- Cleaned up codebase, removing duplicates and unused styles.

### Fixed

- Updated Docker GitHub action and codecov settings.

## [0.2.0] - 2023-10-24

### Added

- Safety checker with retry mechanism for NSFW content detection.
- Tests for the new safety checker.

### Fixed

- Fixed seed on general style.

## [0.1.3] - 2023-10-23

### Added

- Around x1.5 speedup on inference.
- Famous characters and new elements to styles.

### Changed

- Switched to Python 3.10.
