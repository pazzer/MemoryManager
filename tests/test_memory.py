#!/Library/Frameworks/Python.framework/Versions/3.4/bin/python3.4
# -*- coding utf-8 -*-

__author__ = 'paulpatterson'

""" A test class to be used in conjunction with memory.py """

import sys
import os.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
import random
from source.memory import Memory
from pathlib import Path

LOG_PATH = Path(os.path.dirname(__file__)) / "log.txt"


class TestMemory(unittest.TestCase):

    def setUp(self):
        """ Sets up a Memory object which will manage a ram-chip 64 registers long. """
        self.memory = Memory(size=64, heap_ptr=5)

    def write_memory_log(self):
        with open(LOG_PATH.as_posix(), "w") as lf:
            lf.write(self.memory.log)

    # Tests

    def test_startup(self):
        """ Is the ram-chip set up correctly? """
        self.assertEqual(self.memory._peek(5), -1)
        self.assertEqual(self.memory._peek(6), 59)
        self.assertEqual(self.memory.stack_size, 5)
        self.assertEqual(self.memory.heap_size, 59)

    def test_simple_alloc(self):
        """ A simple allocation request. """
        size = 15
        ptr = self.memory.alloc(size)
        self.assertEqual(ptr, 49)
        self.assertEqual(self.memory._peek(47), -100)
        self.assertEqual(self.memory._peek(48), size + 2)
        self.memory.needs_repairs()

    def test_simple_dealloc(self):
        """ A simple deallocation request. """
        _ = self.memory.alloc(15)
        ptr_b = self.memory.alloc(8)
        self.assertEqual(ptr_b, 39)
        self.assertEqual(self.memory._peek(38), 10)
        self.assertEqual(self.memory._free, 5)
        self.memory.deAlloc(ptr_b)
        self.assertEqual(self.memory._free, 37)
        self.assertEqual(self.memory._free_list, [37, 5])

    def test_alloc_size_too_big(self):
        """ Requesting allocation of a chunk of memory that exceeds the size of the ram-chip. """
        self.assertIsNone(self.memory.alloc(65))

    def test_read_segment(self):
        """ Reading the contents of a specific part of the ram-chip """
        ptr = self.memory.alloc(15)
        seg_data = self.memory._read_segment(ptr - 2)
        self.assertEqual(seg_data, ["✗"] * 15)

    def test_write_segment(self):
        """ Writing to a specific part of the ram-chip """
        ptr = self.memory.alloc(15)
        self.memory._write_segment(ptr - 2, "a")
        self.assertEqual(self.memory._read_segment(ptr - 2), ["a"] * 15)

    def test_memory_full(self):
        """ What happens when all registers have been allocated? """
        self.memory.alloc(20)
        self.memory.alloc(20)
        self.memory.alloc(13)
        self.memory.alloc(10)
        self.assertEqual(len(self.memory._free_list), 0)
        self.assertEqual(self.memory._free, -1)

    def test_random_alloc_dealloc(self):
        """ Executes a random assotment of fifty alloc and deAlloc calls, then checks whether or not the ram-chip is in
        a consistent state. Does this two-hundred times. """
        iterations_counter = 0
        ops_counter = 0
        allocated = []
        ops = ["alloc", "alloc", "deAlloc"]

        while iterations_counter < 200:

            try:
                while ops_counter < 50:
                    choice = random.choice(ops)
                    if choice == "alloc":
                        size = random.randrange(1, 8)
                        ptr = self.memory.alloc(size)
                        if ptr is not None:
                            allocated.append(ptr)
                        ops_counter += 1
                    else:
                        if len(allocated) > 0:
                            index = random.randrange(0, len(allocated))
                            ptr = allocated[index]
                            self.memory.deAlloc(ptr)
                            allocated.pop(index)
                            ops_counter += 1

                problem = self.memory.needs_repairs(LOG_PATH)
                if problem:
                    self.write_memory_log()
                    self.assertFalse(problem,
                        "Test failed - 'needs_repairs' == True. See log for the operations that led to this failure.")
                    return
                else:
                    self.assertFalse(problem)

            except Exception as e:
                self.write_memory_log()
                self.assertFalse(True, \
                    "Test failed with exception '{}'. See log for the operations that led to this exception.".format(e))
                return

            iterations_counter += 1


if __name__ == '__main__':
    unittest.main()
