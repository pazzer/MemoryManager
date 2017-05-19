# Introducing MemoryManager

This small project explores the mechanics of memory management from the point of view of the operating system. The 
principal class - ``Memory`` - is the guardian of a single RAM chip, and as such is responsible for handling ``alloc`` 
and ``deAlloc`` requests as they arrive, and for keeping the chip in a consistent state.

The project began life as part of the coursework for the *Coursera* course *Nand2Tetris Part 2*, during which students 
are asked to implement one of two memory allocation algorithms (*first-fit* or *best-fit*) in a simple programming 
language called Jack. I decided to write a Python version of the first of these two algorithms to get a feel for how to 
implement them in Jack, and then, for good measure, implemented an additional memory defragmentation algorithm. 

It's worth pointing out that although the algorithms are sound, the set-up overall is somewhat fanciful. For example, 
in real-world systems the processes responsible for managing RAM would themselves use that RAM for their own 
execution. In this set-up by contrast the ``Memory`` object is assumed to have access to some separate resource that 
allows it to operate irrespective of how much or how little space is available on its chip. I make no apologies for this 
short-coming or others like it: ultimately the aim of the project is to examine the algorithms involved in memory 
management not to create a faithful model of computer memory.


## Exploring the Project
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

If you want to examine the class in more detail, you should think about adding more unittests. The current test suite 
consists of a single class ``TestMemory`` which probes the reliability and predictablity of the methods that make up the 
``Memory`` class, (no attempt to test the effieciency of these methods, though this would be a useful addition). To run 
these tests MORE HERE