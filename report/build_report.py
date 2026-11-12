#!/usr/bin/env python
"""Build Lab 13 report DOCX for Pasit Sugrivaka (6788117)."""
import os
from docx import Document
from docx.shared import Pt, Inches, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.section import WD_SECTION
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

BASE = r"C:\Users\sawu0\Documents\LABMigu\Backend\Lab13"
SHOTS = os.path.join(BASE, "shots")
OUT = os.path.join(BASE, "6788117_lab13.docx")

GREEN = RGBColor(0x14, 0x53, 0x2D)
MIDGREEN = RGBColor(0x16, 0x65, 0x34)
GRAY = RGBColor(0x55, 0x5F, 0x5B)

doc = Document()
sec = doc.sections[0]
sec.page_height = Cm(29.7)
sec.page_width = Cm(21.0)
sec.top_margin = Cm(2.0)
sec.bottom_margin = Cm(1.9)
sec.left_margin = Cm(2.1)
sec.right_margin = Cm(2.1)

styles = doc.styles
normal = styles["Normal"]
normal.font.name = "Calibri"
normal.font.size = Pt(10.5)
normal.paragraph_format.space_after = Pt(5)
normal.paragraph_format.line_spacing = 1.12

for name, size, color, before, after in (
    ("Heading 1", 15, GREEN, 14, 6),
    ("Heading 2", 12, MIDGREEN, 10, 4),
):
    st = styles[name]
    st.font.name = "Calibri"
    st.font.size = Pt(size)
    st.font.bold = True
    st.font.color.rgb = color
    st.paragraph_format.space_before = Pt(before)
    st.paragraph_format.space_after = Pt(after)
    st.paragraph_format.keep_with_next = True


def shade(cell, fill):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill)
    tcPr.append(shd)


def p_shade(par, fill):
    pPr = par._p.get_or_add_pPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill)
    pPr.append(shd)


def p_border(par, color="C9D6CF", size="6"):
    pPr = par._p.get_or_add_pPr()
    borders = OxmlElement("w:pBdr")
    for edge in ("top", "left", "bottom", "right"):
        el = OxmlElement("w:" + edge)
        el.set(qn("w:val"), "single")
        el.set(qn("w:sz"), size)
        el.set(qn("w:space"), "4")
        el.set(qn("w:color"), color)
        borders.append(el)
    pPr.append(borders)


def code(text):
    par = doc.add_paragraph()
    par.paragraph_format.space_before = Pt(2)
    par.paragraph_format.space_after = Pt(8)
    par.paragraph_format.left_indent = Cm(0.15)
    par.paragraph_format.right_indent = Cm(0.1)
    par.paragraph_format.line_spacing = 1.0
    p_shade(par, "F3F5F4")
    p_border(par)
    lines = text.strip("\n").split("\n")
    for i, line in enumerate(lines):
        run = par.add_run(line)
        run.font.name = "Consolas"
        run.font.size = Pt(8)
        run.font.color.rgb = RGBColor(0x22, 0x2A, 0x26)
        if i < len(lines) - 1:
            run.add_break()
    return par


def para(text, bold_lead=None, size=None, italic=False, color=None):
    p = doc.add_paragraph()
    if bold_lead:
        r = p.add_run(bold_lead)
        r.bold = True
        if size:
            r.font.size = Pt(size)
    r = p.add_run(text)
    if size:
        r.font.size = Pt(size)
    r.italic = italic
    if color:
        r.font.color.rgb = color
    return p


def bullet(text, bold_lead=None):
    p = doc.add_paragraph(style="List Bullet")
    p.paragraph_format.space_after = Pt(2)
    if bold_lead:
        r = p.add_run(bold_lead)
        r.bold = True
    p.add_run(text)
    return p


