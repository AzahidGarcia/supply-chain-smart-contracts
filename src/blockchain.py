"""Implementación del núcleo de la blockchain: Block y Blockchain."""

from datetime import datetime
from typing import Optional

from src.crypto_utils import hash_block


class Block:
    """Representa un bloque individual dentro de la cadena de bloques."""

    def __init__(self, index: int, data: dict, previous_hash: str) -> None:
        """
        Inicializa un nuevo bloque.

        Args:
            index: Posición del bloque en la cadena.
            data: Datos almacenados en el bloque (diccionario serializable).
            previous_hash: Hash del bloque anterior.
        """
        self.index: int = index
        self.timestamp: str = datetime.now().isoformat()
        self.data: dict = data
        self.previous_hash: str = previous_hash
        self.nonce: int = 0
        self.hash: str = self.calculate_hash()

    def calculate_hash(self) -> str:
        """Calcula y retorna el hash SHA-256 del bloque."""
        return hash_block(
            self.index,
            self.timestamp,
            self.data,
            self.previous_hash,
            self.nonce,
        )

    def to_dict(self) -> dict:
        """Serializa el bloque a un diccionario compatible con JSON."""
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce,
            "hash": self.hash,
        }

    def __repr__(self) -> str:
        return f"Block(index={self.index}, hash={self.hash[:16]}...)"


class Blockchain:
    """Cadena de bloques con proof-of-work y validación de integridad."""

    def __init__(self, difficulty: int = 2) -> None:
        """
        Inicializa la blockchain con un bloque génesis.

        Args:
            difficulty: Número de ceros iniciales requeridos en el hash (proof-of-work).
        """
        self.difficulty: int = difficulty
        self.chain: list[Block] = []
        self._create_genesis_block()

    def _create_genesis_block(self) -> None:
        """Crea y agrega el bloque génesis a la cadena."""
        genesis = Block(
            index=0,
            data={"mensaje": "Bloque génesis", "tipo": "genesis"},
            previous_hash="0" * 64,
        )
        genesis.hash = genesis.calculate_hash()
        self.chain.append(genesis)

    def _proof_of_work(self, block: Block) -> None:
        """Realiza el proof-of-work hasta encontrar un hash con la dificultad requerida."""
        target = "0" * self.difficulty
        while not block.hash.startswith(target):
            block.nonce += 1
            block.hash = block.calculate_hash()

    def add_block(self, data: dict) -> Block:
        """
        Crea un nuevo bloque, aplica proof-of-work y lo agrega a la cadena.

        Args:
            data: Datos a almacenar en el nuevo bloque.

        Returns:
            El bloque recién creado y añadido.
        """
        previous_block = self.chain[-1]
        new_block = Block(
            index=len(self.chain),
            data=data,
            previous_hash=previous_block.hash,
        )
        self._proof_of_work(new_block)
        self.chain.append(new_block)
        return new_block

    def validate_chain(self) -> bool:
        """
        Verifica la integridad completa de la cadena de bloques.

        Returns:
            True si todos los bloques son válidos y están correctamente enlazados.
        """
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]

            if current.hash != current.calculate_hash():
                return False

            if current.previous_hash != previous.hash:
                return False

        return True

    def get_block(self, index: int) -> Optional[Block]:
        """
        Obtiene un bloque por su índice.

        Args:
            index: Índice del bloque a recuperar.

        Returns:
            El bloque si existe, None en caso contrario.
        """
        if 0 <= index < len(self.chain):
            return self.chain[index]
        return None

    @property
    def chain_length(self) -> int:
        """Retorna el número total de bloques en la cadena."""
        return len(self.chain)

    def to_dict(self) -> list[dict]:
        """Serializa toda la cadena a una lista de diccionarios."""
        return [block.to_dict() for block in self.chain]

    def __repr__(self) -> str:
        return f"Blockchain(bloques={self.chain_length}, dificultad={self.difficulty})"
