python_library(
    name = "pyllemi_lib",
    srcs = glob(
        ["*.py"],
        exclude = ["_test.py"],
    ),
    deps = [
        "//adapters",
        "//common/logger",
        "//imports",
    ],
)

python_binary(
    name = "pyllemi",
    main = "main.py",
    deps = [":pyllemi_lib"],
)
