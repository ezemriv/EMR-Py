from emrpy import get_root_path

project_root = get_root_path(fallback_levels=0)
print(f"Project root directory: {project_root}")
