import hashlib
import json
import time
from urllib.parse import urlparse
from uuid import uuid4
import requests

class Blockchain:
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.nodes = set()  # Use a set to store nodes for uniqueness
        self.new_block(previous_hash="1", proof=100)  # Create the genesis block

    def register_node(self, address):
        """
        Add a new node to the list of nodes.
        """
        parsed_url = urlparse(address)
        if parsed_url.netloc:
            self.nodes.add(parsed_url.netloc)
            print(f"Registered nodes: {self.nodes}")
        
        elif parsed_url.path:
            # Accept localhost without a scheme
            self.nodes.add(parsed_url.path)
        else:
            raise ValueError("Invalid URL")

    def valid_chain(self, chain):
        """
        Check if a given blockchain is valid.
        """
        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]

            # Check that the hash of the block is correct
            if block["previous_hash"] != self.hash(last_block):
                return False

            # Check that the proof of work is correct
            nonce = block.get("nonce", "")  # Retrieve nonce from block or default to an empty string
            if not self.valid_proof(last_block["proof"], block["proof"], nonce):
                return False

            last_block = block
            current_index += 1

        return True

    def resolve_conflicts(self):
        """
        Consensus Algorithm:
        Ensures all nodes synchronize their chains by merging blocks with unique proofs.
        No duplication occurs.
        """
        neighbours = self.nodes
        new_blocks = []  # Store new blocks from other nodes
        known_proofs = {block['proof'] for block in self.chain}  # Track existing proofs in the local chain

        for node in neighbours:
            response = requests.get(f"http://{node}/chain")

            if response.status_code == 200:
                remote_chain = response.json()["chain"]

                for block in remote_chain:
                    # Check if the block's proof is unique
                    if block['proof'] not in known_proofs:
                        # Add the new block to the list of blocks to merge
                        new_blocks.append(block)
                        known_proofs.add(block['proof'])  # Avoid processing the same block again

        # Merge the new blocks into the local chain, maintaining order by proof
        if new_blocks:
            self.chain.extend(new_blocks)
            # Sort the chain by proof to ensure proper structure
            self.chain.sort(key=lambda x: x['proof'])

            print(f"Merged {len(new_blocks)} new blocks from other nodes")
            return True

        print("No new blocks to merge")
        return False

    def valid_block(self, block):
        """
        Validates an individual block's structure and content.
        """
        # Ensure required fields are present
        required_keys = {"index", "timestamp", "transactions", "proof", "previous_hash", "nonce"}
        if not all(key in block for key in required_keys):
            return False

        # Verify the hash integrity (previous hash matches the hash of the previous block)
        if block["index"] > 1:  # Skip genesis block
            previous_block = self.chain[block["index"] - 2]
            if block["previous_hash"] != self.hash(previous_block):
                return False

        # Verify proof of work (use the previous block's proof and the current block's proof and nonce)
        last_proof = self.chain[block["index"] - 2]["proof"] if block["index"] > 1 else 100  # Genesis block has no previous proof
        if not self.valid_proof(last_proof, block["proof"], block["nonce"]):
            return False

        return True

    def new_block(self, proof, previous_hash=None, nonce=None):
        """
        Create a new block in the blockchain.
        """
        block = {
            "index": len(self.chain) + 1,
            "timestamp": time.ctime(),
            "transactions": self.current_transactions,
            "proof": proof,
            "previous_hash": previous_hash or self.hash(self.chain[-1]),
            "nonce": nonce,  # Include the nonce in the block
        }
        self.current_transactions = []
        self.chain.append(block)
        return block

    def new_transaction(self, sender, recipient, amount):
        self.current_transactions.append(
            {
                "sender": sender,
                "recipient": recipient,
                "amount": amount,
            }
        )
        return self.last_block["index"] + 1

    @staticmethod
    def hash(block):
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        return self.chain[-1]

    @staticmethod
    def valid_proof(last_proof, proof, nonce):
        """ Validates the proof: Does hash(last_proof, proof, nonce) contain 4 leading zeroes?
        """
        guess = f"{last_proof}{proof}{nonce}".encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        print(f"Testing proof: {proof}, hash: {guess_hash}")  # Debugging
        return guess_hash[:4] == "0000"
