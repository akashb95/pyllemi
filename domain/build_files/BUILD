package(default_visibility = ["PUBLIC"])

python_library(
    name = "build_files",
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
    name = "build_files_test",
    srcs = glob(["*_test.py"]),
    deps = [
        ":build_files",
    ],
)
