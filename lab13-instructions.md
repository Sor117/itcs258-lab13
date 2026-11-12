# Lab 13 — Deploy One Working Backend

**Compose override · Local reverse proxy (Nginx Proxy Manager) · CORS experiment · Ubuntu VM**

**Dr. Pisit Praiwattana, your mentor in 2026**

Website: [Lab 13](https://pisit-devop.com/itcs258/Lab13/)

Use the **same gacha workshop** for required experiments **01–04**, in this order. Run one environment at a time and keep the same `STUDENT_ID` for the whole lab. Railway/Render/Vercel hosting moved to Lab 14 · CI/CD (platform deploy); it is not part of Lab 13.

ใช้ **gacha workshop ชุดเดิม** ทำงานหลัก **01–04** ตามลำดับ รัน environment ทีละชุด และใช้ `STUDENT_ID` เดิมตลอดทั้ง lab การ host บน Railway/Render/Vercel ย้ายไปอยู่ใน Lab 14 · CI/CD (platform deploy) และไม่ใช่ส่วนของ Lab 13

**How to read this sheet**

- **NPM means Nginx Proxy Manager** (a proxy container with a web admin page), never Node's `npm` command.
- Run commands inside the extracted `gacha-workshop` folder. Every Compose command repeats the full `-f` list on purpose.
- Windows PowerShell: type `curl.exe` (`curl` can be an alias of `Invoke-WebRequest`). macOS/Linux: `curl`.
- Screenshot names (e.g. `npm-1-add-proxy-host.png`) are real captures from NPM 2.16 and Chrome, in `gacha-workshop/docs/images/` and on the Lab 13 site.

## Before you start — two ideas / ก่อนเริ่ม — สองแนวคิด

Read [Before you start](https://pisit-devop.com/itcs258/Lab13/index.html#before) on the Lab 13 site first, and be ready to explain **A** and **B** in your own words before you click anything in NPM.

**A. Compose base + override.** The base holds what every environment shares; an overlay adds only what differs.

| File | What it adds | Used in |
| --- | --- | --- |
| `compose.yml` (base) | app + db + named volume `pgdata` + healthchecks; **no published ports** | every run |
| `compose.override.yml` | app port `127.0.0.1:8085:3000` | loaded **automatically** by plain `docker compose` (Lab 12) |
| `compose.local.yml` | the same app port, chosen explicitly with `-f` | 01, 03 |
| `compose.staging.yml` | app port `127.0.0.1:8086:3000` + restart policy | `config` preview only |
| `compose.production.yml` | `restart: unless-stopped`; no ports | 02, 04 |
| `compose.proxy.yml` | service `npm` (Nginx Proxy Manager 2.16.0) on `80`, `443` and `127.0.0.1:81` | 02, 04 |
| `compose.cors.yml` | service `tester` on `127.0.0.1:5500` (a second origin) | 03 |

With `-f`, Compose reads **only the files you list**: base first, then **one** environment overlay (local or production), then optional helpers (proxy, cors). `ports` lists are **added together**, not replaced (see 01 step 6).

**B. Reverse proxy.** One public entry on 80/443 keeps the app and database private, holds HTTPS in one place, and lets the page and API share one origin. A request for `http://gacha.test/backend/test`:

(1) **name → IP** via hosts file (local) or DNS (server) → (2) the browser sends `GET /backend/test` with `Host: gacha.test` to the proxy on :80 → (3) the proxy picks the `server_name` matching the Host header (no match → NPM's default 404) → (4) picks `location /backend/` → (5) rewrites to `/test` and forwards to `app:3000` via Docker DNS (adds `X-Forwarded-*`) → (6) relays the app's answer.

อ่านหัวข้อ Before you start บนเว็บ Lab 13 ก่อน (A) `compose.yml` เก็บสิ่งที่เหมือนกันทุก environment และไม่ publish พอร์ต ไฟล์ override/overlay เพิ่มเฉพาะส่วนที่ต่างกัน `compose.override.yml` ถูกโหลดอัตโนมัติเมื่อไม่ใส่ `-f` แต่เมื่อใส่ `-f` แล้ว Compose อ่านเฉพาะไฟล์ที่ระบุ รายการ `ports` ถูกรวมกัน ไม่ได้ถูกแทนที่ (B) production ใช้ reverse proxy เป็นทางเข้าเดียวที่พอร์ต 80/443 ทำให้ app และ DB ไม่ต้อง publish พอร์ต จัดการ HTTPS ที่เดียว route ตาม Host และ path และให้หน้าเว็บกับ API อยู่ origin เดียวกันจึงไม่ต้องใช้ CORS ลำดับคือ ชื่อ → IP, เชื่อมต่อพอร์ต 80, เลือก Proxy Host จาก Host header, เลือก location จาก path, ตัด `/backend/` แล้วส่งต่อไป `app:3000` ผ่าน DNS ของ Docker และส่งคำตอบกลับ

## 01 — Compose override + direct port / Compose override และพอร์ตตรง

Goal: run base + local overlay, prove how Compose merges files, and save one real draw.

1. **Prepare `.env`** in the folder that has `compose.yml`.
   - Continuing in your Lab 12 folder? **Keep your `.env`** (do not copy `.env.example` over it), check `STUDENT_ID`, and stop the Lab 12 stack with `docker compose down` (no `-v`).
   - Freshly extracted folder only:

   ```text
   Copy-Item .env.example .env      # Windows PowerShell (fresh folder only)
   cp .env.example .env             # macOS / Linux (fresh folder only)
   notepad .env                     # Windows: set STUDENT_ID, save
   nano .env                        # macOS / Linux: set STUDENT_ID, Ctrl+O, Enter, Ctrl+X
   ```

   Keep this ID all lab: the project name `gacha-<ID>` decides the volume name `gacha-<ID>_pgdata`.

2. **Validate:** `docker compose --env-file .env -f compose.yml -f compose.local.yml config --quiet`. Expected: no output = valid (a missing value prints the hint from `compose.yml`, e.g. `Set STUDENT_ID in .env`).

3. **Start and check.** Expected `ps`: app `127.0.0.1:8085->3000/tcp` (healthy); db `5432/tcp` with no arrow (no host port).

   ```text
   docker compose --env-file .env -f compose.yml -f compose.local.yml up -d --build --wait
   docker compose --env-file .env -f compose.yml -f compose.local.yml ps
   ```

4. **Use the app.** Open `http://localhost:8085/test`, type your student ID, keep Recharge `1000` and Exchange `1000`, then click `GET · Health + DB` → `GET · Wallet` → `POST · Recharge` → `POST · Exchange` → `POST · Draw once` → `GET · Saved history`. Record the draw `id`, result and `created_at`; you read this row again in 02.

5. **Optional: see the row in PostgreSQL.** Expected: the same `id` and `created_at`:

   ```text
   docker compose --env-file .env -f compose.yml -f compose.local.yml exec db psql -U gacha -d gacha -c "SELECT id, result_name, created_at FROM draws ORDER BY id;"
   ```

6. **Compare merged configurations** (read-only). Look at `ports:` (printed as `host_ip: 127.0.0.1`, `target: 3000`, `published: "8085"`) and `restart:`.

   | Command | app ports | restart | extra services |
   | --- | --- | --- | --- |
   | `docker compose config` (auto-loads `compose.override.yml`) | 127.0.0.1:8085→3000 | – | – |
   | `docker compose -f compose.yml config` | none | – | – |
   | `docker compose --env-file .env -f compose.yml -f compose.production.yml -f compose.proxy.yml config` | none | unless-stopped | npm: 80→80, 443→443, 127.0.0.1:81→81 |
   | `docker compose --env-file .env -f compose.yml -f compose.local.yml -f compose.production.yml config` (**pitfall**) | 127.0.0.1:8085→3000 **still there** | unless-stopped | – |
   | `docker compose --env-file .env -f compose.yml -f compose.local.yml -f compose.cors.yml config --services` | – | – | prints `db`, `app`, `tester` |

   Staging is a preview only: `docker compose --env-file .env -f compose.yml -f compose.staging.yml config --quiet`.

**Why:** `ports` lists merge, so production after local cannot remove 8085: choose **one** environment overlay. `config` prints your real `.env` values, so paste only sanitized snippets into the report.

ทำงานในโฟลเดอร์ `gacha-workshop` ที่มี `compose.yml` ถ้าใช้โฟลเดอร์เดิมจาก Lab 12 ให้เก็บ `.env` เดิมไว้ (ห้าม copy `.env.example` ทับ) ตรวจว่า `STUDENT_ID` เป็นของตนเอง และหยุด stack ของ Lab 12 ด้วย `docker compose down` (ไม่ใส่ `-v`) ถ้าเป็นโฟลเดอร์ที่เพิ่งแตกไฟล์ ให้ copy `.env.example` เป็น `.env` แล้วแก้ด้วย `notepad .env` (Windows) หรือ `nano .env` (macOS/Linux) เพื่อตั้ง `STUDENT_ID` (ใช้ค่าเดิมตลอด lab เพราะชื่อ project กำหนดชื่อ volume) ตรวจด้วย `config --quiet` เริ่ม stack ด้วย base + local แล้วดู `ps` ว่า app มีพอร์ต `127.0.0.1:8085` ส่วน db ไม่มีพอร์ตบนโฮสต์ เปิด `/test` ทำ Health → Wallet → Recharge → Exchange → Draw once → Saved history แล้วจด id และ `created_at` ของ draw จากนั้นเปรียบเทียบผล `config` ของแต่ละชุดไฟล์ โดยเฉพาะกรณี local + production ที่ยังเหลือพอร์ต 8085

## 02 — Reverse proxy with local NPM / Reverse proxy ด้วย NPM ในเครื่อง

Goal: the browser talks only to NPM on port 80, and NPM forwards to `app:3000`. Do Steps 0 → 1 → 2 → 3 in order and test after each step.

### Step 0 — Start production + proxy and create the NPM admin

1. Stop the local stack **without `-v`** (keeps the database volume), then start production + proxy with the same `.env`:

   ```text
   docker compose --env-file .env -f compose.yml -f compose.local.yml down
   docker compose --env-file .env -f compose.yml -f compose.production.yml -f compose.proxy.yml up -d --build --wait
   docker compose --env-file .env -f compose.yml -f compose.production.yml -f compose.proxy.yml ps
   ```

   Expected: app `3000/tcp` and db `5432/tcp` (no host ports); npm `0.0.0.0:80->80/tcp, 0.0.0.0:443->443/tcp, 127.0.0.1:81->81/tcp` (IPv6 lines such as `[::]:80->80/tcp` are normal). `docker volume ls` shows `gacha-<ID>_pgdata`, `gacha-<ID>_npm_data`, `gacha-<ID>_npm_certs`. "port is already allocated" for 80/443? Find the program with `netstat -ano | findstr :80` (Windows) or `sudo lsof -i :80` (macOS/Linux), stop it (IIS, another web server, an old NPM stack), then `up` again.

2. Open `http://localhost/`. Expected: NPM's default "Congratulations" page (no proxy host yet).
3. Open `http://127.0.0.1:81`. Expected: "Welcome! Get started by creating your admin account." Fill **Full Name**, **Email address**, **New Password**, click **Save** (NPM 2.16 has no default `admin@example.com` / `changeme`). Screenshot: `npm-0-setup.png`.

### Step 1 — Proxy Host: `localhost` → `http://app:3000`

1. **Hosts → Proxy Hosts → Add Proxy Host**, **Details** tab:

   | Field | Value |
   | --- | --- |
   | Domain Names | type `localhost`, then press **Enter** (it becomes a chip) |
   | Scheme | `http` |
   | Forward Hostname / IP | `app` |
   | Forward Port | `3000` |
   | Access List | leave **Publicly Accessible** |

   Screenshot: `npm-1-add-proxy-host.png`.

2. **Save**. Expected: "Proxy Host has been saved"; row SOURCE `localhost`, DESTINATION `http://app:3000`, SSL `HTTP Only`, ACCESS `Public`, STATUS `Online`. Screenshot: `npm-1-list.png`.
3. Test (terminal: `curl.exe -i http://localhost/health`, macOS/Linux `curl -i http://localhost/health`):

   | Open | Expected |
   | --- | --- |
   | `http://localhost/health` | 200 `{"status":"ok","database":"connected","app":"gacha"}` |
   | `http://localhost/test` → `GET · Health + DB` | `GET http://localhost/health` HTTP 200 OK (screenshot `npm-1-test-localhost.png`) |
   | `http://localhost/api/catalog` | 200 JSON |
   | `http://localhost/visual/` | 200 |

> **Optional — try once, then set it back to `app`.** Edit Forward Hostname / IP, Save, open `http://localhost/health`. STATUS stays **Online** even when wrong: Online only means the Nginx config loaded.
>
> | Forward Hostname / IP | Result |
> | --- | --- |
> | `localhost` | **502 Bad Gateway**; error log: `localhost could not be resolved (3: Host not found)` |
> | `127.0.0.1` | **404** `{"error":{"code":404,"message":"Not Found - /health"}}`: NPM's own admin API on port 3000 inside the NPM container |
> | `app` | 200 from the gacha app (Docker DNS on the shared network) |
>
> `localhost` inside NPM is never your app. Error log (the `*` matches the host number); optional screenshot `npm-1-wrong-localhost.png`:
>
> ```text
> docker compose --env-file .env -f compose.yml -f compose.production.yml -f compose.proxy.yml exec npm sh -c 'tail -n 5 /data/logs/proxy-host-*_error.log'
> ```

### Step 2 — Custom Location `/backend/`

1. Row **⋮ → Edit** → **Custom Locations** → **Add Location**:

   | Field | Value |
   | --- | --- |
   | Location | `/backend/` (slash at both ends) |
   | Scheme | `http` |
   | Forward Hostname / IP | `app` |
   | Forward Port | `3000` (the default is 80, so change it) |

2. Click the **gear** directly right of the Location field (not the gear at the dialog's top-right). In the dark editor type only this line (no `location` block, no `proxy_pass`):

   ```nginx
   rewrite ^/backend/(.*)$ /$1 break;
   ```

3. **Save**. Screenshot: `npm-2-custom-location.png`. NPM generates `location /backend/ { rewrite …; proxy_set_header …; proxy_pass http://app:3000; }`.
4. Test each URL and record what you see (needed in the report):

   | Open | Expected |
   | --- | --- |
   | `http://localhost/backend/test` → `GET · Health + DB` | 200 tester; `GET http://localhost/backend/health` → 200 OK (screenshot `npm-2-test-backend.png`); other buttons call `http://localhost/backend/api/...`, e.g. `POST http://localhost/backend/api/recharge` → 201 |
   | `http://localhost/backend/health` | 200 health JSON |
   | `http://localhost/backend/api/catalog` | 200 |
   | `http://localhost/backend/visual/` | 200 |
   | `http://localhost/backend` | **301** → `Location: http://localhost/backend/` (screenshot `npm-2-backend-redirect.png`; terminal `curl.exe -i http://localhost/backend`) |
   | `http://localhost/backend/` | 200 `{"app":"Gacha Workshop","test":"./test","visual":"./visual/","currency":"virtual demo only"}` |
   | `http://localhost/backendX` | 404 `{"error":"Route not found."}`: not matched by `/backend/`, so `location /` sent `/backendX` to the app |
   | `http://localhost/test` | still 200 (`location /` from Step 1) |

5. Read your 01 draw through the proxy before drawing again: `http://localhost/backend/api/accounts/<ID>/history`. Expected: the 01 draw `id` and `created_at` (same project, same `pgdata` volume).

**`/backend/` versus `/backend`** (all rows tested on NPM 2.16):

| Location | Forward Hostname | Gear (advanced) | `/backend/test` | `/backend` | `/backendX`, `/backend-admin` |
| --- | --- | --- | --- | --- | --- |
| `/backend/` | `app` | rewrite | 200 | 301 → `/backend/` | not captured (they go to `location /`) |
| `/backend` (no slash) | `app` | rewrite | 200 | **404** Route not found (the app received `/backend`; no redirect) | **captured** by this location, sent unchanged → 404 |
| `/backend/` | `app` | empty | **404** Route not found (the app received `/backend/test`) | 301 | – |
| `/backend/` | `app/` | empty | 200 (NPM writes `proxy_pass http://app:3000/;`, which replaces the prefix) | 301 | – |

Rule: use `/backend/` + the rewrite, or Forward Hostname `app/` with an empty gear field. In plain Nginx, `proxy_pass http://app:3000/;` replaces the matched prefix; `proxy_pass http://app:3000;` passes the path unchanged.

### Step 3 — A custom domain: `gacha.test`

**On this laptop:**

1. Add one line to the hosts file (keep existing lines): `127.0.0.1 gacha.test`
   - Windows: **Notepad as Administrator**, open `C:\Windows\System32\drivers\etc\hosts` (file filter: All files), add, save.
   - macOS/Linux: `sudo nano /etc/hosts`, add, Ctrl+O, Enter, Ctrl+X.
2. **Before** changing NPM: `curl.exe -i http://gacha.test/backend/test`. Expected: `HTTP/1.1 404 Not Found`, `Server: openresty`. The name reaches NPM, but no proxy host lists `gacha.test`: the **Host header** decides which proxy host answers.
3. **⋮ → Edit → Details → Domain Names**: type `gacha.test`, **Enter** (chips `localhost` and `gacha.test`), **Save**. Screenshot: `npm-3-domain-gacha-test.png`. NPM writes `server_name gacha.test localhost;`.
4. Test (type the full `http://gacha.test/...`, otherwise the browser may search; `curl.exe -v http://gacha.test/backend/health` shows `Trying 127.0.0.1:80`):

   | Open | Expected |
   | --- | --- |
   | `http://gacha.test/backend/health` | 200 |
   | `http://gacha.test/backend/test` → `GET · Health + DB` | `GET http://gacha.test/backend/health` HTTP 200 OK (screenshot `npm-3-test-gacha.png`) |
   | `http://gacha.test/backend` | 301 → `/backend/` |
   | `http://gacha.test/test` | 200 |

**On a server — what changes** (04 uses the middle column):

| | This laptop | Ubuntu VM in class | Public VPS |
| --- | --- | --- | --- |
| Name → IP | laptop hosts file: `127.0.0.1 gacha.test` | **laptop** hosts file: `192.168.1.50 gacha.test` (your VM IP); no hosts change on the VM | real domain + DNS A/AAAA record → server public IP; no hosts file |
| NPM admin | `http://127.0.0.1:81` | SSH tunnel `ssh -L 8181:127.0.0.1:81 user@SERVER`, then `http://localhost:8181` | the same SSH tunnel |
| HTTPS | none (`.test`) | none in class | SSL tab → "Request a new Certificate" (Let's Encrypt) + Force SSL; the domain must already resolve to the server and port 80 must reach NPM (screenshot `npm-4-ssl-request.png`) |
| Network / firewall | – | bridged: the VM's LAN address; NAT: forward host ports to guest SSH/HTTP | open 80/443 (and your SSH port) only; never publish 3000, 5432 or 81 |
| Page origin through the proxy | `http://gacha.test` | `http://gacha.test` | `https://your-domain`; a page on another origin must be listed in `CORS_ORIGINS` with its exact `https://` origin |

`.test` is reserved for testing (RFC 2606): keep SSL at "None" and do not save "Request a new Certificate" for `gacha.test`. Request path for the report: `Laptop browser → NPM :80 (Host gacha.test, /backend/) → app:3000 (/test) → db:5432`. **Production note:** NPM teaches routing quickly; for real production this course recommends reviewed, version-controlled Nginx configuration or a managed platform, plus application authentication and operational controls.

หยุด local โดยไม่ใส่ `-v` แล้วเริ่ม production + proxy ด้วย `.env` เดิม สร้างบัญชี admin ของ NPM ที่ `http://127.0.0.1:81` จากนั้น Step 1 สร้าง Proxy Host `localhost` → `http`, `app`, `3000` แล้วทดสอบ `http://localhost/test` (ทดลองเสริม ไม่บังคับ: ถ้าใส่ `localhost` จะได้ 502 เพราะ resolver ของ NPM แปลงชื่อนี้ไม่ได้ และ `127.0.0.1` จะได้ 404 จาก API admin ของ NPM เอง ทั้งที่สถานะยังเป็น Online ไม่ว่าแบบใด `localhost` ภายใน NPM ไม่ใช่แอปของเรา ให้ใช้ `app:3000`) Step 2 กดปุ่มเฟืองที่อยู่ขวาของช่อง Location (ไม่ใช่เฟืองมุมขวาบนของหน้าต่าง) เพิ่ม Custom Location `/backend/` พร้อม rewrite ทดสอบ URL ในตาราง และสังเกตว่า `/backend` ได้ 301 ไป `/backend/` ถ้าตั้ง Location เป็น `/backend` (ไม่มี / ท้าย) `/backend/test` ยังใช้ได้ แต่การเปิด `/backend` จะได้ 404 และ location นี้จะจับ `/backendX` ไปด้วย Step 3 เพิ่ม `127.0.0.1 gacha.test` ในไฟล์ hosts ทดสอบก่อนว่าได้ 404 ของ NPM (Host header ยังไม่ตรง) แล้วเพิ่ม `gacha.test` ใน Domain Names บนเซิร์ฟเวอร์จริงให้ใช้ DNS, SSH tunnel สำหรับ admin และขอ certificate ในแท็บ SSL

## 03 — CORS experiment with Docker Compose / ทดลอง CORS ด้วย Docker Compose

An **origin = scheme + host + port** (e.g. `http://localhost:5500`). The browser enforces CORS; the API decides by sending `Access-Control-Allow-Origin`. curl is not a browser, so it is never blocked.

### Step 0 — Start local + the CORS overlay

`compose.cors.yml` adds service `tester` (`node:24-bookworm-slim` running `node serve.js 5500`, `./visual-tester` mounted read-only), which serves the visual tester from a **second origin**, `http://localhost:5500`.

1. Free port 5500: stop VS Code Live Server ("Go Live"), Node's `npm start` or `python -m http.server` in `visual-tester/`.
2. Check that `.env` has `CORS_ORIGINS=` (empty).
3. Stop the 02 stack **without `-v`**, then start local + cors:

   ```text
   docker compose --env-file .env -f compose.yml -f compose.production.yml -f compose.proxy.yml down
   docker compose --env-file .env -f compose.yml -f compose.local.yml -f compose.cors.yml up -d --build --wait
   docker compose --env-file .env -f compose.yml -f compose.local.yml -f compose.cors.yml ps
   ```

   Expected: app `127.0.0.1:8085->3000/tcp` (healthy), db `5432/tcp` (healthy), tester `127.0.0.1:5500->5500/tcp`.

### Step 1 — Same origin first

Open `http://localhost:8085/visual/` → **Connect · GET /health + /api/catalog**. Expected: "Same origin: this page and the API share http://localhost:8085. No CORS setting is needed." and `GET /health` 200. Screenshot: `cors-0-same-origin.png`.

### Step 2 — A second origin is blocked

1. Open `http://localhost:5500`, preset `Local direct port · localhost:8085` (API base URL `http://localhost:8085`), **Connect**. Expected: red ✕ **CORS** at the page node and the note "… put `CORS_ORIGINS=http://localhost:5500` in .env, then recreate the app container (up -d, not restart)." Screenshot: `cors-1-blocked.png`.
2. **F12 → Console**. Expected:

   ```text
   Access to fetch at 'http://localhost:8085/health' from origin 'http://localhost:5500' has been blocked by CORS policy: No 'Access-Control-Allow-Origin' header is present on the requested resource.
   ```

3. Prove the server **did** answer: `curl.exe -i -H "Origin: http://localhost:5500" http://localhost:8085/health`. Expected: `HTTP/1.1 200 OK` and the health JSON, but **no** `Access-Control-Allow-Origin` line.

4. Read the app log: `docker compose --env-file .env -f compose.yml -f compose.local.yml -f compose.cors.yml logs app`. Expected: `CORS_ORIGINS = (empty: only same-origin pages such as /test and /visual/)` and, once per blocked origin, `CORS: page origin http://localhost:5500 is not in CORS_ORIGINS (empty). The browser will hide responses from that page.`

### Step 3 — Edit `.env` and try `restart` (it does not apply the change)

1. In `.env` set `CORS_ORIGINS=http://localhost:5500`.
2. Restart, then look inside the container:

   ```text
   docker compose --env-file .env -f compose.yml -f compose.local.yml -f compose.cors.yml restart app
   docker compose --env-file .env -f compose.yml -f compose.local.yml -f compose.cors.yml exec app printenv CORS_ORIGINS
   ```

   Expected: an **empty line**; curl still has no `Access-Control-Allow-Origin` and the tester still shows ✕. **Why:** `restart` reuses the existing container, whose environment was fixed at creation; `up -d` recreates it.

### Step 4 — Recreate with `up -d` (it works)

1. Recreate only the app. Expected: `http://localhost:5500`; the app log shows `CORS_ORIGINS = http://localhost:5500`.

   ```text
   docker compose --env-file .env -f compose.yml -f compose.local.yml -f compose.cors.yml up -d --wait app
   docker compose --env-file .env -f compose.yml -f compose.local.yml -f compose.cors.yml exec app printenv CORS_ORIGINS
   ```

2. Repeat the Step 2 curl. Expected: `HTTP/1.1 200 OK`, `Vary: Origin`, `Access-Control-Allow-Origin: http://localhost:5500`.
3. Reload `http://localhost:5500`, **Connect**. Expected: "Cross-origin and allowed ✓ …", all nodes green. Type **your** student ID in **Student ID**, then `POST · Recharge` 201 → `POST · Exchange` 201 → `POST · Draw once` 201 → `GET · Saved history` 200. Screenshot: `cors-2-allowed.png`.
4. A JSON `POST` first sends an `OPTIONS` **preflight**. Expected: `HTTP/1.1 204 No Content` with `Access-Control-Allow-Origin: http://localhost:5500`, `Access-Control-Allow-Methods: GET, POST, OPTIONS`, `Access-Control-Allow-Headers: Content-Type`, `Access-Control-Max-Age: 600`.

   ```text
   curl.exe -i -X OPTIONS http://localhost:8085/api/draw -H "Origin: http://localhost:5500" -H "Access-Control-Request-Method: POST" -H "Access-Control-Request-Headers: content-type"
   ```

### Step 5 — The exact-origin trap

1. Open `http://127.0.0.1:5500`, **Connect**. Expected: ✕ CORS plus "Careful: http://127.0.0.1:5500 and http://localhost:5500 are different origins." Screenshot: `cors-3-127-mismatch.png`.
2. Console: `... from origin 'http://127.0.0.1:5500' has been blocked by CORS policy ...`. App log: `CORS: page origin http://127.0.0.1:5500 is not in CORS_ORIGINS (http://localhost:5500). The browser will hide responses from that page.`
3. Fix: open `http://localhost:5500`, or list both (comma-separated, no path, no trailing slash) as `CORS_ORIGINS=http://localhost:5500,http://127.0.0.1:5500` and recreate with `up -d --wait app`. VS Code Live Server opens `http://127.0.0.1:5500` and Python's `http.server` prints `http://0.0.0.0:5500`: both differ from `http://localhost:5500`.

### Step 6 — Through the proxy: same origin, no CORS (optional inside 03)

1. Switch to production + proxy + cors (NPM keeps its proxy hosts in the `npm_data` volume):

   ```text
   docker compose --env-file .env -f compose.yml -f compose.local.yml -f compose.cors.yml down
   docker compose --env-file .env -f compose.yml -f compose.production.yml -f compose.proxy.yml -f compose.cors.yml up -d --build --wait
   ```

2. Open `http://gacha.test/backend/visual/`, **Connect**. Expected: "Same origin: this page and the API share http://gacha.test. No CORS setting is needed." With your student ID, Recharge, Exchange and Draw return 201. Screenshot: `cors-4-proxy-same-origin.png`.
3. Open `http://localhost:5500/?api=http://gacha.test/backend`, **Connect**: it works only because `CORS_ORIGINS` lists `http://localhost:5500` (still a second origin).

**Lesson:** a reverse proxy that serves the page **and** the API under one origin removes the need for CORS.

### Step 7 — CORS checklist

| Symptom | Check | Fix |
| --- | --- | --- |
| ✕ CORS, but curl shows 200 | Is the page origin in `CORS_ORIGINS`? Look for `CORS: page origin … is not in CORS_ORIGINS` in `logs app` | add the exact origin, then `up -d --wait app` |
| Still ✕ after editing `.env` | `exec app printenv CORS_ORIGINS` prints an empty line | you used `restart`; recreate with `up -d --wait app` |
| Works on `localhost:5500`, fails on `127.0.0.1:5500` | compare the address bar with `CORS_ORIGINS` | open the listed origin, or add the second origin |
| The value has a path, e.g. `http://localhost:5500/visual/` | an origin has no path | write only scheme + host + port (this app tolerates one trailing `/`) |
| An `https://` page calls an `http://` API | the browser blocks it as mixed content, not CORS | serve both over HTTPS, or use the same origin |
| `index.html` opened by double-click | the origin is `null` | serve the page from a server (the Compose `tester` service, or Node's `npm start` in `visual-tester/`) |
| `up` fails: "port is already allocated" for 5500 | Live Server or Node's `npm start` still runs on 5500 | stop Live Server / `npm start`, then `up` again |

`CORS_ORIGINS=*` allows every origin; acceptable only for this authless classroom API.

**End of 03 — stop the stack (no `-v`):**

```text
# if you did Step 6
docker compose --env-file .env -f compose.yml -f compose.production.yml -f compose.proxy.yml -f compose.cors.yml down
# if you skipped Step 6
docker compose --env-file .env -f compose.yml -f compose.local.yml -f compose.cors.yml down
```

origin = scheme + host + port เบราว์เซอร์เป็นผู้บังคับใช้ CORS ส่วน API เป็นผู้ตัดสินด้วย `Access-Control-Allow-Origin` และ curl ไม่ใช่เบราว์เซอร์จึงไม่ถูกบล็อก ก่อน Step 0 ให้หยุดโปรแกรมที่ใช้พอร์ต 5500 อยู่ (Live Server หรือ `npm start` ของ Node) แล้วเริ่ม local + `compose.cors.yml` ซึ่งเพิ่ม service `tester` ที่ `http://localhost:5500` (origin ที่สอง) Step 1 เปิด `/visual/` ของแอปเอง (origin เดียวกัน ไม่ต้องตั้ง CORS) Step 2 เปิด tester ที่ `:5500` จะเห็น ✕ CORS แต่ curl ได้ 200 แสดงว่าเซิร์ฟเวอร์ตอบแล้ว เพียงไม่ส่ง `Access-Control-Allow-Origin` และ log ของ app บอก origin ที่ถูกบล็อก Step 3 ใส่ `CORS_ORIGINS=http://localhost:5500` แล้วลอง `restart` — `printenv CORS_ORIGINS` จะยังว่าง เพราะ restart แค่เริ่ม container เดิมใหม่ ซึ่ง environment ถูกกำหนดไว้ตั้งแต่ตอนสร้าง Step 4 ใช้ `up -d --wait app` ซึ่งเทียบค่าตั้งใหม่แล้วสร้าง container ใหม่ จึงผ่าน พิมพ์รหัสนักศึกษาของตนเองในช่อง Student ID ก่อน recharge/exchange/draw และ preflight ได้ 204 Step 5 `127.0.0.1:5500` กับ `localhost:5500` เป็นคนละ origin ถ้าต้องการทั้งสองให้ใส่ `CORS_ORIGINS=http://localhost:5500,http://127.0.0.1:5500` (คั่นด้วย comma ไม่มี path และไม่มี / ท้าย) Step 6 ผ่าน proxy หน้าเว็บกับ API อยู่ origin เดียวกัน (`http://gacha.test`) จึงไม่ต้องใช้ CORS เมื่อจบ 03 ให้ `down` ด้วยรายการ `-f` เดียวกับที่ใช้อยู่ (ไม่ใส่ `-v`)

## 04 — Ubuntu VM as the server / ใช้ Ubuntu VM เป็นเซิร์ฟเวอร์

Goal: run the same production + proxy files on a second Docker host and reach it from the laptop like a server (02 Step 3, "On a server", middle column). Use an Ubuntu VM with a sudo-capable account and Docker Engine (start with 2 vCPU, 4 GB RAM, 25 GB free disk). This is the VPS model; Docker-in-Docker is not required.

1. **Identify the guest** (Ubuntu terminal). Expected: guest info, free memory/disk, the guest address (e.g. `192.168.1.50` bridged), docker `active (running)`, a Compose version. Bridged gives the VM a LAN address; NAT needs host-to-guest port forwarding and is not a public server.

   ```text
   hostnamectl
   free -h
   df -h
   ip -br address
   sudo systemctl status docker --no-pager
   sudo docker compose version
   ```

2. **Connect from the laptop with SSH:** `ssh student@192.168.1.50` (your actual address; NAT example when host port 2222 forwards to guest 22: `ssh -p 2222 student@127.0.0.1`). Expected: a VM shell prompt; practise `pwd`, `ls -la`, `cd`, `mkdir -p`, `cp`, `nano`.

3. **Copy the same workshop** and create the VM's own `.env`. Expected: `~/apps/gacha-workshop` with `compose.yml` and `.env`. Copy source and configuration only, never the laptop's database files.

   ```text
   # Ubuntu VM
   mkdir -p ~/apps
   # Laptop
   scp gacha-workshop.zip student@192.168.1.50:~/apps/
   # Ubuntu VM
   sudo apt install unzip
   cd ~/apps
   unzip gacha-workshop.zip
   cd gacha-workshop
   cp .env.example .env
   nano .env
   ```

4. **Start production + proxy on the VM.** Expected: the same ports as 02 Step 0.

   ```text
   sudo docker compose --env-file .env -f compose.yml -f compose.production.yml -f compose.proxy.yml up -d --build --wait
   sudo docker compose --env-file .env -f compose.yml -f compose.production.yml -f compose.proxy.yml ps
   sudo docker compose --env-file .env -f compose.yml -f compose.production.yml -f compose.proxy.yml logs --tail 30 app db npm
   ```

5. **Open NPM admin through an SSH tunnel** (laptop; keep it open): `ssh -L 8181:127.0.0.1:81 student@192.168.1.50`, then `http://localhost:8181`. Create the VM's NPM admin (new `npm_data` volume) and repeat 02 Steps 1–3: Proxy Host with Domain Names `localhost` and `gacha.test` → `http`, `app`, `3000`, plus Custom Location `/backend/` with the rewrite. Keeping `localhost` lets `curl http://localhost/backend/health` work inside the VM.
6. **Point the laptop's name at the VM.** In the **laptop** hosts file change the line to `VM_IP gacha.test`, e.g. `192.168.1.50 gacha.test` (keep only one `gacha.test` line; NAT users use their forwarded HTTP port). Open `http://gacha.test/backend/test` and run Health → Recharge → Exchange → Draw once → Saved history. Request path: `Laptop browser → VM :80 → NPM → app:3000 → db:5432`.
7. **Prove VM persistence.** Create a VM draw (note `id`, `created_at`), record the app container ID, recreate the app, then show the new ID:

   ```text
   sudo docker compose --env-file .env -f compose.yml -f compose.production.yml -f compose.proxy.yml ps -q app
   sudo docker compose --env-file .env -f compose.yml -f compose.production.yml -f compose.proxy.yml up -d --force-recreate --wait app
   sudo docker compose --env-file .env -f compose.yml -f compose.production.yml -f compose.proxy.yml ps -q app
   ```

   Expected: a different container ID, the same `gacha-<ID>_pgdata` volume (`sudo docker volume ls`), and the same draw at `http://gacha.test/backend/api/accounts/<ID>/history`. Laptop draws are **not** expected on the VM (new host, new storage).

8. **Explain the public-VPS step** (perform only on a server assigned to you): real domain + DNS A/AAAA, provider firewall, ports 80/443 only, kept SSH access, Let's Encrypt from NPM's SSL tab (02 Step 3). Allow the SSH port before enabling UFW:

   ```text
   sudo ufw allow OpenSSH
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   sudo ufw enable
   sudo ufw status
   ```

   Docker-published ports can bypass UFW, so keep app, DB and admin ports unpublished or loopback-only.

ใช้ Ubuntu VM เป็นเซิร์ฟเวอร์ (โมเดล VPS) ตรวจข้อมูล guest, IP และสถานะ Docker เชื่อมต่อด้วย SSH คัดลอก `gacha-workshop.zip` เข้า VM แล้วสร้าง `.env` ใหม่ เริ่ม production + proxy ด้วยคำสั่งเดิม เปิด admin ของ NPM ผ่าน SSH tunnel (`http://localhost:8181`) ทำ 02 Step 1–3 ซ้ำใน NPM ของ VM โดยตั้ง Proxy Host ที่มี Domain Names `localhost` และ `gacha.test` → `http`, `app`, `3000` พร้อม Custom Location `/backend/` แล้วแก้ไฟล์ hosts บน **แล็ปท็อป** เป็น `VM_IP gacha.test` (bridged) ทดสอบ `/backend/test` สร้าง draw บน VM จด app container ID แล้วรัน `up -d --force-recreate --wait app` แสดง container ID ใหม่และ draw เดิมเพื่อพิสูจน์ว่าข้อมูลยังอยู่ ข้อมูลจากแล็ปท็อปไม่ได้ย้ายมาเอง และอธิบาย DNS, firewall และ HTTPS สำหรับ VPS สาธารณะ

## Optional, not submitted / เสริม ไม่ต้องส่ง

- **Another backend:** adapt another Lab 11/12 backend to the same override + proxy pattern (practice only, no report).
- Railway/Render/Vercel hosting moved to Lab 14 · CI/CD (platform deploy); it is not part of Lab 13.

นำแบ็กเอนด์อื่นจาก Lab 11/12 มาปรับใช้กับรูปแบบ override + proxy เดียวกันได้เป็นแบบฝึกเสริม ส่วน Railway/Render/Vercel ย้ายไปอยู่ใน Lab 14 · CI/CD (platform deploy) ไม่ใช่ส่วนของ Lab 13

## In-room check and report / ตรวจในห้องและรายงาน

- Complete required parts **01–04** and show your actual running experiment to the **LA in the room before leaving**.
- Use your own screen, CLI and API results:
  - **01:** sanitized `config` output that shows the override/overlay merge, `ps`, and the `/test` draw `id` + `created_at`.
  - **02:** four screenshots of your own NPM: Step 1 form (Details), the Proxy Hosts list (Online), Step 2 Custom Location and Step 3 Domain Names; browser results for `http://localhost/test`, `http://localhost/backend/test` and `http://gacha.test/backend/test`; the `/backend` versus `/backend/` URL table you observed; a request-path diagram; the original 01 draw read through the proxy.
  - **03:** the CORS evidence table (blocked, `restart`, `up -d`, allowed + preflight 204, `127.0.0.1` trap) and one sentence on why the proxy's same origin needs no CORS.
  - **04:** VM networking, SSH tunnel, `/backend/test` through the VM, and the draw that survives app replacement.
- Include one problem, its diagnosis and fix (or a preventive check), plus your repository URL and sanitized relevant snippets.
- Complete the web self-quiz (Compose, override files, the NPM reverse proxy, the `/backend/` path, common pitfalls) and review its feedback; the optional Ubuntu VM quiz is at `ubuntu-quiz.html`. Both are practice; Moodle assessment instructions remain separate.
- Submit **one `student_ID_lab13.PDF`** to **MyCourse**, replacing `student_ID` with your actual ID. Follow the opening/deadline shown there. Use the report template and check that the PDF is readable after upload.

ทำ 01–04 แล้วแสดงงานจริงให้ LA ตรวจในห้องก่อนออก ใช้ภาพหน้าจอ ผลคำสั่ง และผล API ของตนเอง: 01 ผล `config` ที่ปิดข้อมูลลับซึ่งเห็นการ merge ของ override/overlay, `ps` และ `id` + `created_at` ของ draw จาก `/test`; 02 ภาพหน้าจอ NPM ของตนเองสี่ภาพ ได้แก่ ฟอร์ม Step 1 (Details), รายการ Proxy Hosts (Online), Step 2 (Custom Location) และ Step 3 (Domain Names), ผลใน browser ของ `http://localhost/test`, `http://localhost/backend/test` และ `http://gacha.test/backend/test`, ตาราง `/backend` กับ `/backend/` ที่สังเกตได้, แผนภาพเส้นทางคำขอ (request path) และ draw เดิมจาก 01 ที่อ่านผ่าน proxy; 03 ตารางหลักฐาน CORS (ถูกบล็อก, `restart`, `up -d`, อนุญาตแล้ว + preflight 204, กับดัก `127.0.0.1`) และหนึ่งประโยคอธิบายว่าทำไม same origin ผ่าน proxy จึงไม่ต้องใช้ CORS; 04 เครือข่าย VM, SSH tunnel, `/backend/test` ผ่าน VM และ draw ที่ยังอยู่หลังสร้าง app container ใหม่ ใส่ปัญหาหนึ่งเรื่องพร้อมการวิเคราะห์และวิธีแก้ (หรือการตรวจป้องกัน) URL ของ repository และ snippet ที่ปิดข้อมูลลับแล้ว ทำ self-quiz หลังเวิร์กช็อปและทบทวน feedback (self-quiz หลักครอบคลุม Compose, ไฟล์ override, reverse proxy ด้วย NPM, path `/backend/` และกับดักที่พบบ่อย ส่วน quiz Ubuntu VM แยกต่างหากเป็นแบบเสริมที่ `ubuntu-quiz.html` ทั้งสองเป็นแบบฝึก ส่วนการประเมินใน Moodle แยกต่างหาก) แล้วส่ง **student_ID_lab13.PDF ไฟล์เดียวใน MyCourse** ตามกำหนดใน MyCourse โดยใช้รหัสนักศึกษาจริง ใช้ report template และตรวจว่าไฟล์อ่านได้หลังอัปโหลด
