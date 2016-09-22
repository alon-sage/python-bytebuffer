# encoding: UTF-8

from __future__ import print_function, unicode_literals

import math
import sys
import time

from bytebuffer import ByteBuffer


class PerformanceTest(object):
    def __init__(self, start, end, scale_factor, tl):
        self.start = start
        self.end = end
        self.scale_factor = scale_factor
        self.tl = tl

    def range(self, a):
        if sys.version_info[0] == 3:
            return range(a)
        else:
            return xrange(a)

    def _warm_up(self, fn, args, kwargs):
        fn(*args, **kwargs)

    def _do_test(self, count, fn, args, kwargs):
        started_at = time.time()
        for _ in self.range(count):
            fn(*args, **kwargs)
        estimate = time.time() - started_at

        cumulative = 0
        for _ in self.range(count):
            started_at = time.time()
            fn(*args, **kwargs)
            cumulative += time.time() - started_at

        return estimate, cumulative, estimate > self.tl or cumulative > self.tl

    def run(self, fn, *args, **kwargs):
        self._warm_up(fn, args, kwargs)

        result_set = []
        iteration = 1
        count = self.start
        while count <= self.end:
            int_count = int(math.ceil(count))
            estimate, cumulative, tl_exceeded = self._do_test(
                int_count, fn, args, kwargs)

            result_set.append((iteration, int_count, estimate, cumulative))

            if tl_exceeded:
                break

            if count == self.end:
                break

            iteration += 1
            count = min(count * self.scale_factor, self.end)

        return result_set

    def run_and_print(self, fn, *args, **kwargs):
        rs = self.run(fn, *args, **kwargs)

        fname = fn.__module__ + '.' + fn.__name__

        print('=' * 80)
        print('Function: {}'.format(fname))
        print('Performance test: {:d} -> {:d}, scale_factor={:.3f}, tl={:.3f}'.format(
            self.start, self.end, self.scale_factor, self.tl
        ))
        print('-' * 80)
        print(' {:>3} | {:^8} | {:^13} | {:^29} | {:^13} '.format(
            '', '', '', 'time', ''
        ))
        print('-' * 80)
        print(' {:>3} | {:^8} | {:^13} | {:^13} | {:^13} | {:^13} '.format(
            '#', 'count', 'metric', 'total', 'per op.', 'speed'
        ))
        for iteration, count, estimate, cumulative in rs:
            print('-' * 80)
            print(' {:>3d} | {:>8d} | {:>13} | {:>13.9f} | {:>13.9f} | {:>13.3f} '.format(
                iteration, count, "estimate", estimate, estimate / count, count / estimate,
            ))
            print(' {:>3} | {:>8} | {:>13} | {:>13.9f} | {:>13.9f} | {:>13.3f} '.format(
                "", "", "cumulative", cumulative, cumulative / count, count / cumulative
            ))
        print('=' * 80)
        print()
        print()


test = PerformanceTest(10 ** 3, 10 ** 5, 10, 10.0)
buf = ByteBuffer.allocate(5 * 10 ** 8)

for name in dir(buf):
    if name.startswith("get_"):
        suffix = name.replace("get_", "")

        if suffix in ("capacity", "position", "limit", "remaining", "bytes"):
            continue

        putter = getattr(buf, "put_" + suffix)
        getter = getattr(buf, name)
        buf.clear()
        test.run_and_print(putter, 1)
        buf.flip()
        test.run_and_print(getter)

data = bytearray(b'1' * 8)
buf.clear()
test.run_and_print(buf.put, data)
buf.flip()
test.run_and_print(buf.get, data)

buf.clear()
test.run(buf.put, data)
buf.flip()
test.run_and_print(buf.get_bytes, 8)

from construct import ULInt64

test.run_and_print(ULInt64(str("item")).build, 1)
test.run_and_print(ULInt64(str("item")).parse, b'\x01\x00\x00\x00\x00\x00\x00\x00')
