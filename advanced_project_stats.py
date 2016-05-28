import os

file_count=0
line_count=0

files_list=[]

print("Files:\n")

for root, directories, filenames in os.walk('.'):
    for fname in filenames:
        if ".py" in fname:
            files_list.append(fname)

for root, directories, filenames in os.walk('.'):
    for fn in files_list:
        rel_p = os.path.join(root, fn)
        if os.path.isfile(rel_p):
            print(rel_p)
            file_count+=1
            f = open(rel_p, 'r')
            for line in f:
                line_count+=1

print("\nStatistics\n\n%s files found.\n%s lines of code.\n" % (file_count, line_count))

os.system("pause")