def table(headers, rows, widths=None, font=9.5, header_fill="DCEFE3"):
    t = doc.add_table(rows=1, cols=len(headers))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    hdr = t.rows[0].cells
    # repeat the header row when the table breaks across pages
    trPr = t.rows[0]._tr.get_or_add_trPr()
    trPr.append(OxmlElement("w:tblHeader"))
    for i, h in enumerate(headers):
        hdr[i].text = ""
        p = hdr[i].paragraphs[0]
        p.paragraph_format.space_after = Pt(1)
        r = p.add_run(h)
        r.bold = True
        r.font.size = Pt(font)
        shade(hdr[i], header_fill)
    for row in rows:
        tr = t.add_row()
        trPr = tr._tr.get_or_add_trPr()
        trPr.append(OxmlElement("w:cantSplit"))
        cells = tr.cells
        for i, val in enumerate(row):
            cells[i].text = ""
            p = cells[i].paragraphs[0]
            p.paragraph_format.space_after = Pt(1)
            r = p.add_run(str(val))
            r.font.size = Pt(font)
    if widths:
        for i, w in enumerate(widths):
            for row in t.rows:
                row.cells[i].width = Inches(w)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    return t


def image(name, width=5.6, caption=None):
    path = os.path.join(SHOTS, name)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(2)
    p.add_run().add_picture(path, width=Inches(width))
    if caption:
        c = doc.add_paragraph()
        c.alignment = WD_ALIGN_PARAGRAPH.CENTER
        c.paragraph_format.space_after = Pt(8)
        r = c.add_run(caption)
        r.italic = True
        r.font.size = Pt(8.5)
        r.font.color.rgb = GRAY


def footer():
    f = sec.footer
    p = f.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("Pasit Sugrivaka · 6788117 · ITCS258 Lab 13   |   page ")
    r.font.size = Pt(8)
    r.font.color.rgb = GRAY
    fld = OxmlElement("w:fldSimple")
    fld.set(qn("w:instr"), "PAGE")
    rn = OxmlElement("w:r")
    t = OxmlElement("w:t")
    t.text = "1"
    rn.append(t)
    fld.append(rn)
    p._p.append(fld)


def small(text):
    p = doc.add_paragraph()
    r = p.add_run(text)
    r.font.size = Pt(9)
    r.font.color.rgb = GRAY
    return p


footer()

# ---------------------------------------------------------------- title
t = doc.add_paragraph()
t.paragraph_format.space_after = Pt(2)
r = t.add_run("Lab 13 — Deployment Experiment Report")
r.font.size = Pt(21)
r.bold = True
r.font.color.rgb = GREEN
sub = doc.add_paragraph()
sub.paragraph_format.space_after = Pt(10)
r = sub.add_run("Compose override · local NPM reverse proxy · CORS · Ubuntu VM")
r.font.size = Pt(10.5)
r.font.color.rgb = GRAY
r2 = sub.add_run("\nDr. Pisit Praiwattana, your mentor in 2026")
r2.font.size = Pt(10)
r2.font.color.rgb = GRAY
r2.italic = True

info = [
    ("Student ID / รหัสนักศึกษา", "6788117"),
    ("Name / ชื่อ", "Pasit Sugrivaka"),
    ("Laptop OS, VM OS and Docker versions", "Laptop: Windows 11 (Docker Desktop 29.8.0, Docker Engine 29.8.0)\n"
     "VM: Ubuntu 26.04.1 LTS on WSL2, Docker Engine 29.1.3, Docker Compose 2.40.3"),
    ("Repository URL", "https://github.com/Sor117/itcs258-lab13"),
]
tb = doc.add_table(rows=0, cols=2)
tb.style = "Table Grid"
tb.autofit = False
for label, val in info:
    cells = tb.add_row().cells
    cells[0].text = ""
    cells[1].text = ""
    p0 = cells[0].paragraphs[0]
    r = p0.add_run(label)
    r.bold = True
    r.font.size = Pt(9.5)
    shade(cells[0], "F1F5F2")
    p1 = cells[1].paragraphs[0]
    r1 = p1.add_run(val)
    r1.font.size = Pt(9.5)
    cells[0].width = Inches(1.85)
    cells[1].width = Inches(4.65)
doc.add_paragraph().paragraph_format.space_after = Pt(0)

small("All four experiments use the same gacha-workshop project and the same STUDENT_ID=6788117. "
      "The laptop is Windows 11 with Docker Desktop; the Ubuntu server is a WSL2 Ubuntu 26.04 instance with its own "
      "Docker Engine, SSH access and storage.")

