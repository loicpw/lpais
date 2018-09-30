#! /usr/bin/env python
# -*- coding: utf-8 -*-
""" create functions to decode AIS message from NMEA lines.

    .. note:: Thanks to **Kurt Schwehr** work on
      `libais <https://github.com/schwehr/libais>`_

       Kurt Schwehr: schwehr@gmail.com, schwehr@google.com

    This library uses `libais <https://github.com/schwehr/libais>`_
    and is largely inspired by **ais.stream** module but decode messages
    on a line by line basis.

    Note the **stats** part has been removed as we believe this should
    be implemented by the user if needed.

    example: ::

        import lpais.ais as ais
        decode = ais.decoder()

        with open(data) as inputs:
            for line in inputs:
                line = line.strip()
                if line:
                    data = decode(line)
                    # data is None if line didn't result in a new message
                    if data:
                        # data is a dictionary containing AIS fields
                        print(data)

    use `keep_nmea` option to keep NMEA data into output dictionary,
    if enabled a '**nmea**' field will contain the NMEA line(s), which
    will be a concatenation of original lines if it's a multiline msg.

    example: ::

        import lpais.ais as ais
        decode = ais.decoder(keep_nmea=True)

        with open(data) as inputs:
            for line in inputs:
                line = line.strip()
                if line:
                    data = decode(line)
                    if data:
                        print('NMEA': data['nmea'])

    .. seealso:: `decoder` for more details
"""

from ais.stream.checksum import isChecksumValid, checksumStr
from ais.stream import parseTagBlock
import ais
import logging

logger = logging.getLogger(__name__)


class AISError(Exception):
    """ base class for custom exceptions.

        initialized with `kw` args that are used to format the
        string representation.

        the base implementation add `description` field from
        **self.description**, the implementation class is then
        likely to define a `description` class attribute.

        the base representation (str) will use the following fields
        from `kw`:

        + 'description' : details above

        + 'line' : the text line on which the exception occured
    """
    description = 'AIS error'

    def __init__(self, **kw):
        self.kw = kw
        self.kw['description'] = self.description

    def __str__(self):
        return '{description}: {line}'.format(**self.kw)


class InvalidChecksumError(AISError):
    description = 'Invalid checksum'


class InvalidChecksumInConstructedError(AISError):
    description = 'Invalid checksum in constructed one-liner'


class NoStationFoundError(AISError):
    description = 'No station found'


class TooFewFieldsError(AISError):
    """ Too few fields.

        the representation will use the following fields from `kw`,
        in addition to the fields used by `AISError`:

        + 'fields' : number of fields
    """
    description = 'Too few fields'

    def __str__(self):
        return ('{description}, got {fields} but needed 6: '
                '{line}'.format(**self.kw))


class MissingTimestampsError(AISError):
    """ Timestamps missing.

        the representation will use the following fields from `kw`,
        in addition to the fields used by `AISError`:

        + 'parts' : parts of the multiline message
    """
    description = 'Timestamps missing'

    def __str__(self):
        return '{description}: {line}, parts: {parts}'.format(**self.kw)


class DifferingTimestampsError(AISError):
    """ Timestamps not all the same.

        the representation will use the following fields from `kw`,
        in addition to the fields used by `AISError`:

        + 'timestamp' : value of the timestamp

        + 'parts' : parts of the multiline message
    """
    description = 'Timestamps not all the same'

    def __str__(self):
        return ('{description} for {timestamp}: {line}, '
                'parts: {parts}'.format(**self.kw))


class OnlyMessageEndError(AISError):
    """ Do not have the preceeding packets for a multiline message.

        the representation will use the following fields from `kw`,
        in addition to the fields used by `AISError`:

        + 'bufferSlot' : information to identify the message
    """
    description = 'Do not have the preceeding packets for'

    def __str__(self):
        return '{description} for {bufferSlot}:\n{line}\n'.format(**self.kw)


