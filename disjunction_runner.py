import time
from disjunction_recursive import extract_all_disjunctive_intervals_multi as extract_recursive
from disjunction_linear import extract_all_disjunctive_intervals_multi as extract_linear

# ------------------- CONFIGURATION SECTION -------------------
# Define your clause here as a function
def hidden_query(D1):
    A = D1['A']
    B = D1['B']
    C = D1['C']
    # Example clause (edit as needed)
    return (A < 10 or (20 <= A < 30) or (40 <= A < 50) or A > 60 or A == 15 or
            B < 50 or (60 <= B < 70) or (80 <= B < 90) or B > 100 or B == 85 or
            C < 100 or (200 <= C < 300) or (400 <= C < 500) or C > 600 or C == 30)

# Initial values for D1 (edit as needed)
D1 = {'A': 0, 'B': 0, 'C': 0}

# List of attributes to test (edit as needed)
attributes = ['A', 'B', 'C']

# Domains for each attribute (edit as needed)
domains = {'A': (1, 100000000), 'B': (1, 100000000), 'C': (1, 100000000)}

# Neutral values for each attribute (edit as needed)
neutral_values = {'A': 55, 'B': 75, 'C': 350}
# -------------------------------------------------------------

print("Running Recursive Disjunction Extraction...")
start_time = time.time()
results_recursive = extract_recursive(
    D1.copy(), attributes, domains, neutral_values, hidden_query
)
end_time = time.time()
print("Recursive Results:")
for attr, intervals in results_recursive.items():
    print(f" - {attr}: {intervals}")
print(f"Total time (recursive): {end_time - start_time:.4f} seconds\n")

print("Running Linear Disjunction Extraction...")
start_time = time.time()
results_linear = extract_linear(
    D1.copy(), attributes, domains, neutral_values, hidden_query
)
end_time = time.time()
print("Linear Results:")
for attr, intervals in results_linear.items():
    print(f" - {attr}: {intervals}")
print(f"Total time (linear): {end_time - start_time:.4f} seconds")