import unittest
from fractions import Fraction
from threading import Barrier

from fedavg_demo import ClientUpdate, Server, aggregate, toy_client


class FedAvgTest(unittest.TestCase):
    def test_weighted_mean(self):
        updates = (
            ClientUpdate(1, (Fraction(1), Fraction(0))),
            ClientUpdate(3, (Fraction(0), Fraction(2))),
        )
        self.assertEqual(aggregate(updates, 2), (Fraction(1, 4), Fraction(3, 2)))

    def test_serial_and_parallel_match_each_round(self):
        clients = (toy_client((-2, -1)), toy_client((0, 1, 2)))
        serial = Server((Fraction(0), Fraction(0)))
        parallel = Server(serial.model)
        for _ in range(8):
            self.assertEqual(
                serial.run_round(clients, parallel=False),
                parallel.run_round(clients, parallel=True),
            )

    def test_clients_overlap_and_share_snapshot(self):
        server = Server((Fraction(2),))
        snapshot = server.model
        rendezvous = Barrier(2, timeout=5)

        def client(model):
            self.assertIs(model, snapshot)
            rendezvous.wait()
            self.assertIs(server.model, snapshot)
            return ClientUpdate(1, (model[0] + 1,))

        self.assertEqual(
            server.run_round((client, client), parallel=True), (Fraction(3),)
        )
        self.assertEqual(server.rounds, 1)

    def test_failed_or_invalid_update_preserves_previous_round(self):
        def good(model):
            return ClientUpdate(1, (model[0] + 1,))

        def failed(_):
            raise RuntimeError("simulated client failure")

        def wrong_width(_):
            return ClientUpdate(1, ())

        def wrong_count(model):
            return ClientUpdate(0, model)

        for parallel in (False, True):
            for bad, error in (
                (failed, RuntimeError),
                (wrong_width, ValueError),
                (wrong_count, ValueError),
            ):
                with self.subTest(parallel=parallel, client=bad.__name__):
                    server = Server((Fraction(2),))
                    previous = server.run_round((good,), parallel=parallel)
                    with self.assertRaises(error):
                        server.run_round((good, bad), parallel=parallel)
                    self.assertIs(server.model, previous)
                    self.assertEqual(server.rounds, 1)


if __name__ == "__main__":
    unittest.main()
