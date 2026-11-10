# CFP20 – AMDELCO | Laboratorios de Ciberseguridad con IA y OpenCode

**Docente:** Damian Trajster  
**Entorno:** Windows (anfitrión) + Parrot OS (VirtualBox) + OpenCode  
**Público:** principiantes | **Duración sugerida:** 55–70 minutos (incluyendo instalación)  
**Fecha de revisión de instrucciones:** noviembre de 2026

> **Alcance:** usar solo máquinas y archivos propios, información ficticia y `127.0.0.1`. Nunca subir contraseñas auténticas, datos estudiantiles reales ni archivos privados a un modelo de IA. No ejecutar comandos que la IA proponga sin revisarlos.

## Resultados de aprendizaje

1. Conectar Windows con una VM Parrot usando SSH.
2. Instalar OpenCode en Parrot y seleccionar un modelo gratuito si está disponible.
3. Pedir una revisión de seguridad de un HTML sencillo y evaluar las conclusiones de la IA.
4. Crear con IA una pequeña aplicación Flask de reportes **ficticios**, probar validación, escape de HTML y cabeceras de seguridad.
5. Distinguir entre una mejora visual y un control de seguridad en el servidor.

---

# PARTE 0 — Preparación de Parrot y acceso por SSH

## 0.1. Comprobar la IP dentro de Parrot

En la terminal gráfica de **Parrot**:

```bash
whoami
ip -br addr
hostname -I
```

- `whoami` muestra el nombre de usuario. **No presupongas** que sea `damian`.
- Si la VM usa NAT, es frecuente una IP como `10.0.2.15`. **Windows no suele poder entrar directamente** a esa IP.

## 0.2. Instalar y habilitar servidor SSH (en Parrot)

```bash
sudo apt update
sudo apt install -y openssh-server
sudo systemctl enable --now ssh
sudo systemctl status ssh
```

`active (running)` significa que el servicio está levantado. Presioná `q` para salir de `status`. Para comprobar el puerto:

```bash
sudo ss -tlnp | grep ':22'
```

## 0.3. Recomendada: redirección de puerto SSH en VirtualBox NAT

Con Parrot apagado (o desde la configuración de red de la VM, según permita tu VirtualBox):

1. **VirtualBox → Parrot → Configuración → Red → Adaptador 1**.
2. Dejá **Conectado a: NAT**.
3. Entrá en **Avanzadas → Redirección de puertos** (en algunas versiones está directamente en Red).
4. Agregá una regla:

| Nombre | Protocolo | IP anfitrión | Puerto anfitrión | IP invitado | Puerto invitado |
|---|---|---|---:|---|---:|
| SSH-Parrot | TCP | `127.0.0.1` | `2222` | *(vacío)* | `22` |

5. Iniciá Parrot. Desde **PowerShell o CMD en Windows**:

```powershell
ssh -p 2222 TU_USUARIO@127.0.0.1
```

Ejemplo **solo si** `whoami` devolvió `damian`:

```powershell
ssh -p 2222 damian@127.0.0.1
```

En la primera conexión, verificá la huella del servidor y aceptala si corresponde a tu VM. La contraseña que solicita es la del **usuario de Parrot**, no la de Windows. La contraseña no se ve mientras la escribís: es normal.

**Por qué no usar `ssh damian@10.0.2.15` desde Windows:** en NAT, esa IP normalmente queda detrás de la traducción de direcciones de VirtualBox. El puerto `2222` de Windows se redirige al `22` de Parrot.

**Opción alternativa:** Adaptador puente y `ssh usuario@IP_DE_PARROT`, solo cuando la red permita comunicación entre equipos. Para una demostración local preferimos NAT + redirección.

## 0.4. Si falla SSH

| Error | Comprobación / solución |
|---|---|
| `Connection timed out` | Verificá modo NAT, regla `2222 → 22` y que VM esté encendida. |
| `Connection refused` | Comprobá `sudo systemctl status ssh` en Parrot; verificá regla y puerto. |
| `Permission denied` | Revisá `whoami` y contraseña del usuario Parrot. |
| `WARNING: REMOTE HOST IDENTIFICATION HAS CHANGED` | No ignores la advertencia: corroborá que sea tu VM y su clave, especialmente tras reinstalaciones. |
| `ssh` no existe en Windows | Abrí PowerShell y comprobá `ssh -V`; instalá la característica OpenSSH Client si hace falta. |

