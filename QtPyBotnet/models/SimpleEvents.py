import json
import copy
import types
import datetime

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
NoneType = type(None)


class EventEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return {
                "_type": "datetime",
                "value": obj.strftime(DATETIME_FORMAT)
            }
        return super(EventEncoder, self).default(obj)


class EventDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, obj):
        if '_type' not in obj:
            return obj
        obj_type = obj['_type']
        if obj_type == 'datetime':
            return datetime.datetime.strptime(obj["value"], DATETIME_FORMAT)
        return obj


class SimpleEvent(types.SimpleNamespace):
    allowed_vars = []

    def __init__(self, bot_id, **kwargs):
        super(SimpleEvent, self).__init__(**kwargs)
        self.bot_id = bot_id

    def serialize(self):
        return json.dumps(vars(self), cls=EventEncoder)

    def deserialize(self, obj: dict):
        if type(obj) is not dict:
            raise Exception("object is not dict")

        event_type = obj.get("event_type")
        if event_type:
            if event_type == "task":
                return SimpleTask(self.bot_id)._deserialize(obj)
            elif event_type == "module":
                return SimpleModule(self.bot_id)._deserialize(obj)
            elif event_type == "info":
                return SimpleInfo(self.bot_id)._deserialize(obj)
        return None

    def _deserialize(self, obj: dict):
        if all(var in obj for var in self.allowed_vars):
            clned = copy.deepcopy(obj)
            for var in obj:
                if var not in self.allowed_vars:
                    del clned[var]
            for var in clned:
                if type(clned[var]) not in self.allowed_vars[var]:
                    return None
            return self.__class__(self.bot_id, **clned)
        return None


class SimpleInfo(SimpleEvent):
    allowed_vars = {"info": [list], "results": [str, list, dict, int, NoneType]}

    def __init__(self, bot_id, **kwargs):
        super(SimpleInfo, self).__init__(bot_id, **kwargs)
        self.event_type = "info"


class SimpleModule(SimpleEvent):
    allowed_vars = {"module": [str], "enabled": [bool]}

    def __init__(self, bot_id, **kwargs):
        super(SimpleModule, self).__init__(bot_id, **kwargs)
        self.event_type = "module"


class SimpleAction(SimpleEvent):
    allowed_vars = {"action": [str],
                    }

    def __init__(self, bot_id, **kwargs):
        super(SimpleAction, self).__init__(bot_id, **kwargs)
        self.event_type = "action"


class SimpleAssign(SimpleEvent):
    allowed_vars = {"action": [str],
                    }

    def __init__(self, bot_id, **kwargs):
        super(SimpleAssign, self).__init__(bot_id, **kwargs)
        self.event_type = "assign"


class SimpleTask(SimpleEvent):
    allowed_vars = {"task_id": [int],
                    "task": [str],
                    "result": [str, list, dict, int, NoneType],
                    "exit_code": [int, NoneType],
                    "user_activity": [int],
                    "time_created": [datetime.datetime],
                    "time_started": [datetime.datetime, NoneType],
                    "time_finished": [datetime.datetime, NoneType]}

    def __init__(self, bot_id, **kwargs):
        super(SimpleTask, self).__init__(bot_id, **kwargs)
        self.event_type = "task"
