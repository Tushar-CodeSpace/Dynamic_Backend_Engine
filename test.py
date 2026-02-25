class Solution:
    def minTimeToType(self, word: str) -> int:
        time = 0
        current = 'a'

        for ch in word:
            diff = abs(ord(ch) - ord(current))
            time += min(diff, 26 - diff)  # movement
            time += 1                     # typing
            current = ch

        return time

print(Solution().minTimeToType("hitesh"))

