package(default_visibility=["PUBLIC"])

python_library(
    name = "known",
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
    name = "known_test",
    srcs = glob(["*_test.py"]),
    deps = [
        ":known",
        "//domain/targets",
        "//third_party/python3:jsonschema",
    ],
)
