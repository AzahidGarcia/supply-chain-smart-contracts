"""Dominio de cadena de suministro: productos, envíos y gestión integrada."""

from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from typing import Optional

from src.blockchain import Blockchain
from src.crypto_utils import generate_id
from src.smart_contract import Action, Condition, ContractResult, SmartContract


class ShipmentStatus(Enum):
    """Estados posibles de un envío."""

    CREATED = "creado"
    IN_TRANSIT = "en_transito"
    DELIVERED = "entregado"
    REJECTED = "rechazado"


@dataclass
class Product:
    """Representa un producto registrado en la cadena de suministro."""

    product_id: str
    name: str
    origin: str
    manufacturer: str
    batch_number: str
    manufacture_date: date
    expiry_date: Optional[date] = None

    def to_dict(self) -> dict:
        """Serializa el producto a diccionario."""
        return {
            "product_id": self.product_id,
            "name": self.name,
            "origin": self.origin,
            "manufacturer": self.manufacturer,
            "batch_number": self.batch_number,
            "manufacture_date": self.manufacture_date.isoformat(),
            "expiry_date": self.expiry_date.isoformat() if self.expiry_date else None,
        }

    def __repr__(self) -> str:
        return f"Product(id={self.product_id}, name={self.name})"


@dataclass
class Shipment:
    """Representa un envío con trazabilidad completa de eventos."""

    shipment_id: str
    product: Product
    sender: str
    receiver: str
    status: ShipmentStatus = ShipmentStatus.CREATED
    temperature: Optional[float] = None
    location: str = ""
    history: list[dict] = field(default_factory=list)

    def update_status(
        self,
        new_status: ShipmentStatus,
        location: str,
        temperature: Optional[float] = None,
    ) -> None:
        """
        Actualiza el estado del envío y registra el evento en el historial.

        Args:
            new_status: Nuevo estado del envío.
            location: Ubicación actual del envío.
            temperature: Temperatura registrada (para cadena de frío).
        """
        self.status = new_status
        self.location = location
        if temperature is not None:
            self.temperature = temperature

        self.history.append(
            {
                "timestamp": datetime.now().isoformat(),
                "estado": new_status.value,
                "ubicacion": location,
                "temperatura": temperature,
            }
        )

    def to_dict(self) -> dict:
        """Serializa el envío a diccionario."""
        return {
            "shipment_id": self.shipment_id,
            "product_id": self.product.product_id,
            "sender": self.sender,
            "receiver": self.receiver,
            "status": self.status.value,
            "temperature": self.temperature,
            "location": self.location,
            "history": list(self.history),
        }

    def __repr__(self) -> str:
        return f"Shipment(id={self.shipment_id}, status={self.status.value})"


