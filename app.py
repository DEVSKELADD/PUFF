from flask import Flask, request, jsonify
from flask_cors import CORS
import json
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

import os
from flask import Flask, send_from_directory

app = Flask(__name__)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# 1. Cargar el modelo de IA local
print("Cargando modelo de Inteligencia Artificial (esto puede tomar unos segundos)...")
modelo = SentenceTransformer('all-MiniLM-L6-v2')

# 2. Cargar tu base de datos de libros
print("Cargando catálogo de libros...")
with open('libros.json', 'r', encoding='utf-8') as f:
    libros = json.load(f)

# 3. Preparar la "memoria" de la IA (Embeddings enriquecidos)
print("Procesando el catálogo...")
textos_para_ia = []
for libro in libros:
    # TRUCO: Juntamos toda la info clave en una sola frase para que la IA entienda el contexto completo
    texto_combinado = f"Título: {libro['titulo']}. Autor: {libro['autor']}. Categoría: {libro['categoria']}. Sinopsis: {libro['sinopsis']}"
    textos_para_ia.append(texto_combinado)

# Convertimos esos textos en vectores matemáticos
vectores_libros = modelo.encode(textos_para_ia)

print("¡Servidor Puff listo y escuchando!")

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')

    if not user_message:
        return jsonify({"error": "El mensaje está vacío"}), 400

    try:
        # 1. FILTRO DE SALUDOS: Limpiamos el mensaje (en minúsculas y sin espacios extra)
        mensaje_limpio = user_message.lower().strip()
        
        # Lista de saludos comunes
        saludos = ["hola", "buenas", "buenos dias", "buenas tardes", "buenas noches", "hey", "saludos", "¿que tal?", "que tal"]
        
        if mensaje_limpio in saludos:
            respuesta = "¡Hola!  Soy Puff, tu asistente académico. Mi función principal es recomendarte libros de nuestra biblioteca. ¿Sobre qué materia, autor o tema te gustaría investigar hoy?"
            return jsonify({"reply": respuesta})

        # 2. SI NO ES UN SALUDO, BUSCAMOS LIBROS (El código de IA que ya tenías)
        vector_usuario = modelo.encode([user_message])
        similitudes = cosine_similarity(vector_usuario, vectores_libros)[0]
        indices_top_3 = similitudes.argsort()[-3:][::-1]
        
        respuesta_html = "¡Aquí tienes algunas recomendaciones basadas en tu búsqueda!<br><br>"
        
        for idx in indices_top_3:
            libro = libros[idx]
            puntaje = similitudes[idx] * 100 
            
            if puntaje > 15:
                respuesta_html += f" <strong>{libro['titulo']}</strong> por <em>{libro['autor']}</em><br>"
                respuesta_html += f" <strong>Categoría:</strong> {libro['categoria']}<br>"
                respuesta_html += f" <strong>Sinopsis:</strong> {libro['sinopsis']}<br>"
                
                if libro['stock'] > 0:
                    respuesta_html += f" <strong>Stock:</strong> {libro['stock']} disponibles | <strong>Ubicación:</strong> {libro['ubicacion']}<br><br>"
                else:
                    respuesta_html += f" <strong>Stock:</strong> Agotado por el momento |  <strong>Ubicación:</strong> {libro['ubicacion']}<br><br>"
        
        # 3. MENSAJE DE RESPALDO: Si escribió algo que no es un saludo, pero tampoco coincide con ningún libro
        if respuesta_html == "¡Aquí tienes algunas recomendaciones basadas en tu búsqueda!<br><br>":
            respuesta_html = "Lo siento, no encontré coincidencias exactas en mi catálogo. Recuerda que soy un asistente especializado <strong>exclusivamente en recomendar bibliografía</strong>. ¿Podrías darme detalles sobre el género, autor o tema literario que buscas?"

        return jsonify({"reply": respuesta_html})

    except Exception as e:
        print(f"Error en el servidor: {e}")
        return jsonify({"error": "Hubo un problema procesando tu solicitud en el servidor local."}), 500

@app.route('/')
def index():
    return send_from_directory(BASE_DIR, 'index.html')

@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory(BASE_DIR, filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5500, debug=True)