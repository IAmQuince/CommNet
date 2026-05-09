#ifndef COMMNET_CATENA_BRIDGE_H
#define COMMNET_CATENA_BRIDGE_H

#include <Arduino.h>

class CommNetCatenaBridge {
public:
  void begin();
  void poll();

private:
  static const size_t LINE_BUFFER_SIZE = 320;
  static const size_t VALUE_BUFFER_SIZE = 48;
  static const size_t MSG_ID_BUFFER_SIZE = 32;
  static const size_t PAYLOAD_LIMIT_BYTES = 180;
  static const unsigned long HEARTBEAT_INTERVAL_MS = 10000UL;

  char line_[LINE_BUFFER_SIZE];
  size_t line_len_ = 0;
  bool discarding_long_line_ = false;

  char profile_[VALUE_BUFFER_SIZE] = "serial_only";
  char sf_[VALUE_BUFFER_SIZE] = "unset";
  char bw_[VALUE_BUFFER_SIZE] = "unset";
  char cr_[VALUE_BUFFER_SIZE] = "unset";
  char txp_[VALUE_BUFFER_SIZE] = "unset";
  char last_error_[VALUE_BUFFER_SIZE] = "none";
  char last_msg_id_[MSG_ID_BUFFER_SIZE] = "none";

  unsigned long tx_count_ = 0;
  unsigned long rx_count_ = 0;
  unsigned long err_count_ = 0;
  unsigned long last_heartbeat_ms_ = 0;

  void readSerial();
  void processLine(char *line);
  void handleCommand(char *command, char **fields, size_t field_count);
  void handlePing(char **fields, size_t field_count);
  void handleId();
  void handleStatus();
  void handleCfg(char **fields, size_t field_count);
  void handleTx(char **fields, size_t field_count);

  const char *fieldValue(char **fields, size_t field_count, const char *key);
  bool validateBase64UrlPayload(const char *body, size_t *decoded_len);
  void copySafe(char *dst, size_t dst_size, const char *src);
  void setLastError(const char *code);
  void sendBoot();
  void sendErr(const char *id, const char *code, const char *detail);
  void sendStatusLine();
  void maybeHeartbeat();
};

#endif
