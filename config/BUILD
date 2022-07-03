package(default_visibility = ["PUBLIC"])

python_library(
    name = "config",
    srcs = glob(
        ["*.py"],
        exclude = ["*_test.py"],
    ),
    deps = [
        "//common/logger",
        "//domain/plz/target",
        "//third_party/python3:jsonschema",
    ],
)

python_test(
    name = "config_test",
    srcs = glob(["*_test.py"]),
    deps = [
        ":config",
        "//domain/plz/target",
        "//third_party/python3:jsonschema",
    ],
)
