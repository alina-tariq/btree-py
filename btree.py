class BTreeNode:

    def __init__(self, leaf=False):
        self.leaf = leaf
        self.keys = []
        self.c    = []

class BTree:

    def __init__(self, order):
        self.root = BTreeNode(leaf=True)
        self.maxChild = order

    def insert(self, k):
        r = self.root
        if len(r.keys) == (self.maxChild - 1):     # keys are full, so we must split
            s = BTreeNode()
            self.root = s
            s.c.insert(0, r)                  # former root is now 0th c of new root s
            self.split_child(s, 0)
            self._insert_nonfull(s, k)
        else:
            self._insert_nonfull(r, k)

    def _insert_nonfull(self, x, k):
        i = len(x.keys) - 1
        if x.leaf:
            # insert a key
            x.keys.append(0)
            while i >= 0 and k < x.keys[i]:
                x.keys[i+1] = x.keys[i]
                i -= 1
            x.keys[i+1] = k
        else:
            # insert a c
            while i >= 0 and k < x.keys[i]:
                i -= 1
            i += 1
            if len(x.c[i].keys) == (self.maxChild - 1):
                self.split_child(x, i)
                if k > x.keys[i]:
                    i += 1
            self._insert_nonfull(x.c[i], k)

    def split_child(self, x, i):
        maxChild = self.maxChild
        y = x.c[i]
        midpos = maxChild//2 - 1
        z = BTreeNode(leaf=y.leaf)
        # slide all children of x to the right and insert z at i+1.
        x.c.insert(i+1, z)
        x.keys.insert(i, y.keys[midpos])

        # keys of z are maxChild to 2t - 1,
        # y is then 0 to maxChild-2
        z.keys = y.keys[midpos+1:]
        y.keys = y.keys[0:midpos]

        # children of z are maxChild to 2t els of y.c
        if not y.leaf:
            z.c = y.c[midpos+1:]
            y.c = y.c[0:midpos+1]

    def delete(self, x, k):
        maxChild = self.maxChild
        i = 0
        minKeys = int((maxChild - 1)/2)

        while i < len(x.keys) and k > x.keys[i]:
            i += 1
        if x.leaf:
            if len(x.keys) > minKeys and x.keys[i] == k:
                x.keys.pop(i)
                return
            return

        if i < len(x.keys) and x.keys[i] == k:
            return self.delete_internal_node(x, k, i)
        elif len(x.c[i].keys) > minKeys:
            self.delete(x.c[i], k)
        else:
            if i != 0 and i + 1 < len(x.c):
                if len(x.c[i - 1].keys) > minKeys:
                    self.delete_sibling(x, i, i - 1)
                elif len(x.c[i + 1].keys) > minKeys:
                    self.delete_sibling(x, i, i + 1)
                else:
                    self.delete_merge(x, i, i + 1)
            elif i == 0:
                if len(x.c[i + 1].keys) > minKeys:
                    self.delete_sibling(x, i, i + 1)
                else:
                    self.delete_merge(x, i, i + 1)
            elif i + 2 == len(x.c):
                if len(x.c[i - 1].keys) > minKeys:
                    self.delete_sibling(x, i, i - 1)
                else:
                    self.delete_merge(x, i, i - 1)
            self.delete(x.c[i], k)

    def delete_internal_node(self, x, k, i):
        maxChild = self.maxChild
        minKeys = int((maxChild-1)/2)
        if x.leaf:
            if x.keys[i] == k:
                x.keys.pop(i)
                return
            return
        if len(x.c[i].keys) > minKeys:
            x.keys[i] = self.delete_predecessor(x.c[i])
            return
        elif len(x.c[i + 1].keys) > minKeys:
            x.keys[i] = self.delete_successor(x.c[i + 1])
            return
        else:
            self.delete_merge(x, i, i + 1)
            self.delete_internal_node(x.c[i], k, minKeys)

    def delete_predecessor(self, x):
        minKeys = int((self.maxChild-1)/2)
        if x.leaf:
            return x.keys.pop()
        n = len(x.keys) - 1
        if len(x.c[n].keys) > minKeys:
            self.delete_sibling(x, n + 1, n)
        else:
            self.delete_merge(x, n, n + 1)
        self.delete_predecessor(x.c[n])

    # Delete the successor
    def delete_successor(self, x):
        minKeys = int((self.maxChild-1)/2)
        if x.leaf:
            return x.keys.pop(0)
        if len(x.c[1].keys) > minKeys:
            self.delete_sibling(x, 0, 1)
        else:
            self.delete_merge(x, 0, 1)
        self.delete_successor(x.c[0])

    # Delete resolution
    def delete_merge(self, x, i, j):
        cnode = x.c[i]

        if j > i:
            rsnode = x.c[j]
            cnode.keys.append(x.keys[i])
            for k in range(len(rsnode.keys)):
                cnode.keys.append(rsnode.keys[k])
                if len(rsnode.c) > 0:
                    cnode.c.append(rsnode.c[k])
            if len(rsnode.c) > 0:
                cnode.c.append(rsnode.c.pop())
            new = cnode
            x.keys.pop(i)
            x.c.pop(j)
        else:
            lsnode = x.c[j]
            lsnode.keys.append(x.keys[j])
            for i in range(len(cnode.keys)):
                lsnode.keys.append(cnode.keys[i])
                if len(lsnode.c) > 0:
                    lsnode.c.append(cnode.c[i])
            if len(lsnode.c) > 0:
                lsnode.c.append(cnode.c.pop())
            new = lsnode
            x.keys.pop(j)
            x.c.pop(i)

        if x == self.root and len(x.keys) == 0:
            self.root = new

    # Delete the sibling
    def delete_sibling(self, x, i, j):
        cnode = x.c[i]
        if i < j:
            rsnode = x.c[j]
            cnode.keys.append(x.keys[i])
            x.keys[i] = rsnode.keys[0]
            if len(rsnode.c) > 0:
                cnode.c.append(rsnode.c[0])
                rsnode.c.pop(0)
            rsnode.keys.pop(0)
        else:
            lsnode = x.c[j]
            cnode.keys.insert(0, x.keys[i - 1])
            x.keys[i - 1] = lsnode.keys.pop()
            if len(lsnode.c) > 0:
                cnode.c.insert(0, lsnode.c.pop())

    def print(self, x=None, l=0):
        if not x:
            x = self.root
        space = '\t'
        print(space * l, "Level {0}: ".format(l), end="")
        for i in x.keys:
            print(i, end=" ")
        print()
        l += 1
        if len(x.c) > 0:
            for i in x.c:
                self.print(i, l)

    def vishelper(self, values, x=None, l=0):
        if not x:
            x = self.root

        if l > (len(values) - 1):
            values.append(l)
            values[l] = []

        vals = []
        for i in x.keys:
            vals.append(i)
        values[l].append(vals)

        l += 1
        if len(x.c) > 0:
            for i in x.c:
                self.vishelper(values, i, l)

    def visualize(self):
        vals = []
        self.vishelper(vals)

        spaces = '\t'
        i = len(vals) - 1
        print(" ")
        for level in vals:
            print(spaces * i, end=" ")
            for node in level:
                print(node, spaces * (i + 1), end=" ")
            print()
            i -= 1

B = BTree(4)

for a in range(10):
    B.insert(10*(a+1))

print("InOrder Traversal of Tree:")
print(" ")
B.print()
print(" ")
print("Visualization of B-Tree:")
B.visualize()
print(" ")
print("Deletion of a Node with a 3-Node Sibling:")
B.delete(B.root, 20)
B.visualize()
print(" ")
print("Deletion of a Node with a 2-Node Sibling:")
B.delete(B.root, 40)
B.visualize()
