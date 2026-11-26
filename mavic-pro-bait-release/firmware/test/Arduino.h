// Minimal host-side stand-in for the Arduino-ESP32 API, enough to run bait_release.ino's logic.
#pragma once
#include <cstdint>
#include <cstring>
#include <cstdio>
#include <cstdarg>
#include <deque>
#include <vector>
#include <algorithm>
#include <string>
#include <cstdlib>
#define ESP_ARDUINO_VERSION_MAJOR 3
#define OUTPUT 1
#define LOW 0
#define HIGH 1
#define SERIAL_8N1 0
#define ADC_11db 3
extern uint32_t g_ms;
inline uint32_t millis() { return g_ms; }
template <class T, class A, class B> T constrain(T x, A a, B b) { return x < a ? a : (x > b ? b : x); }
inline void pinMode(int, int) {}
extern int g_led;
inline void digitalWrite(int, int v) { g_led = v; }
extern uint32_t g_duty;
inline bool ledcAttach(int, uint32_t, uint32_t) { return true; }
inline void ledcWrite(int, uint32_t d) { g_duty = d; }
extern uint32_t g_adc_mv;
inline uint32_t analogReadMilliVolts(int) { return g_adc_mv; }
inline void analogReadResolution(int) {}
inline void analogSetPinAttenuation(int, int) {}
struct HostSerial {
  std::deque<uint8_t> in; std::vector<uint8_t> out; bool quiet = true;
  void begin(uint32_t, int = 0, int = -1, int = -1) {}
  int available() { return (int)in.size(); }
  int read() { int b = in.front(); in.pop_front(); return b; }
  size_t write(const uint8_t *p, size_t n) { out.insert(out.end(), p, p + n); return n; }
  void printf(const char *f, ...) { if (quiet) return; va_list a; va_start(a, f); vprintf(f, a); va_end(a); }
};
extern HostSerial Serial, Serial1;