## 0.5. Limitación de una sesión SSH

SSH es una terminal **remota**. Si ejecutás OpenCode dentro de SSH, lo usás allí mismo. Para **abrir Firefox** sobre la pantalla de Parrot, trabajá desde la sesión gráfica de Parrot; no presupongas que `firefox` abrirá una ventana en Windows.

---

# PARTE 1 — Instalar OpenCode en Parrot

## 1.1. Prerrequisitos

Desde una terminal de Parrot (local o SSH):

```bash
sudo apt update
sudo apt install -y curl ca-certificates python3 python3-venv python3-pip
```

## 1.2. Instalar

El instalador actual oficial de OpenCode **v2** es:

```bash
curl -fsSL https://opencode.ai/v2/install | bash
```

**Nota docente:** este comando descarga y ejecuta un instalador remoto. En producción conviene revisar el script y su procedencia antes de ejecutarlo. No usar `sudo` para instalar OpenCode en la cuenta personal salvo indicación oficial específica.

Cerrá y reabrí la terminal. Probá:

```bash
opencode --version
```

Si devuelve `command not found`, comprobá si está instalado en `~/.opencode/bin/opencode` y si esa carpeta aparece en `$PATH`. Según el instalador puede requerir recargar el perfil de shell. Alternativa: seguí la salida del instalador o consultá `https://opencode.ai/docs`.

## 1.3. Seleccionar modelo

Desde la carpeta del laboratorio:

```bash
opencode
```

Dentro de la interfaz, escribí:

```text
/models
```

Seleccioná un modelo indicado como **Free**, si hay uno disponible. Los modelos y límites cambian; si no aparece ninguno, **no ingreses una tarjeta ni actives un plan pago solo para la clase**. En ese caso mostrá los prompts, analizá los archivos manualmente o utilizá una opción gratuita que ya tengas autorizada.

**Privacidad:** no compartas tokens, claves SSH, `.env`, contraseñas de alumnos o archivos reales. No aceptes que el agente instale paquetes, cambie configuración del sistema o publique código sin revisar la acción.

---

# LABORATORIO 1 — IA como auditora de un formulario HTML

**Tiempo:** 15–20 minutos · **Dificultad:** inicial · **No requiere Flask**.

## 1.1. Crear una carpeta y el HTML manualmente

```bash
mkdir -p ~/cfp20-ia/html-auditoria
cd ~/cfp20-ia/html-auditoria
nano index.html
```

Escribí **a mano** este ejemplo breve:

```html
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <title>Ingreso CFP20 (demostración)</title>
</head>
<body>
  <h1>Ingreso ficticio</h1>
  <form>
    <label>Usuario <input type="text" name="usuario"></label>
    <label>Contraseña <input type="text" name="clave"></label>
    <button>Ingresar</button>
  </form>
  <p>No utilizar credenciales reales.</p>
</body>
</html>
```

Guardar en nano: `Ctrl+O`, Enter, `Ctrl+X`.

Si estás en la sesión gráfica de Parrot, podés abrirlo con doble clic o:

```bash
firefox index.html
```

## 1.2. Pregunta para la clase

> ¿Es seguro este formulario? ¿Qué diferencia hay entre **ocultar los caracteres** y **proteger realmente una contraseña**?

## 1.3. Auditoría asistida por IA

```bash
opencode
```

Pegá en el chat de OpenCode el siguiente **prompt**:

> Analizá el archivo `index.html` de este proyecto como docente de ciberseguridad. Es una demostración local con cuentas ficticias. Identificá hasta cinco problemas o limitaciones reales, con gravedad razonable, y distinguí errores de accesibilidad de vulnerabilidades de seguridad. Explicá todo para principiantes. **No modifiques archivos, no ejecutes comandos ni instales paquetes**. Mostrá problema, evidencia y recomendación.

**Verificación docente:** el `type="text"` en la clave la muestra en pantalla. Cambiarlo a `type="password"` **no cifra** la comunicación ni aporta verificación de credenciales. El HTML estático **no tiene autenticación ni backend**, por lo que no se puede presentar como login real. No afirmar que hay SQL Injection o XSS sin evidencia.

## 1.4. Pedir una corrección acotada

> Mejorá únicamente `index.html`: cambiá el campo de clave a `type="password"`, añadí `required`, `autocomplete` y etiquetas accesibles, y colocá un aviso visible de que **no es un login real**. No agregues JavaScript, backend, APIs ni dependencias. **Mostrá primero el cambio propuesto y pedí aprobación antes de editar**. Al final explicá qué riesgos NO resuelve este formulario.

