# Valores de control del tablero

Cifras calculadas directamente desde `data/exportaciones/base_consolidada_pqrs.csv` (exportado el 6 de noviembre de 2026).
Úselas para comprobar que cada medida de Power BI da el mismo resultado, **sin filtros aplicados**.

> Las cifras de plazo (vencidas, días para vencer, antigüedad) dependen de la fecha de exportación. Si exporta de nuevo la base, estas cambian y las demás no.

## Medidas

| Medida | Valor esperado |
|---|---:|
| Total PQRS | 12.000 |
| Promedio días de respuesta (texto) | Sin datos aún |
| PQRS con fecha de solución | 0 |
| Plazo promedio otorgado (días) | 30 |
| Solucionadas | 3.991 |
| Tasa de resolución | 33,3 % |
| PQRS activas | 8.009 |
| Vencidas | 8.009 |
| Próximas a vencer | 0 |
| Al día | 0 |
| % vencidas sobre activas | 100,0 % |
| Antigüedad promedio activas (días) | 175 |
| Retraso promedio vencidas (días) | 145 |
| PQRS por registrador (promedio) | 1.000 |
| Registradores activos | 12 |
| % Comunidad UdeA | 16,8 % |

## PQRS por tipo

| tipo_solicitud | Total PQRS | % del total |
|---|---:|---:|
| Petición | 3.000 | 25,0 % |
| Queja | 3.000 | 25,0 % |
| Reclamo | 3.000 | 25,0 % |
| Sugerencia | 3.000 | 25,0 % |

## 1. Tipo de mascota

| tipo_mascota | Total PQRS | % del total |
|---|---:|---:|
| Otro | 4.081 | 34,0 % |
| Perro | 4.027 | 33,6 % |
| Gato | 3.892 | 32,4 % |

## 2. Canal de recepción

| canal_recepcion | Total PQRS | % del total |
|---|---:|---:|
| Otro | 2.082 | 17,4 % |
| Teléfono | 2.031 | 16,9 % |
| Redes sociales | 1.989 | 16,6 % |
| Página web | 1.978 | 16,5 % |
| Presencial | 1.972 | 16,4 % |
| Correo electrónico | 1.948 | 16,2 % |

## 3. Campus

| campus_relacionado | Total PQRS | % del total |
|---|---:|---:|
| Campus Medellín - Ciudad Universitaria | 1.370 | 11,4 % |
| Campus Medellín - Edificio San Ignacio | 1.361 | 11,3 % |
| Campus en el Área de la salud | 1.350 | 11,2 % |
| Campus Medellín - Casas Patrimoniales | 1.348 | 11,2 % |
| Campus Medellín - Antigua Escuela de Derecho | 1.344 | 11,2 % |
| Campus Medellín - Ciudadela Robledo | 1.322 | 11,0 % |
| Campus Medellín - Edificio Antioquia | 1.309 | 10,9 % |
| Campus Medellín - Edificio de Extensión | 1.300 | 10,8 % |
| Campus Medellín - Sede de Posgrado | 1.296 | 10,8 % |

## 4. Estado de la PQRS

| estado_peticion | Total PQRS | % del total |
|---|---:|---:|
| Registrada | 4.041 | 33,7 % |
| En proceso | 3.968 | 33,1 % |
| Solucionada | 3.991 | 33,3 % |

## 5. Vencidas por rango de retraso

| Rango de retraso | Vencidas | % de las vencidas |
|---|---:|---:|
| 1. 1 a 30 días | 721 | 9,0 % |
| 2. 31 a 90 días | 1.679 | 21,0 % |
| 3. 91 a 180 días | 2.630 | 32,8 % |
| 4. Más de 180 días | 2.979 | 37,2 % |

## 6. Perfil del solicitante (derivado)

| perfil_solicitante | Total PQRS | % del total |
|---|---:|---:|
| Ciudadano externo | 7.605 | 63,4 % |
| Organización (NIT) | 2.382 | 19,9 % |
| Comunidad UdeA | 2.013 | 16,8 % |

## 6. Rol del registrador

| rol_registrador | Total PQRS | % del total |
|---|---:|---:|
| Operador | 7.964 | 66,4 % |
| Supervisor | 2.058 | 17,1 % |
| Administrador | 1.978 | 16,5 % |
