export const PriceRelation = Object.freeze({ LOWER: "lower", EQUAL: "equal", HIGHER: "higher" });
export const Match = Object.freeze({ MATCH: "match", NO_MATCH: "no_match" });

export class Item {
  constructor({ id = null, name = null, price = null, tradeable = null, equipment_slot = null, categories = [], sources = [], regions = [] } = {}) {
    this.id = id;
    this.name = name;
    this.price = price;
    this.tradeable = tradeable;
    this.equipment_slot = equipment_slot;
    this.categories = new Set(categories || []);
    this.sources = new Set(sources || []);
    this.regions = new Set(regions || []);
  }
}

export class Feedback {
  constructor({ tradeable = Match.NO_MATCH, price = PriceRelation.EQUAL, equipment_slot = Match.NO_MATCH, region = Match.NO_MATCH, category = Match.NO_MATCH, source = Match.NO_MATCH, name = Match.NO_MATCH } = {}) {
    Object.assign(this, { tradeable, price, equipment_slot, region, category, source, name });
  }
}
