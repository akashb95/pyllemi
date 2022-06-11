package(default_visibility = ["PUBLIC"])

python_library(
    name = "os",
    srcs = glob(
        ["*.py"],
        exclude = ["_test.py"],
    ),
    deps = [
        "//common/logger",
        "//domain/targets",
    ],
)

python_test(
    name = "os_test",
    srcs = glob(["*_test.py"]),
    deps = [":os", "//utils"],
)
