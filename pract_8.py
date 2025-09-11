# Genealogical tree: father -> [children]
father = {
    "a": ["b", "c"],
    "b": ["d", "e"],
    "c": ["f"]
}

# Check if x is father of y
def is_father(x, y):
    return y in father.get(x, [])

# Predicate: brother(X, Y)
def brother(x, y):
    for f, children in father.items():
        if x in children and y in children and x != y:
            return True
    return False

# Predicate: cousin(X, Y)
def cousin(x, y):
    fx, fy = None, None
    for f, children in father.items():
        if x in children:
            fx = f
        if y in children:
            fy = f
    # their fathers must be brothers
    return fx and fy and brother(fx, fy)

# Predicate: grandson(X, Y)
def grandson(x, y):
    for z in father.get(y, []):
        if x in father.get(z, []):
            return True
    return False

# Predicate: descendent(X, Y) (recursive)
def descendent(x, y):
    if is_father(y, x):
        return True
    for child in father.get(y, []):
        if descendent(x, child):
            return True
    return False

# --------------------------
# Testing the predicates
# --------------------------
print("brother(b,c):", brother("b", "c"))       # True
print("brother(d,e):", brother("d", "e"))       # True
print("cousin(d,f):", cousin("d", "f"))         # True
print("grandson(d,a):", grandson("d", "a"))     # True
print("grandson(f,a):", grandson("f", "a"))     # True
print("descendent(f,a):", descendent("f", "a")) # True
print("descendent(e,a):", descendent("e", "a")) # True
