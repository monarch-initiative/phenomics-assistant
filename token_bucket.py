import time
import json

class TokenBucket:
    """An implementation of the token bucket algorithm."""
    def __init__(self, tokens: float, refill_rate: float):
        self.tokens = tokens
        self.max_tokens = tokens
        self.refill_rate = refill_rate
        self.last_refill = time.time()


    def consume(self, count=1):
        # if max_tokens is None, bucket is infinite
        if self.max_tokens is None:
            return True
        
        if self.tokens >= count:
            self.tokens -= count

            return True
        
        return False


    def refill(self):
        if self.max_tokens is None:
            return
        
        now = time.time()
        elapsed = now - self.last_refill
        refill_amount = elapsed * self.refill_rate
        self.tokens = min(self.tokens + refill_amount, self.max_tokens)
        self.last_refill = now


    def time_until_tokens_available(self, desired_tokens: str) -> float:
        if self.tokens >= self.max_tokens or self.max_tokens is None:
            return 0  # bucket is full
        
        desired_tokens = min(desired_tokens, self.max_tokens)
        tokens_needed = desired_tokens - self.tokens
        seconds_until_refill = tokens_needed / self.refill_rate
        return seconds_until_refill


class TokenBucketManager:
    def __init__(self):
        self.buckets = {}

    def get_bucket(self, identifier):
        return self.buckets.get(identifier)
    
    def get_balance(self, identifier):
        bucket = self.get_bucket(identifier)
        if bucket:
            return bucket.tokens
        return None
    
    def dump_json_str(self):
        #return {identifier: {"tokens": bucket.tokens, "refill_rate": bucket.refill_rate} for identifier, bucket in self.buckets.items()}
        return str(json.dumps({identifier: {"tokens": bucket.tokens, "refill_rate": bucket.refill_rate, "max_tokens": bucket.max_tokens, "last_refill": bucket.last_refill} for identifier, bucket in self.buckets.items()}))

    def load_json(self, json_str):
        self.buckets = {}
        buckets = json.loads(json_str)
        for identifier, bucket in buckets.items():
            self.create_bucket(identifier, bucket['tokens'], bucket['refill_rate'])
            self.buckets[identifier].max_tokens = bucket['max_tokens']
            self.buckets[identifier].last_refill = bucket['last_refill']

    def create_bucket(self, identifier, tokens, refill_rate):
        self.buckets[identifier] = TokenBucket(tokens, refill_rate)

    def consume(self, identifier, count=1):
        bucket = self.get_bucket(identifier)
        if bucket:
            return bucket.consume(count)
        return False

    def refill_buckets(self):
        for bucket in self.buckets.values():
            bucket.refill()

    def time_until_tokens_available(self, identifier, desired_tokens: str) -> float:
        bucket = self.get_bucket(identifier)
        if bucket:
            return bucket.time_until_next_refill(desired_tokens)
        return None