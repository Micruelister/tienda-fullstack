# Proyecto E-commerce Full-Stack

Este es un proyecto de aplicación web de comercio electrónico completo, construido con un backend en Python (Flask) y un frontend dinámico en JavaScript (React). La aplicación está completamente contenedorizada con Docker para facilitar su despliegue y ejecución.

## Tecnologías Utilizadas

*   **Frontend:** React, Vite, JavaScript, HTML5, CSS3
*   **Backend:** Python, Flask, SQLAlchemy
*   **Base de Datos:** SQLite (para desarrollo), compatible con PostgreSQL
*   **Despliegue:** Docker, Docker Compose, Nginx

---

## Guía de Instalación y Puesta en Marcha (Desde Cero)

Esta guía te llevará paso a paso para configurar el entorno y ejecutar el proyecto en una computadora nueva.

### **Paso 1: Instalar Prerrequisitos**

Necesitarás dos programas principales para ejecutar este proyecto: **Git** y **Docker**.

#### A. Instalar Git

Git es un sistema de control de versiones que usarás para descargar (clonar) el código del proyecto a tu computadora.

1.  **Descarga Git:** Ve a la página oficial de descargas de Git: [https://git-scm.com/downloads](https://git-scm.com/downloads)
2.  **Instala Git:** Ejecuta el instalador que descargaste. Durante la instalación, puedes dejar todas las opciones por defecto. La opción más importante es asegurarte de que Git se añada al PATH de tu sistema para que puedas usarlo desde cualquier terminal. En Windows, esto te dará una herramienta llamada **Git Bash**, que es una excelente terminal para usar.

#### B. Instalar Docker Desktop

Docker es una plataforma que nos permite empaquetar la aplicación y todas sus dependencias en "contenedores". Esto asegura que la aplicación funcione de la misma manera en cualquier computadora.

1.  **Descarga Docker Desktop:** Ve a la página oficial de Docker: [https://www.docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop)
2.  **Selecciona tu Sistema Operativo** (Windows, Mac o Linux) y descarga el instalador.
3.  **Instala Docker Desktop:** Ejecuta el instalador. Este proceso puede requerir que reinicies tu computadora. Docker Desktop incluye **Docker Compose**, que es la herramienta que usaremos para orquestar nuestros contenedores.
4.  **Inicia Docker Desktop:** Una vez instalado, asegúrate de que Docker Desktop esté en ejecución. Deberías ver un icono de Docker en tu barra de tareas.

### **Paso 2: Clonar y Configurar el Proyecto**

Ahora que tienes las herramientas, vamos a obtener y configurar el código del proyecto.

1.  **Abre una Terminal:**
    *   En **Windows**, busca y abre **Git Bash**.
    *   En **Mac** o **Linux**, abre la aplicación **Terminal**.

2.  **Clona el Repositorio:**
    Ejecuta el siguiente comando para descargar el código. Reemplaza `<URL_DEL_REPOSITORIO>` con la URL que te proporcionaron (por ejemplo, de GitHub).
    ```bash
    git clone <URL_DEL_REPOSITORIO>
    ```

3.  **Navega al Directorio del Proyecto:**
    Una vez clonado, entra en la carpeta del proyecto.
    ```bash
    cd <NOMBRE_DE_LA_CARPETA_DEL_PROYECTO>
    ```

4.  **Crea tu Archivo de Configuración (`.env`):**
    El proyecto necesita un archivo `.env` para almacenar claves secretas y configuraciones. Puedes crearlo copiando el archivo de ejemplo.
    ```bash
    cp .env.example .env
    ```
    Si estás en Windows y el comando `cp` no funciona en la terminal `cmd`, puedes hacerlo manualmente en el explorador de archivos (copia y pega `.env.example` y renómbralo a `.env`) o usar `copy .env.example .env`.

5.  **Edita el Archivo `.env`:**
    Abre el archivo `.env` con un editor de texto (como VS Code, Sublime Text o el Bloc de notas) y rellena las variables.
    *   `SECRET_KEY`: Debe ser una cadena de texto larga y aleatoria. Puedes generar una aquí: [https://randomkeygen.com/](https://randomkeygen.com/)
    *   `DATABASE_URL`: Para empezar, puedes dejar la configuración de SQLite que viene por defecto (`DATABASE_URL=sqlite:///app.db`).
    *   `VITE_API_BASE_URL`: La URL donde el frontend buscará al backend. Para esta configuración, déjala como `http://localhost:5000/api`.
    *   `VITE_GOOGLE_MAPS_API_KEY`: Tu clave de API de Google Maps. Necesitas obtenerla desde la [Google Cloud Platform](https://cloud.google.com/maps-platform/).
    *   `STRIPE_API_KEY`: Tu clave secreta de API de [Stripe](https://stripe.com/docs/keys).
    *   `CORS_ORIGINS`: La URL de tu frontend. Para esta configuración, déjala como `http://localhost:80`.

### **Paso 3: Ejecutar la Aplicación**

Con todo configurado, ¡es hora de iniciar la aplicación!

1.  **Asegúrate de que Docker Desktop esté en ejecución.**
2.  En tu terminal, desde la raíz del proyecto, ejecuta el siguiente comando:
    ```bash
    docker-compose up --build
    ```
    *   `--build`: Este flag le dice a Docker que construya las "imágenes" de la aplicación la primera vez que lo ejecutas.
    *   La primera vez, este proceso tardará varios minutos mientras Docker descarga todo lo necesario y construye la aplicación. Las siguientes veces será mucho más rápido.

3.  **Accede a tu Aplicación:**
    Una vez que la terminal muestre los logs de los servidores, ¡tu aplicación está en vivo!
    *   **Frontend (la tienda que ven los usuarios):** Abre tu navegador y ve a [http://localhost:80](http://localhost:80)
    *   **Backend (la API):** Está disponible en `http://localhost:5000`, aunque normalmente no interactuarás con ella directamente.

### **Paso 4: Crear tu Usuario Administrador**

Para gestionar productos e inventario, necesitas una cuenta de administrador.

1.  Abre una **nueva terminal** (deja la que está ejecutando `docker-compose` abierta).
2.  Desde la raíz del proyecto, ejecuta el siguiente comando. Reemplaza `<tu-contraseña-segura>` por la contraseña que quieras.
    ```bash
    docker-compose exec backend flask create-admin <tu-contraseña-segura>
    ```
3.  Ahora puedes ir a la página de login de tu tienda, iniciar sesión con el usuario `admin` y la contraseña que acabas de establecer, y tendrás acceso a las funciones de administración.

### **Paso 5: Detener la Aplicación**

Para detener los servidores:

1.  Ve a la terminal donde se está ejecutando `docker-compose up`.
2.  Presiona `Ctrl + C`.
3.  Para detener y eliminar los contenedores y limpiar todo, puedes ejecutar:
    ```bash
    docker-compose down
    ```

¡Y eso es todo! Con estos pasos, tienes el proyecto completamente funcional en tu nueva computadora.
