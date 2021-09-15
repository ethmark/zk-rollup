import hashlib
from math import log2, ceil
import random


def hash_string(s):
    return hashlib.sha256(s.encode()).hexdigest()


def get_witness(problem, assignment):
    """
    Given an instance of a partition problem via a list of numbers (the problem) and a list of
    (-1, 1), we say that the assignment satisfies the problem if their dot product is 0.
    """
    sum = 0
    mx = 0
    side_obfuscator = 1 - 2 * random.randint(0, 1)  # 丢硬币，产生随机的-1或者1
    print('----------生成P的过程---------')
    print('随机生成的side_obfuscator的值：', side_obfuscator)
    witness = [sum]  # witness便是p，p是两个数组的点积，不加绝对值
    assert len(problem) == len(assignment)
    for num, side in zip(problem, assignment):
        assert side == 1 or side == -1
        sum += side * num * side_obfuscator  # 计算p的元素
        witness += [sum]
        mx = max(mx, num)
    # make sure that it is a satisfying assignment
    assert sum == 0
    shift = random.randint(0, mx)  # 0~mx 之间随机取一个数值
    print('witness即P的值', witness)
    witness = [x + shift for x in witness]  # 将随机数r分别加到p的每个元素中
    print('加随机参数后witness即P的值', witness)
    print('---------生成P的结束---------')
    return witness


class ZkMerkleTree:
    """
    A Zero Knowledge Merkle tree implementation using SHA256
    """
    def __init__(self, data):
        self.data = data
        print('data-p值-1:', self.data)
        next_pow_of_2 = int(2**ceil(log2(len(data))))
        self.data.extend([0] * (next_pow_of_2 - len(data)))
        # Intertwine with randomness to obtain zero knowledge.增加默克尔根数叶子节点，获得零知识，
        # 防止verifier暴力破解获取叶子节点明文信息的风险
        rand_list = [random.randint(0, 1 << 32) for x in self.data]
        print('data-p值-2:', self.data)
        print('rand_list的值:', rand_list)
        self.data = [x for tup in zip(self.data, rand_list) for x in tup]
        print('data-p值-3:', self.data)
        # Create bottom level of the tree (i.e. leaves).
        self.tree = ["" for x in self.data] + \
                    [hash_string(str(x)) for x in self.data]  # len(self.tree) = 32
        print('tree-默克尔根数-1:', self.tree)
        print('tree-默克尔根数-1长度', len(self.tree))
        for i in range(len(self.data) - 1, 0, -1):
            print('i=', i)
            self.tree[i] = hash_string(self.tree[i * 2] + self.tree[i * 2 + 1])
            print('self.tree', self.tree[i])
        print('tree-默克尔根数-2:', self.tree)
        print('tree-默克尔根数-2长度', len(self.tree))

    def get_root(self):
        return self.tree[1]

    def get_val_and_path(self, id):
        # Because of the zk padding, the data is now at id * 2
        print('---------- 开始找验证路径 -----------')
        id = id * 2
        val = self.data[id]
        auth_path = []
        print('初始id*2的值:', id)
        print('data的值:', self.data)
        print('初始val的值:', val)
        id = id + len(self.data)
        print('tree:', self.tree)
        print('tree的长度', len(self.tree))
        print('id + len(data)的值:', id)
        while id > 1:
            print('  ')
            print('id ^ 1:', id ^ 1)
            auth_path += [self.tree[id ^ 1]]  # ^ 就是异或门，按位异或运算符：当两对应的二进位相异时，结果为1
            id = id // 2
            print('循环中的auth_path:', auth_path)
            print('循环中的id的值：', id)
            print('  ')
        print('val, auth_path', val, auth_path)
        print('---------- 结束找验证路径 -----------')

        return val, auth_path


