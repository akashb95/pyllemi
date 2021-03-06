import functools
import gc
import os
import subprocess
from unittest import TestCase, mock

from adapters.plz_cli.query import (
    get_all_targets,
    get_build_file_names,
    get_config,
    get_third_party_module_targets,
    get_plz_build_graph,
    get_print,
    get_reporoot,
    get_whatinputs,
    run_plz_fmt,
    WhatInputsResult,
)


class TestGetConfig(TestCase):
    @mock.patch("adapters.plz_cli.query.subprocess.Popen")
    def test_gets_config(self, mock_subprocess_popen):
        process_mock = mock.Mock()
        stdout_mock_return_value = [b"some value"]
        process_mock.configure_mock(**{"stdout": stdout_mock_return_value, "returncode": 0})
        mock_subprocess_popen.return_value = process_mock

        self.assertEqual(
            ["some value"],
            get_config("some specifier"),
        )

        return


class TestGetThirdPartyModules(TestCase):
    @mock.patch("adapters.plz_cli.query.get_all_targets")
    @mock.patch("adapters.plz_cli.query.get_config")
    def test_gets_third_party_modules(
        self,
        mock_get_config,
        mock_get_all_targets,
    ):
        mock_get_config.return_value = ["third_party.python"]
        mock_get_all_targets.return_value = ["//third_party/python:a", "//third_party/python:b"]
        third_party_modules = get_third_party_module_targets()
        mock_get_config.assert_called_once_with("python.moduledir")
        mock_get_all_targets.assert_called_once_with([os.path.join("third_party", "python", "...")])
        self.assertEqual(
            ["//third_party/python:a", "//third_party/python:b"],
            third_party_modules,
        )
        return

    @mock.patch("adapters.plz_cli.query.get_config")
    def test_errors_when_get_config_returns_no_values(self, mock_get_config):
        mock_get_config.return_value = []
        with self.assertRaises(AssertionError):
            get_third_party_module_targets()
        return

    @mock.patch("adapters.plz_cli.query.get_config")
    def test_errors_when_get_config_returns_unexpected_response(
        self,
        mock_get_config,
    ):
        mock_get_config.return_value = []
        with self.assertRaises(AssertionError):
            get_third_party_module_targets()
        return


class TestGetProjectRoot(TestCase):
    @mock.patch("adapters.plz_cli.query.subprocess.Popen")
    def test_gets_reporoot(self, mock_subprocess_popen):
        process_mock = mock.Mock()
        stdout_mock_return_value = [b"/path/to/reporoot"]
        process_mock.configure_mock(**{"stdout": stdout_mock_return_value, "returncode": 0})
        mock_subprocess_popen.return_value = process_mock

        expected_reporoot = "/path/to/reporoot"

        reporoot = get_reporoot()
        self.assertEqual(
            expected_reporoot,
            reporoot,
        )
        return


class TestGetWhatInputs(TestCase):
    @mock.patch("adapters.plz_cli.query.subprocess.Popen")
    def test_gets_target_when_all_inputs_exist(self, mock_subprocess_popen):
        process_mock = mock.Mock()
        stdout_mock_return_value = [
            b"//path/to/pkg:target",
            b"//path/to/other_pkg:target",
        ]
        process_mock.configure_mock(**{"stdout": stdout_mock_return_value, "returncode": 0})
        mock_subprocess_popen.return_value = process_mock

        expected_output = WhatInputsResult(
            plz_targets={"//path/to/pkg:target", "//path/to/other_pkg:target"},
            targetless_paths=set(),
        )

        self.assertEqual(
            expected_output,
            # The inputs here don't matter since the results from plz are mocked anyway.
            get_whatinputs(["path/to/pkg/module.py", "path/to/other_pkg/module.py"]),
        )
        return

    @mock.patch("adapters.plz_cli.query.subprocess.Popen")
    def test_outputs_targetless_input_paths(self, mock_subprocess_popen):
        process_mock = mock.Mock()
        stdout_mock_return_value = [
            b"Error: 'path/to/pkg/module.py' is not a source to any current target",
            b"Error: 'path/to/other_pkg/module.py' is not a source to any current target",
        ]
        process_mock.configure_mock(**{"stdout": stdout_mock_return_value, "returncode": 0})
        mock_subprocess_popen.return_value = process_mock

        expected_output = WhatInputsResult(
            plz_targets=set(),
            targetless_paths={"path/to/pkg/module.py", "path/to/other_pkg/module.py"},
        )
        self.assertEqual(
            expected_output,
            # The inputs here don't matter since the results from plz are mocked anyway.
            get_whatinputs(["path/to/pkg/module.py", "path/to/other_pkg/module.py"]),
        )
        return

    @mock.patch("adapters.plz_cli.query.subprocess.Popen")
    def test_outputs_mixed_targets_and_targetless_paths(self, mock_subprocess_popen):
        process_mock = mock.Mock()
        stdout_mock_return_value = [
            b"//path/to/pkg:target",
            b"Error: 'path/to/other_pkg/module.py' is not a source to any current target",
        ]
        process_mock.configure_mock(**{"stdout": stdout_mock_return_value, "returncode": 0})
        mock_subprocess_popen.return_value = process_mock

        expected_output = WhatInputsResult(
            plz_targets={"//path/to/pkg:target"},
            targetless_paths={"path/to/other_pkg/module.py"},
        )
        self.assertEqual(
            expected_output,
            # The inputs here don't matter since the results from plz are mocked anyway.
            get_whatinputs(["path/to/pkg/module.py", "path/to/other_pkg/module.py"]),
        )
        return


