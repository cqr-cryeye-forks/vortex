import time

from actions.action import Action
from db.dao.profile import ProfileDao
from db.dao.user import UserDao
from scripts.profiler import Profiler
from utils.utils import progress, info, warning


class Profile(Action):
    def __init__(self, workspace):
        super().__init__(workspace)
        self.commands = ["single", "multi"]

    def execute(self, **kwargs):
        self.dbh.connect()
        command = kwargs["command"]
        if not command or command not in self.commands:
            command = self.choose_command()

        keywords = kwargs["keywords"]

        u_dao = UserDao(handler=self.dbh)
        p_dao = ProfileDao(handler=self.dbh)

        users = u_dao.list_all()

        if command == "single":
            if len(keywords) < 1:
                print("[-] Single research needs keywords to operate!")
                exit(1)

            info("Starting single profile search")
            profiler = Profiler(args=keywords)
            profiler.execute()
            print(f"[+] Done!")
        elif command == "multi":
            if len(keywords) < 1:
                keywords = None
            info("Starting per-user profile search")
            if len(users) > 10:
                warning(f"{len(users)} in the DB, the profile search will take some time...", indent=2)
                time.sleep(2)
            for u in users:
                args = []
                if u.name and u.name != "":
                    args += u.name.split(" ")
                else:
                    args += u.email.split("@")[0].split(".")
                args += keywords
                progress(
                    f"Searching profiles for {u.name}. "
                    f"Additional keywords: {','.join(keywords) if len(keywords) > 0 else 'N/A'}", indent=2
                )
                profiler = Profiler(args=args)
                profiler.execute()
            print(f"[+] Done!")
        else:
            print("[-] Unknown command")
