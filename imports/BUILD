python_library(
    name = "imports",
    srcs = glob(["*.py"], exclude=["_test.py"]),
    deps = [
        "//common/logger",
        "//imports/stdlib",
        "//converters",
    ],
)

python_test(
    name = "imports_test",
    srcs = glob(["*_test.py"]),
    deps = [
        ":imports",
        "//utils",
    ],
)