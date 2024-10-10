Thanks to this plugin you don't have to set DEFAULT_HASH_BEHAVIOUR to 'merge' in your ansible configuration file.
It will use 'merge_hash' method on your group / host files in your 'group_vars' and 'host_vars' respectively.
This way you can get your nested dictionaries merged.

Please create plugins/vars folder in you main ansible directory.
Then place the 'merge_group_vars.py' file there.
Update your ansible.cfg file and add there: 'ars_plugins = ./plugins/vars'

Enjoy 
