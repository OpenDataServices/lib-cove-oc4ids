import copy

LIB_COVE_OC4IDS_CONFIG_DEFAULT = {
    "schema_name": "project-package-schema.json",
    "schema_item_name": "project-schema.json",
    "schema_version": "0.9.5",
    "schema_version_choices": {
        "0.9.5": ("0.9.5", "http://standard.open-contracting.org/infrastructure/schema/0__9__5/"),
    },
    "schema_host": "http://standard.open-contracting.org/infrastructure/schema/0__9__5/",
    "schema_codelists": {
        # version: codelist_dir,
        "0.9": "https://raw.githubusercontent.com/open-contracting/infrastructure/0.9/schema/project-level/codelists/",
    },
    #
    # lib-cove options
    #
    "cache_all_requests": False,
    #
    # Flatten Tool options
    #
    "root_list_path": "projects",
    "root_id": "id",
    "convert_titles": False,
    "flatten_tool": {
        "disable_local_refs": True,
        "remove_empty_schema_columns": True,
    },
}


class LibCoveOC4IDSConfig:
    def __init__(self, config=None):
        self.config = copy.deepcopy(LIB_COVE_OC4IDS_CONFIG_DEFAULT)
        if config:
            self.config.update(config)
