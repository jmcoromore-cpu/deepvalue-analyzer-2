# Guía completa: subir la app a GitHub (pública) manteniendo tus datos privados

## La idea clave (por qué es seguro)

El **código** y los **secretos** están separados a propósito:

- El código (público en GitHub) lee las claves desde *variables de entorno*.
- Tus claves reales viven **solo** en tu archivo `.env` local, que `.gitignore` excluye del repositorio.

Resultado: el repo puede ser 100 % público y tus datos siguen siendo 100 % privados.
No necesitas "secretos de GitHub" ni un segundo repositorio.

> Verificado: en este proyecto no hay ningún `.env` real ni ninguna clave incrustada.
> El `.env.example` solo contiene valores de ejemplo. El `.gitignore` bloquea `.env`,
> `.env.local` y `*.env`, y permite únicamente `.env.example`.

---

## Paso 1 — Consigue tus API keys (5 min)

### A) Google Gemini (análisis con IA)
1. Entra en https://aistudio.google.com/app/apikey con tu cuenta de Google.
2. Pulsa **Create API key** y copia la clave (empieza por `AIza...`).
3. Es gratuita con límites generosos.

### B) Identidad SEC (datos de empresas de EE. UU.)
No es una API key: solo tu nombre y correo, que la SEC exige para identificar
quién consulta. Ejemplo: `Jose Coromore tu.correo@gmail.com`.

### C) Alpha Vantage (opcional)
En https://www.alphavantage.co/support/#api-key introduces tu correo y te dan
una clave gratis al instante. Si no la quieres, déjala vacía: la app funciona igual.

---

## Paso 2 — Crea el repositorio en GitHub

1. Ve a https://github.com/new
2. Nombre: `deepvalue-analyzer` (o el que prefieras).
3. Marca **Public**.
4. **NO** marques "Add README / .gitignore / license" (ya vienen incluidos).
5. **Create repository** y copia la URL que te muestra.

---

## Paso 3 — Sube el código

Abre una terminal **dentro de la carpeta `deepvalue-analyzer`** y ejecuta:

```bash
git init
git add .
git commit -m "DeepValue Analyzer: análisis fundamental por ticker"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/deepvalue-analyzer.git
git push -u origin main
```

En este punto, cualquiera que entre en tu perfil verá el proyecto completo
**sin ningún dato tuyo**.

---

## Paso 4 — Configura TUS claves en local (esto NO se sube)

```bash
cp .env.example .env
```

Edita `.env` con tus valores reales:

```
SEC_IDENTITY="Jose Coromore tu.correo@gmail.com"
GEMINI_API_KEY="AIza...tu-clave-real..."
ALPHAVANTAGE_API_KEY="tu-clave-o-vacío"
```

Git ignorará este archivo automáticamente.

---

## Paso 5 — Arranca la app

**Backend** (una terminal):
```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

**Frontend** (otra terminal):
```bash
cd frontend
npm install
npm run dev
```

Abre http://localhost:5173 e introduce un ticker (`AAPL`, `MSFT`, `IBE.MC`...).

---

## Regla de oro (para no filtrar datos nunca)

Antes del primer `git push`, ejecuta:

```bash
git status
```

y **confirma que `.env` NO aparece** en la lista de archivos a subir.
Si por lo que sea apareciera, ejecútalo fuera del control de versiones:

```bash
git rm --cached .env
```

Con el `.gitignore` incluido, `.env` no debería aparecer nunca.

---

## Preguntas frecuentes

**¿Y si más adelante quiero desplegarla en la nube (Render, Railway, Vercel)?**
No pongas las claves en el código. Cada proveedor tiene un panel de
"Environment Variables" donde pegas `GEMINI_API_KEY`, `SEC_IDENTITY`, etc.
Cumplen la misma función que tu `.env` local, pero en el servidor.

**¿Qué son los "secretos de GitHub" entonces?**
Sirven para que GitHub Actions (los tests automáticos en la nube) puedan usar
claves sin exponerlas. En este proyecto los tests corren sin claves, así que
no los necesitas. Si algún día añades tests que llamen a la API real, se
configuran en: repositorio → Settings → Secrets and variables → Actions.

**¿Necesito dos repos (uno privado y otro público)?**
No. Como tus datos nunca están en el código, un único repo público es
suficiente y es lo habitual en proyectos open source. Mantener dos copias
sincronizadas es más trabajo y más propenso a errores.
