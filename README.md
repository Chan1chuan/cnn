# Embedded systems portfolio

Selected projects in embedded machine learning, firmware integration, and hardware measurement. This index describes the work; it does not redistribute code or data held in institutional repositories.

| Project | What I worked on | What I evaluated |
| --- | --- | --- |
| Keyword spotting on MAX78000 | Integrated the CNN execution path with Zephyr and maintained a CPU reference for comparison. | Prediction agreement, inference latency, and board energy for a fixed model. |
| Federated learning across microcontrollers | Ported the training workflow to Zephyr and adapted it across Portenta H7, Thingy:53, and MAX78000. | Local training, host aggregation, and reliable transfer of samples and model state between devices. |
| Accelerator-assisted federated workflow | Integrated accelerator-backed evaluation with CPU-based local training on MAX78000. | End-to-end workflow time separately from the accelerator's compute time, with consistent timing and energy boundaries. |
| Host-side test and measurement tooling | Built automation for firmware/host integration, serial experiments, and repeatable result checks. | Compared outputs at defined checkpoints and separated compute, transport, and host overhead. |

## Repositories and artifacts

The thesis reproduction packages and the board-port code are kept in the existing institutional repositories. Source access follows the permissions on those projects. This index contains no datasets, model weights, measurement traces, or unpublished paper artifacts.
