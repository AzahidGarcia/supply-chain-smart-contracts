"""Tests para el dominio de supply chain: Product, Shipment, SupplyChainManager."""

import pytest
from datetime import date

from src.supply_chain import Product, Shipment, ShipmentStatus, SupplyChainManager


def make_product(product_id: str = "P001", name: str = "Producto Test") -> Product:
    return Product(
        product_id=product_id,
        name=name,
        origin="CDMX",
        manufacturer="Fabricante SA",
        batch_number="LOT-001",
        manufacture_date=date(2026, 1, 1),
    )


class TestProduct:
    def test_to_dict_has_all_fields(self):
        p = make_product()
        d = p.to_dict()
        for field in ("product_id", "name", "origin", "manufacturer", "batch_number", "manufacture_date"):
            assert field in d

    def test_expiry_date_none_when_not_set(self):
        p = make_product()
        assert p.to_dict()["expiry_date"] is None

    def test_expiry_date_serialized_when_set(self):
        p = make_product()
        p.expiry_date = date(2027, 1, 1)
        assert p.to_dict()["expiry_date"] == "2027-01-01"


class TestShipment:
    def _make_shipment(self) -> Shipment:
        return Shipment(
            shipment_id="S001",
            product=make_product(),
            sender="Almacén A",
            receiver="Almacén B",
            location="Almacén A",
        )

    def test_initial_status_is_created(self):
        s = self._make_shipment()
        assert s.status == ShipmentStatus.CREATED

    def test_update_status_changes_status(self):
        s = self._make_shipment()
        s.update_status(ShipmentStatus.IN_TRANSIT, "Centro Distribución")
        assert s.status == ShipmentStatus.IN_TRANSIT

    def test_update_status_records_event_in_history(self):
        s = self._make_shipment()
        s.update_status(ShipmentStatus.IN_TRANSIT, "Punto B", temperature=12.0)
        assert len(s.history) == 1
        assert s.history[0]["estado"] == "en_transito"
        assert s.history[0]["temperatura"] == 12.0

    def test_temperature_updated_on_status_update(self):
        s = self._make_shipment()
        s.update_status(ShipmentStatus.IN_TRANSIT, "Punto C", temperature=7.5)
        assert s.temperature == 7.5

    def test_to_dict_contains_history(self):
        s = self._make_shipment()
        s.update_status(ShipmentStatus.DELIVERED, "Destino")
        d = s.to_dict()
        assert len(d["history"]) == 1


class TestSupplyChainManager:
    def _setup(self) -> tuple[SupplyChainManager, Product]:
        mgr = SupplyChainManager(difficulty=1)
        product = make_product()
        mgr.register_product(product)
        return mgr, product

    def test_register_product_adds_to_blockchain(self):
        mgr, _ = self._setup()
        assert mgr.blockchain.chain_length == 2  # genesis + registro

    def test_register_duplicate_product_raises(self):
        mgr, product = self._setup()
        with pytest.raises(ValueError):
            mgr.register_product(product)

    def test_create_shipment_returns_shipment_object(self):
        mgr, product = self._setup()
        shipment = mgr.create_shipment(product.product_id, "Origen", "Destino")
        assert shipment.product.product_id == product.product_id

    def test_create_shipment_with_unknown_product_raises(self):
        mgr, _ = self._setup()
        with pytest.raises(ValueError):
            mgr.create_shipment("ID_INEXISTENTE", "A", "B")

    def test_update_shipment_evaluates_contracts(self):
        mgr, product = self._setup()
        shipment = mgr.create_shipment(product.product_id, "A", "B")
        contract = mgr.create_delivery_contract(shipment.shipment_id, max_temp=8.0, max_days=3)
        results = mgr.update_shipment(shipment.shipment_id, ShipmentStatus.DELIVERED, "B", 5.0)
        assert len(results) == 1
        assert results[0].success is True

    def test_contract_fails_when_temperature_exceeds_max(self):
        mgr, product = self._setup()
        shipment = mgr.create_shipment(product.product_id, "A", "B")
        mgr.create_delivery_contract(shipment.shipment_id, max_temp=8.0, max_days=3)
        results = mgr.update_shipment(shipment.shipment_id, ShipmentStatus.DELIVERED, "B", 15.0)
        assert results[0].success is False

    def test_get_product_history_returns_events(self):
        mgr, product = self._setup()
        shipment = mgr.create_shipment(product.product_id, "A", "B")
        mgr.update_shipment(shipment.shipment_id, ShipmentStatus.DELIVERED, "B", 5.0)
        history = mgr.get_product_history(product.product_id)
        assert len(history) >= 2

    def test_verify_chain_integrity_is_true(self):
        mgr, product = self._setup()
        mgr.create_shipment(product.product_id, "A", "B")
        assert mgr.verify_chain_integrity() is True

    def test_get_chain_summary_contains_expected_keys(self):
        mgr, _ = self._setup()
        summary = mgr.get_chain_summary()
        for key in ("total_bloques", "total_productos", "total_envios", "total_contratos", "integridad_valida"):
            assert key in summary
