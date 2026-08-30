import { readFileSync } from "node:fs";
import { Item } from "../docs/js/models.js";
import { compare } from "../docs/js/comparator.js";
import { filterCandidates } from "../docs/js/solver.js";

const input = JSON.parse(readFileSync(0, "utf8"));
const items = input.items.map((value) => new Item(value));
const guess = items[input.guessIndex];
const feedback = compare(guess, items[input.answerIndex]);
const plain = Object.fromEntries(Object.entries(feedback));
process.stdout.write(JSON.stringify({ feedback: plain, candidateIds: filterCandidates(items, guess, feedback).map((item) => item.id) }));
