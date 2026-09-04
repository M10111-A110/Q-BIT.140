# Common Misconceptions

The AI should actively avoid reinforcing these misconceptions.

## "A qubit is both 0 and 1 like two classical bits."
Better: A qubit can be in a quantum superposition of computational-basis
states. Measurement produces a classical outcome according to the state's
probabilities.

## "Superposition is just classical randomness."
Better: A quantum superposition contains amplitudes and phase information
that can produce interference. It is not merely a classical probability
distribution.

## "An amplitude is the same thing as probability."
Better: P(x) = |αx|^2. Amplitudes determine measurement probabilities
through squared magnitude.

## "Measurement reveals the complete quantum state."
Better: A single measurement gives a classical outcome. Repeated
measurements can estimate an outcome distribution.

## "Hadamard always produces a 50/50 final result."
Better: Hadamard applied to |0⟩ creates an equal superposition, which gives
50/50 computational-basis measurement probabilities. Later gates can change
the state and therefore the final distribution.

## "The oracle tells the computer the answer."
Better: The oracle marks the desired state, typically through a phase
change. The diffusion step then enables amplitude amplification.

## "Grover always gives the answer with 100% probability."
Better: Grover amplifies the target state's probability. The exact result
depends on the search-space size, number of iterations, oracle, and
execution conditions.

## "More Grover iterations always improve the result."
Better: Grover's amplitude amplification is oscillatory. After an optimal
region, additional iterations can decrease the target probability.

## "Counts are exact probabilities."
Better: Counts are finite-shot observations. Normalized counts provide
empirical probabilities that approximate the underlying distribution.
