from .algorithms.grover import build_grover_circuit


_ALGORITHMS = {
    "grover": build_grover_circuit,
}


def get_algorithm(name: str):
    algorithm = _ALGORITHMS.get(name.lower())

    if algorithm is None:
        raise NotImplementedError(
            f"Algorithm '{name}' is not supported."
        )

    return algorithm