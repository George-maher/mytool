"""
CVSS v3.1 Scoring Utility for X-Shield Framework
Implements standard vulnerability scoring logic
"""

import math
from typing import Dict, Optional

class CVSS31:
    """CVSS v3.1 calculation logic"""

    # Impact Sub Score constants
    ISS_CONST = 6.73

    # Weights for metrics
    METRICS = {
        'AV': {'N': 0.85, 'A': 0.62, 'L': 0.55, 'P': 0.2},
        'AC': {'L': 0.77, 'H': 0.44},
        'PR': {
            'U': {'N': 0.85, 'L': 0.62, 'H': 0.27},
            'C': {'N': 0.85, 'L': 0.68, 'H': 0.50}
        },
        'UI': {'N': 0.85, 'R': 0.62},
        'S': {'U': 6.42, 'C': 7.52},
        'C': {'N': 0.0, 'L': 0.22, 'H': 0.56},
        'I': {'N': 0.0, 'L': 0.22, 'H': 0.56},
        'A': {'N': 0.0, 'L': 0.22, 'H': 0.56}
    }

    @classmethod
    def calculate(cls, vector: str) -> Optional[float]:
        """
        Calculate CVSS v3.1 Base Score from vector string
        Format: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H
        """
        try:
            if not vector.startswith("CVSS:3.1/"):
                return None

            parts = vector.split('/')
            m = {}
            for part in parts[1:]:
                k, v = part.split(':')
                m[k] = v

            # Extract metrics
            av = cls.METRICS['AV'][m['AV']]
            ac = cls.METRICS['AC'][m['AC']]
            s = m['S']
            pr = cls.METRICS['PR'][s][m['PR']]
            ui = cls.METRICS['UI'][m['UI']]
            c = cls.METRICS['C'][m['C']]
            i = cls.METRICS['I'][m['I']]
            a = cls.METRICS['A'][m['A']]

            # Impact Sub Score
            iss = 1 - ((1 - c) * (1 - i) * (1 - a))

            # Impact
            if s == 'U':
                impact = 6.42 * iss
            else:
                impact = 7.52 * (iss - 0.029) - 3.25 * pow(iss - 0.02, 15)

            # Exploitability
            exploitability = 8.22 * av * ac * pr * ui

            if impact <= 0:
                base_score = 0
            else:
                if s == 'U':
                    base_score = cls._round_up(min(impact + exploitability, 10))
                else:
                    base_score = cls._round_up(min(1.08 * (impact + exploitability), 10))

            return base_score

        except Exception:
            return None

    @staticmethod
    def _round_up(n: float) -> float:
        """Standard CVSS rounding rule"""
        return math.ceil(n * 10) / 10.0

    @staticmethod
    def get_severity(score: float) -> str:
        """Get severity string from score"""
        if score == 0: return "None"
        if 0.1 <= score <= 3.9: return "Low"
        if 4.0 <= score <= 6.9: return "Medium"
        if 7.0 <= score <= 8.9: return "High"
        if 9.0 <= score <= 10.0: return "Critical"
        return "Unknown"
