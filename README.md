![Logo](autobfx_logo.png)

# autobfx

[![Tests](https://github.com/Ulthran/autobfx/actions/workflows/routine_tests.yaml/badge.svg)](https://github.com/Ulthran/autobfx/actions/workflows/routine_tests.yaml)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/5c72b0d1e63e4efd8e6fcca22708b506)](https://app.codacy.com/gh/Ulthran/autobfx/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade)
[![codecov](https://codecov.io/gh/Ulthran/autobfx/graph/badge.svg?token=P8XruywW8Q)](https://codecov.io/gh/Ulthran/autobfx)

## NOTES IN DEV



## Getting started

### Installation

Dev install from GitHub: `git clone https://github.com/Ulthran/autobfx/`
`cd autobfx/`
`venv env/`
`source env/bin/activate`
Install (optionally in editable mode): `pip install -e .`
`bash cmd/start` (This is liable to be moved into the library)
Initialize a project: `autobfx init projects/example/` (Doesn't work yet, still consider how this should be done)
Fun dummy run to see that it's working: `autobfx run projects/example/ logo:logo_flow`