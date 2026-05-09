#include "CommNetCatenaBridge.h"

namespace {
const char *PREFIX = "CMN1";
const char *DEVICE = "catena4610";
const char *FIRMWARE = "commnet-catena-bridge";
const char *VERSION = "0.1.0";
const unsigned long SERIAL_WAIT_MS = 3000UL;
}

void CommNetCatenaBridge::begin() {
  Serial.begin(115200);
  const unsigned long start = millis();
  while (!Serial && (millis() - start) < SERIAL_WAIT_MS) {
    delay(10);
  }
  sendBoot();
}

void CommNetCatenaBridge::poll() {
  readSerial();
  maybeHeartbeat();
}

void CommNetCatenaBridge::readSerial() {
  while (Serial.available() > 0) {
    const char ch = static_cast<char>(Serial.read());

    if (ch == '\r') {
      continue;
    }

    if (ch == '\n') {
      if (discarding_long_line_) {
        discarding_long_line_ = false;
        line_len_ = 0;
        sendErr("none", "line_too_long", "max_319");
        return;
      }

      line_[line_len_] = '\0';
      if (line_len_ > 0) {
        processLine(line_);
      }
      line_len_ = 0;
      return;
    }

    if (discarding_long_line_) {
      continue;
    }

    if (line_len_ >= LINE_BUFFER_SIZE - 1) {
      discarding_long_line_ = true;
      line_len_ = 0;
      setLastError("line_too_long");
      continue;
    }

    line_[line_len_++] = ch;
  }
}

void CommNetCatenaBridge::processLine(char *line) {
  char *tokens[16];
  size_t token_count = 0;
  char *save = nullptr;

  for (char *tok = strtok_r(line, "|", &save);
       tok != nullptr && token_count < 16;
       tok = strtok_r(nullptr, "|", &save)) {
    tokens[token_count++] = tok;
  }

  if (token_count < 2 || strcmp(tokens[0], PREFIX) != 0) {
    sendErr("none", "parse_error", "expected_CMN1_prefix");
    return;
  }

  handleCommand(tokens[1], &tokens[2], token_count - 2);
}

void CommNetCatenaBridge::handleCommand(char *command, char **fields, size_t field_count) {
  if (strcmp(command, "PING") == 0) {
    handlePing(fields, field_count);
  } else if (strcmp(command, "ID?") == 0) {
    handleId();
  } else if (strcmp(command, "STATUS?") == 0) {
    handleStatus();
  } else if (strcmp(command, "CFG") == 0) {
    handleCfg(fields, field_count);
  } else if (strcmp(command, "TX") == 0) {
    handleTx(fields, field_count);
  } else {
    sendErr("none", "unknown_command", command);
  }
}

void CommNetCatenaBridge::handlePing(char **fields, size_t field_count) {
  const char *nonce = fieldValue(fields, field_count, "nonce");
  Serial.print(PREFIX);
  Serial.print("|PONG|nonce=");
  Serial.print(nonce ? nonce : "");
  Serial.print("|uptime_ms=");
  Serial.println(millis());
}

void CommNetCatenaBridge::handleId() {
  Serial.print(PREFIX);
  Serial.print("|ID|device=");
  Serial.print(DEVICE);
  Serial.print("|fw=");
  Serial.print(FIRMWARE);
  Serial.print("|ver=");
  Serial.print(VERSION);
  Serial.println("|adapter=catena_serial_lora|rf_mode=disabled");
}

void CommNetCatenaBridge::handleStatus() {
  sendStatusLine();
}

void CommNetCatenaBridge::handleCfg(char **fields, size_t field_count) {
  const char *profile = fieldValue(fields, field_count, "profile");
  const char *sf = fieldValue(fields, field_count, "sf");
  const char *bw = fieldValue(fields, field_count, "bw");
  const char *cr = fieldValue(fields, field_count, "cr");
  const char *txp = fieldValue(fields, field_count, "txp");

  if (profile) copySafe(profile_, sizeof(profile_), profile);
  if (sf) copySafe(sf_, sizeof(sf_), sf);
  if (bw) copySafe(bw_, sizeof(bw_), bw);
  if (cr) copySafe(cr_, sizeof(cr_), cr);
  if (txp) copySafe(txp_, sizeof(txp_), txp);

  Serial.print(PREFIX);
  Serial.print("|ACK|id=cfg|status=accepted|profile=");
  Serial.print(profile_);
  Serial.println("|rf_mode=disabled");
}

