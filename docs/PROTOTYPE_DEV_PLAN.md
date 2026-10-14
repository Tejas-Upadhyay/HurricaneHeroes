# Shelter Mesh — Autonomous Off-Grid Shelter Coordination Network

Development blueprint for the Hurricane Heroes hardware prototype: a LoRa mesh network that
keeps shelters connected to the County EOC when cell towers and broadband go down.

Companion to the web platform at https://southwestfloridahurricaneheroes.com

**Status:** Planning complete. Hardware on order. Build starts once boards arrive (see §11
Getting Started).

---

## 1. The Problem

During major Southwest Florida hurricane landfalls, cellular towers and broadband internet
frequently fail from power loss, storm surge, and structural damage. Emergency shelters become
data silos — unable to report supply shortages (potable water, medical supplies, fuel) or
census counts to the County Emergency Operations Center (EOC), exactly when that information
matters most.

## 2. The Solution

An autonomous, zero-infrastructure communications bridge that pairs long-range radio telemetry
with an app-free local interface:

- **LoRa 915 MHz backhaul** — self-contained microcontroller nodes form an ad-hoc, multi-hop
  mesh, relaying data up to 3–10 miles per hop (terrain dependent) with no towers, satellite
  subscriptions, or commercial power.
- **Zero-app local access** — each node broadcasts a local offline Wi-Fi access point. Shelter
  staff and volunteers connect with any smartphone or laptop browser to submit status, medical
  requests, and inventory requisitions.
- **Automatic multi-hop relaying** — packets route between shelters and relay stations across
  the county, updating an emergency dashboard even during a full telecom blackout.

### Key advantages

- **No recurring cost** — operates on the license-free 915 MHz ISM band.
- **Ultra-low power** — days of runtime on a 5V USB battery pack or small solar charger.
- **Frictionless** — no app downloads, logins, or data plans required of on-site volunteers.
- **Scalable** — low per-facility hardware cost, enabling a county-wide rollout across dozens
  of shelters.

> Note on range: 3–10 miles per hop is best-case and depends on antenna gain, height, terrain,
> and line-of-sight. Field testing (Phase 4) establishes real numbers for our area.

---

## 3. System Architecture

```
[Blackout Shelter Zone]
   Volunteer Smartphone
      | (connects to offline Wi-Fi: "ShelterNet-01" captive portal)
      v
   Node A: LoRa32 V3 (Field Node)
      | (transforms web-form input into a compact 32-byte binary payload)
      v  (915 MHz LoRa radio — up to 3-10 miles)
   Node B: LoRa32 V3 (Intermediate Mesh Relay / Hop)
      v  (915 MHz LoRa radio — up to 3-10 miles)
[County EOC / Emergency Gateway]
   Node C: LoRa32 V3 (Gateway Node)
      | (USB serial bridge -> MQTT)
      v
   AWS Cloud Pipeline (built with Kiro)
      +- AWS IoT Core        (secure MQTT ingestion)
      +- AWS Lambda          (de-duplication, CRC check & decoding)
      +- Amazon DynamoDB     (real-time shelter state store)
      +- S3 + CloudFront     (web dashboard for emergency coordinators)
```

---

## 4. Hardware — Bill of Materials & Purchasing

### 4.1 Core requirement

The project needs **3 complete, all-in-one boards** — each with an ESP32-S3 processor, Wi-Fi,
the SX1262 radio, USB-C, and an OLED screen on a single board. That is the only device type
that can run the shelter Wi-Fi hotspot, the web intake form, and the mesh firmware on its own.
Buy **identical boards** for all 3 nodes (all V3) to keep firmware and pin config simple.

### 4.2 Bill of Materials

| Component | Qty | Purpose | Notes |
|---|---|---|---|
| DIYmall LoRa32 V3 (ESP32-S3 + SX1262, 915 MHz, OLED) | 3 | Microcontroller + LoRa transceiver | Node A = field shelter, Node B = hop relay, Node C = gateway. |
| 5 dBi 915 MHz antenna | 3 | Radio link | Included with the DIYmall boards. |
| USB-C data cables | 2–3 | Flashing firmware + serial bridge + power | **Must be data-capable (4-wire), not charge-only.** Needed now. |
| 5V USB power banks (10,000 mAh) | up to 3 | Portable off-grid power | Only for Phase 4 field testing. May already own one. |
| Solar panel (5V/6V, 5–10 W) | optional | "Runs on solar" demo | Later stages only (see §4.6). |
| IP65/IP66 project box + bulkhead SMA | optional | Outdoor weatherproofing | Real outdoor pilot only (see §4.6). |

