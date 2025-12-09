# 🎙️ Jarvis - Alexa LLM Skill

![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat&logo=python&logoColor=white)
![Alexa](https://img.shields.io/badge/Alexa-Skill-00CAFF?style=flat&logo=amazon-alexa&logoColor=white)
![Gemini](https://img.shields.io/badge/AI-Google_Gemini-8E75B2?style=flat&logo=google&logoColor=white)
![AWS Lambda](https://img.shields.io/badge/Backend-AWS_Lambda-FF9900?style=flat&logo=amazonaws&logoColor=white)

> **Asistente Virtual Avanzado integrado con LLMs para conversaciones naturales y control domótico.**

---

## 💡 Visión General

**Jarvis** es una Skill de Alexa personalizada que trasciende los comandos básicos, integrando la potencia de **Google Gemini 1.5 Pro** para ofrecer respuestas conversacionales, creativas y contextuales. Diseñada para actuar como un mayordomo inteligente, combina capacidades de procesamiento de lenguaje natural con una personalidad refinada.

### 🚀 Características Principales

- 🧠 **Inteligencia Generativa**: Respuestas impulsadas por Google Gemini, permitiendo conversaciones fluidas sobre cualquier tema.
- 🎭 **Personalidad "Butler"**: Prompt de sistema diseñado para responder con elegancia, ingenio y brevedad (máx. 2 oraciones).
- 🗣️ **Voz Personalizada**: Utiliza síntesis SSML para una voz masculina distinguida ("Enrique").
- 🏠 **Contexto Continuo**: Gestión de sesiones para mantener el hilo de la conversación sin invocar el comando de activación repetidamente.
- ⚡ **Despliegue Serverless**: Backend alojado en AWS Lambda (Alexa-Hosted).

---

## 🛠️ Arquitectura

La skill sigue una arquitectura serverless estándar de Alexa:

1.  **VUI (Voice User Interface)**: Definida en `interaction_model.json`. Captura la intención del usuario (`CatchAllIntent`).
2.  **Backend Logic**: `lambda_function.py` procesa la entrada, llama a la API de Gemini y formatea la respuesta SSML.
3.  **LLM**: Google Gemini API procesa el texto y genera la respuesta según el "System Prompt" definido en `jarvis_prompt.md`.

---

## 📂 Estructura del Proyecto

```text
Alexa_Jarvis/
├── 📄 lambda_function.py      # Lógica principal (AWS Lambda Handler)
├── 📄 interaction_model.json  # Modelo de voz (Intents, Slots)
├── 📄 jarvis_prompt.md        # Prompt del Sistema (Personalidad)
├── 📄 requirements.txt        # Dependencias (google-generativeai)
└── 📄 GUIA_INSTALACION.md     # Pasos detallados para desplegar
```

---

## 🚀 Despliegue Rápido

Consulta la [Guía de Instalación](GUIA_INSTALACION.md) para instrucciones paso a paso.

### Resumen:
1.  Crear Skill en **Alexa Developer Console**.
2.  Copiar el modelo de `interaction_model.json`.
3.  Subir el código de `lambda_function.py` y dependencias.
4.  Configurar variable de entorno `GOOGLE_API_KEY`.
5.  Desplegar y probar.

---

## 🤖 Ejemplo de Interacción

> **Usuario:** "Alexa, abre Jarvis"
> **Jarvis:** "A su servicio, señor. ¿En qué puedo asistirle hoy?"
> **Usuario:** "¿Cuál es la distancia a la Luna?"
> **Jarvis:** "La Luna orbita a una distancia media de 384,400 kilómetros de la Tierra. Un viaje fascinante, si me permite decirlo."

---

## 👨‍💻 Autor

**Reinvik (Ariel Mella)**
*Desarrollado como parte de la suite de automatización personal.*
