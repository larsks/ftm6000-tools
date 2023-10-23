Tools for interacting with a Yaesu FTM-6000

## Protocol notes

The clone protocol is a series of 130-byte frames in the following format:

```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|            Address            |                               |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+                               +
|                                                               |
+                                                               +
|                                                               |
+                                                               +
|                              Data                             |
+                               +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                               |    Checksum   |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

The checksum is calculated by summing up the address and data bytes and then reducing that modulo 256:

```
checksum = (sum(address) + sum(data)) % 256
```

While the address is only two bytes (which is only suitable for addressing up to 64k of memory), the radio has 98176 bytes of memory. After reading the first 64k of data, the address wraps to 0, and subsequent addresses must be adjusted by adding `0x10000`.

Addresses are not written sequentially. The data is delivered in the following ranges:

1. `0x0`
1. `0x100` - `0x380`
1. `0x480` - `0x17F80`

This is followed by two blocks with addresses `0xfffd` and `0xfffe`. These addresses don't represent actual memory locations; presumably this is some sort of protocol metadata.

## Memory layout

- Channels appear to start at `0x800`, and occupy 16 bytes each. The frequency is stored in bytes 3 and 4 with a leading `0` for VHF and a leading `8` for VHF. I suspect this is a band identifier, but I have not verified that yet.

  ```
  00000800: 8102 0145 4310 0000 0097 000f 000c 0000  ...EC...........
  00000810: 8102 0145 2310 0000 0088 000f 000c 0000  ...E#...........
  00000820: 8302 8449 7214 0000 0090 000f 0064 0000  ...Ir........d..
  .
  .
  .
  ```

- Channel labels start at 0x10000. Each label occupies 16 bytes, although a label can only be up to 6 characters long.

  ```
  00010000: 4d4d 5242 454c ffff ffff ffff ffff ffff  MMRBEL..........
  00010010: 4241 5243 ffff ffff ffff ffff ffff ffff  BARC............
  00010020: 4d49 54ff ffff ffff ffff ffff ffff ffff  MIT.............
  .
  .
  .
  ```

- The radio supports up to 1100 channels, so channels in theory run from `0x800` to `0x4cc0` and channel labels from `0x10000` to `0x144c0`.
