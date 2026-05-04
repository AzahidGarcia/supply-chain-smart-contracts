"""CLI interactiva con Rich para el sistema Supply Chain Smart Contracts."""

from datetime import date

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, IntPrompt, Prompt
from rich.table import Table
from rich.text import Text

from src.supply_chain import Product, ShipmentStatus, SupplyChainManager

console = Console()
manager = SupplyChainManager(difficulty=2)


def _header() -> None:
    title = Text("🔗  SUPPLY CHAIN SMART CONTRACTS", style="bold cyan")
    subtitle = Text("Blockchain · Smart Contracts · Trazabilidad", style="dim")
    console.print(Panel.fit(f"{title}\n{subtitle}", border_style="cyan"))


def _menu() -> None:
    table = Table(box=box.ROUNDED, show_header=False, border_style="cyan")
    table.add_column("Opción", style="bold yellow", width=6)
    table.add_column("Descripción", style="white")

    items = [
        ("1", "Registrar nuevo producto"),
        ("2", "Crear envío"),
        ("3", "Actualizar estado de envío"),
        ("4", "Crear smart contract de entrega"),
        ("5", "Ver historial de producto"),
        ("6", "Ver cadena de bloques"),
        ("7", "Verificar integridad de la cadena"),
        ("8", "Ejecutar demo automático"),
        ("9", "Salir"),
    ]
    for opt, desc in items:
        table.add_row(opt, desc)

    console.print(table)


def _option_register_product() -> None:
    console.print(Panel("[bold]Registrar Nuevo Producto[/bold]", border_style="green"))
    product_id = Prompt.ask("ID del producto")
    name = Prompt.ask("Nombre")
    origin = Prompt.ask("Origen")
    manufacturer = Prompt.ask("Fabricante")
    batch = Prompt.ask("Número de lote")

    try:
        product = Product(
            product_id=product_id,
            name=name,
            origin=origin,
            manufacturer=manufacturer,
            batch_number=batch,
            manufacture_date=date.today(),
        )
        manager.register_product(product)
        console.print(f"[green]✅ Producto '{name}' registrado en la blockchain.[/green]")
    except ValueError as e:
        console.print(f"[red]❌ Error: {e}[/red]")


def _option_create_shipment() -> None:
    console.print(Panel("[bold]Crear Envío[/bold]", border_style="green"))
    if not manager.products:
        console.print("[yellow]No hay productos registrados.[/yellow]")
        return
    product_id = Prompt.ask("ID del producto")
    sender = Prompt.ask("Remitente")
    receiver = Prompt.ask("Destinatario")
    try:
        shipment = manager.create_shipment(product_id, sender, receiver)
        console.print(f"[green]✅ Envío creado con ID: [bold]{shipment.shipment_id}[/bold][/green]")
    except ValueError as e:
        console.print(f"[red]❌ Error: {e}[/red]")


def _option_update_shipment() -> None:
    console.print(Panel("[bold]Actualizar Estado de Envío[/bold]", border_style="yellow"))
    if not manager.shipments:
        console.print("[yellow]No hay envíos registrados.[/yellow]")
        return
    shipment_id = Prompt.ask("ID del envío")
    console.print("Estados: [1] en_transito  [2] entregado  [3] rechazado")
    opt = IntPrompt.ask("Estado", choices=["1", "2", "3"])
    status_map = {1: ShipmentStatus.IN_TRANSIT, 2: ShipmentStatus.DELIVERED, 3: ShipmentStatus.REJECTED}
    location = Prompt.ask("Ubicación actual")
    temp_str = Prompt.ask("Temperatura (Enter para omitir)", default="")
    temperature = float(temp_str) if temp_str else None
    try:
        results = manager.update_shipment(shipment_id, status_map[opt], location, temperature)
        console.print(f"[green]✅ Estado actualizado.[/green]")
        for r in results:
            color = "green" if r.success else "red"
            icon = "✅" if r.success else "❌"
            console.print(f"[{color}]{icon} Contrato {r.contract_id}: {r.message}[/{color}]")
    except ValueError as e:
        console.print(f"[red]❌ Error: {e}[/red]")


