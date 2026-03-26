"""Deterministic math problem generator."""
from dataclasses import dataclass
from typing import List

from .config import LEVELS, OP_COLORS, OP_SYMBOLS


@dataclass
class MathProblem:
    """A single math problem."""

    a: int
    b: int
    op: str  # "+", "-", "*", "/"
    answer: int
    level: int
    position: int = 0  # Controls Anki new-card ordering

    @property
    def key(self) -> str:
        """Canonical cache key, e.g., '7+5'."""
        return f"{self.a}{self.op}{self.b}"

    @property
    def display(self) -> str:
        """Human-readable display, e.g., '7 + 5 = ?'."""
        sym = OP_SYMBOLS.get(self.op, self.op)
        return f"{self.a} {sym} {self.b} = ?"

    @property
    def display_no_question(self) -> str:
        """Display without '= ?', e.g., '7 + 5'."""
        sym = OP_SYMBOLS.get(self.op, self.op)
        return f"{self.a} {sym} {self.b}"

    @property
    def problem_html(self) -> str:
        """Problem with operation-specific color as inline style."""
        color = OP_COLORS.get(self.op, "#2c3e50")
        return f'<span style="color:{color}">{self.display}</span>'


def _generate_addition(a_range: tuple, b_range: tuple) -> List[MathProblem]:
    """Generate all addition problems for given ranges."""
    problems = []
    for a in range(a_range[0], a_range[1] + 1):
        for b in range(b_range[0], b_range[1] + 1):
            problems.append(MathProblem(a=a, b=b, op="+", answer=a + b, level=0))
    return problems


def _generate_subtraction(a_range: tuple, b_range: tuple) -> List[MathProblem]:
    """Generate subtraction problems where result >= 0."""
    problems = []
    for a in range(a_range[0], a_range[1] + 1):
        for b in range(b_range[0], b_range[1] + 1):
            if a >= b:
                problems.append(
                    MathProblem(a=a, b=b, op="-", answer=a - b, level=0)
                )
    return problems


def _generate_multiplication(a_range: tuple, b_range: tuple) -> List[MathProblem]:
    """Generate all multiplication problems for given ranges."""
    problems = []
    for a in range(a_range[0], a_range[1] + 1):
        for b in range(b_range[0], b_range[1] + 1):
            problems.append(MathProblem(a=a, b=b, op="*", answer=a * b, level=0))
    return problems


def _generate_division(a_range: tuple, b_range: tuple) -> List[MathProblem]:
    """Generate exact division problems.

    a_range is the quotient range, b_range is the divisor range.
    The dividend = quotient * divisor.
    """
    problems = []
    for quotient in range(a_range[0], a_range[1] + 1):
        for divisor in range(b_range[0], b_range[1] + 1):
            dividend = quotient * divisor
            problems.append(
                MathProblem(
                    a=dividend, b=divisor, op="/", answer=quotient, level=0
                )
            )
    return problems


_GENERATORS = {
    "+": _generate_addition,
    "-": _generate_subtraction,
    "*": _generate_multiplication,
    "/": _generate_division,
}


def generate_problems(level: int) -> List[MathProblem]:
    """Generate all problems for a given level.

    Returns problems with level and position fields set.
    Problems are ordered from easiest to hardest within the level.
    """
    if level not in LEVELS:
        raise ValueError(f"Unknown level {level}. Valid levels: {sorted(LEVELS.keys())}")

    level_def = LEVELS[level]
    a_range = level_def["a_range"]
    b_range = level_def["b_range"]
    ops = level_def["ops"]

    all_problems = []
    for op in ops:
        gen = _GENERATORS[op]
        problems = gen(a_range, b_range)
        all_problems.extend(problems)

    # Deduplicate by key (e.g., level 3 combines L1+L2 ops, no actual dupes
    # but level 8 might have overlapping ranges)
    seen = set()
    unique = []
    for p in all_problems:
        if p.key not in seen:
            seen.add(p.key)
            unique.append(p)

    # Smart ordering: progressive difficulty with variety
    unique = _smart_order(unique)

    # Assign level and position
    for i, p in enumerate(unique):
        p.level = level
        p.position = i

    return unique


def _difficulty_score(p: MathProblem) -> float:
    """Assign a difficulty score to a problem.

    Lower = easier. Considers operation type, operand size, and answer.
    """
    op_weight = {"+": 0, "-": 1, "*": 2, "/": 3}[p.op]
    # Identity operations are trivially easy regardless of op type
    if p.op in ("+", "-") and p.b == 0:
        return 0.0 + p.a * 0.1
    if p.op == "*" and (p.a <= 1 or p.b <= 1):
        return 5.0 + max(p.a, p.b) * 0.1
    if p.op == "/" and p.b == 1:
        return 5.0 + p.a * 0.1
    # Doubles are easier (2+2, 3+3, 4×4)
    double_bonus = -2.0 if p.a == p.b else 0.0
    # Round answers are easier (10, 20)
    round_bonus = -1.0 if p.answer % 10 == 0 and p.answer > 0 else 0.0

    return (
        op_weight * 30
        + max(p.a, p.b) * 2
        + p.answer * 0.5
        + double_bonus
        + round_bonus
    )


def _smart_order(problems: List[MathProblem]) -> List[MathProblem]:
    """Order problems for engaging learning: progressive difficulty with variety.

    Strategy:
    1. Score each problem by difficulty
    2. Divide into tiers (buckets of ~8-12 problems)
    3. Within each tier, pick cards to maximize variety:
       - Alternate operations when possible
       - Avoid consecutive same first-operand
       - Avoid consecutive same answer
    """
    if not problems:
        return problems

    # Score and sort by difficulty
    scored = [(p, _difficulty_score(p)) for p in problems]
    scored.sort(key=lambda x: x[1])

    # Divide into tiers
    tier_size = max(8, len(scored) // 15)
    tiers = []
    for i in range(0, len(scored), tier_size):
        tier = [p for p, _ in scored[i : i + tier_size]]
        tiers.append(tier)

    # Within each tier, pick cards for maximum variety
    result = []
    for tier in tiers:
        result.extend(_interleave_tier(tier))

    return result


def _interleave_tier(tier: List[MathProblem]) -> List[MathProblem]:
    """Reorder a tier of similar-difficulty problems for variety.

    Greedy: always pick the card most different from the previous one.
    """
    if len(tier) <= 1:
        return tier

    remaining = list(tier)
    ordered = [remaining.pop(0)]

    while remaining:
        prev = ordered[-1]
        best_idx = 0
        best_score = -1

        for i, candidate in enumerate(remaining):
            variety = 0
            # Different operation → big bonus
            if candidate.op != prev.op:
                variety += 10
            # Different first operand
            if candidate.a != prev.a:
                variety += 5
            # Different second operand
            if candidate.b != prev.b:
                variety += 3
            # Different answer
            if candidate.answer != prev.answer:
                variety += 2
            # Not adjacent numbers
            if abs(candidate.a - prev.a) > 1:
                variety += 1

            if variety > best_score:
                best_score = variety
                best_idx = i

        ordered.append(remaining.pop(best_idx))

    return ordered


def level_problem_count(level: int) -> int:
    """Return the number of problems in a level without generating them all."""
    return len(generate_problems(level))


def normalize_problem_key(key: str) -> str:
    """Normalize a problem key: strip spaces, canonical form."""
    return key.replace(" ", "")
