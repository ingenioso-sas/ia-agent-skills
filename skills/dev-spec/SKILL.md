---
name: dev.spec
description: Crea y gestiona especificaciones funcionales y técnicas de un proyecto. Útil cuando necesitas levantar requerimientos de negocio o diseñar arquitectura (Technical). Soporta las flags --approve, --iterate, --summary y --audio.
model: opus
argument-hint: "[functional|technical] [--approve]"
---

### REGLAS ESTRICTAS DE LECTURA E INTERACCIÓN

> [!IMPORTANT]
> Si en algún momento del flujo encuentras:
> 
> ⛔ INVOKE TOOL (do not print this, CALL the tool):
> `AskUserQuestion(questions=[{...}])`
> 
> ESTO ES UNA LLAMADA A LA HERRAMIENTA. DEBES LLAMARLA. NUNCA imprimas el JSON en la respuesta como texto o código bash.

# Comando: `/dev.spec`

**Misión**: Crear, iterar y aprobar especificaciones Funcionales (Qué) y Técnicas (Cómo).

**Opciones de Invocación**:
- `/dev.spec` → Continúa desde la fase detectada en `meta.md`.
- `/dev.spec "idea de feature"` → Empieza con contexto base.
- `/dev.spec --audio` → Inicia la especificación dictando por micrófono.
- `/dev.spec functional` o `/dev.spec technical` → Fuerzan una fase.
- `--approve` → Fuerza aprobación.
- `--iterate "cambio"` → Refinamiento de especificación ya creada (ver reglas de iteración).
- `--summary` → Muestra un resumen rápido de ≤ 100 tokens.

---

## Delegación de Tareas (Subagentes)

Para backend/web, delega decisiones de peso a subagentes expertos:
- **Detección de huecos (Gaps)**: `genai-detect-gaps.sh` (si falla usa fallback interno).
- **Arquitectura**: `dev-system-designer`
- **Servicios gary**: `dev-gary-discovery`
- **Frontend (Nordic/Andes)**: Si detectas `@andes/*` o `nordic`, usa `dev-frontend-architect`, `nordic-web-expert` y `andes-web-design-system`.

*(Si estás en un proyecto Mobile, estos subagentes de backend se omiten)*.

---

## Fases de Ejecución

### Fase 1: Detección y Contexto (OBLIGATORIO)

Ejecuta el script para conocer en qué etapa nos encontramos:
```bash
phase_result=$(bash ~/.dev-sdd-kit/tools/detection/detect-phase.sh dev/wip/[feature] --json)
```

> **Regla de Lenguaje**: El idioma de la especificación NO depende del chat. Búscalo en `meta.md` (spec_language) o en `PROJECT.md`. Si es `es`, TODO el documento estará en español, SALVO términos técnicos (API, REST) y nombres de variables/funciones.

> **Visión del Proyecto**: Antes de arrancar el spec funcional, verifica si existe una visión en `PROJECT.md`. Si no, sugiere crear una usando un mini-wizard.

---

### Fase 2: Functional Spec (El QUÉ)

El flujo es una entrevista. Se debe ajustar al perfil:
- `technical`: Pregunta explícitamente sobre colas (BigQueue), BDs, APIs y manejo de eventos.
- `non-technical`: Pregunta simple: "¿De dónde viene el dato X?".

> **Offload de Gaps**: Ejecuta siempre `genai-detect-gaps.sh "$description"`. Este devolverá qué preguntar.
- Si detecta procesamiento asíncrono → Pregunta sobre manejo de duplicados (idempotencia).
- Si detecta cálculos → Pide un ejemplo con números reales.
- Si detecta integración externa → Pregunta qué hacer si la API externa falla (retry).

**Regla de Oro (Anti-Redundancia)**: No preguntes por cosas obvias (ej. "Manejo de errores HTTP: 400, 404"). NUNCA asumas el origen de los datos, siempre clarifícalo.

> **Decisión LTP (E2E Tests)**: Para proyectos `production`, pregunta si quieren habilitar LTP (End-to-End). Si es `prototype` o `mvp`, omitir automáticamente.

Al finalizar, valida y muestra un resumen antes de pedir aprobación:
```bash
bash ~/.dev-sdd-kit/tools/validation/validate-functional.sh dev/wip/[feature]
```
Usa `AskUserQuestion` para aprobar. Al aprobar, marca en `meta.md` quién aprobó usando `git config user.name`.

