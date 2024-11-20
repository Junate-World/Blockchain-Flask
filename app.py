from flask import Flask, jsonify, request
from blockchain import Blockchain
from uuid import uuid4

# Instantiate the Node
app = Flask(__name__)

# Generate a unique address for this node
node_identifier = str(uuid4()).replace("-", "")

# Instantiate the Blockchain
blockchain = Blockchain()

# Add a unique identifier for each node when generating the nonce
@app.route('/mine', methods=['GET'])
def mine():
    last_proof = blockchain.last_block["proof"]
    nonce = int(uuid4().int)  # A unique starting point for each node
    proof = None
    increment = 1  # Increment the nonce

    while not proof:
        candidate_proof = last_proof + nonce  # Incorporate unique nonce
        if blockchain.valid_proof(last_proof, candidate_proof, nonce):
            proof = candidate_proof
        nonce += increment  # Increment nonce

    blockchain.new_transaction(sender="0", recipient=node_identifier, amount=1)
    previous_hash = blockchain.hash(blockchain.last_block)
    block = blockchain.new_block(proof, previous_hash, nonce)

    response = {
        "message": "New Block Forged",
        "index": block["index"],
        "transactions": block["transactions"],
        "proof": block["proof"],
        "previous_hash": block["previous_hash"],
    }
    return jsonify(response), 200

@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()
    required = ["sender", "recipient", "amount"]
    if not all(k in values for k in required):
        return "Missing values", 400

    index = blockchain.new_transaction(
        values["sender"], values["recipient"], values["amount"]
    )
    response = {"message": f"Transaction will be added to Block {index}"}
    return jsonify(response), 201

@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        "chain": blockchain.chain,
        "length": len(blockchain.chain),
    }
    return jsonify(response), 200

@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json()
    nodes = values.get("nodes")
    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400
    for node in nodes:
        blockchain.register_node(node)

    print(f"Registered nodes: {blockchain.nodes}")
    
    response = {
        "message": "New nodes have been added",
        "total_nodes": list(blockchain.nodes),
    }
    

    return jsonify(response), 201

@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()

    if replaced:
        print("Chain was replaced with a longer chain")
    else:
        print("No conflict detected, chain remains the same")
        
    response = {
        "message": "Our chain was replaced" if replaced else "Our chain is authoritative",
        "chain": blockchain.chain,
    }
    return jsonify(response), 200

if __name__ == "__main__":
    app.run(debug=True, port=5000)
