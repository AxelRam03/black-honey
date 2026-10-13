# Binance Spot Bot — paper trading only

Este directorio aloja un prototipo de simulación del bot de Binance Spot con velas de 1 hora. Está separado del proyecto principal y **no envía órdenes reales**.

## Parámetros objetivo
- Mercado: Binance Spot
- Pares de observación: BTCUSDT y ETHUSDT
- Temporalidad: 1h
- Capital objetivo: menos de 1000 MXN (requiere conversión MXN/USDT fiable antes de dimensionar posiciones reales)
- Ejecución: paper mode

## Principios de seguridad
- No requiere claves API en modo simulación.
- No guardar `.env` ni secretos en el repositorio.
- No habilitar órdenes reales hasta completar backtesting, pruebas en Binance Demo/Testnet, validación de mínimos de órdenes, manejo de órdenes parciales y reconciliación de estado.
- La estrategia es experimental y no garantiza rentabilidad.

## Estado
Solo documentación inicial en esta rama. El código ejecutable deberá añadirse y probarse antes de ejecutar el bot.
