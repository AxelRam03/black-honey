# Binance Spot Bot — paper trading only

Este directorio contiene un prototipo experimental de Binance Spot con velas de 1 hora. El backtest y el bot en modo paper no envían órdenes reales.

## Ejecutar backtest histórico

Requiere Python 3.12+ y conexión a Internet para descargar velas públicas; no requiere cuenta de Binance ni claves API.

```bash
cd trading-bot
python -m pip install -r requirements.txt
PYTHONPATH=. python -m app.backtest
```

El comando consulta hasta 999 velas horarias cerradas para cada símbolo configurado (por defecto BTCUSDT y ETHUSDT) y muestra un reporte JSON con saldo inicial/final, PnL, retorno, drawdown y operaciones simuladas. Puedes configurar `SYMBOLS`, `BACKTEST_STARTING_BALANCE`, `FEE_RATE` y `BINANCE_BASE_URL` mediante variables de entorno.

## Limitaciones importantes

- Es una primera herramienta de investigación, no una garantía de rentabilidad ni una simulación exacta de exchange.
- Usa una estrategia long-only experimental y una estimación simple de comisiones; no modela deslizamiento, liquidez, órdenes parciales, latencia, impuestos ni mínimos de cada par.
- Si el stop y el objetivo se tocan dentro de la misma vela, el backtest supone de forma conservadora que el stop ocurre primero.
- El resultado de las velas recientes no predice rendimientos futuros; antes de valorar la estrategia hacen falta más datos, validación fuera de muestra y revisión de la lógica de riesgo.

## Seguridad

- No se requieren claves privadas ni secretos para el backtest o paper mode.
- No guardes archivos `.env` ni secretos en el repositorio.
- No habilites órdenes reales hasta completar validaciones adicionales, pruebas en entorno de prueba, validación de mínimos, manejo de órdenes parciales y reconciliación de estado.
