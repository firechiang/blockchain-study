# {
#     "index":"0（区块索引）",
#     "timestamp":"1512121212112（时间戳）",
#     "transactions":[{
#         "sender":"交易的发送者",
#         "recipient":"交易的接受者"
#     }],
#     "proof": "0000sadassadfas（区块工作量证明）",
#     "previous_hash":"00000sdsfds（上一个区块的哈希证明）"
# }
import hashlib
import json
import time
import flask

class Blockchain:
    def __init__(self):
        # 区块链信息
        self.chain = []
        # 交易信息
        self.current_transactions = []
        # 创建创世纪区块（就是首个区块）
        self.new_block(proof = 100,previous_hash = 1)
        # 所有节点
        self.nodes = set()

    # 注册节点
    # address = http://127.0.0.1:50001
    def register_node(self,address: str):
        # 将地址信息添加到节点集合
        self.nodes.add(address)

    # 共识（校准区块链，遍历所有节点的链看谁的最长就以谁的为准）
    def resolve_conflicts(self) -> bool:
        nodes = self.nodes
        # 当前节点链的长度
        current_len = len(self.chain)
        # 遍历所有节点的链看谁的最长就以谁的为准
        for node in nodes:
            # 获取某个节点的链信息
            response = flask.request.get(node+"/chain")
            # 请求成功
            if response.status_code == 200:
                # 获取节点链的长度
                length = response.json()["length"]
                # 获取节点链的信息
                chain = response.json()["chain"]
                # 如果该节点的链比当前节点的长并且节点的链是有效链，就以该节点的链为准，并将当前节点的链信息替换为该节点的链信息
                if length > current_len and self.vaild_chain(chain):
                    self.chain = chain
                    return True
        return False

    # 验证一个区块链是否有效
    def vaild_chain(self,chain):
        # 上一个区块
        last_block = chain[0]
        current_index = 1
        while current_index < len(chain):
            block = chain[current_index]
            # 如果当前块的前一个块的hash值不等与前一个块的hash值，说明该区块链无效
            if block["previous_hash"] != self.hash(last_block):
                return False
            # 上一个区块的工作量证明和当前块的工作量证明要满足以0000开头，否则说明该区块链无效
            if not self.vaild_proof(last_block["proof"],block["proof"]):
                return False
            last_block = block
            current_index+=1
        return True

    # 创建一个区块并且将区块添加到区块链当中
    def new_block(self,proof,previous_hash = None):
        block = {
            # 区块索引(链的长度加1)
            "index": len(self.chain) + 1,
            # 时间戳
            "timestamp": time.time(),
            # 交易信息
            "transactions": self.current_transactions,
            # 区块工作量证明
            "proof": proof,
            # 上一个区块的哈希证明(注意：如果是空的话就用链的最后一个区块取计算)
            "previous_hash":previous_hash or self.hash(self.last_block)
        }
        self.current_transactions = []
        # 将区块加入到区块链当中
        self.chain.append(block)
        return block


    # 创建交易并将其添加到交易列表
    def new_transaction(self,sender,recipient,amount):
        info = {
            "sender":sender,
            "recipient":recipient,
            "amount":amount
        }
        # 将交易信息添加到交易列表
        self.current_transactions.append(info)
        # 返回最后一个区块里面的 index 属性值 + 1
        return self.last_block["index"] + 1

    # 创建区块的hash值（参数是一个区块）
    @staticmethod
    def hash(block):
        # 将json对象转换为字符串
        block_str = json.dumps(block,sort_keys=True).encode()
        # 获取字符串的hash摘要信息
        return hashlib.sha256(block_str).hexdigest()

    # 获取链上最后一个区块
    @property
    def last_block(self):
        # 注意: -1 就是取数组里的最后一个
        return self.chain[-1]

    # 生成工作量证明
    # last_proof = 上一个区块的工作量证明
    def proof_of_work(self,last_proof: int):
        # 工作量从0开始
        proof = 0
        # 死循环直到工作量验证通过
        while self.vaild_proof(last_proof,proof) is False:
            proof += 1
        print(f'工作量={proof}')
        return proof

    # 验证工作量证明
    # last_proof = 上一个区块的工作量证明
    # proof = 当前工作量证明
    def vaild_proof(self,last_proof: int,proof: int) -> bool:
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        print(guess_hash)
        # hash值如果是以4个零开头返回True否则返回False
        return guess_hash[0:4] == "0000"