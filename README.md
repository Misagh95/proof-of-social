# ProofOfSocial — On-Chain Social Identity Verification

An Intelligent Contract on GenLayer that verifies Twitter identity using AI consensus.

## How it works

1. User calls `request()` to create a verification request and receives a `request_id`
2. The **same user** calls `submitData(request_id, handle, tweet_url, wallet)` — an authorized, on-chain method that supplies the handle, tweet URL, and wallet address (owner-only)
3. User calls `verify(request_id)`:
   - Each validator **independently fetches the tweet body** via `gl.nondet.web`
   - Validators compare the fetched tweet bodies (`validate_tweet`) so a single leader cannot substitute arbitrary content
   - An LLM (`prompt_comparative`) checks the tweet genuinely contains the claimed wallet address and belongs to the claimed handle
4. Status is updated to `verified` or `rejected`

## Consensus Design

| Step | Mechanism | Details |
|------|-----------|---------|
| Tweet fetch | `gl.vm.run_nondet_unsafe` + `validate_tweet` | Every validator independently fetches the tweet body and compares it with the leader's result |
| Content check | `gl.eq_principle.prompt_comparative` | LLM confirms the tweet contains the wallet address and matches the handle |
| Timestamp | `strict_eq` over worldtimeapi | All validators agree on the same verification time |

## Deployed on Bradbury

`0x7A676bbefe0CFEfAdA20c91712d5C42f63821B4A`

Explorer: https://explorer-bradbury.genlayer.com/address/0x7A676bbefe0CFEfAdA20c91712d5C42f63821B4A

## Methods

- `request() -> str` — create a new verification request, returns `request_id`
- `submitData(request_id, handle, tweet_url, wallet)` — authorized owner-only method to set the evidence before verification
- `verify(request_id)` — verify the request (only by owner)
- `get(request_id) -> str` — view request status
- `my_requests() -> str` — list your request IDs
