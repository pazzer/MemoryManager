#!/Library/Frameworks/Python.framework/Versions/3.4/bin/python3.4
# -*- coding utf-8 -*-

__author__ = 'paulpatterson'

""" A test class to be used in conjunction with memory.py """

import sys
import os.path
from collections import namedtuple

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

    def memory_with_string(self, memory_string):
        """ Generates a Memory instance whose RAM contents matches the pattern decsribed by memory_string.

        This is a convenience method, allowing the quick and easy creation of Memory instances with a specific RAM
        layout.

        :param memory_string: A typical memory_string is provided at the bottom of this paragraph. Each string should
        begin with a run of N's - one for each register in the stack; the example below specifies that the Memory
        object created from this string should have a stack size of 5. A space should follow the last 'N' and we now
        start describing the heap's layout. The heap is divided into segments each of which has the same structure:
        the first value in a segment conveys whether or not the segment is allocated. If it is allocated, it should have
        the value -100, otherwise the number should be either (i) the address of another unallocated segment elsewhere
        in the RAM, or '-1' - denoting that this segment sits at the end of the free list. Combined, the various
        addresses held by each free segment comprise a linked list, that ultimately provides access to every unallocated
        segment. You do not have specify which segment occupies first place in this list, but it is up to you to ensure
        that such a list can be derived. The second value in a segment describes its width. The minimum allowable width
        is 3 - one register to store the 'next' pointer, one to store the width, and one data register that can be used
        by a client - and the maximum is a function of the overall size of the RAM and the size of the stack. The
        remaining values in a segment can take whatever value you please, though by convention 'x's denote that a given
        register is part of an allocated block of memory (and therefore unavailable), whereas '✔'s denote the opposite.

            sample_memory_string = "NNNNN -100 7 ✗ ✗ ✗ ✗ ✗ -1 8 ✔ ✔ ✔ ✔ ✔ ✔ -100 5 ✗ ✗ ✗ 12 7 ✔ ✔ ✔ ✔ ✔"

        :return: A Memory instance with a RAM chip with a pattern of fragmentation that exactly matches that described
        by memory_string.
        """
        heap_ptr = memory_string.find(" ")
        ram = [None] * heap_ptr + memory_string.split(" ")[1:]

        memory = Memory(size=len(ram), heap_ptr=heap_ptr)

        # Figure out the order of allocations
        free_segments = []
        location = heap_ptr
        allocs = []
        while location < len(ram):
            ptr = int(ram[location])
            alloc_size = int(ram[location + 1]) - 2
            allocs.insert(0, alloc_size)
            if ptr != -100:
                free_segments.append(location)
            location += alloc_size + 2

        # Execute the allocations
        for size in allocs:
            _ = memory.alloc(size)

        # deduce free, and run the required deallocations
        for index in free_segments:
            location = index
            free_list = []
            while int(ram[location]) != -1:
                free_list.insert(0, location)
                location = int(ram[location])
            free_list.insert(0, location)

            if len(free_list) == len(free_segments):
                # index is memory._free
                for segment in free_list:
                    memory.deAlloc(segment + 2)
                break

        assert "{:short}".format(memory) == memory_string, "Failed to create memory from '{}'".format(memory_string)
        return memory


    # Defragmentation

    def test_defrag_possible_a(self):
        """ Examines result of memory.defrag() on a RAM chip that can be defragmentated. """
        before_defrag = "NNNNN -100 3 ✗ 20 3 ✔ 29 3 ✔ 8 3 ✔ -100 3 ✗ 11 3 ✔ -100 3 ✗ -1 3 ✔ 26 3 ✔"
        after_defrag  = "NNNNN -100 3 ✗ 20 9 ✔ ✔ ✔ ✔ ✔ ✔ ✔ -100 3 ✗ 26 3 ✔ -100 3 ✗ -1 6 ✔ ✔ ✔ ✔"
        memory = self.memory_with_string(before_defrag)
        memory.defrag()
        self.assertEqual("{:short}".format(memory), after_defrag)
        self.assertEqual(memory._free, 8)

    def test_defrag_possible_b(self):
        """ Examines result of memory.defrag() on a RAM chip that can be defragmentated. """
        before_defrag = "NNNNN -100 4 ✗ ✗ 19 5 ✔ ✔ ✔ 9 5 ✔ ✔ ✔ -1 10 ✔ ✔ ✔ ✔ ✔ ✔ ✔ ✔ -100 3 ✗"
        after_defrag =  "NNNNN -100 4 ✗ ✗ -1 20 ✔ ✔ ✔ ✔ ✔ ✔ ✔ ✔ ✔ ✔ ✔ ✔ ✔ ✔ ✔ ✔ ✔ ✔ -100 3 ✗"
        memory = self.memory_with_string(before_defrag)
        self.assertEqual(memory._free, 14)
        self.assertIsNone(memory.alloc(15))
        memory.defrag()
        self.assertEqual("{:short}".format(memory), after_defrag)
        self.assertEqual(memory._free, 9)
        self.assertIsNotNone(memory.alloc(15))

    def test_defrag_not_possible_a(self):
        """ Examines result of memory.defrag() on a RAM chip that can NOT be defragmentated. """
        before_defrag = "NNNNN -100 3 ✗ -100 3 ✗ -100 3 ✗ -100 3 ✗ -100 3 ✗ -100 3 ✗ -100 3 ✗ -100 3 ✗ -100 3 ✗"
        after_defrag = before_defrag
        memory = self.memory_with_string(before_defrag)
        memory.defrag()
        self.assertEqual("{:short}".format(memory), after_defrag)
        self.assertEqual(memory._free, -1)

    def test_defrag_not_possible_b(self):
        """ Examines result of memory.defrag() on a RAM chip that can NOT be defragmentated. """
        before_defrag = "NNNNN -100 7 ✗ ✗ ✗ ✗ ✗ -1 8 ✔ ✔ ✔ ✔ ✔ ✔ -100 5 ✗ ✗ ✗ 12 7 ✔ ✔ ✔ ✔ ✔"
        after_defrag =  "NNNNN -100 7 ✗ ✗ ✗ ✗ ✗ 25 8 ✔ ✔ ✔ ✔ ✔ ✔ -100 5 ✗ ✗ ✗ -1 7 ✔ ✔ ✔ ✔ ✔"
        memory = self.memory_with_string(before_defrag)
        self.assertEqual(memory._free, 25)
        memory.defrag()
        self.assertEqual("{:short}".format(memory), after_defrag)
        self.assertEqual(memory._free, 12)

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