### 4.3 Purchasing decision (FINAL)

**Buy now — main project:**

| ASIN | Product | Decision |
|---|---|---|
| B0CY1XKZQC | DIYmall 2-pack LoRa32 V3, ESP32-S3 + SX1262, 5 dBi antennas, OLED | **CHOSEN.** Blank boards → all firmware written by the student = 100% original work (important for science fair / Congressional App Challenge / patent). Best value at ~$48 for a 2-pack (~$24/board). |

**Buy now — side research (separate from main project):**

| ASIN | Product | Purpose |
|---|---|---|
| B0G4418815 | Waveshare Core1262 — bare SX1262 radio modules (2-pack) | Son's independent learning track: raw radio, SPI wiring, antenna behavior. NOT part of the main deliverable. See §4.7. |

**Considered but not chosen (on record):**

| ASIN | Product | Why not |
|---|---|---|
| B0CW6151WJ | Heltec V3 2-pack w/ OLED ~$44.98 | Equivalent to DIYmall, ~$3 cheaper. Acceptable alternative. |
| B0G9PLH9C9 | Meshnology 2-pack, 28dBm, w/ batteries + cases | Ships pre-flashed with Meshtastic (someone else's software) — muddies the "I built it" story. Higher power/batteries not worth that tradeoff here. |
| B0G2QPXYT4 / B0G2QPFP3P | Heltec V4 single, "Without OLED" ~$25–33 each | Dropping the OLED does NOT save money — sold as singles (~$75–99 for 3) vs. the 2-pack. |
| B0D3HY2KT4 / B0DPQH9BP5 | Bare radio modules ~$14–16 | Radio-only: no USB/screen/easy programming. Wrong device type for the main build. |

### 4.4 Cost-reduction notes (what actually works)

Cutting the OLED or antenna does **not** lower the price meaningfully:

- **OLED — keep it.** Removing it saves only ~$1–2, and no-OLED boards sell as singles at
  higher per-board cost. The OLED shows live TX/RX status, RSSI/SNR, and packet counts, which
  makes debugging and the Phase 4 drive test far easier (read range on the screen instead of
  tethering a laptop) and demos much better to judges/officials.
- **Antenna — keep it.** A basic 5 dBi antenna is ~$2–4; dropping it saves almost nothing and
  you'd need one anyway (never transmit bare — see §4.5).

Levers that **do** reduce cost:

- Buy a **2-pack** (the real discount) — DIYmall ~$48 or Heltec V3 2-pack ~$44.98.
- **Defer the 3rd board.** Phases 1–3 (bench, portal, cloud) all work with 2 boards. Buy the
  3rd only when ready to test a multi-hop relay (Phase 4). Defers ~$24.

### 4.5 Antennas — bundled vs. upgrade

**Keep the bundled 5 dBi antenna** — it's the indoor antenna (Phases 1–3), the "always
attached" safety antenna, and the **baseline** for Phase 4 (compare 5 dBi vs. high-gain range —
good science-fair data).

**Optional high-gain upgrade for Phase 4** (buy later, not now):

| ASIN | Product | Purpose |
|---|---|---|
| B09C5K91H7 | 915 MHz fiberglass/high-gain antenna | Biggest lever on real-world range; add when drive-testing. |
| B0FRGD4MNB | 915 MHz antenna 2-pack + IPEX extension cables | Antenna upgrade / gateway relocation. |

**How to connect an upgrade antenna:**

1. Check the board's connector — DIYmall V3 uses a small **U.FL / IPEX** socket (some variants
   add an SMA jack).
2. U.FL socket → buy a **U.FL-to-SMA pigtail** + **SMA-male** antenna. (Kits like B0FRGD4MNB
   include the pigtail.)
3. SMA jack → screw an SMA-male antenna straight on, no pigtail.
4. Swap the 5 dBi for the high-gain antenna and re-run the drive test; keep both result sets.

**Connector warning:** SMA vs. U.FL/IPEX mismatch is the most common first-build mistake —
match the chain. **Never power on to transmit with no antenna attached** — it can damage the
SX1262.

### 4.6 Power, solar & enclosure — by phase

**Power:**

