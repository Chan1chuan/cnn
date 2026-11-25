# Embedded systems portfolio

Selected work in embedded machine learning, firmware integration, and hardware measurement, with small examples that can be run without a development board.

| Research project | What I worked on | What I evaluated |
| --- | --- | --- |
| Keyword spotting on MAX78000 | Integrated the CNN execution path with Zephyr and maintained a CPU reference for comparison. | Prediction agreement, inference latency, and board energy for a fixed model. |
| Federated learning across microcontrollers | Ported the training workflow to Zephyr and adapted it across Portenta H7, Thingy:53, and MAX78000. | Local training, host aggregation, and reliable transfer of samples and model state between devices. |
| Accelerator-assisted federated workflow | Integrated accelerator-backed evaluation with CPU-based local training on MAX78000. | End-to-end workflow time separately from the accelerator's compute time, with consistent timing and energy boundaries. |
| Quantized on-device training | Worked on CPU and accelerator execution paths for a fixed CNN engine. | Operator reference checks, learning-state agreement, and matched runtime and energy measurements. |
| Parallel multi-board training | Worked on host-side coordination, round barriers, and aggregation for multiple embedded clients. | Checked results across serial and parallel schedules and separated communication from device work. |

## Run the examples

These are independent demonstrations of general techniques, rather than the research firmware or a reproduction of the research results. All inputs are synthetic.

| Example | What to try |
| --- | --- |
| [Energy-window analysis](examples/energy_window/) | Integrate a power trace over a selected time range and check the boundaries. |
| [Parallel federated averaging](examples/parallel_fedavg/) | Run synthetic clients in serial and parallel and compare the resulting global state. |
| [Keyword metadata audit](examples/keyword_metadata/) | Count exact keyword matches and check a speaker-aware selection on a synthetic corpus. |
| [Embedded checks](examples/embedded_checks/) | Exercise fragmented message framing, counter rollover, and local stack-size arithmetic. |

```sh
python3 -B run_tests.py
```

See [project and release scope](PROJECTS.md) for how the demonstrations relate to the research.