# ---------------------------------------------------------------- 01
doc.add_heading("01 — Compose override + direct port / Compose override และพอร์ตตรง", level=1)

para("Base + local overlay, started with every -f listed explicitly:")
code("""cd gacha-workshop
docker compose --env-file .env -f compose.yml -f compose.local.yml config --quiet
docker compose --env-file .env -f compose.yml -f compose.local.yml up -d --build --wait
docker compose --env-file .env -f compose.yml -f compose.local.yml ps""")

para("config --quiet printed nothing and exited 0. The merged config shows the port that the local overlay adds:")
code("""services:
  app:
    ports:
      - mode: ingress
        host_ip: 127.0.0.1
        target: 3000
        published: "8085"
        protocol: tcp""")

para("ps shows the app published on loopback only and PostgreSQL with no host port:")
code("""NAME                  SERVICE   STATUS                    PORTS
gacha-6788117-app-1   app       Up (healthy)              127.0.0.1:8085->3000/tcp
gacha-6788117-db-1    db        Up (healthy)              5432/tcp""")

para("In http://localhost:8085/test with Student ID 6788117 I ran Health → Wallet → Recharge 1000 → "
     "Exchange 1000 → Draw once → Saved history. Results: 200, 200, 201, 201, 201 (Copper Golem, COMMON) and 200. "
     "The saved history came back with the draw row and the two coin transactions.")

para("Merge table from my own config runs:", bold_lead=None)
table(["Command (shortened)", "app ports I saw", "restart I saw"],
      [["docker compose config", "127.0.0.1:8085 → 3000", "–"],
       ["docker compose -f compose.yml config", "none", "–"],
       ["... -f compose.yml -f compose.production.yml -f compose.proxy.yml config", "none (npm: 80, 443, 127.0.0.1:81)", "unless-stopped"],
       ["... -f compose.yml -f compose.local.yml -f compose.production.yml config", "127.0.0.1:8085 → 3000 still there", "unless-stopped"]],
      widths=[3.05, 2.35, 1.15])

para("id 1 · Copper Golem (COMMON) · 2026-11-11T04:09:56.243Z (11:09:56 GMT+7). The same row read from the container:",
     bold_lead="Original local draw: ")
code("""docker compose --env-file .env -f compose.yml -f compose.local.yml exec -T db \\
  psql -U gacha -d gacha -c "SELECT id, result_name, created_at FROM draws ORDER BY id;"

 id | result_name  |          created_at
----+--------------+-------------------------------
  1 | Copper Golem | 2026-11-11 04:09:56.243929+00""")

para("-f replaces the automatic file list. compose.override.yml is only loaded when no -f is given, so an explicit "
     "run uses exactly the files I list: base, one environment overlay, then optional helpers.",
     bold_lead="Why is compose.override.yml not used when you pass -f? ")
para("ports is a list and Compose adds lists together instead of replacing them. The local overlay still contributes "
     "8085 and the production overlay adds no ports, so 8085 stays published. Only one environment overlay should be used.",
     bold_lead="Why does local + production still publish 8085? ")

para("The merge is easy to prove: the same yaml file shows 8085 under local and no ports under production. "
     "The pitfall is that adding production after local cannot remove the earlier port. "
     "config prints real .env values, so I only copied short, sanitized snippets into this report.",
     bold_lead="Evidence and explanation: ")

image("01-history-crop.png", 5.3, "Saved history on the direct port: HTTP 200, GET /api/accounts/6788117/history, "
      "with the draw transaction at the same time as draw id 1.")

# ---------------------------------------------------------------- 02
doc.add_heading("02 — Reverse proxy with local NPM / Reverse proxy ด้วย NPM ในเครื่อง", level=1)

para("Production + proxy, with the same project and volume:")
code("""docker compose --env-file .env -f compose.yml -f compose.local.yml down
docker compose --env-file .env -f compose.yml -f compose.production.yml \\
  -f compose.proxy.yml up -d --build --wait
docker compose --env-file .env -f compose.yml -f compose.production.yml \\
  -f compose.proxy.yml ps""")
