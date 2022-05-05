python_library(
    name = "snaky_lib",
    srcs = glob(
        ["*.py"],
        exclude = ["_test.py"],
    ),
    deps = [
        "//common/logger",
        "//adapters",
        "//imports",
        "//converters",
    ],
)

python_binary(
    name = "snaky",
    main = "main.py",
    deps = [":snaky_lib"],
)
