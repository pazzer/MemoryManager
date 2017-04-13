# Introduction
This small project was created to explore the three memory allocation algorithms discussed in *The Elements of a 
Computing System - Building a Computer From First Principles* (Nisan and Schocken). The first of the three algorithms -
**first-fit** has been implemented, but the remaining two - *best-fit* and *defrag* - are still outstanding. 

# Exploring the Project
The project consists of just two files: ``memory.py`` and ``test_memory.py``. The latter of these two is used to put
the former through its paces. To do this run the following command:
 
    $ python /path/to/tests/test_memory.py


## TODO
1. Implement the ``defrag`` stub method in the ``Memory`` class.
2. Create a separate branch (named *BestFit*) and reimplment ``alloc`` so that it allocates memory according
to the *best-fit* algorithm.