- **Phases 1–3 (indoor bench):** power straight from the **computer's USB port** (a data-capable
  USB-C cable both powers and flashes/debugs the board), or any **USB wall adapter**. No battery
  purchase needed. Data cable, not charge-only.
- **Phase 4 (field/drive test):** each node needs its own **USB power bank** (any 5V USB-C bank).
  May already own one.

**Solar (later, optional — supports the "runs on solar" claim):**

- Wire it as **solar panel → USB power bank → board**, not panel straight to the board. The
  power bank buffers the panel's variable output so the node doesn't brown out on clouds and
  keeps running at night.
- A small **5V/6V, 5–10 W USB solar panel** is plenty for one node. Some "solar power banks"
  combine panel + battery in one unit — simplest for a demo.
- Honest framing: a small panel demonstrates the concept; a real multi-day deployment needs a
  properly sized panel + battery. Don't over-claim continuous operation.

**Weatherproof enclosure (only for real outdoor/multi-day placement):**

- Use an **IP65/IP66-rated project box** (sealed, gasketed).
- Mount the **antenna outside** the box via a **bulkhead SMA** + U.FL-to-SMA pigtail (a sealed
  box blocks/attenuates the radio signal — keep the antenna in open air).
- Add a sealed **grommet/gland** for the cable entry.
- Florida heat: light-colored box + shade; dark boxes bake in direct sun.
- **Timing:** not needed for Phases 1–3 (indoor) or a short Phase 4 drive test (a plastic
  container or bag keeps light rain off). Buy enclosures only for a real outdoor pilot with the
  county.

### 4.7 Two-track plan: main project vs. side research

Two parallel tracks, kept separate on purpose:

- **Main project (deliverable):** the DIYmall LoRa32 V3 boards. All firmware written and loaded
  by the student. This is what goes in the outreach emails, the demo, the science fair, and any
  patent filing. Keep its code and notes in their own workspace so the "what I built" story
  stays clean.
- **Side research (learning):** the bare Waveshare Core1262 modules (B0G4418815) + spare
  antennas. Good for learning the raw SX1262 radio, SPI wiring, and antenna behavior. Keep in a
  separate folder/notebook. Lessons here (especially antenna tuning) can feed the main nodes in
  Phase 4.

Guardrails so the side track doesn't derail the main one:

1. Get the DIYmall boards through **Phase 1 (two-board ping-pong)** first — deliverable before
   experiments.
2. Keep the two tracks in separate workspaces; don't mix experimental code into the main
   firmware.

---

## 5. Software Architecture & Implementation

### A. Binary Packet Specification (node-to-node)

To maximize radio range and minimize airtime, submissions are packed into a fixed-length C
struct rather than JSON:

```cpp
struct __attribute__((packed)) ShelterPacket {
    uint16_t messageId;    // Sequential ID to eliminate duplicate packets
    uint8_t  shelterId;    // Numeric ID (e.g., 0x01 = Estero, 0x02 = Cape Coral)
    uint8_t  urgencyLevel; // 1 = Normal, 2 = Supply Need, 3 = Medical / Critical
    uint16_t waterGallons; // Water requested (gallons)
    uint16_t mealsNeeded;  // Meals required
    uint16_t cotsNeeded;   // Cots / blankets required
    uint8_t  hopCount;     // TTL (decremented at every mesh relay; drops at 0)
    uint16_t checksum;     // CRC-16 integrity verification
};
```

### B. Field Node Firmware (ESP32-S3 + SX1262)

- **Framework:** PlatformIO with the Arduino core and RadioLib.
- **SoftAP + captive portal:** DNSServer + ESPAsyncWebServer redirect all connected mobile
  traffic to `192.168.4.1`, serving a responsive HTML form cached in LittleFS flash.
- **Mesh routing:** nodes listen in continuous receive mode (`startReceive()`). On each
  incoming frame the node:
  1. Verifies the CRC-16 checksum.
  2. Checks a local ring-buffer to confirm it hasn't seen this `messageId` in the last ~10
     minutes (de-duplication).
  3. Decrements `hopCount`.
  4. Waits a short randomized jitter (50–200 ms) to avoid collisions.
  5. Retransmits if `hopCount > 0`.
- **OLED status:** the built-in 0.96" OLED shows TX/RX status, last packet, and RSSI/SNR.

### C. Gateway Serial Bridge (Python)

A lightweight script on the gateway host at the EOC:

