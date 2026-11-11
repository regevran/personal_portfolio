Yet another fast log — a low-footprint binary logging mechanism built around generated message maps and CMake.

The logger writes compact binary records, and an m4 preprocessing step keeps the number-to-text map in sync with the message strings. The repository includes the build system, a demo logger, and the reader/tail/grep tools.
