package(default_visibility = ["PUBLIC"])

python_library(
    name = "dependency",
    srcs = glob(
        ["*.py"],
        exclude = ["*_test.py"],
    ),
    deps = [
        "//adapters/plz_cli",
        "//common/logger",
        "//common/trie",
        "//domain/plz/target",
        "//domain/python_import",
        "//service/ast/converters",
        "//service/python_import:imports",
    ],
)

python_test(
    name = "dependency_test",
    srcs = glob(["*_test.py"]),
    deps = [
        ":dependency",
        "//adapters/plz_cli",
        "//domain/plz/target",
        "//domain/python_import",
    ],
)
