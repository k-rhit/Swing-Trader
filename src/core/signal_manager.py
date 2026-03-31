import json
from src.utils.file_store import FileStore

class SignalManager:

    def filter_new_signals(self, signals):
        sent = FileStore.load("sent_signals.json")
        sent_keys = set(s["id"] for s in sent)

        new_signals = [s for s in signals if s["id"] not in sent_keys]
        return new_signals

    def save_sent_signals(self, new_signals):
        if len(new_signals) == 0:
            return
        
        sent = FileStore.load("sent_signals.json")
        for s in new_signals:
            sent.append(s)
        FileStore.save("sent_signals.json", sent)