class TestGetAllTargets(TestCase):
    @mock.patch("adapters.plz_cli.query.subprocess.Popen")
    def test_gets_all_targets(self, mock_subprocess_popen):
        process_mock = mock.Mock()
        stdout_mock_return_value = [
            b"//pkg/dir:target_1",
            b"//pkg/dir:target_2 ",
            b"//pkg/dir_2",
        ]
        process_mock.configure_mock(**{"stdout": stdout_mock_return_value, "returncode": 0})
        mock_subprocess_popen.return_value = process_mock

        self.assertEqual(
            ["//pkg/dir:target_1", "//pkg/dir:target_2", "//pkg/dir_2"],
            get_all_targets(["//pkg/dir", "//pkg/dir_2"]),
        )
        return


class TestGetPlzBuildGraph(TestCase):
    @mock.patch("adapters.plz_cli.query.subprocess.Popen")
    def test_get_plz_build_graph(self, mock_subprocess_popen):
        process_mock = mock.Mock()
        stdout_mock_return_value = [
            b"{",
            b'    "packages": {',
            b'        "third_party/python": {',
            b'             "targets": {',
            b'                 "_hidden": {}, "not_hidden": {}',
            b"             }",
            b"         }",
            b"     }",
            b"}",
        ]
        process_mock.configure_mock(**{"stdout": stdout_mock_return_value, "returncode": 0})
        mock_subprocess_popen.return_value = process_mock

        out = get_plz_build_graph()

        self.assertEqual(
            {
                "packages": {
                    "third_party/python": {
                        "targets": {
                            "_hidden": {},
                            "not_hidden": {},
                        },
                    },
                },
            },
            out,
        )
        return

    @mock.patch("adapters.plz_cli.query.subprocess.Popen")
    def test_when_returncode_is_non_zero(self, mock_subprocess_popen):
        process_mock = mock.Mock()
        process_mock.configure_mock(**{"stderr": "mock err", "returncode": 1})
        mock_subprocess_popen.return_value = process_mock

        self.assertRaises(
            RuntimeError,
            get_plz_build_graph,
            # This is to stop the cache from returning the result from a previous call.
            "//pkg/dir/y",
        )
        return


class TestGetBuildFileNames(TestCase):
    def setUp(self) -> None:
        # Clear all cache so that @lru_cache calls do not interfere with mocks.
        gc.collect()
        wrappers = [a for a in gc.get_objects() if isinstance(a, functools._lru_cache_wrapper)]

        for wrapper in wrappers:
            wrapper.cache_clear()

        return

    @mock.patch("adapters.plz_cli.query.get_config")
    def test_empty_stdout(self, mock_get_config: mock.MagicMock):
        mock_get_config.return_value = []
        self.assertRaisesRegex(
            AssertionError,
            "expected to find at least 1 build file name",
            get_build_file_names,
        )
        mock_get_config.assert_called_once_with("parse.buildfilename")
        return

    @mock.patch("adapters.plz_cli.query.get_config")
    def test_get_build_file_names(self, mock_get_config):
        mock_get_config.return_value = ["BUILD.plz", "BUILD"]
        self.assertCountEqual(["BUILD.plz", "BUILD"], get_build_file_names())
        mock_get_config.assert_called_once_with("parse.buildfilename")
        return


class TestPrint(TestCase):
    @mock.patch("adapters.plz_cli.query.subprocess.Popen")
    def test_print(self, mock_subprocess_popen):
        process_mock = mock.Mock()
        stdout_mock_return_value = [b"__init__.py", b"module.py"]
        process_mock.configure_mock(**{"stdout": stdout_mock_return_value, "returncode": None})
        mock_subprocess_popen.return_value = process_mock

        self.assertEqual(["__init__.py", "module.py"], get_print("//path/to:target", "srcs"))
        mock_subprocess_popen.assert_called_once_with(
            ["plz", "query", "print", "//path/to:target", "-f", "srcs"],
            stdout=subprocess.PIPE,
        )
        return


class TestFmt(TestCase):
    @mock.patch("adapters.plz_cli.query.subprocess.Popen")
    def test_fmt(self, mock_subprocess_popen):
        process_mock = mock.Mock()
        process_mock.configure_mock(**{"returncode": 0})
        mock_subprocess_popen.return_value = process_mock

        run_plz_fmt(os.path.join("some", "random", "build_pkg"), os.path.join("some", "other", "build_pkg"))
        mock_subprocess_popen.assert_called_once_with(
            f"plz fmt -w {os.path.join('some', 'random', 'build_pkg')} {os.path.join('some', 'other', 'build_pkg')}",
            stdout=subprocess.PIPE,
            shell=True,
        )

        return

    def test_raises_err_with_no_args(self):
        self.assertRaisesRegex(
            ValueError,
            ".*expected at least 1 path.*",
            run_plz_fmt,
        )
        return
