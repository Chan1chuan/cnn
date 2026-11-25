import unittest

from checks import FrameDecoder, elapsed_ticks, saved_register_bytes


class FrameTests(unittest.TestCase):
    wire = b"\x04\x00sync\x02\x00ok"

    def test_split_at_every_boundary(self):
        for split in range(len(self.wire) + 1):
            with self.subTest(split=split):
                decoder = FrameDecoder()
                decoded = decoder.feed(self.wire[:split]) + decoder.feed(self.wire[split:])
                self.assertEqual(decoded, [b"sync", b"ok"])
                decoder.finish()

    def test_one_byte_at_a_time(self):
        decoder = FrameDecoder()
        self.assertEqual([frame for b in self.wire for frame in decoder.feed(bytes([b]))],
                         [b"sync", b"ok"])
        decoder.finish()

    def test_bad_length_resets_decoder(self):
        for header in (b"\x00\x00", b"\x05\x00"):
            decoder = FrameDecoder(max_payload=4)
            with self.assertRaisesRegex(ValueError, "invalid frame length"):
                decoder.feed(header + b"ignored")
            self.assertEqual(decoder.feed(self.wire), [b"sync", b"ok"])

    def test_missing_bytes(self):
        for prefix in (b"\x02", b"\x02\x00x"):
            decoder = FrameDecoder()
            decoder.feed(prefix)
            with self.assertRaisesRegex(ValueError, "truncated"):
                decoder.finish()


class ArithmeticTests(unittest.TestCase):
    def test_counter_rollover(self):
        self.assertEqual(elapsed_ticks(2, 14, bits=4), 4)
        self.assertEqual(elapsed_ticks(14, 2, bits=4, down=False), 4)
        self.assertEqual(elapsed_ticks(100, 20), 80)

    def test_counter_limits(self):
        with self.assertRaises(ValueError):
            elapsed_ticks(16, 0, bits=4)

    def test_saved_registers(self):
        self.assertEqual(saved_register_bytes("s16-s31"), 64)
        self.assertEqual(saved_register_bytes("d8, d9-d10"), 24)

    def test_reject_gaps_duplicates_and_mixed_width(self):
        for text in ("", "d8,d10", "d8,d8", "s0,d0", "s2-s1", "d16"):
            with self.subTest(text=text), self.assertRaises(ValueError):
                saved_register_bytes(text)


if __name__ == "__main__":
    unittest.main()
