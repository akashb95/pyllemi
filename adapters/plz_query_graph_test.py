import os
from unittest import TestCase, mock

from adapters.plz_query_graph import (
    get_all_targets,
    get_config,
    get_third_party_modules,
    get_plz_build_graph,
    get_reporoot,
    get_whatinputs,
    WhatInputsResult,
)


class TestGetConfig(TestCase):
    @mock.patch("adapters.plz_query_graph.subprocess.Popen")
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
    @mock.patch("adapters.plz_query_graph.get_all_targets")
    @mock.patch("adapters.plz_query_graph.get_config")
    def test_gets_third_party_modules(
        self,
        mock_get_config,
        mock_get_all_targets,
    ):
        mock_get_config.return_value = ["third_party.python"]
        mock_get_all_targets.return_value = ["//third_party/python:a", "//third_party/python:b"]
        third_party_modules = get_third_party_modules()
        mock_get_config.assert_called_once_with("python.moduledir")
        mock_get_all_targets.assert_called_once_with([os.path.join("third_party", "python", "...")])
        self.assertEqual(
            ["//third_party/python:a", "//third_party/python:b"],
            third_party_modules,
        )
        return

    @mock.patch("adapters.plz_query_graph.get_config")
    def test_errors_when_get_config_returns_no_values(self, mock_get_config):
        mock_get_config.return_value = []
        with self.assertRaises(AssertionError):
            get_third_party_modules()
        return

    @mock.patch("adapters.plz_query_graph.get_config")
    def test_errors_when_get_config_returns_unexpected_response(
        self,
        mock_get_config,
    ):
        mock_get_config.return_value = []
        with self.assertRaises(AssertionError):
            get_third_party_modules()
        return


class TestGetProjectRoot(TestCase):
    @mock.patch("adapters.plz_query_graph.subprocess.Popen")
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
    @mock.patch("adapters.plz_query_graph.subprocess.Popen")
    def test_gets_target_when_all_inputs_exist(self, mock_subprocess_popen):
        process_mock = mock.Mock()
        stdout_mock_return_value = [
            b"//path/to/pkg:target",
            b"//path/to/other_pkg:target",
        ]
        process_mock.configure_mock(**{"stdout": stdout_mock_return_value, "returncode": 0})
        mock_subprocess_popen.return_value = process_mock

        expected_output = WhatInputsResult(
            plz_targets=["//path/to/pkg:target", "//path/to/other_pkg:target"],
            targetless_paths=[],
        )

        self.assertEqual(
            expected_output,
            # The inputs here don't matter since the results from plz are mocked anyway.
            get_whatinputs(["path/to/pkg/module.py", "path/to/other_pkg/module.py"]),
        )
        return

    @mock.patch("adapters.plz_query_graph.subprocess.Popen")
    def test_outputs_targetless_input_paths(self, mock_subprocess_popen):
        process_mock = mock.Mock()
        stdout_mock_return_value = [
            b"Error: 'path/to/pkg/module.py' is not a source to any current target",
            b"Error: 'path/to/other_pkg/module.py' is not a source to any current target",
        ]
        process_mock.configure_mock(**{"stdout": stdout_mock_return_value, "returncode": 0})
        mock_subprocess_popen.return_value = process_mock

        expected_output = WhatInputsResult(
            plz_targets=[],
            targetless_paths=["path/to/pkg/module.py", "path/to/other_pkg/module.py"],
        )
        self.assertEqual(
            expected_output,
            # The inputs here don't matter since the results from plz are mocked anyway.
            get_whatinputs(["path/to/pkg/module.py", "path/to/other_pkg/module.py"]),
        )
        return

    @mock.patch("adapters.plz_query_graph.subprocess.Popen")
    def test_outputs_mixed_targets_and_targetless_paths(self, mock_subprocess_popen):
        process_mock = mock.Mock()
        stdout_mock_return_value = [
            b"//path/to/pkg:target",
            b"Error: 'path/to/other_pkg/module.py' is not a source to any current target",
        ]
        process_mock.configure_mock(**{"stdout": stdout_mock_return_value, "returncode": 0})
        mock_subprocess_popen.return_value = process_mock

        expected_output = WhatInputsResult(
            plz_targets=["//path/to/pkg:target"],
            targetless_paths=["path/to/other_pkg/module.py"],
        )
        self.assertEqual(
            expected_output,
            # The inputs here don't matter since the results from plz are mocked anyway.
            get_whatinputs(["path/to/pkg/module.py", "path/to/other_pkg/module.py"]),
        )
        return


class TestGetAllTargets(TestCase):
    @mock.patch("adapters.plz_query_graph.subprocess.Popen")
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
    @mock.patch("adapters.plz_query_graph.subprocess.Popen")
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

    @mock.patch("adapters.plz_query_graph.subprocess.Popen")
    def test_when_returncode_is_non_zero(self, mock_subprocess_popen):
        process_mock = mock.Mock()
        process_mock.configure_mock(**{"stderr": "mock err", "returncode": 1})
        mock_subprocess_popen.return_value = process_mock

        self.assertRaises(
            RuntimeError,
            get_plz_build_graph,
        )
        return
