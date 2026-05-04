# 🔗 Supply Chain Smart Contracts

> Aplicación blockchain con smart contracts para trazabilidad de cadena de suministro.

Proyecto desarrollado para la materia **Sistema de la Cadena de Bloques y Computación Cuántica** — TECNM Campus Cananea.

## 📋 Descripción

Este proyecto implementa una blockchain desde cero en Python con un motor de smart contracts diseñado para la trazabilidad de productos en cadena de suministro. Incluye:

- **Blockchain core**: Implementación completa con proof-of-work, validación de integridad y serialización
- **Motor de smart contracts**: Evaluación condicional y ejecución automática de acciones
- **Dominio de supply chain**: Gestión de productos, envíos y trazabilidad end-to-end
- **CLI interactiva**: Interfaz visual con Rich para demostración y uso

## 🚀 Instalación

### Requisitos

- Python 3.10+
- pip

### Setup

```bash
git clone https://github.com/AzahidGarcia/supply-chain-smart-contracts.git
cd supply-chain-smart-contracts
pip install -r requirements.txt
```

## 💻 Uso

### CLI Interactiva

```bash
python -m src.cli
```

### Demo Automático

```bash
python examples/demo_supply_chain.py
```

### Como Librería

```python
from datetime import date
from src.blockchain import Blockchain
from src.supply_chain import SupplyChainManager, Product

# Crear manager
manager = SupplyChainManager(difficulty=2)

# Registrar producto
product = Product(
    product_id="PROD-001",
    name="Vacuna COVID-19",
    origin="CDMX",
    manufacturer="Laboratorio Nacional",
    batch_number="LOT-2026-001",
    manufacture_date=date(2026, 4, 1)
)
manager.register_product(product)

# Crear envío
shipment = manager.create_shipment("PROD-001", "Almacén CDMX", "Hospital Sonora")

# Crear smart contract con condición de temperatura
contract = manager.create_delivery_contract(
    shipment.shipment_id, max_temp=8.0, max_days=3
)
```

## 🧪 Tests

```bash
python -m pytest tests/ -v
```

## 🏗️ Arquitectura

Ver documentación completa en [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

El sistema se compone de cuatro capas:

1. **Capa criptográfica** (`crypto_utils`): Hashing SHA-256 y generación de IDs
2. **Capa de blockchain** (`blockchain`): Bloques, cadena, proof-of-work
3. **Capa de smart contracts** (`smart_contract`): Condiciones, acciones, ejecución
4. **Capa de dominio** (`supply_chain`): Productos, envíos, gestión de cadena

```
Presentación (CLI / Demo)
        │
   Dominio (supply_chain)
   ┌─────┴─────┐
Contratos  Blockchain
   └─────┬─────┘
  Criptografía (SHA-256)
```

## 📁 Estructura

```
supply-chain-smart-contracts/
├── README.md
├── LICENSE
├── requirements.txt
├── setup.py
├── .gitignore
├── src/
│   ├── blockchain.py          # Core blockchain: Block, Blockchain
│   ├── smart_contract.py      # Motor de smart contracts
│   ├── supply_chain.py        # Dominio: Product, Shipment, SupplyChainManager
│   ├── crypto_utils.py        # Hashing SHA-256, generación de IDs
│   └── cli.py                 # CLI interactiva con Rich
├── tests/
│   ├── test_blockchain.py
│   ├── test_smart_contract.py
│   └── test_supply_chain.py
├── examples/
│   └── demo_supply_chain.py
└── docs/
    └── ARCHITECTURE.md
```

## 📄 Licencia

MIT License — ver [`LICENSE`](LICENSE).

## 👤 Autor

Desarrollado como proyecto académico para TECNM Campus Cananea, 2026.
