# Seguridad y alcance del prototipo

Este es un proyecto educativo en fase inicial. El contenido actual es documentación y configuración para desarrollar en paper mode; todavía no contiene un ejecutor de órdenes real.

## Reglas obligatorias
1. `LIVE_TRADING=false` siempre durante desarrollo.
2. No crear ni almacenar claves API para pruebas públicas.
3. No operar con fondos reales hasta que se implementen y prueben backtesting con comisiones/slippage, lógica de stop, mínimos y filtros de símbolos, órdenes parciales, reintentos idempotentes, reconciliación de saldo/órdenes, límites de pérdida persistentes, alertas y recuperación después de reinicio.
4. Spot solamente; sin margen ni apalancamiento.
5. El riesgo presupuestado no garantiza la pérdida máxima real. Slippage, gaps y fallos pueden excederlo.
6. Capital inferior a 1000 MXN puede no satisfacer el mínimo de orden de algunos pares. Convertir MXN a USDT con una cotización fiable y verificar `LOT_SIZE`, `MIN_NOTIONAL`/`NOTIONAL` y filtros actuales de Binance antes de cualquier orden futura.
7. Nunca activar permisos de retiro o transferencia en una clave de trading. Restringir la clave a una IP fija cuando sea posible.

## Validación futura
- Pruebas unitarias e integración en un entorno de demostración compatible con Binance.
- Backtesting out-of-sample y paper trading durante un periodo suficiente.
- Confirmar manualmente el estado de cada orden incierta antes de reintentar.
- Revisión de código antes de cualquier habilitación de live.
