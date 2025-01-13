#!/bin/zsh

# Use this script to test the local builds

set -e

# build system

pip3 install -U pip setuptools wheel build twine nuitka

# build python package version

(rm -rf dist/* || :)
python3 -m build --wheel &&
twine check dist/*.whl

# build executable version

(brew install ccache || :)
(rm -rf mverb3.app || :)
python3 -m nuitka --standalone --enable-plugin=pyside6 --macos-create-app-bundle --macos-app-icon=resources/icon.icns mverb3
