# Preventing LLM Hallucinations in Aria

The recent issue where the LLM "pretended" to send an email without actually doing it is a classic example of **Hallucination**. Here is how we fixed it and how to prevent it in the future.

## 1. The "Router" Pattern (Deterministic vs. Probabilistic)

**The Problem:**
LLMs are *probabilistic*. When you asked "Yes", the LLM predicted that the most likely response to "Do you want to send it?" is "Okay, I sent it." It didn't know it was supposed to run code.

**The Solution (What we did):**
We implemented **Deterministic Routing**.
Instead of sending *everything* to the LLM, we check the system state first.

```python
# backend_fastapi.py

# 1. Check State (Deterministic)
if aria.command_processor.pending_email:
    # FORCE the logic to handle the confirmation
    # Do NOT let the LLM decide what to do
    process_command("yes") 

# 2. Only if no state exists, ask the LLM (Probabilistic)
else:
    llm.ask(user_input)
```

**Rule:** Never rely on the LLM to "decide" to run a critical action based on a vague input like "Yes". Use code to trap that state.

## 2. State Machines

We treat the application as a **State Machine**.
- **State: Idle** -> User says "Send email" -> **State: Drafting**
- **State: Drafting** -> User says "Yes" -> **Action: Send Email** -> **State: Idle**

By tracking `pending_email` (the state), we know *exactly* what "Yes" means. We don't need the LLM to guess.

## 3. Tool/Function Calling (For Future)

Currently, we use a "Classifier" + "Brain" approach.
A more advanced method is **Function Calling** (available in GPT-4).
- You define a tool: `send_email(to, subject, body)`
- You force the LLM to output a *JSON object* calling that tool, instead of text.
- The code executes the tool and gives the *result* back to the LLM.
- The LLM then says "I sent it" *only after* seeing the tool's success result.

## 4. Verification Loops

Always make the LLM "read" the result of the code.
- **Bad:** LLM thinks "I will send it" -> Output "Sent!"
- **Good:** Code sends email -> Returns `Success: ID 123` -> LLM reads `Success` -> Output "Sent!"

In our fix, `process_command` handles the sending and *then* tells the TTS to speak "Email sent". The LLM isn't even involved in the final confirmation message, which is the safest way.