def verify_zk_merkle_path(root, data_size, value_id, value, path):
    cur = hash_string(str(value))
    # Due to zk padding, data_size needs to be multiplied by 2, as does the value_id
    # 由于zk填充，data_size需要乘以2，就像value_id一样
    print(' ')
    print('----------- 验证路径 ----------')
    print('root:', root)
    print('data_size:', data_size)
    print('value_id:', value_id)
    print('value:', value)
    print('path:', path)
    tree_node_id = value_id * 2 + int(2**ceil(log2(data_size * 2)))

    print('value哈希后的cur:', cur)
    print(' ')
    for sibling in path:
        print('tree_node_id的值:', tree_node_id)
        print('sibling:', sibling)
        assert tree_node_id > 1
        if tree_node_id % 2 == 0:
            cur = hash_string(cur + sibling)
        else:
            cur = hash_string(sibling + cur)
        tree_node_id = tree_node_id // 2
        print('相加后的cur:', cur)
        print('除2后的tree_node_id:', tree_node_id)
        print(' ')
    assert tree_node_id == 1
    print('+++++++++ root == cur:', root == cur)
    return root == cur


def get_proof(problem, assignment, num_queries):
    proof = []
    randomness_seed = problem[:]
    print('   ')
    print('********** 生成proof开始 **********')
    for i in range(num_queries):
        witness = get_witness(problem, assignment)
        print('witness即P的值：', witness)
        tree = ZkMerkleTree(witness)
        print('默克尔根树：', tree)
        random.seed(str(randomness_seed))
        query_idx = random.randint(0, len(problem))
        print('query_idx「即l的长度」:', query_idx)
        query_and_response = [tree.get_root()]
        print('query_and_response---根结点:', query_and_response)
        query_and_response += [query_idx]
        print('query_and_response---数组:', query_and_response)
        query_and_response += tree.get_val_and_path(query_idx)
        print('query_and_response---验证路径:', query_and_response)
        query_and_response += tree.get_val_and_path((query_idx + 1) % len(witness))
        print('query_and_response---加1除P的长度:', query_and_response)
        proof += [query_and_response]
        randomness_seed += [query_and_response]
    print('  ')
    print('********** 生成proof结束 **********')
    return proof


def verify_proof(problem, proof):
    proof_checks_out = True
    randomness_seed = problem[:]
    print('  ')
    print('********** 证明proof的开始 **********')
    print('randomness_seed的值:', randomness_seed)
    for query in proof:
        print('query:', query)
        random.seed(str(randomness_seed))
        print('随机randomness_seed的值:', randomness_seed)
        query_idx = random.randint(0, len(problem))
        merkle_root = query[0]
        proof_checks_out &= query_idx == query[1]
        print('验证中的query_idx:', query_idx)
        print('merkle_root:', merkle_root)
        print('proof_checks_out的值:', proof_checks_out)
        # Test witness properties.
        if query_idx < len(problem):
            proof_checks_out &= abs(query[2] - query[4]) == abs(problem[query_idx])
        else:
            proof_checks_out &= query[2] == query[4]
        print('变化后的proof_checks_out的值:', proof_checks_out)
        # Authenticate paths
        proof_checks_out &= \
            verify_zk_merkle_path(merkle_root, len(problem) + 1, query_idx, query[2], query[3])
        print('proof_checks_out-第一个验证路径:', proof_checks_out)
        proof_checks_out &= \
            verify_zk_merkle_path(merkle_root, len(problem) + 1, (query_idx + 1) % (len(problem) + 1), query[4], query[5])
        randomness_seed += [query]
        print('proof_checks_out-第二个验证路径:', proof_checks_out)
    print('  ')
    print('********** 证明proof的结束 **********')
    return proof_checks_out


def test(q=1):
    # problem = [1, 2, 3, 6, 6, 6, 12]
    # assignment = [1, 1, 1, -1, -1, -1, 1]
    l = [4, 11, 8, 1]
    m = [1, -1, 1, -1]
    # q = [0, 4, -7, 1, 0]
    proof = get_proof(problem=l, assignment=m, num_queries=q)
    print('proof:', proof)
    return verify_proof(problem=l, proof=proof)

test()
