python_library(
    name = "pyllemi_lib",
    srcs = glob(
        ["*.py"],
        exclude = ["*_test.py", "*main.py"],
    ),
    deps = [
        "//adapters",
        "//common/logger",
        "//domain/build_pkgs",
        "//domain/imports",
        "//domain/targets",
        "//domain/targets/plz",
    ],
)

python_binary(
    name = "pyllemi",
    main = "main.py",
    deps = [":pyllemi_lib"],
)
