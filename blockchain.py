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
        Consensus Algorithm: Resolves conflicts by replacing our chain with the longest valid one in the network.
        """
        neighbours = self.nodes
        new_chain = None
        max_length = len(self.chain)  # Start with the current chain length

        for node in neighbours:
            try:
                response = requests.get(f"http://{node}/chain")
                if response.status_code == 200:
                    length = response.json().get("length")
                    chain = response.json().get("chain")

                    # Check if the fetched chain is longer and valid
                    if length > max_length and self.valid_chain(chain):
                        max_length = length
                        new_chain = chain

            except requests.exceptions.RequestException as e:
                print(f"Error communicating with node {node}: {e}")
                continue

        # Replace our chain if we discovered a new, valid chain longer than ours
        if new_chain:
            self.chain = new_chain
            return True  # Chain was replaced

        return False  # Chain remains authoritative
    def calculate_proof_cumulative(self, chain):
        """
        Calculate the cumulative proof of the entire chain.
        A measure of the computational work put into the chain.
        """
        return sum(block["proof"] for block in chain if "proof" in block)


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
