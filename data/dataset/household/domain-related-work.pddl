(define (domain ai_domain)
    (:requirements :strips :typing :equality :negative-preconditions :disjunctive-preconditions :existential-preconditions :conditional-effects)

    (:types
        agent household_object furniture_appliance - object
        small_receptacle small_items - household_object
    )

    (:predicates
        (knife ?x - small_items)
        (cutting-board ?x - small_receptacle)
        (microwave ?x - furniture_appliance)
        (pan ?x - small_receptacle)
        (stove-burner ?x - furniture_appliance)
        (blender ?x - small_receptacle)
        (sink-basin ?x - furniture_appliance)
        (cloth ?x - small_items)
        (carpet ?x - furniture_appliance)
        (handheld-vacuum ?x - small_items)
        (garbage-can ?x - furniture_appliance)

        ;; Robot location and hand state
        (at-agent ?a - agent ?y - furniture_appliance)
        (holding ?a - agent ?x - household_object)
        (agent-hand-empty ?a - agent)

        ;; Object locations and properties
        (at-object ?x - household_object ?y - furniture_appliance)
        (at-receptacle ?x - household_object ?z - small_receptacle)
        (pickupable ?x - household_object)

        ;; Stacking properties
        (stackable ?x - household_object)
        (object-clear ?x - household_object)
        (stacked-on ?x - household_object ?y - household_object)

        ;; Furniture/appliance properties
        (openable ?y - furniture_appliance)
        (is-open ?y - furniture_appliance)
        (flat-surface ?y - furniture_appliance)

        ;; Small appliance properties
        (toggleable ?x - household_object)
        (is-switched-on ?x - household_object)

        ;; Food preparation properties
        (sliceable ?x - household_object)
        (sliced ?x - household_object)
        (mashed ?x - household_object)
        (heated ?x - household_object)

        ;; Small receptacle properties
        (receptacle-openable ?z - small_receptacle)
        (is-receptacle-open ?z - small_receptacle)

        ;; Cleaning properties
        (washable ?x - household_object)
        (dirty ?x - household_object)
        (dirty-surface ?x - furniture_appliance)
        (is-empty-dust-bin ?v - household_object)
    )

    (:action go-to-a-furniture-piece-or-an-appliance
        :parameters (?a - agent ?x - furniture_appliance ?y - furniture_appliance)
        :precondition (and
            (at-agent ?a ?x)
            (not (= ?x ?y))
        )
        :effect (and
            (not (at-agent ?a ?x))
            (at-agent ?a ?y)
        )
    )

    (:action pick-up-an-object-on-or-in-a-furniture-piece-or-an-appliance
        :parameters (?a - agent ?x - household_object ?y - furniture_appliance)
        :precondition (and
            (at-agent ?a ?y)
            (at-object ?x ?y)
            (pickupable ?x)
            (imply
                (stackable ?x)
                (object-clear ?x))
            (agent-hand-empty ?a)
            (imply
                (openable ?y)
                (is-open ?y))
        )
        :effect (and
            (not (at-object ?x ?y))
            (holding ?a ?x)
            (not (agent-hand-empty ?a))
        )
    )

    (:action put-an-object-on-or-in-a-furniture-piece-or-an-appliance
        :parameters (?a - agent ?x - household_object ?y - furniture_appliance)
        :precondition (and
            (at-agent ?a ?y)
            (holding ?a ?x)
            (pickupable ?x)
            (imply
                (openable ?y)
                (is-open ?y))
        )
        :effect (and
            (not (holding ?a ?x))
            (agent-hand-empty ?a)
            (at-object ?x ?y)
            (when
                (stackable ?x)
                (object-clear ?x))
        )
    )

    (:action stack-objects
        :parameters (?a - agent ?x - household_object ?y - household_object ?z - furniture_appliance)
        :precondition (and
            (holding ?a ?x)
            (at-object ?y ?z)
            (object-clear ?y)
            (flat-surface ?z)
            (stackable ?x)
            (stackable ?y)
            (at-agent ?a ?z)
        )
        :effect (and
            (not (holding ?a ?x))
            (not (object-clear ?y))
            (agent-hand-empty ?a)
            (at-object ?x ?z)
            (object-clear ?x)
            (stacked-on ?x ?y)
        )
    )

    (:action unstack-objects
        :parameters (?a - agent ?x - household_object ?y - household_object ?z - furniture_appliance)
        :precondition (and
            (at-agent ?a ?z)
            (at-object ?x ?z)
            (at-object ?y ?z)
            (pickupable ?x)
            (object-clear ?x)
            (agent-hand-empty ?a)
            (stacked-on ?x ?y)
        )
        :effect (and
            (not (at-object ?x ?z))
            (not (agent-hand-empty ?a))
            (holding ?a ?x)
            (object-clear ?y)
            (not (stacked-on ?x ?y))
        )
    )

    (:action open-a-furniture-piece-or-an-appliance
        :parameters (?a - agent ?y - furniture_appliance)
        :precondition (and
            (at-agent ?a ?y)
            (openable ?y)
            (not (is-open ?y))
            ; (agent_hand_empty)
        )
        :effect (and
            (is-open ?y)
        )
    )

    (:action close-a-furniture-piece-or-an-appliance
        :parameters (?a - agent ?y - furniture_appliance)
        :precondition (and
            (at-agent ?a ?y)
            (openable ?y)
            (is-open ?y)
            ; (agent_hand_empty)
        )
        :effect (and
            (not (is-open ?y))
        )
    )

    (:action toggle-a-small-appliance-on
        :parameters (?a - agent ?x - household_object ?y - furniture_appliance)
        :precondition (and
            (at-agent ?a ?y)
            (at-object ?x ?y)
            ; (agent_hand_empty)
            (not (is-switched-on ?x))
            (toggleable ?x)
        )
        :effect (and
            (is-switched-on ?x)
        )
    )

    (:action toggle-a-small-appliance-off
        :parameters (?a - agent ?x - household_object ?y - furniture_appliance)
        :precondition (and
            (at-agent ?a ?y)
            (at-object ?x ?y)
            (is-switched-on ?x)
            (toggleable ?x)
            ; (agent_hand_empty)
        )
        :effect (and
            (not (is-switched-on ?x))
        )
    )

    (:action slice-objects
        :parameters (?a - agent ?x - household_object ?k - small_items ?y - furniture_appliance ?z - small_receptacle)
        :precondition (and
            (knife ?k)
            (cutting-board ?z)
            (at-agent ?a ?y)
            (at-receptacle ?x ?z)
            (at-object ?z ?y)
            (holding ?a ?k)
            (sliceable ?x)
            (flat-surface ?y)
            (not (sliced ?x))
            (not (mashed ?x))
        )
        :effect (and
            (sliced ?x)
        )
    )

    (:action heat-food-with-a-microwave
        :parameters (?a - agent ?x - household_object ?y - furniture_appliance ?z - small_receptacle)
        :precondition (and
            (microwave ?y)
            (at-agent ?a ?y)
            (at-receptacle ?x ?z)
            (at-object ?z ?y)
            (not (is-open ?y))
            (not (heated ?x))
        )
        :effect (and
            (not (pickupable ?x))
            (heated ?x)
        )
    )

    (:action heat-food-with-pan
        :parameters (?a - agent ?f - household_object ?p - small_receptacle ?s - furniture_appliance)
        :precondition (and
            (pan ?p)
            (stove-burner ?s)
            (at-agent ?a ?s)
            (at-receptacle ?f ?p)
            (at-object ?p ?s)
            ; (agent_hand_empty)
        )
        :effect (and
            (not (pickupable ?f))
            (heated ?f)
        )
    )

    (:action transfer-food-from-one-small-receptacle-to-another
        :parameters (?a - agent ?x - household_object ?y1 - small_receptacle ?y2 - small_receptacle ?z - furniture_appliance)
        :precondition (and
            (at-agent ?a ?z)
            (at-object ?y1 ?z)
            (at-object ?y2 ?z)
            (at-receptacle ?x ?y1)
            (flat-surface ?z)
            (agent-hand-empty ?a)
            (imply
                (stackable ?y1)
                (object-clear ?y1))
            (imply
                (stackable ?y2)
                (object-clear ?y2))
            (imply
                (receptacle-openable ?y1)
                (is-receptacle-open ?y1))
            (imply
                (receptacle-openable ?y2)
                (is-receptacle-open ?y2))
        )
        :effect (and
            (not (at-receptacle ?x ?y1))
            (at-receptacle ?x ?y2)
        )
    )

    (:action puts-an-object-onto-or-into-a-small-receptacle
        :parameters (?a - agent ?x - household_object ?y - furniture_appliance ?z - small_receptacle)
        :precondition (and
            (at-agent ?a ?y)
            (pickupable ?x)
            (flat-surface ?y)
            (holding ?a ?x)
            (at-object ?z ?y)
            (imply
                (stackable ?z)
                (object-clear ?z))
            (imply
                (receptacle-openable ?z)
                (is-receptacle-open ?z))
        )
        :effect (and
            (not (holding ?a ?x))
            (agent-hand-empty ?a)
            (at-receptacle ?x ?z)
        )
    )

    (:action pick-up-an-object-on-or-in-a-small-receptacle
        :parameters (?a - agent ?x - household_object ?y - furniture_appliance ?z - small_receptacle)
        :precondition (and
            (at-agent ?a ?y)
            (at-receptacle ?x ?z)
            (at-object ?z ?y)
            (pickupable ?x)
            (flat-surface ?y)
            (agent-hand-empty ?a)
            (imply
                (stackable ?z)
                (object-clear ?z))
            (imply
                (receptacle-openable ?z)
                (is-receptacle-open ?z))
        )
        :effect (and
            (not (at-receptacle ?x ?z))
            (not (agent-hand-empty ?a))
            (holding ?a ?x)
        )
    )

    (:action open-a-small-receptacle
        :parameters (?a - agent ?x - small_receptacle ?y - furniture_appliance)
        :precondition (and
            (at-agent ?a ?y)
            (at-object ?x ?y)
            (receptacle-openable ?x)
            (flat-surface ?y)
            ; (agent_hand_empty)
            (not (is-receptacle-open ?x))
            (imply
                (stackable ?x)
                (object-clear ?x))
        )
        :effect (and
            (is-receptacle-open ?x)
        )
    )

    (:action close-a-small-receptacle
        :parameters (?a - agent ?x - small_receptacle ?y - furniture_appliance)
        :precondition (and
            (at-agent ?a ?y)
            (at-object ?x ?y)
            (receptacle-openable ?x)
            (is-receptacle-open ?x)
            (flat-surface ?y)
            ; (agent_hand_empty)
            (imply
                (stackable ?x)
                (object-clear ?x))
        )
        :effect (and
            (not (is-receptacle-open ?x))
        )
    )

    (:action mash-food-with-a-blender
        :parameters (?a - agent ?b - small_receptacle ?f - household_object ?y - furniture_appliance)
        :precondition (and
            (blender ?b)
            (at-agent ?a ?y)
            (at-object ?b ?y)
            (at-receptacle ?f ?b)
            (sliced ?f)
            ; (agent_hand_empty)
        )
        :effect (and
            (mashed ?f)
            (not (pickupable ?f))
        )
    )

    (:action wash-an-object
        :parameters (?a - agent ?x - household_object ?y - furniture_appliance)
        :precondition (and
            (sink-basin ?y)
            (at-agent ?a ?y)
            (washable ?x)
            (dirty ?x)
            (holding ?a ?x)
        )
        :effect (and
            (not (dirty ?x))
        )
    )

    (:action wipe-a-surface
        :parameters (?a - agent ?x - furniture_appliance ?c - small_items)
        :precondition (and
            (cloth ?c)
            (at-agent ?a ?x)
            (holding ?a ?c)
            (washable ?c)
            (not (dirty ?c))
            (dirty-surface ?x)
        )
        :effect (and
            (dirty ?c)
            (not (dirty-surface ?x))
        )
    )

    (:action vacuum-a-carpet
        :parameters (?a - agent ?v - small_items ?c - furniture_appliance)
        :precondition (and
            (handheld-vacuum ?v)
            (carpet ?c)
            (holding ?a ?v)
            (at-agent ?a ?c)
            (pickupable ?v)
            (is-empty-dust-bin ?v)
            (dirty-surface ?c)
        )
        :effect (and
            (not (dirty-surface ?c))
            (not (is-empty-dust-bin ?v))
        )
    )

    (:action empty-a-vacuum-cleaner
        :parameters (?a - agent ?v - small_items ?t - furniture_appliance)
        :precondition (and
            (handheld-vacuum ?v)
            (garbage-can ?t)
            (at-agent ?a ?t)
            (holding ?a ?v)
            (not (is-empty-dust-bin ?v))
            (pickupable ?v)
            (imply
                (openable ?t)
                (is-open ?t))
        )
        :effect (and
            (is-empty-dust-bin ?v)
        )
    )
)