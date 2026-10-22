"""Classroom-sized modular arithmetic algorithms with worked steps."""

from math import prod


class ModularArithmeticEngine:
    @staticmethod
    def divides(divisor, value):
        return divisor != 0 and value % divisor == 0

    @staticmethod
    def gcd(a, b):
        a, b = abs(int(a)), abs(int(b))
        steps = []
        while b:
            q, r = divmod(a, b)
            steps.append(f"{a} = {q}({b}) + {r}")
            a, b = b, r
        return a, steps

    @staticmethod
    def extended_gcd(a, b):
        original_a, original_b = int(a), int(b)
        old_r, r, old_s, s, old_t, t = abs(original_a), abs(original_b), 1, 0, 0, 1
        while r:
            q = old_r // r
            old_r, r = r, old_r - q * r
            old_s, s = s, old_s - q * s
            old_t, t = t, old_t - q * t
        x = old_s * (1 if original_a >= 0 else -1)
        y = old_t * (1 if original_b >= 0 else -1)
        return old_r, x, y

    @classmethod
    def modular_inverse(cls, a, modulus):
        if modulus <= 1:
            raise ValueError("Modulus must be greater than 1.")
        gcd_value, x, _ = cls.extended_gcd(a, modulus)
        if gcd_value != 1:
            return None
        return x % modulus

    @staticmethod
    def is_prime(n):
        n = int(n)
        if n < 2:
            return False
        divisor = 2
        while divisor * divisor <= n:
            if n % divisor == 0:
                return False
            divisor += 1
        return True

    @staticmethod
    def prime_factorization(n):
        n = int(n)
        if n < 1:
            raise ValueError("Factorization is defined here for positive integers.")
        factors, divisor = {}, 2
        while divisor * divisor <= n:
            while n % divisor == 0:
                factors[divisor] = factors.get(divisor, 0) + 1
                n //= divisor
            divisor += 1
        if n > 1:
            factors[n] = factors.get(n, 0) + 1
        return factors

    @classmethod
    def phi(cls, n):
        if n < 1:
            raise ValueError("Euler phi is defined here for positive integers.")
        result = n
        for prime in cls.prime_factorization(n):
            result = result // prime * (prime - 1)
        return result

    @staticmethod
    def modular_power(base, exponent, modulus):
        if exponent < 0 or modulus <= 0:
            raise ValueError("Exponent must be nonnegative and modulus positive.")
        return pow(base, exponent, modulus)

    @classmethod
    def fermat_demo(cls, a, prime):
        if not cls.is_prime(prime):
            raise ValueError("Fermat demonstration requires a prime modulus.")
        if a % prime == 0:
            raise ValueError("a must not be divisible by the prime modulus.")
        return pow(a, prime - 1, prime)

    @classmethod
    def chinese_remainder(cls, residues, moduli):
        if len(residues) != len(moduli) or not moduli:
            raise ValueError("Provide one residue for each modulus.")
        if any(m <= 1 for m in moduli):
            raise ValueError("Each modulus must be greater than 1.")
        for i, m in enumerate(moduli):
            for n in moduli[i + 1 :]:
                if cls.gcd(m, n)[0] != 1:
                    raise ValueError("CRT requires pairwise-coprime moduli in this version.")
        product_moduli = prod(moduli)
        total = 0
        details = []
        for residue, modulus in zip(residues, moduli):
            partial = product_moduli // modulus
            inverse = cls.modular_inverse(partial, modulus)
            term = (residue % modulus) * partial * inverse
            total += term
            details.append({"residue": residue % modulus, "modulus": modulus, "partial": partial, "inverse": inverse, "term": term})
        return total % product_moduli, product_moduli, details

    @classmethod
    def solve_congruence(cls, a, b, modulus):
        """Solve a*x = b (mod m); return all residues or an empty list."""
        if modulus <= 0:
            raise ValueError("Modulus must be positive.")
        g, _ = cls.gcd(a, modulus)
        if b % g:
            return []
        reduced_modulus = modulus // g
        inverse = cls.modular_inverse(a // g, reduced_modulus) if reduced_modulus > 1 else 0
        first = ((b // g) * inverse) % reduced_modulus if reduced_modulus > 1 else 0
        return [(first + k * reduced_modulus) % modulus for k in range(g)]
