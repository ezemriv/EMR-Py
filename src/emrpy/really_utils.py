# src/emrpy/really_utils.py

from pathlib import Path
from typing import Union

def get_root_path(file_: Union[str, Path], levels: int = 1) -> Path:
    """
    Return a parent directory relative to a given file path.

    Commonly used to resolve project root paths by walking up from `__file__`.

    Parameters:
    -----------
    file_ : str or Path
        File path to resolve from (typically `__file__`).
    levels : int, default 1
        Number of directory levels to go up.

    Returns:
    --------
    Path
        The resolved parent directory.

    Examples:
    ---------
    >>> get_root_path(__file__, levels=2)
    PosixPath('/path/to/project')
    """
    return Path(file_).resolve().parents[levels]
