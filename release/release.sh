set -euxo pipefail

version="$1"

#
# Make sure the version is correctly set and documented
#
grep --silent "## $version," CHANGELOG.md
grep --silent "version='$version'" setup.py
grep --silent "__version__ = '$version'" bounter/__init__.py

pandoc --from=markdown --to=rst --output=README.rst README.md

set +e
git commit README.rst -m "updated README.rst from README.md"
set -e

#
# Tagging will fail if the tag already exists.
#
git tag "$version"
git push origin master --tags
python setup.py sdist upload