void CommNetCatenaBridge::handleTx(char **fields, size_t field_count) {
  const char *id = fieldValue(fields, field_count, "id");
  const char *payload_class = fieldValue(fields, field_count, "class");
  const char *to = fieldValue(fields, field_count, "to");
  const char *body = fieldValue(fields, field_count, "body");
  size_t decoded_len = 0;

  if (!id || id[0] == '\0') {
    sendErr("none", "missing_id", "TX_requires_id");
    return;
  }

  if (!body || body[0] == '\0') {
    sendErr(id, "missing_body", "TX_requires_body");
    return;
  }

  if (!validateBase64UrlPayload(body, &decoded_len)) {
    sendErr(id, "bad_body", "body_must_be_base64url_and_under_limit");
    return;
  }

  copySafe(last_msg_id_, sizeof(last_msg_id_), id);
  copySafe(last_error_, sizeof(last_error_), "none");
  tx_count_++;

  Serial.print(PREFIX);
  Serial.print("|ACK|id=");
  Serial.print(last_msg_id_);
  Serial.print("|status=accepted|detail=local_hardware_ack_only|class=");
  Serial.print(payload_class ? payload_class : "unknown");
  Serial.print("|to=");
  Serial.print(to ? to : "broadcast");
  Serial.print("|bytes=");
  Serial.println(decoded_len);
}

const char *CommNetCatenaBridge::fieldValue(char **fields, size_t field_count, const char *key) {
  const size_t key_len = strlen(key);
  for (size_t i = 0; i < field_count; ++i) {
    if (strncmp(fields[i], key, key_len) == 0 && fields[i][key_len] == '=') {
      return fields[i] + key_len + 1;
    }
  }
  return nullptr;
}

bool CommNetCatenaBridge::validateBase64UrlPayload(const char *body, size_t *decoded_len) {
  size_t encoded_len = 0;
  size_t pad_count = 0;

  for (const char *p = body; *p; ++p) {
    const char ch = *p;
    const bool ok =
      (ch >= 'A' && ch <= 'Z') ||
      (ch >= 'a' && ch <= 'z') ||
      (ch >= '0' && ch <= '9') ||
      ch == '-' ||
      ch == '_' ||
      ch == '=';

    if (!ok) {
      setLastError("bad_body");
      return false;
    }

    if (ch == '=') {
      pad_count++;
    }
    encoded_len++;
  }

  if (encoded_len == 0) {
    setLastError("bad_body");
    return false;
  }

  size_t estimate = (encoded_len * 3) / 4;
  if (pad_count <= 2 && estimate >= pad_count) {
    estimate -= pad_count;
  }

  if (estimate > PAYLOAD_LIMIT_BYTES) {
    setLastError("payload_too_large");
    return false;
  }

  if (decoded_len) {
    *decoded_len = estimate;
  }
  return true;
}

void CommNetCatenaBridge::copySafe(char *dst, size_t dst_size, const char *src) {
  if (!dst || dst_size == 0) {
    return;
  }
  if (!src) {
    dst[0] = '\0';
    return;
  }

  size_t out = 0;
  for (size_t i = 0; src[i] && out < dst_size - 1; ++i) {
    const char ch = src[i];
    const bool safe =
      (ch >= 'A' && ch <= 'Z') ||
      (ch >= 'a' && ch <= 'z') ||
      (ch >= '0' && ch <= '9') ||
      ch == '_' ||
      ch == '-' ||
      ch == '.' ||
      ch == ':' ||
      ch == '/';
    dst[out++] = safe ? ch : '_';
  }
  dst[out] = '\0';
}

void CommNetCatenaBridge::setLastError(const char *code) {
  copySafe(last_error_, sizeof(last_error_), code ? code : "unknown");
  err_count_++;
}

void CommNetCatenaBridge::sendBoot() {
  Serial.print(PREFIX);
  Serial.print("|BOOT|device=");
  Serial.print(DEVICE);
  Serial.print("|fw=");
  Serial.print(FIRMWARE);
  Serial.print("|ver=");
  Serial.print(VERSION);
  Serial.println("|baud=115200|rf_mode=disabled");
}

void CommNetCatenaBridge::sendErr(const char *id, const char *code, const char *detail) {
  setLastError(code);
  Serial.print(PREFIX);
  Serial.print("|ERR|id=");
  Serial.print(id && id[0] ? id : "none");
  Serial.print("|code=");
  Serial.print(code ? code : "unknown");
  Serial.print("|detail=");
  Serial.println(detail ? detail : "");
}

void CommNetCatenaBridge::sendStatusLine() {
  Serial.print(PREFIX);
  Serial.print("|STATUS|uptime_ms=");
  Serial.print(millis());
  Serial.print("|tx=");
  Serial.print(tx_count_);
  Serial.print("|rx=");
  Serial.print(rx_count_);
  Serial.print("|err=");
  Serial.print(err_count_);
  Serial.print("|last_error=");
  Serial.print(last_error_);
  Serial.print("|last_msg_id=");
  Serial.print(last_msg_id_);
  Serial.print("|profile=");
  Serial.print(profile_);
  Serial.println("|rf_mode=disabled");
}

void CommNetCatenaBridge::maybeHeartbeat() {
  const unsigned long now = millis();
  if ((now - last_heartbeat_ms_) >= HEARTBEAT_INTERVAL_MS) {
    last_heartbeat_ms_ = now;
    sendStatusLine();
  }
}