class DecodeError(AISError):
    """ Error while decoding AIS.

        the representation will use the following fields from `kw`,
        in addition to the fields used by `AISError`:

        + 'error_type' : error type
        + 'error' : error message
    """
    def __str__(self):
        return ('{description}: {error_type}: {error} ({line})'
                ''.format(**self.kw))


def decoder(*args, keep_nmea=False, handle_err=logger.error, **kwargs):
    """ create a decoder function used to process NMEA lines one by one.

        The created function will take a single text line as input arg
        and return either:

        + `None` if the line didn't result as a new decoded AIS message

          this will be the case if it's a part of a multiline message or
          thie line could not be properly decoded or processed...

        + a `dict` containing all the AIS message's fields.

        The parameters used to create the decoder function are:

        .. seealso:: except for `keep_nmea`, all the parameters are
            forwarded to `normalizer` function.

        + `validate_checksum`: (optional) wether or not to control cs.

        + `allow_unknown` : (optional) allow no station.

        + `window` : (optional) number of seconds to allow the later
          parts of a multiline message to span.

        + `ignore_tagblock_station` : (optional) dont look for station
          in tagblock_station.

        + `treat_ab_equal` : (optional) dont use A or B to identify msgs.

        + `pass_invalid_checksums` : (optional) accept invalid cs.

        + `allow_missing_timestamps` : (optional) accept missing ts.

        + `handle_err` : (optional) called for every exception, default
          is `logger.error`.

        + `keep_nmea` : (optional) keep origin NMEA line(s) and add it
          as 'nmea' field in output dictionary, all NMEA lines will be
          concatenated if multiline message.
    """
    nrml = normalizer(*args, handle_err=handle_err, **kwargs)
    decode_ais = ais.decode

    def decode(line):
        """ decode a single NMEA line, return `None` or AIS `dict`.

            return a `dict` containing the fields if the line resulted
            into a new complete AIS message, `None` otherwise.
        """
        data = nrml(line)

        if data:
            tagblock, line, origline = data
            body = "".join(line.split(",")[5])
            pad = int(line.split("*")[0][-1])
            try:
                res = decode_ais(body, pad)
            except Exception as err:
                handle_err(DecodeError(line=origline.strip(),
                                       error_type=type(err).__qualname__,
                                       error=err))
                return
            res.update(tagblock)
            if keep_nmea:
                res["nmea"] = origline
            return res

    return decode


