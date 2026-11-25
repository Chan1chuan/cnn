# Project and release scope

## Research work

- **MAX78000 keyword spotting and benchmarking.** Compared fixed-model inference on an MCU CPU and its CNN engine. Evaluated latency and board energy separately from end-to-end workflow timing.
- **Zephyr board ports.** Worked on federated keyword spotting across Portenta H7, Thingy:53, and MAX78000. The engineering work included transport, sample or feature handling, and target memory limits.
- **Quantized training on an inference-oriented accelerator.** Worked on executing convolutional operations and maintaining training state on a resource-constrained MCU. Used numerical reference checks and matched experimental conditions for CPU and accelerator implementations.
- **Multi-board coordination.** Worked on independent client execution, a round boundary for aggregation, and state checks before the next round. Evaluated orchestration separately from changes to the learning algorithm.

## What the repository provides

The examples are standalone demonstrations written around generic problems and synthetic inputs. They do not load real audio, model weights, or board hardware, and their outputs are not the research measurements.

- Energy integration illustrates how a result depends on the selected measurement window and units.
- The federated averaging example illustrates round coordination and serial/parallel result agreement. It does not train a neural network on an MCU.
- Metadata selection illustrates keyword and speaker handling without redistribution of a speech dataset.
- Embedded checks illustrate testing a protocol with byte streams and computing counter deltas and saved-register sizes without a target.

The original research repositories, paper reproduction package, hardware-specific source, vendor-generated code and binaries, and experiment records are not distributed here. Access to those artifacts is governed by their respective projects.
