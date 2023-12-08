# Changelog

## [0.5.0] - 07/12/2023

- [Added] [stabilityai/sdxl-turbo](https://huggingface.co/stabilityai/sdxl-turbo) model which is x10 faster than [segmind/SSD-1B](https://huggingface.co/segmind/SSD-1B)
- [Changed] Pytorch version from `==2.0.0` to `>=2.1.1`

## [0.4.0] - 05/12/2023

- Adds probability to variables in styles

## [0.3.0] - 11/11/2023

### Added

- `test_prompt_randomness` feature for improved prompt generation.
- Plot variable distributions utils for quickly displaying prompt variable value distribution across generated prompts.

### Changed

- Public domain characters now used for famous characters variables.
- Cleaned up codebase, removing duplicates and unused styles.

### Fixed

- Updated Docker GitHub action and codecov settings.

## [0.2.0] - 24/10/2023

### Added

- Introduced safety checker with retry mechanism for NSFW content detection.
- Added tests for the new safety checker.

### Fixed

- Fixed seed on general style.

## [0.1.3] - 23/10/2023

### Added

- Around x1.5 speedup on inference.
- Famous characters and new elements to styles.

### Changed

- Switched to Python 3.10.
