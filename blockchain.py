class blockchain(object):
    def __init__(self):
        self.chain = []
        self.current_transactions = []

    #crea un nuevo bloque y lo adhiere a la cadena
    def new_block(self):
        pass

    # Agrega una nueva transacción a la lista de transacciones
    def new_transaction(self):
        pass
        
    #encripta un bloque
    @staticmethod
    def hash(block):
        pass

    #devuelve el ultimo bloque de la cadena
    @property
    def last_block(self):
        pass