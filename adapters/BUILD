package(default_visibility = ["PUBLIC"])

python_library(
    name = "adapters",
    srcs = glob(
        ["*.py"],
        exclude = ["*_test.py"],
    ),
    deps = ["//common/logger"],
)

python_test(
    name = "adapters_test",
    srcs = glob(["*_test.py"]),
    deps = ["//adapters"],
)
