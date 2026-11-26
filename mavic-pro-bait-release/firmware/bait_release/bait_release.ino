// Bait release controller — ESP32-C3 SuperMini
//
// Reads CRSF from an ExpressLRS or TBS Crossfire receiver, drives the release servo,
// and sends the pod's battery voltage and release state back to the radio as telemetry.
//
// Behaviour
//   * Power on -> servo LOCKED, state SAFE. Release is ignored until the release switch
//     has been seen LOW (locked) for BOOT_LOW_MS. So a switch left in OPEN at power-up
//     cannot drop the bait.
//   * Switch HIGH for RELEASE_HOLD_MS -> OPEN. Switch LOW for CLOSE_HOLD_MS -> LOCKED.
//     (Loading: switch to OPEN, put the loop in the gap, switch back to LOCKED.)
//   * Optional arm switch (ARM_CH): when set, OPEN also needs that switch HIGH.
//   * Link lost (no RC frames for FAILSAFE_MS, or link quality 0): the servo holds where it
//     is. If it was LOCKED it goes back to SAFE and needs the switch LOW again before the
//     next release. It never opens on failsafe.
//   * Telemetry every TELEM_MS: battery sensor (pod voltage, % estimate) and a flight-mode
//     string: SAFE / LOCK / OPEN. In EdgeTX: "RxBt" (volts), "Bat%" and "FM" after Discover sensors.
//
// Wiring (see ../README.md): RX TX -> GPIO20, RX RX <- GPIO21, servo signal GPIO4,
// battery divider (100k/100k from the switched cell +) -> GPIO3, onboard LED GPIO8.
//
// Builds with the Arduino IDE (board "ESP32C3 Dev Module", USB CDC On Boot: Enabled)
// or PlatformIO (../platformio.ini). Arduino-ESP32 core 2.x or 3.x.

#include <Arduino.h>

// ------------------------------------------------------------------ settings
#define CRSF_BAUD        420000   // ELRS default. TBS Crossfire: 416666 also works at 420000
#define PIN_CRSF_RX      20       // <- receiver TX
#define PIN_CRSF_TX      21       // -> receiver RX (telemetry). Leave unwired if not wanted
#define PIN_SERVO        4
#define PIN_VBAT         3        // ADC1_CH3, via 100k/100k divider
#define PIN_LED          8        // SuperMini blue LED, active low

#define RELEASE_CH       6        // 1-based CRSF channel for the release switch
#define ARM_CH           0        // 1-based arm channel, 0 = not used
#define HIGH_US          1700     // switch counts as HIGH above this
#define LOW_US           1300     // switch counts as LOW below this

#define LOCK_US          1250     // servo pulse for LOCKED (arc across the gap)
#define OPEN_US          1850     // servo pulse for OPEN (arc ~52 deg back). Calibrate both.

#define RELEASE_HOLD_MS  100
#define CLOSE_HOLD_MS    200
#define BOOT_LOW_MS      500
#define FAILSAFE_MS      300
#define TELEM_MS         500

#define VBAT_DIVIDER     2.0f     // (R1 + R2) / R2
#define VBAT_TRIM        1.00f    // multiply to match a multimeter
#define VBAT_EMPTY       3.30f    // 0 % for the estimate
#define VBAT_FULL        4.20f    // 100 %

// ------------------------------------------------------------------ CRSF
enum : uint8_t {
  CRSF_SYNC          = 0xC8,
  CRSF_RC_CHANNELS   = 0x16,
  CRSF_LINK_STATS    = 0x14,
  CRSF_BATTERY       = 0x08,
  CRSF_FLIGHT_MODE   = 0x21,
};

static uint8_t crc8_dvb_s2(const uint8_t *p, size_t n) {
  uint8_t crc = 0;
  while (n--) {
    crc ^= *p++;
    for (int i = 0; i < 8; i++) crc = (crc & 0x80) ? (uint8_t)((crc << 1) ^ 0xD5) : (uint8_t)(crc << 1);
  }
  return crc;
}

