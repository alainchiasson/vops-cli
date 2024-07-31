# vopscli

[![PyPI](https://img.shields.io/pypi/v/vopscli.svg)](https://pypi.org/project/vopscli/)
[![Changelog](https://img.shields.io/github/v/release/alainchiasson/vopscli?include_prereleases&label=changelog)](https://github.com/alainchiasson/vopscli/releases)
[![Tests](https://github.com/alainchiasson/vopscli/actions/workflows/test.yml/badge.svg)](https://github.com/alainchiasson/vopscli/actions/workflows/test.yml)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/alainchiasson/vopscli/blob/master/LICENSE)

Vault Operations CLI

## Installation

Install this tool using `pip`:
```bash
pip install vopscli
```
## Usage

For help, run:
```bash
vopscli --help
```
You can also use:
```bash
python -m vopscli --help
```
## Development

To contribute to this tool, first checkout the code. Then create a new virtual environment:
```bash
cd vopscli
python -m venv venv
source venv/bin/activate
```
Now install the dependencies and test dependencies:
```bash
pip install -e '.[test]'
```
To run the tests:
```bash
pytest
```
