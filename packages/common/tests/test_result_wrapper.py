from vaayutrade_common import Result, Ok, Err, AppError, ErrorCode

def test_ok_serialization():
    r = Ok({"hello": "world"})
    j = r.model_dump_json()
    r2 = Result[dict].model_validate_json(j)
    assert r2.ok and r2.value == {"hello":"world"} and r2.error is None

def test_err_serialization():
    e = AppError(code=ErrorCode.RISK_HALT, message="Daily loss cap hit", retryable=False)
    r = Err(e)
    j = r.model_dump_json()
    out = Result.model_validate_json(j)
    assert not out.ok and out.error is not None and out.error.code == ErrorCode.RISK_HALT
