# Pyllemi

[![CI](https://github.com/akashb95/pyllemi/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/akashb95/pyllemi/actions/workflows/ci.yml)

Pyllemi is a CLI tool to automatically update and create Please BUILD dependencies for Python targets. More
specifically, it can:

* Create `python_library` and `python_test` targets for new BUILD Package Directories.
* Update dependencies for `python_library`, `python_binary` and `python_test` targets.

Pyllemi does not generate third party `pip_library` or `python_wheel` rules.

## Config

Configuration for Pyllemi is passed in via a `.pyllemi.json` file at the reporoot.

### `knownDependencies`

Array of objects. Allows setting a Plz target dependency for a Python module.

```json
{
  "knownDependencies": [
    {
      "module": "path.to.module",
      "plzTarget": "//path/to/dependency:target"
    }
  ]
}
```

### `useGlobAsSrcs`

Boolean. Setting this to True uses `glob` call to set the pattern for `srcs` for `python_library` and `python_test`
targets when generate a BUILD file in BUILD packages (without a pre-existing BUILD files).

```json
{
  "useGlobAsSrcs": true
}
```

The above setting will generate new BUILD files like so:

```python
python_library(
    name="target",
    srcs=glob(["*.py"], exclude=["*_test.py"]),
    deps=[...],
)

python_library(
    name="target",
    srcs=glob(["*_test.py"]),
    deps=[...],
)
```

Note that the `glob`s in the example are the exact values that will appear in any generated BUILD files, and cannot be
configured.

## Running Pyllemi with Please

WIP

```python
# tools/BUILD

PYLLEMI_VERSION = "v0.8.1"
remote_file(
    name="pyllemi",
    url=f"https://github.com/akashb95/pyllemi/releases/download/{PYLLEMI_VERSION}/pyllemi.pex",
    extract=False,
    binary=True,
)
```