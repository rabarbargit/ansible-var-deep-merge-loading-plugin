from ansible.plugins.vars import BaseVarsPlugin
from ansible.inventory.host import Host
from ansible.inventory.group import Group
from ansible.utils.vars import merge_hash
import os
import yaml

DOCUMENTATION = '''
    vars: merge_group_vars
    short_description: Merges host and group variables with caching
    description:
        - This plugin merges variables from host_vars and group_vars files, 
          processing groups derived from each host.
        - Supports both .yml and .yaml file extensions.
    options: {}
'''

class VarsModule(BaseVarsPlugin):
    def __init__(self):
        super(VarsModule, self).__init__()
        self.entity_vars_cache = {}
        self.path_cache = {}

    def get_vars_from_file(self, vars_file_base):
        """Read variables from a YAML file with either .yml or .yaml extension."""
        for ext in ['.yml', '.yaml']:
            vars_file = vars_file_base + ext
            if os.path.exists(vars_file):
                try:
                    with open(vars_file, 'r') as f:
                        data = yaml.safe_load(f)
                        return data if data is not None else {}
                except (yaml.YAMLError, IOError) as e:
                    print(f"Error reading file {vars_file}: {e}")
        return {}

    def _get_entity_vars(self, entity, path):
        """Get vars for an entity (host or group) from cache or file system."""
        if entity.name not in self.entity_vars_cache:
            if isinstance(entity, Host):
                vars_path = os.path.join(path, 'host_vars', entity.name)
            else:
                vars_path = os.path.join(path, 'group_vars', entity.name)
            self.entity_vars_cache[entity.name] = self.get_vars_from_file(vars_path)
        return self.entity_vars_cache[entity.name]

    def get_vars(self, loader, path, entities, cache=True):
        super(VarsModule, self).get_vars(loader, path, entities)

        if path in self.path_cache:
            # print(f"  -- Reusing cache for path: {path}")
            return self.path_cache[path]

        # print(f"Path: [{path}], loaderType: {type(loader)}, loaderName: {loader}")
        data = {}

        if not isinstance(entities, list):
            entities = [entities]

        for entity in entities:
            if isinstance(entity, Host):
                # print(f"Processing host: {entity.name}")
                merged_vars = {}
                
                # Process groups first, from least specific to most specific
                groups = sorted(entity.get_groups(), key=lambda g: g.depth)
                for group in groups:
                    # print(f"  Processing group: {group.name} (depth: {group.depth})")
                    group_vars = self._get_entity_vars(group, path)
                    if group_vars:
                        merged_vars = merge_hash(merged_vars, group_vars)
                
                # Then process host vars, which will override group vars
                host_vars = self._get_entity_vars(entity, path)
                merged_vars = merge_hash(merged_vars, host_vars)
                
                # Merge the host's vars into the overall data
                data = merge_hash(data, merged_vars)

        self.path_cache[path] = data
        return data
      