code("""NAME                  SERVICE   STATUS       PORTS
gacha-6788117-app-1   app       Up healthy   3000/tcp
gacha-6788117-db-1    db        Up healthy   5432/tcp
gacha-6788117-npm-1   npm       Up           0.0.0.0:80->80, 443->443, 127.0.0.1:81->81""")

para("I created the NPM admin at http://127.0.0.1:81 and added the proxy host in the lab order: domain localhost, "
     "scheme http, forward app:3000. The four screenshots below are from that NPM instance.")
image("npm-1-add-proxy-host.png", 5.9, "Step 1 Details tab: localhost → http, app, 3000, Publicly Accessible.")
image("npm-1-list-crop.png", 6.2, "Proxy Hosts list: localhost → http://app:3000, HTTP Only, Public, Online.")
image("npm-2-custom-location.png", 5.9, "Step 2 Custom Location /backend/ with the gear editor and the rewrite line.")
image("npm-3-domain-gacha-test.png", 5.9, "Step 3 Domain Names with both chips: localhost and gacha.test.")

para("Step test table — what I observed:")
table(["Step", "URL", "Observed status / result"],
      [["0", "http://localhost/ (no proxy host yet)", "200 NPM default welcome page"],
       ["1", "http://localhost/health", "200 {\"status\":\"ok\",\"database\":\"connected\",\"app\":\"gacha\"}"],
       ["1", "http://localhost/test → Health", "200; GET http://localhost/health"],
       ["2", "http://localhost/backend/test → Health", "200; GET http://localhost/backend/health"],
       ["2", "http://localhost/backend/api/catalog", "200 JSON"],
       ["2", "http://localhost/backend", "301 → Location: http://localhost/backend/"],
       ["2", "http://localhost/backend/", "200 app root JSON"],
       ["2", "http://localhost/backendX", "404 Route not found"],
       ["3", "http://gacha.test/backend/test before adding gacha.test", "404, Server: openresty (no proxy host matched the Host header)"],
       ["3", "http://gacha.test/backend/test after adding it", "200; GET http://gacha.test/backend/health"],
       ["3", "curl.exe -v http://gacha.test/backend/health", "Trying 127.0.0.1:80… 200 OK"]],
      widths=[0.4, 2.35, 3.75], font=8.5)

para("Browser results for the three required URLs:")
image("npm-1-test-localhost-crop.png", 5.5, "http://localhost/test → Health: GET http://localhost/health, HTTP 200.")
image("npm-2-test-backend-crop.png", 5.5, "http://localhost/backend/test → Health: GET http://localhost/backend/health, HTTP 200.")
image("npm-3-test-gacha-crop.png", 5.5, "http://gacha.test/backend/test → Health: GET http://gacha.test/backend/health, HTTP 200.")

para("Nginx matches the location /backend/ only, so /backend (no trailing slash) does not match it and NPM answers 301 "
     "to /backend/; the app then serves the root JSON. /backendX is not matched either, so location / sends it unchanged "
     "to the app, which answers 404 Route not found. If the location were /backend (no slash), /backend itself would be "
     "sent to the app as 404 and /backendX would be captured by that location.",
     bold_lead="/backend/ versus /backend: ")

para("Laptop browser → NPM :80 (Host: gacha.test, path: /backend/test) → app:3000 (path: /test) → db:5432",
     bold_lead="Request path: ")

table(["Item", "Direct local (01)", "Local proxy (02)"],
      [["Browser URL", "http://localhost:8085/test", "http://gacha.test/backend/test"],
       ["Host entry port", "8085 (published by compose.local.yml)", "80 (published by NPM; the app has no host port)"],
       ["App service/internal port", "3000", "3000"],
       ["Database volume name", "gacha-6788117_pgdata", "gacha-6788117_pgdata"],
       ["Original draw ID + created_at", "1 / 2026-11-11T04:09:56.243Z", "1 / 2026-11-11T04:09:56.243Z"]],
      widths=[1.65, 2.45, 2.4], font=9)

