
def quicksort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    print("left: ", left)
    print("middle: ", middle)
    print("right: ", right)
    return quicksort(left) + middle + quicksort(right)

n = 10
print('--------A--------')
A = [1 for i in range(n)]
print(quicksort(A))
print('-----------------')
print('--------B--------')
B = [i for i in range(n)] 
print(quicksort(B))
print('-----------------')
print('--------C--------')
C = [(n - i) % 3 for i in range(n)]
print(quicksort(C))
print('-----------------')
print('--------D--------')
D = [i + 5 if i % 2 == 1 else n - 5 - i for i in range(n)]
print(quicksort(D))