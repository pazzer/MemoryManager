# Introducing MemoryManager

This small project explores the mechanics of memory management from the point of view of the operating system. It began 
life as part of the coursework for the *Coursera* course *Nand2Tetris Part 2*, during which students are asked to write
code that ultimately becomes part of a rudimentary operating system called *Hack*.

The coursework required that each student write thir own implementation of the *first-fit* memory allocation algorithm
in a programming language called Jack. I decided to write a Python version of this algorithm first, and then for good
measure, implmented an additional memory defragmentation algorithm. Finally, rather than leave these two functions
as isolated chunks of code I decided to wrap them up in a single ``Memory`` class and create a simulation of the 
process/processes that handle ``alloc`` and ``deAlloc`` calls in a real operating system.

It's worth pointing out that although the memory-management algorithms used here are sound, 
the set-up overall is somewhat fanciful. For example, in real-world systems the processes responsible for managing RAM 
would themselves use that RAM for their own execution. In this set-up by contrast the ``Memory`` object is assumed to 
have access to some separate resource that allows it to operate irrespective of how much or how little space is 
available on its chip. I make no apologies for this short-coming or others like it: ultimately the aim of the project is 
to examine the algorithms involved in memory management, not to create a faithful model of computer memory.

## Exploring the Project

To get to grips with the project, I recommend two approaches: (i) experimenting directly with the ``Memory`` class and 
(ii) probing this class via unittests.

### Probing ``Memory`` Directly

The principal class in this project is the ``Memory`` class, which exposes three key public methods: ``alloc``, 
``deAlloc``, and ``defrag``. You can call these as many times as you like, and in any order. To see how a sequence of 
such calls effects the RAM chip, ``status_report`` provides a comprehensive summary of the ``Memory`` object's internal 
state, including a complete reproduction of the RAM chip's contents.

```
memory = Memory(size=64, heap_ptr=5)
a = memory.alloc(7)
b = memory.alloc(10)
c = memory.alloc(4)
d = memory.alloc(8)
e = memory.alloc(5)
f = memory.alloc(9)

memory.deAlloc(b)
memory.deAlloc(a)
memory.deAlloc(f)

print(memory.status_report())
```

### Probing ``Memory`` with Unittests 

If you want to examine the class in more detail, you should think about doing so through unittests. The current test 
suite  consists of a single class ``TestMemory`` which probes the reliability and predictablity of the methods that make
up the ``Memory`` class, (no attempt to test the effieciency of these methods, though this would be a useful addition). 
To run these tests execute the following command:

```
$ tests/test_memory.py
```

