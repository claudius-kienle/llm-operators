def describe_predicate(predicate_name, predicate_args):
    """
    Predicates:
    - (knife ?x - small_items)
    - (cutting-board ?x - small_receptacle)
    - (microwave ?x - furniture_appliance)
    - (pan ?x - small_receptacle)
    - (stove-burner ?x - furniture_appliance)
    - (blender ?x - small_receptacle)
    - (sink-basin ?x - furniture_appliance)
    - (cloth ?x - small_items)
    - (carpet ?x - furniture_appliance)
    - (handheld-vacuum ?x - small_items)
    - (garbage-can ?x - furniture_appliance)
    - (at-agent ?a - agent ?y - furniture_appliance)
    - (holding ?a - agent ?x - household_object)
    - (agent-hand-empty ?a - agent)
    - (at-object ?x - household_object ?y - furniture_appliance)
    - (at-receptacle ?x - household_object ?z - small_receptacle)
    - (pickupable ?x - household_object)
    - (stackable ?x - household_object)
    - (object-clear ?x - household_object)
    - (stacked-on ?x - household_object ?y - household_object)
    - (openable ?y - furniture_appliance)
    - (is-open ?y - furniture_appliance)
    - (flat-surface ?y - furniture_appliance)
    - (toggleable ?x - household_object)
    - (is-switched-on ?x - household_object)
    - (sliceable ?x - household_object)
    - (sliced ?x - household_object)
    - (mashed ?x - household_object)
    - (heated ?x - household_object)
    - (receptacle-openable ?z - small_receptacle)
    - (is-receptacle-open ?z - small_receptacle)
    - (washable ?x - household_object)
    - (dirty ?x - household_object)
    - (dirty-surface ?x - furniture_appliance)
    - (is-empty-dust-bin ?v - household_object)

    :param predicate_name: str
    :param predicate_args: Tuple[str]
    :return: Tuple[str, str] - (positive, negative)
    """
    # (knife ?x - small_items)
    if predicate_name == "knife":
        (x,) = predicate_args
        return f"{x} is a knife.", f"{x} is not a knife."
    # (cutting-board ?x - small_receptacle)
    elif predicate_name == "cutting-board":
        (x,) = predicate_args
        return f"{x} is a cutting board.", f"{x} is not a cutting board."
    # (microwave ?x - furniture_appliance)
    elif predicate_name == "microwave":
        (x,) = predicate_args
        return f"{x} is a microwave.", f"{x} is not a microwave."
    # (pan ?x - small_receptacle)
    elif predicate_name == "pan":
        (x,) = predicate_args
        return f"{x} is a pan.", f"{x} is not a pan."
    # (stove-burner ?x - furniture_appliance)
    elif predicate_name == "stove-burner":
        (x,) = predicate_args
        return f"{x} is a stove burner.", f"{x} is not a stove burner."
    # (blender ?x - small_receptacle)
    elif predicate_name == "blender":
        (x,) = predicate_args
        return f"{x} is a blender.", f"{x} is not a blender."
    # (sink-basin ?x - furniture_appliance)
    elif predicate_name == "sink-basin":
        (x,) = predicate_args
        return f"{x} is a sink basin.", f"{x} is not a sink basin."
    # (cloth ?x - small_items)
    elif predicate_name == "cloth":
        (x,) = predicate_args
        return f"{x} is a cloth.", f"{x} is not a cloth."
    # (carpet ?x - furniture_appliance)
    elif predicate_name == "carpet":
        (x,) = predicate_args
        return f"{x} is a carpet.", f"{x} is not a carpet."
    # (handheld-vacuum ?x - small_items)
    elif predicate_name == "handheld-vacuum":
        (x,) = predicate_args
        return f"{x} is a handheld vacuum.", f"{x} is not a handheld vacuum."
    # (garbage-can ?x - furniture_appliance)
    elif predicate_name == "garbage-can":
        (x,) = predicate_args
        return f"{x} is a garbage can.", f"{x} is not a garbage can."
    # (at-agent ?a - agent ?y - furniture_appliance)
    elif predicate_name == "at-agent":
        (a, y) = predicate_args
        return f"Agent {a} is at {y}.", f"Agent {a} is not at {y}."
    # (holding ?a - agent ?x - household_object)
    elif predicate_name == "holding":
        (a, x) = predicate_args
        return f"Agent {a} is holding {x}.", f"Agent {a} is not holding {x}."
    # (agent-hand-empty ?a - agent)
    elif predicate_name == "agent-hand-empty":
        (a,) = predicate_args
        return f"Agent {a}'s hand is empty.", f"Agent {a}'s hand is not empty."
    # (at-object ?x - householdObject ?y - furnitureAppliance)
    elif predicate_name == "at-object":
        x, y = predicate_args
        return f"Object {x} is at {y}.", f"Object {x} is not at {y}."
    # (at-receptacle ?x - household_object ?z - small_receptacle)
    elif predicate_name == "at-receptacle":
        x, z = predicate_args
        return f"Object {x} is in/at receptacle {z}.", f"Object {x} is not in/at receptacle {z}."
    # (pickupable ?x - household_object)
    elif predicate_name == "pickupable":
        (x,) = predicate_args
        return f"Object {x} is pickupable.", f"Object {x} is not pickupable."
    # (stackable ?x - household_object)
    elif predicate_name == "stackable":
        (x,) = predicate_args
        return f"Object {x} is stackable.", f"Object {x} is not stackable."
    # (object-clear ?x - household_object)
    elif predicate_name == "object-clear":
        (x,) = predicate_args
        return f"Object {x} is clear.", f"Object {x} is not clear."
    # (stacked-on ?x - household_object ?y - household_object)
    elif predicate_name == "stacked-on":
        x, y = predicate_args
        return f"Object {x} is stacked on {y}.", f"Object {x} is not stacked on {y}."
    # (openable ?y - furniture_appliance)
    elif predicate_name == "openable":
        (y,) = predicate_args
        return f"{y} is openable.", f"{y} is not openable."
    # (is-open ?y - furniture_appliance)
    elif predicate_name == "is-open":
        (y,) = predicate_args
        return f"{y} is open.", f"{y} is not open."
    # (flat-surface ?y - furniture_appliance)
    elif predicate_name == "flat-surface":
        (y,) = predicate_args
        return f"{y} has a flat surface.", f"{y} does not have a flat surface."
    # (toggleable ?x - household_object)
    elif predicate_name == "toggleable":
        (x,) = predicate_args
        return f"{x} is toggleable.", f"{x} is not toggleable."
    # (is-switched-on ?x - household_object)
    elif predicate_name == "is-switched-on":
        (x,) = predicate_args
        return f"{x} is switched on.", f"{x} is not switched on."
    # (sliceable ?x - household_object)
    elif predicate_name == "sliceable":
        (x,) = predicate_args
        return f"{x} is sliceable.", f"{x} is not sliceable."
    # (sliced ?x - household_object)
    elif predicate_name == "sliced":
        (x,) = predicate_args
        return f"{x} is sliced.", f"{x} is not sliced."
    # (mashed ?x - household_object)
    elif predicate_name == "mashed":
        (x,) = predicate_args
        return f"{x} is mashed.", f"{x} is not mashed."
    # (heated ?x - household_object)
    elif predicate_name == "heated":
        (x,) = predicate_args
        return f"{x} is heated.", f"{x} is not heated."
    # (receptacle-openable ?z - small_receptacle)
    elif predicate_name == "receptacle-openable":
        (z,) = predicate_args
        return f"Receptacle {z} is openable.", f"Receptacle {z} is not openable."
    # (is-receptacle-open ?z - small_receptacle)
    elif predicate_name == "is-receptacle-open":
        (z,) = predicate_args
        return f"Receptacle {z} is open.", f"Receptacle {z} is not open."
    # (washable ?x - household_object)
    elif predicate_name == "washable":
        (x,) = predicate_args
        return f"{x} is washable.", f"{x} is not washable."
    # (dirty ?x - household_object)
    elif predicate_name == "dirty":
        (x,) = predicate_args
        return f"{x} is dirty.", f"{x} is not dirty."
    # (dirty-surface ?x - furniture_appliance)
    elif predicate_name == "dirty-surface":
        (x,) = predicate_args
        return f"Surface of {x} is dirty.", f"Surface of {x} is not dirty."
    # (is-empty-dust-bin ?v - household_object)
    elif predicate_name == "is-empty-dust-bin":
        (v,) = predicate_args
        return f"Dust bin of {v} is empty.", f"Dust bin of {v} is not empty."
    else:
        raise ValueError(f"Unknown predicate: {predicate_name}")