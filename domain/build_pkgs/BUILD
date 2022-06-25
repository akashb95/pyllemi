package(default_visibility = ["PUBLIC"])

python_library(
    name = "build_pkgs",
    srcs = glob(
        ["*.py"],
        exclude = ["*_test.py"],
    ),
    deps = [
        "//adapters/os",
        "//common/logger",
        "//domain/build_files",
        "//domain/targets",
    ],
)

python_test(
    name = "build_pkgs_test",
    srcs = glob(["*_test.py"]),
    deps = [
        ":build_pkgs",
        "//domain/targets",
        "//utils",
    ],
)
