# Chains
Chains is an abstraction to chain various steps as a runnable.
Actually chains pass an output of one step to the input of another step.

# Types
1. LLM chain
2. Sequential chain - idea is to pass output of one chain to another one
    - type1: SimpleSequentialChain  - single input/output
    - type2: SequentialChain        - multiple input/output
3. Router chain