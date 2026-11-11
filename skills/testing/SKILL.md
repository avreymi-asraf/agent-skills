---
name: testing
description: Decides what to test and how, favoring a small set of meaningful tests over many trivial unit tests. Covers running code directly to check it, boundary and end-to-end component tests, integration tests between modules, tests of external interactions (APIs, model endpoints, databases, files), and when a unit test is justified. Use whenever writing, adding, reviewing, or pruning tests, setting up a test suite, or when tempted to add a unit test for a new function.
---

<testing>
Few tests, each one meaningful. A test exists only if it protects something the project's purpose depends on. Agents tend to generate piles of unit tests that check trivial functions; this skill stops that and points the effort at the places where systems actually break: component boundaries, the connections between parts, and the edges with external systems.

### Topics Covered
- **Use [Run-Instead-of-Test]** to check new code by executing it, not by writing a test file.
- **Use [What-to-Test]** for the priority order: boundaries, connections, external interactions.
- **Use [External-Interactions]** for API / endpoint / database test patterns.
- **Use [When-Unit-Tests-Are-Justified]** for the narrow exception.
- **Use [Suite-Shape]** for layout, speed, and keeping the suite fast enough to run in every round.
- **Use [Anti-Patterns]** to recognize and delete pointless tests.

Connected skills: prerequisite `coding-principles` (code is written first); companion `notebook-observability` and `code-as-tools` (where running code to check it happens); successor `experiment-lab-loop` (the suite is run during an experiment's rounds). Lab-wide policy lives in `CODE-STANDARDS.md` §6.
</testing>

<Run-Instead-of-Test>
To confirm a function works, run it: `uv run python -c ...`, a small `uv run` script, or a notebook cell that imports the real code. Give it realistic input, look at the output, try one or two awkward inputs. That check is part of writing the code and leaves no test file behind.

Write a test only when the check guards something that could silently break later and that matters to the project (see [What-to-Test]).
</Run-Instead-of-Test>

<What-to-Test>
In priority order:

1. **Boundaries / end-to-end.** Drive a whole component, or the whole system, through its public entry point with realistic input and assert on the outcome that matters (output shape, key values, side effects). One such test replaces dozens of unit tests.
2. **Connections between parts.** Data handed from one module to the next, config loading and wiring (does config X actually select component Y?), and the contracts between parts (schemas, types, file formats).
3. **External interactions.** Every edge with an outside system (see [External-Interactions]).
4. **Intricate logic.** Only via [When-Unit-Tests-Are-Justified].

Before writing a test, ask: *what failure that matters would this catch?* If there is no good answer, don't write it.
</What-to-Test>

<External-Interactions>
External edges are where real failures happen; test them thoroughly.

- **Contract:** the request we build and the response we parse match the real API shape.
- **Failure handling:** errors (4xx/5xx), timeouts, rate limits, retries, malformed or empty responses, partial data.
- **Fast mode:** use recorded real responses (fixtures saved from an actual call) or a small fake. Never hand-invent response shapes.
- **Live mode:** a separate suite marked `@pytest.mark.live`, skipped by default, run on demand (`uv run pytest -m live`) to catch drift in the real service.
- Secrets come from `.env`; tests never print or store them.
</External-Interactions>

<When-Unit-Tests-Are-Justified>
Unit tests are the exception, reserved for functions with intricate logic: parsers, scoring/metric functions, state machines, non-trivial algorithms, tricky edge-case handling.

When one is justified, test it **comprehensively**: the full range of cases, edge cases, invalid inputs. `pytest.mark.parametrize` keeps it compact. A half-tested complex function is worse than an honest gap.
</When-Unit-Tests-Are-Justified>

<Suite-Shape>
```
tests/
├── test_<component>_e2e.py      # boundary tests, one file per component/flow
├── test_integration_<a>_<b>.py  # connections between parts
├── test_<service>_api.py        # external interactions (+ fixtures/)
├── test_<logic>_unit.py         # only for justified intricate logic
└── fixtures/                    # recorded real responses, small sample inputs
```
- The default run (`uv run pytest -q`, no live tests) must be small and fast; it is what an experiment runs in every round.
- Tests check correctness; the final evaluation (`evaluate.py`) checks quality. Don't put metric thresholds in tests.
</Suite-Shape>

<Anti-Patterns>
Delete or don't write:
- Tests of trivial functions, getters, simple wrappers, dataclass constructors.
- Tests that restate the implementation (asserting the code does what the code literally says).
- Tests made almost entirely of mocks that verify call order instead of behavior.
- One test per function "for coverage". Coverage is not a goal.
- Snapshot tests of large outputs nobody reviews.

Rule of thumb: if a test cannot fail for a meaningful reason, it is noise.
</Anti-Patterns>

<examples>
**Task:** add an LLM-based `ToolSelector` to an agent repo.

1. Write `LLMToolSelector`. Check it by running it in a notebook against three real tasks and reading the selected tools. No unit test.
2. Its helper `parse_tool_choice(text)` handles messy model output (JSON in markdown fences, trailing text, wrong case). That is intricate logic, so add `test_tool_choice_parser_unit.py` with parametrized cases covering every format seen in traces, plus garbage input.
3. Add one boundary test: `AgentRunner` with `configs/llm_selector.yaml` runs one episode on a fixture task and returns a final answer with a valid trace. This also checks the config wiring.
4. Add an external test: the model client with a recorded response, a recorded 429, and a timeout. Also add one `@pytest.mark.live` test that hits the real endpoint.

**Mistake:** the agent also wrote `test_selector_init`, `test_selector_has_name`, and `test_get_tools_returns_list`. Delete them: none can fail for a meaningful reason.

Result: 4 test files, all meaningful, and the suite runs in seconds.
</examples>
