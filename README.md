![Logo](autobfx_logo.png)

# autobfx

[![Tests](https://github.com/Ulthran/autobfx/actions/workflows/test.yaml/badge.svg)](https://github.com/Ulthran/autobfx/actions/workflows/test.yaml)
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

Fun dummy run to see that it's working: `autobfx run tests/data/example_project/ logo:logo_flow`

### Hidden directories

There is a `.autobfx/` directory created in the root of the library that holds information on running services such as the Prefect server and workers. In each project directory there are also `.autobfx/` directories that store marker files with information on that project's task run states.