package(default_visibility = ["PUBLIC"])

python_library(
    name = "imports",
    srcs = glob(
        ["*.py"],
        exclude = ["*_test.py"],
    ),
    deps = [
        "//common/logger",
        "//domain/python_import",
    ],
)

python_test(
    name = "imports_test",
    srcs = glob(["*_test.py"]),
    deps = [
        ":imports",
        "//domain/python_import",
        "//utils",
    ],
)
