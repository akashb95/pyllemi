package(default_visibility=["//domain/...", "//service/...", "//adapters/..."])

python_library(
    name = "rule",
    srcs = glob(
        ["*.py"],
        exclude = ["*_test.py"],
    ),
    deps = [],
)

python_test(
    name = "rule_test",
    srcs = glob(["*_test.py"]),
    deps = [":rule"],
)
