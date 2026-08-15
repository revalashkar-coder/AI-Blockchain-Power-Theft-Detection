import hashlib
import json
import time


class Block:

    def __init__(
        self,
        index,
        timestamp,
        data,
        previous_hash
    ):

        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash

        self.hash = self.calculate_hash()

    def calculate_hash(self):

        block_string = (
            str(self.index)
            + str(self.timestamp)
            + json.dumps(
                self.data,
                sort_keys=True
            )
            + str(self.previous_hash)
        )

        return hashlib.sha256(
            block_string.encode()
        ).hexdigest()

    def to_dict(self):

        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash,
            "hash": self.hash
        }


class Blockchain:

    def __init__(self):

        self.chain = []

        self.create_genesis_block()

    def create_genesis_block(self):

        genesis = Block(
            0,
            time.time(),
            {
                "message": "Genesis Block"
            },
            "0"
        )

        self.chain.append(genesis)

    def get_latest_block(self):

        return self.chain[-1]

    def add_block(self, data):

        latest_block = self.get_latest_block()

        new_block = Block(
            len(self.chain),
            time.time(),
            data,
            latest_block.hash
        )

        self.chain.append(new_block)

        return new_block

    def is_chain_valid(self):

        for i in range(1, len(self.chain)):

            current = self.chain[i]

            previous = self.chain[i - 1]

            # Check current hash
            if current.hash != current.calculate_hash():
                return False

            # Check previous hash
            if current.previous_hash != previous.hash:
                return False

        return True

    def get_chain(self):

        return [
            block.to_dict()
            for block in self.chain
        ] 