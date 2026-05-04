"""Tests para el motor de smart contracts: Condition, Action, SmartContract."""

import pytest

from src.smart_contract import (
    Action,
    Condition,
    ContractResult,
    ContractStatus,
    SmartContract,
)


class TestCondition:
    def test_equal_operator_true(self):
        c = Condition(field="status", operator="==", value="entregado")
        assert c.evaluate({"status": "entregado"}) is True

    def test_equal_operator_false(self):
        c = Condition(field="status", operator="==", value="entregado")
        assert c.evaluate({"status": "pendiente"}) is False

    def test_less_than_or_equal_operator(self):
        c = Condition(field="temperature", operator="<=", value=8.0)
        assert c.evaluate({"temperature": 5.0}) is True
        assert c.evaluate({"temperature": 8.0}) is True
        assert c.evaluate({"temperature": 9.0}) is False

    def test_in_operator(self):
        c = Condition(field="location", operator="in", value=["CDMX", "Monterrey"])
        assert c.evaluate({"location": "CDMX"}) is True
        assert c.evaluate({"location": "Tijuana"}) is False

    def test_missing_field_returns_false(self):
        c = Condition(field="nonexistent", operator="==", value="x")
        assert c.evaluate({}) is False

    def test_unknown_operator_raises_value_error(self):
        c = Condition(field="x", operator="???", value=1)
        with pytest.raises(ValueError):
            c.evaluate({"x": 1})


class TestAction:
    def test_release_payment_action(self):
        a = Action(action_type="release_payment", params={"monto": 500, "moneda": "MXN"})
        result = a.execute({})
        assert "500" in result["mensaje"]
        assert result["estado"] == "ejecutado"

    def test_transfer_ownership_action(self):
        a = Action(action_type="transfer_ownership", params={"nuevo_propietario": "Empresa X"})
        result = a.execute({})
        assert "Empresa X" in result["mensaje"]

    def test_notify_action(self):
        a = Action(action_type="notify", params={"destinatario": "admin", "mensaje": "Listo"})
        result = a.execute({})
        assert "admin" in result["mensaje"]

    def test_flag_alert_action(self):
        a = Action(action_type="flag_alert", params={"razon": "Temperatura excedida"})
        result = a.execute({})
        assert "Temperatura excedida" in result["mensaje"]

    def test_unknown_action_type_executes_without_error(self):
        a = Action(action_type="custom_action", params={})
        result = a.execute({})
        assert result["estado"] == "ejecutado"


class TestSmartContract:
    def _make_contract(self, conditions=None, actions=None):
        conditions = conditions or [Condition("status", "==", "entregado")]
        actions = actions or [Action("notify", {"destinatario": "admin", "mensaje": "ok"})]
        return SmartContract("Test", "envio-001", conditions, actions)

    def test_initial_status_is_pending(self):
        contract = self._make_contract()
        assert contract.status == ContractStatus.PENDING

    def test_execute_success_when_all_conditions_met(self):
        contract = self._make_contract()
        result = contract.execute({"status": "entregado"})
        assert result.success is True
        assert contract.status == ContractStatus.EXECUTED

    def test_execute_failure_when_condition_not_met(self):
        contract = self._make_contract()
        result = contract.execute({"status": "en_transito"})
        assert result.success is False
        assert contract.status == ContractStatus.FAILED

    def test_executed_actions_populated_on_success(self):
        contract = self._make_contract()
        result = contract.execute({"status": "entregado"})
        assert len(result.executed_actions) == 1

    def test_executed_actions_empty_on_failure(self):
        contract = self._make_contract()
        result = contract.execute({"status": "rechazado"})
        assert result.executed_actions == []

    def test_to_dict_contains_contract_id(self):
        contract = self._make_contract()
        d = contract.to_dict()
        assert d["contract_id"] == contract.contract_id

    def test_contract_result_to_dict(self):
        from datetime import datetime
        r = ContractResult(
            success=True,
            contract_id="abc123",
            executed_actions=[{"tipo": "notify"}],
            timestamp=datetime.now(),
            message="ok",
        )
        d = r.to_dict()
        assert d["success"] is True
        assert "timestamp" in d
