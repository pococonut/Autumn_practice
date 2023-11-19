x = str(input())
x_array = []
for i in x:
    x_array.append(i)

if len(x_array) == 5:
    x_array.reverse()
    f = ''
    for i in range(len(x_array)):
            f = f + x_array[i]
    print(int(f))
elif len(x_array) == 6:
    g = x_array[0]
    x_array.remove(x_array[0])
    x_array.reverse()
    x_array.insert(0, g)
    f = ''
    for i in range(len(x_array)):
            f = f + x_array[i]
    print(int(f))