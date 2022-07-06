package(default_visibility = ["PUBLIC"])

python_library(
    name = "build_files",
    srcs = glob(
        ["*.py"],
        exclude = ["_test.py"],
    ),
    deps = [
        "//common/logger",
        "//domain/plz/rule",
        "//domain/targets",
        "//service/ast/converters",
    ],
)

python_test(
    name = "build_files_test",
    srcs = glob(["*_test.py"]),
    deps = [
        ":build_files",
        "//domain/plz/rule",
    ],
)