def _option_create_contract() -> None:
    console.print(Panel("[bold]Crear Smart Contract de Entrega[/bold]", border_style="magenta"))
    if not manager.shipments:
        console.print("[yellow]No hay envíos registrados.[/yellow]")
        return
    shipment_id = Prompt.ask("ID del envío")
    max_temp = float(Prompt.ask("Temperatura máxima permitida (°C)"))
    max_days = IntPrompt.ask("Días máximos para entrega")
    try:
        contract = manager.create_delivery_contract(shipment_id, max_temp, max_days)
        console.print(f"[magenta]✅ Contrato creado con ID: [bold]{contract.contract_id}[/bold][/magenta]")
    except ValueError as e:
        console.print(f"[red]❌ Error: {e}[/red]")


def _option_product_history() -> None:
    console.print(Panel("[bold]Historial de Trazabilidad[/bold]", border_style="blue"))
    product_id = Prompt.ask("ID del producto")
    history = manager.get_product_history(product_id)
    if not history:
        console.print("[yellow]Sin historial para ese producto.[/yellow]")
        return
    table = Table(title=f"Trazabilidad: {product_id}", box=box.ROUNDED, border_style="blue")
    table.add_column("Bloque", style="cyan", width=7)
    table.add_column("Tipo", style="yellow")
    table.add_column("Timestamp", style="dim")
    table.add_column("Hash", style="dim")
    for event in history:
        table.add_row(
            str(event.get("block_index", "-")),
            event.get("tipo", "-"),
            event.get("timestamp", "-")[:19],
            event.get("block_hash", "-"),
        )
    console.print(table)


def _option_view_chain() -> None:
    console.print(Panel("[bold]Cadena de Bloques[/bold]", border_style="cyan"))
    table = Table(box=box.ROUNDED, border_style="cyan")
    table.add_column("#", style="bold cyan", width=5)
    table.add_column("Tipo", style="yellow")
    table.add_column("Hash", style="green")
    table.add_column("Anterior", style="dim")
    table.add_column("Nonce", style="dim", width=8)

    for block in manager.blockchain.chain:
        table.add_row(
            str(block.index),
            block.data.get("tipo", "genesis"),
            block.hash[:20] + "...",
            block.previous_hash[:16] + "...",
            str(block.nonce),
        )
    console.print(table)


def _option_verify_integrity() -> None:
    valid = manager.verify_chain_integrity()
    if valid:
        console.print(Panel("[bold green]✅ La cadena de bloques es VÁLIDA e íntegra.[/bold green]", border_style="green"))
    else:
        console.print(Panel("[bold red]❌ ¡La cadena ha sido COMPROMETIDA![/bold red]", border_style="red"))


