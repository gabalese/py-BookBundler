# logica di base del matching
def matches(file1, file2):
    lista1 = open(file1, "r").readlines()
    lista2 = open(file2, "r").readlines()

    for i in lista1:
        for v in lista2:
            if map(len, i.split(" ")) == map(len, v.split(" ")):
                if i == v:
                    return True
    else:
        return False