static uint16_t ch_us[16];          // channel values in microseconds
static uint32_t last_rc_ms = 0;     // last good RC frame
static bool     have_rc = false;
static uint8_t  uplink_lq = 100;

static void handle_frame(const uint8_t *f, uint8_t len) {
  // f[0] = type, f[1..len-2] = payload, f[len-1] = crc
  uint8_t type = f[0];
  if (type == CRSF_RC_CHANNELS && len == 24) {
    const uint8_t *p = f + 1;
    uint32_t bits = 0; int nbits = 0, ch = 0;
    for (int i = 0; i < 22 && ch < 16; i++) {
      bits |= (uint32_t)p[i] << nbits;
      nbits += 8;
      while (nbits >= 11 && ch < 16) {
        uint16_t v = bits & 0x7FF;
        bits >>= 11; nbits -= 11;
        ch_us[ch++] = (uint16_t)(((int32_t)v - 992) * 5 / 8 + 1500);   // 172..1811 -> 988..2012
      }
    }
    last_rc_ms = millis();
    have_rc = true;
  } else if (type == CRSF_LINK_STATS && len >= 11) {
    uplink_lq = f[3];   // payload: rssi1, rssi2, lq, ...
  }
}

static void crsf_poll() {
  static uint8_t buf[64];
  static uint8_t pos = 0, need = 0;
  while (Serial1.available()) {
    uint8_t b = Serial1.read();
    if (pos == 0) {                       // address byte: accept the usual ones
      if (b == 0xC8 || b == 0xEE || b == 0xEA || b == 0xEC) buf[pos++] = b;
      continue;
    }
    if (pos == 1) {
      if (b < 2 || b > 62) { pos = 0; continue; }
      need = b; buf[pos++] = b;
      continue;
    }
    buf[pos++] = b;
    if (pos == need + 2) {
      if (crc8_dvb_s2(buf + 2, need - 1) == buf[need + 1]) handle_frame(buf + 2, need);
      pos = 0;
    }
  }
}

static void crsf_send(uint8_t type, const uint8_t *payload, uint8_t n) {
  uint8_t f[64];
  f[0] = CRSF_SYNC;
  f[1] = n + 2;                 // type + payload + crc
  f[2] = type;
  memcpy(f + 3, payload, n);
  f[3 + n] = crc8_dvb_s2(f + 2, n + 1);
  Serial1.write(f, n + 4);
}

// ------------------------------------------------------------------ servo (LEDC, 50 Hz)
static const uint32_t SERVO_HZ = 50, SERVO_BITS = 14;
static void servo_begin() {
#if ESP_ARDUINO_VERSION_MAJOR >= 3
  ledcAttach(PIN_SERVO, SERVO_HZ, SERVO_BITS);
#else
  ledcSetup(0, SERVO_HZ, SERVO_BITS);
  ledcAttachPin(PIN_SERVO, 0);
#endif
}
static void servo_us(uint16_t us) {
  uint32_t duty = (uint32_t)us * ((1u << SERVO_BITS) - 1) / (1000000u / SERVO_HZ);
#if ESP_ARDUINO_VERSION_MAJOR >= 3
  ledcWrite(PIN_SERVO, duty);
#else
  ledcWrite(0, duty);
#endif
}

// ------------------------------------------------------------------ battery
static float vbat = 0;
static void vbat_poll() {
  static uint32_t t = 0;
  if (millis() - t < 50) return;
  t = millis();
  float v = analogReadMilliVolts(PIN_VBAT) / 1000.0f * VBAT_DIVIDER * VBAT_TRIM;
  vbat = (vbat == 0) ? v : vbat * 0.9f + v * 0.1f;
}

// ------------------------------------------------------------------ state machine
enum State : uint8_t { SAFE, LOCKED, OPEN };
static State state = SAFE;
static const char *STATE_NAME[] = {"SAFE", "LOCK", "OPEN"};

