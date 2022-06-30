python_library(
    name = "converters",
    srcs = glob(
        ["*.py"],
        exclude = ["*_test.py"],
    ),
    deps = [
        "//adapters/plz_cli",
        "//domain/imports",
        "//domain/plz/rule",
        "//domain/plz/target",
    ],
    visibility=["PUBLIC"],
)

python_test(
    name = "converters_test",
    srcs = glob(["*_test.py"]),
    deps = [
        ":converters",
        "//domain/imports",
        "//domain/plz/rule",
        "//utils",
    ],
)
