import os

# Import from existing code
import sys
from typing import Any, Dict, List

from gtm_client import GTMClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src', 'scripts', 'bin')))

# We need clean_item from import.py - import it carefully
import importlib

_import_module = importlib.import_module("import")
clean_item = _import_module.clean_item
GTMDependencyResolver = _import_module.GTMDependencyResolver


class ImportService:
    def __init__(self, client: GTMClient):
        self.client = client

    def preview(self, workspace_path: str, data: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """Compare local data with remote and return diffs without making changes."""
        remote = {
            "variables": {v['name']: v for v in self.client.list_variables(workspace_path)},
            "triggers": {t['name']: t for t in self.client.list_triggers(workspace_path)},
            "tags": {t['name']: t for t in self.client.list_tags(workspace_path)},
            "built_in_variables": {v['type']: v for v in self.client.list_built_in_variables(workspace_path)},
        }

        diffs = []
        summary = {"create": 0, "update": 0, "skip": 0}

        # Built-in variables
        for bv in data.get("built_in_variables", []):
            bv_type = bv.get("type")
            if bv_type in remote["built_in_variables"]:
                diffs.append({"name": bv_type, "type": "built_in_variables", "action": "skip", "remote": remote["built_in_variables"][bv_type], "local": bv})
                summary["skip"] += 1
            else:
                diffs.append({"name": bv_type, "type": "built_in_variables", "action": "create", "local": bv})
                summary["create"] += 1

        # Variables, Triggers, Tags
        for ctype in ["variables", "triggers", "tags"]:
            for item in data.get(ctype, []):
                name = item.get("name", "")
                remote_item = remote[ctype].get(name)
                if remote_item:
                    if clean_item(item) == clean_item(remote_item):
                        diffs.append({"name": name, "type": ctype, "action": "skip", "remote": remote_item, "local": item})
                        summary["skip"] += 1
                    else:
                        diffs.append({"name": name, "type": ctype, "action": "update", "remote": remote_item, "local": item})
                        summary["update"] += 1
                else:
                    diffs.append({"name": name, "type": ctype, "action": "create", "local": item})
                    summary["create"] += 1

        return {"diffs": diffs, "summary": summary}

    def execute(self, workspace_path: str, data: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """Execute the import using GTMDependencyResolver with in-memory data."""
        resolver = GTMDependencyResolver(
            client=self.client,
            workspace_path=workspace_path,
            data=data,
        )

        results = []
        summary = {"created": 0, "updated": 0, "skipped": 0, "error": 0}

        # Built-in variables
        built_in_vars = data.get("built_in_variables", [])
        if built_in_vars:
            existing_built_ins = resolver.remote_registry["built_in_variables"]
            types_to_enable = [v['type'] for v in built_in_vars if v.get('type') not in existing_built_ins]
            if types_to_enable:
                try:
                    self.client.create_built_in_variables(workspace_path, types_to_enable)
                    for t in types_to_enable:
                        results.append({"type": "built_in_variables", "name": t, "action": "created"})
                        summary["created"] += 1
                except Exception as e:
                    for t in types_to_enable:
                        results.append({"type": "built_in_variables", "name": t, "action": "error", "error": str(e)})
                        summary["error"] += 1

        # Variables -> Triggers -> Tags
        for ctype in ["variables", "triggers", "tags"]:
            local_map = resolver.local_repo[ctype]
            if not local_map:
                continue

            for name, item in local_map.items():
                remote_item = resolver.remote_registry[ctype].get(name)
                processed = resolver._process_dependencies(ctype, item)

                if remote_item:
                    if clean_item(processed) == clean_item(remote_item):
                        results.append({"type": ctype, "name": name, "action": "skipped"})
                        summary["skipped"] += 1
                        continue

                    try:
                        method_name = f"update_{ctype[:-1]}"
                        getattr(self.client, method_name)(remote_item['path'], clean_item(processed))
                        results.append({"type": ctype, "name": name, "action": "updated"})
                        summary["updated"] += 1
                    except Exception as e:
                        results.append({"type": ctype, "name": name, "action": "error", "error": str(e)})
                        summary["error"] += 1
                else:
                    try:
                        resolver.ensure_component(ctype, name)
                        results.append({"type": ctype, "name": name, "action": "created"})
                        summary["created"] += 1
                    except Exception as e:
                        results.append({"type": ctype, "name": name, "action": "error", "error": str(e)})
                        summary["error"] += 1

        return {"results": results, "summary": summary}
