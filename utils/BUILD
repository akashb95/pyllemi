package(default_visibility = ["PUBLIC"])

python_library(
    name = "utils",
    srcs = glob(
        ["*.py"],
        exclude = ["*_test.py"],
    ),
)

python_test(
    name = "utils_test",
    srcs = glob(["*_test.py"]),
    deps = [":utils"],
)