1. Reads raw bytes from the serial interface (`COMx` on Windows, `/dev/ttyUSB0` on Linux).
2. Validates frame structure and unescapes binary fields.
3. Decodes the payload into JSON.
4. Publishes to AWS IoT Core topic `shelters/southwest-fl/telemetry` using mutual TLS (X.509
   device certificates).

### D. AWS Cloud Pipeline

- **AWS IoT Core** — MQTT authentication, device shadows, and an ingestion rule on
  `shelters/+/telemetry`.
- **AWS Lambda (`ProcessShelterTelemetry`)** — verifies CRC, filters duplicate `messageId`s
  arriving via multiple mesh hops, decodes, and writes state to DynamoDB. Dead-letter queue for
  failures.
- **Amazon DynamoDB (`ShelterState`)** — partition key `shelterId`, sort key `timestamp`;
  attributes for inventory, bed/cot counts, last-ping timestamp, and active alerts.
- **S3 + CloudFront** — a React dashboard showing a real-time supply heat map, integrated with
  southwestfloridahurricaneheroes.com.

---

## 6. Building It in Kiro (AWS Spec-Driven IDE)

### Step 1 — Steering file

Create `.kiro/steering/disaster-mesh.md`:

```markdown
# Disaster Relief Communications Project
- Cloud Provider: AWS (Region: us-east-1)
- Infrastructure-as-Code: AWS CDK (TypeScript)
- Ingestion: AWS IoT Core MQTT -> AWS Lambda -> Amazon DynamoDB
- Target Hardware: ESP32-S3 with SX1262 (DIYmall / Heltec LoRa32 V3)
- Firmware: PlatformIO (RadioLib, Arduino framework, LittleFS)
- Security: TLS 1.2+ for IoT Core; IAM least privilege
```

### Step 2 — Cloud generation prompt

> Generate an AWS CDK (TypeScript) stack for an emergency shelter monitoring pipeline. Include:
> 1. An AWS IoT Core rule listening to MQTT topic `shelters/+/telemetry`.
> 2. A TypeScript Lambda function that decodes telemetry, validates message uniqueness, and
>    writes shelter status to DynamoDB (with dead-letter queue support).
> 3. A DynamoDB table named `ShelterState` with partition key `shelterId` and sort key
>    `timestamp`, on-demand capacity.
> 4. All IAM roles adhering to least-privilege permissions.

### Step 3 — Firmware generation prompt

> Generate a PlatformIO project for the DIYmall / Heltec WiFi LoRa 32 V3 (ESP32-S3 + SX1262).
> Write firmware that:
> 1. Configures a SoftAP Wi-Fi network and a DNS captive portal.
> 2. Serves a responsive HTML/CSS form for shelter requisitions (water, food, medical status).
> 3. Serializes submissions into a 32-byte struct and transmits over 915 MHz LoRa via RadioLib.
> 4. Displays packet transmission status on the built-in 0.96-inch OLED screen.

### Step 4 — Deploy & test end-to-end

1. Run `cdk deploy` from Kiro's terminal to provision the cloud infrastructure.
2. Flash two boards with node firmware and one with gateway firmware via PlatformIO.
3. Submit a test form from a phone connected to Node A's Wi-Fi.
4. Verify the packet relays through Node B, prints on Node C's serial monitor, triggers the
   Lambda, and updates DynamoDB in real time.

---

## 7. Execution Roadmap

| Phase | Timeline | Goal | Deliverables |
|---|---|---|---|
| 1. Bench validation | Days 1–7 | Prove basic radio link | Flash two boards with a 915 MHz ping-pong sketch; confirm TX/RX across two rooms with antennas attached. |
| 2. Local portal integration | Days 8–14 | App-free intake | Implement the captive portal + LittleFS web form; connect a phone, submit a test form, confirm the node broadcasts the binary packet — no internet. |
| 3. AWS cloud pipeline | Days 15–21 | End-to-end ingestion | Deploy CDK stack via Kiro; connect the gateway over USB; confirm LoRa packets trigger Lambda and populate DynamoDB. |
| 4. Field testing & data | Days 22–30 | Real-world metrics | Buy 3rd board + power banks; 1–3 mile drive test across Lee County; log Packet Success Rate (PSR), SNR, and RSSI. Optionally test high-gain antenna. |
| 5. Competition & IP | Ongoing | Recognition + protection | Submit prototype + video to the Congressional App Challenge and a local ISEF-affiliated regional science fair; file a USPTO Provisional Patent Application (Micro-Entity) for 12 months of "Patent Pending" priority. |

