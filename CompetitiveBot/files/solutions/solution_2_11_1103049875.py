n = int(input())
m = []
s = 0
for r in range(n):
    x = input().split()
    m.append(x)
for r in range(n):
    for c in range(n):
        if r == c:
            s += int(m[r][c])
print(s)