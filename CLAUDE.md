# Reglas para asistentes IA — Equipo 5

- Antes de cambiar el dashboard, leer `README.md`, `contrato-datos.md` y `src/contrato_datos.py`.
- No inventar unidades ni monedas, en particular `Lifetime_Value`, `Average_Order_Value` y `Credit_Balance` no tienen moneda documentada.
- Mantener separadas las cifras observadas en CSV, las calculadas en Python, las predicciones del modelo y los escenarios hipotéticos.
- No sustituir valores ausentes o `N/A` por cero sin autorización del equipo.
- Si se cambia una regla del contrato de datos, ajustar y ejecutar sus pruebas, justificar la decisión y registrar el cambio.
- Ejecutar `python -m unittest discover -s tests -v` antes de proponer integrar cambios, indicar cuáles pasaron o fallaron, nunca afirmar que se ejecutaron si no ocurrió.
- No cambiar sin justificación la regla del perfil de riesgo, la meta del 5% o la forma de calcular denominadores.
- Corregir primero la causa del fallo, no borrar controles para conseguir una prueba verde.
