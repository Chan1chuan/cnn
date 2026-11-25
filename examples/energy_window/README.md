# Energy window from CSV power samples

This standalone example computes energy and average power for a requested
interval. It uses only the Python 3 standard library and works with the
synthetic CSV in this directory; no power monitor or board is needed.

From the repository root:

```sh
python3 examples/energy_window/energy_window.py examples/energy_window/synthetic_power.csv --start-s 0.5 --end-s 2.5
python3 -B -m unittest discover -s examples/energy_window -p 'test_*.py'
```

The sample window yields **92.5 mJ** over **2 s**, or **46.25 mW** on average.
The CSV must provide `time_s` (seconds) and `power_mw` (milliwatts).
Rename columns and convert units before analyzing a different format.

The tool clips each adjacent sample pair to the window, linearly interpolates
power at the clipped endpoints, and sums the trapezoid areas. Timestamps must
be strictly increasing, samples must be finite, and the window must fit within
the measured span. Nonuniform spacing is allowed. Negative power is preserved,
so the result is signed energy. The tool does not infer missing samples,
detect hardware events, or correct instrument drift.

This demonstration does not include instrument recordings, firmware, or
laboratory measurement scripts.
