# Changelog

## 3.6 - 2026-07-16

### Added

* Complete CDS validation for input and target sequences
* Three-frame complete ORF detection
* ORF frame and coordinate information in CSV output
* Distinct completion, cancellation, and no-result statuses

### Changed

* Restricted ORF detection and target scoring to mutated replicates
* Reused parent scoring results for unchanged replicates
* Replaced per-replicate scoring tasks with batch processing
* Replaced full sorting with heap-based Top-N selection
* Improved GUI reset behavior after simulation completion

### Fixed

* Incorrect successful-completion message after manual cancellation
* GUI state not being restored after completion
* Previous log and cancellation state persisting into subsequent runs

