// Host test for bait_release.ino: CRSF decode, state machine, failsafe, telemetry framing.
//   g++ -std=c++17 -I. test_logic.cpp -o t && ./t
#include "Arduino.h"
uint32_t g_ms = 0, g_duty = 0, g_adc_mv = 1950; int g_led = 1;
HostSerial Serial, Serial1;
#include "../bait_release/bait_release.ino"

static int fails = 0;
#define CHECK(c, msg) do { if (!(c)) { printf("FAIL %s (line %d)\n", msg, __LINE__); fails++; } else printf("ok   %s\n", msg); } while (0)

static uint16_t us_to_ticks(int us) { return (uint16_t)((us - 1500) * 8 / 5 + 992); }
static void push_rc(const int *us16) {
  uint8_t p[22] = {0}; uint32_t bits = 0; int nb = 0, k = 0;
  for (int c = 0; c < 16; c++) {
    bits |= (uint32_t)us_to_ticks(us16[c]) << nb; nb += 11;
    while (nb >= 8) { p[k++] = bits & 0xFF; bits >>= 8; nb -= 8; }
  }
  uint8_t f[26] = {0xC8, 24, 0x16};
  memcpy(f + 3, p, 22);
  f[25] = crc8_dvb_s2(f + 2, 23);
  for (auto b : f) Serial1.in.push_back(b);
}
static void push_lq(uint8_t lq) {
  uint8_t f[14] = {0xC8, 12, 0x14, 50, 50, lq, 10, 0, 4, 3, 60, 100, 8};
  f[13] = crc8_dvb_s2(f + 2, 11);
  for (auto b : f) Serial1.in.push_back(b);
}
static int sw = 1000;   // release switch position (us)
static void run(uint32_t ms, bool link = true) {   // 4 ms frames (250 Hz)
  for (uint32_t t = 0; t < ms; t += 4) {
    if (link) { int ch[16]; for (auto &c : ch) c = 1500; ch[RELEASE_CH - 1] = sw; push_rc(ch); }
    g_ms += 4; loop();
  }
}
static uint16_t servo_now() { return (uint16_t)((uint64_t)g_duty * 20000 / ((1u << 14) - 1) + 0.5); }

int main() {
  setup();
  CHECK(state == SAFE && servo_now() >= LOCK_US - 2 && servo_now() <= LOCK_US + 2, "power on: SAFE, servo at LOCK");

  // decode check with distinct channel values
  int ch[16]; for (int i = 0; i < 16; i++) ch[i] = 1000 + i * 60;
  push_rc(ch); g_ms += 4; crsf_poll();
  bool dec = true; for (int i = 0; i < 16; i++) dec &= abs((int)ch_us[i] - ch[i]) <= 1;
  CHECK(dec, "16 channels decode to within 1 us");

  // corrupt frame is ignored
  uint16_t before = ch_us[0]; int bad[16]; for (auto &c : bad) c = 2000;
  push_rc(bad); Serial1.in[Serial1.in.size() - 1] ^= 0x55; crsf_poll();
  CHECK(ch_us[0] == before, "bad CRC frame ignored");

  sw = 2000; run(2000);
  CHECK(state == SAFE, "switch left at OPEN on power-up: stays SAFE (no drop)");
  sw = 1000; run(300);
  CHECK(state == SAFE, "LOW for 0.3 s: still SAFE");
  run(300);
  CHECK(state == LOCKED, "LOW for 0.6 s: LOCKED");
  sw = 2000; run(48); sw = 1000; run(100);
  CHECK(state == LOCKED, "48 ms glitch to OPEN: ignored");
  sw = 2000; run(120);
  CHECK(state == OPEN && abs((int)servo_now() - OPEN_US) <= 2, "switch OPEN 120 ms: OPEN, servo at OPEN_US");
  sw = 1000; run(250);
  CHECK(state == LOCKED && abs((int)servo_now() - LOCK_US) <= 2, "switch back: LOCKED (reload)");

  run(400, false);
  CHECK(state == SAFE && abs((int)servo_now() - LOCK_US) <= 2, "link lost while locked: SAFE, servo holds LOCK");
  sw = 2000; run(1000);
  CHECK(state == SAFE, "link back with switch at OPEN: no drop until re-armed");
  sw = 1000; run(600); sw = 2000; run(150);
  CHECK(state == OPEN, "re-armed then OPEN: releases");
  run(500, false);
  CHECK(state == OPEN, "link lost while open: stays open");
  sw = 1000; run(300);
  CHECK(state == LOCKED, "link back, switch LOW: closes");

  push_lq(0); run(8);
  // lq 0 is applied, but the next RC frames keep coming: ELRS sends LQ 0 only while in failsafe
  CHECK(uplink_lq == 0 || state != OPEN, "link stats LQ parsed");
  push_lq(100); run(8);

  // telemetry: last battery frame
  Serial1.out.clear(); g_adc_mv = 1950; for (int i = 0; i < 100; i++) vbat_poll(), g_ms += 50;
  run(600);
  auto &o = Serial1.out; bool found = false, crc_ok = false; float v = 0; std::string fm;
  for (size_t i = 0; i + 4 < o.size(); i++) {
    if (o[i] != 0xC8) continue;
    uint8_t len = o[i + 1]; if (i + 2 + len > o.size()) continue;
    if (o[i + 2] == 0x08 && len == 10) {
      found = true; crc_ok = crc8_dvb_s2(&o[i + 2], len - 1) == o[i + 1 + len];
      v = ((o[i + 3] << 8) | o[i + 4]) / 10.0f;
    }
    if (o[i + 2] == 0x21) fm = std::string((const char *)&o[i + 3]);
  }
  CHECK(found && crc_ok, "battery telemetry frame sent with good CRC");
  CHECK(v > 3.85f && v < 3.95f, "battery reads 3.9 V from 1.95 V at the pin");
  CHECK(fm == "LOCK", "flight-mode string reports LOCK");

  printf(fails ? "\n%d FAILED\n" : "\nall passed\n", fails);
  return fails != 0;
}
