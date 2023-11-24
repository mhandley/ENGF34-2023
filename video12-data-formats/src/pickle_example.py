import pickle

list1 = [1,2,3,4,5]
list2 = ["Hello", "World"]
list3 = [list1, list2, list1, list2]

print(list3)

with open('data.pickle', 'wb') as outfile:
    pickle.dump(list3, outfile, 1)
    