para("On the laptop gacha.test is 127.0.0.1 inside the Windows hosts file. On the Ubuntu VM the laptop hosts file "
     "points to the VM address and the VM needs no hosts change; NPM admin is reached through an SSH tunnel because "
     "port 81 stays on loopback. A public VPS uses a real DNS A/AAAA record instead of hosts, opens only 80/443 and SSH, "
     "and gets HTTPS from NPM's SSL tab with a real domain.",
     bold_lead="Local versus server: ")

para("Inside the npm container localhost is the container itself, not the laptop. Port 3000 there is NPM's own admin "
     "API, so it returns NPM's 404 instead of the app, and the hostname localhost cannot be resolved by the nginx "
     "resolver, which gives 502. The app is only reachable by its Compose service name app on the shared project network.",
     bold_lead="Why localhost inside NPM is never my app (use app:3000): ")
para("Online only means nginx accepted and loaded the generated configuration. It does not test the upstream: a wrong "
     "forward host still shows Online and fails with 502 at request time.",
     bold_lead="Why STATUS Online does not prove the upstream works: ")

para("I tried the optional experiment: I changed Forward Hostname / IP to localhost, saved, and opened /health. "
     "NPM still showed Online but returned 502, and its error log said localhost could not be resolved. "
     "The custom location (/backend/ → app:3000) kept working, which proved only the root location was wrong. "
     "I set the value back to app and /health returned 200 again.")
code("""2026/11/11 04:18:25 [error] 353#353: *195 localhost could not be resolved (3: Host not found),
client: 172.20.0.1, server: gacha.test, request: "GET /health HTTP/1.1", host: "localhost\"""")

para("The 01 draw read through the proxy, without drawing again:")
code("""curl.exe -s http://localhost/backend/api/accounts/6788117/history
{"transactions":[...],"draws":[{"id":"1","student_id":"6788117","result_id":"copper-golem",
"result_name":"Copper Golem","rarity":"COMMON","transaction_id":"3",
"created_at":"2026-11-11T04:09:56.243Z"}]}""")

# ---------------------------------------------------------------- 03
doc.add_heading("03 — CORS experiment with Docker Compose / ทดลอง CORS ด้วย Docker Compose", level=1)

para("Local + CORS overlay (app 8085, db internal, tester 5500):")
code("""docker compose --env-file .env -f compose.yml -f compose.local.yml -f compose.cors.yml up -d --build --wait
docker compose --env-file .env -f compose.yml -f compose.local.yml -f compose.cors.yml ps

NAME                     SERVICE   STATUS       PORTS
gacha-6788117-app-1      app       Up (healthy) 127.0.0.1:8085->3000/tcp
gacha-6788117-db-1       db        Up (healthy) 5432/tcp
gacha-6788117-tester-1   tester    Up (healthy) 127.0.0.1:5500->5500/tcp""")

para("The visual tester shows the whole request path; red means the browser hid the response, green means it read it.")
image("cors-0-same-origin.png", 5.45, "Same origin: http://localhost:8085/visual/ and the API share http://localhost:8085, no CORS needed.")
image("cors-1-blocked.png", 5.45, "Blocked: page http://localhost:5500, API http://localhost:8085, CORS_ORIGINS empty.")
image("cors-2-allowed.png", 5.45, "Allowed after recreating: CORS_ORIGINS=http://localhost:5500; recharge/exchange/draw/history all green.")
image("cors-3-127-mismatch.png", 5.45, "127.0.0.1:5500 is a different origin from localhost:5500, so it is blocked again.")

