"""BPE didático sobre bytes UTF-8, treinado somente nos textos de treino."""

from collections import Counter
import heapq


class ByteBPE:
    BOS, EOS, SEP, PAD = 256, 257, 258, 259

    def __init__(self, merges=()):
        self.merges = [tuple(pair) for pair in merges]
        self.vocab = {i: bytes([i]) for i in range(256)}
        for token, (left, right) in enumerate(self.merges, 260):
            self.vocab[token] = self.vocab[left] + self.vocab[right]
        self.ranks = {pair: token for token, pair in enumerate(self.merges, 260)}

    @property
    def vocab_size(self):
        return 260 + len(self.merges)

    @staticmethod
    def merge(ids, pair, token):
        result, index = [], 0
        while index < len(ids):
            if index + 1 < len(ids) and (ids[index], ids[index + 1]) == pair:
                result.append(token)
                index += 2
            else:
                result.append(ids[index])
                index += 1
        return result

    @classmethod
    def train(cls, texts, vocab_size=512):
        if vocab_size < 260:
            raise ValueError("Vocabulário precisa reservar 256 bytes e quatro tokens especiais.")
        sequences = [list(text.encode("utf-8")) for text in texts]
        merges = []
        while len(merges) + 260 < vocab_size:
            counts = Counter(pair for ids in sequences for pair in zip(ids, ids[1:]))
            if not counts:
                break
            pair = max(counts, key=lambda item: (counts[item], item))
            if counts[pair] < 2:
                break
            token = 260 + len(merges)
            sequences = [cls.merge(ids, pair, token) for ids in sequences]
            merges.append(pair)
        return cls(merges)

    def encode(self, text):
        ids = list(text.encode("utf-8"))
        if not ids:
            return []
        previous = list(range(-1, len(ids) - 1))
        following = list(range(1, len(ids))) + [-1]
        alive = [True] * len(ids)
        pending = []

        def schedule(index):
            if index >= 0 and following[index] >= 0:
                rank = self.ranks.get((ids[index], ids[following[index]]))
                if rank is not None:
                    heapq.heappush(pending, (rank, index))

        for index in range(len(ids) - 1):
            schedule(index)
        while pending:
            rank, left = heapq.heappop(pending)
            right = following[left]
            if not alive[left] or right < 0 or self.ranks.get((ids[left], ids[right])) != rank:
                continue
            ids[left] = rank
            alive[right] = False
            following[left] = following[right]
            if following[right] >= 0:
                previous[following[right]] = left
            schedule(previous[left])
            schedule(left)
        return [token for token, active in zip(ids, alive) if active]

    def decode(self, ids):
        return b"".join(self.vocab[token] for token in ids if token not in {self.BOS, self.EOS, self.SEP, self.PAD}).decode("utf-8", errors="replace")
