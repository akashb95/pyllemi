package(default_visibility = ["PUBLIC"])

python_library(
    name = "build_pkgs",
    srcs = glob(
        ["*.py"],
        exclude = ["_test.py"],
    ),
    deps = [
        "//common/logger",
    ],
)

# python_test(
#     name = "build_pkg_test",
#     srcs = glob(["*_test.py"]),
#     deps = [":build_pkg"],
# )
