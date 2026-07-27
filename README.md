# ProofOfSocial — On-Chain Social Identity Verification

An Intelligent Contract on GenLayer that verifies Twitter identity using AI consensus.

## How it works

1. User calls `request()` to create a verification request
2. A backend API stores the user's Twitter handle, tweet URL, and wallet address in `request_data`
3. User calls `verify(id)` — validators fetch the tweet via `gl.nondet.web` and use LLM consensus to check if the tweet contains the claimed wallet address
4. Status is updated to `verified` or `rejected`

## Deployed on Bradbury

`0xAD3047dB9aAE82F8d66927F22681Ea46eD7313ab`

## Methods

- `request()` — create a new verification request
- `verify(request_id: u256)` — verify the request (only by owner)
- `get(request_id: u256) -> str` — view request status
- `my_requests() -> str` — list your request IDs
