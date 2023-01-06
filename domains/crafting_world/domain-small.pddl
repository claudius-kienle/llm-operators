(define
 (domain crafting-world-v20230106)
 (:requirements :strips)
 (:types
   tile
   object
   inventory
   object-type
 )
 (:predicates
   (tile-up ?t1 - tile ?t2 - tile)  ;; t2 is up of t1
   (tile-down ?t1 - tile ?t2 - tile)  ;; t2 is down of t1
   (tile-left ?t1 - tile ?t2 - tile)  ;; t2 is left of t1
   (tile-right ?t1 - tile ?t2 - tile)  ;; t2 is right of t1

   (agent-at ?t - tile)
   (object-at ?x - object ?t - tile)
   (inventory-holding ?i - inventory ?x - object)
   (inventory-empty ?i - inventory)

   (object-of-type ?x - object ?ot - object-type)
 )
 (:constants
  Key - object-type
  WorkStation - object-type
  Pickaxe - object-type
  IronOreVein - object-type
  IronOre - object-type
  IronIngot - object-type
  CoalOreVein - object-type
  Coal - object-type
  GoldOreVein - object-type
  GoldOre - object-type
  GoldIngot - object-type
  CobblestoneStash - object-type
  Cobblestone - object-type
  Axe - object-type
  Tree - object-type
  Wood - object-type
  WoodPlank - object-type
  Stick - object-type
  WeaponStation - object-type
  Sword - object-type
  Chicken - object-type
  Feather - object-type
  Arrow - object-type
  ToolStation - object-type
  Shears - object-type
  Sheep - object-type
  Wool - object-type
  Bed - object-type
  BedStation - object-type
  BoatStation - object-type
  Boat - object-type
  SugarCanePlant - object-type
  SugarCane - object-type
  Paper - object-type
  Furnace - object-type
  FoodStation - object-type
  Bowl - object-type
  PotatoPlant - object-type
  Potato - object-type
  CookedPotato - object-type
  BeetrootCrop - object-type
  Beetroot - object-type
  BeetrootSoup - object-type

  Hypothetical - object-type
  Trash - object-type
 )

 (:action move-up
  :parameters (?t1 - tile ?t2 - tile)
  :precondition (and (agent-at ?t1) (tile-up ?t1 ?t2))
  :effect (and (agent-at ?t2) (not (agent-at ?t1)))
 )
 (:action move-down
  :parameters (?t1 - tile ?t2 - tile)
  :precondition (and (agent-at ?t1) (tile-down ?t1 ?t2))
  :effect (and (agent-at ?t2) (not (agent-at ?t1)))
 )
 (:action move-left
  :parameters (?t1 - tile ?t2 - tile)
  :precondition (and (agent-at ?t1) (tile-left ?t1 ?t2))
  :effect (and (agent-at ?t2) (not (agent-at ?t1)))
 )
 (:action move-right
  :parameters (?t1 - tile ?t2 - tile)
  :precondition (and (agent-at ?t1) (tile-right ?t1 ?t2))
  :effect (and (agent-at ?t2) (not (agent-at ?t1)))
 )
 (:action pick-up
  :parameters (?i - inventory ?x - object ?t - tile)
  :precondition (and (agent-at ?t) (object-at ?x ?t) (inventory-empty ?i))
  :effect (and (inventory-holding ?i ?x) (not (object-at ?x ?t)) (not (inventory-empty ?i)))
 )
 (:action place-down
  :parameters (?i - inventory ?x - object ?t - tile)
  :precondition (and (agent-at ?t) (inventory-holding ?i ?x))
  :effect (and (object-at ?x ?t) (not (inventory-holding ?i ?x)) (inventory-empty ?i))
 )

 (:action mine-iron-ore
  :parameters (?toolinv - inventory ?targetinv - inventory ?x - object ?tool - object ?target - object ?t - tile)
  :precondition (and
    (agent-at ?t)
    (object-at ?x ?t)
    (object-of-type ?x IronOreVein)
    (inventory-holding ?toolinv ?tool)
    (object-of-type ?tool Pickaxe)
    (inventory-empty ?targetinv)
    (object-of-type ?target Hypothetical)
  )
  :effect (and
    (not (inventory-empty ?targetinv))
    (inventory-holding ?targetinv ?target)
    (not (object-of-type ?target Hypothetical))
    (object-of-type ?target IronOre)
  )
 )
 (:action mine-wood
  :parameters (?toolinv - inventory ?targetinv - inventory ?x - object ?tool - object ?target - object ?t - tile)
  :precondition (and
    (agent-at ?t)
    (object-at ?x ?t)
    (object-of-type ?x Tree)
    (inventory-holding ?toolinv ?tool)
    (object-of-type ?tool Axe)
    (inventory-empty ?targetinv)
    (object-of-type ?target Hypothetical)
  )
  :effect (and
    (not (inventory-empty ?targetinv))
    (inventory-holding ?targetinv ?target)
    (not (object-of-type ?target Hypothetical))
    (object-of-type ?target Wood)
  )
 )

 (:action craft-wood-plank
  :parameters (?ingredientinv1 - inventory ?targetinv - inventory ?station - object ?ingredient1 - object ?target - object ?t - tile)
  :precondition (and
    (agent-at ?t)
    (object-at ?station ?t)
    (object-of-type ?station WorkStation)
    (inventory-holding ?ingredientinv1 ?ingredient1)
    (object-of-type ?ingredient1 Wood)
    (inventory-empty ?targetinv)
    (object-of-type ?target Hypothetical)
  )
  :effect (and
    (not (inventory-empty ?targetinv))
    (inventory-holding ?targetinv ?target)
    (not (object-of-type ?target Hypothetical))
    (object-of-type ?target WoodPlank)
    (not (inventory-holding ?ingredientinv1 ?ingredient1))
    (inventory-empty ?ingredientinv1)
    (not (object-of-type ?ingredient1 Wood))
    (object-of-type ?ingredient1 Hypothetical)
  )
 )
)
