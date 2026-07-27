# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
from genlayer import *
from genlayer import allow_storage
from dataclasses import dataclass
import json


@allow_storage
@dataclass
class Verification:
    owner: Address
    status: u256  # 0=pending, 1=verified, 2=rejected
    timestamp: u256


class SocialIdentity(gl.Contract):
    requests: TreeMap[u256, Verification]
    request_data: TreeMap[u256, str]
    user_requests: TreeMap[Address, DynArray[u256]]
    next_id: u256

    def __init__(self):
        self.next_id = u256(1)

    @gl.public.write
    def request(self):
        pid = self.next_id
        self.requests[pid] = Verification(
            owner=gl.message.sender_address,
            status=u256(0),
            timestamp=u256(0),
        )
        self.request_data[pid] = ""
        existing = self.user_requests.get(gl.message.sender_address)
        if existing is None:
            existing = DynArray[u256]()
        existing.append(pid)
        self.user_requests[gl.message.sender_address] = existing
        self.next_id += u256(1)

    @gl.public.write
    def verify(self, request_id: u256):
        r = self.requests.get(request_id)
        if r is None:
            raise UserError("not found")
        if r.owner != gl.message.sender_address:
            raise UserError("not your request")
        if r.status != u256(0):
            raise UserError("already processed")

        data_raw = gl.storage.copy_to_memory(self.request_data[request_id])
        if not data_raw:
            raise UserError("no data")

        parts = data_raw.split("|")
        if len(parts) < 3:
            raise UserError("invalid data")
        handle = parts[0]
        tweet_url = parts[1]
        wallet = parts[2]

        def fetch_tweet():
            resp = gl.nondet.web.get(tweet_url)
            return resp.body.decode("utf-8")

        def validate_tweet(leader_res):
            if not isinstance(leader_res, gl.vm.Return):
                return False
            return True

        content = gl.vm.run_nondet_unsafe(fetch_tweet, validate_tweet)
        if content is None:
            r.status = u256(2)
            self.requests[request_id] = r
            return

        prompt = (
            f"You are verifying social identity.\n"
            f"User claims wallet: {wallet}\n"
            f"Twitter handle: @{handle}\n"
            f"Tweet content: {content}\n"
            f'Return JSON: {{"contains_wallet":bool,"match":bool}}'
        )

        def evaluate():
            return gl.nondet.exec_prompt(prompt)

        decision = gl.eq_principle.prompt_comparative(
            evaluate, "Validators must agree on wallet verification"
        )

        try:
            raw = str(decision).strip()
            raw = (raw.removeprefix("```json")
                      .removeprefix("```")
                      .removesuffix("```")
                      .strip())
            data = json.loads(raw)
            if data.get("contains_wallet") and data.get("match"):
                r.status = u256(1)
            else:
                r.status = u256(2)
        except Exception:
            r.status = u256(2)

        r.timestamp = u256(int(__import__("time").time()))
        self.requests[request_id] = r

    @gl.public.view
    def get(self, request_id: u256) -> str:
        r = self.requests.get(request_id)
        if r is None:
            return "not found"
        status_str = ["pending", "verified", "rejected"][int(r.status)]
        return f"status={status_str}|owner={r.owner.as_hex}"

    @gl.public.view
    def my_requests(self) -> str:
        arr = self.user_requests.get(gl.message.sender_address)
        if arr is None:
            return "empty"
        return ",".join(str(int(x)) for x in arr)
