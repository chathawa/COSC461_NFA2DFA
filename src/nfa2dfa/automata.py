from __future__ import annotations

from itertools import chain
from sys import stdin
from typing import Tuple, Union, Dict, Generator
import re


class StateMachine:
    @classmethod
    def read_nfa(cls) -> StateMachine:
        start_state = int(stdin.readline().strip().split(':')[1].strip())
        accept_states = tuple(
            int(state.strip()) for state in re.match(
                r'\{(.*)\}',
                stdin.readline().split(':')[1].strip()
            ).group(1).split(',')
        )
        total_states = int(stdin.readline().strip().split(':')[1].strip())
        alphabet = ''.join((
            symbol for symbol in stdin.readline().strip().split(' ') if symbol and symbol != 'State'
        ))
        trans: Dict[
            int,                 # The state to transition from
            Dict[
                str,             # The symbol to be read in
                Tuple[int, ...]  # States that can be transitioned to on this symbol, from this state
            ]
        ] = {}

        for state in range(1, total_states + 1):
            trans[state] = {}

        for line in stdin.readlines():
            words = (s for s in line.strip().split(' ') if s)
            state_trans = trans[int(next(words))]
            for symbol, states in zip(alphabet, words):
                state_trans[symbol] = tuple(
                    int(state.strip()) for state in re.match(
                        r'\{(.*)\}',
                        states
                    ).group(1).split(',') if state
                )

        return StateMachine(
            alphabet,
            {n: n for n in range(1, total_states + 1)},
            start_state,
            accept_states,
            trans
        )

    @staticmethod
    def _assert_unique_symbols(alphabet: str):
        for index, symbol in enumerate(alphabet):
            try:
                assert symbol not in alphabet[:index] + alphabet[index + 1:]
            except AssertionError:
                raise ValueError(
                    f"every symbol in the alphabet should be unique; "
                    "found two occurrences of '{symbol}' in \"{alphabet}\""
                )

    def __init__(
            self,
            alphabet: str,
            states: Dict,
            start_state: Union[int, Tuple],
            accept_states: Tuple,
            trans: Dict
    ):
        self._assert_unique_symbols(alphabet)

        self.alphabet = alphabet
        self.states = states
        self.start_state = start_state
        self.accept_states = accept_states
        self.trans = trans

    def _adjacent_states(self, symbol: str, state: Union[int, Tuple]) -> Generator[Union[int, Tuple], None, None]:
        return (
            dest_state

            for read_symbol, dest_states in self.trans[state].items()
            for dest_state in dest_states
            if read_symbol == symbol
        )

    def _contains_accept_state(self) -> Generator[Tuple]:
        return (
            dest_states

            for state_trans in self.trans.values()
            for dest_states in state_trans.values()
            for dest_state in dest_states
            if dest_state in self.accept_states
        )

    def _epsilon_closure(self, *states: Union[int, Tuple]) -> Tuple:
        stack, result = (list(states) for _ in range(2))
        while stack:
            state = stack.pop()
            for adj_state in self._adjacent_states('E', state):
                if adj_state not in result:
                    result.append(adj_state)
                    stack.append(adj_state)
        return tuple(result)

    def _move(self, symbol: str, *states: Union[int, Tuple]):
        return tuple(chain(
            *(self.trans[state][symbol] for state in states)
        ))

    def to_dfa(self) -> StateMachine:
        old_start_state = self._epsilon_closure(self.start_state)
        old_accept_states = self._contains_accept_state()

        trans = {}
        new_start_state, new_accept_states = None, []
        states = [(False, old_start_state)]

        while True:
            index, marked, state = None, True, None
            for index, (marked, state) in enumerate(states):
                if not marked:
                    break
            if marked:
                break

            states[index] = (True, state)

            for a in (symbol for symbol in self.alphabet if symbol != 'E'):
                unmarked_state = self._epsilon_closure(*self._move(a, *state))
                if unmarked_state not in (state for _, state in states):
                    states.append((False, unmarked_state))
                try:
                    state_trans = trans[index]
                except KeyError:
                    trans[index] = state_trans = {}
                state_trans[a] = unmarked_state

        for index, (_, state) in enumerate(states):
            if state == old_start_state:
                new_start_state = index + 1

            if state in old_accept_states and index + 1 not in new_accept_states:
                new_accept_states.append(index)

        return StateMachine(
            ''.join((symbol for symbol in self.alphabet if symbol != 'E')),
            {index + 1: state for index, (_, state) in enumerate(states)},
            new_start_state,
            tuple(new_accept_states),
            trans
        )