para("CORS evidence table:")
table(["Stage", "What I did", "Evidence", "Result"],
      [["Same origin", "http://localhost:8085/visual/ → Connect", "cors-0 screenshot", "\"Same origin… no CORS setting is needed\", /health 200"],
       ["Blocked", "http://localhost:5500 with API http://localhost:8085, CORS_ORIGINS empty", "cors-1 + Console", "✕ CORS at page node; console says No 'Access-Control-Allow-Origin'"],
       ["Server answered", "curl -H \"Origin: http://localhost:5500\" http://localhost:8085/health", "terminal", "HTTP 200 + health JSON, no Access-Control-Allow-Origin"],
       ["App log", "docker compose … logs app", "terminal", "CORS_ORIGINS = (empty…); CORS: page origin http://localhost:5500 is not in CORS_ORIGINS (empty)"],
       ["restart", "edit .env, restart app, exec app printenv CORS_ORIGINS", "terminal", "empty line; curl still has no header"],
       ["up -d", "up -d --wait app, printenv CORS_ORIGINS", "terminal", "http://localhost:5500; Vary: Origin + Access-Control-Allow-Origin"],
       ["Allowed", "reload http://localhost:5500 → Connect → Recharge → Exchange → Draw → History", "cors-2 screenshot", "all nodes green, POST 201, GET 200"],
       ["Preflight", "curl -X OPTIONS http://localhost:8085/api/draw …", "terminal", "204 with ACAO, Allow-Methods, Allow-Headers, Max-Age 600"],
       ["127.0.0.1 trap", "http://127.0.0.1:5500 → Connect", "cors-3 + app log", "✕ CORS; origin http://127.0.0.1:5500 is not in CORS_ORIGINS (http://localhost:5500)"],
       ["Through proxy (optional)", "http://gacha.test/backend/visual/ → Connect", "cors-4 screenshot", "Same origin: page and API share http://gacha.test"]],
      widths=[0.85, 2.05, 1.35, 2.25], font=8)

para("Key outputs:")
code("""# blocked, server still answered
HTTP/1.1 200 OK
{"status":"ok","database":"connected","app":"gacha","version":"dev"}

# after restart app (new value in .env, old container)
$ docker compose ... exec app printenv CORS_ORIGINS
                      <- empty line

# after up -d --wait app
$ docker compose ... exec app printenv CORS_ORIGINS
http://localhost:5500
Vary: Origin
Access-Control-Allow-Origin: http://localhost:5500

# preflight
HTTP/1.1 204 No Content
Access-Control-Allow-Origin: http://localhost:5500
Access-Control-Allow-Methods: GET, POST, OPTIONS
Access-Control-Allow-Headers: Content-Type
Access-Control-Max-Age: 600""")

image("cors-4-proxy-same-origin.png", 5.45, "Through NPM: the page and the API share http://gacha.test, so no CORS is involved.")

para("restart only stops and starts the existing container. Its environment was fixed when the container was created, "
     "so the new .env value is not read; up -d compares the desired configuration, sees the changed value and recreates "
     "the container.",
     bold_lead="Why restart did not apply CORS_ORIGINS: ")
para("An origin is scheme + host + port. The host names are compared as strings, so 127.0.0.1 and localhost are "
     "different origins even though they reach the same server on the same machine.",
     bold_lead="Why 127.0.0.1:5500 and localhost:5500 are different origins: ")
para("NPM serves the page and forwards /backend/ on the same host and port, so the browser sees one origin and "
     "never sends a cross-origin request.",
     bold_lead="Why the proxy makes the page and API same-origin (one sentence): ")

para("The 127.0.0.1 trap is the most useful part: the app log showed CORS_ORIGINS (http://localhost:5500) while the "
     "page origin was http://127.0.0.1:5500. Opening the listed origin fixed it without changing the server. "
     "CORS_ORIGINS=* would allow every origin, but it is only acceptable for this authless classroom API.",
     bold_lead="Evidence and explanation: ")

# ---------------------------------------------------------------- 04
doc.add_heading("04 — Ubuntu VM as the server / ใช้ Ubuntu VM เป็นเซิร์ฟเวอร์", level=1)

para("The second host is an Ubuntu 26.04.1 LTS instance on WSL2 with its own Docker Engine, SSH server and disk. "
     "It has the address 172.31.236.39 and uses NAT, not bridged networking: Docker publishes 80/443 on the VM "
     "interface and 81 on the VM loopback only, and Windows reaches the VM address directly, so no port forwarding "
     "was needed on the laptop. The NPM admin page is opened through an SSH tunnel.")

