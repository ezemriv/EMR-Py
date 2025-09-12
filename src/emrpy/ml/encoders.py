# src/emrpy/ml/encoders.py
"""
Machine Learning Encoding Utilities

Functions for encoding categorical columns.
"""

from typing import List, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.preprocessing import OrdinalEncoder


def encode_cats_pandas(
    train_df: pd.DataFrame,
    cat_cols: List[str],
    test_df: Optional[pd.DataFrame] = None,
) -> Tuple[pd.DataFrame, Optional[pd.DataFrame], OrdinalEncoder]:
    """
    Encode categorical columns with handling for unknown and missing values.

    Applies an OrdinalEncoder to the specified columns in a training DataFrame,
    then transforms an optional test DataFrame using the same encoder settings.

    Parameters:
    -----------
    train_df : pandas.DataFrame
        DataFrame containing the training data with categorical columns to encode.
    cat_cols : list[str]
        Names of the categorical columns to encode.
    test_df : pandas.DataFrame, optional (default=None)
        Optional DataFrame containing the same categorical columns to transform.

    Returns:
    --------
    tuple[pandas.DataFrame, pandas.DataFrame or None, OrdinalEncoder]
        - Encoded copy of `train_df` with specified columns replaced by integer codes.
        - Encoded copy of `test_df`, or None if no test DataFrame was provided.
        - The fitted `OrdinalEncoder` instance for use on new data.

    Examples:
    ---------
    >>> import pandas as pd
    >>> from emrpy.ml.encoders import encode_cats_pandas
    >>> df_train = pd.DataFrame({"color": ["red", "blue", None]})
    >>> df_test  = pd.DataFrame({"color": ["blue", "yellow", None]})
    >>> train_enc, test_enc, encoder = encode_cats_pandas(df_train, ["color"], df_test)
    >>> train_enc["color"].tolist()
    [0, 1, -1]
    >>> test_enc["color"].tolist()
    [1, -2, -1]
    """
    train_df = train_df.copy()
    test_df = test_df.copy() if test_df is not None else None

    encoder = OrdinalEncoder(
        categories="auto",
        dtype=np.int16,
        handle_unknown="use_encoded_value",
        unknown_value=-2,
        encoded_missing_value=-1,
    )

    train_encoded = encoder.fit_transform(train_df[cat_cols])
    for idx, col in enumerate(cat_cols):
        train_df[col] = train_encoded[:, idx]

    if test_df is not None:
        test_encoded = encoder.transform(test_df[cat_cols])
        for idx, col in enumerate(cat_cols):
            test_df[col] = test_encoded[:, idx]

    return train_df, test_df, encoder
