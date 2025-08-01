# Inside a .py file, you can rely on the built-in __file__ variable to get root path.

from emrpy import get_root_path

project_root = get_root_path(__file__, levels=1)
print(f"Project root directory: {project_root}")