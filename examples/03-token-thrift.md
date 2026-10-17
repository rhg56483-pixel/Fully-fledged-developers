# Example 3: the same task, two habits

Task: "the checkout total is wrong in my shop project: find and fix it."

| Step | Costly habit | Thrift habit |
|---|---|---|
| Orient | Open `src/` file by file (tens of thousands of tokens) | `python scripts/repomap.py . --budget 1500`: tree, line counts, symbols (≈1.5k) |
| Locate | Read `cart.js` fully (900 lines) | Search `total`, read lines 212–260 around `calcTotal` (≈60 lines) |
| Reproduce | Paste the entire test log | `npm test 2>&1 \| python scripts/logtrim.py`: the failing assertion plus 2 lines of context |
| Fix | Reprint the whole file | One targeted replace of the faulty line |
| Verify | Run every suite | The suite that covers `calcTotal`, then the journey check |
| Report | Four paragraphs of recap | ≈12 lines: what changed, evidence (`passed`), limits, next step |

The habits change *how much is read and repeated*, never which checks are run. Measure your own numbers with `scripts/tokencount.py`; estimates are ±25 % and are not billing figures.
