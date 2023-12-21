class NutritionixCacheEntry:
    def __init__(self, query, query_hash, data, entry_date):
        self.query = query
        self.query_hash = query_hash
        self.data = data
        self.entry_date = entry_date