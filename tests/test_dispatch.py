"""Exercise the actual pinned runner resolver, not only direct Python methods."""
import ast
import sys
import typing
from pathlib import Path
from types import SimpleNamespace

import pytest
from genlayer_py.abi import calldata
from genlayer_py.contracts import actions
from genlayer_py.contracts.utils import make_calldata_object

from studionet_compat import RUNNER, legacy_calldata_object, pinned_runner_calldata


def resolver(contract):
    from genlayer.gl.genvm_contracts import __known_contract__
    import genlayer.py.get_schema as schema
    import genlayer.py.public_abi as abi
    sdk = Path(sys.modules["genlayer"].__file__).parent.parent
    runner = sdk / "_genlayer_runner.py"
    tree = ast.parse(runner.read_text(encoding="utf-8"))
    main = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "_handle_main")
    functions = [n for n in main.body if isinstance(n, ast.FunctionDef) and n.name in {"check_abstracts", "resolve_method"}]
    assert len(functions) == 2
    namespace = {"typing": typing, "MethodResolverInfo": SimpleNamespace,
                 "_get_schema": schema, "ABI": abi, "__known_contract__": __known_contract__}
    exec(compile(ast.Module(body=functions, type_ignores=[]), str(runner), "exec"), namespace)
    return namespace["resolve_method"], __known_contract__


def test_legacy_runner_dispatches_view_and_registration(direct_vm, direct_deploy, direct_owner):
    direct_vm.sender = direct_owner
    contract = direct_deploy("contracts/license_bundle_clearinghouse.py", sdk_version="v0.6.0-rc5")
    resolve, contract_type = resolver(contract)
    context = SimpleNamespace(msg={"is_init": False, "value": 0}, contract_type=contract_type)
    context.cd = calldata.decode(calldata.encode(make_calldata_object(method="get_accounting")))
    # This is precisely the failed .19 -> legacy runner route.
    with pytest.raises(ValueError, match="private method.*__handle_undefined_method__"):
        resolve(context)
    with pinned_runner_calldata(chain_id=61999, runner=RUNNER):
        context.cd = calldata.decode(calldata.encode(actions.make_calldata_object(method="get_accounting")))
        assert resolve(context)(contract._instance)["conserved"] is True
        args = ["dispatch-work", "Attribution illustration", "CC-BY-4.0 style: share and adapt for any purpose with attribution and a license link.", 30]
        context.cd = calldata.decode(calldata.encode(actions.make_calldata_object(method="register_license", args=args)))
        row = resolve(context)(contract._instance, *context.cd["args"])
        assert row["version"] == 1
        assert contract.get_license("dispatch-work") == row
    assert actions.make_calldata_object is make_calldata_object


def test_compatibility_is_scoped_and_preserves_arguments():
    assert legacy_calldata_object("get_balance", ["address"], {"x": 1}) == {
        "method": "get_balance", "args": ["address"], "kwargs": {"x": 1}}
    assert legacy_calldata_object() == {}
    with pytest.raises(ValueError, match="restricted"):
        with pinned_runner_calldata(chain_id=1, runner=RUNNER):
            pass
