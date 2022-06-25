package(default_visibility = ["PUBLIC"])

python_library(
    name = "imports",
    srcs = glob(
        ["*.py"],
        exclude = ["*_test.py"],
    ),
    deps = ["//common/logger"],
)

python_test(
    name = "imports_test",
    srcs = glob(["*_test.py"]),
    deps = [
        "//domain/imports",
        "//utils",
    ],
)
