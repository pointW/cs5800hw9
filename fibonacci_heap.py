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
        s = 'key:' + str(self.key)
        s += ', degree:' + str(self.degree)
        s += ', mark:' + str(self.mark)
        s += ', p:' + str(self.p.key) if self.p is not None else ', p:None'
        s += ', left:' + str(self.left.key)
        s += ', right:' + str(self.right.key)
        return s

    def draw(self, height=0):
        """
        print the tree
        :param height: int, current height for drawing
        """
        for x in self.siblings():
            print '    ' * (height-1) + '+----' * (height > 0) + x.__str__()
            if x.child is not None:
                x.child.draw(height+1)

    def size(self):
        """
        compute the size of self and siblings
        :return: int, the size
        """
        size = 1
        p = self.right
        while p is not self:
            size += 1
            p = p.right
        return size

    def find_key(self, k):
        """
        if key k is in self's siblings
        :param k: int, key being looking for
        :return: bool, True iff key k is in self's siblings
        """
        if self.key == k:
            return True
        p = self.right
        while p is not self:
            if p.key == k:
                return True
            p = p.right
        return False

    def insert(self, x):
        """
        insert x into self's sibling
        :param x: Node
        """
        if x is None:
            return
        x.left = self
        x.right = self.right
        self.right.left = x
        self.right = x

    def concatenate(self, l):
        """
        concatenate l into self's sibling
        :param l: Node, a node in l
        """
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
        """
        all children of self
        :return: list[Node], all children of self
        """
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
        """
        all siblings of self
        :return: list[Node]
        """
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
        """
        insert node x into root list, self.n += 1
        :param x: Node
        """
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
        """
        unites self and h2
        :param h2: FibonacciHeap, another heap that will be united with self
        """
        if self.min is None:
            self.min = h2.min
            self.n = h2.n
        else:
            self.min.concatenate(h2.min)
            if h2.min is not None and h2.min.key < self.min.key:
                self.min = h2.min
            self.n += h2.n

    def extract_min(self):
        """
        extract the node with minimum key, and reshape the heap
        :return: Node, node with minimum key
        """
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
        """
        reshape the heap such that there is only 1 tree for every degree
        """
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
        """
        insert y into x's children, unmark y
        :param y: Node, child
        :param x: Node, parent
        """
        # if self.min.right is self.min:
        #     self.min = None
        # else:
        if y.key == 39 and x.key == 18:
            aaa = 1
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
        """
        the max degree of current heap
        :return: int
        """
        return int(math.log(self.n, 1.62))

    def cut(self, x, y):
        """
        cut x out from y's children, add x into root list, unmark x
        :param x: Node, previous y's child
        :param y: Node, previous x's p
        :return:
        """
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
        """
        if y is not marked(previously no child of y is cut out), mark it(now 1 of y's child is cut)
        if y is marked(previously 1 child is cut, now 2 of y's child is cut), cut y from y's parent
        :param y: Node
        """
        z = y.p
        if z is not None:
            if y.mark is False:
                y.mark = True
            else:
                self.cut(y, z)
                self.cascading_cut(z)

    def decrease_key(self, x, k):
        """
        decrease the key of x into k
        :param x: Node
        :param k: int, new key
        :raise Exception if k is greater than current key
        """
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
        """
        delete node x
        :param x: Node
        """
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
        n18.p = n3
        n52.p = n3
        n38.p = n3
        n18.child = n39
        n39.p = n18
        n38.child = n41
        n41.p = n38
        n3.degree = 3
        n18.degree = 1
        n38.degree = 1
        n18.mark = True
        n39.mark = True

        n17.child = n30
        n30.p = n17
        n17.degree = 1

        n26.child = n35
        n35.p = n26
        n26.degree = 1
        n26.insert(n46)
        n24.child = n26
        n26.p = n24
        n46.p = n24
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
        h.min.draw()
        self.assertEqual(h.min.key, 7)
        self.assertEqual(h.min.degree, 2)
        self.assertEqual(h.min.right.degree, 3)
        self.assertEqual(h.min.right.right.degree, 1)


if __name__ == '__main__':
    unittest.main()
