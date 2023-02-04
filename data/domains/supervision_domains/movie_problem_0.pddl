;; Movie Domain instance-1 from IPC-1998 https://github.com/potassco/pddl-instances/blob/master/ipc-1998/domains/movie-round-1-adl/instances/instance-1.pddl
(define (problem movie-x-1)
    (:domain movie-dom)
    (:objects
        chips5 chips4 chips3 chips2 chips1 - chips
        dip5 dip4 dip3 dip2 dip1 - dip
        pop5 pop4 pop3 pop2 pop1 - pop
        cheese5 cheese4 cheese3 cheese2 cheese1 - cheese
        crackers5 crackers4 crackers3 crackers2 crackers1 - crackers
    )
    (:init
        (not (movie-rewound))
        (not (counter-at-two-hours))
        (not (counter-at-zero))
    )
    (:goal
        (and (movie-rewound)
            (counter-at-zero)
            (have-chips)
            (have-dip)
            (have-pop)
            (have-cheese)
            (have-crackers))
    )
)