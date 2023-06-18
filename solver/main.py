from agents import Prover, Checker, CoqEvaluator

prover = Prover('Prove the fundamental theorem of calculus.')
checker = Checker()
evaluator = CoqEvaluator()

feedback = None 
accepted = False 
steps = 0
explanations = []

while not accepted and steps < 3: 
    explanation, coq = prover.step(input=feedback)
    coq_output, coq_success = evaluator.evaluate(coq)

    if not coq_success: 
        feedback = f"Coq error: {coq_output}. \nCheck the Coq code for syntax errors, and try again."
        explanations.append(checker.check(explanation))
    else:
        feedback, accepted = checker.check(explanation)
        explanations.append((feedback, accepted))

    print("\033[92m" + feedback + "\033[0m") 
    if accepted: break

    steps += 1

for i, thing in enumerate(explanations):
    print(i)
    print(thing)