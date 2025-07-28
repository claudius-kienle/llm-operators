def go_to_a_furniture_piece_or_an_appliance(furniture_or_appliance: str):
    """This action enables the robot to navigate from one normally immovable piece of furniture to another (e.g., dining tables, side tables, cabinets, and sinks) or an appliance (e.g., refrigerators, coffee makers, microwaves, and washers)."""
    ...

def pick_up_an_object_on_or_in_a_furniture_piece_or_an_appliance(object_id: str, furniture_or_appliance: str):
    """This action enables the robot to pick up an object in/on a large piece of furniture (e.g., dining tables, drawers, cabinets) or an appliance (e.g., dishwashers and refrigerators). The furniture piece or appliance should be opened if it is openable. The object to pick up should not be stacked on top of other household items."""
    ...

def put_an_object_on_or_in_a_furniture_piece_or_an_appliance(object_id: str, furniture_or_appliance: str):
    """This action enables the robot to put an object in/on a large piece of furniture (e.g., dining tables, drawers, cabinets) or an appliance (e.g., dishwashers and refrigerators). The furniture piece or appliance should be opened if it is openable."""
    ...

def stack_objects(object_to_stack: str, base_object: str):
    """This action enables the robot to stack one object on top of another object that is on the same piece of furniture. The furniture piece has to have an open and flat surface. Both objects must be stackable objects. You may assume the robot is holding the object_to_stack at the beginning. Also, there should be no other object on top of the base_object."""
    ...

def unstack_objects(top_object: str, base_object: str):
    """This action enables the robot to unstack one object that is on top of another object. The robot will hold the top_object after unstacking it."""
    ...

def open_a_furniture_piece_or_an_appliance(furniture_or_appliance: str):
    """This action enables the robot to open a large piece of furniture (e.g., cabinets and drawers) or an appliance (e.g., dishwashers and refrigerators) that is openable."""
    ...

def close_a_furniture_piece_or_an_appliance(furniture_or_appliance: str):
    """This action enables the robot to close a large piece of furniture (e.g., cabinets and drawers) or an appliance (e.g., dishwashers and refrigerators) that is openable."""
    ...

def toggle_a_small_appliance_on(appliance: str):
    """This action enables the robot to toggle a small appliance (like humidifiers and light bulbs) to switch them on."""
    ...

def toggle_a_small_appliance_off(appliance: str):
    """This action enables the robot to toggle a small appliance (like humidifiers and light bulbs) to switch them off."""
    ...

def slice_objects(object_to_slice: str, knife: str):
    """This action enables the robot to slice objects (like fruits and vegetables) with a knife. The object to slice needs to be placed on a cutting board. You may assume the robot is holding the knife in its gripper at the beginning. The object to slice should be sliceable. The furniture piece needs to have an open and flat surface."""
    ...

def heat_food_with_a_microwave(food: str, microwave: str):
    """This action enables the robot to start a microwave and heat up the food inside. The food to heat should be placed in a small receptacle (e.g., a plate or a bowl). The robot also needs to close the door of the microwave before taking this action. Note that the food is no longer pickupable after it has been heated."""
    ...

def heat_food_with_pan(food: str, pan: str):
    """This action enables the robot to heat food which is heatable with a pan. The food should be placed on the pan, and the pan needs to be placed on a stove burner before executing this action. Note that the food is no longer pickupable after it has been heated."""
    ...

def transfer_food_from_one_small_receptacle_to_another(food: str, source_receptacle: str, target_receptacle: str):
    """This action enables the robot to transfer food from one small receptacle to another small receptacle. The furniture piece needs to have an open and flat surface. Both receptacles should be opened if openable and not stacked on top of other objects if they are stackable."""
    ...

def put_an_object_onto_or_into_a_small_receptacle(object_id: str, receptacle: str):
    """This action enables the robot to put an object into/onto a small receptacle (e.g. storage boxes, bowls, plates, or pans). The furniture piece needs to have an open and flat surface. The receptacle should be opened if it is openable and not stacked on top of other objects if it is stackable."""
    ...

def pick_up_an_object_on_or_in_a_small_receptacle(object_id: str, receptacle: str):
    """This action enables the robot to pick up an object in some small receptacle (e.g. storage boxes, lunch boxes, bowls, plates). The furniture piece needs to have an open and flat surface. The receptacle should be opened if it is openable and not stacked on top of other objects if it is stackable."""
    ...

def open_a_small_receptacle(receptacle: str):
    """This action enables the robot to open a small receptacle (e.g. small storage boxes or lunch boxes with lids). This action is only applicable for receptacles that are openable. The receptacle needs to be placed on a furniture piece that has an open and flat surface. The receptacle should not be stacked on top of other objects if it is stackable."""
    ...

def close_a_small_receptacle(receptacle: str):
    """This action enables the robot to close a small receptacle that is openable (e.g. small storage boxes or lunch boxes with lids). This action is only applicable for receptacles that are openable. The receptacle needs to be placed on a furniture piece that has an open and flat surface. The receptacle should not be stacked on top of other objects if it is stackable."""
    ...

def mash_food_with_a_blender(food: str, blender: str):
    """This action enables the robot to use a blender to mash some food in it. The food needs to be sliced beforehand and placed inside the blender. Note that the food remains in the blender after this action is performed. You may also assume the blender is turned off before and after mashing the food."""
    ...

def wash_an_object(object_id: str):
    """This action enables the robot to wash an object (e.g., fruits and cloths) in a sink or basin. The object has to be something washable. The robot should hold the object when washing it."""
    ...

def wipe_a_surface(surface: str, cloth: str):
    """This action enables the robot to wipe and clean the surface of a piece of furniture or an appliance, such as a dining table, a mirror, a sink, or a bathtub, with a cloth. You may assume the robot is holding the cloth before executing this action. The cloth will be dirty after executing the action. The robot should also use a clean cloth."""
    ...

def vacuum_a_carpet(vacuum_cleaner: str, carpet: str):
    """This action enables the robot to vacuum a carpet with a handheld vacuum cleaner. You need to make sure the dust bin of the vacuum cleaner is not full before executing this action. You may assume the robot is holding the vacuum cleaner at the beginning. The dust bin of the vacuum cleaner will be full of dust if the carpet is not clean."""
    ...

def empty_a_vacuum_cleaner(vacuum_cleaner: str, trash_can: str):
    """This action enables the robot to empty a vacuum cleaner's dust bin by standing next to a trash can and dumping the dust into it. Note that the robot should hold the vacuum cleaner and stand by the trash can before executing this action. After executing this action, the robot is still holding the vacuum cleaner. The trash can should be opened if it's openable. The dust bin will be empty after executing this action."""
    ...