Aprobá solo los cambios que entiendas. Volvé a abrir el HTML y mostrá la diferencia.

## 1.5. Preguntas de cierre

- ¿Qué mejoró? Experiencia del usuario y entrada de datos.
- ¿Qué falta? Backend, HTTPS en un despliegue real, sesiones, protección contra abusos y almacenamiento adecuado de contraseñas.
- ¿La IA siempre acierta? No. Hay que contrastar cada afirmación con el archivo real.

---

# LABORATORIO 2 — Flask desde cero CON IA: registro de incidentes ficticios

**Tiempo:** 25–35 minutos · **Dificultad:** principiantes · **Sin base de datos, sin usuarios, sin Internet público**.

## Objetivo

Crear con OpenCode una aplicación web local para **registrar reportes ficticios de seguridad**. Un formulario recibe un título, una categoría y una descripción, y una lista muestra los reportes. Vamos a pedirle a la IA **validación en el servidor, escape automático de contenido HTML y cabeceras defensivas básicas**, y comprobarlo manualmente.

**Por qué este tema y no otro login:** permite enseñar seguridad de formularios y tratamiento de entradas sin implementar cuentas, contraseñas, SQLite o ataques reales.

## 2.1. Crear el proyecto desde cero

En una terminal nueva (o saliendo de OpenCode con la opción de salir de su interfaz):

```bash
mkdir -p ~/cfp20-ia/reportes-flask
cd ~/cfp20-ia/reportes-flask
python3 -m venv .venv
source .venv/bin/activate
python -m pip install Flask
```

`(.venv)` al inicio del prompt indica que el entorno virtual está activo. Este entorno aísla las dependencias. No uses `sudo pip install`.

## 2.2. Pedir a OpenCode que construya la aplicación

Desde **esa misma carpeta**:

```bash
opencode
```

Prompt principal:

> Sos docente de Python y ciberseguridad para principiantes del CFP20. Creá desde cero una aplicación web Flask **solo local** llamada "Centro de Reportes CFP20". Necesito `app.py`, `templates/index.html`, `static/estilos.css` y `requirements.txt`.
>
> Funcionalidad: formulario para cargar un **reporte totalmente ficticio** con título, categoría (phishing, malware, contraseña o red) y descripción; debajo, mostrar los últimos 10 reportes en memoria, con fecha. Precargar dos reportes de ejemplo. No usar base de datos, login, servicios externos ni frameworks de CSS.
>
> Seguridad y enseñanza: usar `request.form`, validar en el **backend** campos vacíos y largos (título máximo 60, descripción máximo 250), rechazar categorías desconocidas, usar plantillas Jinja con escape automático **sin `|safe`**, y añadir cabeceras `X-Content-Type-Options: nosniff` y `Referrer-Policy: no-referrer`. Para la demo local, definir `debug=False` y ejecutar en `127.0.0.1:5001`. No guardar datos sensibles ni implementar una API pública.
>
> Escribí comentarios breves en español que expliquen las partes importantes. **Mostrá el plan y solicitá aprobación antes de crear o modificar archivos**. No ejecutes comandos destructivos.

Si la IA pide permiso para escribir archivos, revisá los nombres y aprobá únicamente los necesarios.

## 2.3. Iniciar y abrir la aplicación

En otra terminal, dentro de `~/cfp20-ia/reportes-flask`:

```bash
source .venv/bin/activate
python app.py
```

En la **pantalla gráfica de Parrot**, abrí Firefox:

```text
http://127.0.0.1:5001
```

Si estás conectado desde Windows por **SSH y NAT**, la web no aparecerá en Windows automáticamente. Para abrirla desde Firefox de Windows, creá un túnel local desde **otra ventana de PowerShell**:

```powershell
ssh -N -L 5001:127.0.0.1:5001 -p 2222 TU_USUARIO@127.0.0.1
```

Dejá esa ventana abierta y entrá desde **Windows** a `http://127.0.0.1:5001`. Si Windows ya usa ese puerto, reemplazá el **primer** `5001` por `5501`, y abrí `http://127.0.0.1:5501`.

## 2.4. Probar un reporte normal (5 min)

Cargá manualmente:

