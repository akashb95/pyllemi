import os
from unittest import TestCase, mock

from adapters.plz_query_graph import get_third_party_modules, get_plz_build_graph


class TestGetThirdPartyLibs(TestCase):
    @mock.patch("adapters.plz_query_graph.get_plz_build_graph")
    def test_get_third_party_libs(self, mock_get_plz_build_graph):
        mock_get_plz_build_graph.return_value = {
            "packages": {
                "third_party/python": {
                    "targets": {
                        "_hidden": {},
                        "not_hidden": {},
                    },
                },
            },
        }
        third_parties = get_third_party_modules(os.path.join("third_party", "python"))
        self.assertEqual(1, len(third_parties))
        self.assertIn("not_hidden", third_parties)
        self.assertNotIn("_hidden", third_parties)
        return

    @mock.patch("adapters.plz_query_graph.subprocess.Popen")
    def test_propagates_get_plz_build_graph_errors(self, mock_subprocess_popen):
        # Make subprocess cmd return err in get_plz_build_graph().
        # This is expected to be raised again so that get_third_party_libs() catches it,
        # where it is once again reraised.
        process_mock = mock.Mock()
        process_mock.configure_mock(**{"stderr": "mock err", "returncode": 1})
        mock_subprocess_popen.return_value = process_mock
        self.assertRaises(
            RuntimeError,
            get_third_party_modules,
            os.path.join("third_party", "does-not-exist"),
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
