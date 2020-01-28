from src.main.Module import Module
from src.utility.Config import Config


class ObjectManipulator(Module):
    """ Allows basic manipulator for MESH objects.
    Specify a desired getter for selecting objects in 'selector' section, then specify any desired {key: value} pairs.
    Each pair is treated like a {attribute_name:attribute_value} where attr_name is any valid name for an existing
    attribute or custom property or a name of a custom property to create, while the attr_value is an according value
    for such attribute or custom property (this value can be sampled).

    **Configuration**:

    .. csv-table::
        :header: "Parameter", "Description"

    "selector", "ObjectGetter specific dict."
    "selector/name", "Name of the getter to use. Type: string."
    "selector/condition", "Condition to use for selecting. Type: dict."
    "mode", "Mode of operation. Optional. Type: string. Available values: "once_for_each" (if samplers are called, new sampled value is set to each selected object) and "once_for_all" (if samplers are called, value is sampled once and set to all selected objects)."
    """

    def __init__(self, config):
        Module.__init__(self, config)

    def run(self):
        """ 'Selects' objects and sets according values for defined attributes/custom properties."""
        instances = self.config.get_list("instances", [])
        for instance in instances:
            # separating defined part with the selector from ambiguous part with attribute names and their values to set
            set_params = {}
            sel_objs = {}
            for key in instance.keys():
                # if its not a selector -> to the set parameters dict
                if key != 'selector':
                    set_params[key] = instance[key]
                else:
                    sel_objs[key] = instance[key]
            # create Config objects
            params_conf = Config(set_params)
            sel_conf = Config(sel_objs)
            # invoke a Getter, get a list of objects to manipulate
            objects = sel_conf.get_list("selector")

            op_mode = self.config.get_string("mode", "once_for_each")

            for key in params_conf.data.keys():
                # get raw value from the set parameters if it is to be sampled once for all selected objects
                if op_mode == "once_for_all":
                    result = params_conf.get_raw_value(key)

                for obj in objects:
                    # if it is a mesh
                    if obj.type == "MESH":

                        if op_mode == "once_for_each":
                            # get raw value from the set parameters if it is to be sampled anew for each selected object
                            result = params_conf.get_raw_value(key)

                        # if an attribute with such name exists for this object
                        if hasattr(obj, key):
                            # set the value
                            setattr(obj, key, result)
                        # if not, then treat it as a custom property. Values will be overwritten for existing custom
                        # property, but if the name is new then new custom property will be created
                        else:
                            obj[key] = result
