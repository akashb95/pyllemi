python_library(
    name = "converters",
    srcs = glob(
        ["*.py"],
        exclude = ["*_test.py"],
    ),
    visibility = ["PUBLIC"],
    deps = [
        "//adapters/plz_cli",
        "//domain/plz/rule",
        "//domain/plz/target",
        "//domain/python_import",
        "//service/python_import:imports",
    ],
)

python_test(
    name = "converters_test",
    srcs = glob(["*_test.py"]),
    deps = [
        ":converters",
        "//domain/plz/rule",
        "//domain/python_import",
        "//utils",
    ],
)
