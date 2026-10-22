"""Core concepts displayed in the application's context-aware Math Guide."""

CONCEPTS = {
    "Daily return and correlation": {
        "definition": "A daily simple return is the fractional change between consecutive closes. Pearson correlation measures linear co-movement between two return series.",
        "use": "MarketMesh aligns dates first, calculates returns, then uses the correlation matrix to decide which stock pairs become edges.",
        "method": "Rₜ=(Pₜ−Pₜ₋₁)/Pₜ₋₁; ρ(X,Y)=cov(X,Y)/(σXσY). An edge is added when |ρ| meets the threshold, or ρ meets it when negative edges are disabled.",
    },
    "Vertex degree": {
        "definition": "The degree of a vertex is the number of incident edges.",
        "use": "It counts how many other selected stocks meet the current relationship rule.",
        "method": "deg(v)=Σᵤ A[v,u], where A is the binary adjacency matrix.",
    },
    "Connected components": {
        "definition": "A connected component is a maximal set of vertices where every pair is linked by some path.",
        "use": "Components identify groups that are connected under the chosen threshold; different components have no qualifying edge between them.",
        "method": "Run graph traversal from each unvisited vertex; each traversal tree yields one component.",
    },
    "Adjacency and incidence matrices": {
        "definition": "The adjacency matrix records vertex-to-vertex edges. The incidence matrix records which vertices touch each edge.",
        "use": "MarketMesh displays binary and correlation-weighted adjacency matrices, plus an incidence matrix.",
        "method": "For a simple undirected graph, A[i,j]=1 exactly when an edge joins i and j; weighted A stores the correlation. Each incidence column has 1s at its edge endpoints.",
    },
    "Traversal, paths, and cycles": {
        "definition": "BFS and DFS visit reachable vertices; a path connects vertices; a cycle is a closed path with no repeated interior vertex.",
        "use": "The app shows traversal order, shortest paths, a bounded set of simple paths, and a cycle basis.",
        "method": "BFS uses a queue, DFS uses a stack or recursion, shortest paths use unweighted breadth-first search, and a cycle basis spans the graph's cycle space.",
    },
    "Euler and Hamiltonian properties": {
        "definition": "An Euler trail uses every edge once; a Hamiltonian path visits every vertex once.",
        "use": "These describe different ways of covering the selected graph and are evaluated independently.",
        "method": "For a connected non-isolated graph, an Euler circuit requires all degrees even and an Euler trail requires exactly zero or two odd degrees. Hamiltonian search checks vertex orderings.",
    },
    "Trees and bipartite graphs": {
        "definition": "A tree is connected and acyclic. A bipartite graph's vertices split into two classes so each edge crosses classes.",
        "use": "The stock-to-sector graph is bipartite by construction because edges join stock labels to sector labels.",
        "method": "A finite graph is a tree when it is connected and has n−1 edges. Bipartiteness can be tested by BFS two-coloring.",
    },
    "Walk counts and adjacency powers": {
        "definition": "A walk is a sequence of adjacent vertices; vertices and edges may repeat. The adjacency powers count walks by length.",
        "use": "The selected source and target's counts at lengths 0…k form the sequence used by the generating-function view.",
        "method": "(Aⁿ)[i,j] equals the number of length-n walks from i to j, using the binary adjacency matrix.",
    },
    "Ordinary generating function": {
        "definition": "An ordinary generating function stores a sequence as coefficients of powers of x.",
        "use": "MarketMesh displays a finite polynomial for the computed walk-count sequence.",
        "method": "G(x)=Σₙ aₙxⁿ. With finitely many computed terms, the result is a truncated polynomial rather than a claimed closed form.",
    },
    "Recurrence relations": {
        "definition": "A recurrence defines sequence terms from earlier terms and initial conditions.",
        "use": "The lab compares homogeneous, non-homogeneous, first-order, and second-order examples, including Fibonacci.",
        "method": "The supported form is aₙ=c₁aₙ₋₁+c₂aₙ₋₂+d; initial values a₀ and a₁ determine the sequence.",
    },
    "Divisibility and Euclidean algorithms": {
        "definition": "d divides n when n is an integer multiple of nonzero d. The gcd is the largest positive common divisor.",
        "use": "The modular arithmetic lab checks divisibility and displays Euclidean remainders and an extended-Euclid identity.",
        "method": "Repeated division a=qb+r preserves gcd(a,b)=gcd(b,r); extended Euclid finds x,y such that ax+by=gcd(a,b).",
    },
    "Modular inverse and congruences": {
        "definition": "An inverse of a modulo m is y with ay≡1 (mod m). A congruence asks for residues satisfying an equality modulo m.",
        "use": "The lab reports inverses when they exist and solves linear congruences in the algorithm module.",
        "method": "An inverse exists exactly when gcd(a,m)=1. Reduce ax≡b (mod m) by gcd(a,m), then solve the reduced coprime equation.",
    },
    "Primes, Euler phi, and Fermat": {
        "definition": "A prime has no positive divisors besides 1 and itself. φ(n) counts residues from 1 to n coprime to n.",
        "use": "The app factors n to compute φ(n) and demonstrates Fermat's Little Theorem for a prime modulus.",
        "method": "φ(n)=n∏ₚ|ₙ(1−1/p); if p is prime and p∤a, then a^(p−1)≡1 (mod p).",
    },
    "Chinese Remainder Theorem": {
        "definition": "For pairwise-coprime moduli, simultaneous congruences have a unique solution modulo their product.",
        "use": "The cycle analyzer models alignment of simulated repeating event schedules, not real market cycles.",
        "method": "Let M=∏mᵢ, Mᵢ=M/mᵢ and yᵢ=Mᵢ⁻¹ mod mᵢ. Then x=ΣrᵢMᵢyᵢ mod M.",
    },
    "Graph stress test": {
        "definition": "A vertex or edge deletion creates a modified graph whose structural measures can be compared with the original.",
        "use": "The stress page reports changes to components, edges, largest component, reachability, and cycles.",
        "method": "Copy G, remove the chosen item, and recompute the same metrics on both graphs. This is structural analysis, not market causality.",
    },
}
