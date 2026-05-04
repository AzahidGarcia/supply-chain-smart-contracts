# Arquitectura del Sistema — Supply Chain Smart Contracts

## Visión General

El sistema implementa una blockchain desde cero en Python con un motor de smart contracts aplicado al dominio de trazabilidad de cadena de suministro. El diseño sigue una arquitectura en capas donde cada capa depende únicamente de las capas inferiores.

```
┌─────────────────────────────────────────────────────────┐
│                  Capa de Presentación                    │
│            cli.py · demo_supply_chain.py                 │
│           (Rich — tablas, paneles, colores)               │
└───────────────────────┬─────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────┐
│                  Capa de Dominio                          │
│                   supply_chain.py                        │
│       Product · Shipment · SupplyChainManager            │
└──────────┬────────────────────────┬─────────────────────┘
           │                        │
┌──────────▼──────────┐  ┌──────────▼──────────────────── ┐
│  Capa de Contratos  │  │      Capa de Blockchain         │
│  smart_contract.py  │  │        blockchain.py            │
│  Condition · Action │  │      Block · Blockchain         │
│  SmartContract      │  │      Proof-of-Work              │
└──────────┬──────────┘  └──────────┬─────────────────────┘
           │                        │
┌──────────▼────────────────────────▼─────────────────────┐
│                  Capa Criptográfica                       │
│                   crypto_utils.py                        │
│           hash_data · hash_block · generate_id           │
│                      SHA-256 · UUID4                     │
└─────────────────────────────────────────────────────────┘
```

## Módulos

### `crypto_utils.py` — Capa Criptográfica

Funciones puras sin estado. Toda operación de hashing en el sistema pasa por aquí.

- `hash_data(data: str) -> str` — SHA-256 sobre cadena UTF-8
- `hash_block(...)  -> str` — serializa un bloque a JSON (llaves ordenadas) y aplica `hash_data`
- `generate_id() -> str` — primeros 8 caracteres de un UUID4

**Decisión de diseño:** usar `json.dumps(sort_keys=True)` garantiza que el mismo bloque siempre produzca el mismo hash independientemente del orden de inserción en el diccionario.

### `blockchain.py` — Capa Blockchain

#### `Block`
Estructura de datos inmutable (por convención) con: `index`, `timestamp`, `data`, `previous_hash`, `nonce`, `hash`.

#### `Blockchain`
- **Proof-of-Work:** iteración de `nonce` hasta que `hash.startswith("0" * difficulty)`. Dificultad default = 2 (ajustable para demos rápidos).
- **Validación:** recorre la cadena verificando que cada `block.hash == block.calculate_hash()` y que `block.previous_hash == previous_block.hash`.
- **Serialización:** `to_dict()` permite exportar a JSON para persistencia futura.

### `smart_contract.py` — Motor de Contratos

#### `Condition`
Dataclass con `field`, `operator`, `value`. El método `evaluate(context)` aplica el operador sobre `context[field]`. Soporta 8 operadores: `==`, `!=`, `>`, `<`, `>=`, `<=`, `in`, `not_in`.

#### `Action`
Dataclass con `action_type` y `params`. Simula ejecución de acciones de negocio: transferencia de propiedad, liberación de pago, notificaciones, alertas.

#### `SmartContract`
- Estado inicial: `PENDING`.
- `execute(context)`: evalúa **todas** las condiciones. Si alguna falla, el contrato pasa a `FAILED` sin ejecutar acciones. Si todas se cumplen, ejecuta todas las acciones y pasa a `EXECUTED`.
- Retorna `ContractResult` con detalle completo de ejecución.

**Decisión de diseño:** usar `dataclasses` en lugar de Pydantic elimina dependencias externas y mantiene la lógica de negocio portable.

### `supply_chain.py` — Capa de Dominio

#### `SupplyChainManager`
Punto central de integración. Mantiene tres registros en memoria: `products`, `shipments`, `contracts`.

**Flujo principal:**
1. `register_product()` → persiste en blockchain con tipo `registro_producto`
2. `create_shipment()` → crea `Shipment`, persiste con tipo `creacion_envio`
3. `create_delivery_contract()` → crea `SmartContract`, persiste con tipo `creacion_contrato`
4. `update_shipment()` → actualiza estado, persiste con tipo `actualizacion_envio`, luego evalúa todos los contratos cuyo `creator == shipment_id` y `status == PENDING`

**Trazabilidad:** `get_product_history()` recorre la blockchain completa buscando bloques asociados al `product_id` dado. Esto garantiza que la trazabilidad es resistente a modificaciones en memoria.

## Flujo de Datos — Demo Típico

```
Producto registrado
      │
      ▼
  Bloque #1 en blockchain (tipo: registro_producto)
      │
      ▼
  Envío creado
      │
      ▼
  Bloque #2 (tipo: creacion_envio)
      │
      ▼
  Smart contract creado con condiciones
      │
      ▼
  Bloque #3 (tipo: creacion_contrato)
      │
      ▼
  Actualización de estado (en_transito)
      │
      ▼
  Bloque #4 (tipo: actualizacion_envio)
      │                    │
      ▼                    ▼
 Contratos pendientes   contexto = {status, temperature, location, ...}
 evaluados                         │
                                   ▼
                        ¿Condiciones cumplidas?
                         /                 \
                       SÍ                  NO
                        │                   │
                        ▼                   ▼
                   Acciones             ContractResult
                   ejecutadas           success=False
                        │
                        ▼
                  Bloque #5 (tipo: ejecucion_contrato)
```

## Decisiones Técnicas

| Decisión | Alternativa descartada | Razón |
|---|---|---|
| `dataclasses` para contratos | Pydantic | Cero dependencias extra; validación suficiente en este contexto |
| SHA-256 con `hashlib` | `cryptography` lib | Librería estándar; adecuado para demostración académica |
| PoW con nonce simple | No usar PoW | Demuestra el mecanismo de consenso de forma didáctica |
| `ContractStatus` como Enum | strings planos | Previene errores de tipeo; comparaciones seguras |
| `json.dumps(sort_keys=True)` | Concatenación de strings | Determinismo del hash independiente del orden de keys |
| Contratos enlazados por `creator=shipment_id` | FK relacional | Simplicidad; suficiente para el dominio en memoria |