static void set_state(State s) {
  state = s;
  servo_us(s == OPEN ? OPEN_US : LOCK_US);
}

static void update_state() {
  uint32_t now = millis();
  bool link = have_rc && (now - last_rc_ms < FAILSAFE_MS) && uplink_lq > 0;
  static uint32_t low_since = 0, high_since = 0;

  if (!link) {                         // failsafe: hold position, never open
    low_since = high_since = 0;
    if (state == LOCKED) set_state(SAFE);
    return;
  }
  uint16_t rel = ch_us[RELEASE_CH - 1];
  bool armed = (ARM_CH == 0) || ch_us[ARM_CH - 1] > HIGH_US;
  bool hi = rel > HIGH_US, lo = rel < LOW_US;
  if (hi) { if (!high_since) high_since = now; } else high_since = 0;
  if (lo) { if (!low_since)  low_since  = now; } else low_since  = 0;

  switch (state) {
    case SAFE:
      if (lo && now - low_since >= BOOT_LOW_MS) set_state(LOCKED);
      break;
    case LOCKED:
      if (hi && armed && now - high_since >= RELEASE_HOLD_MS) set_state(OPEN);
      break;
    case OPEN:
      if (lo && now - low_since >= CLOSE_HOLD_MS) set_state(LOCKED);
      break;
  }
}

// ------------------------------------------------------------------ telemetry
static void telemetry() {
  static uint32_t t = 0;
  if (millis() - t < TELEM_MS || !have_rc) return;
  t = millis();
  uint16_t dv = (uint16_t)(vbat * 10.0f + 0.5f);
  float pct = (vbat - VBAT_EMPTY) / (VBAT_FULL - VBAT_EMPTY) * 100.0f;
  uint8_t rem = (uint8_t)constrain(pct, 0.0f, 100.0f);
  uint8_t bat[8] = {(uint8_t)(dv >> 8), (uint8_t)dv, 0, 0, 0, 0, 0, rem};
  crsf_send(CRSF_BATTERY, bat, sizeof bat);
  const char *s = STATE_NAME[state];
  crsf_send(CRSF_FLIGHT_MODE, (const uint8_t *)s, strlen(s) + 1);
}

// ------------------------------------------------------------------ LED
static void led() {
  uint32_t ms = millis();
  bool link = have_rc && (ms - last_rc_ms < FAILSAFE_MS);
  bool on;
  if (!link)              on = (ms % 1000) < 60 || ((ms % 1000) > 200 && (ms % 1000) < 260);  // double blip
  else if (state == SAFE) on = (ms % 200) < 100;          // fast blink: flip release switch to LOCK
  else if (state == OPEN) on = true;
  else                    on = (ms % 1000) < 60;          // locked: slow blip
  digitalWrite(PIN_LED, on ? LOW : HIGH);
}

void setup() {
  pinMode(PIN_LED, OUTPUT);
  digitalWrite(PIN_LED, HIGH);
  for (auto &c : ch_us) c = 1500;
  servo_begin();
  set_state(SAFE);                     // servo to LOCK straight away
  analogReadResolution(12);
  analogSetPinAttenuation(PIN_VBAT, ADC_11db);
  Serial.begin(115200);
  Serial1.begin(CRSF_BAUD, SERIAL_8N1, PIN_CRSF_RX, PIN_CRSF_TX);
}

void loop() {
  crsf_poll();
  vbat_poll();
  update_state();
  telemetry();
  led();
  static uint32_t dbg = 0;             // USB serial status once a second
  if (millis() - dbg > 1000) {
    dbg = millis();
    Serial.printf("%s rel=%u arm=%u lq=%u vbat=%.2f link=%d\n", STATE_NAME[state],
                  ch_us[RELEASE_CH - 1], ARM_CH ? ch_us[ARM_CH - 1] : 0, uplink_lq, vbat,
                  have_rc && millis() - last_rc_ms < FAILSAFE_MS);
  }
}
