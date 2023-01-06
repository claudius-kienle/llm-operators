(define
 (problem crafting-world-v20230106-p2)
 (:domain crafting-world-v20230106)
 (:objects
   t1 - tile
   t2 - tile
   i1 - inventory
   i2 - inventory
   o1 - object
   o2 - object
   o3 - object
   o4 - object
   o5 - object
 )
 (:init
   (object-of-type o1 Tree)
   (object-of-type o2 Axe)
   (object-of-type o3 WorkStation)
   (object-of-type o4 Hypothetical)
   (object-of-type o5 Hypothetical)

   (inventory-holding i1 o2)
   (inventory-empty i2)

   (object-at o1 t2)
   (object-at o3 t1)
   (agent-at t1)

   (tile-right t1 t2)
   (tile-left t2 t1)
 )
 (:goal (and
   (inventory-holding i2 o5)
   (object-of-type o5 WoodPlank)
 ))
)
