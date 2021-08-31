from automata import StateMachine


def main():
    nfa = StateMachine.read_nfa()
    dfa = nfa.to_dfa()

    new_dfa_state_temp = "new DFA state:  {new_state}" + ' ' * 4 + "-->  {old_state}"

    print(f"reading NFA ... done .\n\n"
          "creating corresponding DFA ...\n" +
          '\n'.join((
              new_dfa_state_temp.format(**{
                  field: value

                  for field, value in zip(
                      ("new_state", "old_state"),
                      (new_state, '{' + ','.join((str(state) for state in old_state)) + '}')
                  )
              }) for new_state, old_state in dfa.states.items()
          )) +
          "\ndone.\n\n"
          "final DFA:\n"
          f"Initial State:{' ' * 4}{dfa.start_state}\n"
          f"Final States:{' ' * 6}{'{' + ','.join(dfa.accept_states) + '}'}\n"
          f"Total States:{' ' * 6}{len(dfa.trans)}\n"
          f"State  {(' ' * 8).join(dfa.alphabet)}\n" +
          '\n'.join((
              f"{state}{' ' * 8}" + (' ' * 10).join((
                  '{' + f'{dest_state}' + '}'
                  for dest_state in dest_states.values()
                ))
              for state, dest_states in dfa.trans.items()
          )))


if __name__ == '__main__':
    main()
