package(default_visibility = ["PUBLIC"])

python_library(
    name = "converters",
    srcs = glob(["*.py"], exclude=["_test.py"]),
    deps = [
        "//utils",
    ],
)

python_test(
    name = "converters_test",
    srcs = glob(["*_test.py"]),
    deps = [
        ":converters",
    ],
)
