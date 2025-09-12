# src/emrpy/really_utils.py

from pathlib import Path


def get_root_path(fallback_levels: int = 0) -> Path:
    """
    Resolve a root-like path from the current working directory.

    Parameters:
    -----------
    fallback_levels : int, default 0
        Number of parent directories to ascend from the current working
        directory (CWD). Must be >= 0. When 0, returns the resolved CWD.

    Returns:
    --------
    Path
        Absolute path obtained after moving up `fallback_levels` parents
        from the resolved CWD.

    Notes:
    ------
    Typical usage:
      - Scripts: `fallback_levels=0` usually suffices because scripts are
        run from the repository root (so CWD is already the root).
      - Notebooks: CWD is the notebook's folder. Set `fallback_levels`
        to the depth from the notebook folder to the project root.
        Example: for `<repo>/notebooks/notebook.ipynb`, use `fallback_levels=1`
        to return `<repo>`.

    Examples:
    ---------
    >>> # CWD: /home/user/project/subdir
    >>> get_root_path()
    PosixPath('/home/user/project/subdir')
    >>> get_root_path(fallback_levels=1)
    PosixPath('/home/user/project')
    """
    path = Path.cwd().resolve()
    for _ in range(fallback_levels):
        path = path.parent
    return path
