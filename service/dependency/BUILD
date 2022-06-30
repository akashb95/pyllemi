package(default_visibility=["PUBLIC"])

python_library(
    name = "dependency",
    srcs = glob(
        ["*.py"],
        exclude = ["*_test.py"],
    ),
    deps = [
        "//adapters/plz_cli",
        "//common/logger",
        "//domain/imports",
        "//domain/plz/target",
        "//service/ast/converters",
    ],
)

python_test(
    name = "dependency_test",
    srcs = glob(["*_test.py"]),
    deps = [
        ":dependency",
        "//adapters/plz_cli",
        "//domain/imports",
        "//domain/plz/target",
    ],
)