- **Título:** Equipo sin actualizar
- **Categoría:** Malware
- **Descripción:** La computadora ficticia del aula no recibió actualizaciones.

**Resultado esperado:** aparece el reporte en la lista con su categoría y fecha.

## 2.5. Validación en servidor (5 min)

Intentá enviar:

1. Título vacío → el servidor debe rechazarlo con mensaje claro.
2. Una descripción de más de 250 caracteres → el servidor debe rechazarla, incluso si se evita la validación del navegador.
3. Una categoría fuera del listado → el servidor debe rechazarla, sin confiar solo en la lista desplegable.

Para el caso 2, el profesor puede explicar que `maxlength` ayuda en el navegador, **pero la seguridad exige validación del lado del servidor**.

## 2.6. Contenido HTML tratado como texto (5 min)

En el título de un reporte ficticio escribí **manualmente**:

```text
<b>Alerta de prueba</b>
```

**Resultado esperado:** debería verse literalmente `<b>Alerta de prueba</b>`, no como texto en negrita. Es una comprobación simple del escape de HTML por Jinja. **No demuestra que la aplicación esté libre de cualquier XSS**, pero permite conversar sobre salida segura.

**Pregunta:** ¿Por qué no debemos usar `|safe` con texto escrito por usuarios?

## 2.7. Inspeccionar una respuesta HTTP (5 min)

En otra terminal de Parrot:

```bash
curl -I http://127.0.0.1:5001/
```

Buscá las cabeceras:

```text
X-Content-Type-Options: nosniff
Referrer-Policy: no-referrer
```

`curl -I` envía una solicitud HEAD: el endpoint debe permitirla. No son una garantía de seguridad integral, sino capas de protección.

## 2.8. Pedirle a la IA una revisión final (5 min)

En OpenCode:

> Revisá los archivos de este proyecto Flask. Comprobá si el servidor valida título, categoría y descripción, si el contenido de usuarios se escapa al mostrarse y si existen las dos cabeceras pedidas. Indicá dónde se implementó cada control y proponé **una prueba manual por control**. No cambies archivos ni ejecutes comandos. Aclarame también qué limitaciones quedan: datos en memoria, sin autenticación y sin despliegue de producción.

**Chequeo clave:** no creas automáticamente el informe de la IA. Si no encontrás el control en `app.py` o la plantilla, hay que corregirlo.

## 2.9. Cierre (3 minutos)

- ¿Qué hace OpenCode? Ayuda a crear y revisar código, pero no garantiza seguridad.
- ¿Qué hicimos nosotros? Definimos requisitos y verificamos resultados.
- ¿Qué aprendimos? Validar entradas, mostrar contenido como texto y controlar la exposición del servicio.

---

# Cronograma sugerido (si incluís ambos en una clase de dos horas)

| Minutos | Actividad |
|---|---|
| 0–10 | Recordatorio sobre IA y riesgos de seguridad |
| 10–25 | Conectar por SSH, verificar entorno e instalación de OpenCode (idealmente preinstalado) |
| 25–45 | Laboratorio 1: HTML y auditoría con IA |
| 45–80 | Laboratorio 2: crear Flask con IA |
| 80–100 | Probar validación, escape HTML y cabeceras |
| 100–115 | Discusión: límites de IA y controles defensivos |
| 115–120 | Cierre y preguntas |

> **Consejo de aula:** prepará SSH, OpenCode y Flask antes del encuentro para que la instalación no consuma la práctica. El archivo `solucion_flask/` de este kit es un **respaldo funcional** por si falla un modelo gratuito; la actividad principal consiste en pedir a la IA que lo cree desde cero, no en copiar y pegar una solución.

---

# Solución docente de respaldo

Dentro del kit existe `solucion_flask/`, con el mismo ejemplo construido previamente para poder ejecutar la clase incluso si OpenCode no responde. Para probarlo:

```bash
cd solucion_flask
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Visitá `http://127.0.0.1:5001` desde la sesión gráfica de Parrot o con el túnel SSH indicado.

---

# Fuentes y documentación

- Instalación actual y modelos de OpenCode: https://opencode.ai/docs y https://opencode.ai/
- Documentación Flask: https://flask.palletsprojects.com/
- Referencia SSH OpenSSH: https://www.openssh.com/manual.html
- Seguridad de aplicaciones web: https://owasp.org/www-project-top-ten/

**Uso exclusivo en laboratorios propios y autorizados. No ingresar secretos ni información personal real.**
