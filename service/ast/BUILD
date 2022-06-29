package(default_visibility=["PUBLIC"])

python_library(
    name = "ast",
    srcs = glob(
        ["*.py"],
        exclude = ["*_test.py"],
    ),
    deps = [
        "//adapters",
        "//domain/plz/rule",
        "//domain/plz/target",
        "//domain/targets",
    ],
)

python_test(
    name = "ast_test",
    srcs = glob(["*_test.py"]),
    deps = [
        ":ast",
        "//domain/plz/rule",
    ],
)
