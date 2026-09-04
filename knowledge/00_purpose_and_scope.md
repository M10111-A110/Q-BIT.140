# Purpose and Scope

This is the curated knowledge base for the Q-BIT AI Guidance component (M5).

Q-BIT's MVP is intentionally bounded around one quantum algorithm: Grover's
Algorithm, together with the prerequisite concepts required to understand it.
The platform is not intended to teach all of quantum computing in the MVP.

The AI should use this material as curated conceptual knowledge. It should
combine this knowledge with structured learner context and, where applicable,
verified simulator results supplied by the quantum engine.

## Component Boundaries

- **M2 — Adaptive Learner Model**: interprets learner evidence and maintains
  learner context.
- **M3 — Quantum Engine**: executes quantum experiments and provides verified
  quantum evidence.
- **M5 — AI Guidance**: explains concepts, interprets learner context, gives
  targeted guidance, and proposes explanations or next-step learning support.
- **M4 — Backend/Integration**: connects components and handles
  persistence/API concerns.

The AI must not invent quantum execution results. If a simulation result is
supplied by the quantum engine, treat it as the authoritative execution
evidence.

## MVP Curriculum Path

Mathematics → Quantum Computing Foundations → Quantum Circuits → Quantum
Gates → Grover's Algorithm → Qiskit / Simulation

Mathematics prerequisites: Linear Algebra, Probability.

The learner should not necessarily be forced through every topic in this
order. The adaptive system can use prerequisite evidence to determine which
concepts need attention.

## Scope Boundary

The following are **not** required as core MVP teaching content unless
introduced for a specific reason:

- Shor's algorithm
- Quantum Fourier Transform
- Variational Quantum Eigensolver
- Quantum error correction
- Full quantum mechanics
- Advanced quantum hardware physics
- Advanced density-matrix formalism
- Advanced mixed-state theory
- Fault-tolerant quantum computing
- Hardware-specific optimization

These may be future curriculum extensions. The MVP should remain focused on
the complete learning loop around Grover's Algorithm and its relevant
prerequisites.
