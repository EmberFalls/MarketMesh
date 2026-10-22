"""Second-order linear recurrence simulator."""


class RecurrenceSolver:
    @staticmethod
    def generate(c1: int, c2: int, constant: int, a0: int, a1: int, terms: int):
        if terms < 1 or terms > 100:
            raise ValueError("Choose between 1 and 100 terms.")
        sequence = [int(a0)]
        if terms > 1:
            sequence.append(int(a1))
        while len(sequence) < terms:
            sequence.append(int(c1 * sequence[-1] + c2 * sequence[-2] + constant))
        return sequence

    @staticmethod
    def describe(c1: int, c2: int, constant: int, a0: int, a1: int, terms: int):
        order = 2 if c2 else 1
        terms_list = RecurrenceSolver.generate(c1, c2, constant, a0, a1, terms)
        equation = rf"a_n = {c1}a_{{n-1}}" + (rf" + {c2}a_{{n-2}}" if c2 else "") + (f" + {constant}" if constant else "")
        return {"equation": equation, "order": order, "homogeneous": constant == 0, "linear": True, "sequence": terms_list}

    @staticmethod
    def fibonacci(terms: int):
        return RecurrenceSolver.generate(1, 1, 0, 0, 1, terms)
