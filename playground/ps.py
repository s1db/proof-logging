s = [1,2,3]
ps = [[]]

for i in s:
    for sub_set in ps:
        ss = [list(sub_set)+[i]]
        ps=ps+ss
        # print(ss)
print(ps)