# coding:  utf-8

import datetime
import codecs

def conv_encoding(data, to_enc="utf_8"):
    """
    stringのエンコーディングを変換する
    @param ``data'' str object.
    @param ``to_enc'' specified convert encoding.
    @return str object.
    """
    lookup = ('utf_8', 'euc_jp', 'euc_jis_2004', 'euc_jisx0213',
            'shift_jis', 'shift_jis_2004','shift_jisx0213',
            'iso2022jp', 'iso2022_jp_1', 'iso2022_jp_2', 'iso2022_jp_3',
            'iso2022_jp_ext','latin_1', 'ascii')
    for encoding in lookup:
        try:
            data = data.decode(encoding)
            break
        except:
            pass
    if isinstance(data, unicode):
        return data.encode(to_enc)
    else:
        return data


class TZ(datetime.tzinfo):
  def __init__(self, name, offset):
    self.name_ = name
    self.offset_ = offset
  def utcoffset(self, dt):
    return datetime.timedelta(hours=self.offset_)
  def tzname(self, dt):
    return self.name
  def dst(self, dt):
    return datetime.timedelta(0)

UTC = TZ('UTC', 0)
JST = TZ('JST', 9)

def jst_from_utc(dt):
  return dt.replace(tzinfo=UTC).astimezone(JST)

def utc_from_jst(dt):
  return dt.replace(tzinfo=JST).astimezone(UTC)