---

## 8. Metrics to Capture (Phase 4)

- **PSR (Packet Success Rate):** delivered packets / sent packets, per distance.
- **RSSI:** received signal strength, per hop.
- **SNR:** signal-to-noise ratio, per hop.
- **Latency:** time from form submit to dashboard update.
- **Range:** max reliable distance per hop for our terrain (validates the 3–10 mile claim).

---

## 9. Open Questions / Risks

- **Encryption:** LoRa payloads should be encrypted (e.g., AES) before transmission; confirm
  RadioLib + key management approach. "Encrypted" claims in outreach depend on this being
  implemented.
- **FCC:** 915 MHz ISM operation is license-free within duty-cycle and power limits; confirm
  the chosen settings stay within Part 15 limits.
- **Mesh scale:** flood-with-TTL routing is simple and robust for a handful of nodes; revisit
  if scaling past ~10–15 nodes.
- **Antenna safety:** never transmit without an antenna attached (can damage the SX1262).

---

## 10. Decisions Log

Key decisions made during planning, so we don't re-litigate them later:

- **Board:** DIYmall 2-pack LoRa32 V3 (B0CY1XKZQC). Blank boards so all software is the
  student's own work. Chosen over pre-flashed (Meshnology), no-OLED singles, and bare radio
  modules.
- **OLED:** kept — near-zero cost, big value for debugging and demos.
- **Bundled antenna:** kept — indoor use, safety default, Phase 4 baseline.
- **Board count:** start with 2 (Phases 1–3), buy the 3rd for Phase 4 multi-hop testing.
- **Power:** USB/wall power for indoor phases; USB power banks for field testing; solar only at
  a later pilot stage.
- **Enclosure:** none until a real outdoor pilot; then IP65/66 box with external antenna.
- **Side research:** son's bare Waveshare modules (B0G4418815) are a separate learning track,
  not part of the main deliverable.
- **Sourcing (Amazon vs. Temu):** buy from **Amazon (DIYmall)**, not Temu. Confirmed from the
  Temu product page: the listing is **"1pc" (a single board), antenna NOT included** — the
  "with 5DBi Antenna" text is copied from the Amazon title, but the actual item and its spec
  sheet describe only the board (ESP32-S3FN8 + SX1262, Type-C, no antenna, no battery). Net:
  Temu ~$18.42 + antenna (~$3–5) ≈ $22–26 for **one** board with antenna, vs. DIYmall ~$24 for
  **one of two** boards *with* antenna (2-pack $47.99, two antennas included). Effectively the
  same price per board, but DIYmall gives 2 matched boards + 2 antennas, Amazon shipping, and
  easy returns. The Temu board is genuine same-spec hardware (reviews confirm it works as a
  Meshtastic node) — just not a better deal once it's a single without the antenna.
- **Honesty in outreach:** range framed as "up to 3–10 miles, terrain dependent"; prototype
  described as early-stage (not built); website demo offered, hardware demo not offered yet.

---

## 11. Getting Started (once hardware arrives)

Do these in order. Stop and confirm each works before moving on.

1. **Unbox & inspect.** Confirm 2 boards + 2 antennas. **Attach an antenna to each board before
   ever powering on** (never transmit bare).
2. **Install tools.** VS Code + PlatformIO extension (or Arduino IDE). Install the RadioLib
   library. Have a data-capable USB-C cable ready.
3. **Phase 1 — ping-pong test.** Flash a basic RadioLib 915 MHz transmit sketch on one board and
   a receive sketch on the other. Confirm messages pass between two rooms; note RSSI/SNR on the
   OLED. *This is the go/no-go gate — get this working first.*
4. **Phase 2 — captive portal.** Add the SoftAP + DNS captive portal + LittleFS web form. Connect
   a phone, submit the form, confirm the transmitting node sends the 32-byte packet.
5. **Phase 3 — cloud pipeline.** Use the Kiro prompts in §6 to generate the AWS CDK stack.
   Connect the gateway board over USB and confirm packets reach Lambda → DynamoDB.
6. **Phase 4 — field test.** Buy the 3rd board + power banks. Do the 1–3 mile drive test and log
   the §8 metrics. Optionally swap in a high-gain antenna and compare.
7. **Phase 5 — write-up.** Record a demo video, document results, prepare competition
   submissions and the provisional patent filing.

**First milestone to hit:** Phase 1 ping-pong working. Everything else builds on it.
