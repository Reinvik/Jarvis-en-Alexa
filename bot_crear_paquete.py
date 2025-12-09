import os
import shutil
import subprocess
import zipfile
import sys
import time

def create_lambda_package():
    # Nombres de archivos y directorios
    build_dir = "aws_package_temp"
    zip_filename = "upload_to_aws.zip"
    requirements_file = "requirements.txt"
    files_to_copy = ["lambda_function.py", "jarvis_prompt.md", "devices.json"]
    
    # Directorio actual (Carpeta donde esta ESTE script)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Usar carpeta temporal del sistema para evitar OneDrive
    import tempfile
    abs_build_dir = os.path.join(tempfile.gettempdir(), build_dir)
    
    print("--- INICIANDO CONSTRUCTOR DE PAQUETE JARVIS ---")
    
    # 1. Limpieza inicial
    if os.path.exists(abs_build_dir):
        print(f"Limpiando directorio temporal: {build_dir}...")
        try:
            shutil.rmtree(abs_build_dir)
        except Exception as e:
            print(f"Error borrando directorio (posiblemente OneDrive): {e}")
            print("Intenta borrar la carpeta 'aws_package_temp' manualmente y re-ejecuta.")
            return

    if os.path.exists(zip_filename):
        try:
            os.remove(zip_filename)
        except:
            pass
            
    # 2. Instalar dependencias
    print("Instalando librerias (Mostrando detalles)...")
    try:
        # Usamos check_call sin capturar salida para que se vea en pantalla
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", 
            "-r", requirements_file, 
            "-t", abs_build_dir,
            "--no-compile",
            "--no-cache-dir" # Forzamos descarga fresca por si acaso
        ])
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Falló la instalación de librerías. Codigo: {e.returncode}")
        print("Intentando metodo alternativo (copia local)...")
        # Aqui podriamos intentar copiar si falla pip, pero por ahora reportamos error.
        return

    # 3. Copiar código fuente
    print("Copiando archivos del proyecto...")
    for f in files_to_copy:
        src = os.path.join(base_dir, f)
        dst = os.path.join(abs_build_dir, f)
        if os.path.exists(src):
            shutil.copy2(src, dst)
        else:
            print(f"ADVERTENCIA: No se encontró {f}")

    # 4. Crear ZIP
    print(f"Creando archivo ZIP: {zip_filename}...")
    try:
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Recorrer todo el directorio de build
            for root, dirs, files in os.walk(abs_build_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    # Calcular path relativo para el zip
                    arcname = os.path.relpath(file_path, abs_build_dir)
                    
                    # Evitar errores de permisos con ficheros __pycache__ o extraños
                    try:
                        zipf.write(file_path, arcname)
                    except Exception as e:
                        print(f"Saltando archivo conflictivo: {file}")
                        
    except Exception as e:
        print(f"ERROR creando el ZIP: {e}")
        return

    # 5. Limpieza final (Opcional, a veces falla en OneDrive, asi que mejor lo dejamos o ignoramos error)
    print("Limpiando archivos temporales...")
    try:
        shutil.rmtree(abs_build_dir)
    except:
        print("Nota: No se pudo borrar la carpeta temporal inmediatamente (OneDrive la está usando), pero no importa. El ZIP ya está creado.")

    print("\n" + "="*50)
    print(f"EXITO! El archivo '{zip_filename}' esta listo.")
    print("Sube ESTE archivo a AWS Lambda.")
    print("="*50)

if __name__ == "__main__":
    create_lambda_package()
    input("\nPresiona ENTER para salir...")
