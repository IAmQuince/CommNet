---
document_id: CMN-HW-GUIDE-001
title: Catena Manual Test
revision: r0
status: WIP
package: 20260508_07_NetPathCatena
---

# Catena Manual Test

Use 115200 baud and newline line endings. Test commands:

```text
CMN1|PING|nonce=12345
CMN1|ID?
CMN1|STATUS?
CMN1|CFG|profile=us915_test|sf=7|bw=125|cr=45|txp=10
CMN1|TX|id=msg_002|class=text_message|to=broadcast|body=SGVsbG8
```

Expected TX response:

```text
CMN1|ACK|id=msg_002|status=accepted|detail=local_hardware_ack_only|class=text_message|to=broadcast|bytes=5
```
