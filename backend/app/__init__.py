import os
import sys

# Add src/scripts to path so we can import existing modules
_scripts_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'scripts'))
if _scripts_dir not in sys.path:
    sys.path.insert(0, _scripts_dir)
