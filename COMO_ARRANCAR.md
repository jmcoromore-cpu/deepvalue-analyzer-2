# Cómo arrancar DeepValue Analyzer (uso diario)

La instalación (Python, Node, librerías) ya está hecha y NO se repite.
Para usar la app solo necesitas abrir 2 ventanas de CMD en la carpeta del proyecto.

Truco para abrir CMD en la carpeta correcta:
GitHub Desktop → Repository → Show in Explorer → clic en la barra de direcciones
del Explorador → escribe `cmd` → Enter.

---

## Ventana 1 — Backend (el motor)

```
cd backend
.venv\Scripts\activate
uvicorn main:app --reload --port 8000
```

Espera a ver "Application startup complete" y DEJA la ventana abierta.

## Ventana 2 — Frontend (la web)

```
cd frontend
npm run dev
```

(Nota: `npm install` solo hace falta la primera vez, ya no.)

## Abrir la app

En el navegador entra en:  http://localhost:5173

Escribe un ticker (AAPL, MSFT, IBE.MC...) y pulsa Analizar.

## Para cerrar

Pulsa Ctrl + C en las dos ventanas, o simplemente ciérralas.

---

## Tu API key (configuración única)

Tus claves van en un archivo llamado `.env` en la carpeta principal del proyecto
(copiado de `.env.example`). Contenido:

```
SEC_IDENTITY="Tu Nombre tu.correo@gmail.com"
GEMINI_API_KEY="AIza...tu-clave..."
ALPHAVANTAGE_API_KEY=""
```

- La clave de Gemini se saca gratis en https://aistudio.google.com/app/apikey
- Si cambias el `.env`, reinicia el backend (Ctrl + C y volver a arrancarlo) para
  que lea los nuevos valores.
- El `.env` está protegido por `.gitignore`: tus claves nunca se suben a GitHub.
- Sin clave de Gemini la app funciona igual, pero el análisis cualitativo lo hace
  por reglas en vez de con IA.
```
