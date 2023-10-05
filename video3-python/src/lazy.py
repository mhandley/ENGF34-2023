
x = 0
y = 3

# although y // x would normally be an error, python's lazy evaluation
# means that the error is avoided.  The "x != 0" clause will mean the
# "and" expression will always be false.  Python is lazy in evaluating
# logic expressions, so does not bother to calculate y // x, so there
# is no error.

if x != 0 and y // x > 2:
    print("Hello")

x = 1
if x != 0 and y // x > 2:
    print("World")
    
