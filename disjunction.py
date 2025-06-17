from typing import Callable, Dict, List, Tuple
import re
import time
from tqdm import tqdm

# --- Rewriter from rewrite_bounds_with_Disjuncts.py ---

def rewrite_disjuncts_with_bounds(sql_clause: str, domain_bounds: Dict[str, tuple]) -> str:
    def bound_clause(attr: str, op: str, val: str) -> str:
        dmin, dmax = domain_bounds[attr]
        val = int(val)
        if op == "<":
            return f"({dmin} <= {attr} and {attr} < {val})"
        elif op == "<=":
            return f"({dmin} <= {attr} and {attr} <= {val})"
        elif op == ">":
            return f"({attr} > {val} and {attr} <= {dmax})"
        elif op == ">=":
            return f"({attr} >= {val} and {attr} <= {dmax})"
        else:
            return f"{attr} {op} {val}"  # fallback

    def bound_range_clause(attr: str, low: str, high: str) -> str:
        dmin, dmax = domain_bounds[attr]
        low_val = int(low)
        high_val = int(high)
        start = max(dmin, low_val)
        end = min(dmax + 1, high_val + 1)  # because < upper bound
        return f"({attr} >= {start} and {attr} < {end})"

    # Handle BETWEEN
    sql_clause = re.sub(
        r"(\w+)\s+BETWEEN\s+(\d+)\s+AND\s+(\d+)",
        lambda m: bound_range_clause(m[1], m[2], m[3]),
        sql_clause,
        flags=re.IGNORECASE
    )

    # Handle comparisons
    comparison_pattern = re.compile(r"(\w+)\s*(<=|>=|<|>)\s*(\d+)")
    parts = re.split(r"\s+OR\s+", sql_clause, flags=re.IGNORECASE)
    bounded_parts = []
    for part in parts:
        part = part.strip()
        match = comparison_pattern.match(part)
        if match:
            attr, op, val = match.groups()
            if attr in domain_bounds:
                bounded_parts.append(bound_clause(attr, op, val))
                continue
        bounded_parts.append(part)  # keep unmodified if no match
    return " or ".join(bounded_parts)

# --- Core interval extractor ---

def extract_disjunctive_intervals(
    D1: Dict[str, int],
    A: str,
    domain_min: int,
    domain_max: int,
    run_QH: Callable[[Dict[str, int]], bool]
) -> List[Tuple[int, int]]:
    intervals = []
    def recurse(L: int, R: int):
        if L > R:
            return
        mid = (L + R) // 2
        D1[A] = mid
        if not run_QH(D1):
            recurse(L, mid - 1)
            recurse(mid + 1, R)
            return
        start = mid
        while start > L:
            D1[A] = start - 1
            if run_QH(D1):
                start -= 1
            else:
                break
        end = mid
        while end < R:
            D1[A] = end + 1
            if run_QH(D1):
                end += 1
            else:
                break
        intervals.append((start, end))
        recurse(L, start - 1)
        recurse(end + 1, R)
    recurse(domain_min, domain_max)
    intervals.sort()
    return intervals

def extract_all_disjunctive_intervals_multi(
    D1, attributes, domains, run_QH
):
    all_results = {}
    for attr in tqdm(attributes, desc="Attributes"):
        for other_attr in attributes:
            if other_attr != attr:
                domain_min, domain_max = domains[other_attr]
                D1[other_attr] = domain_max + 1
        domain_min, domain_max = domains[attr]
        intervals = extract_disjunctive_intervals(D1, attr, domain_min, domain_max, run_QH)
        all_results[attr] = intervals
    return all_results

# --- Use the rewriter to create a bounded hidden query ---

def make_bounded_query(sql_clause: str, domain_bounds: Dict[str, tuple]):
    bounded_clause = rewrite_disjuncts_with_bounds(sql_clause, domain_bounds)
    # Build a function that evaluates the clause using D1's values
    def query(D1):
        # Make variables available in eval's scope
        scope = {k: D1.get(k, 0) for k in domain_bounds}
        return eval(bounded_clause, {}, scope)
    return query


def measure_execution_time(main_func):
    """
    Measures and prints the execution time of the provided function.
    """
    start = time.time()
    result = main_func()
    end = time.time()
    print(f"\n Total execution time: {end - start:.4f} seconds")
    return result


# --- Example usage ---

if __name__ == "__main__":
    def main():
        D1 = {'A': 0, 'B': 0, 'C': 0}  # Initial values for attributes
        attributes = ['A', 'B', 'C']
        domains = {
            'A': (1, 1000000),
            'B': (1, 1000000),
            'C': (1, 1000000)
        }
        sql = "A < 20 OR A > 40 OR B < 10 OR 20 <= B < 30 OR B > 90 OR C < 5 OR 10 <= C < 15 OR C > 95"
        bounded_query = make_bounded_query(sql, domains)

        results = extract_all_disjunctive_intervals_multi(D1, attributes, domains, bounded_query)

        print("Allowed intervals per attribute:")
        for attr, intervals in results.items():
            print(f" - {attr}: {intervals}")
        return results    
    # Measure execution time
    measure_execution_time(main)