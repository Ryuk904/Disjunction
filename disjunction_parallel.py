from concurrent.futures import ThreadPoolExecutor
import time

def parallel_extract_disjunctive_intervals(D1, A, domain_min, domain_max, run_QH, max_workers=4):
    intervals = []
    start = None

    def check(val):
        D1_copy = D1.copy()
        D1_copy[A] = val
        return run_QH(D1_copy)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(check, range(domain_min, domain_max + 1)))

    for idx, val in enumerate(range(domain_min, domain_max + 1)):
        if results[idx]:
            if start is None:
                start = val
        else:
            if start is not None:
                intervals.append((start, val - 1))
                start = None
    if start is not None:
        intervals.append((start, domain_max))
    return intervals

def extract_all_disjunctive_intervals_multi(D1, attributes, domains, neutral_values, run_QH, max_workers=4):
    all_results = {}
    for attr in attributes:
        for other_attr in attributes:
            if other_attr != attr:
                D1[other_attr] = neutral_values[other_attr]
        domain_min, domain_max = domains[attr]
        intervals = parallel_extract_disjunctive_intervals(
            D1, attr, domain_min, domain_max, run_QH, max_workers=max_workers
        )
        all_results[attr] = intervals
    return


def hidden_query(D1):
    A = D1['A']
    B = D1['B']
    C = D1['C']

    return (A < 10 or (20 <= A < 30) or (40 <= A < 50) or A > 60 or A == 15 or
            B < 50 or (60 <= B < 70) or (80 <= B < 90) or B > 100 or B == 85 or
            C < 100 or (200 <= C < 300) or (400 <= C < 500) or C > 600 or C == 30)

D1 = {'A': 0, 'B': 0, 'C': 0}
attributes = ['A', 'B', 'C']
domains = {'A': (1, 100000000), 'B': (1, 100000000), 'C': (1, 100000000)}
neutral_values = {'A': 55, 'B': 75, 'C': 350}  # safe zones

start_time = time.time()
results, attribute_times = extract_all_disjunctive_intervals_multi(D1, attributes, domains, neutral_values, hidden_query)
end_time = time.time()

print("Disjunctive Intervals:")
for attr, intervals in results.items():
    print(f" - {attr}: {intervals}")

print("\nExecution time per attribute:")
for attr, exec_time in attribute_times.items():
    print(f" - {attr}: {exec_time:.4f} seconds")

print(f"\nTotal Execution time: {end_time - start_time:.4f} seconds")