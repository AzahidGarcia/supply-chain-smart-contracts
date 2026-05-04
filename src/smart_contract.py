"""Motor de Smart Contracts: condiciones, acciones y ejecución condicional."""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class ContractStatus(Enum):
    """Estados posibles de un smart contract."""

    PENDING = "pendiente"
    EXECUTED = "ejecutado"
    FAILED = "fallido"
    EXPIRED = "expirado"


@dataclass
class Condition:
    """
    Condición evaluable sobre un contexto de ejecución.

    Soporta los operadores: ==, !=, >, <, >=, <=, in, not_in.
    """

    field: str
    operator: str
    value: Any

    def evaluate(self, context: dict) -> bool:
        """
        Evalúa la condición sobre el contexto dado.

        Args:
            context: Diccionario con los valores actuales del entorno.

        Returns:
            True si la condición se cumple, False en caso contrario.

        Raises:
            ValueError: Si el operador no es reconocido.
        """
        if self.field not in context:
            return False

        actual = context[self.field]

        operators: dict[str, Any] = {
            "==": lambda a, b: a == b,
            "!=": lambda a, b: a != b,
            ">": lambda a, b: a > b,
            "<": lambda a, b: a < b,
            ">=": lambda a, b: a >= b,
            "<=": lambda a, b: a <= b,
            "in": lambda a, b: a in b,
            "not_in": lambda a, b: a not in b,
        }

        if self.operator not in operators:
            raise ValueError(f"Operador desconocido: {self.operator}")

        try:
            return operators[self.operator](actual, self.value)
        except TypeError:
            return False

    def __str__(self) -> str:
        return f"{self.field} {self.operator} {self.value}"


@dataclass
class Action:
    """
    Acción ejecutable dentro de un smart contract.

    Tipos soportados: transfer_ownership, release_payment, update_status,
    notify, flag_alert.
    """

    action_type: str
    params: dict = field(default_factory=dict)

    def execute(self, context: dict) -> dict:
        """
        Ejecuta la acción y retorna el resultado.

        Args:
            context: Contexto de ejecución actual.

        Returns:
            Diccionario con el resultado de la acción.
        """
        result: dict[str, Any] = {
            "tipo": self.action_type,
            "params": self.params,
            "timestamp": datetime.now().isoformat(),
            "estado": "ejecutado",
        }

        messages = {
            "transfer_ownership": lambda p: f"Propiedad transferida a {p.get('nuevo_propietario', 'desconocido')}",
            "release_payment": lambda p: f"Pago liberado: ${p.get('monto', 0)} {p.get('moneda', 'MXN')}",
            "update_status": lambda p: f"Estado actualizado a: {p.get('nuevo_estado', 'desconocido')}",
            "notify": lambda p: f"Notificación enviada a {p.get('destinatario', 'desconocido')}: {p.get('mensaje', '')}",
            "flag_alert": lambda p: f"¡ALERTA! {p.get('razon', 'Condición no cumplida')}",
        }

        generator = messages.get(self.action_type, lambda p: f"Acción ejecutada: {self.action_type}")
        result["mensaje"] = generator(self.params)

        return result


@dataclass
class ContractResult:
    """Resultado de la ejecución de un smart contract."""

    success: bool
    contract_id: str
    executed_actions: list[dict]
    timestamp: datetime
    message: str

    def to_dict(self) -> dict:
        """Serializa el resultado a diccionario."""
        return {
            "success": self.success,
            "contract_id": self.contract_id,
            "executed_actions": self.executed_actions,
            "timestamp": self.timestamp.isoformat(),
            "message": self.message,
        }


class SmartContract:
    """
    Contrato inteligente con evaluación condicional y ejecución automática.

    El contrato evalúa una lista de condiciones sobre un contexto dado.
    Si todas se cumplen, ejecuta la lista de acciones definidas.
    """

    def __init__(
        self,
        name: str,
        creator: str,
        conditions: list[Condition],
        actions: list[Action],
    ) -> None:
        """
        Inicializa el smart contract.

        Args:
            name: Nombre descriptivo del contrato.
            creator: Identificador del creador (puede ser ID de envío u otro).
            conditions: Lista de condiciones que deben cumplirse.
            actions: Lista de acciones a ejecutar si las condiciones se cumplen.
        """
        self.contract_id: str = str(uuid.uuid4())[:8]
        self.name: str = name
        self.creator: str = creator
        self.created_at: datetime = datetime.now()
        self.conditions: list[Condition] = conditions
        self.actions: list[Action] = actions
        self.status: ContractStatus = ContractStatus.PENDING

    def execute(self, context: dict) -> ContractResult:
        """
        Evalúa condiciones y ejecuta acciones si todas se cumplen.

        Args:
            context: Diccionario con los valores del entorno actual.

        Returns:
            ContractResult con el resultado de la ejecución.
        """
        failed_conditions = [c for c in self.conditions if not c.evaluate(context)]

        if failed_conditions:
            self.status = ContractStatus.FAILED
            reasons = "; ".join(str(c) for c in failed_conditions)
            return ContractResult(
                success=False,
                contract_id=self.contract_id,
                executed_actions=[],
                timestamp=datetime.now(),
                message=f"Condiciones no cumplidas: {reasons}",
            )

        executed = [action.execute(context) for action in self.actions]
        self.status = ContractStatus.EXECUTED

        return ContractResult(
            success=True,
            contract_id=self.contract_id,
            executed_actions=executed,
            timestamp=datetime.now(),
            message="Contrato ejecutado exitosamente",
        )

    def to_dict(self) -> dict:
        """Serializa el contrato a un diccionario."""
        return {
            "contract_id": self.contract_id,
            "name": self.name,
            "creator": self.creator,
            "created_at": self.created_at.isoformat(),
            "status": self.status.value,
            "conditions": [str(c) for c in self.conditions],
            "actions_count": len(self.actions),
        }

    def __repr__(self) -> str:
        return f"SmartContract(id={self.contract_id}, status={self.status.value})"