class SupplyChainManager:
    """
    Gestor central que integra blockchain, smart contracts y dominio de supply chain.

    Coordina el registro de productos, creación de envíos, evaluación de contratos
    y consulta de trazabilidad completa.
    """

    def __init__(self, difficulty: int = 2) -> None:
        """
        Inicializa el gestor con una nueva blockchain.

        Args:
            difficulty: Dificultad del proof-of-work de la blockchain.
        """
        self.blockchain: Blockchain = Blockchain(difficulty=difficulty)
        self.products: dict[str, Product] = {}
        self.shipments: dict[str, Shipment] = {}
        self.contracts: dict[str, SmartContract] = {}

    def register_product(self, product: Product) -> None:
        """
        Registra un producto y lo persiste en la blockchain.

        Args:
            product: Producto a registrar.

        Raises:
            ValueError: Si el producto ya existe.
        """
        if product.product_id in self.products:
            raise ValueError(f"Producto ya registrado: {product.product_id}")

        self.products[product.product_id] = product
        self.blockchain.add_block(
            {
                "tipo": "registro_producto",
                "producto": product.to_dict(),
                "timestamp": datetime.now().isoformat(),
            }
        )

    def create_shipment(self, product_id: str, sender: str, receiver: str) -> Shipment:
        """
        Crea un nuevo envío y lo registra en la blockchain.

        Args:
            product_id: ID del producto a enviar.
            sender: Remitente del envío.
            receiver: Destinatario del envío.

        Returns:
            El envío recién creado.

        Raises:
            ValueError: Si el producto no existe.
        """
        if product_id not in self.products:
            raise ValueError(f"Producto no encontrado: {product_id}")

        shipment = Shipment(
            shipment_id=generate_id(),
            product=self.products[product_id],
            sender=sender,
            receiver=receiver,
            location=sender,
        )
        shipment.history.append(
            {
                "timestamp": datetime.now().isoformat(),
                "estado": ShipmentStatus.CREATED.value,
                "ubicacion": sender,
                "temperatura": None,
            }
        )

        self.shipments[shipment.shipment_id] = shipment
        self.blockchain.add_block(
            {
                "tipo": "creacion_envio",
                "envio": shipment.to_dict(),
                "timestamp": datetime.now().isoformat(),
            }
        )
        return shipment

    def update_shipment(
        self,
        shipment_id: str,
        status: ShipmentStatus,
        location: str,
        temperature: Optional[float] = None,
    ) -> list[ContractResult]:
        """
        Actualiza el estado de un envío, lo registra en blockchain y evalúa contratos.

        Args:
            shipment_id: ID del envío a actualizar.
            status: Nuevo estado del envío.
            location: Nueva ubicación.
            temperature: Temperatura actual (opcional).

        Returns:
            Lista de resultados de contratos evaluados.

        Raises:
            ValueError: Si el envío no existe.
        """
        if shipment_id not in self.shipments:
            raise ValueError(f"Envío no encontrado: {shipment_id}")

        shipment = self.shipments[shipment_id]
        shipment.update_status(status, location, temperature)

        self.blockchain.add_block(
            {
                "tipo": "actualizacion_envio",
                "envio_id": shipment_id,
                "nuevo_estado": status.value,
                "ubicacion": location,
                "temperatura": temperature,
                "timestamp": datetime.now().isoformat(),
            }
        )

        context = {
            "shipment_id": shipment_id,
            "status": status.value,
            "location": location,
            "temperature": temperature,
            "product_id": shipment.product.product_id,
            "sender": shipment.sender,
            "receiver": shipment.receiver,
        }

        terminal = status in (ShipmentStatus.DELIVERED, ShipmentStatus.REJECTED)

        results: list[ContractResult] = []
        for contract in self.contracts.values():
            if terminal and contract.creator == shipment_id and contract.status.value == "pendiente":
                result = contract.execute(context)
                results.append(result)
                self.blockchain.add_block(
                    {
                        "tipo": "ejecucion_contrato",
                        "contrato_id": contract.contract_id,
                        "resultado": result.success,
                        "mensaje": result.message,
                        "timestamp": datetime.now().isoformat(),
                    }
                )

        return results

    def create_delivery_contract(
        self,
        shipment_id: str,
        max_temp: float,
        max_days: int,
    ) -> SmartContract:
        """
        Crea un smart contract de entrega con condiciones de temperatura y tiempo.

        Args:
            shipment_id: ID del envío al que aplica el contrato.
            max_temp: Temperatura máxima permitida.
            max_days: Días máximos para entrega.

        Returns:
            El smart contract creado.

        Raises:
            ValueError: Si el envío no existe.
        """
        if shipment_id not in self.shipments:
            raise ValueError(f"Envío no encontrado: {shipment_id}")

        shipment = self.shipments[shipment_id]

        conditions = [
            Condition(field="status", operator="==", value=ShipmentStatus.DELIVERED.value),
            Condition(field="temperature", operator="<=", value=max_temp),
        ]

        actions = [
            Action(
                action_type="release_payment",
                params={"monto": 1000, "moneda": "MXN"},
            ),
            Action(
                action_type="transfer_ownership",
                params={"nuevo_propietario": shipment.receiver},
            ),
            Action(
                action_type="update_status",
                params={"nuevo_estado": "completado"},
            ),
            Action(
                action_type="notify",
                params={
                    "destinatario": shipment.receiver,
                    "mensaje": "Envío entregado correctamente — contrato completado",
                },
            ),
        ]

        contract = SmartContract(
            name=f"Contrato de Entrega — Envío {shipment_id}",
            creator=shipment_id,
            conditions=conditions,
            actions=actions,
        )

        self.contracts[contract.contract_id] = contract
        self.blockchain.add_block(
            {
                "tipo": "creacion_contrato",
                "contrato": contract.to_dict(),
                "max_temperatura": max_temp,
                "max_dias": max_days,
                "timestamp": datetime.now().isoformat(),
            }
        )

        return contract

    def get_product_history(self, product_id: str) -> list[dict]:
        """
        Retorna el historial completo de trazabilidad de un producto desde la blockchain.

        Args:
            product_id: ID del producto a consultar.

        Returns:
            Lista de eventos ordenados cronológicamente.
        """
        history: list[dict] = []

        for block in self.blockchain.chain:
            data = block.data
            tipo = data.get("tipo", "")
            match = False

            if tipo == "registro_producto":
                match = data.get("producto", {}).get("product_id") == product_id
            elif tipo == "creacion_envio":
                match = data.get("envio", {}).get("product_id") == product_id
            elif tipo in ("actualizacion_envio", "creacion_contrato", "ejecucion_contrato"):
                envio_id = data.get("envio_id") or (data.get("contrato", {}) or {}).get("creator", "")
                shipment = self.shipments.get(envio_id or "")
                match = bool(shipment and shipment.product.product_id == product_id)

            if match:
                history.append(
                    {
                        **data,
                        "block_index": block.index,
                        "block_hash": block.hash[:16] + "...",
                    }
                )

        return history

    def verify_chain_integrity(self) -> bool:
        """Verifica la integridad de toda la blockchain."""
        return self.blockchain.validate_chain()

    def get_chain_summary(self) -> dict:
        """Retorna estadísticas generales del sistema."""
        contracts_by_status: dict[str, int] = {}
        for contract in self.contracts.values():
            key = contract.status.value
            contracts_by_status[key] = contracts_by_status.get(key, 0) + 1

        return {
            "total_bloques": self.blockchain.chain_length,
            "total_productos": len(self.products),
            "total_envios": len(self.shipments),
            "total_contratos": len(self.contracts),
            "contratos_por_estado": contracts_by_status,
            "integridad_valida": self.verify_chain_integrity(),
            "dificultad": self.blockchain.difficulty,
        }
