"""Aggregate behavioural response to a charge (component 3).

The share of chargeable crossings removed at the reference price is calibrated
to the observed international band (config/assumptions.yaml: calibration). A
constant-elasticity curve, D1 = D0 * ((c0 + p) / c0) ** e, moves the response
along prices; c0 is solved so the curve passes through the calibration point.

The removed share is then split into responses. Rerouting is NOT applied here:
SUMO produces it by routing the remaining drivers on travel time plus toll.
Only the non-reroute responses (switch mode, change time, change destination
or cancel/combine, professional traffic) take vehicles off the network.
"""

from dataclasses import dataclass

import yaml

from cordon import CONFIG


def load_assumptions():
    return yaml.safe_load((CONFIG / "assumptions.yaml").read_text())


def solve_c0(elasticity, target_reduction, ref_price):
    """Cost base c0 such that ((c0 + ref) / c0) ** e == 1 - target."""
    ratio = (1 - target_reduction) ** (1 / elasticity)
    return ref_price / (ratio - 1)


def removed_share(price, c0, elasticity):
    if price <= 0:
        return 0.0
    return 1 - ((c0 + price) / c0) ** elasticity


@dataclass
class Response:
    case: str
    c0: float
    elasticity: float
    composition: dict  # non-reroute responses, normalised to sum to 1
    reroute_share: float

    def offnetwork_share(self, price):
        """Share of chargeable vehicles that leave the AM car network at this price."""
        return removed_share(price, self.c0, self.elasticity) * (1 - self.reroute_share)


def response_for(case="base", a=None):
    a = a or load_assumptions()
    cal = a["calibration"]["observed_band_at_reference_price"]
    key = {"base": "value", "low": "low", "high": "high"}[case]
    target = cal["crossing_reduction_at_reference"][key]
    e = cal["elasticity_for_price_curve"]["value"]
    c0 = solve_c0(e, target, cal["reference_price_cad"]["value"])
    comp = a["behaviour"]["response_composition_of_removed_trips"]
    reroute = comp["reroute_around_zone"]["value"]
    others = {k: v["value"] for k, v in comp.items()
              if isinstance(v, dict) and k != "reroute_around_zone"}
    total = sum(others.values())
    return Response(case, c0, e, {k: v / total for k, v in others.items()}, reroute)


if __name__ == "__main__":
    for case in ("low", "base", "high"):
        r = response_for(case)
        print(f"{case:5} c0=${r.c0:6.2f}  removed@$3={removed_share(3, r.c0, r.elasticity):.3f}"
              f"  @$6.29={removed_share(6.29, r.c0, r.elasticity):.3f}  @$12.58={removed_share(12.58, r.c0, r.elasticity):.3f}"
              f"  off-network@$12.58={r.offnetwork_share(12.58):.3f}")
    print({k: round(v, 3) for k, v in response_for().composition.items()})
