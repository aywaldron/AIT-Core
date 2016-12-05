#!/usr/bin/env python2.7

# Copyright 2015 California Institute of Technology.  ALL RIGHTS RESERVED.
# U.S. Government Sponsorship acknowledged.


import datetime
import os
import struct
import time
import warnings

import nose

from bliss.core import dmc, pcap


TmpFilename = None

with warnings.catch_warnings():
    warnings.simplefilter('ignore')
    TmpFilename = os.tmpnam()


def testPCapGlobalHeader ():
    header = pcap.PCapGlobalHeader()
    assert header.magic_number  == 0xA1B2C3D4
    assert header.version_major == 2
    assert header.version_minor == 4
    assert header.thiszone      == 0
    assert header.sigfigs       == 0
    assert header.snaplen       == 65535
    assert header.network       == 147
    assert str(header)          == header._data
    assert len(header)          == 24
    assert header.incomplete()  == False


def testPCapPacketHeader ():
    header = pcap.PCapPacketHeader()
    assert time.time() - header.ts <= 1
    assert header.incl_len == 0
    assert header.orig_len == 0
    assert str(header)     == header._data


def testReadBigEndian ():
    bytes = 'Hello World!'
    ts    = int( time.time() )

    # Write pcap file
    with open(TmpFilename, 'wb') as stream:
        stream.write( struct.pack('>IHHiIII', 0xA1B2C3D4, 2, 4, 0, 0, 65535, 147) )
        stream.write( struct.pack('>IIII', ts, 0, len(bytes), len(bytes)) )
        stream.write(bytes)

    # Read pcap using API
    with pcap.open(TmpFilename, 'r') as stream:
        assert stream.header.magic_number  == 0xA1B2C3D4
        assert stream.header.version_major == 2
        assert stream.header.version_minor == 4
        assert stream.header.thiszone      == 0
        assert stream.header.sigfigs       == 0
        assert stream.header.snaplen       == 65535
        assert stream.header.network       == 147

        header, packet = stream.read()
        assert header.ts       == ts
        assert header.incl_len == len(bytes)
        assert header.orig_len == len(bytes)
        assert packet          == bytes

        header, packet = stream.read()
        assert header.incomplete()
        assert packet is None

    os.unlink(TmpFilename)


def testReadLittleEndian ():
    bytes = 'Hello World!'
    ts    = int( time.time() )

    # Write pcap file
    with open(TmpFilename, 'wb') as stream:
        stream.write( struct.pack('<IHHiIII', 0xA1B2C3D4, 2, 4, 0, 0, 65535, 147) )
        stream.write( struct.pack('<IIII', ts, 0, len(bytes), len(bytes)) )
        stream.write(bytes)

    # Read pcap using API
    with pcap.open(TmpFilename, 'r') as stream:
        assert stream.header.magic_number  == 0xA1B2C3D4
        assert stream.header.version_major == 2
        assert stream.header.version_minor == 4
        assert stream.header.thiszone      == 0
        assert stream.header.sigfigs       == 0
        assert stream.header.snaplen       == 65535
        assert stream.header.network       == 147

        header, packet = stream.read()
        assert header.ts       == ts
        assert header.incl_len == len(bytes)
        assert header.orig_len == len(bytes)
        assert packet          == bytes

        header, packet = stream.read()
        assert header.incomplete()
        assert packet is None

    os.unlink(TmpFilename)


def testWrite ():
    bytes = 'Hello World!'
    ts    = time.time()

    # Write pcap using API
    with pcap.open(TmpFilename, 'w') as stream:
        assert stream.write(bytes) == len(bytes)

    # Read pcap file
    with open(TmpFilename, 'rb') as stream:
        header = struct.unpack('IHHiIII', stream.read(24))
        assert header == (0xA1B2C3D4, 2, 4, 0, 0, 65535, 147)

        header = struct.unpack('IIII', stream.read(16))
        assert header[0] - ts <= 1      # write timestamp
        assert header[2] == len(bytes)  # number of octets of packet saved in file
        assert header[3] == len(bytes)  # actual length of packet

        assert stream.read(header[2]) == bytes
        assert len(stream.read())     == 0

    os.unlink(TmpFilename)


def testWriteRead ():
    packets = 'When a packet hits a pocket on a socket on a port.'.split()

    with pcap.open(TmpFilename, 'w') as stream:
        for p in packets:
            stream.write(p)

    with pcap.open(TmpFilename, 'r') as stream:
        index   = 0
        prev_ts = 0

        for header, packet in stream:
            assert header.ts       >= prev_ts
            assert header.incl_len == len( packets[index] )
            assert header.orig_len == len( packets[index] )
            assert packet          == packets[index]

            index   += 1
            prev_ts  = header.ts

        assert index == len(packets)

        header, packet = stream.read()
        assert header.incomplete()
        assert packet is None

    os.unlink(TmpFilename)


def testPCapPacketHeaderInit ():
    header = pcap.PCapPacketHeader()
    assert header._format == 'IIII'
    assert header._size == 16
    assert header.incl_len == 0
    assert header.orig_len == 0
    assert header._data == str(header)
    assert header._swap == '@'

    ts, usec = dmc.getTimestampUTC()
    header.ts_sec, header.ts_usec = ts, usec

    float_ts = float(ts) + (float(usec) / 1e6)
    assert header.ts == float_ts
    assert header.timestamp == datetime.datetime.utcfromtimestamp(float_ts)


if __name__ == '__main__':
  nose.main()