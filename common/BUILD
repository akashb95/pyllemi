package(default_visibility = ["PUBLIC"])

python_library(
    name = "common",
    srcs = glob(
        ["*.py"],
        exclude = ["*_test.py"],
    ),
    deps = ["//common/logger"],
)

python_test(
    name = "common_test",
    srcs = glob(["*_test.py"]),
    deps = [":common"],
)
