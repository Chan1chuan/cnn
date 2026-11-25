# Synchronous FedAvg with parallel clients

This standalone Python example runs two synthetic linear-regression clients in
serial and in parallel. Each round starts from the same immutable global model,
then averages the returned models by sample count after all clients finish.
A failed or invalid update leaves the previous global model and round number
unchanged. Client side effects are outside the coordinator's control.

From this directory, with Python 3.9 or newer and no additional dependencies:

```sh
python3 fedavg_demo.py
python3 -m unittest -v
```

The demo compares both modes after every round using exact fractions. A test
uses a thread barrier to verify that both client calls can be active together.
This illustrates coordination for independent device or I/O calls, not a
speedup benchmark for CPU-bound Python. There is no firmware, device protocol,
hardware access, or real training data in this example.
