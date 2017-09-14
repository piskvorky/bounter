#!/bin/bash
pandoc --from=markdown --to=rst --output=README README.md
python setup.py sdist upload
