import { Feedback, Match, PriceRelation } from "./models.js";

export const valuesMatch = (guess, answer) => [...guess].some((value) => answer.has(value));

export function compare(guess, answer) {
  let price = PriceRelation.EQUAL;
  if (guess.price !== null && answer.price !== null) {
    price = guess.price === answer.price ? PriceRelation.EQUAL : answer.price < guess.price ? PriceRelation.LOWER : PriceRelation.HIGHER;
  }
  return new Feedback({
    tradeable: guess.tradeable === answer.tradeable ? Match.MATCH : Match.NO_MATCH,
    price,
    equipment_slot: guess.equipment_slot !== null && answer.equipment_slot !== null && guess.equipment_slot === answer.equipment_slot ? Match.MATCH : Match.NO_MATCH,
    region: valuesMatch(guess.regions, answer.regions) ? Match.MATCH : Match.NO_MATCH,
    category: valuesMatch(guess.categories, answer.categories) ? Match.MATCH : Match.NO_MATCH,
    source: valuesMatch(guess.sources, answer.sources) ? Match.MATCH : Match.NO_MATCH,
    name: guess.name === answer.name ? Match.MATCH : Match.NO_MATCH,
  });
}
