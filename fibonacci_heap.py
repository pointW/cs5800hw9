import unittest
import math
import sys


class Node:
    def __init__(self, key):
        self.key = key
        self.p = None
        self.child = None
        self.left = self
        self.right = self
        self.mark = False
        self.degree = 0

    def __str__(self):
        return 'key:' + str(self.key) + ', degree' + str(self.degree)

    def size(self):
        size = 1
        p = self.right
        while p is not self:
            size += 1
            p = p.right
        return size

    def find_key(self, k):
        if self.key == k:
            return True
        p = self.right
        while p is not self:
            if p.key == k:
                return True
            p = p.right
        return False

    def insert(self, x):
        if x is None:
            return
        x.left = self
        x.right = self.right
        self.right.left = x
        self.right = x

    def concatenate(self, l):
        if l is None:
            return
        head1 = self
        tail1 = self.left
        head2 = l
        tail2 = l.left
        head1.left = tail2
        tail2.right = head1
        tail1.right = head2
        head2.left = tail1

    def children(self):
        children = []
        child = self.child
        if child is None:
            return children
        children.append(child)
        p = child.right
        while p is not child:
            children.append(p)
            p = p.right
        return children

    def siblings(self):
        siblings = []
        siblings.append(self)
        p = self.right
        while p is not self:
            siblings.append(p)
            p = p.right
        return siblings


class FibonacciHeap:
    def __init__(self, head=None):
        self.min = head
        self.n = 0 if self.min is None else 1

    def insert(self, x):
        if self.min is None:
            self.min = x
        else:
            # x.left = self.min
            # x.right = self.min.right
            # self.min.right.left = x
            # self.min.right = x
            self.min.insert(x)
            if x.key < self.min.key:
                self.min = x
        self.n += 1

    def union(self, h2):
        if self.min is None:
            self.min = h2.min
            self.n = h2.n
        else:
            self.min.concatenate(h2.min)
            if h2.min is not None and h2.min.key < self.min.key:
                self.min = h2.min
            self.n += h2.n

    def extract_min(self):
        z = self.min
        if z is not None:
            # for x in z.children():
            #     x.p = None
            #     z.insert(x)
            z.concatenate(z.child)
            z.left.right = z.right
            z.right.left = z.left
            if z is z.right:
                self.min = None
            else:
                self.min = z.right
                self.consolidate()
            self.n -= 1
        return z

    def consolidate(self):
        a = [None for _ in range(self.max_degree())]
        for w in self.min.siblings():
            x = w
            d = x.degree
            while a[d] is not None:
                y = a[d]
                if x.key > y.key:
                    x, y = y, x
                self.link(y, x)
                a[d] = None
                d += 1
            a[d] = x
        self.min = None
        for i in range(len(a)):
            if a[i] is not None:
                if self.min is None:
                    self.min = a[i]
                    self.min.left = self.min
                    self.min.right = self.min
                else:
                    self.min.insert(a[i])
                    if a[i].key < self.min.key:
                        self.min = a[i]

    def link(self, y, x):
        # if self.min.right is self.min:
        #     self.min = None
        # else:
        y.left.right = y.right
        y.right.left = y.left
        if x.child is not None:
            x.child.insert(y)
        else:
            y.left = y.right = y
            x.child = y
        y.p = x
        x.degree += 1
        y.mark = False

    def max_degree(self):
        return int(math.log(self.n, 1.62))

    def cut(self, x, y):
        if y.child.size() == 1:
            y.child = None
        else:
            x.left.right = x.right
            x.right.left = x.left
        y.degree -= 1
        x.p = None
        x.left = x.right = x
        x.mark = False
        self.min.insert(x)

    def cascading_cut(self, y):
        z = y.p
        if z is not None:
            if y.mark is False:
                y.mark = True
            else:
                self.cut(y, z)
                self.cascading_cut(z)

    def decrease_key(self, x, k):
        if k > x.key:
            raise Exception('new key is greater than current key')
        x.key = k
        y = x.p
        if y is not None and x.key < y.key:
            self.cut(x, y)
            self.cascading_cut(y)
        if x.key < self.min.key:
            self.min = x

    def delete(self, x):
        self.decrease_key(x, -sys.maxint)
        self.extract_min()


class Test(unittest.TestCase):
    def test_insert(self):
        n1 = Node(1)
        n2 = Node(2)
        n3 = Node(3)
        n4 = Node(4)
        n5 = Node(5)
        n1.insert(n2)
        self.assertEqual(n1.size(), 2)
        self.assertTrue(n1.find_key(1) and n1.find_key(2))
        h1 = FibonacciHeap(n1)
        h1.insert(n3)
        self.assertTrue(h1.min.size() == 3 and h1.min.find_key(3))
        h2 = FibonacciHeap(n5)
        h2.insert(n4)
        self.assertEqual(h2.min.key, 4)

    def test_union(self):
        n1 = Node(1)
        n2 = Node(2)
        n3 = Node(3)
        n4 = Node(4)
        n5 = Node(5)
        h1 = FibonacciHeap(n1)
        h2 = FibonacciHeap(n4)
        h1.insert(n2)
        h1.insert(n3)
        h2.insert(n5)
        h1.union(h2)
        self.assertEqual(h1.n, 5)
        self.assertEqual(h1.min.size(), 5)
        self.assertTrue(h1.min.find_key(4))
        self.assertTrue(h1.min.find_key(5))

    def test_extract_min(self):
        n23 = Node(23)
        n7 = Node(7)
        n21 = Node(21)
        n3 = Node(3)
        n18 = Node(18)
        n52 = Node(52)
        n38 = Node(38)
        n39 = Node(39)
        n41 = Node(41)
        n17 = Node(17)
        n30 = Node(30)
        n24 = Node(24)
        n26 = Node(26)
        n46 = Node(46)
        n35 = Node(35)

        n18.insert(n52)
        n52.insert(n38)
        n3.child = n18
        n18.child = n39
        n38.child = n41
        n3.degree = 3
        n18.degree = 1
        n38.degree = 1
        n18.mark = True
        n39.mark = True

        n17.child = n30
        n17.degree = 1

        n26.child = n35
        n26.degree = 1
        n26.insert(n46)
        n24.child = n26
        n24.degree = 2
        n26.mark = True

        h = FibonacciHeap(n23)
        h.insert(n7)
        h.insert(n21)
        h.insert(n3)
        h.insert(n17)
        h.insert(n24)
        h.n = 15

        x = h.extract_min()
        self.assertEqual(h.min.key, 7)
        self.assertEqual(h.min.degree, 3)
        self.assertEqual(h.min.right.degree, 2)
        self.assertEqual(h.min.right.right.degree, 1)


if __name__ == '__main__':
    unittest.main()
