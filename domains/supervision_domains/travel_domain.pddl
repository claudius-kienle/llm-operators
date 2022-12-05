;; Source: https://github.com/SoarGroup/Domains-Planning-Domain-Definition-Language/blob/master/pddl/travel.pddl
(define (domain travel)
    (:requirements :strips)
    (:predicates
        (road ?from ?to)
        (at ?thing ?place)
        (driving ?p ?v)
        (bridge ?from ?to)
        (mobile ?thing)
        (person ?p)
        (vehicle ?v)
    )

    (:action drive
        :parameters (?thing ?from ?to)
        :precondition (and (mobile ?thing) (road ?from ?to)
            (at ?thing ?from))
        :effect (and (at ?thing ?to) (not (at ?thing ?from)))
    )

    (:action cross
        :parameters (?thing ?from ?to)
        :precondition (and (mobile ?thing) (bridge ?from ?to)
            (at ?thing ?from))
        :effect (and (at ?thing ?to) (not (at ?thing ?from)))
    )

    (:action board
        :parameters (?person ?place ?vehicle)
        :precondition (and (person ?person) (vehicle ?vehicle)
            (at ?person ?place) (at ?vehicle ?place))
        :effect (and (driving ?person ?vehicle) (mobile ?vehicle)
            (not (at ?person ?place)) (not (mobile ?person)))
    )

    (:action disembark
        :parameters (?person ?place ?vehicle)
        :precondition (and (person ?person) (vehicle ?vehicle)
            (driving ?person ?vehicle) (at ?vehicle ?place))
        :effect (and (at ?person ?place) (mobile ?person)
            (not (driving ?person ?vehicle)) (not (mobile ?vehicle)))
    )
)