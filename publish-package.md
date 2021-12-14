# Publishing package on PyPI

These are the steps for publishing the package on the [Python Package Index](https://pypi.org/).

More detailed information can be found here: [Packaging Documentation](https://packaging.python.org/en/latest/tutorials/packaging-projects/#creating-the-package-files)

## 1. Tagging the version
This package uses `setuptools_scm` for version tagging from git tags.

To create a new version, first a git tag has to be created either on the commandline:
```
git tag -a v0.1 -m "arxiv-scan v0.1"
git push --tags
```
Or by creating a release in the Github interface.
The Github release can also be created from the git tag.

## 2. Build the package
With this the package can be build using the `build`-package:
```
pip install --upgrade build
python -m build .
```

## 3. Upload package to PyPI
The package can now be uploaded to PyPI with `twine`:
```
pip install --upgrade twine
```
The login information (or tokens) can either be stored in a `.pypirc`-file, or this information will be prompted.
[More info on the `.pypirc`-file.](https://packaging.python.org/en/latest/specifications/pypirc/)

To upload the package:
```
python -m twine upload dist/*
```
Make sure to only upload the intended versions, so maybe customize the globbing (e.g. `python -m twine upload dist/arxiv-scan-0.1*`).
