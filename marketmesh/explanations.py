"""Short definitions used by the educational interface."""

CONCEPTS = {
    "Vertex degree": "The degree of a vertex is the number of incident edges. Here it counts other selected stocks whose return correlation meets the threshold.",
    "Connected component": "A maximal set of vertices where every pair is joined by a path. A component is a structural cluster in this selected graph.",
    "Adjacency powers": "For binary adjacency matrix A, entry (i,j) of A^n counts walks of length n from vertex i to vertex j.",
    "Generating function": "The ordinary generating polynomial stores a sequence as coefficients: G(x) = sum(a_n x^n). For walks, the coefficient of x^n is the number of length-n walks.",
    "Euler path": "A trail that uses every edge exactly once exists in a connected non-isolated part when it has zero or two odd-degree vertices.",
    "Hamiltonian path": "A path visiting every vertex exactly once. Exact search is exponential, so MarketMesh limits it to small graphs.",
    "Chinese Remainder Theorem": "For pairwise-coprime moduli, simultaneous congruences have one solution modulo the product of the moduli.",
}
