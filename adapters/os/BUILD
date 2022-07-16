package(default_visibility = ["PUBLIC"])

python_library(
    name = "os",
    srcs = glob(
        ["*.py"],
        exclude = ["*_test.py"],
    ),
    deps = [
        "//common/logger",
        "//domain/plz/rule",
    ],
)

python_test(
    name = "os_test",
    srcs = glob(["*_test.py"]),
    deps = [
        ":os",
        "//domain/plz/rule",
        "//utils",
    ],
)
