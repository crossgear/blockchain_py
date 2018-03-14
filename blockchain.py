import hashlib
import json
from textwrap import dedent
from time import time
from uuid import uuid4
from flask import Flask, jsonify, request


class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.current_transactions = []

        # Crea el bloque de genesis
        self.new_block( previous_hash=1, proof=100 )
    
    #crea un nuevo bloque y lo adhiere a la cadena
    def new_block(self, proof, previous_hash='none'):
        """
        Crea un nuevo bloque en la cadena de bloques
        :param proof: <int> La prueba dada por el algoritmo de prueba de trabajo
        :param previous_hash: (Opcional) <str> hash del bloque anterior
        :return: <dict> New Block
        """

        block = {
            'index' : len(self.chain) + 1,
            'timestamp' : time(),
            'transactions' : self.current_transactions,
            'proof' : proof,
            'previous_hash' : previous_hash or self.hash(self.chain(-1)),

        }

        #Reestablecer la lista de transacciones
        self.current_transactions = []

        self.chain.append(block)
        
        return block


    # Agrega una nueva transacción a la lista de transacciones
    def new_transaction(self):
        """
        Crea una nueva transacción para ir al siguiente bloque minado
        :param sender: <str> Dirección del remitente
        :param recipient: <str> Dirección del destinatario
        :param amount: <int> Cantidad
        :return: <int> El índice del bloque que contendrá esta transacción
        """
        self.current_transactions.append({
            'sender' : sender,
            'recipient' : recipient,
            'amount' : amount
        })

        return self.last_block['index'] + 1

    #devuelve el ultimo bloque de la cadena
    @property
    def last_block(self):
        return self.chain[-1]

    #encripta un bloque
    @staticmethod
    def hash(block):
        """
        Crea un hash SHA-256 de un bloque
        :param block: <dict> Bloque
        :return: <str>
        """
        # Debemos asegurarnos de que se ordena el diccionario, o tendremos hashes inconsistentes
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def proof_of_work(self, last_block):
        """
        Algoritmo simple de prueba de trabajo:
         - Encuentre un número p' tal que hash (pp') contiene los 4 ceros principales, donde p es la prueba anterior, y p' es la nueva prueba
        :param last_proof: <int>
        :return: <int>
        """
        proof = 0
        
        while self.valid_proof(last_proof, proof) is False:
            proof += 1
        return proof

    @staticmethod
    def valid_proof(self, last_proof, proof):
        """
        Valida la prueba: ¿El hash (last_proof, proof) contiene 4 ceros a la izquierda?
        :param last_proof: <int> proof anterior
        :param proof: <int> proof actual
        :return: <bool> Verdadero si es correcto, falso si no.
        """
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

# Instantiate our Node
app = Flask(__name__)

# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')

# Instantiate the Blockchain
blockchain = Blockchain()


@app.route('/mine', methods=['GET'])
def mine():
    # We run the proof of work algorithm to get the next proof...
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)

    # We must receive a reward for finding the proof.
    # The sender is "0" to signify that this node has mined a new coin.
    blockchain.new_transaction(
        sender="0",
        recipient=node_identifier,
        amount=1,
    )

    # Forge the new Block by adding it to the chain
    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)

    response = {
        'message': "New Block Forged",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    return jsonify(response), 200
  
@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()

    # Verificar que los campos requeridos estén en los datos POST
    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Missing values', 400

    # Crear una nueva transacción
    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])

    response = {'message': f'Transaction will be added to Block {index}'}
    return jsonify(response), 201

@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)





