"""
Script de demostración ejecutable del sistema Supply Chain Smart Contracts.

Uso:
    python examples/demo_supply_chain.py
"""

import sys
from pathlib import Path

# Permite ejecutar el script desde la raíz del proyecto
sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import date

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.progress import BarColumn, Progress, SpinnerColumn, TaskProgressColumn, TextColumn
from rich.table import Table
from rich.text import Text

from src.supply_chain import Product, ShipmentStatus, SupplyChainManager

console = Console()


def banner() -> None:
    """Muestra el banner inicial del proyecto."""
    console.print()
    console.print(Panel(
        Text.assemble(
            ("🔗  SUPPLY CHAIN SMART CONTRACTS\n", "bold cyan"),
            ("Sistema Blockchain con Contratos Inteligentes\n", "bold white"),
            ("TECNM Campus Cananea · Cadena de Bloques y Computación Cuántica · 2026", "dim"),
        ),
        border_style="bright_cyan",
        padding=(1, 4),
    ))


def section(title: str) -> None:
    console.print()
    console.rule(f"[bold yellow]{title}[/bold yellow]")


def run_demo() -> None:
    banner()
    manager = SupplyChainManager(difficulty=2)

    # ─────────────────────────────────────────────────────────────────────────
    section("PASO 1 · Registro de Productos en Blockchain")
    # ─────────────────────────────────────────────────────────────────────────

    pharma = Product(
        product_id="FARM-001",
        name="Vacuna BioShield",
        origin="Monterrey, Nuevo León",
        manufacturer="BioMex Laboratorios S.A.",
        batch_number="LOT-2026-004",
        manufacture_date=date(2026, 1, 15),
        expiry_date=date(2027, 1, 15),
    )
    elec = Product(
        product_id="ELEC-001",
        name="Sensor IoT Industrial X200",
        origin="Guadalajara, Jalisco",
        manufacturer="TechMex Industries S.A.",
        batch_number="LOT-2026-021",
        manufacture_date=date(2026, 3, 1),
    )

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        t = progress.add_task("Minando bloque para FARM-001...", total=None)
        manager.register_product(pharma)
        progress.update(t, description="Minando bloque para ELEC-001...")
        manager.register_product(elec)

    prod_table = Table(title="📦 Productos Registrados en Blockchain", box=box.ROUNDED, border_style="green")
    prod_table.add_column("ID", style="cyan", width=10)
    prod_table.add_column("Nombre", style="bold white")
    prod_table.add_column("Origen", style="yellow")
    prod_table.add_column("Fabricante", style="dim")
    prod_table.add_column("Lote", style="dim")
    prod_table.add_column("Vence", style="dim")
    prod_table.add_column("Cadena Frío", style="magenta", justify="center")

    prod_table.add_row(
        "FARM-001", "Vacuna BioShield", "Monterrey, NL",
        "BioMex Laboratorios", "LOT-2026-004", "2027-01-15", "🥶 ≤ 8°C",
    )
    prod_table.add_row(
        "ELEC-001", "Sensor IoT Industrial", "Guadalajara, Jal",
        "TechMex Industries", "LOT-2026-021", "—", "➖ No aplica",
    )
    console.print(prod_table)

    # ─────────────────────────────────────────────────────────────────────────
    section("PASO 2 · Creación de Envíos")
    # ─────────────────────────────────────────────────────────────────────────

    shipment_pharma = manager.create_shipment(
        "FARM-001", "BioMex Monterrey", "Hospital General Cananea"
    )
    shipment_elec = manager.create_shipment(
        "ELEC-001", "TechMex Guadalajara", "Planta Industrial Hermosillo"
    )

    ship_table = Table(title="🚚 Envíos Creados", box=box.ROUNDED, border_style="blue")
    ship_table.add_column("ID Envío", style="bold cyan", width=12)
    ship_table.add_column("Producto", style="white")
    ship_table.add_column("Remitente", style="yellow")
    ship_table.add_column("Destinatario", style="green")
    ship_table.add_column("Estado Inicial", style="dim")

    ship_table.add_row(
        shipment_pharma.shipment_id, "Vacuna BioShield",
        "BioMex Monterrey", "Hospital General Cananea", "creado",
    )
    ship_table.add_row(
        shipment_elec.shipment_id, "Sensor IoT Industrial",
        "TechMex Guadalajara", "Planta Industrial Hermosillo", "creado",
    )
    console.print(ship_table)

    # ─────────────────────────────────────────────────────────────────────────
    section("PASO 3 · Creación de Smart Contracts")
    # ─────────────────────────────────────────────────────────────────────────

    contract_pharma = manager.create_delivery_contract(
        shipment_pharma.shipment_id, max_temp=8.0, max_days=3
    )
    contract_elec = manager.create_delivery_contract(
        shipment_elec.shipment_id, max_temp=40.0, max_days=7
    )

    c_table = Table(title="📜 Smart Contracts Registrados", box=box.ROUNDED, border_style="magenta")
    c_table.add_column("ID Contrato", style="bold magenta", width=12)
    c_table.add_column("Envío", style="cyan")
    c_table.add_column("Condición 1", style="yellow")
    c_table.add_column("Condición 2", style="yellow")
    c_table.add_column("Acciones", style="green")

    c_table.add_row(
        contract_pharma.contract_id,
        shipment_pharma.shipment_id,
        "estado == entregado",
        "temperatura ≤ 8°C",
        "pago · transferir · notificar",
    )
    c_table.add_row(
        contract_elec.contract_id,
        shipment_elec.shipment_id,
        "estado == entregado",
        "temperatura ≤ 40°C",
        "pago · transferir · notificar",
    )
    console.print(c_table)

    # ─────────────────────────────────────────────────────────────────────────
    section("PASO 4 · Simulación de Movimientos en Tránsito")
    # ─────────────────────────────────────────────────────────────────────────

    moves_table = Table(title="📍 Registro de Movimientos", box=box.ROUNDED, border_style="blue")
    moves_table.add_column("Envío", style="cyan", width=12)
    moves_table.add_column("Producto", style="white")
    moves_table.add_column("Ubicación", style="yellow")
    moves_table.add_column("Estado", style="dim")
    moves_table.add_column("Temp °C", style="bold", justify="right", width=10)
    moves_table.add_column("¿OK?", justify="center", width=6)

    # Farmacéutico — primer tramo OK
    manager.update_shipment(
        shipment_pharma.shipment_id, ShipmentStatus.IN_TRANSIT,
        "Centro Distribución Hermosillo", 5.0,
    )
    moves_table.add_row(
        shipment_pharma.shipment_id, "Vacuna BioShield",
        "Centro Dist. Hermosillo", "en_transito", "[green]5.0[/green]", "[green]✓[/green]",
    )

    # Farmacéutico — ruptura de cadena de frío
    manager.update_shipment(
        shipment_pharma.shipment_id, ShipmentStatus.IN_TRANSIT,
        "Bodega Nogales", 12.5,
    )
    moves_table.add_row(
        shipment_pharma.shipment_id, "Vacuna BioShield",
        "Bodega Nogales", "en_transito", "[red bold]12.5[/red bold]", "[red]✗[/red]",
    )

    # Electrónico — transporte normal
    manager.update_shipment(
        shipment_elec.shipment_id, ShipmentStatus.IN_TRANSIT,
        "Almacén Guaymas", 28.0,
    )
    moves_table.add_row(
        shipment_elec.shipment_id, "Sensor IoT Industrial",
        "Almacén Guaymas", "en_transito", "[green]28.0[/green]", "[green]✓[/green]",
    )

    manager.update_shipment(
        shipment_elec.shipment_id, ShipmentStatus.IN_TRANSIT,
        "Centro Distribución Sonora", 31.0,
    )
    moves_table.add_row(
        shipment_elec.shipment_id, "Sensor IoT Industrial",
        "Centro Dist. Sonora", "en_transito", "[green]31.0[/green]", "[green]✓[/green]",
    )
    console.print(moves_table)

    # ─────────────────────────────────────────────────────────────────────────
    section("PASO 5 · Entrega Final y Evaluación Automática de Contratos")
    # ─────────────────────────────────────────────────────────────────────────

    console.print("[bold]Entregando envío farmacéutico (temperatura 12.5°C — supera el límite de 8°C)...[/bold]")
    results_pharma = manager.update_shipment(
        shipment_pharma.shipment_id, ShipmentStatus.DELIVERED,
        "Hospital General Cananea", 12.5,
    )

    for result in results_pharma:
        if result.success:
            console.print(Panel(
                f"[green]✅  Contrato [{result.contract_id}]\n[bold]{result.message}[/bold][/green]",
                border_style="green",
            ))
        else:
            console.print(Panel(
                f"[red]❌  Contrato Farmacéutico [{result.contract_id}]\n[bold]{result.message}[/bold]\n\n"
                "[dim]El producto excedió la temperatura máxima permitida (8°C).\n"
                "El contrato fue RECHAZADO — pago bloqueado.[/dim][/red]",
                border_style="red",
                title="[bold red]CONTRATO RECHAZADO[/bold red]",
            ))

    console.print()
    console.print("[bold]Entregando envío electrónico (temperatura 28.0°C — dentro del límite de 40°C)...[/bold]")
    results_elec = manager.update_shipment(
        shipment_elec.shipment_id, ShipmentStatus.DELIVERED,
        "Planta Industrial Hermosillo", 28.0,
    )

    for result in results_elec:
        if result.success:
            console.print(Panel(
                f"[green]✅  Contrato Electrónico [{result.contract_id}]\n[bold]{result.message}[/bold][/green]",
                border_style="green",
                title="[bold green]CONTRATO APROBADO[/bold green]",
            ))
            actions_table = Table(box=box.SIMPLE, border_style="green", show_header=False)
            actions_table.add_column("", style="green")
            actions_table.add_column("", style="white")
            for action in result.executed_actions:
                actions_table.add_row("  →", action["mensaje"])
            console.print(actions_table)

    # ─────────────────────────────────────────────────────────────────────────
    section("PASO 6 · Trazabilidad Completa por Producto")
    # ─────────────────────────────────────────────────────────────────────────

    for pid, pname in [("FARM-001", "Vacuna BioShield"), ("ELEC-001", "Sensor IoT Industrial")]:
        history = manager.get_product_history(pid)
        trace_table = Table(
            title=f"🔍 Trazabilidad: {pname} ({pid})",
            box=box.ROUNDED,
            border_style="blue",
        )
        trace_table.add_column("Bloque #", style="bold cyan", width=9)
        trace_table.add_column("Tipo de Evento", style="yellow")
        trace_table.add_column("Hash (parcial)", style="dim")
        for event in history:
            trace_table.add_row(
                str(event["block_index"]),
                event.get("tipo", "—"),
                event.get("block_hash", "—"),
            )
        console.print(trace_table)

    # ─────────────────────────────────────────────────────────────────────────
    section("PASO 7 · Verificación de Integridad de la Blockchain")
    # ─────────────────────────────────────────────────────────────────────────

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task("Verificando bloques...", total=manager.blockchain.chain_length)
        for _ in manager.blockchain.chain:
            progress.advance(task)

    valid = manager.verify_chain_integrity()
    color = "green" if valid else "red"
    icon = "✅" if valid else "❌"
    console.print(Panel(
        f"[{color}]{icon}  Integridad de la cadena: [bold]{'VÁLIDA' if valid else 'COMPROMETIDA'}[/bold]\n"
        f"Total de bloques verificados: {manager.blockchain.chain_length}[/{color}]",
        border_style=color,
    ))

    # ─────────────────────────────────────────────────────────────────────────
    section("RESUMEN ESTADÍSTICO FINAL")
    # ─────────────────────────────────────────────────────────────────────────

    summary = manager.get_chain_summary()
    s_table = Table(
        title="📊 Estadísticas del Sistema",
        box=box.ROUNDED,
        border_style="cyan",
    )
    s_table.add_column("Métrica", style="bold white", width=30)
    s_table.add_column("Valor", style="bold cyan", justify="right")

    contratos_estado = summary.get("contratos_por_estado", {})
    ejecutados = contratos_estado.get("ejecutado", 0)
    fallidos = contratos_estado.get("fallido", 0)
    pendientes = contratos_estado.get("pendiente", 0)

    s_table.add_row("Total de bloques en cadena", str(summary["total_bloques"]))
    s_table.add_row("Productos registrados", str(summary["total_productos"]))
    s_table.add_row("Envíos gestionados", str(summary["total_envios"]))
    s_table.add_row("Smart contracts creados", str(summary["total_contratos"]))
    s_table.add_row("Contratos ejecutados (✅)", f"[green]{ejecutados}[/green]")
    s_table.add_row("Contratos fallidos (❌)", f"[red]{fallidos}[/red]")
    s_table.add_row("Contratos pendientes", str(pendientes))
    s_table.add_row("Dificultad proof-of-work", str(summary["dificultad"]))
    s_table.add_row(
        "Integridad de la cadena",
        "[green]✅ Válida[/green]" if summary["integridad_valida"] else "[red]❌ Comprometida[/red]",
    )
    console.print(s_table)

    console.print()
    console.print(Panel(
        "[bold cyan]Demo completado exitosamente.[/bold cyan]\n\n"
        "[white]Este proyecto demuestra una implementación funcional de blockchain con smart contracts\n"
        "aplicados a la trazabilidad de cadena de suministro, incluyendo:\n"
        "  • Proof-of-work con dificultad configurable\n"
        "  • Motor de contratos con condiciones y acciones parametrizables\n"
        "  • Trazabilidad end-to-end desde registro hasta entrega\n"
        "  • Validación de integridad criptográfica de la cadena[/white]\n\n"
        "[dim]TECNM Campus Cananea · Sistema de la Cadena de Bloques y Computación Cuántica · 2026[/dim]",
        border_style="bright_cyan",
        padding=(1, 2),
    ))


if __name__ == "__main__":
    run_demo()
