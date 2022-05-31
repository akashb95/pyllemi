package(default_visibility = ["PUBLIC"])

python_library(
    name = "targets",
    srcs = glob(
        ["*.py"],
        exclude = ["_test.py"],
    ),
    deps = [
        "//adapters",
        "//common/logger",
        "//converters",
    ],
)

# python_test(
#     name = "targets_test",
#     srcs = glob(["*_test.py"]),
#     deps = [
#         ":imports",
#         "//utils",
#     ],
# )
