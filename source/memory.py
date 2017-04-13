#!/Library/Frameworks/Python.framework/Versions/3.4/bin/python3.4
# -*- coding utf-8 -*-

__author__ = 'paulpatterson'

"""
The following class has been created to explor memory allocation algorithms, notably: first-fit, best-fit,
and defrag (only the first of these is currently implemented). It was inspired by a lecture presented in Schocken and
Nissan's Nand2Tetris course (see 'The Elements of a Computing System - Building a Computer From First Principles'). The
class is best used in conjuction with the associated testing file (test_memory.py), which allows you to put your
algorithm implmentations to the test.
"""

from collections import namedtuple
from pathlib import Path
import os.path

Alloc = namedtuple("Alloc", "size addr")
Dealloc = namedtuple("Dealloc", "addr")

TICK = "✔"
CROSS = "✗"

class Memory:
    """ This class is a crude simulation of an OS-level object charged with managing a RAM chip. Once
    the Memory instance has been initialized, client objects interact with it via its two public methods: alloc
    and deAlloc. The former returns an integer, analagous to a memory address, that points to a segment of memory
    that has been reserved for the caller; the latter returns previosuly reserved memory to the pool of 'free'
    memory, ready for resuse. """

    def __init__(self, size, heap_ptr):
        """ Creates an object that manages a RAM unit `size` registers large.

        'Under the hood' the ram chip is modelled as a list, where len(list) == `size`. Each item in the list represents
        a register, and the index referring to a given list item can be thought of as a register's 'address'. Wherever
        possible, all subsequent docstrings use the language of the abstraction, rather than the language of the
        implementation. That is, 'ram', 'address', 'register contents', etc are preferred over 'list', 'list index',
        'list value', etc

        :param size: the total size of the ram chip managed by this object.
        :param heap_ptr: an address specifying the point on the ram chip at which the heap starts. All addresses below
        this value are considered to be stack addresses.
        """
        self._ram = [None for i in range(0, size)]

        self._ram[heap_ptr] = -1
        self._ram[heap_ptr + 1] = len(self._ram) - heap_ptr

        self._heap_ptr = heap_ptr
        self._free = heap_ptr
        self._write_segment(self._free, "✔")
        self._log = []

    def alloc(self, size):
        """ Uses the first-fit algorithm to find a run of unallocated memory that is at least as big as `size`.

        This implementation of alloc walks the free_list looking for the first segment large enough to service this
        request. If a segment is large enough, it is split in order to create a new segment. The returned pointer
        points to a block of memory exactly `size` registers long, and the pre-existing segment is guaranteed to be no
        smaller than 3 registers long (two book-keeping registers, one data-register). If a segment is large enough to
        service the request, but not large enough to be split, the whole segment is effectively allocated to the client.
        If the free_list contains no segment where either of the above is possible, the allocation request fails.

        :param size: the size of the memory block required by the client.
        :return: a pointer to the first register in the allocated memory, or None if the request can be met.
        """
        if self._free == -1:
            self._log.insert(0, Alloc(size, None))
            return None  # ram full!

        seg_base = self._free
        previous_seg_base = None

        while True:
            total_segment_size = self._ram[seg_base + 1]

            if size < (total_segment_size - 4):
                # Split the segment, and return the 'second half' of the split
                self._ram[seg_base + 1] = total_segment_size - 2 - size
                new_seg_base = seg_base + total_segment_size - 2 - size
                self._ram[new_seg_base] = -100
                self._ram[new_seg_base + 1] = size + 2
                self._write_segment(new_seg_base, CROSS)
                self._log.insert(0, Alloc(size, new_seg_base + 2))
                return new_seg_base + 2

            if size < (total_segment_size - 1):
                # Return the whole segment (modify the free list first)
                if seg_base == self._free:
                    # Removing first link
                    self._free = self._ram[self._free]
                elif self._ram[seg_base] == -1:
                    # Removing last link
                    self._ram[previous_seg_base] = -1
                else:
                    # Removing middle link
                    self._ram[previous_seg_base] = self._ram[seg_base]

                self._ram[seg_base] = -100
                self._write_segment(seg_base, CROSS)
                self._log.insert(0, Alloc(size, seg_base + 2))
                return seg_base + 2

            if self._ram[seg_base] == -1:
                self._log.insert(0, Alloc(size, -1))
                return
            else:
                previous_seg_base = seg_base
                seg_base = self._ram[seg_base]

    def deAlloc(self, addr):
        """ Releases a block of previously allocated memory.

        :param addr: A memory address pointing to the start of a segment of previously allocated memory.
        """
        self._ram[addr- 2] = self._free
        self._free = addr - 2
        self._write_segment(self._free, TICK)
        self._log.insert(0, Dealloc(addr))

    def defrag(self):
        """ Not Yet Implemented """
        pass

    def _peek(self, addr):
        """ Returns the value stored in the register referenced by `addr`.

        :param addr: a memory address
        :return: the value stored in the register referenced by `addr`
        """
        return self._ram[addr]

    def _poke(self, addr, value):
        """ Writes the given value into the register referenced by `addr`.

        :param addr: a memory address
        :param value: any value
        """
        self._ram[addr] = value

    def _read_segment(self, seg_base):
        """ Returns the values stored in the user-accessible registers in the segment addressed by seg_base.

        The first two values of each segment are used for internal book-keeping; these are not included in the return
        value.

        :param seg_base: an address pointing to the start of a memory segment.
        :return: all of the values (in list format) of the user-accessible registers in the specified segment.
        """
        segment_size = self._ram[seg_base + 1]
        return self._ram[seg_base + 2: seg_base + segment_size]

    def _write_segment(self, seg_base, value):
        """ Writes `value` into all of the user-accessible registers in the segment addressed by seg_base

        The first two register of each segment are used for internal book-keeping; the contents of these registers
        is not affected by this operation.

        :param seg_base:
        :param value:
        """
        available_size = self._ram[seg_base + 1] - 2
        for i in range(0, available_size):
            self._ram[seg_base + 2 + i] = value

    @property
    def _free_list(self):
        """ A list of memory addresses corresponding to unallocated segments of memory.

        A memory segment consists of a run of contiguous memory registers not smaller than three registers long. If a
        segment is part of the free list (that is, it has not been allocated) the first register stores the base address
        of the next free segment (see below), otherwise it has a placeholder value (-100). Regardless of whether a
        segment is part of the free-list or not, the second register stores the total size of the segment. All of the
        subsequent registers in the segment are 'data-registers' - registers that can be made available via alloc.

        In the following list [29, 43, 40, 54] the segment starting at address 29 is the first 'free' segment.
        The base address of the next free segment is stored in register 29 - in this case its 43. In turn, register
        43 stores the address of the next free segment (40).

        :return: a list of memory addresses corresponding to unallocated segments of memory.
        """
        if self._free == -1:
            return []
        else:
            locations = [self._free]
            nxt = self._ram[self._free]
            while nxt != -1:
                locations.append(nxt)
                nxt = self._ram[nxt]
            return locations

    @property
    def heap_size(self):
        """ The size of the heap section of the memory unit. """
        return len(self._ram) - self.stack_size

    @property
    def stack_size(self):
        """ The size of the stack section of the memory unit. """
        return self._heap_ptr

    @property
    def log(self):
        """ A string containing the details of all received alloc and deAlloc calls. """
        report = "ALLOCATIONS LOG\n---------------\n"
        for (i, entry) in enumerate(self._log):
            timing = len(self._log) - i
            if len(entry) == 1:
                report += "{}.\t\tdeAlloc({})\n".format(timing, entry.addr)
            else:
                report += "{}.\t\talloc({}) -> {}\n".format(timing, entry.size, entry.addr)
        return report


    def needs_repairs(self, report_path=None):
        """ Determines whether or not the ram-chip is in a consistent state.

        Comprises the following checks:
        1. Does the total number of allocated segments, added to the total number of unallocated segments, added to the
         size of the stack, total the size of the chip?
        2. Is every 'free' memory segment referenced in the free_list?
        3. Do all identifiable memory segments have the expected structure (see free_list)

        :param report_path: a Path object referencing a file to which the generated repairs log can be written. If no
        path is provided no report is created.
        :return: True if any one of the three consistency checks fails, False otherwise (indicating a healthy chip).
        """
        malformed_segments = False
        malformed_free_list = None
        bad_register_count = None

        indexes_of_numbers = [i for i in range(0, len(self._ram)) if isinstance(self._ram[i], int)]

        indexes_of_unallocated_segments = []
        indexes_of_allocated_segments = []
        unallocated_register_count = 0  # Number of registers in all unallocated segments (inc. 'book-keeping')
        allocated_register_count = 0    # Number of registers in all allocated segments (inc. 'book-keeping')

        for i in range(0, len(indexes_of_numbers), 2):
            index = indexes_of_numbers[i]
            if indexes_of_numbers[i+1] != index + 1 and malformed_segments is False:
                malformed_segments = True
                break

            nxt = self._ram[index]
            seg_size = self._ram[index + 1]

            if nxt == -100:
                allocated_register_count += seg_size
                indexes_of_allocated_segments.append(index)
            else:
                unallocated_register_count += seg_size
                indexes_of_unallocated_segments.append(index)

        # Checks
        bad_register_count = unallocated_register_count + allocated_register_count + self.stack_size != len(self._ram)
        malformed_free_list = sorted(self._free_list) != indexes_of_unallocated_segments

        # Report (if requested)
        if report_path is not None:
            with open(report_path.as_posix(), "w+") as logfile:
                div = "-" * 45
                report = "- - - - - - - \nMEMORY REPORT\n- - - - - - - \n\n"
                report += "RAM (✗ = allocated, ✔ = free) \n{}\n{}\n\n{}\n".format(div, self, self.log)
                report += "FAULTS\n{}\n".format(div)
                report += "Any Malformed segments?    {}\n".format("YES" if malformed_segments else "NO")
                report += "Unexpected register count? {}\n".format("YES" if bad_register_count else "NO")
                report += "Malformed free list?       {}\n".format("YES" if malformed_free_list else "NO")
                report += "\nFREE LIST\n{}\n".format(div)
                report += " -> ".join([str(i) for i in self._free_list])
                logfile.write(report)

        return malformed_segments | bad_register_count | malformed_free_list

    def __str__(self):
        """ A string representation of the contents of the entire memory unit. """
        lines = [""] * 16
        for (register, value) in enumerate(self._ram):
            lines[register % 16] += "{:5}{:10}".format(str(register), str(value))
        return "\n".join(lines)


if __name__ == "__main__":
    # Sample use #
    memory = Memory(size=128, heap_ptr=5)
    addr = memory.alloc(5)
    _ = memory.alloc(23)
    memory.deAlloc(addr)

    proj_dir = Path(os.path.dirname(__file__)).parent
    print("Repairs needed: {}".format(memory.needs_repairs(proj_dir / "tests" / "log.txt") == True))













