# Binance Spot Bot — paper trading only

Este directorio contiene un prototipo experimental de Binance Spot con velas de 1 hora. El backtest y el bot en modo paper no envían órdenes reales.

## Ejecutar el bot en simulación (sin dinero real)

Este proceso necesita estar encendido en una computadora o servidor con Python 3.12+ e Internet. **No se ejecuta directamente como proceso permanente dentro de la app de iPhone.** No requiere iniciar sesión en Binance ni crear claves API.

En Windows, abre PowerShell en la carpeta del repositorio y ejecuta:

```powershell
cd trading-bot
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
$env:PAPER_QUOTE_BALANCE = "100"
$env:SYMBOLS = "BTCUSDT,ETHUSDT"
$env:DB_PATH = "bot.sqlite3"
$env:BINANCE_BASE_URL = "https://data-api.binance.vision"
$env:POLL_SECONDS = "60"
$env:FEE_RATE = "0.001"
$env:RISK_PER_TRADE = "0.001"
$env:MAX_DAILY_LOSS = "0.005"
$env:MAX_DRAWDOWN = "0.02"
$env:MAX_POSITION_FRACTION = "0.10"
PYTHONPATH=. python -m app.main
```

Si PowerShell bloquea la activación del entorno virtual, puedes saltarte la activación y usar `.venv\Scripts\python.exe -m pip install -r requirements.txt` y después `.venv\Scripts\python.exe -m app.main`.

Para detenerlo, pulsa `Ctrl+C`. El historial de eventos se guarda en `bot.sqlite3` (o en la ruta indicada por `DB_PATH`). No borres ni compartas ese archivo si quieres conservar tu historial local.

**Importante:** el bot solo simula compras y ventas; no envía órdenes reales. Debe mantenerse así mientras el backtest muestre pérdidas y no se haya validado con datos fuera de muestra y condiciones realistas. La simulación no equivale a una cuenta demo de Binance ni reproduce por completo las ejecuciones del mercado.

## Ejecutar backtest histórico

Requiere Python 3.12+ y conexión a Internet para descargar velas públicas; no requiere cuenta de Binance ni claves API.

```bash
cd trading-bot
python -m pip install -r requirements.txt
PYTHONPATH=. python -m app.backtest
```

El comando consulta hasta 999 velas horarias cerradas para cada símbolo configurado (por defecto BTCUSDT y ETHUSDT) y muestra un reporte JSON con saldo inicial/final, PnL, retorno, drawdown, número de operaciones, porcentaje de aciertos, factor de beneficio y PnL promedio por operación. Puedes configurar `SYMBOLS`, `BACKTEST_STARTING_BALANCE`, `FEE_RATE` y `BINANCE_BASE_URL` mediante variables de entorno.

## Último resultado de validación (13 de octubre de 2026)

Ejecución automática con hasta 999 velas horarias cerradas por par, saldo simulado inicial de 1,000 USDT por símbolo y comisión configurada de 0.1% por lado:

| Par | PnL neto | Retorno | Operaciones | Aciertos | Factor de beneficio | Drawdown máximo |
|---|---:|---:|---:|---:|---:|---:|
| BTCUSDT | -14.00 USDT | -1.40% | 20 | 30.0% | 0.61 | 1.73% |
| ETHUSDT | -24.95 USDT | -2.50% | 26 | 26.9% | 0.53 | 2.70% |

**Decisión:** estos resultados son negativos; esta estrategia no debe pasar a operaciones con dinero real. El backtest es limitado (muestra reciente, sin deslizamiento ni liquidez real) y no demuestra rentabilidad futura. El resultado sirve para detectar que aún hay trabajo de investigación, no como promesa de ingresos.

## Limitaciones importantes

- Es una primera herramienta de investigación, no una garantía de rentabilidad ni una simulación exacta de exchange.
- Usa una estrategia long-only experimental y una estimación simple de comisiones; no modela deslizamiento, liquidez, órdenes parciales, latencia, impuestos ni mínimos de cada par.
- Si el stop y el objetivo se tocan dentro de la misma vela, el backtest supone de forma conservadora que el stop ocurre primero.
- El resultado de las velas recientes no predice rendimientos futuros; antes de valorar la estrategia hacen falta más datos, validación fuera de muestra y revisión de la lógica de riesgo.

## Seguridad

- No se requieren claves privadas ni secretos para el backtest o paper mode.
- No guardes archivos `.env` ni secretos en el repositorio.
- No habilites órdenes reales hasta completar validaciones adicionales, pruebas en entorno de prueba, validación de mínimos, manejo de órdenes parciales y reconciliación de estado.
