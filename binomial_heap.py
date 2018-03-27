import unittest
import sys
import copy


class Node:
    def __init__(self, key):
        self.key = key
        self.p = None
        self.child = None
        self.sibling = None
        self.degree = 0

    def __str__(self):
        s = 'key=' + str(self.key)
        s += ', degree=' + str(self.degree)
        s += ', p:' + str(self.p.key) if self.p is not None else ', p:None'
        s += ', sibling' + str(self.sibling.key) if self.sibling is not None else ', sibling:None'
        return s

    def draw(self, height=0):
        """
        print the tree
        :param height: int, current height for drawing
        """
        print '    ' * (height - 1) + '+----' * (height > 0) + self.__str__()
        if self.child is not None:
            self.child.draw(height + 1)
        if self.sibling is not None:
            self.sibling.draw(height)

    def reverse_child(self):
        """
        reverse self.child
        """
        p = None
        c_head = self.child
        if c_head:
            p = c_head.sibling
            c_head.sibling = None
        while p:
            q = p.sibling
            p.sibling = c_head
            c_head = p
            p = q
        self.child = c_head


def binomial_link(y, z):
    """
    make y the new head of the linked list of node z's children
    :param y: new child head
    :param z: parent node
    """
    y.p = z
    y.sibling = z.child
    z.child = y
    z.degree += 1


class BinomialHeap:
    def __init__(self, head=None):
        self.head = head
        if head is not None:
            p = head
            while p:
                p.p = None
                p = p.sibling

    def minimum(self):
        """
        return the min node
        :return: node with min key
        """
        x = self.head
        y = x
        if x is None:
            return y
        minimum = x.key
        while x is not None:
            if x.key < minimum:
                minimum = x.key
                y = x
            x = x.sibling
        return y

    def merge(self, h1):
        """
        merge the root list of self and h2 into a single linked list sorted by degree
        :param h1: another heap that will merge with this heap
        :return: head node of merged linked list sorted by degree
        """
        p = self.head
        q = h1.head
        if p is None:
            return q
        elif q is None:
            return p
        if p.degree < q.degree:
            head = p
            p = p.sibling
        else:
            head = q
            q = q.sibling
        k = head
        k.sibling = None
        while p and q:
            if p.degree < q.degree:
                k.sibling = p
                p = p.sibling
            else:
                k.sibling = q
                q = q.sibling
            k = k.sibling
            k.sibling = None
        if p:
            k.sibling = p
        elif q:
            k.sibling = q
        return head

    def union(self, h1):
        """
        unites self and h1
        :param h1: another heap that will union with this heap
        """
        self.head = self.merge(h1)
        if self.head is None:
            return
        prev_x = None
        x = self.head
        next_x = x.sibling
        while next_x is not None:
            if x.degree != next_x.degree or \
                    (next_x.sibling is not None and next_x.sibling.degree == x.degree):
                prev_x = x
                x = next_x
            else:
                if x.key <= next_x.key:
                    x.sibling = next_x.sibling
                    binomial_link(next_x, x)
                else:
                    if prev_x is None:
                        self.head = next_x
                    else:
                        prev_x.sibling = next_x
                    binomial_link(x, next_x)
                    x = next_x
            next_x = x.sibling
        return

    def insert(self, x):
        """
        insert node x into binomial heap h
        :param x: node that will be inserted
        """
        h1 = BinomialHeap(x)
        return self.union(h1)

    def extract_min(self):
        """
        extract the node with the minimum key, and reshape the heap
        :return: node with minimum key
        """
        x = self.minimum()

        # remove x from the root list of h
        p = self.head
        prev_p = None
        while p is not x:
            if prev_p is None:
                prev_p = p
            else:
                prev_p = prev_p.sibling
            p = p.sibling
        prev_p.sibling = p.sibling

        # reverse the order of the linked list of x's children
        x.reverse_child()

        h1 = BinomialHeap(x.child)
        self.union(h1)
        return x

    def delete(self, x):
        """
        delete node x from heap
        :param x: node that will be deleted
        """
        self.decrease_key(x, -sys.maxint)
        self.extract_min()

    def draw(self):
        """
        call draw on self.head
        """
        self.head.draw()

    @staticmethod
    def make_heap():
        """
        create a new heap with head=None
        :return: new heap
        """
        return BinomialHeap()

    @staticmethod
    def decrease_key(x, k):
        """
        decrease x.key to k, k should be smaller than x.key
        :param x: node that will have k decreased
        :param k: new key for node x
        :raise : exception when k > x.key
        """
        if k > x.key:
            raise Exception('new key is greater than current key')
        x.key = k
        y = x
        z = x.p
        while z is not None and y.key < z.key:
            y.key, z.key = z.key, y.key
            y = z
            z = y.p


