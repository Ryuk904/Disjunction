import time

def extract_disjunctive_intervals_linear(D1, A, domain_min, domain_max, run_QH):
    intervals = []
    start = None

    for val in range(domain_min, domain_max + 1):
        D1[A] = val
        if run_QH(D1):
            if start is None:
                start = val
        else:
            if start is not None:
                intervals.append((start, val - 1))
                start = None

    if start is not None:
        intervals.append((start, domain_max))

    return intervals


def extract_all_disjunctive_intervals_multi(D1, attributes, domains, neutral_values, run_QH):
    """
    D1: dict with all attribute values
    attributes: list of attribute names (e.g. ['A', 'B'])
    domains: dict of (min, max) per attribute, e.g. { 'A': (1, 100), 'B': (1, 100) }
    neutral_values: dict of values to freeze for each attribute when it's not being tested
    run_QH: function that runs the hidden query on D1
    """
    all_results = {}
    #attribute_times = {} # Dictionary to store execution time for each attribute

    for attr in attributes:
        #attr_start_time = time.time() # Start time for the current attribute
        # Freeze other attributes to neutral values
        for other_attr in attributes:
            if other_attr != attr:
                D1[other_attr] = neutral_values[other_attr]

        # Extract disjunctive intervals for this attribute using linear search
        domain_min, domain_max = domains[attr]
        intervals = extract_disjunctive_intervals_linear(D1, attr, domain_min, domain_max, run_QH)
        all_results[attr] = intervals
        # attr_end_time = time.time() # End time for the current attribute
        # attribute_times[attr] = attr_end_time - attr_start_time # Store execution time

    return all_results #, attribute_times # Return both results and attribute times


# def hidden_query(D1):
#     A = D1['A']
#     B = D1['B']
#     C = D1['C']
#
#     return (A < 10 or (20 <= A < 30) or (40 <= A < 50) or A > 60 or A == 15 or
#             B < 50 or (60 <= B < 70) or (80 <= B < 90) or B > 100 or B == 85 or
#             C < 100 or (200 <= C < 300) or (400 <= C < 500) or C > 600 or C == 30)
#
# D1 = {'A': 0, 'B': 0, 'C': 0}
# attributes = ['A', 'B', 'C']
# domains = {'A': (1, 100000), 'B': (1, 100000), 'C': (1, 100000)}
# neutral_values = {'A': 55, 'B': 75, 'C': 350}  # safe zones
#
# start_time = time.time()
# results, attribute_times = extract_all_disjunctive_intervals_multi(D1, attributes, domains, neutral_values, hidden_query)
# end_time = time.time()
#
# print("Disjunctive Intervals:")
# for attr, intervals in results.items():
#     print(f" - {attr}: {intervals}")
#
# print("\nExecution time per attribute:")
# for attr, exec_time in attribute_times.items():
#     print(f" - {attr}: {exec_time:.4f} seconds")
#
# print(f"\nTotal execution time: {end_time - start_time:.4f} seconds")