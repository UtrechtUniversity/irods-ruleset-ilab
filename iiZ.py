# \brief     Experimental Python rule benchmarking / tracing utility.
# \author    Chris Smeele
# \copyright Copyright (c) 2019 Utrecht University. All rights reserved.
# \license   GPLv3, see LICENSE.

def trace_on():
    """Wrap all toplevel Python functions to print timing information.

       This also visualizes the execution path by indenting trace lines with
       the current stack depth.

       Each line shows a timestamp at execution time, the execution length, and
       the function name. Lines are printed after execution compeletes, so
       nested function calls appear *above* parent functions.
    """
    import inspect
    import time
    from types import FunctionType

    def wrap(fn, name):
        def wrapper(*args, **kwargs):
            depth = len(inspect.stack()) // 2
            x = time.time()
            result = fn(*args, **kwargs)
            y = time.time()
            print('TRACE: [%010.3f]+%4dms %s %s' % (x, int((y-x)*1000), '*'*depth, name))
            return result
        return wrapper
    g = list(filter(lambda (_,x): type(x) is FunctionType, globals().items()))
    for name, fn in g:
        globals()[name] = wrap(fn, name)

# trace_on()