code("""Laptop (Windows 11)
  hosts: 172.31.236.39 gacha.test
  browser http://gacha.test/backend/test
        |
        | TCP 80, Host: gacha.test, path /backend/test
        v
Ubuntu VM (WSL2, 172.31.236.39)
  NPM container :80/:443 (admin 127.0.0.1:81, reached with ssh -L 8181:127.0.0.1:81)
        | proxy_pass http://app:3000, path /test
        v
  app container :3000  --->  db container :5432  --->  volume gacha-6788117_pgdata""")

para("SSH session and basic shell operations on the VM:")
code("""student@ubuntu-server:~$ pwd
/home/student
student@ubuntu-server:~$ ls -la ~/apps/gacha-workshop | head -5
total 308
drwxr-xr-x 8 student student  4096 Nov 11 11:27 .
drwxr-xr-x 3 student student  4096 Nov 11 11:27 ..
-rwxr-xr-x 1 student student   166 Nov 11 11:27 .dockerignore
-rwxr-xr-x 1 student student   110 Nov 11 11:27 .env
student@ubuntu-server:~$ mkdir -p ~/notes && cd ~/notes && pwd
/home/student/notes""")

para("VM identification and Docker service:")
code("""student@ubuntu-server:~$ hostnamectl
 Static hostname: ubuntu-server
Operating System: Ubuntu 26.04.1 LTS
          Kernel: Linux 6.18.33.2-microsoft-standard-WSL2
    Architecture: x86-64
student@ubuntu-server:~$ free -h | head -2
               total        used        free      shared  buff/cache   available
Mem:            15Gi       2.5Gi       9.8Gi        61Mi       3.4Gi        12Gi
student@ubuntu-server:~$ df -h / | tail -1
/dev/sdf       1007G  5.5G  951G   1% /
student@ubuntu-server:~$ ip -br address
eth0  UP  172.31.236.39/20
student@ubuntu-server:~$ sudo systemctl status docker --no-pager
     Active: active (running)
student@ubuntu-server:~$ sudo docker compose version
Docker Compose version 2.40.3+ds1-0ubuntu1""")

para("Copy and startup, from the laptop and then the VM:")
code("""scp -r gacha-workshop student@172.31.236.39:~/apps/
ssh student@172.31.236.39
cd ~/apps/gacha-workshop
cp .env.example .env && nano .env        # STUDENT_ID=6788117, own .env
sudo docker compose --env-file .env -f compose.yml -f compose.production.yml -f compose.proxy.yml \\
  up -d --build --wait""")

para("NPM on the VM was reached through the tunnel, not by opening port 81:")
code("""ssh -L 8181:127.0.0.1:81 student@172.31.236.39
# browser: http://localhost:8181  -> new NPM admin for the VM""")
image("vm-npm-3-list-crop.png", 6.2, "The VM's own NPM: one proxy host for gacha.test + localhost → http://app:3000, Online.")

para("Then the laptop hosts file was changed to the VM address (only one gacha.test line) and the same URL was tested:")
code("""C:\\Windows\\System32\\drivers\\etc\\hosts
172.31.236.39 gacha.test

curl.exe -v http://gacha.test/backend/health
*   Trying 172.31.236.39:80...
< HTTP/1.1 200 OK""")
image("vm-4-test-gacha-crop.png", 5.5, "http://gacha.test/backend/test through the VM: Health 200, recharge/exchange/draw 201, history 200.")

para("VM persistence — app container recreated, storage untouched:")
table(["Item", "Before app replacement", "After app replacement"],
      [["App container ID", "9219ea89b0af…", "b9e6ed93402c…"],
       ["DB volume identity", "gacha-6788117_pgdata", "gacha-6788117_pgdata"],
       ["Original VM draw ID + created_at", "1 / 2026-11-11T04:33:34.579Z", "1 / 2026-11-11T04:33:34.579Z"]],
      widths=[2.05, 2.2, 2.2], font=9)
