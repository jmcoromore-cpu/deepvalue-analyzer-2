# Cómo subir DeepValue Analyzer a un nuevo repositorio de GitHub

Sigue estos pasos desde la carpeta `deepvalue-analyzer/` en tu ordenador.

## 1. Crea el repositorio vacío en GitHub

Ve a <https://github.com/new>, ponle un nombre (por ejemplo `deepvalue-analyzer`),
**no** marques "Add a README / .gitignore / license" (ya vienen incluidos), y pulsa
**Create repository**. Copia la URL que te da (algo como
`https://github.com/TU_USUARIO/deepvalue-analyzer.git`).

## 2. Inicializa git y sube el proyecto

Abre una terminal dentro de la carpeta `deepvalue-analyzer` y ejecuta:

```bash
git init
git add .
git commit -m "DeepValue Analyzer: análisis fundamental a partir del ticker"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/deepvalue-analyzer.git
git push -u origin main
```

> ⚠️ **Importante:** el archivo `.env` está excluido por `.gitignore`, así que tus
> claves API **nunca** se subirán. Solo se sube `.env.example` como plantilla.

## 3. Prueba la app en local

```bash
# 1) configura tus claves
cp .env.example .env        # y edita .env con tu GEMINI_API_KEY y SEC_IDENTITY

# 2) backend
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000               # http://localhost:8000/docs

# 3) frontend (en otra terminal)
cd frontend
npm install
npm run dev                                         # http://localhost:5173
```

O todo junto con Docker:

```bash
docker compose up --build
```

## 4. Verás que funciona

- Introduce un ticker (por ejemplo `AAPL`, `MSFT` o `IBE.MC` para Iberdrola).
- La app extrae los datos, calcula ratios y las 4 valoraciones, y muestra el
  veredicto (COMPRAR / MANTENER / EVITAR) con el análisis cualitativo del moat,
  las 5 fuerzas de Porter y el equipo gestor.

## Notas

- Sin `GEMINI_API_KEY`, la app funciona igualmente y genera el análisis cualitativo
  por reglas (con menor detalle). Añade la clave para el análisis con IA.
- La cobertura de datos depende de la fuente: EDGAR da más histórico pero solo para
  empresas de EE. UU.; yfinance cubre todo el mundo con algo menos de profundidad.
- Los tests del backend se ejecutan con `cd backend && pytest -q`.
