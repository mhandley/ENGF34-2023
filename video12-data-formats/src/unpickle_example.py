import pickle

with open('data.pickle', 'rb') as infile:
    # The protocol version used is detected automatically, so we do not
    # have to specify it.
    list2 = pickle.load(infile)

print(list2)
