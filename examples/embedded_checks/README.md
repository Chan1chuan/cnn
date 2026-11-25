# Embedded checks without a board

Three small examples use synthetic inputs to test assumptions before moving to hardware:

- Decode a simple length-prefixed byte stream when bytes arrive in fragments or multiple messages arrive together.
- Compute elapsed ticks for an up- or down-counter that may wrap, assuming less than one full period between readings.
- Count bytes in a contiguous saved floating-point register list. The result covers only those registers, not the whole stack, interrupts, or RTOS context.

From this directory:

```sh
python3 -B -m unittest -v
```

There is no actual serial connection, firmware image, or benchmark measurement in this directory.
