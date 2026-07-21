n = int(input("Enter the value of n : "))
for i in range(1, n+1):
    for j in range(1, i+1):
        print("*", end=" ")
    print()

for i in range(n-1,-1,-1):
    for j in range(1, i +1):
        print("*", end=" ")
    print()