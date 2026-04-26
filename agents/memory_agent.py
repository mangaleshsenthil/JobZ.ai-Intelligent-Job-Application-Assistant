import json
import datetime

class MemoryAgent:

    FILE = "data/memory.json"

    @staticmethod
    def store_application(job, score):

        record = {
            "job_title": job["title"],
            "company": job["company"],
            "score": score,
            "date": str(datetime.datetime.now())
        }

        try:
            with open(MemoryAgent.FILE, "r") as f:
                data = json.load(f)
        except:
            data = []

        data.append(record)

        with open(MemoryAgent.FILE, "w") as f:
            json.dump(data, f, indent=4)
