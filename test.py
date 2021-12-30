from lib import convert_utc_to_usertz, convert_to_utc, checksiswa, checkuser
from datetime import datetime
from pytz import timezone

format_time = '%d/%m/%Y %H:%M'

def test_convert_to_utc():
    assert convert_to_utc(datetime.now(timezone('Asia/Jakarta'))).strftime(format_time) == datetime.utcnow().strftime(format_time)

def test_convert_utc_to_usertz():
    assert convert_utc_to_usertz(datetime.utcnow().strftime(format_time), "WIB") == datetime.now(timezone('Asia/Jakarta')).strftime(format_time)

def test_siswa_success():
    assert checksiswa(1201809639) == True

def test_siswa_fail():
    assert checksiswa(1234567890) == False

def test_checkuser_success():
    assert checkuser(1201809639) == True

def test_checkuser_fail():
    assert checkuser(1255213541) == False