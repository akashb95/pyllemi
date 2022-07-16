package(default_visibility=["PUBLIC"])

python_library(
    name = "trie",
    srcs = glob(
        ["*.py"],
        exclude = ["*_test.py"],
    ),
    deps = [],
)

python_test(
    name = "trie_test",
    srcs = glob(["*_test.py"]),
    deps = [":trie"],
)
