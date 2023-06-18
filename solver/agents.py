from typing import Dict, List, Optional, Tuple
import openai
import pexpect
from utils import colors

class Prover:
    '''
    Agent that uses coq to generate proofs and a corresponding natural language explanation.
    '''

    def __init__(
        self, 
        goal: str, 
        system_prompt_path: str = 'prompts/prover.txt', 
        model: str = 'gpt-3.5-turbo',
        api_key: str = ''
    ):
        self._model = model 
        self._context: List[Dict[str, str]] = []

        with open(system_prompt_path, 'r') as f:
            system_prompt = f.read()
            self._context.append({'role': 'system', 'content': system_prompt})
        self._context.append({'role': 'user', 'content': goal})

        openai.api_key = api_key

    def _call_model(self, temperature: float = 0.5) -> str:
        response = openai.ChatCompletion.create(
            model=self._model,
            messages=self._context,
            temperature=temperature
        )

        output = response['choices'][0]['message']['content']
        return output

    def step(self, input: Optional[str]) -> Tuple[str, str]:
        if input is not None:
            self._context.append({'role': 'user', 'content': input})

        mistakes = 0
        while mistakes < 3:
            print('>>> Trying to step...')

            model_output = self._call_model()
            self._context.append({'role': 'assistant', 'content': model_output})

            print(colors['YELLOW'] + f'>>> Result: {model_output}' + colors['RESET'])

            if len(model_output.split("```")) == 3: break

            self._context.append({
                'role': 'user', 
                'content': (
                    'Please use the specified format.' 
                    ' Do not leave out the specified natural language and coq code sections.' 
                    ' Do not add any additional unnecessary output.'
                )
            })

            mistakes += 1

        explanation, coq, *_ = model_output.split("```")

        if 'COQ' in explanation.split('\n')[-1]: explanation = '\n'.join(explanation.split('\n')[:-1])
        coq = coq.strip()
        coq = '\n'.join([line for line in coq.split('\n') if '```' not in line])

        print(colors['BLUE'] + f'>>> Explanation: {explanation}' + colors['RESET'])
        print(colors['CYAN'] +  f'>>> Coq: {coq}' + colors['RESET'])
        
        return explanation, coq


class Checker:
    '''
    Stateless agent that evaluates natural language portion of generated proof.
    '''

    def __init__(
        self,
        system_prompt_path: str = 'prompts/checker.txt',
        model: str = 'gpt-3.5-turbo',
        api_key: str = ''
    ):
        self._model = model

        with open(system_prompt_path, 'r') as f:
            self._system_prompt = f.read()

        openai.api_key = api_key

    def check(self, explanation: str) -> Tuple[str, bool]:
        print('>>> Checking natural language...')

        response = openai.ChatCompletion.create(
            model=self._model,
            messages=[
                {'role': 'system', 'content': self._system_prompt},
                {'role': 'user', 'content': explanation}
            ]
        )

        output = response['choices'][0]['message']['content']
        accepted = 'ACCEPTED' in output 

        return output, accepted

class CoqEvaluator():
    '''
    (Non-LLM) Agent that runs coq code with pexpect.
    '''

    def __init__(self):
        self.child = pexpect.spawn('coqtop -emacs')
        self._expect_prompt()

    def evaluate(self, coq: str) -> Tuple[str, bool]:
        self._reset() 
        output = ''
        success = True 

        for line in coq.split('\n'):
            if line == '' or line[0] == '(': continue 

            output = self._send(line)
            output = '\n'.join(output)

            if "Error" in output:
                success = False 
                break

        return output, success

    def _expect_prompt(self) -> int:
        self.child.expect(r"</prompt>$")

    def _send(self, command: str) -> List[str]:
        self.child.sendline(command)
        self._expect_prompt()
        return self.child.before.decode().split('\n')

    def _reset(self): 
        self.child.sendline("Reset Initial.")
        self._expect_prompt()

    def quit(self):
        self.child.sendline("Quit.")
        self.child.expect(pexpect.EOF)
        self.child.close(force=True)

    def __del__(self):
        self.quit()