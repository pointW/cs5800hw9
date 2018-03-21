import unittest


class Node:
    def __init__(self, key):
        self.key = key
        self.p = None
        self.child = None
        self.sibling = None
        self.degree = 0

    def __str__(self):
        return 'key=' + str(self.key) + ', degree=' + str(self.degree)

    def reverse_child(self):
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
    :param y: Node
    :param z: Node
    :return: None
    """
    y.p = z
    y.sibling = z.child
    z.child = y
    z.degree += 1


class BinomialHeap:
    def __init__(self, head=None):
        self.head = head

    def minimum(self):
        """
        return the min node
        :return: Node
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
        merge the root list of h1 and h2 into a single linked list sorted by degree
        :param h1: BinomialHeap
        :return: Node
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
        unites h1 and h2
        :param h1: BinomialHeap
        :return: BinomialHeap
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
        :param x: Node
        :return: BinomialHeap
        """
        h1 = BinomialHeap(x)
        return self.union(h1)

    def extract_min(self):
        """
        extract the node with the minimum key
        :return: Node
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
        n18 = Node(18)
        n3 = Node(3)
        n37 = Node(37)
        binomial_link(n37, n3)
        n18.sibling = n3
        h1 = BinomialHeap(n12)
        h2 = BinomialHeap(n18)
        h1.union(h2)
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
        n18 = Node(18)
        n3 = Node(3)
        n37 = Node(37)
        binomial_link(n37, n3)
        n18.sibling = n3
        h1 = BinomialHeap(n12)
        h2 = BinomialHeap(n18)
        h1.union(h2)
        x = h1.extract_min()
        self.assertEqual(x.key, 3)
        self.assertEqual(h1.head.key, 37)
        self.assertEqual(h1.head.sibling.degree, 3)
        self.assertEqual(h1.head.sibling.sibling, None)
        self.assertEqual(h1.head.sibling.child.key, 15)
        self.assertEqual(h1.head.sibling.child.child.child.key, 41)


if __name__ == '__main__':
    unittest.main()