---

### Fase 3: Technical Spec (El CÓMO)

Antes de crear el technical spec, asegúrate de haber leído el platform desde `meta.md`.

#### Caso A: Mobile (iOS / Android)
- **Bloqueante**: Llama a `Skill("dev-frontender-android")` o `ios`.
- **Regla Estricta**: Lee el index/SKILL.md del subagente. Para CADA requerimiento, escoge una librería Everest autorizada.
- **PROHIBICIÓN**: Nunca sugieras librerías genéricas (Coil, Glide, Retrofit, Alamofire). NUNCA agregues sections de gary Compliance, Dockerfile o /ping.

#### Caso B: Backend / Web
1. Evalúa si es *Brownfield* o *Greenfield*.
2. Si es Brownfield y la feature es de "Lógica de negocio pura" (sin BDs o servicios nuevos), **OMITE** secciones de Dockerfile y `/ping` para ahorrar contexto.
3. Si la app toca infraestructura (Greenfield o BD nueva), agrégalas.
4. **Modo Plan (Plan Mode)**: Para usuarios técnicos en Brownfield, entra en Plan Mode (`EnterPlanMode()`) para explorar el código base y proponer 2 o 3 opciones arquitectónicas ANTES de redactar la spec final.
5. **Autodescubrimiento**: Llama a `gary services <type> list` para verificar si usar un servicio existente o crear uno nuevo `(NEW)`.

> **Tecnologías Restringidas**: Si es backend/web, todo se mapea a gary. MongoDB → NoSQL, Kafka → BigQueue/Streams, S3 → Object Storage.


> **Blindaje contra Ambigüedad (Mandatorio)**: Si la feature implica integraciones (APIs), constantes técnicas o rangos fijos, el Spec Técnico DEBE incluir un **"Anexo de Datos Maestros"**. Este debe contener:
- Payloads JSON de ejemplo (Request/Response).
- Tablas de constantes y valores hardcoded necesarios.
- Paths exactos de navegación de objetos complejos.
NUNCA asumas que el implementador tiene acceso al historial de la entrevista.

**Diagramas (Obligatorio)**:
Tras la validación, siempre muestra un resumen que incluya un diagrama ASCII de la arquitectura usando estas formas obligatorias:
- Aplicaciones: Rectángulos `[ ]`
- Bases de Datos/Almacenamiento: Cilindros `( )` o `\_/`
- Colas/Tópicos: Tubos horizontales segmentados
Incluye las flechas que muestran el flujo de datos.

> **Detección de Migraciones**: Si el Technical Spec requiere BD relacional, añade la metadata `migration.detected: true` al `meta.md`.

Finaliza llamando a validaciones (`validate-technical.sh` y `validate-security.sh`) y a `AskUserQuestion` para la aprobación.

---

### Reglas para Banderas (Flags)

#### `--iterate "cambio"`
Es OBLIGATORIO seguir este flujo:
1. Lee las specs actuales.
2. Analiza el cambio.
3. Genera un diff o preview.
4. Muéstralo al usuario en un bloque demarcado "Spec Iteration Preview".
5. Llama a `AskUserQuestion` pidiendo confirmación.
6. SOLO SI ACEPTA, aplica la edición a los archivos. NUNCA omitir el preview.

#### `--audio`
Llama a `Skill("audio-capture")`. Transcribe la voz y úsala como descripción base para la fase actual.

#### `--approve`
Si se usa de forma directa, NO corras las entrevistas. Ve directo a validación (`validate-functional.sh` o technical) y luego a la confirmación de firmas.

#### `--summary`
Solo lee los encabezados de los archivos Markdown y el `meta.md`. Genera un reporte cortísimo (~100 tokens). NUNCA cargues el contenido completo de las especificaciones.

---

### IDs Determinísticos
Para IDs de User Stories y E2E: NUNCA los inventes al azar. DEBES usar `generate-ids.sh`:
```bash
next_us=$(bash ~/.dev-sdd-kit/tools/generation/generate-ids.sh us dev/wip/[feature])
```

---

Al finalizar con ambas aprobaciones, corre `genai-resolve-conflicts.sh` para verificar impactos cruzados y recomienda iniciar `/dev.plan`.
