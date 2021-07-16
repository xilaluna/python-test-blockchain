import json
from time import time
import hashlib
from flask import Flask, request
from uuid import uuid4
from flask.json import jsonify


class Blockchain:
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.new_block(previous_hash=1, proof=100)

    def new_block(self, previous_hash, proof):
        '''Creates a new block and adds it to the chain'''
        new_block = {
            'transactions': self.current_transactions,
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1])
        }

        self.current_transactions = []
        self.chain.append(new_block)

        return new_block

    def new_transaction(self, sender, recipient, amount):
        '''Adds a transaction to existing transactions'''
        self.current_transactions.append(
            {
                'sender': sender,
                'recipient': recipient,
                'amount': amount
            }
        )

        return self.last_block['index'] + 1

    def proof_of_work(self, last_proof):
        proof = 0

        while self.valid_proof(last_proof, proof) is False:
            proof += 1

        return proof

    @staticmethod
    def valid_proof(last_proof, proof):
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()

        return guess_hash[:4] == '0000'

    @staticmethod
    def hash(block):
        '''Hashes a block'''
        block_string = json.dumps(block, sort_keys=True).encode()

        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        '''Returns last block in the chain'''
        return self.chain[-1]


app = Flask(__name__)

node_identifier = str(uuid4()).replace('-', '')

blockchain = Blockchain()


@app.route('/mine', methods=['GET'])
def mine():
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)

    blockchain.new_transaction(
        sender='0',
        recipient=node_identifier,
        amount=1
    )

    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(previous_hash, proof)

    response = {
        'message': 'New block added to chain.',
        'Index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash']
    }

    return jsonify(response), 200


@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()

    required = ['sender', 'recipient', 'amount']

    if not all(items in values for items in required):
        return 'Missing an entry', 400

    index = blockchain.new_transaction(
        values['sender'], values['recipient'], values['amount'])
    response = {'message': f'Transaction pending for block {index}.'}

    return jsonify(response), 201


@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }

    return jsonify(response)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
