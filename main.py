'''
程序入口
'''
import flask
import uuid
from blockchain import Blockchain

# 初始化 Flask Http Server
app = flask.Flask(__name__)
# 初始化区块链
blockchain = Blockchain()
# 当前节点ID（就是uuid替换了-再转换为字符串）
node_id = str(uuid.uuid4())

# 处理 /index 请求地址
@app.route("/index",methods=["GET"])
def index():
    return "Hello BlockChain"


# 共识（校准区块链，遍历所有节点的链看谁的最长就以谁的为准）
@app.route("/resolve",methods=["GET"])
def resolve():
    succ = blockchain.resolve_conflicts()
    return f"共识完成我们的链是否被替换：{succ}",200

# 注册节点
@app.route("/nodes/register",methods=["POST"])
def register_node():
    values = flask.request.get_json()
    nodes = values.get("nodes")
    if nodes is None:
        return "请传递有效的节点列表",400
    for node in nodes:
        blockchain.register_node(node)
    response = {
        "msg": f'成功添加{len(nodes)}个节点'
    }
    return flask.jsonify(response),200

# 获取所有节点
@app.route("/nodes/get",methods=["GET"])
def get_node():

    return str(blockchain.nodes),200

# 添加交易
@app.route("/transactions/new",methods=["POST"])
def add_transaction():
    values = flask.request.get_json()
    if values is None:
        return "缺少必要参数",400
    # 参数名称
    required = ["sender","recipient","amount"]
    # 如果required里面有一个内容不在values里面
    if not all(k in values for k in required):
        return "缺少必要参数",400
    # 创建交易
    index = blockchain.new_transaction(values["sender"],values["recipient"],values["amount"])
    response = {
        "msg": f'该笔交易将会添加在块 {index}'
    }
    return flask.jsonify(response),201

# 挖矿并且打包交易上链
@app.route("/mine",methods=["GET"])
def mine():
    last_block = blockchain.last_block
    last_proof = last_block["proof"]
    # 工作量
    proof = blockchain.proof_of_work(last_proof)
    # 挖矿成功给自己添加交易
    blockchain.new_transaction(sender="0",recipient=node_id,amount=1)
    # 新建一个区块
    block = blockchain.new_block(proof,None)
    response = {
        "msg": "新的区块生成完成",
        "index": block["index"],
        # 交易信息
        "transactions": block["transactions"],
        # 区块工作量证明
        "proof": block["proof"],
        # 上一个区块的哈希证明(注意：如果是空的话就用链的最后一个区块取计算)
        "previous_hash": block["previous_hash"]
    }
    return flask.jsonify(response), 200

# 获取整个区块链信息
@app.route("/chain",methods=["GET"])
def chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }
    return flask.jsonify(response),200


if __name__ == "__main__":
    # parser = ArgumentParser()
    # parser.add_argument('-p','--port',default=5000,type=int,help="请填写绑定端口")
    # args = parser.parse_args
    # port = args.port
    app.run(host="0.0.0.0",port=5000)


