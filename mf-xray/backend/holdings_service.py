"""
Holdings Service for looking up mutual fund stock holdings.

Provides ISIN-based lookup (primary) and fuzzy name matching (fallback)
for mapping funds to their underlying stock holdings.
"""

import json
import os
import re
from typing import Dict, Optional
from difflib import SequenceMatcher


class HoldingsService:
    """
    Singleton service for fund holdings lookup.
    Loads holdings data from JSON file and provides lookup methods.
    """
    _instance = None
    _data = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._load_data()
        return cls._instance

    @classmethod
    def _load_data(cls):
        """Load holdings data from JSON file."""
        data_path = os.path.join(os.path.dirname(__file__), 'data', 'fund_holdings.json')
        try:
            with open(data_path, 'r', encoding='utf-8') as f:
                cls._data = json.load(f)
        except FileNotFoundError:
            cls._data = {"schemes": {}, "name_index": {}}
            print(f"Warning: Holdings data file not found at {data_path}")

    def get_holdings_by_isin(self, isin: str) -> Optional[Dict[str, float]]:
        """
        Primary lookup by ISIN - most reliable method.

        Args:
            isin: ISIN code (e.g., INF200K01RJ1)

        Returns:
            Dict of {stock_name: weight_as_fraction} or None if not found
        """
        if not isin:
            return None
        scheme = self._data.get("schemes", {}).get(isin)
        return scheme.get("holdings") if scheme else None

    def get_holdings_by_name(self, fund_name: str, threshold: float = 0.65) -> Optional[Dict[str, float]]:
        """
        Fuzzy match fallback when ISIN is unavailable.

        Args:
            fund_name: Fund name from PDF
            threshold: Minimum similarity score (0-1) for a match

        Returns:
            Dict of {stock_name: weight_as_fraction} or None if no match above threshold
        """
        if not fund_name:
            return None

        normalized = self._normalize(fund_name)
        name_index = self._data.get("name_index", {})

        # Try exact match first
        if normalized in name_index:
            isin = name_index[normalized]
            return self.get_holdings_by_isin(isin)

        # Fuzzy match on name_index keys
        best_match_isin = None
        best_score = threshold

        for indexed_name, isin in name_index.items():
            score = self._similarity(normalized, indexed_name)
            if score > best_score:
                best_score = score
                best_match_isin = isin

        if best_match_isin:
            return self.get_holdings_by_isin(best_match_isin)

        # Try fuzzy match on full scheme names
        for isin, scheme in self._data.get("schemes", {}).items():
            scheme_name = self._normalize(scheme.get("name", ""))
            score = self._similarity(normalized, scheme_name)
            if score > best_score:
                best_score = score
                best_match_isin = isin

        return self.get_holdings_by_isin(best_match_isin) if best_match_isin else None

    def get_fund_info(self, fund_name: str = None, isin: str = None) -> Optional[dict]:
        """
        Get full fund information including name, AMC, category, and holdings.

        Args:
            fund_name: Fund name for fuzzy lookup
            isin: ISIN for direct lookup

        Returns:
            Full scheme dict or None
        """
        if isin and isin in self._data.get("schemes", {}):
            return self._data["schemes"][isin]

        if fund_name:
            normalized = self._normalize(fund_name)
            name_index = self._data.get("name_index", {})

            if normalized in name_index:
                isin = name_index[normalized]
                return self._data.get("schemes", {}).get(isin)

        return None

    def _normalize(self, name: str) -> str:
        """
        Normalize fund name for matching.
        Strips common suffixes and special characters.
        """
        if not name:
            return ""

        name = name.lower()

        # Remove common suffixes
        strip_patterns = [
            r'\s*-?\s*direct\s*plan\s*',
            r'\s*-?\s*regular\s*plan\s*',
            r'\s*-?\s*growth\s*option?\s*',
            r'\s*-?\s*growth\s*$',
            r'\s*-?\s*idcw\s*',
            r'\s*-?\s*dividend\s*',
            r'\s*fund\s*$',
            r'\s*scheme\s*',
        ]

        for pattern in strip_patterns:
            name = re.sub(pattern, '', name, flags=re.IGNORECASE)

        # Remove special characters except spaces
        name = re.sub(r'[^a-z0-9\s]', '', name)

        # Collapse multiple spaces
        return ' '.join(name.split()).strip()

    def _similarity(self, s1: str, s2: str) -> float:
        """
        Calculate similarity ratio between two strings.
        Uses SequenceMatcher for fuzzy matching.
        """
        if not s1 or not s2:
            return 0.0
        return SequenceMatcher(None, s1, s2).ratio()

    def list_available_funds(self) -> list:
        """Return list of all available fund names in the database."""
        return [scheme.get("name") for scheme in self._data.get("schemes", {}).values()]


# Module-level instance for convenience
_holdings_service = None

def get_holdings_service() -> HoldingsService:
    """Get singleton instance of HoldingsService."""
    global _holdings_service
    if _holdings_service is None:
        _holdings_service = HoldingsService()
    return _holdings_service
