import { compare } from "./comparator.js";
import { Match, PriceRelation } from "./models.js";

const setMatch = (guess, candidate, expected) => !guess.size || !candidate.size || ([...guess].some((value) => candidate.has(value)) ? Match.MATCH : Match.NO_MATCH) === expected;
const boolMatch = (guess, candidate, expected) => guess === null || candidate === null || (guess === candidate ? Match.MATCH : Match.NO_MATCH) === expected;
const priceMatch = (guess, candidate, expected) => guess === null || candidate === null || (guess === candidate ? PriceRelation.EQUAL : candidate < guess ? PriceRelation.LOWER : PriceRelation.HIGHER) === expected;

export function filterCandidates(candidates, guess, feedback) {
  return candidates.filter((candidate) => boolMatch(guess.tradeable, candidate.tradeable, feedback.tradeable)
    && priceMatch(guess.price, candidate.price, feedback.price)
    && boolMatch(guess.equipment_slot, candidate.equipment_slot, feedback.equipment_slot)
    && setMatch(guess.regions, candidate.regions, feedback.region)
    && setMatch(guess.categories, candidate.categories, feedback.category)
    && setMatch(guess.sources, candidate.sources, feedback.source)
    && (guess.name === null || candidate.name === null || (guess.name === candidate.name ? Match.MATCH : Match.NO_MATCH) === feedback.name));
}

const isHard = (item) => item.tradeable === false && (item.equipment_slot === null || item.equipment_slot === "-");
const hardBucketSize = (item, pool) => {
  if (!isHard(item) || item.sources.size !== 1) return 0;
  const source = item.sources.values().next().value;
  return pool.filter((candidate) => isHard(candidate) && candidate.sources.size === 1 && candidate.sources.has(source)
    && (!item.regions.size || !candidate.regions.size || [...item.regions].some((region) => candidate.regions.has(region)))
    && candidate.name !== item.name).length;
};
const keyFor = (feedback) => [feedback.tradeable, feedback.price, feedback.equipment_slot, feedback.region, feedback.category, feedback.source, feedback.name].join("|");
const rankBefore = (left, right) => left.some((value, index) => value !== right[index] && value < right[index] && left.slice(0, index).every((prior, priorIndex) => prior === right[priorIndex]));

export class Solver {
  constructor(candidates) { this.allCandidates = [...candidates]; this.reset(); }
  applyFeedback(guess, feedback) { this.candidates = filterCandidates(this.candidates, guess, feedback); this.guessCount += 1; this.cache.clear(); }
  reset() { this.candidates = [...this.allCandidates]; this.guessCount = 0; this.cache = new Map(); }
  recommendNextGuess({ guessPool = null, answerPool = null, maxGuesses = 2000 } = {}) {
    const current = guessPool === null && answerPool === null;
    const cacheKey = `${this.guessCount}:${maxGuesses}`;
    if (current && this.cache.has(cacheKey)) return this.cache.get(cacheKey);
    let guesses = [...(guessPool || this.candidates)];
    const answers = answerPool || this.candidates;
    // Cloggle's opening guess is intentionally limited to untradeable, unequippable items.
    if (current && this.guessCount === 0) guesses = guesses.filter(isHard);
    if (maxGuesses !== null && guesses.length > maxGuesses) guesses = guesses.slice(0, maxGuesses);
    if (!guesses.length || !answers.length) return [null, Infinity];
    const weights = new Map(guesses.map((item) => [item, hardBucketSize(item, answers)]));
    guesses.sort((a, b) => (weights.get(b) - weights.get(a)) || a.name.localeCompare(b.name));
    let best = null; let bestRank = null;
    for (const guess of guesses) {
      const partitions = new Map();
      for (const answer of answers) { const key = keyFor(compare(guess, answer)); partitions.set(key, (partitions.get(key) || 0) + 1); }
      const expected = [...partitions.values()].reduce((total, size) => total + (size / answers.length) * size, 0);
      const weight = weights.get(guess); const hard = isHard(guess);
      const rank = [weight > 0 || hard ? 0 : 1, -weight, hard ? 0 : 1, expected];
      if (!bestRank || rankBefore(rank, bestRank)) { best = guess; bestRank = rank; }
    }
    const result = [best, best ? bestRank[3] : Infinity];
    if (current) this.cache.set(cacheKey, result);
    return result;
  }
}
