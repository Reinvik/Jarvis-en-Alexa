# Guía de Instalación para Jarvis Alexa Skill

Esta guía te ayudará a desplegar tu propia versión de Jarvis en Alexa usando la Developer Console de Amazon.

## Requisitos Previos
1.  **Cuenta de Amazon Developer**: [developer.amazon.com](https://developer.amazon.com/) (Gratis).
2.  **API Key de Google Gemini**: [aistudio.google.com](https://aistudio.google.com/app/apikey).
    *   Crea una API Key y **guárdala bien**.

## Paso 1: Crear la Skill en Alexa Console
1.  Ve a [Alexa Developer Console](https://developer.amazon.com/alexa/console/ask).
2.  Haz clic en **"Create Skill"**.
3.  **Skill Name**: `Jarvis` (o como quieras llamarlo).
4.  **Primary Locale**: `Spanish (ES)` (o `Spanish (MX)`/`Spanish (US)` según tu región).
5.  **Choose a model**: "Custom".
6.  **Choose a method to host**: "Alexa-hosted (Python)".
7.  Haz clic en **"Create Skill"** (arriba a la derecha).
8.  Espera un momento (aprox 1 min) mientras se provisiona.

## Paso 2: Configurar el Modelo de Interacción
1.  En el menú de la izquierda, ve a **Interaction Model** -> **JSON Editor**.
2.  Borra todo el contenido que aparece ahí.
3.  Copia y pega el contenido del archivo `interaction_model.json` que generamos en la carpeta `Alexa_Jarvis`.
4.  Haz clic en **"Save Model"**.
5.  Haz clic en **"Build Model"**. (Esto puede tardar un poco).

## Paso 3: Subir el Código
3.  **SUBIR ARCHIVO ZIP (RECOMENDADO):**
    *   Como tenemos muchas librerías (tinytuya, requests, etc...), NO funcionará solo con copiar y pegar el código.
    *   Haz clic en **"Import Code"** o busca la opción **"Upload from" -> ".zip file"**.
    *   Sube el archivo `upload_to_aws.zip` que generamos.
    *   Esto cargará automáticamente `lambda_function.py`, `devices.json`, `jarvis_prompt.md` y todas las carpetas de librerías.

4.  **CONFIGURAR VARIABLES DE ENTORNO (MUY IMPORTANTE):**
    *   Para seguridad, NO hemos puesto tus claves en el código. Debes ponerlas en AWS.
    *   En la consola de Code, busca abajo o arriba un botón de configuración de la Lambda/Skill. Si estás en "Alexa Hosted", a veces es difícil encontrar donde poner Env Vars.
    *   **Alternativa Mejor:** Ve a la consola de [AWS Lambda](https://console.aws.amazon.com/lambda/).
        *   Busca tu función (tendrá un nombre largo y raro).
        *   Ve a la pestaña **Configuration** -> **Environment variables**.
        *   Haz clic en **Edit** y agrega las siguientes:
            *   `GOOGLE_API_KEY`: Tu clave "AIzaSy..."
            *   `TUYA_API_KEY`: Tu clave "3eqj..."
            *   `TUYA_API_SECRET`: Tu secreto "f665..."
            *   `TUYA_REGION`: "us" (o tu región)
            *   `GEMINI_MODEL`: "gemini-2.0-flash-exp" (opcional)
    *   Guarda los cambios.

## Paso 4: Probar
1.  Ve a la pestaña **"Test"** en la parte superior.
2.  Donde dice "Test is disabled for this skill", cambia a **"Development"**.
3.  En el chat de la izquierda, escribe o mantén presionado el micrófono y di:
    *   *"Abre Jarvis"*
4.  Debería responderte con la personalidad que definimos.

## ¿No funciona en tu Alexa físico (Echo/Dot)?
Si en el simulador funciona pero en tu aparato no, revisa esto:

1.  **Misma Cuenta**: Tu Alexa debe estar registrada con **el mismo correo electrónico** que usaste para la cuenta de Developer.
2.  **Idioma (Locale)**:
    *   Si tu Alexa está configurada en **Español (México)** pero creaste la skill en **Español (España)**, NO la encontrará.
    *   **Solución**: En la consola, ve a "Build", haz clic en el idioma (arriba a la izquierda) -> "Language Settings" -> "+ Add New Language".
    *   Agrega `Spanish (Mexico)` y `Spanish (US)` si estás en Latinoamérica.
    *   Copia el `interaction_model.json` también para esos idiomas y dale a **Build Model** nuevamente en cada uno.
3.  **Nombre de Invocación**: Asegúrate de decir clarito "Alexa, abre Jarvis".
