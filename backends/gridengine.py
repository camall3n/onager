
from ._backend import Backend

class GridEngineBackend(Backend):
    def __init__(self):
        super().__init__()
        pass

    def generate_tasklist(self, commands, tasklist):
        if tasklist is None:
            ids = sorted(commands.keys())
            tasklist = ','.join(map(str,ids))
            # TODO: split into comma-separated blocks
        return tasklist