def _run_demo() -> None:
    """Demo automático con Rich: farmacéutico falla por temperatura, electrónico se entrega."""
    from time import sleep
    from rich.progress import Progress, SpinnerColumn, TextColumn

    console.print()
    console.print(Panel(
        "[bold cyan]🚀 DEMO AUTOMÁTICO — CADENA DE SUMINISTRO CON SMART CONTRACTS[/bold cyan]\n"
        "[dim]Simulación completa: productos, envíos, contratos, trazabilidad[/dim]",
        border_style="cyan",
    ))

    # ── 1. Registrar productos ──────────────────────────────────────────────
    console.rule("[bold yellow]PASO 1 · Registro de Productos")

    pharma = Product(
        product_id="FARM-001",
        name="Vacuna BioShield",
        origin="Monterrey, NL",
        manufacturer="BioMex Laboratorios",
        batch_number="LOT-2026-004",
        manufacture_date=date(2026, 1, 15),
        expiry_date=date(2027, 1, 15),
    )
    elec = Product(
        product_id="ELEC-001",
        name="Sensor IoT Industrial",
        origin="Guadalajara, Jalisco",
        manufacturer="TechMex Industries",
        batch_number="LOT-2026-021",
        manufacture_date=date(2026, 3, 1),
    )

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
        t = progress.add_task("Registrando productos en blockchain...", total=None)
        manager.register_product(pharma)
        manager.register_product(elec)
        progress.update(t, completed=True)

    prod_table = Table(title="Productos Registrados", box=box.ROUNDED, border_style="green")
    prod_table.add_column("ID", style="cyan")
    prod_table.add_column("Nombre", style="white")
    prod_table.add_column("Fabricante", style="yellow")
    prod_table.add_column("Lote", style="dim")
    prod_table.add_column("Cadena Frío", style="magenta")

    prod_table.add_row("FARM-001", "Vacuna BioShield", "BioMex Laboratorios", "LOT-2026-004", "🥶 Sí (≤8°C)")
    prod_table.add_row("ELEC-001", "Sensor IoT Industrial", "TechMex Industries", "LOT-2026-021", "➖ No")
    console.print(prod_table)

    # ── 2. Crear envíos ─────────────────────────────────────────────────────
    console.rule("[bold yellow]PASO 2 · Creación de Envíos")
    shipment_pharma = manager.create_shipment("FARM-001", "BioMex Monterrey", "Hospital General Cananea")
    shipment_elec = manager.create_shipment("ELEC-001", "TechMex Guadalajara", "Planta Industrial Hermosillo")
    console.print(f"  [cyan]Envío farmacéutico:[/cyan] [bold]{shipment_pharma.shipment_id}[/bold]")
    console.print(f"  [cyan]Envío electrónico:[/cyan]  [bold]{shipment_elec.shipment_id}[/bold]")

    # ── 3. Crear smart contracts ─────────────────────────────────────────────
    console.rule("[bold yellow]PASO 3 · Smart Contracts")
    contract_pharma = manager.create_delivery_contract(shipment_pharma.shipment_id, max_temp=8.0, max_days=3)
    contract_elec = manager.create_delivery_contract(shipment_elec.shipment_id, max_temp=40.0, max_days=7)

    c_table = Table(title="Contratos Creados", box=box.ROUNDED, border_style="magenta")
    c_table.add_column("ID Contrato", style="magenta")
    c_table.add_column("Envío", style="cyan")
    c_table.add_column("Condición Temperatura", style="yellow")
    c_table.add_column("Condición Estado", style="yellow")
    c_table.add_row(contract_pharma.contract_id, shipment_pharma.shipment_id, "temperatura ≤ 8°C", "estado == entregado")
    c_table.add_row(contract_elec.contract_id, shipment_elec.shipment_id, "temperatura ≤ 40°C", "estado == entregado")
    console.print(c_table)

    # ── 4. Simulación de movimientos ─────────────────────────────────────────
    console.rule("[bold yellow]PASO 4 · Simulación de Movimientos")

    moves_table = Table(title="Eventos de Transporte", box=box.ROUNDED, border_style="blue")
    moves_table.add_column("Envío", style="cyan", width=12)
    moves_table.add_column("Producto", style="white")
    moves_table.add_column("Ubicación", style="yellow")
    moves_table.add_column("Estado", style="dim")
    moves_table.add_column("Temp °C", style="magenta", justify="right")

    # Farmacéutico: excede temperatura → contrato fallará
    manager.update_shipment(shipment_pharma.shipment_id, ShipmentStatus.IN_TRANSIT, "Centro Distribución Hermosillo", 5.0)
    moves_table.add_row(shipment_pharma.shipment_id, "Vacuna BioShield", "Centro Dist. Hermosillo", "en_transito", "[green]5.0[/green]")

    manager.update_shipment(shipment_pharma.shipment_id, ShipmentStatus.IN_TRANSIT, "Bodega Nogales", 12.5)
    moves_table.add_row(shipment_pharma.shipment_id, "Vacuna BioShield", "Bodega Nogales", "en_transito", "[red bold]12.5 ⚠[/red bold]")

    # Electrónico: entrega correcta
    manager.update_shipment(shipment_elec.shipment_id, ShipmentStatus.IN_TRANSIT, "Almacén Guaymas", 28.0)
    moves_table.add_row(shipment_elec.shipment_id, "Sensor IoT", "Almacén Guaymas", "en_transito", "[green]28.0[/green]")

    console.print(moves_table)

    # ── 5. Entrega final y evaluación de contratos ───────────────────────────
    console.rule("[bold yellow]PASO 5 · Entrega Final y Evaluación de Contratos")

    results_pharma = manager.update_shipment(
        shipment_pharma.shipment_id, ShipmentStatus.DELIVERED, "Hospital General Cananea", 12.5
    )
    results_elec = manager.update_shipment(
        shipment_elec.shipment_id, ShipmentStatus.DELIVERED, "Planta Industrial Hermosillo", 28.0
    )

    for result in results_pharma:
        color = "green" if result.success else "red"
        icon = "✅" if result.success else "❌"
        console.print(Panel(
            f"[{color}]{icon}  Contrato Farmacéutico [{result.contract_id}]\n"
            f"[bold]{result.message}[/bold][/{color}]",
            border_style=color,
        ))

    for result in results_elec:
        color = "green" if result.success else "red"
        icon = "✅" if result.success else "❌"
        console.print(Panel(
            f"[{color}]{icon}  Contrato Electrónico [{result.contract_id}]\n"
            f"[bold]{result.message}[/bold][/{color}]",
            border_style=color,
        ))
        if result.success:
            for action in result.executed_actions:
                console.print(f"   [green]→ {action['mensaje']}[/green]")

    # ── 6. Trazabilidad ─────────────────────────────────────────────────────
    console.rule("[bold yellow]PASO 6 · Trazabilidad de Productos")
    for pid, pname in [("FARM-001", "Vacuna BioShield"), ("ELEC-001", "Sensor IoT Industrial")]:
        hist = manager.get_product_history(pid)
        trace_table = Table(title=f"Trazabilidad: {pname}", box=box.SIMPLE, border_style="blue")
        trace_table.add_column("Bloque", style="cyan", width=7)
        trace_table.add_column("Tipo", style="yellow")
        trace_table.add_column("Hash", style="dim")
        for event in hist:
            trace_table.add_row(str(event["block_index"]), event.get("tipo", "-"), event.get("block_hash", "-"))
        console.print(trace_table)

    # ── 7. Verificación de integridad ────────────────────────────────────────
    console.rule("[bold yellow]PASO 7 · Integridad de la Blockchain")
    valid = manager.verify_chain_integrity()
    color = "green" if valid else "red"
    icon = "✅" if valid else "❌"
    console.print(f"[{color}]{icon} Integridad de la cadena: {'VÁLIDA' if valid else 'COMPROMETIDA'}[/{color}]")

    # ── 8. Resumen final ─────────────────────────────────────────────────────
    console.rule("[bold yellow]RESUMEN FINAL")
    summary = manager.get_chain_summary()
    s_table = Table(box=box.ROUNDED, border_style="cyan", title="Estadísticas del Sistema")
    s_table.add_column("Métrica", style="bold white")
    s_table.add_column("Valor", style="bold cyan", justify="right")
    s_table.add_row("Total de bloques", str(summary["total_bloques"]))
    s_table.add_row("Productos registrados", str(summary["total_productos"]))
    s_table.add_row("Envíos creados", str(summary["total_envios"]))
    s_table.add_row("Smart contracts", str(summary["total_contratos"]))
    s_table.add_row("Dificultad PoW", str(summary["dificultad"]))
    s_table.add_row("Integridad", "[green]✅ Válida[/green]" if summary["integridad_valida"] else "[red]❌ Inválida[/red]")
    console.print(s_table)

    console.print(Panel(
        "[bold cyan]Demo finalizado.[/bold cyan]\n"
        "[dim]Blockchain · Smart Contracts · Trazabilidad — TECNM Campus Cananea, 2026[/dim]",
        border_style="cyan",
    ))


def main() -> None:
    """Punto de entrada de la CLI interactiva."""
    _header()

    dispatch = {
        "1": _option_register_product,
        "2": _option_create_shipment,
        "3": _option_update_shipment,
        "4": _option_create_contract,
        "5": _option_product_history,
        "6": _option_view_chain,
        "7": _option_verify_integrity,
        "8": _run_demo,
    }

    while True:
        console.print()
        _menu()
        choice = Prompt.ask("\n[bold cyan]Elige una opción[/bold cyan]", choices=[str(i) for i in range(1, 10)])

        if choice == "9":
            console.print("[cyan]👋 Hasta pronto.[/cyan]")
            break

        handler = dispatch.get(choice)
        if handler:
            console.print()
            handler()


if __name__ == "__main__":
    main()
