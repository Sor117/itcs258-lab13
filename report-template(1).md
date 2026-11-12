# Lab 13 — Deployment Experiment Report / รายงานทดลอง deployment

**Dr. Pisit Praiwattana, your mentor in 2026**

Student ID / รหัสนักศึกษา:

Name / ชื่อ:

Laptop OS, VM OS and Docker versions / OS แล็ปท็อป, OS ของ VM และรุ่น Docker:

Repository URL / URL repository:

Use **one gacha project** for required experiments **01–04**. Explain in English or Thai. Every screenshot must come from your own actual screen, and passwords/tokens must be hidden. Railway/Render/Vercel hosting moved to Lab 14 · CI/CD (platform deploy); it is not part of Lab 13 or this report.

ใช้ **gacha โปรเจกต์เดียว** ทำงานหลัก **01–04** อธิบายภาษาอังกฤษหรือไทยได้ ภาพต้องมาจากหน้าจอที่รันจริงของตนเอง และปิดรหัสผ่าน/token การ host บน Railway/Render/Vercel ย้ายไปอยู่ใน Lab 14 · CI/CD (platform deploy) ไม่ใช่ส่วนของ Lab 13 และไม่ต้องใส่ในรายงานนี้

## 01 — Compose override + direct port / Compose override และพอร์ตตรง

- Show the complete `-f` command you used and sanitized `config` output that shows the merge (the app `ports:` block added by the local overlay).
- Show `config --quiet` (no output), `ps` (app `127.0.0.1:8085->3000/tcp`, db with no host port) and `http://localhost:8085/test`.
- Show your own recharge, exchange, draw and saved-history results.
- Fill the merge table from your own `config` runs (01 step 6).

| Command (shortened) | app ports you saw | restart you saw |
| --- | --- | --- |
| `docker compose config` | | |
| `docker compose -f compose.yml config` | | |
| `... -f compose.yml -f compose.production.yml -f compose.proxy.yml config` | | |
| `... -f compose.yml -f compose.local.yml -f compose.production.yml config` | | |

Original local draw ID, result and created_at / ID ผล และเวลาสร้างของ draw ในเครื่อง:

Why is `compose.override.yml` not used when you pass `-f`? / เหตุใดจึงไม่ใช้ `compose.override.yml` เมื่อใส่ `-f`?

Why does local + production still publish 8085? / เหตุใด local + production ยัง publish พอร์ต 8085?

Evidence and explanation / หลักฐานและคำอธิบาย:

## 02 — Reverse proxy with local NPM / Reverse proxy ด้วย NPM ในเครื่อง

- Show `ps` for production + proxy: app and db without host ports; npm on 80, 443 and `127.0.0.1:81`.
- Show **four screenshots of your own** NPM: Step 1 form (Details: `localhost` → `http`, `app`, `3000`), the Proxy Hosts list (Online), Step 2 Custom Location (`/backend/` + rewrite) and Step 3 Domain Names (`localhost`, `gacha.test`).
- Show browser results for `http://localhost/test`, `http://localhost/backend/test` and `http://gacha.test/backend/test` (Health button with its request URL and status).
- Read the original 01 draw through the proxy without drawing again.
- Explain why `localhost` inside NPM is never your app (use `app:3000`), and why STATUS "Online" does not prove the upstream works.

Step test table — write what **you** observed / ตารางผลทดสอบที่ **ตนเอง** สังเกตได้:

| Step | URL | Observed status / result |
| --- | --- | --- |
| 0 | `http://localhost/` (before any proxy host) | |
| 1 | `http://localhost/health` | |
| 1 | `http://localhost/test` → Health | |
| 2 | `http://localhost/backend/test` → Health | |
| 2 | `http://localhost/backend/api/catalog` | |
| 2 | `http://localhost/backend` | |
| 2 | `http://localhost/backend/` | |
| 2 | `http://localhost/backendX` | |
| 3 | `http://gacha.test/backend/test` **before** adding `gacha.test` to Domain Names | |
| 3 | `http://gacha.test/backend/test` **after** adding it | |
| 3 | `curl.exe -v http://gacha.test/backend/health` (the `Trying …` line) | |

`/backend/` versus `/backend` — explain the 301 and the 404 in your own words / อธิบาย 301 และ 404 ด้วยคำของตนเอง:

Request path / เส้นทางคำขอ:

`Laptop browser → __________ (Host: ______, path: ______) → __________ (path: ______) → __________`

| Item | Direct local (01) | Local proxy (02) |
| --- | --- | --- |
| Browser URL | | |
| Host entry port | | |
| App service/internal port | | |
| Database volume name | | |
| Original draw ID + created_at | | |

Local versus server — what changes for `gacha.test` on a VM or a public VPS? / ในเครื่องกับบนเซิร์ฟเวอร์ต่างกันอย่างไร:

Evidence and explanation / หลักฐานและคำอธิบาย:

## 03 — CORS experiment with Docker Compose / ทดลอง CORS ด้วย Docker Compose

- Show `ps` for local + cors (app `127.0.0.1:8085`, db, tester `127.0.0.1:5500`).
- Show each stage below with your own screenshot, terminal output or log line.

