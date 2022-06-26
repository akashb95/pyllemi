package(default_visibility=["PUBLIC"])

python_library(
    name = "known",
    srcs = [
        "__init__.py",
        "known.py",
    ],
    deps = [
        "//common/logger",
        "//domain/targets",
        "//third_party/python3:jsonschema",
    ],
)

python_test(
    name = "known_test",
    srcs = ["known_test.py"],
    deps = [
        ":known",
        "//domain/targets",
        "//third_party/python3:jsonschema",
    ],
)
