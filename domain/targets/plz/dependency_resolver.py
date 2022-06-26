import os
from typing import Collection, Optional

from adapters.plz_query import get_whatinputs
from common.logger.logger import setup_logger
from converters.converters import convert_os_path_to_import_path
from domain.imports.enriched_import import to_whatinputs_input, EnrichedImport
from domain.imports.enricher import ToEnrichedImports
from domain.imports.nodes_collator import NodesCollator
from domain.targets.plz_target import PlzTarget


def get_top_level_module_name(abs_import_path: str) -> str:
    return abs_import_path.split(".", maxsplit=1)[0] if "." in abs_import_path else abs_import_path


class DependencyResolver:
    def __init__(
        self,
        *,
        python_moduledir: str,
        enricher: ToEnrichedImports,
        std_lib_modules: Collection[str],
        available_third_party_module_targets: set[str],
        known_dependencies: dict[str, Collection[PlzTarget]],
        nodes_collator: NodesCollator,
    ):
        self._logger = setup_logger(__name__)

        self.python_moduledir = python_moduledir
        self.std_lib_modules = std_lib_modules
        self.available_third_party_module_targets = frozenset(available_third_party_module_targets)
        self.known_dependencies = known_dependencies
        self.enricher = enricher

        self.collator = nodes_collator

        self._whatinputs_inputs_for_this_target: set[str] = set()
        return

    def resolve_deps_for_srcs(self, srcs_plz_target: PlzTarget, srcs: set[str]) -> set[PlzTarget]:
        if len(srcs) == 0:
            return set()

        import_targets: set[PlzTarget] = set()
        for src in srcs:
            self._logger.debug(
                f"Starting to resolve dependencies for {os.path.join(srcs_plz_target.build_pkg_dir, src)}"
            )
            with open(relative_path_to_src := os.path.join(srcs_plz_target.build_pkg_dir, src), "r") as pyfile:
                code = pyfile.read()
            for import_node in self.collator.collate(code=code, path=relative_path_to_src):
                for enriched_imports in self.enricher.convert(import_node):
                    for enriched_import in enriched_imports:
                        deps = self._resolve_dependencies_for_enriched_import(enriched_import)
                        if deps is None:
                            continue
                        import_targets |= deps

            # Inject known dependencies.
            self._logger.warning(convert_os_path_to_import_path(relative_path_to_src))

            if (
                known_deps_for_src := self.known_dependencies.get(convert_os_path_to_import_path(relative_path_to_src))
            ) is not None:
                self._logger.debug(
                    f"Injecting {set(map(str, known_deps_for_src))} as known dependencies for src '{src}'"
                )
                import_targets |= set(known_deps_for_src)

        # Make the call to `plz query whatinputs ...` to find all the custom module dep targets.
        import_targets |= self._query_whatinputs_for_whatinputs_batch()
        self._whatinputs_inputs_for_this_target.clear()

        # Remove "self-dependency" cycles.
        import_targets.discard(srcs_plz_target)
        return import_targets

    def _resolve_dependencies_for_enriched_import(self, enriched_import: EnrichedImport) -> Optional[set[PlzTarget]]:
        # Filter out stdlib modules.
        top_level_module_name = get_top_level_module_name(enriched_import.import_)
        if top_level_module_name in self.std_lib_modules:
            self._logger.debug(f"Found import of a standard lib module: {top_level_module_name}")
            return None

        # Resolve 3rd-party library targets.
        possible_third_party_module_target = f"//{self.python_moduledir}:{top_level_module_name}".replace(".", "/")
        if possible_third_party_module_target in self.available_third_party_module_targets:
            return {PlzTarget(possible_third_party_module_target)}

        self._logger.debug(f"Found import of a custom lib module: {enriched_import.import_}")

        # TODO(#4): add ability to 'guess' target based on import path -- if it is not a target,
        #  then revert to whatinputs.
        if (whatinputs_input := to_whatinputs_input(enriched_import)) is not None:
            # Batch whatinputs calls for performance gains.
            self._whatinputs_inputs_for_this_target |= set(whatinputs_input)

        return None

    def _query_whatinputs_for_whatinputs_batch(self) -> set[PlzTarget]:
        self._logger.debug(f"running whatinputs on {self._whatinputs_inputs_for_this_target}")

        whatinputs_result = get_whatinputs(list(self._whatinputs_inputs_for_this_target))
        if len(whatinputs_result.targetless_paths) > 0:
            self._logger.error(f"Could not find targets for imports: {', '.join(whatinputs_result.targetless_paths)}")
        return set(map(PlzTarget, whatinputs_result.plz_targets))