| Stage | What you did | Evidence (screenshot / output) | Result |
| --- | --- | --- | --- |
| Same origin | `http://localhost:8085/visual/` → Connect | | |
| Blocked | `http://localhost:5500` → API `http://localhost:8085`, `CORS_ORIGINS` empty | tester ✕ + Console line | |
| Server still answered | `curl.exe -i -H "Origin: http://localhost:5500" http://localhost:8085/health` | status + (no) `Access-Control-Allow-Origin` | |
| App log | `docker compose ... logs app` | `CORS: page origin … is not in CORS_ORIGINS …` line | |
| `restart` | edit `.env`, `restart app`, `exec app printenv CORS_ORIGINS` | printenv output | |
| `up -d` | `up -d --wait app`, `exec app printenv CORS_ORIGINS` | printenv output + curl header | |
| Allowed | reload `http://localhost:5500` → Connect, Recharge, Draw | tester ✓ screenshot | |
| Preflight | `curl.exe -i -X OPTIONS http://localhost:8085/api/draw ...` | status + `Access-Control-Allow-*` headers | |
| `127.0.0.1` trap | `http://127.0.0.1:5500` → Connect | tester warning + app log line | |
| Through the proxy (optional) | `http://gacha.test/backend/visual/` → Connect | tester note | |

Why did `restart` not apply `CORS_ORIGINS`? / เหตุใด `restart` จึงไม่ใช้ค่า `CORS_ORIGINS` ใหม่?

Why are `http://127.0.0.1:5500` and `http://localhost:5500` different origins? / เหตุใดสองค่านี้จึงเป็นคนละ origin?

Why does the proxy make the page and the API same-origin, so no CORS is needed? (one sentence) / เหตุใด proxy ทำให้หน้าเว็บกับ API เป็น origin เดียวกันจึงไม่ต้องใช้ CORS (หนึ่งประโยค):

Evidence and explanation / หลักฐานและคำอธิบาย:

## 04 — Ubuntu VM as the server / ใช้ Ubuntu VM เป็นเซิร์ฟเวอร์

- Identify the Ubuntu guest address and whether access uses bridged networking or NAT/forwarded ports.
- Show the basic shell operations, Docker Engine service, Compose startup, status and relevant logs.
- Show SSH-tunnel access to loopback-only NPM admin and browser access to the VM's `/backend/test` route (the laptop hosts file points `gacha.test` to the VM).
- Explain that VM data storage is separate from laptop storage.
- Create a VM record, record the app container ID (`ps -q app`), recreate it with `up -d --force-recreate --wait app`, then show the new container ID and the same original VM record.
- Explain the public-VPS requirements: actual DNS, provider/host network rules, deliberate public ports, SSH access and HTTPS certificate.

VM network diagram / แผนภาพเครือข่าย VM:

| Item | Before app replacement | After app replacement |
| --- | --- | --- |
| App container ID | | |
| DB volume identity | | |
| Original VM draw ID + created_at | | |

Evidence and explanation / หลักฐานและคำอธิบาย:

## Diagnosis and reflection / วิเคราะห์ปัญหาและสะท้อนผล

Symptom → hypothesis → check → fix / อาการ → สมมติฐาน → การตรวจ → วิธีแก้:

Why does production publish no app or database ports, and what does the reverse proxy do instead? / เหตุใด production จึงไม่ publish พอร์ต app และฐานข้อมูล และ reverse proxy ทำหน้าที่อะไรแทน?

How did NPM decide which proxy host and which location answered `http://gacha.test/backend/test`? / NPM เลือก Proxy Host และ location สำหรับ URL นี้อย่างไร?

What changed between your laptop and the Ubuntu VM, and what operational work still belongs to the developer? / สิ่งใดเปลี่ยนระหว่างแล็ปท็อปกับ Ubuntu VM และผู้พัฒนายังต้องดูแลงานระบบอะไร?

Self-quiz topic to revisit / หัวข้อจาก self-quiz ที่ต้องทบทวน:

> The main self-quiz covers Compose, override files, the NPM reverse proxy, the `/backend/` path and common pitfalls. An optional, separate Ubuntu VM quiz is at `ubuntu-quiz.html`.
>
> Self-quiz หลักครอบคลุม Compose, ไฟล์ override, reverse proxy ด้วย NPM, path `/backend/` และกับดักที่พบบ่อย ส่วน quiz Ubuntu VM แยกต่างหากเป็นแบบเสริมที่ `ubuntu-quiz.html`

## In-room check and final submission / ตรวจในห้องและส่งงาน

- [ ] I completed 01–04 using the same working example.
- [ ] I demonstrated my actual experiment to the LA in the room.
- [ ] All evidence is from my own screen and readable.
- [ ] My report includes the merge evidence, my four NPM screenshots, the URL test tables, the CORS evidence table, request paths, persistence comparisons and repository URL.
- [ ] No actual passwords or tokens are visible.
- [ ] The single PDF is named **`student_ID_lab13.PDF`**, using my actual ID.
- [ ] I uploaded it to MyCourse by its deadline and opened the uploaded PDF to verify it.

Optional extension: another backend may be described here, but it is not required.

แบบฝึกเสริม: อธิบายแบ็กเอนด์อื่นเพิ่มเติมได้ แต่ไม่ใช่งานบังคับ
