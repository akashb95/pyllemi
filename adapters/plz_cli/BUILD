package(default_visibility=["PUBLIC"])

python_library(
    name = "plz_cli",
    srcs = glob(
        ["*.py"],
        exclude = ["*_test.py"],
    ),
    deps = ["//common/logger"],
)

python_test(
    name = "plz_cli_test",
    srcs = glob(["*_test.py"]),
    deps = [":plz_cli"],
)
