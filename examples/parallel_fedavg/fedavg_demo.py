"""A synthetic, exact-arithmetic example of synchronous FedAvg."""

import argparse
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from fractions import Fraction
from typing import Callable, Sequence

Model = tuple[Fraction, ...]


@dataclass(frozen=True)
class ClientUpdate:
    sample_count: int
    model: Model


Client = Callable[[Model], ClientUpdate]


def aggregate(updates: Sequence[ClientUpdate], width: int) -> Model:
    """Average local models, weighting each by its client's sample count."""
    if not updates:
        raise ValueError("at least one client update is required")
    for update in updates:
        if type(update.sample_count) is not int or update.sample_count < 1:
            raise ValueError("sample count must be a positive integer")
        if len(update.model) != width:
            raise ValueError("client model has the wrong width")
        if any(type(value) not in (int, Fraction) for value in update.model):
            raise ValueError("model components must be exact numbers")
    total = sum(update.sample_count for update in updates)
    return tuple(
        sum(Fraction(update.model[i]) * update.sample_count for update in updates)
        / total
        for i in range(width)
    )


class Server:
    def __init__(self, model: Model):
        self.model = tuple(Fraction(value) for value in model)
        if not self.model:
            raise ValueError("initial model must not be empty")
        self.rounds = 0

    def run_round(self, clients: Sequence[Client], *, parallel: bool) -> Model:
        """Send one shared snapshot and commit only after every client succeeds."""
        snapshot = self.model
        if parallel and clients:
            with ThreadPoolExecutor(max_workers=len(clients)) as executor:
                updates = list(executor.map(lambda client: client(snapshot), clients))
        else:
            updates = [client(snapshot) for client in clients]
        next_model = aggregate(updates, len(snapshot))
        self.model = next_model
        self.rounds += 1
        return next_model


def toy_client(features: Sequence[int]) -> Client:
    """Fit a line with one local gradient step on synthetic y = 2x + 1."""
    samples = tuple((x, 2 * x + 1) for x in features)
    if not samples:
        raise ValueError("a toy client needs at least one sample")

    def train(model: Model) -> ClientUpdate:
        slope, intercept = model
        residuals = [(x, slope * x + intercept - y) for x, y in samples]
        step = Fraction(1, 8 * len(samples))
        return ClientUpdate(
            len(samples),
            (
                slope - step * sum(x * error for x, error in residuals),
                intercept - step * sum(error for _, error in residuals),
            ),
        )

    return train


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rounds", type=int, default=6)
    options = parser.parse_args()
    if options.rounds < 1:
        parser.error("--rounds must be positive")

    clients = (toy_client((-2, -1)), toy_client((0, 1, 2)))
    serial = Server((Fraction(0), Fraction(0)))
    parallel = Server(serial.model)
    for _ in range(options.rounds):
        expected = serial.run_round(clients, parallel=False)
        actual = parallel.run_round(clients, parallel=True)
        if expected != actual:
            raise RuntimeError("serial and parallel models differ")
        print(
            f"Round {serial.rounds:2d}: slope={float(actual[0]):.6f}, "
            f"intercept={float(actual[1]):.6f} (exact match)"
        )


if __name__ == "__main__":
    main()
