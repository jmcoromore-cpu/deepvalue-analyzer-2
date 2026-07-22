# 📊 DeepValue Analyzer

**Análisis fundamental exhaustivo de empresas cotizadas a partir de su _ticker_.**

Introduce el ticker de una empresa (p. ej. `AAPL`, `MSFT`, `IBE.MC`) y la aplicación extrae sus
datos financieros, replica una plantilla de valoración profesional (balance, cuenta de resultados,
flujos de caja, ratios y **4 modelos de valoración**) y emite un **veredicto de inversión**
—COMPRAR / MANTENER / EVITAR— combinando análisis **cuantitativo** con análisis **cualitativo**
(ventajas competitivas / _moat_, 5 Fuerzas de Porter, calidad del equipo gestor) potenciado por IA.

> ⚠️ **Aviso:** herramienta educativa. No es asesoramiento financiero. Ver [docs/METODOLOGIA.md](docs/METODOLOGIA.md).

---

## ✨ Características

- **Un ticker → informe completo.** Cobertura mundial vía yfinance + datos oficiales de la SEC (EE. UU.).
- **Réplica de plantilla de valoración:** balance, P&L y cash flows normalizados a 10 años con
  variación anual, CAGR-5Y y CAGR-10Y.
- **+25 ratios** (liquidez, actividad, solvencia, rentabilidad) con **semáforos** según rangos óptimos.
- **4 valoraciones:** Múltiplos, DCF, Descuento de Dividendos y Graham → precio objetivo medio,
  margen de seguridad y precio máximo de compra.
- **Análisis cualitativo con IA (Gemini):** tipo e intensidad del _moat_ (framework Pat Dorsey),
  5 Fuerzas de Porter, evaluación del equipo gestor, riesgos y tesis de inversión.
- **Score y veredicto** combinando ambos pilares con pesos configurables.
- **Frontend React** con dashboard interactivo y gráficos.

---

## 🏗️ Arquitectura

```
deepvalue-analyzer/
├── backend/          FastAPI (Python) — datos, cálculo, valoración, IA
│   └── app/
│       ├── data_sources/   yfinance · SEC EDGAR · Alpha Vantage · aggregator
│       ├── core/           financials · ratios · valuation/ · scoring · verdict
│       │   └── qualitative/  moat (Dorsey) · porter · management
│       └── ai/             gemini_analyst
├── frontend/         React + Vite + Tailwind + Recharts
└── docs/             METODOLOGIA.md
```

Detalle completo del marco conceptual en **[docs/METODOLOGIA.md](docs/METODOLOGIA.md)**.

---

## 🚀 Puesta en marcha rápida

### Requisitos
- Python 3.11+
- Node.js 18+ (para el frontend)
- (Opcional) Docker + Docker Compose

### 1. Clonar y configurar variables de entorno

```bash
git clone https://github.com/<tu-usuario>/deepvalue-analyzer.git
cd deepvalue-analyzer
cp .env.example .env
# Edita .env y añade tu GEMINI_API_KEY y tu SEC_IDENTITY (tu correo)
```

Claves necesarias (todas con instrucciones en `.env.example`):
- `SEC_IDENTITY` — tu nombre y correo (obligatorio para datos de la SEC).
- `GEMINI_API_KEY` — gratis en <https://aistudio.google.com/app/apikey> (para el veredicto con IA).
- `ALPHAVANTAGE_API_KEY` — opcional, gratis en <https://www.alphavantage.co>.

> Sin `GEMINI_API_KEY` la app **sigue funcionando**: entrega todo el análisis cuantitativo y un
> veredicto basado en reglas; solo se omite la redacción cualitativa con IA.

### 2. Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate    # en Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

La API queda en <http://localhost:8000> y la documentación interactiva en <http://localhost:8000/docs>.

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

Abre <http://localhost:5173>.

### 4. (Alternativa) Todo con Docker

```bash
cp .env.example .env   # y rellena las claves
docker compose up --build
```

- Frontend: <http://localhost:5173>
- Backend:  <http://localhost:8000/docs>

---

## 🔌 API principal

`GET /api/analyze/{ticker}` — devuelve el análisis completo en JSON:

```jsonc
{
  "profile": { "name": "...", "sector": "...", "price": 0, "market_cap": 0, ... },
  "financials": { "balance": [...], "income": [...], "cashflow": [...] },
  "ratios": { "liquidity": {...}, "solvency": {...}, "profitability": {...} },
  "valuation": {
    "multiples": 0, "dcf": 0, "dividends": 0, "graham": 0,
    "mean_valuation": 0, "margin_of_safety": 0.2,
    "max_buy_price": 0, "current_price": 0, "upside": 0
  },
  "qualitative": { "moat": {...}, "porter": {...}, "management": {...} },
  "scoring": { "quant_score": 0, "qual_score": 0, "final_score": 0 },
  "verdict": { "decision": "COMPRAR|MANTENER|EVITAR", "confidence": "...", "thesis": "...", "risks": [...] }
}
```

Parámetros opcionales de query: `?margin_of_safety=0.25&discount_rate=0.09&use_ai=true`.

---

## 🧪 Tests

```bash
cd backend
pytest -q
```

Los tests verifican que los ratios y valoraciones se calculan correctamente sobre un conjunto
de datos sintéticos de referencia.

---

## ☁️ Despliegue

- **Backend** → Render / Railway / Fly.io (imagen Docker en `backend/Dockerfile`).
- **Frontend** → Vercel / Netlify (`npm run build`, carpeta `frontend/dist`).

Recuerda configurar las variables de entorno en el panel del proveedor y actualizar
`VITE_API_BASE_URL` en el frontend para apuntar a la URL pública del backend.

---

## 📄 Licencia

MIT — ver [LICENSE](LICENSE).


