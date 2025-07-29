from pathlib import Path
from typing import Union

def get_root_path(file_: Union[str, Path], levels: int = 1) -> Path:
    """
    Return the directory obtained by walking `levels` parents up
    from *file_*.

    Parameters
    ----------
    file_   : str | Path
        Usually pass in ``__file__`` from the calling module.
    levels  : int, default 1
        How many directory levels to go up.

    Returns
    -------
    pathlib.Path
        The directory ``levels`` steps above *file_*.
    """
    return Path(file_).resolve().parents[levels]
