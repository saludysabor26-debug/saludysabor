#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agrega la tarjeta "Versión de la app" a Mi Perfil (y una línea discreta
en el login) del index.html de Salud & Sabor.

USO:  python3 agregar_version.py

- Hace una copia de seguridad con fecha ANTES de tocar nada.
- Si no encuentra algo esperado, ABORTA sin modificar el archivo.
- Si ya fue aplicado antes, avisa y no hace nada.
"""
import io, os, re, shutil, sys
from datetime import datetime

ARCHIVO = "index.html"

# ── Edita estos dos valores en cada publicación ──────────────
VERSION = "1.1.0"
FECHA   = "04 sep 2026"
# ─────────────────────────────────────────────────────────────

def abortar(msg):
    print("\n❌ ABORTADO: " + msg)
    print("   El archivo NO fue modificado.\n")
    sys.exit(1)

if not os.path.exists(ARCHIVO):
    abortar("no encuentro '%s'. Corre el script dentro de la carpeta del proyecto." % ARCHIVO)

s = io.open(ARCHIVO, encoding="utf-8").read()
original = s

if "APP_VERSION" in s:
    print("\n⚠️  Este archivo YA tiene APP_VERSION. No hago nada.")
    print("   Para cambiar la versión, edita a mano las lineas de APP_VERSION / APP_BUILD.\n")
    sys.exit(0)

# 1) Copia de seguridad
copia = "index_ANTES_%s.html" % datetime.now().strftime("%Y-%m-%d_%H%M%S")
shutil.copy2(ARCHIVO, copia)
print("\n💾 Copia de seguridad: %s" % copia)

# 2) Constantes de versión
if s.count("const USERS = [") != 1:
    abortar("no encontre 'const USERS = [' (o hay mas de uno).")
s = s.replace("const USERS = [",
    '// ── VERSION DE LA APP ──────────────────────\n'
    '// \U0001F449 Sube estos dos valores CADA VEZ que publiques.\n'
    'const APP_VERSION = "%s";\n'
    'const APP_BUILD   = "%s";\n\n'
    'const USERS = [' % (VERSION, FECHA), 1)

# 3) Tarjeta de version en Mi Perfil: se inserta despues del </Card>
#    que sigue al boton "Guardar contrasena".
m = re.search(r"Guardar contraseña\s*</Btn>", s)
if not m:
    abortar("no encontre el boton 'Guardar contrasena' de Mi Perfil.")
cierre = s.find("</Card>", m.end())
if cierre == -1:
    abortar("no encontre el cierre </Card> despues del boton de contrasena.")
cierre += len("</Card>")

TARJETA = """

      {/* ── VERSION DE LA APP ── */}
      <Card>
        <div style={{display:"flex",alignItems:"center",gap:"0.7rem",marginBottom:"0.9rem"}}>
          <Logo size={34}/>
          <div>
            <div style={{fontWeight:800,fontSize:"0.88rem",color:G.text,lineHeight:1.15}}>Salud &amp; Sabor</div>
            <div style={{fontSize:"0.62rem",color:G.sub,letterSpacing:0.5}}>COMIDA SALUDABLE · by María C.</div>
          </div>
        </div>
        <div style={{display:"flex",justifyContent:"space-between",alignItems:"center",padding:"0.55rem 0",borderTop:`1px solid ${G.border}`}}>
          <span style={{fontSize:"0.78rem",color:G.sub,fontWeight:600}}>Versión de la app</span>
          <span style={{background:G.primaryLight,color:G.primaryDark,fontWeight:800,fontSize:"0.78rem",padding:"0.22rem 0.7rem",borderRadius:20,border:`1px solid ${G.primaryMid}`}}>v{APP_VERSION}</span>
        </div>
        <div style={{display:"flex",justifyContent:"space-between",alignItems:"center",padding:"0.55rem 0",borderTop:`1px solid ${G.border}`}}>
          <span style={{fontSize:"0.78rem",color:G.sub,fontWeight:600}}>Actualizada</span>
          <span style={{fontSize:"0.78rem",color:G.text,fontWeight:700}}>{APP_BUILD}</span>
        </div>
      </Card>"""

s = s[:cierre] + TARJETA + s[cierre:]

# 4) Linea discreta en el login (opcional, no aborta si no calza)
m2 = re.search(r"Ingresar\s*→\s*</Btn>\s*\n(\s*)</div>", s)
if m2:
    ind = m2.group(1)
    linea = ('\n%s<div style={{color:"rgba(255,255,255,0.75)",fontSize:"0.68rem",'
             'fontWeight:600,marginTop:"1.1rem",letterSpacing:0.5}}>'
             'v{APP_VERSION} · {APP_BUILD}</div>' % ind)
    s = s[:m2.end()] + linea + s[m2.end():]
    print("✅ Version agregada al login")
else:
    print("⚠️  No pude agregar la version al login (no pasa nada, es opcional)")

if s == original:
    abortar("no se aplico ningun cambio.")

io.open(ARCHIVO, "w", encoding="utf-8").write(s)
print("✅ Tarjeta de version agregada a Mi Perfil")
print("\n\U0001F389 Listo. Ahora revisa que se vea bien y publica con:")
print("   vercel --prod --yes")
print("\n   Si algo salio mal:  cp \"%s\" index.html\n" % copia)
