---
authors:
---
# Limitations and next steps

This is a concept design produced in a few weeks, and some of its numbers are estimates. We
think it is more useful to be clear about that than to hide it. The most important open
questions are listed below, roughly in order of how much they could change the design.

1. **The energy model.** We have not yet calculated the building's heating demand, so we cannot
   yet say how much of the {{server_heat_mwh}} MWh of server heat is useful, how big the heat
   pump, thermal store and battery need to be, or whether the building is net zero
   ([[The energy balance so far]]). A monthly model of heat loss against server heat and solar
   generation is the single most valuable next step.
2. **The server load.** The {{server_kw}} kW per rack is an assumption. It should be based on
   what the university would actually run in the room, because it drives both the heat supply
   and the largest electricity demand.
3. **Plant prices.** {{unpriced_count}} plant items have no price yet ([[Cost analysis]]).
4. **Real supplier prices.** Every catalogue price should be replaced with a sourced price and
   cited.
5. **Construction cost.** The building structure has not been costed; a published cost per m²
   benchmark would give a first estimate.
6. **The west façade.** Its {{wwr_w}}% glazing is an overheating risk on summer afternoons and
   needs shading or a smaller window area ([[Windows where they help]]).
7. **Embodied carbon.** A simple estimate of the carbon in the main materials, compared with the
   LETI or RIBA targets, would back up the case for timber ([[Targets for the whole building]]).

!!! contribute "Anyone: anything else?"
    Add any other limitation you notice while writing your section, and what would resolve it.