image("vm-5-history-after-crop.png", 5.5, "Saved history after up -d --force-recreate --wait app: same draw id 1, Stone Knight, same time.")
code("""sudo docker compose ... ps -q app
9219ea89b0afe5f51199d7f70fb28146f14100b23b456fc4750d56262d084f4e
sudo docker compose ... up -d --force-recreate --wait app
sudo docker compose ... ps -q app
b9e6ed93402c62e52f8af2a8cbe7c79255a120a1eac764b341e4640a6406c3c6
sudo docker volume ls
local  gacha-6788117_pgdata""")

para("The VM has its own /var/lib/docker and its own gacha-6788117_pgdata volume. Draw IDs start again at 1 and the "
     "laptop draws are not present, so the storage really is separate. Recreating the app container kept the same "
     "database and the same draw.",
     bold_lead="Separate storage: ")

para("A public VPS needs a real domain with a DNS A/AAAA record to the server, provider firewall rules, and only "
     "ports 80/443 plus the SSH port exposed. NPM's SSL tab requests the Let's Encrypt certificate and Force SSL, "
     "which is impossible with the reserved .test name. Allow SSH before enabling UFW so the session is not lost; "
     "Docker-published ports can bypass UFW, so app, DB and admin ports stay unpublished or loopback-only. "
     "The developer still owns updates, backups, log review, certificate renewal and access control.",
     bold_lead="Public VPS requirements: ")

# ---------------------------------------------------------------- reflection
doc.add_heading("Diagnosis and reflection / วิเคราะห์ปัญหาและสะท้อนผล", level=1)

para("Symptom → hypothesis → check → fix", bold_lead="", italic=True, color=GRAY)
para("After I first saved the localhost proxy host, /health returned 502 while the Proxy Hosts list still said Online. "
     "My hypothesis was a wrong upstream name, not a broken app. I checked the NPM error log and read "
     "\"localhost could not be resolved (3: Host not found)\", then confirmed the app itself was healthy through the "
     "/backend/ location. I changed Forward Hostname / IP back to app and /health returned 200. "
     "The preventive check is to open /health after every NPM save and to remember that Online only means the nginx "
     "configuration loaded.")

para("Production publishes no app or database ports because only NPM is exposed to the outside world. "
     "NPM terminates HTTP/HTTPS, chooses the proxy host by Host header and the location by path, rewrites /backend/ "
     "and forwards to app:3000 over the Compose network. The database stays on the private network with no host port.",
     bold_lead="Why production publishes no ports, and what the proxy does instead: ")

para("NPM compared the Host header gacha.test with the server_name list of each proxy host and chose the host that "
     "contained both localhost and gacha.test. Inside that server it used the longest matching prefix, /backend/, "
     "applied the rewrite and proxied the rest of the path to app:3000.",
     bold_lead="How NPM chose the proxy host and location for http://gacha.test/backend/test: ")

para("The URL, DNS/hosts entry, TLS and storage change between the laptop and the VM. What does not change is the "
     "developer's work: keeping images and base images updated, monitoring logs and disk, backing up the pgdata "
     "volume, renewing certificates, limiting public ports and reviewing the proxy configuration before production.",
     bold_lead="What changed between laptop and VM: ")

para("Why restart does not reload .env, how Compose decides to recreate a container, and longest-prefix matching "
     "for /backend/. I expected restart to apply the new origin, so I will review that pitfall before the quiz.",
     bold_lead="Self-quiz topic to revisit: ")

# ---------------------------------------------------------------- checklist
doc.add_heading("In-room check and final submission / ตรวจในห้องและส่งงาน", level=1)
for item in [
    "I completed 01–04 using the same working example.",
    "I demonstrated my actual experiment to the LA in the room.",
    "All evidence is from my own screen and readable.",
    "My report includes the merge evidence, my four NPM screenshots, the URL test tables, the CORS evidence table, request paths, persistence comparisons and repository URL.",
    "No actual passwords or tokens are visible.",
    "The single PDF is named student_ID_lab13.PDF, using my actual ID (6788117_lab13.PDF).",
    "I uploaded it to MyCourse by its deadline and opened the uploaded PDF to verify it.",
]:
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(3)
    r = p.add_run("[X]  ")
    r.bold = True
    r.font.color.rgb = MIDGREEN
    p.add_run(item)

doc.save(OUT)
print("saved", OUT)
