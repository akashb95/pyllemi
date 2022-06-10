import logging
from typing import Iterable

from adapters.plz_query import get_whatinputs
from common.logger.logger import setup_logger
from domain.imports.common import IMPORT_NODE_TYPE
from domain.imports.enriched_import import to_whatinputs_input, EnrichedImport
from domain.imports.enricher import ToEnrichedImports


class Resolver:
    python_moduledir: str
    std_lib_modules: set[str]
    third_party_module_targets: set[str]

    def __init__(
            self,
            reporoot: str,
            python_moduledir: str,
            std_lib_modules: set[str],
            third_party_module_targets: set[str],
    ):
        self._logger = setup_logger(__name__, logging.INFO)

        self.reporoot = reporoot
        self.python_moduledir = python_moduledir
        self.std_lib_modules = std_lib_modules
        self.third_party_module_targets = third_party_module_targets

        self.third_party_module_imports: set[str] = set()
        self.custom_module_targets: set[str] = set()
        self.custom_module_sources_without_targets: set[str] = set()
        return

    def resolve(self, import_nodes: Iterable[IMPORT_NODE_TYPE]):
        to_enriched_imports = ToEnrichedImports(self.reporoot, self.python_moduledir)
        for import_node in import_nodes:
            for enriched_imports in to_enriched_imports.convert(import_node):
                for enriched_import in enriched_imports:
                    self._resolve_single_enriched_import(enriched_import)

                    # TODO: find usages of subpackages and find innermost plz targets of package imports.
        return

    def _resolve_single_enriched_import(self, enriched_import: EnrichedImport):
        # Filter out stdlib modules.
        top_level_module_name = get_top_level_module_name(enriched_import.import_)
        if top_level_module_name in self.std_lib_modules:
            self._logger.info(f"Found import of a standard lib module: {top_level_module_name}")
            return

        # Resolve 3rd-party library targets.
        possible_third_party_module_target = (
            f"//{self.python_moduledir}:{top_level_module_name}".replace(".", "/")
        )
        if possible_third_party_module_target in self.third_party_module_targets:
            self.third_party_module_imports.add(possible_third_party_module_target)
            return

        self._logger.debug(f"Found import of a custom lib module: {enriched_import.import_}")

        if (whatinputs_input := to_whatinputs_input(enriched_import)) is not None:
            whatinputs_result = get_whatinputs(whatinputs_input)
            self.custom_module_targets |= whatinputs_result.plz_targets
            self.custom_module_sources_without_targets |= whatinputs_result.targetless_paths

        return


def get_top_level_module_name(abs_import_path: str) -> str:
    return abs_import_path.split(".", maxsplit=1)[0] if "." in abs_import_path else abs_import_path
