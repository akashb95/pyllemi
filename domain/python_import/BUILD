package(default_visibility = ["//service/...", "//domain/..."])

python_library(
    name = "python_import",
    srcs = glob(
        ["*.py"],
        exclude = ["*_test.py"],
    ),
    deps = [
        "//common/logger",
    ],
)
