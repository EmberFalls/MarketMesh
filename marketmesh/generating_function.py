"""Ordinary generating-polynomial representations of finite sequences."""


class GeneratingFunctionEngine:
    @staticmethod
    def polynomial(sequence, variable="x"):
        terms = []
        for power, coefficient in enumerate(sequence):
            coefficient = int(coefficient)
            if coefficient == 0:
                continue
            if power == 0:
                term = str(coefficient)
            elif power == 1:
                term = f"{'' if coefficient == 1 else '-' if coefficient == -1 else str(coefficient) + '*'}{variable}"
            else:
                term = f"{'' if coefficient == 1 else '-' if coefficient == -1 else str(coefficient) + '*'}{variable}^{power}"
            terms.append((power, term))
        if not terms:
            return "0"
        expression = terms[0][1]
        for _, term in terms[1:]:
            expression += f" - {term[1:]}" if term.startswith("-") else f" + {term}"
        return expression
