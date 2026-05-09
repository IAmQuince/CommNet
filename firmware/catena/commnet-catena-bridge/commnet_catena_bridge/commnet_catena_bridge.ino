#include "src/CommNetCatenaBridge.h"

CommNetCatenaBridge bridge;

void setup() {
  bridge.begin();
}

void loop() {
  bridge.poll();
}
