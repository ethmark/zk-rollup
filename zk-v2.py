import hashlib
from math import log2, ceil


def hash_string(s):
    return hashlib.sha256(s.encode()).hexdigest()


class MerkleTree:
    """
    A naive Merkle tree implementation using SHA256
    """
    def __init__(self, data):
        self.data = data
        print('data原数据:', self.data)
        next_pow_of_2 = int(2**ceil(log2(len(data))))  # ceil() 函数返回数字的上入整数。
        print('next_pow_of_2:', next_pow_of_2)
        self.data.extend([0] * (next_pow_of_2 - len(data)))
        print('data拓展后的数据:', self.data)
        print('111111111111:', ["" for x in self.data])
        print('222222222222:', [hash_string(str(x)) for x in self.data])
        self.tree = ["" for x in self.data] + \
                    [hash_string(str(x)) for x in self.data]
        print('tree的结构-1:', self.tree)
        for i in range(len(self.data) - 1, 0, -1):  # i [7,6,5, 4, 3, 2, 1]
            self.tree[i] = hash_string(self.tree[i * 2] + self.tree[i * 2 + 1])
        print('tree的结构-2:', self.tree)

    def get_root(self):
        """获得根结点"""
        return self.tree[1]

    def get_val_and_path(self, id):
        """获得认证路径"""
        val = self.data[id]
        auth_path = []
        id = id + len(self.data)
        print('------id------', id)
        while id > 1:
            print('id的值', id)
            print('^^^^', id ^ 1)
            print('--auth_path--', auth_path)
            auth_path += [self.tree[id ^ 1]]  # ^ 按位异或运算符：当两对应的二进位相异时，结果为1
            id = id // 2
        return val, auth_path

    def verify_merkle_path(self, root, data_size, value_id, value, path):
        cur = hash_string(str(value))
        tree_node_id = value_id + int(2**ceil(log2(data_size)))
        for sibling in path:
            assert tree_node_id > 1
            if tree_node_id % 2 == 0:
                cur = hash_string(cur + sibling)
            else:
                cur = hash_string(sibling + cur)
            tree_node_id = tree_node_id // 2
        print('tree_node_id', tree_node_id)
        assert tree_node_id == 1
        print('******* cur ********', cur)




p = [0, 4, -7, 1, 0]
markle = MerkleTree(data=p)
root = markle.get_root()
val, auth_path = markle.get_val_and_path(id=2)
print('----------------------------')
print('root:', root)
print('val:', val)
print('auth_path:', auth_path)
print('----------------------------')
markle.verify_merkle_path(root=root, data_size=7, value_id=9, value=val, path=auth_path)
print('log2(data_size)',log2(7))
print('ceil(log2(data_size))', ceil(log2(7)))

# a = ''
# b = '5feceb66ffc86f38d952786c6d696c79c2dbc239dd4e91b46729d73a27fb57e9'
# c = '5feceb66ffc86f38d952786c6d696c79c2dbc239dd4e91b46729d73a27fb57e9'
# print('b+c', b+c)
# print('a+b', a+b)
# print('b+c的哈希', hash_string(b+c))
# print('4^2', 9 ^ 3)