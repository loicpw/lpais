#!/usr/bin/env python

import lpais.ais as ais
import pytest
import sys
import logging
import pathlib


@pytest.fixture
def data():
    path = pathlib.Path(__file__).parent
    data = path / 'data/samples.raw'
    assert data.exists()
    return data


@pytest.fixture
def decoded():
    path = pathlib.Path(__file__).parent
    data = path / 'data/decoded_samples.txt'
    assert data.exists()
    return data


@pytest.fixture
def decoded_nmea():
    path = pathlib.Path(__file__).parent
    data = path / 'data/decoded_nmea_samples.txt'
    assert data.exists()
    return data


def do_test_decoder(decoder, data, decoded, caplog, create=False):
    result = []

    if create:
        # create the decoded file
        with open(decoded, 'w') as fw:
            with open(data) as f:
                for line in f:
                    if line.strip() and not line.strip().startswith('#'):
                        data = decoder(line)
                        if data:
                            result.append(str(data))

            fw.writelines('\n'.join(result))
        return '\n'.join(result)

    with open(decoded) as outf:
        with open(data) as inpf:
            for line in inpf:
                if line.strip() and not line.strip().startswith('#'):
                    data = decoder(line)
                    if data:
                        result.append(str(data))

        assert '\n'.join(result) == outf.read()
        assert ("DecodeError: Ais7_13: AIS_ERR_BAD_BIT_COUNT "
                "(origin: !AIVDM,1,1,,B,70C<HvRftSLBTtwN4oTg8261,"
                "0*02,r17PDUT1,1272439747)") in caplog.text

        assert "Invalid checksum: !AIVDM,1,1,,B,ENjOspPr?@6a9Qh70`62aP100000PaJ<;co0P00000N010,4*0B" in caplog.text

    return '\n'.join(result)


def test_decoder(data, decoded, caplog):
    decode = ais.decoder()
    do_test_decoder(decode, data, decoded, caplog)

def test_decoder_keep_nmea(data, decoded_nmea, caplog):
    decode = ais.decoder(keep_nmea=True)
    result = do_test_decoder(decode, data, decoded_nmea, caplog)
    # check concatenated nmea if multiline
    assert  "'nmea': '\\\\g:1-2-1604,s:rORBCOMM008,c:1418169601,T:2014-12-10 00.00.01*37\\\\!AIVDM,2,1,6,A,53@o0E000001Q0CG37U8u<Tp4q@D00000000000018330400000000000000,0*63\\n\\\\g:2-2-1604,s:rORBCOMM008,c:1418169601,T:2014-12-10 00.00.01*34\\\\!AIVDM,2,2,6,A,00000000008,2*2A\\n'" in result
