"""Return-correlation calculations and threshold-based relationships."""

import pandas as pd


class RelationshipAnalyzer:
    """Analyze Pearson correlation between aligned daily return series."""

    @staticmethod
    def correlation_matrix(returns: pd.DataFrame) -> pd.DataFrame:
        if returns.empty or returns.shape[1] < 2:
            raise ValueError("At least two stocks with overlapping returns are required.")
        return returns.corr(method="pearson")

    @staticmethod
    def qualifying_pairs(correlations: pd.DataFrame, threshold: float, include_negative: bool = False):
        if not -1 <= threshold <= 1:
            raise ValueError("Correlation threshold must be between -1 and 1.")
        pairs = []
        symbols = list(correlations.columns)
        for i, left in enumerate(symbols):
            for right in symbols[i + 1 :]:
                value = correlations.loc[left, right]
                if pd.notna(value) and (abs(value) >= threshold if include_negative else value >= threshold):
                    pairs.append((left, right, float(value)))
        return pairs
