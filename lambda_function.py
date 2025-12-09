import logging
import os
import json
import requests
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_model import Response
from ask_sdk_model.ui import SimpleCard

# Logger setup
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# --- CONFIGURATION ---
# Las claves se obtienen de Variables de Entorno en AWS Lambda
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash-exp") 

def get_system_prompt():
    """Reads the system prompt from the jarvis_prompt.md file."""
    try:
        with open("jarvis_prompt.md", "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error reading prompt file: {e}")
        return "Eres Jarvis, asistente virtual." # Fallback

def call_gemini_api(prompt, question):
    """Calls Gemini API via requests (REST) to avoid library issues."""
    if not GOOGLE_API_KEY:
        return "Error de configuración: Falta la GOOGLE_API_KEY en las variables de entorno."

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GOOGLE_API_KEY}"
    
    headers = {'Content-Type': 'application/json'}
    
    # Structure the payload manually with SAFETY SETTINGS DISABLED
    data = {
        "contents": [
            {
                "parts": [
                    {"text": f"{prompt}\n\nUser Question: {question}\n\nINSTRUCCION CRÍTICA: Sé breve (máximo 2 oraciones). Sé servicial y usa humor ligero."}
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 1024
        },
        "safetySettings": [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
        ]
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status() 
        
        result_json = response.json()
        
        # Robust extraction
        candidates = result_json.get('candidates', [])
        if not candidates:
             if 'error' in result_json:
                 return f"Error API: {result_json['error'].get('message')}"
             return "Error: Respuesta vacía del servidor."
             
        first_candidate = candidates[0]
        content = first_candidate.get('content', {})
        parts = content.get('parts', [])
        
        if parts and 'text' in parts[0]:
            return parts[0]['text']
            
        # If we are here, we didn't find standard text. Check why.
        finish_reason = first_candidate.get('finishReason', 'UNKNOWN')
        
        if finish_reason == 'MAX_TOKENS':
            return "Intente preguntar algo más breve, señor."
            
        if finish_reason == 'SAFETY':
             return "Mis protocolos de seguridad se activaron, y bloquearon esa respuesta."
             
        return f"Respuesta ilegible (Reason: {finish_reason}). Estructura: {str(first_candidate)[:100]}"
        
    except Exception as e:
        logger.error(f"Gemini API Error: {e}")
        return f"Error conectando: {str(e)}"

class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        return is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        speech_text = "A sus órdenes, jefe. Sistemas Nexus en línea. "
        ssml_text = f"<speak><voice name='Enrique'>{speech_text}</voice></speak>"
        return (
            handler_input.response_builder
            .speak(ssml_text)
            .ask(ssml_text)
            .set_card(SimpleCard("Jarvis", speech_text))
            .response
        )


# --- SHARED TUYA FUNCTION ---
def execute_tuya_command(action_word, device_word):
    """Executes Tuya command based on action and device name."""
    try:
        import tinytuya
        
        # Obtener credenciales de variables de entorno
        TUYA_REGION = os.environ.get("TUYA_REGION", "us")
        TUYA_API_KEY = os.environ.get("TUYA_API_KEY")
        TUYA_API_SECRET = os.environ.get("TUYA_API_SECRET")

        if not TUYA_API_KEY or not TUYA_API_SECRET:
            return "Error: Faltan las credenciales de Tuya en las variables de entorno."

        # Cargar mapa de dispositivos desde archivo JSON
        try:
            with open("devices.json", "r", encoding="utf-8") as f:
                DEVICE_MAP = json.load(f)
        except FileNotFoundError:
            return "Error: No se encontró el archivo devices.json"
        except json.JSONDecodeError:
            return "Error: El archivo devices.json tiene un formato inválido"

        # Normalize input
        device_key = device_word.lower()
        if "luz " in device_key and device_key not in DEVICE_MAP:
             # Try to find "comedor" in "luz comedor"
             stripped = device_key.replace("luz ", "").strip()
             if stripped in DEVICE_MAP:
                 device_key = stripped

        target_id = DEVICE_MAP.get(device_key)
        
        # Fuzzy search if exact match fails
        if not target_id:
            for key in DEVICE_MAP:
                if key in device_key:
                    target_id = DEVICE_MAP[key]
                    device_word = key # Update name for speech
                    break

        if not target_id:
            return f"No encontré el dispositivo '{device_word}'. Revise su mapa."

        c = tinytuya.Cloud(apiRegion=TUYA_REGION, apiKey=TUYA_API_KEY, apiSecret=TUYA_API_SECRET)
        
        # Action logic
        is_on = True 
        if any(x in action_word.lower() for x in ["apaga", "desactiva", "cierra", "off"]):
            is_on = False
            
        commands = {
            "commands": [
                {"code": "switch_1", "value": is_on}
            ]
        }
        
        result = c.sendcommand(target_id, commands)
        
        if result and result.get('success'):
            state_str = "encendido" if is_on else "apagado"
            return f"He {state_str} {device_word}."
        else:
             return f"Error Tuya: {result.get('msg', 'Unknown')}"

    except Exception as e:
        return f"Error de sistema: {str(e)}"

class AskJarvisIntentHandler(AbstractRequestHandler):
    """Handler for AskJarvisIntent."""
    def can_handle(self, handler_input):
        return is_intent_name("AskJarvisIntent")(handler_input)

    def handle(self, handler_input):
        slots = handler_input.request_envelope.request.intent.slots
        question = slots["question"].value if slots["question"].value else None
        
        if not question:
            speech_text = "Señor, necesito que me diga algo. No leo mentes... todavía."
            return handler_input.response_builder.speak(speech_text).ask("¿Qué necesita?").response

        # --- INTERCEPTOR DE COMANDOS DE CASA ---
        # Si Alexa manda el comando a Gemini por error, lo interceptamos aqui.
        q_lower = question.lower()
        if any(act in q_lower for act in ["enciende", "prender", "activa", "apaga", "desactiva"]):
             # Es probable un comando
             # Extraer accion
             action = "encender"
             if "apaga" in q_lower or "desactiva" in q_lower:
                 action = "apagar"
                 
             # Extraer dispositivo (simple heuristic: remove action word)
             # Esto es basico pero efectivo para "enciende luz comedor"
             device_guess = q_lower.replace("enciende", "").replace("prender", "").replace("activa", "").replace("apaga", "").replace("desactiva", "").replace("por favor", "").replace("jarvis", "").strip()
             
             # Ejecutar logica Tuya directa
             jarvis_response = execute_tuya_command(action, device_guess)
        else:
            # Call Gemini via REST normally
            system_instruction = get_system_prompt()
            jarvis_response = call_gemini_api(system_instruction, question)
            
        # Wrap response in SSML to use male voice (Enrique)
        ssml_response = f"<speak><voice name='Enrique'>{jarvis_response}</voice></speak>"
        ssml_reprompt = f"<speak><voice name='Enrique'>¿Alguna otra instrucción, señor?</voice></speak>"

        return (
            handler_input.response_builder
            .speak(ssml_response)
            .ask(ssml_reprompt) # Wait for user input with a short prompt if they don't speak
            .set_card(SimpleCard("Jarvis", jarvis_response))
            .response
        )



class ControlDeviceIntentHandler(AbstractRequestHandler):
    """Handler for ControlDeviceIntent."""
    def can_handle(self, handler_input):
        return is_intent_name("ControlDeviceIntent")(handler_input)

    def handle(self, handler_input):
        slots = handler_input.request_envelope.request.intent.slots
        
        # Safe extraction of slot values
        action = slots["action"].value if slots.get("action") and slots["action"].value else "encender"
        device = slots["device"].value if slots.get("device") and slots["device"].value else "luz"
        
        # Call shared function
        speech_text = execute_tuya_command(action, device)
        
        ssml_text = f"<speak><voice name='Enrique'>{speech_text}</voice></speak>"
        
        return (
            handler_input.response_builder
            .speak(ssml_text)
            .set_card(SimpleCard("Jarvis Home", f"Action: {action} {device}\nResult: {speech_text}"))
            .response
        )

class HelpIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        speech_text = "Pregúntame cualquier cosa. Desde el estado de Nexus hasta datos inútiles de Nintendo."
        ssml_text = f"<speak><voice name='Enrique'>{speech_text}</voice></speak>"
        return handler_input.response_builder.speak(ssml_text).ask(ssml_text).response

class YesIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.YesIntent")(handler_input)

    def handle(self, handler_input):
        speech_text = "Adelante, jefe. ¿Cuál es su siguiente orden?"
        ssml_text = f"<speak><voice name='Enrique'>{speech_text}</voice></speak>"
        return handler_input.response_builder.speak(ssml_text).ask(ssml_text).response

class NoIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.NoIntent")(handler_input)

    def handle(self, handler_input):
        speech_text = "Entendido. Desconectando sistemas."
        ssml_text = f"<speak><voice name='Enrique'>{speech_text}</voice></speak>"
        return handler_input.response_builder.speak(ssml_text).set_should_end_session(True).response

class CancelOrStopIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return (is_intent_name("AMAZON.CancelIntent")(handler_input) or
                is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        speech_text = "Desconectando. Adiós."
        ssml_text = f"<speak><voice name='Enrique'>{speech_text}</voice></speak>"
        return handler_input.response_builder.speak(ssml_text).set_should_end_session(True).response

class SessionEndedRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        return handler_input.response_builder.response

class CatchAllExceptionHandler(AbstractExceptionHandler):
    def can_handle(self, handler_input, exception):
        return True

    def handle(self, handler_input, exception):
        logger.error(exception, exc_info=True)
        speech_text = f"He detectado un error interno: {str(exception)}. Por favor revise los logs."
        ssml_text = f"<speak><voice name='Enrique'>{speech_text}</voice></speak>"
        return handler_input.response_builder.speak(ssml_text).response

class FallbackIntentHandler(AbstractRequestHandler):
    """Handler for Fallback Intent.
    AMAZON.FallbackIntent is only available in en-US locale.
    This handler will not be triggered except in that locale,
    so it is safe to deploy on any locale.
    """
    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        logger.info("In FallbackIntentHandler")
        speech_text = "Disculpe, jefe, no entendí esa instrucción. Mi procesador de lenguaje natural está en 99%, pero esa frase se me escapó. ¿Puede repetir?"
        ssml_text = f"<speak><voice name='Enrique'>{speech_text}</voice></speak>"
        return (
            handler_input.response_builder
            .speak(ssml_text)
            .ask(ssml_text)
            .response
        )

# Request Interceptor to log incoming JSON
from ask_sdk_core.dispatch_components import AbstractRequestInterceptor
class RequestLogger(AbstractRequestInterceptor):
    def process(self, handler_input):
        logger.info(f"Incoming Request: {handler_input.request_envelope.request}")

sb = SkillBuilder()
sb.add_global_request_interceptor(RequestLogger())
sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(AskJarvisIntentHandler())
sb.add_request_handler(ControlDeviceIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(YesIntentHandler())
sb.add_request_handler(NoIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()
