python_library(
    name = "snaky_lib",
    srcs = glob(
        ["*.py"],
        exclude = ["_test.py"],
    ),
    deps = [
        "//common/logger",
    ],
)

python_binary(
    name = "snaky",
    main = ":snaky_lib",
        )