class TestHeapMethods(unittest.TestCase):
    def test_merge(self):
        nodes = [Node(0) for _ in range(5)]
        for i in range(len(nodes)):
            nodes[i].degree = i
        node1 = Node(0)
        node1.degree = 1
        nodes[0].sibling = nodes[2]
        nodes[2].sibling = nodes[4]
        nodes[1].sibling = node1
        node1.sibling = nodes[3]
        h1 = BinomialHeap(nodes[0])
        h2 = BinomialHeap(nodes[1])
        h = h1.merge(h2)
        p = h
        self.assertEqual(p.degree, 0)
        p = p.sibling
        self.assertEqual(p.degree, 1)
        p = p.sibling
        self.assertEqual(p.degree, 1)
        p = p.sibling
        self.assertEqual(p.degree, 2)
        p = p.sibling
        self.assertEqual(p.degree, 3)
        p = p.sibling
        self.assertEqual(p.degree, 4)

    def test_union(self):
        # h1:
        # 12 -> 7 -> 15
        #      25    28-33
        #            41
        n12 = Node(12)
        n7 = Node(7)
        n25 = Node(25)
        binomial_link(n25, n7)
        n15 = Node(15)
        n33 = Node(33)
        n28 = Node(28)
        n41 = Node(41)
        binomial_link(n33, n15)
        binomial_link(n41, n28)
        binomial_link(n28, n15)
        n12.sibling = n7
        n7.sibling = n15
        # h2:
        # 18 -> 3
        #      37
        n18 = Node(18)
        n3 = Node(3)
        n37 = Node(37)
        binomial_link(n37, n3)
        n18.sibling = n3
        h1 = BinomialHeap(n12)
        h2 = BinomialHeap(n18)
        h1.union(h2)
        # new h1
        # 12 ->  3
        # 18    15-----7-37
        #       28-33 25
        #       41
        h1.draw()
        self.assertEqual(h1.head.degree, 1)
        self.assertEqual(h1.head.sibling.degree, 3)
        head = h1.head
        self.assertEqual(head.key, 12)
        self.assertEqual(head.child.key, 18)
        head_next = head.sibling
        self.assertEqual(head_next.key, 3)
        self.assertEqual(head_next.child.key, 15)
        self.assertEqual(head_next.child.sibling.key, 7)
        self.assertEqual(head_next.child.sibling.sibling.key, 37)
        self.assertEqual(head_next.child.child.child.key, 41)

    def test_reverse(self):
        nodes = [Node(i) for i in range(5)]
        for i in range(len(nodes)-1):
            nodes[i].sibling = nodes[i+1]
        p = Node(100)
        p.child = nodes[0]
        p.reverse_child()
        self.assertEqual(p.child.key, 4)
        self.assertEqual(p.child.sibling.key, 3)
        self.assertEqual(p.child.sibling.sibling.key, 2)
        self.assertEqual(p.child.sibling.sibling.sibling.key, 1)
        self.assertEqual(p.child.sibling.sibling.sibling.sibling.key, 0)
        self.assertTrue(p.child.sibling.sibling.sibling.sibling.sibling is None)

    def test_extract(self):
        # h1:
        # 12 -> 7 -> 15
        #      25    28-33
        #            41
        n12 = Node(12)
        n7 = Node(7)
        n25 = Node(25)
        binomial_link(n25, n7)
        n15 = Node(15)
        n33 = Node(33)
        n28 = Node(28)
        n41 = Node(41)
        binomial_link(n33, n15)
        binomial_link(n41, n28)
        binomial_link(n28, n15)
        n12.sibling = n7
        n7.sibling = n15
        # h2:
        # 18 -> 3
        #      37
        n18 = Node(18)
        n3 = Node(3)
        n37 = Node(37)
        binomial_link(n37, n3)
        n18.sibling = n3
        h1 = BinomialHeap(n12)
        h2 = BinomialHeap(n18)
        h1.union(h2)
        # new h1
        # 12 ->  3
        # 18    15-----7-37
        #       28-33 25
        #       41
        x = h1.extract_min()
        # new h1
        # 37 ->  7
        #       15----12-25
        #       28-33 18
        #       41
        self.assertEqual(x.key, 3)
        self.assertEqual(h1.head.key, 37)
        self.assertEqual(h1.head.sibling.degree, 3)
        self.assertEqual(h1.head.sibling.sibling, None)
        self.assertEqual(h1.head.sibling.child.key, 15)
        self.assertEqual(h1.head.sibling.child.child.child.key, 41)

    def test_decrease_key(self):
        # h1:
        # 12 -> 7 -> 15
        #      25    28-33
        #            41
        n12 = Node(12)
        n7 = Node(7)
        n25 = Node(25)
        binomial_link(n25, n7)
        n15 = Node(15)
        n33 = Node(33)
        n28 = Node(28)
        n41 = Node(41)
        binomial_link(n33, n15)
        binomial_link(n41, n28)
        binomial_link(n28, n15)
        n12.sibling = n7
        n7.sibling = n15
        # h2:
        # 18 -> 3
        #      37
        n18 = Node(18)
        n3 = Node(3)
        n37 = Node(37)
        binomial_link(n37, n3)
        n18.sibling = n3
        h1 = BinomialHeap(n12)
        h2 = BinomialHeap(n18)
        h1.union(h2)
        # new h1
        # 12 ->  3
        # 18    15-----7-37
        #       28-33 25
        #       41
        h1.decrease_key(n41, 1)
        # new h1
        # 12 ->  1
        # 18     3-----7-37
        #       15-33 25
        #       28
        self.assertEqual(h1.head.sibling.key, 1)
        self.assertEqual(h1.head.sibling.child.child.child.key, 28)
        self.assertEqual(h1.head.sibling.child.child.key, 15)
        self.assertEqual(h1.head.sibling.child.child.sibling.key, 33)
        self.assertEqual(h1.head.sibling.child.key, 3)
        self.assertEqual(h1.head.sibling.child.sibling.key, 7)
        self.assertEqual(h1.head.sibling.child.sibling.child.key, 25)
        self.assertEqual(h1.head.sibling.child.sibling.sibling.key, 37)

    def test_delete(self):
        # h1:
        # 12 -> 7 -> 15
        #      25    28-33
        #            41
        n12 = Node(12)
        n7 = Node(7)
        n25 = Node(25)
        binomial_link(n25, n7)
        n15 = Node(15)
        n33 = Node(33)
        n28 = Node(28)
        n41 = Node(41)
        binomial_link(n33, n15)
        binomial_link(n41, n28)
        binomial_link(n28, n15)
        n12.sibling = n7
        n7.sibling = n15
        h1 = BinomialHeap(n12)
        h1.delete(n25)
        # h1.head.draw()
        # new h1
        # 7 -> 15
        # 12   28-33
        #      41
        self.assertEqual(h1.head.key, 7)
        self.assertEqual(h1.head.child.key, 12)
        self.assertTrue(h1.head.child.child is None)
        self.assertTrue(h1.head.child.sibling is None)


if __name__ == '__main__':
    unittest.main()
