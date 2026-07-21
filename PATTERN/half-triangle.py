n = int(input("Enter the value of n : "))
for i in range(1, n+1):
    print(" "*(n-i), "*"*i)  
    
# uncomment this to make it full triangle
# for i in range(1, n):
#     print(" "*i, "*"*(n-i))
