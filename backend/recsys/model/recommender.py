
class Recommender:
    def rank(self, seq, lengths, hidden):
        raise NotImplementedError()

    def recall(self, seq, lengths, hidden):
        raise NotImplementedError()