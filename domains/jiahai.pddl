;Header and description

(define (domain cooking)

    ;remove requirements that are not needed
    (:requirements :strips :typing :conditional-effects :negative-preconditions :equality :disjunctive-preconditions)

    (:types
        food container tool - object
        mixture - food
        knife - tool
        bowl plate pot pan - container
    )

    ; un-comment following line if constants are needed
    ;(:constants )

    (:predicates
        ; attributes (immutable)
        (toastable ?f - food)
        (spreadable ?f - food)
        (sliceable ?f - food)
        (pourable ?f - food)
        (heatable ?f - food)
        (fryable ?f - food)

        ; object states
        (placedon ?f - food ?c - container)
        (spreadon ?f - food ?g - food)
        (isclean ?t - tool)
        (toasted ?f - food)
        (washed ?f - food)
        (fried ?f - food)
        (heated ?f - food)
        (sliced ?f - food)
        (served ?c - container)
        (mixture_contains ?m - mixture ?f - food)
    )

    ;define actions here

    (:action mix
        :parameters (?c - container ?m - mixture)
        :precondition (and
            (forall
                (?f - food)
                (not (mixture_contains ?m ?f))
            )
        )
        :effect (and
            (forall
                (?f - food)
                (
                when
                    (placedon ?f ?c)
                    (and
                        (not (placedon ?f ?c))
                        (mixture_contains ?m ?f)
                    )
                )
            )
        )
    )
    (:action pour
        :parameters (?l - food ?c - container)
        :precondition (and
            (pourable ?l)
        )
        :effect (and
            (placedon ?l ?c)
            (forall
                (?d - container)
                (when
                    (not (= ?d ?c))
                    (not (placedon ?l ?d))
                )
            )
        )
    )
    (:action fry
        :parameters (?p - pot)
        :precondition (and
            (forall
                (?f - food)
                (or (not (placedon ?f ?p))
                    (fryable ?f))
            )
        )
        :effect (and
            (forall
                (?f - food)
                (when
                    (placedon ?f ?p)
                    (fried ?f))
            )
        )
    )
    (:action slice
        :parameters (?f - food)
        :precondition (and
            (sliceable ?f)
        )
        :effect (and
            (sliced ?f)
        )
    )
    (:action spread
        :parameters (?j - food ?b - food ?k - knife)
        :precondition (and
            ; (isclean ?k)
            (spreadable ?j)
        )
        :effect (and
            (spreadon ?j ?b)
            (not (isclean ?k))
        )
    )
    (:action wash
        :parameters (?f - food)
        :precondition ()
        :effect (and
            (washed ?f)
        )
    )
    (:action clean
        :parameters (?k - tool)
        :precondition ()
        :effect (and
            (isclean ?k)
        )
    )
    (:action toast
        :parameters ( ?b - food)
        :precondition (and
            (toastable ?b)
        )
        :effect ( toasted ?b)
    )
    (:action put
        :parameters (?f - food ?c - container)
        :precondition ()
        :effect (and
            (placedon ?f ?c)
            (forall
                (?d - container)
                (when
                    (not (= ?d ?c))
                    (not (placedon ?f ?d))
                )
            )
        )
    )
    (:action serve
        :parameters (?c - container)
        :precondition ()
        :effect (and
            (served ?c)
        )
    )
    (:action heat
        :parameters (?c - container)
        :precondition (and
            (forall
                (?f - food)
                (or (not (placedon ?f ?c))
                    (heatable ?f)
                )
            )
        )
        :effect (and
            (forall
                (?f - food)
                (
                when
                    (placedon ?f ?c)
                    (heated ?f)
                )
            )
        )
    )

)