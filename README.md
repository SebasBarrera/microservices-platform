# Plataforma para el Monitoreo de la Interoperabilidad en Ecosistemas de Microservicios Basada en *Arquitectura de Eventos*

Este repositorio proporciona los lineamientos para implementar una plataforma que facilite el monitoreo de la interoperabilidad entre microservicios desplegados en **AWS**. La solución hace uso de patrones de diseño en sistemas distribuidos (HeartBeat, Idempotent Receiver, Lamport Clock, Versioned Value, Write-Ahead Log) y aprovecha servicios administrados como **ECS**, **ECR**, **SQS**, **SNS**, **Lambda**, **DynamoDB**, **CloudWatch** y **X-Ray**. El objetivo es lograr escalabilidad, resiliencia, trazabilidad y eficiencia en la comunicación entre microservicios.

## Contenido

- [Introducción](#introducción)
- [Arquitectura General](#arquitectura-general)
- [Patrones de Diseño Integrados](#patrones-de-diseño-integrados)
- [Estructura del Repositorio](#estructura-del-repositorio)
- [Prerrequisitos](#prerrequisitos)
- [Preparación del Entorno](#preparación-del-entorno)
- [Configuración en AWS](#configuración-en-aws)
- [Implementación de la Plataforma](#implementación-de-la-plataforma)
- [Despliegue de Contenedores y Servicios](#despliegue-de-contenedores-y-servicios)
- [Monitoreo y Trazabilidad](#monitoreo-y-trazabilidad)
- [Pruebas y Validación](#pruebas-y-validación)
- [Mejores Prácticas](#mejores-prácticas)
- [Mejoras Futuras](#mejoras-futuras)

## Introducción

El uso de microservicios ha transformado la manera de desarrollar aplicaciones, permitiendo mayor flexibilidad y una entrega más ágil de nuevas funcionalidades. Sin embargo, a medida que las aplicaciones se dividen en múltiples servicios, la necesidad de asegurar que todos se comuniquen bien, se puedan monitorear y se detecten fallos a tiempo, se vuelve crítica. Esta plataforma busca resolver ese reto integrando patrones de diseño reconocidos con herramientas sencillas y servicios de AWS, mejorando así la resiliencia y eficiencia del ecosistema de microservicios.

## Arquitectura General

La plataforma se basa en una *arquitectura de eventos*, donde los microservicios se comunican usando *SNS* y *SQS*. Se emplean funciones *Lambda* para procesar señales de salud (HeartBeat), *DynamoDB* para almacenar estados versionados e información sobre operaciones antes de aplicar cambios, *CloudWatch* y *X-Ray* para obtener métricas y trazas, y *ECS* (o *EKS*) para orquestar contenedores. La idea es que los microservicios envíen eventos asíncronos, se puedan detectar fallos, ordenar eventos sin relojes físicos, procesar eventos una sola vez y mantener versiones históricas del estado.

## Patrones de Diseño Integrados

1. **HeartBeat:** Los microservicios envían señales periódicas indicando su estado. Una Lambda las procesa y actualiza métricas en CloudWatch, permitiendo detectar servicios caídos.
2. **Idempotent Receiver:** Antes de procesar un evento, se verifica si ya se procesó. Así se evita procesar el mismo evento dos veces.
3. **Lamport Clock:** Se usan contadores lógicos para ordenar y sincronizar eventos sin depender de relojes físicos.
4. **Versioned Value:** El estado de los microservicios se almacena con versiones, lo que permite rastrear cambios en el tiempo y volver a estados previos.
5. **Write-Ahead Log:** Antes de cambiar el estado, se registra la operación en un log, asegurando la integridad de datos ante fallos.

## Estructura del Repositorio

La estructura recomendada es la siguiente:


```bash
microservices-platform/
├── service-a/
│   ├── app.py
│   └── Dockerfile
├── service-b/
│   ├── app.py
│   └── Dockerfile
├── lambda-functions/
│   └── heartbeat_processor.py
├── infrastructure/ 
├── README.md
└── .gitignore
```

En `service-a` y `service-b` se definen los contenedores, en `lambda-functions` las funciones Lambda.

## Prerrequisitos

- Cuenta de AWS con permisos para SNS, SQS, ECS, ECR, DynamoDB, Lambda, CloudWatch, X-Ray.
- Docker instalado localmente.
- Git para clonar y gestionar el repositorio.
- AWS CLI configurada.
- Editor de texto o IDE para ajustes locales.

## Preparación del Entorno

1. Clonar el repositorio:
   Ir a la terminal local y ejecutar:
   `git clone https://github.com/tu-usuario/microservices-platform.git`
   
2. Entrar al repositorio:  
   `cd microservices-platform`

3. Crear y ajustar `.gitignore`, `README.md` u otros archivos necesarios.

4. Hacer el primer commit:
   - `git add .`
   - `git commit -m "Estructura inicial del proyecto"`
   - `git push origin main`

## Configuración en AWS

### Tablas DynamoDB

Crear tres tablas en la consola de DynamoDB:
- `IdempotencyTable`: Clave primaria `RequestID` (String).
- `VersionedState`: Clave primaria `ServiceID` (String), Sort key: `VersionNumber` (Number).
- `WriteAheadLog`: Clave primaria `LogID` (String).

### Tema SNS y Cola SQS

- Crear un tema SNS: `HeartbeatTopic`.
- Crear una cola SQS: `ServiceBQueue`.
- Suscribir la cola `ServiceBQueue` al tema `HeartbeatTopic`.

### Función Lambda para HeartBeat

- Crear una Lambda `HeartbeatProcessor` (por ejemplo con Python 3.8).
- Configurar el disparador SNS con el `HeartbeatTopic`.
- Asegurar permisos en la Lambda para escribir métricas en CloudWatch.

## Implementación de la Plataforma

1. **Microservicio A (service-a)**: Envía HeartBeats y eventos con marcas lógicas. Esto permite detectar fallos y mantener orden en los eventos.
2. **Microservicio B (service-b)**: Recibe eventos, verifica si ya se procesaron (Idempotent Receiver), registra la operación en el Write-Ahead Log antes de aplicar cambios, y actualiza el estado en Versioned Value.
3. **Lambda HeartBeatProcessor**: Procesa las señales de HeartBeat, actualiza métricas en CloudWatch.
4. **CloudWatch & X-Ray**: Proporcionan métricas, registros y trazabilidad, ayudando a monitorear la interoperabilidad y el desempeño.

## Despliegue de Contenedores y Servicios

1. Crear repositorios ECR para `service-a` y `service-b`.
2. Construir y subir las imágenes Docker a ECR.
3. En ECS, crear un clúster Fargate (`MicroservicesCluster`).
4. Definir las Task Definitions para `service-a` y `service-b` usando las imágenes de ECR.
5. Ejecutar las tareas en el clúster, seleccionando subredes, grupos de seguridad y otros ajustes.

## Monitoreo y Trazabilidad

- **HeartBeat:** Métricas en CloudWatch bajo el namespace `Microservices`.
- **Idempotent Receiver, Lamport Clock, Versioned Value, Write-Ahead Log:** Se reflejan en el comportamiento correcto del sistema al procesar eventos.
- **X-Ray:** Permite ver el mapa de servicios y rastrear transacciones entre microservicios, identificando cuellos de botella o problemas.

## Pruebas y Validación

1. Revisar la cola SQS y asegurar que los eventos llegan a `service-b`.
2. Verificar en DynamoDB que `IdempotencyTable` registra eventos procesados, `VersionedState` mantiene versiones y `WriteAheadLog` guarda operaciones.
3. Observar en CloudWatch las métricas de HeartBeat, confirmando que `service-a` manda señales periódicamente.
4. Consultar X-Ray para trazar el flujo entre `service-a` y `service-b`.
5. Simular fallos: detener `service-a` y ver si HeartBeat deja de aparecer, generando alertas.

## Mejores Prácticas

- Asignar roles IAM con permisos mínimos necesarios.
- Ajustar recursos (CPU, memoria, frecuencia de envío de eventos) según la carga esperada.
- Automatizar la infraestructura con CDK.
- Monitorear costos y métricas continuamente para optimizar el gasto.
- Mantener el repositorio organizado, usando ramas y pull requests.

## Mejoras Futuras

- Integrar *circuit breakers* o *API gateways* para mayor resiliencia.
- Realizar pruebas de carga intensivas para evaluar la capacidad de escalar.
- Añadir más herramientas de seguridad y auditoría de eventos.
- Extender el enfoque a entornos híbridos o diferentes *public cloud service providers*.
