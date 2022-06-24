package(default_visibility = ["PUBLIC"])

python_library(
    name = "plz",
    srcs = glob(
        ["*.py"],
        exclude = ["*_test.py"],
    ),
    deps = [
        "//adapters",
        "//common/logger",
        "//converters",
        "//domain/ast",
    ],
)

python_test(
    name = "plz_test",
    srcs = glob(["*_test.py"]),
    deps = [
        ":plz",
        "//adapters",
        "//domain/targets",
        "//domain/imports",
    ],
)
