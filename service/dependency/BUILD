package(default_visibility=["PUBLIC"])

python_library(
    name = "dependency",
    srcs = glob(
        ["*.py"],
        exclude = ["*_test.py"],
    ),
    deps = [
        "//adapters",
        "//common/logger",
        "//converters",
        "//domain/imports",
        "//domain/plz/target",
    ],
)

python_test(
    name = "dependency_test",
    srcs = glob(["*_test.py"]),
    deps = [
        ":dependency",
        "//adapters",
        "//domain/imports",
        "//domain/plz/target",
    ],
)
