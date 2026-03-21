from typing import Dict, Any, List
from gtm_client import GTMClient

class ExportService:
    def __init__(self, client: GTMClient):
        self.client = client

    def export_workspace(self, workspace_path: str) -> Dict[str, List[Dict[str, Any]]]:
        tags = self.client.list_tags(workspace_path)
        triggers = self.client.list_triggers(workspace_path)
        variables = self.client.list_variables(workspace_path)
        built_in_variables = self.client.list_built_in_variables(workspace_path)
        return {
            "tags": tags,
            "triggers": triggers,
            "variables": variables,
            "built_in_variables": built_in_variables,
        }
