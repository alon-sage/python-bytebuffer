# encoding: UTF-8

from unittest import TestCase


class ByteBufferTestCase(TestCase):
    def test_bytearray(self):
        a = bytearray(b'aa')
        b = a[:]
        b[1] = ord('b')

        self.assertEqual(a, b'aa')
        self.assertEqual(b, b'ab')