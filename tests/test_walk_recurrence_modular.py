import networkx as nx

from marketmesh.generating_function import GeneratingFunctionEngine
from marketmesh.modular import ModularArithmeticEngine as Modular
from marketmesh.recurrence import RecurrenceSolver
from marketmesh.walk_analysis import WalkAnalyzer


def test_walk_counts_and_generating_polynomial():
    graph = nx.path_graph(["A", "B", "C"])
    assert WalkAnalyzer(graph).count_walks("A", "C", 3) == [0, 0, 1, 0]
    assert GeneratingFunctionEngine.polynomial([1, 2, 4]) == "1 + 2*x + 4*x^2"


def test_recurrence_fibonacci_and_nonhomogeneous():
    assert RecurrenceSolver.fibonacci(7) == [0, 1, 1, 2, 3, 5, 8]
    assert RecurrenceSolver.generate(2, 0, 3, 1, 0, 5) == [1, 0, 3, 9, 21]
    first_order = RecurrenceSolver.describe_first_order(2, 3, 1, 5)
    assert first_order["sequence"] == [1, 5, 13, 29, 61]
    assert first_order["order"] == 1 and not first_order["homogeneous"]


def test_modular_arithmetic_examples():
    assert Modular.gcd(252, 105)[0] == 21
    assert Modular.modular_inverse(7, 26) == 15
    assert Modular.modular_power(7, 13, 23) == pow(7, 13, 23)
    assert Modular.modular_power_trace(7, 13, 23)[1]
    assert Modular.phi(9) == 6
    assert Modular.fermat_demo(2, 7) == 1
    assert Modular.chinese_remainder([2, 3, 2], [3, 5, 7])[:2] == (23, 105)
    assert Modular.solve_congruence(4, 2, 6) == [2, 5]
    assert Modular.modular_inverse(6, 15) is None
    assert Modular.is_prime(97) is True
    assert Modular.is_prime(91) is False
    assert Modular.prime_factorization(360) == {2: 3, 3: 2, 5: 1}