def normalizer(
    validate_checksum=True,
    allow_unknown=False,
    window=2,
    ignore_tagblock_station=False,
    treat_ab_equal=False,
    pass_invalid_checksums=False,
    allow_missing_timestamps=False,
    handle_err=logger.error,
):
    """ create a function which assembles single or multiline messages.

        The created function will take a single text line as input arg
        and return either:

        + `None` if the line didn't result in a new message

          this will be the case if it's a part of a multiline message or
          thie line could not be properly processed...

        + a tuple (`tagblock`, `line`, `origin`) where `tagblock` is a
          `dict` containing tagblock info, `line` is the complete AIS
          message to decode, `origin` is the original NMEA line(s)
          composed of a concatenation of the lines if it's a multiline
          message.

        .. seealso:: `decoder` for args description
    """
    # Put partial messages in a queue by station so that
    # they can be reassembled
    buffers = {}

    def normalize(origline):
        """ process a single NMEA line, return complete message or None.

            return either (tagblock, line, origin) if a new message is
            complete, None otherwise.
        """
        tagblock, line = parseTagBlock(origline)
        line = line.strip() + "\n"  # Get rid of DOS issues.

        # TODO ???
        if len(line) < 7 or line[3:6] not in ("VDM", "VDO"):
            return tagblock, line, origline

        if validate_checksum and not isChecksumValid(line):
            handle_err(InvalidChecksumError(line=line.strip()))
            if not pass_invalid_checksums:
                return

        fields = line.split(",")
        if len(fields) < 6:
            handle_err(TooFewFieldsError(line=line.strip(),
                                         fields=len(fields)))
            return

        # Total NMEA lines that compose this message [1..9].
        totNumSentences = int(fields[1])
        if 1 == totNumSentences:
            # A single line needs no work, so pass it along.
            return tagblock, line, origline

        # ------------------------------------------------------------ #
        # multiline message                                            #
        # ------------------------------------------------------------ #
        sentenceNum = int(fields[2])  # Msg sequence nbr 1..9 (packetNum)
        payload = fields[5]  # AIS binary data encoded in whacky ways
        timestamp = fields[-1].strip()  # epoch UTC.  Always last field

        station = None  # USCG Receive Stations
        for fld in fields[-1:5:-1]:
            if len(fld) and fld[0] in ("r", "b"):
                station = fld
                break  # Found it so ditch the for loop.

        if ignore_tagblock_station:
            tagblock_station = None
        else:
            tagblock_station = tagblock.get("tagblock_station", None)

        if station is None and allow_unknown:
            station = "UNKNOWN"

        if station is None and tagblock_station is None:
            handle_err(NoStationFoundError(line=line.strip()))
            return

        bufferSlot = (
            tagblock_station,
            station,
            fields[3],
        )  # seqId and Channel make a unique stream
        if not treat_ab_equal:
            bufferSlot += (fields[4],)  # channel id

        newPacket = {
            "payload": payload,
            "timestamp": timestamp,
            "tagblock": tagblock,
            "origline": origline,
        }

        if sentenceNum == 1:
            buffers[bufferSlot] = [newPacket]  # Overwrite any partials
            return

        if totNumSentences > sentenceNum:
            buffers[bufferSlot].append(newPacket)
            return

        # Finished a message
        if bufferSlot not in buffers:
            handle_err(OnlyMessageEndError(line=line, bufferSlot=bufferSlot))
            return

        buffers[bufferSlot].append(newPacket)
        parts = buffers[bufferSlot]  # Now have all the pieces.
        del buffers[bufferSlot]  # remove the used packets

        # Sanity check
        ts1 = None
        for part in parts:
            try:
                ts1 = float(part["timestamp"])
                ts2 = float(timestamp)
            except ValueError:
                try:
                    ts1 = float(part["tagblock"]["tagblock_timestamp"])
                    ts2 = float(tagblock["tagblock_timestamp"])
                except:
                    if allow_missing_timestamps:
                        ts1 = 0
                        ts2 = 0
                    else:
                        handle_err(MissingTimestampsError(
                            line=line.strip(),
                            parts=parts
                        ))
                        return

            if ts1 > ts2 + window or ts1 < ts2 - window:
                handle_err(DifferingTimestampsError(line=line.strip(),
                                                    timestamp=timestamp,
                                                    parts=parts))
                return

        payload = "".join([p["payload"] for p in parts])
        tagblock = {}
        for p in reversed(parts):
            tagblock.update(p["tagblock"])

        # Try to mirror the packet as much as possible...
        # same seqId and channel.
        checksumed_str = ",".join((
                fields[0],
                "1,1",
                fields[3],
                fields[4],
                payload,
                fields[6].split("*")[0] + "*",
        ))

        if ts1 == 0:
            # allowed missing timestamp and it is missing
            out_str = f'{checksumed_str}{checksumStr(checksumed_str)}'
            if len(fields[7:-1]) > 0:
                out_str = f'{out_str},{",".join(fields[7:-1])}'
        else:
            out_str = (f'{checksumed_str}{checksumStr(checksumed_str)},'
                       f'{",".join(fields[7:])}')

        if not isChecksumValid(out_str):
            handle_err(InvalidChecksumInConstructedError(line=line.strip()))

        # TODO: Why do I have to do this last strip?
        out_str = out_str.strip() + "\n"
        origstr = "".join([p["origline"] for p in parts])
        return tagblock, out_str, origstr

    return normalize
